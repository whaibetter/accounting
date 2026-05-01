const { getBills, deleteBill, getAccounts, getCategories } = require('../../utils/api');
const { getCurrentMonth, getMonthRange, todayStr, formatDate } = require('../../utils/format');

Page({
  data: {
    bills: [],
    page: 1,
    size: 20,
    total: 0,
    hasMore: true,
    loading: false,

    currentMonth: getCurrentMonth(),
    filterType: 0,
    filterCategoryId: '',
    filterAccountId: '',

    accounts: [],
    categories: [],
    showFilter: false,
  },

  onLoad() {
    this.loadFilters();
  },

  onShow() {
    this.setData({ page: 1, bills: [], hasMore: true });
    this.loadBills();
  },

  onPullDownRefresh() {
    this.setData({ page: 1, bills: [], hasMore: true });
    this.loadBills().then(() => wx.stopPullDownRefresh());
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadBills();
    }
  },

  async loadFilters() {
    try {
      const [accRes, catRes] = await Promise.all([
        getAccounts(),
        getCategories(),
      ]);
      if (accRes.code === 200) this.setData({ accounts: accRes.data || [] });
      if (catRes.code === 200) this.setData({ categories: catRes.data || [] });
    } catch (_) {}
  },

  async loadBills() {
    if (this.data.loading) return;
    this.setData({ loading: true });

    const { page, size, currentMonth, filterType, filterCategoryId, filterAccountId } = this.data;
    const { start, end } = getMonthRange(currentMonth);

    try {
      const params = { page, size, start_date: start, end_date: end };
      if (filterType > 0) params.type = filterType;
      if (filterCategoryId) params.category_id = filterCategoryId;
      if (filterAccountId) params.account_id = filterAccountId;

      const res = await getBills(params);
      if (res.code === 200) {
        const { items, total } = res.data;
        const newBills = page === 1 ? items : [...this.data.bills, ...items];
        this.setData({
          bills: newBills,
          total,
          hasMore: newBills.length < total,
          loading: false,
        });
      }
    } catch (_) {
      this.setData({ loading: false });
    }
  },

  onPrevMonth() {
    const [y, m] = this.data.currentMonth.split('-');
    let ny = parseInt(y), nm = parseInt(m) - 1;
    if (nm === 0) { nm = 12; ny -= 1; }
    this.setData({ currentMonth: `${ny}-${nm.toString().padStart(2, '0')}`, page: 1, bills: [] });
    this.loadBills();
  },

  onNextMonth() {
    const [y, m] = this.data.currentMonth.split('-');
    let ny = parseInt(y), nm = parseInt(m) + 1;
    if (nm === 13) { nm = 1; ny += 1; }
    this.setData({ currentMonth: `${ny}-${nm.toString().padStart(2, '0')}`, page: 1, bills: [] });
    this.loadBills();
  },

  onToggleFilter() {
    this.setData({ showFilter: !this.data.showFilter });
  },

  onFilterType(e) {
    this.setData({ filterType: parseInt(e.currentTarget.dataset.type) });
  },

  onFilterCategory(e) {
    const id = e.currentTarget.dataset.id;
    this.setData({ filterCategoryId: this.data.filterCategoryId === id ? '' : id });
  },

  onFilterAccount(e) {
    const id = e.currentTarget.dataset.id;
    this.setData({ filterAccountId: this.data.filterAccountId === id ? '' : id });
  },

  onApplyFilter() {
    this.setData({ page: 1, bills: [], showFilter: false });
    this.loadBills();
  },

  onResetFilter() {
    this.setData({
      filterType: 0, filterCategoryId: '', filterAccountId: '',
      page: 1, bills: [], showFilter: false,
    });
    this.loadBills();
  },

  onEdit(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/add-bill/add-bill?id=${id}` });
  },

  async onDelete(e) {
    const id = e.currentTarget.dataset.id;
    const res = await wx.showModal({ title: '确认删除', content: '确定要删除这条账单吗？' });
    if (res.confirm) {
      try {
        await deleteBill(id);
        wx.showToast({ title: '已删除', icon: 'success' });
        this.setData({ bills: this.data.bills.filter(b => b.id !== id) });
      } catch (_) {
        wx.showToast({ title: '删除失败', icon: 'none' });
      }
    }
  },

  onAddBill() {
    wx.navigateTo({ url: '/pages/add-bill/add-bill' });
  },
});
