// Easy-QFNUJW 微信小程序主应用文件 (测试模式)
App({
  globalData: {
    userInfo: null,
    token: null,
    apiBase: 'https://api.easy-qfnujw.com/api', // 后端API地址
    isLogin: false,
    studentId: null,
    isTestMode: true // 测试模式开关
  },

  onLaunch() {
    console.log('Easy-QFNUJW 小程序启动 (测试模式)')
    
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
      
      if (!this.globalData.isTestMode) {
        // 验证token有效性（仅非测试模式）
        this.verifyToken()
      }
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

  // 获取测试账号信息
  getTestAccounts() {
    return {
      '2020001001': {
        password: '123456',
        name: '张三',
        class: '计算机科学与技术2020级1班'
      },
      '2020001002': {
        password: '123456',
        name: '李四',
        class: '软件工程2020级2班'
      },
      '2021001001': {
        password: '123456',
        name: '王五',
        class: '数据科学与大数据技术2021级1班'
      },
      'test': {
        password: 'test',
        name: '测试用户',
        class: '测试班级'
      }
    }
  },

  // 获取模拟数据
  getMockData(studentId) {
    const baseData = {
      // 基础信息
      userInfo: {
        studentId: studentId,
        name: this.getTestAccounts()[studentId]?.name || '同学',
        class: this.getTestAccounts()[studentId]?.class || '未知班级'
      },
      
      // 成绩数据
      grades: [
        {
          id: 1,
          courseName: '高等数学A',
          score: 92,
          credits: 4,
          semester: '2023-2024-1',
          courseType: '必修',
          teacher: '李教授',
          gradePoint: 4.2
        },
        {
          id: 2,
          courseName: '线性代数',
          score: 88,
          credits: 3,
          semester: '2023-2024-1',
          courseType: '必修',
          teacher: '王教授',
          gradePoint: 3.8
        },
        {
          id: 3,
          courseName: '大学英语',
          score: 85,
          credits: 2,
          semester: '2023-2024-1',
          courseType: '必修',
          teacher: '张教授',
          gradePoint: 3.5
        },
        {
          id: 4,
          courseName: 'C程序设计',
          score: 95,
          credits: 4,
          semester: '2023-2024-1',
          courseType: '必修',
          teacher: '赵教授',
          gradePoint: 4.5
        },
        {
          id: 5,
          courseName: '大学物理',
          score: 78,
          credits: 3,
          semester: '2023-2024-2',
          courseType: '必修',
          teacher: '陈教授',
          gradePoint: 2.8
        }
      ],
      
      // 课表数据
      schedule: [
        {
          id: 1,
          course_name: '高等数学A',
          teacher: '李教授',
          location: '教学楼A101',
          day_of_week: 1,
          start_time: '08:00',
          end_time: '09:40',
          week_start: 1,
          week_end: 16,
          course_type: '必修'
        },
        {
          id: 2,
          course_name: 'C程序设计',
          teacher: '赵教授',
          location: '机房B201',
          day_of_week: 2,
          start_time: '10:00',
          end_time: '11:40',
          week_start: 1,
          week_end: 16,
          course_type: '必修'
        },
        {
          id: 3,
          course_name: '大学英语',
          teacher: '张教授',
          location: '教学楼C102',
          day_of_week: 3,
          start_time: '14:00',
          end_time: '15:40',
          week_start: 1,
          week_end: 16,
          course_type: '必修'
        },
        {
          id: 4,
          course_name: '线性代数',
          teacher: '王教授',
          location: '教学楼A203',
          day_of_week: 4,
          start_time: '08:00',
          end_time: '09:40',
          week_start: 1,
          week_end: 16,
          course_type: '必修'
        },
        {
          id: 5,
          course_name: '大学物理',
          teacher: '陈教授',
          location: '教学楼B305',
          day_of_week: 5,
          start_time: '10:00',
          end_time: '11:40',
          week_start: 1,
          week_end: 16,
          course_type: '必修'
        }
      ]
    }
    
    return baseData
  },

  // 登录 (测试模式)
  login(studentId, password) {
    return new Promise((resolve, reject) => {
      wx.showLoading({
        title: '登录中...'
      })

      if (this.globalData.isTestMode) {
        // 测试模式登录
        const testAccounts = this.getTestAccounts()
        
        setTimeout(() => {
          wx.hideLoading()
          
          if (testAccounts[studentId] && testAccounts[studentId].password === password) {
            // 模拟成功登录
            const mockToken = `mock_token_${Date.now()}`
            
            // 保存登录信息
            wx.setStorageSync('access_token', mockToken)
            wx.setStorageSync('student_id', studentId)
            wx.setStorageSync('login_time', Date.now())
            
            // 更新全局数据
            this.globalData.token = mockToken
            this.globalData.studentId = studentId
            this.globalData.isLogin = true
            
            resolve({
              access_token: mockToken,
              user: testAccounts[studentId]
            })
          } else {
            reject(new Error('学号或密码错误'))
          }
        }, 1000) // 模拟网络延迟
        
      } else {
        // 正常API请求
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
      }
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
      if (this.globalData.isTestMode) {
        // 测试模式，返回模拟数据
        this.handleMockRequest(options, resolve, reject)
        return
      }
      
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

  // 处理模拟请求
  handleMockRequest(options, resolve, reject) {
    const mockData = this.getMockData(this.globalData.studentId)
    
    setTimeout(() => {
      try {
        const url = options.url
        
        if (url.includes('/grades')) {
          if (url.includes('/summary')) {
            // 成绩摘要
            const grades = mockData.grades
            const totalCredits = grades.reduce((sum, g) => sum + g.credits, 0)
            const weightedSum = grades.reduce((sum, g) => sum + g.gradePoint * g.credits, 0)
            const gpa = (weightedSum / totalCredits).toFixed(2)
            
            resolve({
              total_courses: grades.length,
              total_credits: totalCredits,
              gpa: parseFloat(gpa)
            })
          } else {
            // 成绩列表
            resolve({
              grades: mockData.grades,
              summary: {
                total_courses: mockData.grades.length,
                total_credits: mockData.grades.reduce((sum, g) => sum + g.credits, 0),
                gpa: 3.6
              }
            })
          }
        } else if (url.includes('/schedule')) {
          if (url.includes('/today')) {
            // 今日课程
            const today = new Date().getDay()
            const todayCourses = mockData.schedule.filter(c => c.day_of_week === today)
            resolve({
              courses: todayCourses
            })
          } else if (url.includes('/summary')) {
            // 课表摘要
            resolve({
              total_courses: mockData.schedule.length,
              this_week: mockData.schedule.length
            })
          } else {
            // 完整课表
            resolve({
              schedule: mockData.schedule,
              current_week: 8
            })
          }
        } else if (url.includes('/stats')) {
          // 统计数据
          resolve({
            grade_distribution: {
              excellent: 2,
              good: 2,
              average: 1,
              poor: 0
            },
            class_rank: {
              rank: 15,
              total: 120,
              percentile: 0.875,
              percentileText: '87.5'
            }
          })
        } else {
          resolve({})
        }
      } catch (error) {
        reject(error)
      }
    }, 500) // 模拟网络延迟
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