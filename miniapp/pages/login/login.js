const { doLogin } = require('../../utils/auth');

Page({
  data: {
    serverUrl: 'http://localhost:8000',
    username: '',
    password: '',
    loading: false,
  },

  onLoad() {
    const savedUrl = wx.getStorageSync('serverUrl');
    if (savedUrl) {
      this.setData({ serverUrl: savedUrl });
    }
  },

  onServerUrlInput(e) {
    this.setData({ serverUrl: e.detail.value });
  },

  onUsernameInput(e) {
    this.setData({ username: e.detail.value });
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value });
  },

  async onLogin() {
    const { serverUrl, username, password } = this.data;
    if (!serverUrl.trim()) {
      wx.showToast({ title: '请输入服务器地址', icon: 'none' });
      return;
    }
    if (!username.trim()) {
      wx.showToast({ title: '请输入用户名', icon: 'none' });
      return;
    }
    if (!password.trim()) {
      wx.showToast({ title: '请输入密码', icon: 'none' });
      return;
    }

    wx.setStorageSync('serverUrl', serverUrl.trim());
    this.setData({ loading: true });

    try {
      await doLogin(username.trim(), password);
      wx.showToast({ title: '登录成功', icon: 'success' });
      setTimeout(() => {
        wx.reLaunch({ url: '/pages/index/index' });
      }, 1000);
    } catch (err) {
      wx.showToast({ title: err.message || '登录失败', icon: 'none' });
    } finally {
      this.setData({ loading: false });
    }
  },
});
