// pages/grades/grades.js (最终完整版)
Page({
  data: {
    isLoading: true,  // 页面初始为加载状态
    semesters: []     // 用于存放按学期分组后的成绩
  },

  /**
   * 页面加载时运行
   */
  onLoad(options) {
    this.fetchGrades(); // 调用获取成绩的函数
  },

  /**
   * 从后端获取成绩数据的函数
   */
  fetchGrades() {
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      wx.reLaunch({ url: '/pages/login/login' });
      return;
    }

    wx.request({
      url: 'http://127.0.0.1:8000/api/v1/grades',
      method: 'GET',
      header: {
        'Authorization': 'Bearer ' + token
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          const rawGrades = res.data.data;
          // 调用我们修正好的辅助函数
          const groupedGrades = this.groupGradesBySemester(rawGrades);
          this.setData({
            semesters: groupedGrades
          });
        } else {
          const errorMessage = res.data.detail || '获取成绩失败';
          wx.showToast({ title: errorMessage, icon: 'none' });
        }
      },
      fail: (err) => {
        console.error("请求失败", err);
        wx.showToast({ title: '服务器连接失败', icon: 'none' });
      },
      complete: () => {
        this.setData({ isLoading: false });
      }
    });
  },

  /**
   * 辅助函数：将平铺的成绩列表按学期分组
   * @param {Array} grades - 从后端获取的原始成绩数组
   */
  groupGradesBySemester(grades) {
    if (!grades || grades.length === 0) {
      return [];
    }

    const semesterMap = {};

    grades.forEach(grade => {
      // ⬇️⬇️⬇️ 关键修正点：使用英文键名 'semester' ⬇️⬇️⬇️
      const semesterName = grade.semester;
      if (!semesterMap[semesterName]) {
        semesterMap[semesterName] = [];
      }
      semesterMap[semesterName].push(grade);
    });

    const result = Object.keys(semesterMap).map(semesterName => {
      return {
        semesterName: semesterName,
        grades: semesterMap[semesterName]
      };
    });

    result.sort((a, b) => b.semesterName.localeCompare(a.semesterName));

    return result;
  } // <--- 注意：作为对象最后一个属性，这里末尾没有逗号
});