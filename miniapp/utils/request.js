const getServerUrl = () => {
  return wx.getStorageSync('serverUrl') || 'http://localhost:8000';
};

const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync('token');
    const serverUrl = getServerUrl();

    wx.request({
      url: `${serverUrl}${options.url}`,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...(options.header || {}),
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');
          wx.reLaunch({ url: '/pages/login/login' });
          reject(new Error('登录已过期'));
        } else {
          const msg = (res.data && res.data.message) || '请求失败';
          reject(new Error(msg));
        }
      },
      fail: (err) => {
        reject(new Error('网络异常，请检查网络连接'));
      },
    });
  });
};

const get = (url, params = {}) => {
  const query = Object.keys(params)
    .filter(k => params[k] !== undefined && params[k] !== null && params[k] !== '')
    .map(k => `${encodeURIComponent(k)}=${encodeURIComponent(params[k])}`)
    .join('&');
  return request({ url: query ? `${url}?${query}` : url, method: 'GET' });
};

const post = (url, data = {}) => {
  return request({ url, method: 'POST', data });
};

const put = (url, data = {}) => {
  return request({ url, method: 'PUT', data });
};

const del = (url) => {
  return request({ url, method: 'DELETE' });
};

module.exports = { request, get, post, put, del, getServerUrl };
