const { getUserInfo, logout } = require('../../utils/auth');

Page({
  data: {
    userInfo: {},
  },

  onShow() {
    this.setData({ userInfo: getUserInfo() });
  },

  onNavAccounts() {
    wx.navigateTo({ url: '/pages/accounts/accounts' });
  },

  onNavCategories() {
    wx.navigateTo({ url: '/pages/categories/categories' });
  },

  onServerConfig() {
    const url = wx.getStorageSync('serverUrl') || '';
    wx.showModal({
      title: '服务器地址',
      editable: true,
      content: '',
      placeholderText: url || 'http://localhost:8000',
      success: (res) => {
        if (res.confirm && res.content) {
          wx.setStorageSync('serverUrl', res.content.trim());
          wx.showToast({ title: '已更新', icon: 'success' });
        }
      },
    });
  },

  onLogout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          logout();
          wx.reLaunch({ url: '/pages/login/login' });
        }
      },
    });
  },
});
