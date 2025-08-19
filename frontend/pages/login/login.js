// pages/login/login.js
Page({
  data: {
    studentId: "",    // 用来存储用户输入的学号
    password: "",     // 用来存储用户输入的密码
    isLoading: false  // 用来控制按钮的加载状态
  },

  /**
   * 处理输入框变化的函数
   */
  handleInput(e) {
    const field = e.currentTarget.dataset.field;
    this.setData({
      [field]: e.detail.value
    });
  },

  /**
   * 处理登录按钮点击的函数
   */
  handleLogin() {
    // 1. 简单的输入校验
    if (!this.data.studentId || !this.data.password) {
      wx.showToast({
        title: '学号和密码不能为空',
        icon: 'none'
      });
      return;
    }

    // 2. 显示加载状态
    this.setData({ isLoading: true });

    // 3. 发起网络请求，调用我们的后端API
    wx.request({
      // 确保你的后端服务正在本地运行！
      url: 'http://127.0.0.1:8000/api/v1/login',
      method: 'POST',
      data: {
        student_id: this.data.studentId,
        password: this.data.password
      },

      // 请求成功后的回调函数
      success: (res) => {
        if (res.statusCode === 200 && res.data.access_token) {
          console.log("登录成功, Token:", res.data.access_token);
          wx.showToast({ title: '登录成功', icon: 'success' });
          wx.setStorageSync('token', res.data.access_token);

          // 延时1.5秒后，跳转到首页 (假设你的首页是 'index')
          setTimeout(() => {
            // 假设你的首页是 TabBar 页面
            wx.switchTab({
              url: '/pages/index/index', // ⚠️ 替换成你的首页路径
              fail: () => {
                // 如果 switchTab 失败 (因为首页不是 TabBar 页面), 则使用 reLaunch
                wx.reLaunch({
                  url: '/pages/index/index' // ⚠️ 替换成你的首页路径
                })
              }
            });
          }, 1500);

        } else {
          // 其他情况，比如后端返回了401错误
          const errorMessage = res.data.detail || '学号或密码错误';
          wx.showToast({ title: errorMessage, icon: 'none' });
        }
      },

      // 请求失败后的回调函数
      fail: (err) => {
        console.error("请求失败", err);
        wx.showToast({ title: '服务器连接失败', icon: 'none' });
      },

      // 请求完成后的回调函数
      complete: () => {
        // 4. 隐藏加载状态
        this.setData({ isLoading: false });
      }
    });
  }
});