const { isLoggedIn } = require('./utils/auth');

App({
  onLaunch() {
    this.checkLogin();
  },

  checkLogin() {
    const loggedIn = isLoggedIn();
    this.globalData.isLoggedIn = loggedIn;
    if (!loggedIn) {
      wx.reLaunch({ url: '/pages/login/login' });
    }
  },

  globalData: {
    isLoggedIn: false,
  },
});
