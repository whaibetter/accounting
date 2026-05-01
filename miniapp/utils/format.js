const formatAmount = (amount, type) => {
  const sign = type === 2 ? '+' : type === 1 ? '-' : '';
  const num = parseFloat(amount).toFixed(2);
  return `${sign}¥${num}`;
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const month = d.getMonth() + 1;
  const day = d.getDate();
  const weekDays = ['日', '一', '二', '三', '四', '五', '六'];
  const weekDay = weekDays[d.getDay()];
  return `${month}月${day}日 周${weekDay}`;
};

const formatDateShort = (dateStr) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const month = (d.getMonth() + 1).toString().padStart(2, '0');
  const day = d.getDate().toString().padStart(2, '0');
  return `${month}-${day}`;
};

const formatMonth = (dateStr) => {
  if (!dateStr) return '';
  const parts = dateStr.split('-');
  return `${parts[0]}年${parts[1]}月`;
};

const getCurrentMonth = () => {
  const now = new Date();
  const y = now.getFullYear();
  const m = (now.getMonth() + 1).toString().padStart(2, '0');
  return `${y}-${m}`;
};

const getMonthRange = (monthStr) => {
  const [y, m] = monthStr.split('-');
  const start = `${y}-${m}-01`;
  const lastDay = new Date(parseInt(y), parseInt(m), 0).getDate();
  const end = `${y}-${m}-${lastDay.toString().padStart(2, '0')}`;
  return { start, end };
};

const getYearRange = (year) => {
  return {
    start: `${year}-01-01`,
    end: `${year}-12-31`,
  };
};

const todayStr = () => {
  const d = new Date();
  return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`;
};

const accountTypes = {
  1: '现金',
  2: '银行卡',
  3: '信用卡',
  4: '支付宝',
  5: '微信',
  6: '其他',
};

const getAccountTypeName = (type) => accountTypes[type] || '未知';

const billTypeName = {
  1: '支出',
  2: '收入',
  3: '转账',
};

module.exports = {
  formatAmount, formatDate, formatDateShort, formatMonth,
  getCurrentMonth, getMonthRange, getYearRange, todayStr,
  getAccountTypeName, billTypeName,
};
