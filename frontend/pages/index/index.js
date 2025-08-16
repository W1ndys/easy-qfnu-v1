// 首页 - 简洁灰白设计
const app = getApp()

Page({
  data: {
    userInfo: {
      name: '同学',
      studentId: '未知'
    },
    stats: {
      totalCourses: '-',
      avgGpa: '-',
      totalCredits: '-'
    },
    todayCourses: [],
    isLoading: false
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

    this.loadPageData()
  },

  onPullDownRefresh() {
    this.refreshData()
  },

  // 初始化页面
  initPage() {
    this.loadUserInfo()
    this.loadPageData()
  },

  // 加载用户信息
  loadUserInfo() {
    const studentId = app.globalData.studentId || '未知'
    this.setData({
      userInfo: {
        studentId: studentId,
        name: studentId !== '未知' ? `同学 ${studentId.slice(-4)}` : '同学'
      }
    })
  },

  // 加载页面数据
  loadPageData() {
    this.loadTodayCourses()
    this.loadStats()
  },

  // 刷新数据
  refreshData() {
    wx.showNavigationBarLoading()
    this.setData({ isLoading: true })

    Promise.all([
      this.loadTodayCourses(),
      this.loadStats()
    ]).then(() => {
      app.showSuccess('刷新成功')
    }).catch(error => {
      console.error('刷新失败:', error)
      app.showError('刷新失败')
    }).finally(() => {
      this.setData({ isLoading: false })
      wx.hideNavigationBarLoading()
      wx.stopPullDownRefresh()
    })
  },

  // 加载今日课程
  loadTodayCourses() {
    return app.request({
      url: '/schedule/today',
      method: 'GET'
    }).then(result => {
      const courses = (result.courses || []).map(course => ({
        id: course.id || Math.random(),
        courseName: course.course_name || '未知课程',
        teacher: course.teacher || '未知教师',
        location: course.location || '未知地点',
        timeSlot: `${course.start_time || ''}${course.end_time ? '-' + course.end_time : ''}`
      }))

      this.setData({ todayCourses: courses })
    }).catch(error => {
      console.error('加载今日课程失败:', error)
      this.setData({ todayCourses: [] })
    })
  },

  // 加载统计数据
  loadStats() {
    return Promise.all([
      app.request({ url: '/grades/summary', method: 'GET' }),
      app.request({ url: '/schedule/summary', method: 'GET' })
    ]).then(([gradesSummary, scheduleSummary]) => {
      this.setData({
        stats: {
          totalCourses: scheduleSummary.total_courses || '-',
          avgGpa: gradesSummary.gpa ? gradesSummary.gpa.toFixed(2) : '-',
          totalCredits: gradesSummary.total_credits || '-'
        }
      })
    }).catch(error => {
      console.error('加载统计数据失败:', error)
      this.setData({
        stats: {
          totalCourses: '-',
          avgGpa: '-',
          totalCredits: '-'
        }
      })
    })
  },

  // 导航到成绩页面
  navigateToGrades() {
    wx.switchTab({
      url: '/pages/grades/grades'
    })
  },

  // 导航到课表页面
  navigateToSchedule() {
    wx.switchTab({
      url: '/pages/schedule/schedule'
    })
  },

  // 导航到统计页面
  navigateToStats() {
    wx.switchTab({
      url: '/pages/stats/stats'
    })
  },

  // 查询课程容量
  checkCourseCapacity() {
    wx.showModal({
      title: '选课助手',
      content: '此功能正在开发中，敬请期待！',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 显示设置
  showSettings() {
    wx.switchTab({
      url: '/pages/profile/profile'
    })
  }
})