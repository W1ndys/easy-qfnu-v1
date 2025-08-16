// 登录页面
const app = getApp()

Page({
  data: {
    studentId: '',
    password: '',
    isLoading: false,
    showPassword: false,
    rememberMe: false,
    errors: {
      studentId: '',
      password: ''
    }
  },

  onLoad() {
    // 检查是否已登录
    if (app.globalData.isLogin) {
      wx.switchTab({
        url: '/pages/index/index'
      })
      return
    }

    // 获取上次登录的学号
    const lastStudentId = wx.getStorageSync('last_student_id')
    if (lastStudentId) {
      this.setData({
        studentId: lastStudentId
      })
    }
  },

  // 学号输入
  onStudentIdInput(e) {
    const value = e.detail.value
    this.setData({
      studentId: value,
      'errors.studentId': ''
    })
  },

  // 密码输入
  onPasswordInput(e) {
    const value = e.detail.value
    this.setData({
      password: value,
      'errors.password': ''
    })
  },

  // 切换密码显示状态
  togglePassword() {
    this.setData({
      showPassword: !this.data.showPassword
    })
  },

  // 切换记住学号
  toggleRemember() {
    this.setData({
      rememberMe: !this.data.rememberMe
    })
  },

  // 表单验证
  validateForm() {
    const { studentId, password } = this.data
    const errors = {}
    let isValid = true

    // 验证学号
    if (!studentId.trim()) {
      errors.studentId = '请输入学号'
      isValid = false
    }

    // 验证密码
    if (!password.trim()) {
      errors.password = '请输入密码'
      isValid = false
    }

    this.setData({ errors })
    return isValid
  },

  // 登录处理
  handleLogin() {
    if (!this.validateForm()) {
      return
    }

    const { studentId, password } = this.data

    this.setData({ isLoading: true })

    app.login(studentId.trim(), password).then(() => {
      // 保存学号（如果勾选了记住学号）
      if (this.data.rememberMe) {
        wx.setStorageSync('last_student_id', studentId.trim())
      }
      
      app.showSuccess('登录成功')
      
      // 跳转到首页
      setTimeout(() => {
        wx.switchTab({
          url: '/pages/index/index'
        })
      }, 1000)

    }).catch((error) => {
      console.error('登录失败:', error)
      
      let errorMessage = '登录失败'
      if (error.message) {
        if (error.message.includes('学号或密码错误')) {
          errorMessage = '学号或密码错误，请检查后重试'
        } else if (error.message.includes('网络')) {
          errorMessage = '网络连接失败，请检查网络后重试'
        } else {
          errorMessage = error.message
        }
      }
      
      app.showError(errorMessage)
    }).finally(() => {
      this.setData({ isLoading: false })
    })
  },

  // 查看用户协议
  showUserAgreement() {
    wx.showModal({
      title: '用户协议',
      content: '这是Easy-QFNUJW用户协议的内容。本应用是第三方教务辅助工具，不会存储您的密码，仅用于获取教务信息。使用本应用即表示您同意我们的服务条款。',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 查看隐私政策
  showPrivacyPolicy() {
    wx.showModal({
      title: '隐私政策',
      content: '我们重视您的隐私。本应用不会收集您的个人敏感信息，所有数据传输均采用HTTPS加密。您的密码不会被存储在我们的服务器上。',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 显示帮助信息
  showHelp() {
    wx.showModal({
      title: '登录帮助',
      content: '如遇登录问题：\n1. 检查学号和密码是否正确\n2. 确认网络连接正常\n3. 尝试在学校官网登录\n4. 联系学校教务处重置密码',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 联系我们
  contactUs() {
    wx.showModal({
      title: '联系我们',
      content: '如有问题请加QQ群：1053432087 或发送邮件至：w1ndys@qq.com',
      showCancel: true,
      cancelText: '关闭',
      confirmText: '加QQ群',
      success: (res) => {
        if (res.confirm) {
          // 这里可以添加跳转到QQ群的逻辑
          wx.showToast({
            title: '正在跳转...',
            icon: 'loading'
          })
        }
      }
    })
  }
})
