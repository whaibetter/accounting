const { get, post, put, del } = require('./request');

// ============ 认证 ============
const login = (username, password) =>
  post('/api/v1/auth/login', { username, password });

const checkAuth = () =>
  get('/api/v1/auth/status');

// ============ 账单 ============
const getBills = (params = {}) =>
  get('/api/v1/bills', params);

const createBill = (data) =>
  post('/api/v1/bills', data);

const updateBill = (id, data) =>
  put(`/api/v1/bills/${id}`, data);

const deleteBill = (id) =>
  del(`/api/v1/bills/${id}`);

// ============ 账户 ============
const getAccounts = () =>
  get('/api/v1/accounts');

const createAccount = (data) =>
  post('/api/v1/accounts', data);

const updateAccount = (id, data) =>
  put(`/api/v1/accounts/${id}`, data);

const deleteAccount = (id) =>
  del(`/api/v1/accounts/${id}`);

// ============ 分类 ============
const getCategories = (type) =>
  get('/api/v1/categories', type !== undefined ? { type } : {});

const createCategory = (data) =>
  post('/api/v1/categories', data);

const updateCategory = (id, data) =>
  put(`/api/v1/categories/${id}`, data);

const deleteCategory = (id) =>
  del(`/api/v1/categories/${id}`);

// ============ 标签 ============
const getTags = () =>
  get('/api/v1/tags');

const createTag = (data) =>
  post('/api/v1/tags', data);

const updateTag = (id, data) =>
  put(`/api/v1/tags/${id}`, data);

const deleteTag = (id) =>
  del(`/api/v1/tags/${id}`);

// ============ 统计 ============
const getOverview = (params = {}) =>
  get('/api/v1/statistics/overview', params);

const getCategoryStats = (params = {}) =>
  get('/api/v1/statistics/by-category', params);

const getTrend = (params = {}) =>
  get('/api/v1/statistics/trend', params);

const getBalanceTrend = (params = {}) =>
  get('/api/v1/statistics/balance-trend', params);

// ============ AI ============
const aiAccount = (text) =>
  post('/api/v1/ai/accounting', { text });

// ============ 导出 ============
const getExportUrl = (format, params) => {
  const serverUrl = require('./request').getServerUrl();
  const query = new URLSearchParams(params).toString();
  return `${serverUrl}/api/v1/export/${format}?${query}`;
};

module.exports = {
  login, checkAuth,
  getBills, createBill, updateBill, deleteBill,
  getAccounts, createAccount, updateAccount, deleteAccount,
  getCategories, createCategory, updateCategory, deleteCategory,
  getTags, createTag, updateTag, deleteTag,
  getOverview, getCategoryStats, getTrend, getBalanceTrend,
  aiAccount, getExportUrl,
};
