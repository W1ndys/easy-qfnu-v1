// 数据统计页面
const app = getApp()

Page({
  data: {
    activeTab: 'course', // course, rank, contribute
    courseStats: null,
    classRank: null,
    contributionEnabled: false,
    searchCourseId: '',
    courseHistory: [],
    isLoading: false
  },

  onLoad() {
    this.checkContributionStatus()
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

  // 切换标签页
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({ activeTab: tab })
  },

  // 检查贡献状态
  async checkContributionStatus() {
    try {
      // 这里应该从用户信息中获取贡献偏好
      // 暂时模拟
      this.setData({ contributionEnabled: false })
    } catch (error) {
      console.error('检查贡献状态失败:', error)
    }
  },

  // 搜索课程统计
  onSearchInput(e) {
    this.setData({ searchCourseId: e.detail.value })
  },

  async searchCourseStats() {
    const { searchCourseId } = this.data
    
    if (!searchCourseId.trim()) {
      app.showError('请输入课程ID')
      return
    }

    this.setData({ isLoading: true })

    try {
      const result = await app.request({
        url: '/stats/course/',
        method: 'GET',
        data: { course_id: searchCourseId.trim() }
      })

      this.setData({ courseStats: result })

      // 添加到搜索历史
      this.addToHistory(searchCourseId.trim(), result.course_name)

    } catch (error) {
      console.error('搜索课程统计失败:', error)
      app.showError(error.message || '搜索失败')
    } finally {
      this.setData({ isLoading: false })
    }
  },

  // 添加到搜索历史
  addToHistory(courseId, courseName) {
    const { courseHistory } = this.data
    const newItem = { course_id: courseId, course_name: courseName, time: new Date().toLocaleString() }
    
    // 移除重复项
    const filteredHistory = courseHistory.filter(item => item.course_id !== courseId)
    
    // 添加到开头，限制最多10条
    const updatedHistory = [newItem, ...filteredHistory].slice(0, 10)
    
    this.setData({ courseHistory: updatedHistory })
    
    // 保存到本地存储
    wx.setStorageSync('course_search_history', updatedHistory)
  },

  // 加载搜索历史
  loadSearchHistory() {
    const history = wx.getStorageSync('course_search_history') || []
    this.setData({ courseHistory: history })
  },

  // 历史项点击
  onHistoryItemTap(e) {
    const courseId = e.currentTarget.dataset.courseid
    this.setData({ searchCourseId: courseId })
    this.searchCourseStats()
  },

  // 清除搜索历史
  clearSearchHistory() {
    wx.showModal({
      title: '确认清除',
      content: '确定要清除所有搜索历史吗？',
      success: (res) => {
        if (res.confirm) {
          this.setData({ courseHistory: [] })
          wx.removeStorageSync('course_search_history')
          app.showSuccess('已清除搜索历史')
        }
      }
    })
  },

  // 查询班内排名
  async queryClassRank() {
    const { searchCourseId } = this.data
    
    if (!searchCourseId.trim()) {
      app.showError('请先搜索课程')
      return
    }

    this.setData({ isLoading: true })

    try {
      const result = await app.request({
        url: '/stats/class_rank/',
        method: 'GET',
        data: { course_id: searchCourseId.trim() }
      })

      // 处理百分位显示
      if (result.percentile) {
        result.percentileText = (result.percentile * 100).toFixed(1)
      }

      this.setData({ classRank: result })

    } catch (error) {
      console.error('查询班内排名失败:', error)
      
      if (error.message && error.message.includes('数据量不足')) {
        app.showError('班内数据量不足，无法计算排名')
      } else {
        app.showError(error.message || '查询失败')
      }
    } finally {
      this.setData({ isLoading: false })
    }
  },

  // 切换贡献设置
  async toggleContribution(e) {
    const enabled = e.detail.value

    try {
      await app.request({
        url: '/stats/contribution/preference',
        method: 'POST',
        data: { enabled }
      })

      this.setData({ contributionEnabled: enabled })
      
      if (enabled) {
        app.showSuccess('已开启数据贡献')
        this.showContributionInfo()
      } else {
        app.showSuccess('已关闭数据贡献')
      }

    } catch (error) {
      console.error('更新贡献设置失败:', error)
      app.showError('设置失败')
      
      // 恢复开关状态
      this.setData({ contributionEnabled: !enabled })
    }
  },

  // 显示贡献说明
  showContributionInfo() {
    wx.showModal({
      title: '数据贡献说明',
      content: '开启数据贡献后，您的成绩信息将以匿名形式用于计算课程平均分和班内排名。这将帮助其他同学获得更准确的数据参考。\n\n您的隐私将得到严格保护，所有数据都经过匿名化处理。',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 手动贡献成绩
  async contributeGrades() {
    if (!this.data.contributionEnabled) {
      wx.showModal({
        title: '需要开启数据贡献',
        content: '请先在设置中开启数据贡献功能',
        showCancel: false,
        confirmText: '知道了'
      })
      return
    }

    wx.showLoading({ title: '贡献中...' })

    try {
      // 这里应该获取用户的成绩数据并提交
      // 暂时模拟
      await new Promise(resolve => setTimeout(resolve, 1000))

      wx.hideLoading()
      app.showSuccess('成绩数据贡献成功')

    } catch (error) {
      wx.hideLoading()
      console.error('贡献成绩失败:', error)
      app.showError('贡献失败')
    }
  },

  // 查看统计详情
  showStatsDetail() {
    const { courseStats } = this.data
    if (!courseStats) return

    let content = `课程：${courseStats.course_name}\n`
    
    if (courseStats.historical) {
      content += `\n历史数据：\n平均分：${courseStats.historical.average_score}\n样本数：${courseStats.historical.sample_count}`
    }
    
    if (courseStats.crowdsourced) {
      content += `\n\n众包数据：\n平均分：${courseStats.crowdsourced.average_score}\n样本数：${courseStats.crowdsourced.sample_count}`
    }
    
    if (courseStats.combined_average) {
      content += `\n\n综合平均分：${courseStats.combined_average}`
    }

    wx.showModal({
      title: '课程统计详情',
      content: content,
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 查看排名详情
  showRankDetail() {
    const { classRank } = this.data
    if (!classRank) return

    const content = `课程：${classRank.course_name}\n您的成绩：${classRank.user_score}分\n班内排名：${classRank.rank}\n百分位：${(classRank.percentile * 100).toFixed(1)}%\n班级平均：${classRank.class_average}分\n${classRank.is_above_average ? '超过平均水平' : '低于平均水平'}`

    wx.showModal({
      title: '班内排名详情',
      content: content,
      showCancel: false,
      confirmText: '知道了'
    })
  }
})
