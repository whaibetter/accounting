const { getOverview, getBills } = require('../../utils/api');
const { formatAmount, getCurrentMonth, getMonthRange } = require('../../utils/format');

Page({
  data: {
    month: getCurrentMonth(),
    overview: { total_income: 0, total_expense: 0, balance: 0, bill_count: 0 },
    recentBills: [],
    loading: true,
  },

  onShow() {
    this.loadData();
  },

  onPullDownRefresh() {
    this.loadData().then(() => wx.stopPullDownRefresh());
  },

  async loadData() {
    this.setData({ loading: true });
    try {
      const { start, end } = getMonthRange(this.data.month);
      const [overviewRes, billsRes] = await Promise.all([
        getOverview({ start_date: start, end_date: end }),
        getBills({ page: 1, size: 10, start_date: start, end_date: end }),
      ]);

      const overview = overviewRes.code === 200 ? overviewRes.data : this.data.overview;
      const bills = billsRes.code === 200 ? (billsRes.data.items || []) : [];

      this.setData({
        overview,
        recentBills: bills,
        loading: false,
      });
    } catch (err) {
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  onPrevMonth() {
    const [y, m] = this.data.month.split('-');
    let ny = parseInt(y), nm = parseInt(m) - 1;
    if (nm === 0) { nm = 12; ny -= 1; }
    this.setData({ month: `${ny}-${nm.toString().padStart(2, '0')}` });
    this.loadData();
  },

  onNextMonth() {
    const [y, m] = this.data.month.split('-');
    let ny = parseInt(y), nm = parseInt(m) + 1;
    if (nm === 13) { nm = 1; ny += 1; }
    this.setData({ month: `${ny}-${nm.toString().padStart(2, '0')}` });
    this.loadData();
  },

  onAddBill() {
    wx.navigateTo({ url: '/pages/add-bill/add-bill' });
  },

  onViewBills() {
    wx.switchTab({ url: '/pages/bills/bills' });
  },

  onViewStats() {
    wx.switchTab({ url: '/pages/statistics/statistics' });
  },
});
