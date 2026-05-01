const { getAccounts, createAccount, updateAccount, deleteAccount } = require('../../utils/api');
const { getAccountTypeName } = require('../../utils/format');

Page({
  data: {
    accounts: [],
    showForm: false,
    isEdit: false,
    editId: null,
    form: { name: '', type: 1, icon: '', color: '', initial_balance: 0, is_default: false },
    submitting: false,
    loading: false,
  },

  onShow() {
    this.loadAccounts();
  },

  onPullDownRefresh() {
    this.loadAccounts().then(() => wx.stopPullDownRefresh());
  },

  async loadAccounts() {
    this.setData({ loading: true });
    try {
      const res = await getAccounts();
      if (res.code === 200) this.setData({ accounts: res.data || [], loading: false });
    } catch (_) {
      this.setData({ loading: false });
    }
  },

  onShowForm() {
    this.setData({ showForm: true, isEdit: false, editId: null,
      form: { name: '', type: 1, icon: '', color: '', initial_balance: 0, is_default: false } });
  },

  onHideForm() {
    this.setData({ showForm: false });
  },

  onEdit(e) {
    const account = this.data.accounts.find(a => a.id === parseInt(e.currentTarget.dataset.id));
    if (account) {
      this.setData({ showForm: true, isEdit: true, editId: account.id,
        form: { name: account.name, type: account.type, icon: account.icon, color: account.color, initial_balance: account.initial_balance, is_default: !!account.is_default } });
    }
  },

  onFormField(e) {
    const key = e.currentTarget.dataset.key;
    this.setData({ [`form.${key}`]: e.detail.value });
  },

  onFormType(e) {
    this.setData({ 'form.type': parseInt(e.currentTarget.dataset.value) });
  },

  async onSave() {
    const { form, isEdit, editId } = this.data;
    if (!form.name.trim()) {
      wx.showToast({ title: '请输入账户名称', icon: 'none' }); return;
    }

    const data = {
      name: form.name.trim(),
      type: parseInt(form.type),
      icon: form.icon || '',
      color: form.color || '',
      initial_balance: parseFloat(form.initial_balance) || 0,
      is_default: !!form.is_default,
    };

    this.setData({ submitting: true });
    try {
      if (isEdit) await updateAccount(editId, data);
      else await createAccount(data);
      wx.showToast({ title: isEdit ? '已更新' : '已创建', icon: 'success' });
      this.setData({ showForm: false, submitting: false });
      this.loadAccounts();
    } catch (err) {
      wx.showToast({ title: err.message || '操作失败', icon: 'none' });
      this.setData({ submitting: false });
    }
  },

  async onDelete(e) {
    const id = e.currentTarget.dataset.id;
    const res = await wx.showModal({ title: '确认删除', content: '删除后不可恢复' });
    if (res.confirm) {
      try {
        await deleteAccount(id);
        wx.showToast({ title: '已删除', icon: 'success' });
        this.loadAccounts();
      } catch (_) {
        wx.showToast({ title: '删除失败', icon: 'none' });
      }
    }
  },
});
