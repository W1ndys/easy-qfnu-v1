<template>
  <view class="page-container page-rounded-container">
    <!-- 背景装饰 -->
    <view class="background-decoration">
      <view class="circle circle-1"></view>
      <view class="circle circle-2"></view>
      <view class="circle circle-3"></view>
    </view>

    <!-- 页面头部 -->
    <view class="page-header">
      <view class="header-content">
        <text class="page-title">平均分查询</text>
        <text class="page-subtitle">Academic Score Analysis</text>
      </view>
    </view>

    <!-- 主内容区域 -->
    <view class="content-wrapper">
      <!-- 搜索表单卡片 -->
      <view class="search-card modern-card">
        <view class="card-header">
          <view class="header-icon">
            <uni-icons type="search" size="24" color="#7f4515"></uni-icons>
          </view>
          <view class="header-text">
            <text class="card-title">课程信息查询</text>
            <text class="card-subtitle">输入课程信息开始查询</text>
          </view>
        </view>

        <view class="form-content">
          <view class="form-group">
            <view class="input-label">
              <uni-icons type="book" size="20" color="#495057"></uni-icons>
              <text>课程名称/代码</text>
            </view>
            <view class="input-wrapper">
              <input
                class="modern-input"
                :class="{
                  'input-error': courseError,
                  'input-focus': courseFocused,
                }"
                v-model="searchForm.course"
                placeholder="请输入课程名称或课程代码（至少3个字符）"
                @confirm="handleSearch"
                @input="validateCourse"
                @focus="courseFocused = true"
                @blur="courseFocused = false" />
              <view
                class="input-line"
                :class="{ active: courseFocused }"></view>
            </view>
            <text class="input-hint" :class="{ 'hint-error': courseError }">
              {{ courseHint }}
            </text>
          </view>

          <view class="form-group">
            <view class="input-label">
              <uni-icons type="person" size="20" color="#495057"></uni-icons>
              <text>教师姓名（选填）</text>
            </view>
            <view class="input-wrapper">
              <input
                class="modern-input"
                :class="{
                  'input-error': teacherError,
                  'input-focus': teacherFocused,
                }"
                v-model="searchForm.teacher"
                placeholder="不填则查询所有老师（至少2个字符）"
                @confirm="handleSearch"
                @input="validateTeacher"
                @focus="teacherFocused = true"
                @blur="teacherFocused = false" />
              <view
                class="input-line"
                :class="{ active: teacherFocused }"></view>
            </view>
            <text
              class="input-hint"
              :class="{ 'hint-error': teacherError }"
              v-if="searchForm.teacher.trim()">
              {{ teacherHint }}
            </text>
          </view>

          <view class="button-group">
            <button
              class="action-btn primary-btn"
              @click="handleSearch"
              :loading="loading"
              :disabled="!canSearch">
              <uni-icons
                type="search"
                size="20"
                color="#ffffff"
                v-if="!loading"></uni-icons>
              <text>{{ loading ? "查询中..." : "开始查询" }}</text>
            </button>
            <button class="action-btn secondary-btn" @click="handleReset">
              <uni-icons type="refresh" size="20" color="#495057"></uni-icons>
              <text>重置</text>
            </button>
          </view>
        </view>
      </view>

      <!-- 查询结果 -->
      <view class="results-section" v-if="hasResults">
        <view class="results-header">
          <view class="results-info">
            <text class="results-title">查询结果</text>
            <text class="results-count"
              >共找到 {{ Object.keys(resultData).length }} 门课程</text
            >
          </view>
        </view>

        <view
          class="course-card modern-card"
          v-for="(teachers, courseName) in resultData"
          :key="courseName">
          <view class="course-header">
            <view class="course-info">
              <view class="course-icon">
                <uni-icons type="book" size="20" color="#7f4515"></uni-icons>
              </view>
              <text class="course-name">{{ courseName }}</text>
            </view>
          </view>

          <view class="course-content">
            <view
              class="teacher-section"
              v-for="(teacherName, teacherIndex) in Object.keys(teachers)"
              :key="teacherName">
              <view class="teacher-header">
                <view class="teacher-info">
                  <view class="teacher-avatar">
                    <uni-icons
                      type="person"
                      size="16"
                      color="#7f4515"></uni-icons>
                  </view>
                  <text class="teacher-name">{{ teacherName }}</text>
                </view>
              </view>

              <view class="semester-list">
                <view
                  class="semester-item"
                  v-for="(data, semester) in teachers[teacherName]"
                  :key="semester">
                  <view class="semester-info">
                    <text class="semester-name">{{ semester }}</text>
                    <text class="update-time" v-if="data.update_time">
                      {{ formatTime(data.update_time) }}
                    </text>
                  </view>
                  <view class="score-info">
                    <view class="score-item">
                      <text class="score-label">平均分</text>
                      <text class="score-value primary">{{ data.average_score.toFixed(2) }}</text>
                    </view>
                    <view class="score-item">
                      <text class="score-label">人数</text>
                      <text class="score-value secondary">{{ data.student_count }}</text>
                    </view>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state modern-card" v-else-if="searched && !loading">
        <view class="empty-content">
          <view class="empty-icon">
            <uni-icons type="info" size="80" color="#adb5bd"></uni-icons>
          </view>
          <text class="empty-title">未找到相关数据</text>
          <text class="empty-subtitle">{{ emptyMessage }}</text>
          <button class="action-btn primary-btn retry-btn" @click="handleReset">
            <uni-icons type="refresh" size="20" color="#ffffff"></uni-icons>
            <text>重新搜索</text>
          </button>
        </view>
      </view>

      <!-- 初始状态 -->
      <view class="initial-state modern-card" v-else-if="!searched && !loading">
        <view class="initial-content">
          <view class="initial-icon">
            <uni-icons type="search" size="80" color="#7f4515"></uni-icons>
          </view>
          <text class="initial-title">欢迎使用平均分查询</text>
          <text class="initial-subtitle">请输入课程信息开始查询学术数据</text>
        </view>
      </view>

      <!-- 加载状态 -->
      <view class="loading-state modern-card" v-else-if="loading">
        <view class="loading-content">
          <view class="loading-spinner">
            <uni-icons
              type="spinner-cycle"
              size="60"
              color="#7f4515"></uni-icons>
          </view>
          <text class="loading-text">正在查询数据...</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      searchForm: {
        course: "",
        teacher: "",
      },
      resultData: {},
      loading: false,
      searched: false,
      emptyMessage: "未找到相关数据",
      courseError: false,
      teacherError: false,
      courseFocused: false,
      teacherFocused: false,
    };
  },

  computed: {
    hasResults() {
      return Object.keys(this.resultData).length > 0;
    },

    courseHint() {
      const length = this.searchForm.course.trim().length;
      if (length === 0) {
        return "请输入课程名称或代码";
      } else if (length < 3) {
        return `至少需要3个字符，当前${length}个字符`;
      } else {
        return `已输入${length}个字符`;
      }
    },

    teacherHint() {
      const length = this.searchForm.teacher.trim().length;
      if (length === 0) {
        return "";
      } else if (length < 2) {
        return `至少需要2个字符，当前${length}个字符`;
      } else {
        return `已输入${length}个字符`;
      }
    },

    canSearch() {
      const courseLength = this.searchForm.course.trim().length;
      const teacherLength = this.searchForm.teacher.trim().length;

      return courseLength >= 3 && (teacherLength === 0 || teacherLength >= 2);
    },
  },

  onLoad() {
    uni.setNavigationBarTitle({
      title: "平均分查询",
    });
  },

  methods: {
    validateCourse() {
      const length = this.searchForm.course.trim().length;
      this.courseError = length > 0 && length < 3;
    },

    validateTeacher() {
      const length = this.searchForm.teacher.trim().length;
      this.teacherError = length > 0 && length < 2;
    },

    async handleSearch() {
      if (!this.searchForm.course.trim()) {
        uni.showToast({
          title: "请输入课程名称或代码",
          icon: "none",
        });
        return;
      }

      if (this.searchForm.course.trim().length < 3) {
        uni.showToast({
          title: "课程名称至少需要3个字符",
          icon: "none",
        });
        return;
      }

      if (
        this.searchForm.teacher.trim() &&
        this.searchForm.teacher.trim().length < 2
      ) {
        uni.showToast({
          title: "教师姓名至少需要2个字符",
          icon: "none",
        });
        return;
      }

      this.loading = true;
      this.searched = true;

      try {
        const params = {
          course: this.searchForm.course.trim(),
        };

        if (this.searchForm.teacher.trim()) {
          params.teacher = this.searchForm.teacher.trim();
        }

        const response = await this.queryAverageScores(params);

        if (response.code === 200) {
          this.resultData = response.data;
          if (!this.hasResults) {
            this.emptyMessage = "未找到相关数据";
          }
        } else {
          this.resultData = {};
          this.emptyMessage = response.message || "查询失败";
          uni.showToast({
            title: this.emptyMessage,
            icon: "none",
          });
        }
      } catch (error) {
        console.error("查询平均分失败:", error);
        this.resultData = {};

        // 显示更详细的错误信息
        let errorMessage = "网络错误，请重试";
        if (error.message) {
          if (error.message.includes("HTTP 422")) {
            errorMessage = "输入参数格式错误，请检查输入内容";
          } else if (error.message.includes("HTTP 400")) {
            errorMessage = "请求参数错误，请检查输入内容";
          } else if (error.message.includes("HTTP 500")) {
            errorMessage = "服务器内部错误，请稍后重试";
          } else if (error.message.includes("HTTP")) {
            errorMessage = `请求失败: ${error.message}`;
          }
        }

        this.emptyMessage = errorMessage;
        uni.showToast({
          title: errorMessage,
          icon: "none",
          duration: 3000,
        });
      } finally {
        this.loading = false;
      }
    },

    handleReset() {
      this.searchForm = {
        course: "",
        teacher: "",
      };
      this.resultData = {};
      this.searched = false;
      this.courseError = false;
      this.teacherError = false;
    },

    async queryAverageScores(params) {
      // 统一从 App.globalData 读取 API 基础域名
      const baseURL = getApp().globalData.apiBaseURL;
      const token = uni.getStorageSync("token");

      if (!token) {
        uni.showToast({
          title: "请先登录",
          icon: "none",
        });
        uni.reLaunch({ url: "/pages/index/index" });
        return;
      }

      return new Promise((resolve, reject) => {
        uni.request({
          url: `${baseURL}/api/v1/average-scores`,
          method: "GET",
          data: params,
          header: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          success: (res) => {
            if (res.statusCode === 401) {
              uni.showToast({
                title: "登录已过期，请重新登录",
                icon: "none",
              });
              uni.removeStorageSync("token");
              uni.reLaunch({ url: "/pages/index/index" });
              return;
            }

            // 处理其他非200状态码
            if (res.statusCode !== 200) {
              console.error("API请求失败:", res);
              reject(
                new Error(
                  `HTTP ${res.statusCode}: ${res.data?.message || "请求失败"}`
                )
              );
              return;
            }

            resolve(res.data);
          },
          fail: (err) => {
            reject(err);
          },
        });
      });
    },

    formatTime(timeStr) {
      if (!timeStr) return "";
      // 简单的时间格式化，您可以根据实际格式调整
      return timeStr.replace("T", " ").split(".")[0];
    },
  },
};
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

// 页面容器
.page-container {
  min-height: 100vh;
  background: #f7f8fa;
  position: relative;
  overflow: hidden;
}

// 外层圆角容器（与其他页面一致）
.page-rounded-container {
  background: #ffffff;
  border-radius: 40rpx;
  padding: 20rpx 20rpx 30rpx;
  box-shadow: 0 20rpx 60rpx var(--shadow-light);
  border: 1rpx solid var(--border-light);
}

// 背景装饰
.background-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(127, 69, 21, 0.06);

  &.circle-1 {
    width: 200rpx;
    height: 200rpx;
    top: 10%;
    right: -50rpx;
    animation: float 6s ease-in-out infinite;
  }

  &.circle-2 {
    width: 150rpx;
    height: 150rpx;
    bottom: 20%;
    left: -30rpx;
    animation: float 8s ease-in-out infinite reverse;
  }

  &.circle-3 {
    width: 100rpx;
    height: 100rpx;
    top: 30%;
    left: 20%;
    animation: float 4s ease-in-out infinite;
  }
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20rpx) rotate(180deg);
  }
}

// 页面头部
.page-header {
  padding: 40rpx 30rpx 30rpx;
  position: relative;
  z-index: 1;
}

.header-content {
  text-align: center;
}

.page-title {
  display: block;
  font-size: 44rpx;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 12rpx;
  letter-spacing: 1rpx;
}

.page-subtitle {
  display: block;
  font-size: 24rpx;
  color: #7f8c8d;
  font-style: italic;
}

// 内容区域
.content-wrapper {
  padding: 0 30rpx 30rpx;
  position: relative;
  z-index: 1;
}

// 现代化卡片
.modern-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20rpx);
  border-radius: var(--radius-large);
  border: 1rpx solid var(--border-light);
  box-shadow: 0 20rpx 60rpx var(--shadow-light);
  margin-bottom: 40rpx;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4rpx);
    box-shadow: 0 24rpx 80rpx var(--shadow-medium);
  }
}

// 搜索卡片
.search-card {
  padding: 40rpx;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 24rpx;
  margin-bottom: 50rpx;
}

.header-icon {
  width: 80rpx;
  height: 80rpx;
  background: rgba(127, 69, 21, 0.08);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-text {
  flex: 1;
}

.card-title {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8rpx;
}

.card-subtitle {
  display: block;
  font-size: 24rpx;
  color: var(--text-secondary);
}

// 表单样式
.form-group {
  margin-bottom: 50rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

.input-label {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 20rpx;
  font-size: 28rpx;
  font-weight: 600;
  color: var(--text-primary);
}

.input-wrapper {
  position: relative;
}

.modern-input {
  width: 100%;
  height: 88rpx;
  border: 2rpx solid #e9ecef;
  border-radius: var(--radius-small);
  padding: 0 24rpx;
  font-size: 28rpx;
  color: var(--text-primary);
  background: #f8fafc;
  transition: all 0.3s ease;
  box-sizing: border-box;

  &:focus {
    border-color: #7f4515;
    background: #ffffff;
    box-shadow: 0 0 0 6rpx rgba(127, 69, 21, 0.1);
  }

  &.input-error {
    border-color: #dc3545;
    background: rgba(220, 53, 69, 0.05);
  }
}

.input-line {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4rpx;
  background: linear-gradient(90deg, #7f4515, #8c5527);
  border-radius: 2rpx;
  transform: scaleX(0);
  transition: transform 0.3s ease;

  &.active {
    transform: scaleX(1);
  }
}

.input-hint {
  display: block;
  font-size: 22rpx;
  color: var(--text-light);
  margin-top: 12rpx;
  transition: color 0.3s ease;

  &.hint-error {
    color: #dc3545;
  }
}

// 按钮组
.button-group {
  display: flex;
  gap: 24rpx;
  margin-top: 60rpx;
}

.action-btn {
  flex: 1;
  height: 72rpx;
  border-radius: 9999rpx;
  font-size: 26rpx;
  padding: 16rpx 24rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  transition: all 0.3s ease;
  border: none;

  &::after {
    border: none;
  }

  &:active {
    transform: scale(0.95);
  }

  text {
    font-weight: inherit;
  }
}

.primary-btn {
  background: linear-gradient(135deg, #7f4515, #8c5527);
  color: #ffffff;
  box-shadow: 0 8rpx 24rpx rgba(127, 69, 21, 0.25);

  &:disabled {
    background: #adb5bd;
    color: #6c757d;
    box-shadow: none;
  }

  &:active:not(:disabled) {
    box-shadow: 0 4rpx 12rpx rgba(155, 4, 0, 0.4);
  }
}

.secondary-btn {
  background: #f8f9fa;
  color: var(--text-primary);
  border: 2rpx solid #e9ecef;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);

  &:active {
    background: #e9ecef;
    border-color: #dee2e6;
  }
}

// 结果区域
.results-header {
  padding: 20rpx 30rpx;
  text-align: center;
  margin-bottom: 20rpx;
}

.results-info {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.results-title {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--text-primary);
}

.results-count {
  font-size: 22rpx;
  color: var(--text-secondary);
}

// 课程卡片
.course-card {
  padding: 0;
  overflow: hidden;
  margin-bottom: 24rpx;
}

.course-header {
  background: linear-gradient(135deg, #7f4515, #8c5527);
  padding: 24rpx 30rpx;
}

.course-info {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.course-icon {
  width: 44rpx;
  height: 44rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.course-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #ffffff;
  flex: 1;
}

.course-content {
  padding: 20rpx 30rpx 30rpx;
}

// 教师区域
.teacher-section {
  margin-bottom: 24rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

.teacher-header {
  margin-bottom: 16rpx;
}

.teacher-info {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.teacher-avatar {
  width: 36rpx;
  height: 36rpx;
  background: rgba(127, 69, 21, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.teacher-name {
  font-size: 24rpx;
  font-weight: 500;
  color: var(--text-primary);
}

// 学期列表
.semester-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.semester-item {
  background: #f8f9fa;
  border-radius: var(--radius-small);
  padding: 16rpx 20rpx;
  border: 1rpx solid #e9ecef;
  transition: all 0.2s ease;

  &:hover {
    background: #ffffff;
    border-color: rgba(127, 69, 21, 0.2);
  }
}

.semester-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.semester-name {
  background: linear-gradient(135deg, #7f4515, #8c5527);
  color: #ffffff;
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
  font-size: 20rpx;
  font-weight: 500;
}

.update-time {
  font-size: 18rpx;
  color: var(--text-light);
}

// 分数信息
.score-info {
  display: flex;
  gap: 24rpx;
}

.score-item {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-label {
  font-size: 20rpx;
  color: var(--text-secondary);
  font-weight: 400;
}

.score-value {
  font-size: 22rpx;
  font-weight: 600;
  
  &.primary {
    color: #7f4515;
  }
  
  &.secondary {
    color: #6c757d;
  }
}

// 状态页面样式
.empty-state,
.initial-state,
.loading-state {
  padding: 80rpx 40rpx;
}

.empty-content,
.initial-content,
.loading-content {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30rpx;
}

.empty-icon,
.initial-icon,
.loading-spinner {
  opacity: 0.6;
}

.empty-title,
.initial-title,
.loading-text {
  font-size: 32rpx;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-subtitle,
.initial-subtitle {
  font-size: 24rpx;
  color: var(--text-secondary);
  text-align: center;
  line-height: 1.5;
}

.retry-btn {
  width: 200rpx;
  margin-top: 20rpx;
}

// 加载动画
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

// 响应式适配
@media (max-width: 600rpx) {
  .content-wrapper {
    padding: 0 15rpx 30rpx;
  }

  .search-card {
    padding: 25rpx;
  }

  .button-group {
    flex-direction: column;
  }

  .score-info {
    flex-direction: column;
    gap: 8rpx;
  }

  .page-title {
    font-size: 36rpx;
  }
  
  .course-card {
    margin-bottom: 20rpx;
  }
  
  .course-header {
    padding: 20rpx 24rpx;
  }
  
  .course-content {
    padding: 16rpx 24rpx 24rpx;
  }
}
</style>
