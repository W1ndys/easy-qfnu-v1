// 首页
const app = getApp()

Page({
  data: {
    userInfo: null,
    todayCourses: [],
    gradesSummary: null,
    isLoading: false,
    currentTime: '',
    greeting: '',
    weatherInfo: null,
    quickActions: [
      { id: 'grades', name: '成绩查询', icon: '📊', path: '/pages/grades/grades' },
      { id: 'schedule', name: '课程表', icon: '📅', path: '/pages/schedule/schedule' },
      { id: 'stats', name: '数据统计', icon: '📈', path: '/pages/stats/stats' },
      { id: 'capacity', name: '课余量', icon: '👥', path: '/pages/capacity/capacity' }
    ],
    announcements: [
      { id: 1, title: '欢迎使用Easy-QFNUJW', content: '这是一个第三方教务辅助工具，帮助您更便捷地查看教务信息。', time: '2024-01-15' }
    ]
  },

  onLoad() {
    this.initPage()
  },

  onShow() {
    // 检查登录状态
    if (!app.globalData.isLogin) {
      wx.reLaunch({
        url: '/pages/login/login'
      })
      return
    }

    this.updateTime()
    this.loadTodayCourses()
  },

  onPullDownRefresh() {
    this.refreshData()
  },

  // 初始化页面
  initPage() {
    this.updateTime()
    this.setGreeting()
    this.loadUserInfo()
    this.loadTodayCourses()
    this.loadGradesSummary()
  },

  // 刷新数据
  async refreshData() {
    wx.showNavigationBarLoading()
    
    try {
      await Promise.all([
        this.loadTodayCourses(),
        this.loadGradesSummary()
      ])
      
      app.showSuccess('刷新成功')
    } catch (error) {
      console.error('刷新失败:', error)
      app.showError('刷新失败')
    } finally {
      wx.hideNavigationBarLoading()
      wx.stopPullDownRefresh()
    }
  },

  // 更新当前时间
  updateTime() {
    const now = new Date()
    const timeString = now.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
    const dateString = now.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    })
    
    this.setData({
      currentTime: `${dateString} ${timeString}`
    })

    // 每分钟更新一次时间
    setTimeout(() => {
      this.updateTime()
    }, 60000)
  },

  // 设置问候语
  setGreeting() {
    const hour = new Date().getHours()
    let greeting = ''
    
    if (hour >= 5 && hour < 12) {
      greeting = '早上好'
    } else if (hour >= 12 && hour < 18) {
      greeting = '下午好'
    } else {
      greeting = '晚上好'
    }
    
    this.setData({ greeting })
  },

  // 加载用户信息
  loadUserInfo() {
    const studentId = app.globalData.studentId
    this.setData({
      userInfo: {
        studentId: studentId,
        name: `同学 ${studentId.slice(-4)}` // 显示学号后4位
      }
    })
  },

  // 加载今日课程
  async loadTodayCourses() {
    try {
      const result = await app.request({
        url: '/schedule/today',
        method: 'GET'
      })

      this.setData({
        todayCourses: result.courses || []
      })

    } catch (error) {
      console.error('加载今日课程失败:', error)
      // 不显示错误提示，避免打扰用户
    }
  },

  // 加载成绩摘要
  async loadGradesSummary() {
    try {
      const result = await app.request({
        url: '/grades/summary',
        method: 'GET'
      })

      this.setData({
        gradesSummary: result
      })

    } catch (error) {
      console.error('加载成绩摘要失败:', error)
      // 不显示错误提示
    }
  },

  // 快捷操作点击
  onQuickActionTap(e) {
    const { path } = e.currentTarget.dataset
    
    if (path.startsWith('/pages/')) {
      // TabBar页面
      if (['grades', 'schedule', 'stats'].some(tab => path.includes(tab))) {
        wx.switchTab({ url: path })
      } else {
        wx.navigateTo({ url: path })
      }
    }
  },

  // 课程卡片点击
  onCourseTap(e) {
    const course = e.currentTarget.dataset.course
    
    wx.showModal({
      title: course.course_info.course_name,
      content: `教师：${course.course_info.teacher}\n地点：${course.course_info.location}\n时间：${course.start_time}-${course.end_time}`,
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 查看更多课程
  viewMoreCourses() {
    wx.switchTab({
      url: '/pages/schedule/schedule'
    })
  },

  // 查看成绩详情
  viewGradesDetail() {
    wx.switchTab({
      url: '/pages/grades/grades'
    })
  },

  // 公告点击
  onAnnouncementTap(e) {
    const announcement = e.currentTarget.dataset.announcement
    
    wx.showModal({
      title: announcement.title,
      content: announcement.content,
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 进入设置页面
  goToSettings() {
    wx.switchTab({
      url: '/pages/profile/profile'
    })
  }
})
