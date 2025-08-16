// 调试页面
Page({
  data: {
    systemInfo: {},
    testResults: []
  },

  onLoad() {
    this.runTests()
  },

  runTests() {
    const tests = []

    // 测试1: 系统信息
    try {
      const systemInfo = wx.getSystemInfoSync()
      tests.push({
        name: '系统信息获取',
        status: 'success',
        result: `${systemInfo.platform} ${systemInfo.version}`
      })
      this.setData({ systemInfo })
    } catch (e) {
      tests.push({
        name: '系统信息获取',
        status: 'error',
        result: e.message
      })
    }

    // 测试2: 存储功能
    try {
      wx.setStorageSync('test_key', 'test_value')
      const value = wx.getStorageSync('test_key')
      tests.push({
        name: '本地存储',
        status: value === 'test_value' ? 'success' : 'error',
        result: value === 'test_value' ? '正常' : '异常'
      })
    } catch (e) {
      tests.push({
        name: '本地存储',
        status: 'error',
        result: e.message
      })
    }

    // 测试3: 网络请求
    wx.request({
      url: 'https://api.easy-qfnujw.com/api/v1/health',
      success: (res) => {
        tests.push({
          name: '网络请求',
          status: 'success',
          result: '连接正常'
        })
        this.setData({ testResults: tests })
      },
      fail: (err) => {
        tests.push({
          name: '网络请求',
          status: 'error',
          result: err.errMsg || '网络异常'
        })
        this.setData({ testResults: tests })
      }
    })

    this.setData({ testResults: tests })
  },

  goToLogin() {
    wx.navigateTo({
      url: '/pages/login/login'
    })
  }
})
