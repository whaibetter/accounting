const { createBill, updateBill, getBills, getAccounts, getCategories, getTags } = require('../../utils/api');
const { todayStr } = require('../../utils/format');

Page({
  data: {
    isEdit: false,
    editId: null,

    billType: 1,
    amount: '',
    categoryId: null,
    categories: [],
    selectedCategoryName: '',
    selectedCategoryIcon: '',

    accountId: null,
    accounts: [],

    billDate: todayStr(),
    billTime: '',
    remark: '',
    selectedTags: [],
    allTags: [],

    showCategoryPicker: false,
    showAccountPicker: false,
    showTagPicker: false,

    submitting: false,
  },

  async onLoad(options) {
    await this.loadOptions();

    if (options.id) {
      this.setData({ isEdit: true, editId: options.id });
      await this.loadBillData(options.id);
    }
  },

  async loadOptions() {
    try {
      const [accRes, catRes] = await Promise.all([
        getAccounts(),
        getCategories(),
      ]);
      if (accRes.code === 200) {
        const accounts = accRes.data || [];
        this.setData({ accounts, accountId: accounts.length > 0 ? accounts[0].id : null });
      }
      if (catRes.code === 200) {
        const all = catRes.data || [];
        const expenseCats = this.flattenCategories(all, 1);
        this.setData({ categories: all, expenseFlatCats: expenseCats });
        if (expenseCats.length > 0) {
          this.setData({
            categoryId: expenseCats[0].id,
            selectedCategoryName: expenseCats[0].name,
            selectedCategoryIcon: expenseCats[0].icon,
          });
        }
      }
      const tagRes = await getTags();
      if (tagRes.code === 200) this.setData({ allTags: tagRes.data || [] });
    } catch (_) {}
  },

  flattenCategories(tree, filterType) {
    const result = [];
    for (const node of tree) {
      if (node.type === filterType) {
        result.push(node);
        if (node.children) {
          for (const child of node.children) {
            if (child.type === filterType) result.push(child);
          }
        }
      }
    }
    return result;
  },

  async loadBillData(id) {
    try {
      const res = await getBills({ page: 1, size: 1 });
    } catch (_) {}
  },

  onTypeChange(e) {
    const type = parseInt(e.currentTarget.dataset.type);
    this.setData({ billType: type });

    if (type === 1 || type === 2) {
      const cats = this.flattenCategories(this.data.categories, type);
      const key = type === 1 ? 'expenseFlatCats' : 'incomeFlatCats';
      this.setData({ [key]: cats, selectedCategoryName: '', selectedCategoryIcon: '', categoryId: null });
      if (cats.length > 0) {
        this.setData({ categoryId: cats[0].id, selectedCategoryName: cats[0].name, selectedCategoryIcon: cats[0].icon || '💰' });
      }
    }
  },

  onAmountInput(e) {
    let val = e.detail.value;
    val = val.replace(/[^0-9.]/g, '');
    const parts = val.split('.');
    if (parts.length > 2) val = parts[0] + '.' + parts.slice(1).join('');
    if (parts.length === 2 && parts[1].length > 2) val = parts[0] + '.' + parts[1].slice(0, 2);
    this.setData({ amount: val });
  },

  onAmountTap(e) {
    const key = e.currentTarget.dataset.key;
    let { amount } = this.data;
    if (key === 'clear') { amount = ''; }
    else if (key === 'del') { amount = amount.slice(0, -1); }
    else {
      if (key === '.' && amount.includes('.')) return;
      if (amount.includes('.') && amount.split('.')[1].length >= 2) return;
      if (amount === '0' && key !== '.') amount = '';
      amount += key;
    }
    this.setData({ amount });
  },

  onToggleCategoryPicker() {
    this.setData({ showCategoryPicker: !this.data.showCategoryPicker });
  },

  onSelectCategory(e) {
    const { id, name, icon } = e.currentTarget.dataset;
    this.setData({ categoryId: parseInt(id), selectedCategoryName: name, selectedCategoryIcon: icon || '💰', showCategoryPicker: false });
  },

  onToggleAccountPicker() {
    this.setData({ showAccountPicker: !this.data.showAccountPicker });
  },

  onSelectAccount(e) {
    const { id, name } = e.currentTarget.dataset;
    this.setData({ accountId: parseInt(id), selectedAccountName: name, showAccountPicker: false });
  },

  onDateChange(e) {
    this.setData({ billDate: e.detail.value });
  },

  onTimeInput(e) {
    this.setData({ billTime: e.detail.value });
  },

  onRemarkInput(e) {
    this.setData({ remark: e.detail.value });
  },

  onToggleTagPicker() {
    this.setData({ showTagPicker: !this.data.showTagPicker });
  },

  onSelectTag(e) {
    const { id } = e.currentTarget.dataset;
    let { selectedTags } = this.data;
    const idx = selectedTags.indexOf(parseInt(id));
    if (idx >= 0) selectedTags.splice(idx, 1);
    else selectedTags.push(parseInt(id));
    this.setData({ selectedTags });
  },

  async onSubmit() {
    const { isEdit, editId, billType, amount, categoryId, accountId, billDate, billTime, remark, selectedTags } = this.data;

    if (!amount || parseFloat(amount) <= 0) {
      wx.showToast({ title: '请输入有效金额', icon: 'none' }); return;
    }
    if (!categoryId) {
      wx.showToast({ title: '请选择分类', icon: 'none' }); return;
    }
    if (!accountId) {
      wx.showToast({ title: '请选择账户', icon: 'none' }); return;
    }

    const billData = {
      account_id: accountId,
      category_id: categoryId,
      type: billType,
      amount: parseFloat(amount),
      bill_date: billDate,
      remark: remark || '',
      tag_ids: selectedTags,
    };
    if (billTime) billData.bill_time = billTime;

    this.setData({ submitting: true });

    try {
      if (isEdit) {
        await updateBill(editId, billData);
        wx.showToast({ title: '已更新', icon: 'success' });
      } else {
        await createBill(billData);
        wx.showToast({ title: '记账成功', icon: 'success' });
      }
      setTimeout(() => wx.navigateBack(), 1000);
    } catch (err) {
      wx.showToast({ title: err.message || '操作失败', icon: 'none' });
    } finally {
      this.setData({ submitting: false });
    }
  },
});
