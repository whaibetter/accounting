const { login, checkAuth } = require('./api');

const isLoggedIn = () => {
  const token = wx.getStorageSync('token');
  return !!token;
};

const doLogin = async (username, password) => {
  const res = await login(username, password);
  if (res.code === 200 && res.data && res.data.access_token) {
    wx.setStorageSync('token', res.data.access_token);
    wx.setStorageSync('userInfo', {
      username: res.data.username || username,
      nickname: res.data.nickname || username,
    });
    return res.data;
  }
  throw new Error(res.message || '登录失败');
};

const logout = () => {
  wx.removeStorageSync('token');
  wx.removeStorageSync('userInfo');
};

const getUserInfo = () => {
  return wx.getStorageSync('userInfo') || {};
};

module.exports = { isLoggedIn, doLogin, logout, getUserInfo };
