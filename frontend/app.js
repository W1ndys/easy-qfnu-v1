// Easy-QFNUJW 微信小程序主应用文件
App({
  globalData: {
    userInfo: null,
    token: null,
    apiBase: 'https://your-domain.com/api', // 后端API地址
    isLogin: false,
    studentId: null
  },

  onLaunch() {
    console.log('Easy-QFNUJW 小程序启动')
    
    // 检查登录状态
    this.checkLoginStatus()
    
    // 初始化应用
    this.initApp()
  },

  onShow() {
    console.log('应用显示')
  },

  onHide() {
    console.log('应用隐藏')
  },

  onError(error) {
    console.error('应用错误:', error)
    wx.showToast({
      title: '应用出现错误',
      icon: 'none'
    })
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('access_token')
    const studentId = wx.getStorageSync('student_id')
    
    if (token && studentId) {
      this.globalData.token = token
      this.globalData.studentId = studentId
      this.globalData.isLogin = true
      
      // 验证token有效性
      this.verifyToken()
    }
  },

  // 验证token有效性
  verifyToken() {
    wx.request({
      url: `${this.globalData.apiBase}/verify`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${this.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode !== 200) {
          this.logout()
        }
      },
      fail: () => {
        this.logout()
      }
    })
  },

  // 初始化应用
  initApp() {
    // 获取系统信息（兼容旧版本）
    wx.getSystemInfo({
      success: (res) => {
        this.globalData.systemInfo = res
        console.log('系统信息:', res)
      },
      fail: (err) => {
        console.warn('获取系统信息失败:', err)
      }
    })
  },

  // 登录
  login(studentId, password) {
    return new Promise((resolve, reject) => {
      wx.showLoading({
        title: '登录中...'
      })

      wx.request({
        url: `${this.globalData.apiBase}/login`,
        method: 'POST',
        data: {
          student_id: studentId,
          password: password
        },
        success: (res) => {
          wx.hideLoading()
          
          if (res.statusCode === 200) {
            const { access_token, expires_in } = res.data
            
            // 保存登录信息
            wx.setStorageSync('access_token', access_token)
            wx.setStorageSync('student_id', studentId)
            wx.setStorageSync('login_time', Date.now())
            
            // 更新全局数据
            this.globalData.token = access_token
            this.globalData.studentId = studentId
            this.globalData.isLogin = true
            
            resolve(res.data)
          } else {
            reject(new Error(res.data.detail || '登录失败'))
          }
        },
        fail: (error) => {
          wx.hideLoading()
          reject(error)
        }
      })
    })
  },

  // 退出登录
  logout() {
    // 清除本地存储
    wx.removeStorageSync('access_token')
    wx.removeStorageSync('student_id')
    wx.removeStorageSync('login_time')
    
    // 重置全局数据
    this.globalData.token = null
    this.globalData.studentId = null
    this.globalData.isLogin = false
    this.globalData.userInfo = null
    
    // 跳转到登录页
    wx.reLaunch({
      url: '/pages/login/login'
    })
  },

  // 通用API请求方法
  request(options) {
    return new Promise((resolve, reject) => {
      const defaultOptions = {
        header: {
          'Content-Type': 'application/json'
        }
      }

      // 添加Authorization header
      if (this.globalData.token) {
        defaultOptions.header['Authorization'] = `Bearer ${this.globalData.token}`
      }

      // 合并配置
      const requestOptions = {
        ...defaultOptions,
        ...options,
        url: `${this.globalData.apiBase}${options.url}`,
        header: {
          ...defaultOptions.header,
          ...options.header
        }
      }

      wx.request({
        ...requestOptions,
        success: (res) => {
          if (res.statusCode === 401) {
            // Token过期或无效
            wx.showModal({
              title: '登录过期',
              content: '请重新登录',
              showCancel: false,
              success: () => {
                this.logout()
              }
            })
            return
          }

          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data)
          } else {
            reject(new Error(res.data.detail || `请求失败: ${res.statusCode}`))
          }
        },
        fail: (error) => {
          reject(error)
        }
      })
    })
  },

  // 显示错误信息
  showError(message) {
    wx.showToast({
      title: message || '操作失败',
      icon: 'none',
      duration: 2000
    })
  },

  // 显示成功信息
  showSuccess(message) {
    wx.showToast({
      title: message || '操作成功',
      icon: 'success',
      duration: 1500
    })
  }
})
