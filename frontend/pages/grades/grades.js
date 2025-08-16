// 成绩查询页面
const app = getApp()

Page({
  data: {
    grades: [],
    gradeStats: null,
    isLoading: false,
    selectedSemester: '',
    semesters: [],
    showSemesterPicker: false,
    sortBy: 'semester', // semester, score, credit
    sortOrder: 'desc', // asc, desc
    semesterSortIcon: '',
    scoreSortIcon: '',
    creditSortIcon: ''
  },

  onLoad() {
    this.loadGrades()
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
    this.refreshGrades()
  },

  // 加载成绩数据
  async loadGrades(semester = '') {
    this.setData({ isLoading: true })

    try {
      const params = {}
      if (semester) {
        params.semester = semester
      }

      const result = await app.request({
        url: '/grades',
        method: 'GET',
        data: params
      })

      // 提取学期列表
      const semesters = [...new Set(result.grades.map(grade => grade.semester))]
        .sort().reverse()

      this.setData({
        grades: result.grades,
        gradeStats: result.stats,
        semesters: semesters,
        selectedSemester: semester
      })

      this.updateSortIcons()
      this.sortGrades()

    } catch (error) {
      console.error('加载成绩失败:', error)
      app.showError(error.message || '加载成绩失败')
    } finally {
      this.setData({ isLoading: false })
    }
  },

  // 刷新成绩
  async refreshGrades() {
    wx.showNavigationBarLoading()
    
    try {
      await this.loadGrades(this.data.selectedSemester)
      app.showSuccess('刷新成功')
    } catch (error) {
      app.showError('刷新失败')
    } finally {
      wx.hideNavigationBarLoading()
      wx.stopPullDownRefresh()
    }
  },

  // 学期选择器
  showSemesterPicker() {
    this.setData({ showSemesterPicker: true })
  },

  hideSemesterPicker() {
    this.setData({ showSemesterPicker: false })
  },

  onSemesterChange(e) {
    const index = e.detail.value
    const semester = index === 0 ? '' : this.data.semesters[index - 1]
    
    this.setData({ 
      selectedSemester: semester,
      showSemesterPicker: false
    })
    
    this.loadGrades(semester)
  },

  // 排序功能
  onSortChange(e) {
    const { sort } = e.currentTarget.dataset
    let { sortBy, sortOrder } = this.data

    if (sortBy === sort) {
      sortOrder = sortOrder === 'asc' ? 'desc' : 'asc'
    } else {
      sortBy = sort
      sortOrder = sort === 'score' ? 'desc' : 'asc'
    }

    this.setData({ sortBy, sortOrder })
    this.updateSortIcons()
    this.sortGrades()
  },

  // 更新排序图标
  updateSortIcons() {
    const { sortBy, sortOrder } = this.data
    const upIcon = ' ↑'
    const downIcon = ' ↓'
    
    this.setData({
      semesterSortIcon: sortBy === 'semester' ? (sortOrder === 'asc' ? upIcon : downIcon) : '',
      scoreSortIcon: sortBy === 'score' ? (sortOrder === 'asc' ? upIcon : downIcon) : '',
      creditSortIcon: sortBy === 'credit' ? (sortOrder === 'asc' ? upIcon : downIcon) : ''
    })
  },

  // 排序成绩
  sortGrades() {
    const { grades, sortBy, sortOrder } = this.data
    
    const sortedGrades = [...grades].sort((a, b) => {
      let aValue, bValue

      switch (sortBy) {
        case 'score':
          aValue = a.score
          bValue = b.score
          break
        case 'credit':
          aValue = a.credit
          bValue = b.credit
          break
        case 'semester':
        default:
          aValue = a.semester
          bValue = b.semester
          break
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })

    this.setData({ grades: sortedGrades })
  },

  // 成绩详情
  showGradeDetail(e) {
    const grade = e.currentTarget.dataset.grade
    
    let gradeLevel = '不及格'
    if (grade.score >= 90) gradeLevel = '优秀'
    else if (grade.score >= 80) gradeLevel = '良好'
    else if (grade.score >= 70) gradeLevel = '中等'
    else if (grade.score >= 60) gradeLevel = '及格'

    wx.showModal({
      title: grade.course_name,
      content: `成绩：${grade.score}分 (${gradeLevel})\n学分：${grade.credit}\n绩点：${grade.grade_point}\n学期：${grade.semester}${grade.teacher ? `\n教师：${grade.teacher}` : ''}`,
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 查看统计详情
  showStatsDetail() {
    if (!this.data.gradeStats) return

    const stats = this.data.gradeStats
    const content = `总课程：${stats.total_courses}门\n总学分：${stats.total_credits}\n总GPA：${stats.gpa}\n加权平均：${stats.weighted_average}分\n优秀课程：${stats.excellent_courses}门\n挂科课程：${stats.failed_courses}门`

    wx.showModal({
      title: '成绩统计',
      content: content,
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 导出成绩
  exportGrades() {
    wx.showActionSheet({
      itemList: ['导出为图片', '复制成绩单'],
      success: (res) => {
        if (res.tapIndex === 0) {
          this.exportAsImage()
        } else if (res.tapIndex === 1) {
          this.copyGrades()
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

  // 复制成绩单
  copyGrades() {
    const { grades, gradeStats } = this.data
    
    let text = `Easy-QFNUJW 成绩单\n\n`
    
    if (gradeStats) {
      text += `总GPA：${gradeStats.gpa}\n`
      text += `加权平均：${gradeStats.weighted_average}分\n`
      text += `总学分：${gradeStats.total_credits}\n\n`
    }
    
    text += `课程成绩明细：\n`
    grades.forEach(grade => {
      text += `${grade.course_name}: ${grade.score}分 (${grade.credit}学分)\n`
    })

    wx.setClipboardData({
      data: text,
      success: () => {
        app.showSuccess('成绩单已复制到剪贴板')
      }
    })
  }
})
