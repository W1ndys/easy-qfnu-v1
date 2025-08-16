// 课程表页面
const app = getApp()

Page({
  data: {
    schedule: [],
    currentWeek: 1,
    currentSemester: '',
    isLoading: false,
    weekDays: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    timeSlots: [
      { period: '1-2节', time: '08:00-09:40' },
      { period: '3-4节', time: '10:00-11:40' },
      { period: '5-6节', time: '14:00-15:40' },
      { period: '7-8节', time: '16:00-17:40' },
      { period: '9-10节', time: '19:00-20:40' }
    ],
    viewMode: 'week', // week, today
    todayCourses: [],
    coursesGrid: [] // 二维数组存储课程网格
  },

  onLoad() {
    this.loadSchedule()
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

  onPullDownRefresh() {
    this.refreshSchedule()
  },

  // 加载课程表
  async loadSchedule(week = null, semester = null) {
    this.setData({ isLoading: true })

    try {
      const params = {}
      if (week) params.week = week
      if (semester) params.semester = semester

      const result = await app.request({
        url: '/schedule',
        method: 'GET',
        data: params
      })

      this.setData({
        schedule: result.schedule,
        currentWeek: result.current_week,
        currentSemester: result.semester
      })

      // 构建课程网格
      this.buildCoursesGrid()

      // 如果是今日视图，加载今日课程
      if (this.data.viewMode === 'today') {
        this.loadTodayCourses()
      }

    } catch (error) {
      console.error('加载课程表失败:', error)
      app.showError(error.message || '加载课程表失败')
    } finally {
      this.setData({ isLoading: false })
    }
  },

  // 构建课程网格
  buildCoursesGrid() {
    const { schedule, timeSlots } = this.data
    const grid = []

    // 初始化网格
    for (let slotIndex = 0; slotIndex < timeSlots.length; slotIndex++) {
      grid[slotIndex] = []
      for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
        grid[slotIndex][dayIndex] = []
      }
    }

    // 填充课程数据
    schedule.forEach(course => {
      const dayIndex = course.week_day - 1
      const slotIndex = this.getSlotIndex(course.class_period)
      
      if (dayIndex >= 0 && dayIndex < 7 && slotIndex >= 0 && slotIndex < timeSlots.length) {
        grid[slotIndex][dayIndex].push(course)
      }
    })

    this.setData({ coursesGrid: grid })
  },

  // 加载今日课程
  async loadTodayCourses() {
    try {
      const result = await app.request({
        url: '/schedule/today',
        method: 'GET'
      })

      // 处理今日课程的状态
      const processedCourses = (result.courses || []).map(course => {
        const status = this.getCourseStatus(course)
        return {
          ...course,
          statusClass: status,
          statusText: this.getStatusText(status)
        }
      })

      this.setData({
        todayCourses: processedCourses
      })

    } catch (error) {
      console.error('加载今日课程失败:', error)
      this.setData({ todayCourses: [] })
    }
  },

  // 刷新课程表
  async refreshSchedule() {
    wx.showNavigationBarLoading()
    
    try {
      await this.loadSchedule(this.data.currentWeek)
      app.showSuccess('刷新成功')
    } catch (error) {
      app.showError('刷新失败')
    } finally {
      wx.hideNavigationBarLoading()
      wx.stopPullDownRefresh()
    }
  },

  // 切换视图模式
  switchViewMode(e) {
    const mode = e.currentTarget.dataset.mode
    this.setData({ viewMode: mode })

    if (mode === 'today') {
      this.loadTodayCourses()
    }
  },

  // 周次切换
  changeWeek(e) {
    const direction = e.currentTarget.dataset.direction
    let newWeek = this.data.currentWeek

    if (direction === 'prev') {
      newWeek = Math.max(1, newWeek - 1)
    } else {
      newWeek = Math.min(20, newWeek + 1)
    }

    if (newWeek !== this.data.currentWeek) {
      this.setData({ currentWeek: newWeek })
      this.loadSchedule(newWeek)
    }
  },

  // 跳转到当前周
  goToCurrentWeek() {
    this.loadSchedule()
  },



  // 获取时间段索引
  getSlotIndex(classPeriod) {
    const periodMap = {
      '1-2节': 0,
      '3-4节': 1,
      '5-6节': 2,
      '7-8节': 3,
      '9-10节': 4
    }
    return periodMap[classPeriod] ?? 0
  },

  // 课程点击
  onCourseTap(e) {
    const course = e.currentTarget.dataset.course
    
    wx.showModal({
      title: course.course_info.course_name,
      content: `时间：${course.start_time}-${course.end_time}\n地点：${course.course_info.location}\n教师：${course.course_info.teacher}\n周次：${course.weeks}`,
      showCancel: true,
      cancelText: '关闭',
      confirmText: '查课余量',
      success: (res) => {
        if (res.confirm) {
          this.checkCourseCapacity(course.course_info.course_id)
        }
      }
    })
  },

  // 查询课余量
  async checkCourseCapacity(courseId) {
    wx.showLoading({ title: '查询中...' })

    try {
      const result = await app.request({
        url: `/courses/${courseId}/capacity`,
        method: 'GET'
      })

      wx.hideLoading()

      const { course_name, total_capacity, enrolled_count, available_spots, is_full } = result

      wx.showModal({
        title: `${course_name} 课余量`,
        content: `总容量：${total_capacity}人\n已选：${enrolled_count}人\n剩余：${available_spots}人\n状态：${is_full ? '已满' : '可选'}`,
        showCancel: false,
        confirmText: '知道了'
      })

    } catch (error) {
      wx.hideLoading()
      app.showError('查询课余量失败')
    }
  },

  // 今日课程项点击
  onTodayCourseTap(e) {
    const course = e.currentTarget.dataset.course
    this.onCourseTap(e)
  },

  // 获取状态文本
  getStatusText(status) {
    const statusMap = {
      'upcoming': '即将开始',
      'soon': '马上开始',
      'ongoing': '进行中',
      'ended': '已结束'
    }
    return statusMap[status] || '未知'
  },

  // 获取课程状态
  getCourseStatus(course) {
    const now = new Date()
    const currentTime = now.getHours() * 60 + now.getMinutes()
    const [startHour, startMin] = course.start_time.split(':').map(Number)
    const [endHour, endMin] = course.end_time.split(':').map(Number)
    const startTime = startHour * 60 + startMin
    const endTime = endHour * 60 + endMin

    if (currentTime < startTime - 30) {
      return 'upcoming' // 即将开始
    } else if (currentTime >= startTime - 30 && currentTime < startTime) {
      return 'soon' // 马上开始
    } else if (currentTime >= startTime && currentTime <= endTime) {
      return 'ongoing' // 进行中
    } else {
      return 'ended' // 已结束
    }
  },

  // 导出课程表
  exportSchedule() {
    wx.showActionSheet({
      itemList: ['导出为图片', '复制课程表'],
      success: (res) => {
        if (res.tapIndex === 0) {
          this.exportAsImage()
        } else if (res.tapIndex === 1) {
          this.copySchedule()
        }
      }
    })
  },

  // 导出为图片
  exportAsImage() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  },

  // 复制课程表
  copySchedule() {
    const { schedule, currentWeek, currentSemester } = this.data
    
    let text = `Easy-QFNUJW 课程表\n学期：${currentSemester}\n周次：第${currentWeek}周\n\n`
    
    // 按天分组
    const coursesByDay = {}
    schedule.forEach(course => {
      const day = course.week_day
      if (!coursesByDay[day]) {
        coursesByDay[day] = []
      }
      coursesByDay[day].push(course)
    })

    // 生成文本
    for (let day = 1; day <= 7; day++) {
      const dayName = this.data.weekDays[day - 1]
      text += `${dayName}：\n`
      
      const dayCourses = coursesByDay[day] || []
      if (dayCourses.length === 0) {
        text += '  无课程\n'
      } else {
        dayCourses.sort((a, b) => a.start_time.localeCompare(b.start_time))
        dayCourses.forEach(course => {
          text += `  ${course.start_time}-${course.end_time} ${course.course_info.course_name} ${course.course_info.location}\n`
        })
      }
      text += '\n'
    }

    wx.setClipboardData({
      data: text,
      success: () => {
        app.showSuccess('课程表已复制到剪贴板')
      }
    })
  }
})
