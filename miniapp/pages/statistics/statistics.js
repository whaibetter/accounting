const { getOverview, getCategoryStats, getTrend } = require('../../utils/api');
const { getCurrentMonth, getMonthRange, getYearRange } = require('../../utils/format');

Page({
  data: {
    periodType: 'month',
    currentPeriod: getCurrentMonth(),
    currentYear: new Date().getFullYear(),

    overview: { total_income: 0, total_expense: 0, balance: 0, bill_count: 0 },
    expenseStats: [],
    incomeStats: [],
    trend: [],

    activeTab: 'expense',
    loading: true,
  },

  onShow() {
    this.loadData();
  },

  onChangePeriodType(e) {
    this.setData({ periodType: e.currentTarget.dataset.type });
    this.loadData();
  },

  onPrev() {
    if (this.data.periodType === 'month') {
      const [y, m] = this.data.currentPeriod.split('-');
      let ny = parseInt(y), nm = parseInt(m) - 1;
      if (nm === 0) { nm = 12; ny -= 1; }
      this.setData({ currentPeriod: `${ny}-${nm.toString().padStart(2, '0')}` });
    } else {
      this.setData({ currentYear: this.data.currentYear - 1 });
    }
    this.loadData();
  },

  onNext() {
    if (this.data.periodType === 'month') {
      const [y, m] = this.data.currentPeriod.split('-');
      let ny = parseInt(y), nm = parseInt(m) + 1;
      if (nm === 13) { nm = 1; ny += 1; }
      this.setData({ currentPeriod: `${ny}-${nm.toString().padStart(2, '0')}` });
    } else {
      this.setData({ currentYear: this.data.currentYear + 1 });
    }
    this.loadData();
  },

  async loadData() {
    this.setData({ loading: true });
    try {
      const { periodType, currentPeriod, currentYear } = this.data;
      let dateRange;
      if (periodType === 'month') {
        dateRange = getMonthRange(currentPeriod);
      } else {
        dateRange = getYearRange(currentYear);
      }

      const [overviewRes, expenseRes, incomeRes] = await Promise.all([
        getOverview({ start_date: dateRange.start, end_date: dateRange.end }),
        getCategoryStats({ start_date: dateRange.start, end_date: dateRange.end, type: 1 }),
        getCategoryStats({ start_date: dateRange.start, end_date: dateRange.end, type: 2 }),
      ]);

      const overview = overviewRes.code === 200 ? overviewRes.data : this.data.overview;
      const expenseStats = expenseRes.code === 200 ? (expenseRes.data || []) : [];
      const incomeStats = incomeRes.code === 200 ? (incomeRes.data || []) : [];

      this.setData({ overview, expenseStats, incomeStats, loading: false });
    } catch (_) {
      this.setData({ loading: false });
    }
  },

  onTabChange(e) {
    this.setData({ activeTab: e.currentTarget.dataset.tab });
  },
});
