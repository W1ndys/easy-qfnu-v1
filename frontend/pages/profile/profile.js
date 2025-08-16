// 个人中心页面
const app = getApp()

Page({
  data: {
    userInfo: null,
    appVersion: '0.0.1',
    menuItems: [
      {
        id: 'settings',
        name: '应用设置',
        icon: '⚙️',
        desc: '个性化设置和偏好'
      },
      {
        id: 'feedback',
        name: '意见反馈',
        icon: '💬',
        desc: '帮助我们改进产品'
      },
      {
        id: 'about',
        name: '关于我们',
        icon: 'ℹ️',
        desc: '了解应用详情'
      },
      {
        id: 'help',
        name: '帮助中心',
        icon: '❓',
        desc: '常见问题和使用指南'
      }
    ]
  },

  onLoad() {
    this.loadUserInfo()
  },

  onShow() {
    // 检查登录状态
    if (!app.globalData.isLogin) {
      wx.reLaunch({
        url: '/pages/login/login'
      })
      return
    }
  },

  // 加载用户信息
  loadUserInfo() {
    const studentId = app.globalData.studentId
    
    this.setData({
      userInfo: {
        studentId: studentId,
        name: `同学 ${studentId.slice(-4)}`,
        avatar: '👤',
        joinDate: this.getJoinDate()
      }
    })
  },

  // 获取加入日期（模拟）
  getJoinDate() {
    const joinTime = wx.getStorageSync('login_time') || Date.now()
    return new Date(joinTime).toLocaleDateString('zh-CN')
  },

  // 菜单项点击
  onMenuItemTap(e) {
    const { id } = e.currentTarget.dataset
    
    switch (id) {
      case 'settings':
        this.showSettings()
        break
      case 'feedback':
        this.showFeedback()
        break
      case 'about':
        this.showAbout()
        break
      case 'help':
        this.showHelp()
        break
      default:
        break
    }
  },

  // 应用设置
  showSettings() {
    const items = [
      '通知设置',
      '缓存清理',
      '数据同步',
      '隐私设置'
    ]
    
    wx.showActionSheet({
      itemList: items,
      success: (res) => {
        const item = items[res.tapIndex]
        
        switch (res.tapIndex) {
          case 0:
            this.showNotificationSettings()
            break
          case 1:
            this.clearCache()
            break
          case 2:
            this.syncData()
            break
          case 3:
            this.showPrivacySettings()
            break
        }
      }
    })
  },

  // 通知设置
  showNotificationSettings() {
    wx.showModal({
      title: '通知设置',
      content: '暂时只支持系统通知，更多通知功能正在开发中。',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 清理缓存
  clearCache() {
    wx.showModal({
      title: '清理缓存',
      content: '确定要清理应用缓存吗？这将删除所有本地存储的临时数据。',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '清理中...' })
          
          // 清理缓存（保留重要数据）
          const keysToKeep = ['access_token', 'student_id', 'login_time', 'last_student_id']
          
          wx.getStorageInfo({
            success: (info) => {
              info.keys.forEach(key => {
                if (!keysToKeep.includes(key)) {
                  wx.removeStorageSync(key)
                }
              })
              
              wx.hideLoading()
              app.showSuccess('缓存清理完成')
            }
          })
        }
      }
    })
  },

  // 数据同步
  async syncData() {
    wx.showLoading({ title: '同步中...' })
    
    try {
      // 模拟数据同步
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      wx.hideLoading()
      app.showSuccess('数据同步完成')
    } catch (error) {
      wx.hideLoading()
      app.showError('同步失败')
    }
  },

  // 隐私设置
  showPrivacySettings() {
    wx.navigateTo({
      url: '/pages/privacy/privacy'
    }).catch(() => {
      // 如果页面不存在，显示模态框
      wx.showModal({
        title: '隐私设置',
        content: '您可以在数据统计页面中管理数据贡献设置，控制个人数据的使用方式。',
        showCancel: true,
        cancelText: '关闭',
        confirmText: '前往设置',
        success: (res) => {
          if (res.confirm) {
            wx.switchTab({
              url: '/pages/stats/stats'
            })
          }
        }
      })
    })
  },

  // 意见反馈
  showFeedback() {
    const items = [
      '问题反馈',
      '功能建议',
      '联系客服',
      'QQ群交流'
    ]
    
    wx.showActionSheet({
      itemList: items,
      success: (res) => {
        switch (res.tapIndex) {
          case 0:
            this.submitFeedback('问题反馈')
            break
          case 1:
            this.submitFeedback('功能建议')
            break
          case 2:
            this.contactSupport()
            break
          case 3:
            this.joinQQGroup()
            break
        }
      }
    })
  },

  // 提交反馈
  submitFeedback(type) {
    wx.showModal({
      title: type,
      content: '请通过以下方式提交您的反馈：\n\n• QQ群：123456789\n• 邮箱：support@example.com\n• 微信群：扫描小程序码\n\n我们会认真处理每一条反馈！',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 联系客服
  contactSupport() {
    wx.showModal({
      title: '联系客服',
      content: '客服工作时间：9:00-18:00\n\n联系方式：\n• QQ：123456789\n• 邮箱：support@example.com\n• 电话：400-123-4567',
      showCancel: true,
      cancelText: '关闭',
      confirmText: '复制QQ',
      success: (res) => {
        if (res.confirm) {
          wx.setClipboardData({
            data: '123456789',
            success: () => {
              app.showSuccess('QQ号已复制')
            }
          })
        }
      }
    })
  },

  // 加入QQ群
  joinQQGroup() {
    wx.showModal({
      title: '加入QQ群',
      content: 'Easy-QFNUJW交流群：123456789\n\n在群里您可以：\n• 获取最新功能更新\n• 反馈问题和建议\n• 与其他用户交流\n• 获得技术支持',
      showCancel: true,
      cancelText: '关闭',
      confirmText: '复制群号',
      success: (res) => {
        if (res.confirm) {
          wx.setClipboardData({
            data: '123456789',
            success: () => {
              app.showSuccess('群号已复制，请手动加群')
            }
          })
        }
      }
    })
  },

  // 关于我们
  showAbout() {
    const content = `Easy-QFNUJW v${this.data.appVersion}\n\n一个专为曲阜师范大学学生设计的第三方教务辅助工具。\n\n主要功能：\n• 快速查询成绩和课表\n• 智能数据统计分析\n• 班内排名查看\n• 课余量实时查询\n\n本应用与学校官方无关，请遵守相关规定使用。`
    
    wx.showModal({
      title: '关于 Easy-QFNUJW',
      content: content,
      showCancel: true,
      cancelText: '关闭',
      confirmText: '检查更新',
      success: (res) => {
        if (res.confirm) {
          this.checkUpdate()
        }
      }
    })
  },

  // 检查更新
  checkUpdate() {
    wx.showLoading({ title: '检查中...' })
    
    // 模拟检查更新
    setTimeout(() => {
      wx.hideLoading()
      wx.showModal({
        title: '检查更新',
        content: '当前已是最新版本 v0.0.1',
        showCancel: false,
        confirmText: '知道了'
      })
    }, 1000)
  },

  // 帮助中心
  showHelp() {
    const helpItems = [
      {
        title: '如何登录？',
        content: '使用您的学号和教务系统密码登录即可。密码不会被存储在服务器上。'
      },
      {
        title: '为什么登录失败？',
        content: '请检查学号和密码是否正确，确保网络连接正常。如果仍有问题，请联系客服。'
      },
      {
        title: '数据不准确怎么办？',
        content: '数据直接来源于教务系统，如有疑问请核对官方系统。统计数据仅供参考。'
      },
      {
        title: '如何保护隐私？',
        content: '我们采用HTTPS加密传输，不存储密码，您可以在设置中控制数据贡献。'
      }
    ]
    
    let content = '常见问题：\n\n'
    helpItems.forEach((item, index) => {
      content += `${index + 1}. ${item.title}\n${item.content}\n\n`
    })
    
    wx.showModal({
      title: '帮助中心',
      content: content,
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？退出后需要重新输入学号密码。',
      success: (res) => {
        if (res.confirm) {
          app.logout()
        }
      }
    })
  },

  // 个人信息点击
  onUserInfoTap() {
    const { userInfo } = this.data
    if (!userInfo) return
    
    wx.showModal({
      title: '个人信息',
      content: `学号：${userInfo.studentId}\n加入时间：${userInfo.joinDate}\n\n这是一个第三方教务辅助工具，与学校官方无关。`,
      showCancel: false,
      confirmText: '知道了'
    })
  }
})