<template>
  <PageLayout>
    <LoadingScreen v-if="isLoading" text="正在从教务系统同步成绩..." />

    <view v-else class="page-container page-rounded-container">
      <view class="background-decoration">
        <view class="circle circle-1"></view>
        <view class="circle circle-2"></view>
        <view class="circle circle-3"></view>
      </view>

      <view class="content-wrapper">
        <EmptyState v-if="isEmpty" icon-type="info-filled" title="没有查询到任何成绩记录" description="请检查网络连接或稍后重试"
          :show-retry="true" @retry="fetchGrades" />

        <view v-else>
          <view v-if="gpaAnalysis" class="analysis-container">
            <view class="main-gpa-section">
              <view class="gpa-item">
                <text class="gpa-value">{{ gpaAnalysis?.weighted_gpa?.toFixed(2) || 'N/A' }}</text>
                <text class="gpa-label">总加权平均GPA</text>
              </view>
              <view class="gpa-item">
                <text class="gpa-value">{{ effectiveGpa?.weighted_gpa?.toFixed(2) || 'N/A' }}</text>
                <text class="gpa-label">有效GPA (去重修)</text>
              </view>
              <view class="gpa-item">
                <text class="gpa-value">{{ totalCourses || 0 }}</text>
                <text class="gpa-label">总课程数</text>
              </view>
            </view>

            <view class="detailed-gpa-section">
              <view class="section-header">
                <text class="section-title">详细GPA分布</text>
              </view>
              <view class="details-flex-container">
                <template v-if="yearlyGpa && Object.keys(yearlyGpa).length > 0">
                  <view v-for="(gpa, year) in yearlyGpa" :key="year" class="detail-item-flex">
                    <text class="detail-label">{{ year }}学年</text>
                    <text class="detail-sub-info">{{ gpa.course_count }}门 / {{ gpa.total_credit.toFixed(1) }}学分</text>
                    <text class="detail-value">{{ gpa.weighted_gpa.toFixed(2) }}</text>
                  </view>
                </template>
                <template v-if="semesterGpa && Object.keys(semesterGpa).length > 0">
                  <view v-for="(gpa, semester) in semesterGpa" :key="semester" class="detail-item-flex">
                    <text class="detail-label">{{ semester }}</text>
                    <text class="detail-sub-info">{{ gpa.course_count }}门 / {{ gpa.total_credit.toFixed(1) }}学分</text>
                    <text class="detail-value">{{ gpa.weighted_gpa.toFixed(2) }}</text>
                  </view>
                </template>
              </view>
            </view>
          </view>

          <view class="custom-gpa-toggle-section">
            <view class="toggle-left">
              <text class="toggle-title">自定义GPA计算</text>
              <text class="toggle-desc">勾选课程以计算特定GPA</text>
            </view>
            <switch :checked="isCustomMode" @change="toggleCustomMode" color="#7F4515" />
          </view>

          <view v-if="isCustomMode" class="custom-mode-tip">
            <view class="tip-icon">💡</view>
            <text class="tip-text">请勾选 **需要计入** GPA的课程</text>
          </view>

          <view class="grades-list-container">
            <view v-for="semester in semesters" :key="semester.semesterName" class="semester-block">
              <view class="semester-header">
                <text class="semester-name">{{ semester.semesterName }}</text>
              </view>
              <view class="courses-list">
                <view v-for="course in semester.grades" :key="course.index" class="course-card" :class="{
                  'is-custom-mode': isCustomMode,
                  'is-selected': isCourseSelected(course.index)
                }">
                  <view class="course-main" @click="handleCourseClick(course)">
                    <view v-if="isCustomMode" class="course-checkbox-wrapper">
                      <view class="checkbox-inner" :class="{ 'checked': isCourseSelected(course.index) }"></view>
                    </view>

                    <view class="course-core-info">
                      <text class="course-name">{{ course.courseName }}</text>
                      <view class="course-meta">
                        <view class="meta-tag credit">学分: {{ course.credit }}</view>
                        <view class="meta-tag gpa">绩点: {{ course.gpa }}</view>
                        <view v-if="course.courseAttribute" class="meta-tag attribute">{{ course.courseAttribute }}
                        </view>
                      </view>
                    </view>

                    <view class="course-side">
                      <view class="course-score">
                        <text class="score-text" :class="getScoreClass(course.score)">
                          {{ course.score }}
                        </text>
                        <text v-if="course.scoreTag" class="score-tag">{{ course.scoreTag }}</text>
                      </view>
                      <view class="expand-icon" :class="{ 'expanded': isCourseExpanded(course.index) }">
                        <uni-icons type="down" size="16" color="#868e96"></uni-icons>
                      </view>
                    </view>
                  </view>

                  <view v-show="isCourseExpanded(course.index)" class="course-details">
                    <view class="detail-grid">
                      <view class="detail-item">
                        <text class="detail-label">课程代码</text>
                        <text class="detail-value">{{ course.courseCode }}</text>
                      </view>
                      <view class="detail-item">
                        <text class="detail-label">总学时</text>
                        <text class="detail-value">{{ course.totalHours }}</text>
                      </view>
                      <view class="detail-item">
                        <text class="detail-label">课程性质</text>
                        <text class="detail-value">{{ course.courseNature }}</text>
                      </view>
                      <view class="detail-item">
                        <text class="detail-label">课程类别</text>
                        <text class="detail-value">{{ course.courseCategory }}</text>
                      </view>
                      <view class="detail-item">
                        <text class="detail-label">考核方式</text>
                        <text class="detail-value">{{ course.assessmentMethod }}</text>
                      </view>
                      <view class="detail-item">
                        <text class="detail-label">考试类型</text>
                        <text class="detail-value">{{ course.examType }}</text>
                      </view>
                      <view v-if="course.groupName" class="detail-item">
                        <text class="detail-label">课程分组</text>
                        <text class="detail-value">{{ course.groupName }}</text>
                      </view>
                      <view v-if="course.retakeSemester" class="detail-item">
                        <text class="detail-label">重修学期</text>
                        <text class="detail-value">{{ course.retakeSemester }}</text>
                      </view>
                    </view>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view v-if="isCustomMode" class="custom-gpa-footer">
      <view v-if="customGPAResult" class="result-display-card">
        <view class="result-header">
          <text class="result-title">自定义计算结果</text>
          <text class="close-result-btn" @click="clearCustomResult">关闭</text>
        </view>
        <view class="result-content">
          <view class="result-gpa">
            <text class="gpa-value">{{ customGPAResult.weighted_gpa?.toFixed(2) || '0.00' }}</text>
            <text class="gpa-label">加权平均GPA</text>
          </view>
          <view class="result-stats">
            <view class="stat-item">
              <text class="stat-value">{{ customGPAResult.total_credit || 0 }}</text>
              <text class="stat-label">总学分</text>
            </view>
            <view class="stat-item">
              <text class="stat-value">{{ customGPAResult.course_count || 0 }}</text>
              <text class="stat-label">课程数</text>
            </view>
          </view>
        </view>
      </view>

      <view class="footer-actions">
        <view class="selection-info">
          <text class="info-text">{{ selectionInfoText }}</text>
          <view class="actions">
            <text class="action-btn" @click="selectAllCourses">全选</text>
            <text class="action-btn" @click="clearSelection">清空</text>
          </view>
        </view>
        <button class="calculate-btn" @click="calculateCustomGPA" :disabled="isCalculateDisabled">
          {{ isCalculating ? '计算中...' : '计算自定义GPA' }}
        </button>
      </view>
    </view>

    <transition name="modal">
      <view v-if="showNoticeModal" class="modal-overlay" @click.self="closeNoticeModal">
        <view class="modal-container">
          <view class="modal-header">
            <text class="modal-title">成绩查询与GPA分析提示</text>
          </view>
          <view class="modal-content">
            <text>
              因不同专业或不同目标院校的要求不同，保研所需要的绩点要求不同，如有需求，请前往底部自定义GPA计算自行计算
            </text>
          </view>
          <view class="modal-footer">
            <button class="modal-btn" @click="closeNoticeModal">我已知晓</button>
          </view>
        </view>
      </view>
    </transition>
  </PageLayout>
</template>

<script setup>
import { ref, computed } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import LoadingScreen from "../../components/LoadingScreen/LoadingScreen.vue";
import EmptyState from "../../components/EmptyState/EmptyState.vue";

// --- API & 全局常量 ---
const API_BASE_URL = getApp().globalData.apiBaseURL;
const API_GRADES_URL = `${API_BASE_URL}/api/v1/grades`;
const API_GPA_CALCULATE_URL = `${API_BASE_URL}/api/v1/gpa/calculate`;

// --- 基础页面状态 ---
const isLoading = ref(true);
const semesters = ref([]);
const gpaAnalysis = ref(null);
const semesterGpa = ref(null);
const yearlyGpa = ref(null);
const effectiveGpa = ref(null);
const totalCourses = ref(0);
const allCourses = ref([]);

// --- 自定义GPA计算状态 ---
const isCustomMode = ref(false);
const selectedCourses = ref([]); // 存储选中的课程 `index`
const isCalculating = ref(false);
const customGPAResult = ref(null); // 用于存储计算结果

// --- UI交互状态 ---
const expandedCourses = ref(new Set()); // 存储展开的课程 `index`
const showNoticeModal = ref(false);

// --- 计算属性 ---
const isEmpty = computed(() => semesters.value.length === 0);
const selectionInfoText = computed(() => `已选 ${selectedCourses.value.length} / ${allCourses.value.length} 门`);
const isCalculateDisabled = computed(() => isCalculating.value || selectedCourses.value.length === 0);

// --- 生命周期钩子 ---
onLoad(() => {
  // 1. 检查登录并获取数据
  checkLoginAndFetch();
  // 2. 延迟500ms后弹出提示窗口
  setTimeout(() => {
    // 可选: 增加判断条件，例如仅在有成绩数据时显示
    if (semesters.value.length > 0 || !isLoading.value) {
      showNoticeModal.value = true;
    }
  }, 500);
});

onShow(() => {
  // 每次页面显示时检查 token，防止在其他页面退出登录后，返回此页面时状态不正确
  if (!uni.getStorageSync("token")) {
    uni.showToast({ title: "请先登录", icon: "none" });
    uni.reLaunch({ url: "/pages/index/index" });
  }
});

// --- 数据获取与处理 ---
const checkLoginAndFetch = () => {
  if (!uni.getStorageSync("token")) {
    uni.showToast({ title: "请先登录", icon: "none" });
    uni.reLaunch({ url: "/pages/index/index" });
    return;
  }
  fetchGrades();
};

const fetchGrades = async () => {
  isLoading.value = true;
  try {
    const { statusCode, data } = await uni.request({
      url: API_GRADES_URL,
      method: "GET",
      header: { Authorization: "Bearer " + uni.getStorageSync("token") },
    });

    if (statusCode === 200 && data.success) {
      allCourses.value = data.data || [];
      semesters.value = groupGradesBySemester(allCourses.value);

      gpaAnalysis.value = data.gpa_analysis?.basic_gpa;
      semesterGpa.value = data.semester_gpa;
      yearlyGpa.value = data.yearly_gpa;
      effectiveGpa.value = data.effective_gpa;
      totalCourses.value = data.total_courses;

    } else if (statusCode === 401) {
      uni.removeStorageSync("token");
      uni.showToast({ title: "登录已过期，请重新登录", icon: "none" });
      setTimeout(() => uni.reLaunch({ url: "/pages/index/index" }), 1500);
    } else {
      uni.showToast({ title: data.detail || "获取成绩失败", icon: "none" });
    }
  } catch (error) {
    console.error("请求失败", error);
    uni.showToast({ title: "服务器连接失败", icon: "none" });
  } finally {
    isLoading.value = false;
  }
};

const groupGradesBySemester = (grades) => {
  if (!grades || grades.length === 0) return [];
  const semesterMap = grades.reduce((acc, grade) => {
    (acc[grade.semester] = acc[grade.semester] || []).push(grade);
    return acc;
  }, {});
  return Object.keys(semesterMap)
    .map(name => ({ semesterName: name, grades: semesterMap[name] }))
    .sort((a, b) => b.semesterName.localeCompare(a.semesterName));
};

// --- UI交互与辅助函数 ---
const isCourseSelected = (courseIndex) => selectedCourses.value.includes(courseIndex);
const isCourseExpanded = (courseIndex) => expandedCourses.value.has(courseIndex);

const toggleExpand = (courseIndex) => {
  if (expandedCourses.value.has(courseIndex)) {
    expandedCourses.value.delete(courseIndex);
  } else {
    expandedCourses.value.add(courseIndex);
  }
};

const handleCourseClick = (course) => {
  if (isCustomMode.value) {
    toggleCourseSelection(course.index);
  } else {
    toggleExpand(course.index);
  }
};

const getScoreClass = (score) => {
  const numScore = parseFloat(score);
  if (isNaN(numScore)) return 'score-text-grade'; // 用于“优秀”、“良好”等文本成绩
  if (numScore >= 90) return 'score-high';
  if (numScore >= 75) return 'score-mid';
  if (numScore >= 60) return 'score-low';
  return 'score-fail';
};

const closeNoticeModal = () => {
  showNoticeModal.value = false;
};

// --- 自定义GPA计算逻辑 ---
const toggleCustomMode = (e) => {
  isCustomMode.value = e.detail.value;
  if (!isCustomMode.value) {
    clearSelection();
    clearCustomResult();
  }
};

const toggleCourseSelection = (courseIndex) => {
  const idx = selectedCourses.value.indexOf(courseIndex);
  if (idx > -1) {
    selectedCourses.value.splice(idx, 1);
  } else {
    selectedCourses.value.push(courseIndex);
  }
  clearCustomResult(); // 每次选择变化时，清除旧的计算结果
};

const selectAllCourses = () => {
  selectedCourses.value = allCourses.value.map(c => c.index);
  clearCustomResult();
};

const clearSelection = () => {
  selectedCourses.value = [];
  clearCustomResult();
};

const clearCustomResult = () => {
  customGPAResult.value = null;
};

const calculateCustomGPA = async () => {
  if (selectedCourses.value.length === 0) {
    uni.showToast({ title: "请至少选择一门课程", icon: "none" });
    return;
  }
  isCalculating.value = true;

  const payload = {
    include_indices: selectedCourses.value,
    remove_retakes: true
  };

  try {
    const { statusCode, data } = await uni.request({
      url: API_GPA_CALCULATE_URL,
      method: "POST",
      header: {
        Authorization: "Bearer " + uni.getStorageSync("token"),
        "Content-Type": "application/json"
      },
      data: payload
    });

    if (statusCode === 200 && data.success) {
      customGPAResult.value = data.data;
      uni.showToast({ title: "GPA计算完成", icon: "success" });
    } else {
      uni.showToast({ title: data.detail || "GPA计算失败", icon: "none" });
    }
  } catch (error) {
    console.error("GPA计算请求失败", error);
    uni.showToast({ title: "网络连接失败", icon: "none" });
  } finally {
    isCalculating.value = false;
  }
};
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

/* --- 主题变量 --- */
$primary-color: #7F4515;
$primary-color-light: #F5EFE6;

/* --- 颜色变量 --- */
$text-color-primary: #343a40;
$text-color-secondary: #495057;
$text-color-muted: #8c7d70;
$border-color: #f0e9e4;
$background-color: #f7f8fa;
$background-color-light: #fdfcfa;
$background-color-card: #ffffff;
$score-high: #28a745;
$score-mid: #17a2b8;
$score-low: #ffc107;
$score-fail: #dc3545;

/* --- 尺寸变量 --- */
$border-radius-lg: 40rpx;
$border-radius-base: 16rpx;
$border-radius-sm: 12rpx;
$border-radius-xs: 8rpx;

/* --- 字体变量 --- */
$font-size-xxl: 40rpx;
$font-size-xl: 36rpx;
$font-size-lg: 30rpx;
$font-size-base: 28rpx;
$font-size-sm: 24rpx;
$font-size-xs: 22rpx;
$font-size-xxs: 20rpx;

/* 页面基本布局 */
.page-container {
  min-height: 100vh;
  background: $background-color;
  position: relative;
  overflow: hidden;
}

.page-rounded-container {
  background: $background-color-card;
  border-radius: $border-radius-lg;
  padding: 20rpx 20rpx 30rpx;
  box-shadow: 0 20rpx 60rpx var(--shadow-light);
  border: 1rpx solid var(--border-light);
}

.content-wrapper {
  position: relative;
  z-index: 1;
}

/* 背景装饰 */
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

/* GPA分析模块 */
.analysis-container {
  background-color: $background-color-card;
  border-radius: $border-radius-base;
  padding: 20rpx;
  margin-bottom: 25rpx;
  border: 1rpx solid $border-color;
}

.main-gpa-section {
  display: flex;
  justify-content: space-around;
  text-align: center;
  padding-bottom: 20rpx;
  margin-bottom: 20rpx;
  border-bottom: 1rpx solid $border-color;

  .gpa-item {
    .gpa-value {
      display: block;
      font-size: $font-size-xxl;
      font-weight: bold;
      color: $primary-color;
      line-height: 1.2;
    }

    .gpa-label {
      display: block;
      font-size: $font-size-xs;
      color: $text-color-muted;
      margin-top: 4rpx;
    }
  }
}

.detailed-gpa-section {
  .section-header {
    margin-bottom: 10rpx;

    .section-title {
      font-size: 26rpx;
      font-weight: bold;
      color: $text-color-primary;
    }
  }
}

.details-flex-container {
  display: flex;
  flex-wrap: wrap;
  gap: 15rpx;

  .detail-item-flex {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: $background-color-light;
    padding: 10rpx 15rpx;
    border-radius: $border-radius-xs;
    flex-grow: 1;
    min-width: calc(50% - 15rpx);

    .detail-label {
      font-size: $font-size-sm;
      color: $text-color-secondary;
      white-space: nowrap;
    }

    .detail-sub-info {
      font-size: $font-size-xxs;
      color: #a09387;
      margin: 0 10rpx;
      white-space: nowrap;
    }

    .detail-value {
      font-size: 26rpx;
      font-weight: bold;
      color: $primary-color;
      flex-shrink: 0;
      margin-left: auto;
    }
  }
}

/* 自定义GPA切换 */
.custom-gpa-toggle-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: $background-color-card;
  padding: 20rpx;
  border-radius: $border-radius-base;
  margin: 25rpx 0;
  border: 1rpx solid $border-color;

  .toggle-left {
    .toggle-title {
      display: block;
      font-size: $font-size-lg;
      font-weight: bold;
      color: $text-color-primary;
      margin-bottom: 4rpx;
    }

    .toggle-desc {
      font-size: $font-size-sm;
      color: $text-color-muted;
    }
  }
}

/* 自定义模式提示 */
.custom-mode-tip {
  display: flex;
  align-items: center;
  padding: 16rpx;
  background: $primary-color-light;
  border-radius: $border-radius-sm;
  margin-bottom: 25rpx;
  border-left: 6rpx solid $primary-color;

  .tip-icon {
    font-size: 26rpx;
    margin-right: 12rpx;
  }

  .tip-text {
    color: $primary-color;
    font-size: $font-size-sm;
    line-height: 1.4;
  }
}

/* 成绩列表 */
.grades-list-container {
  padding-bottom: 250rpx; // 为悬浮操作栏留出空间
}

.semester-block {
  margin-bottom: 30rpx;
}

.semester-header {
  padding-left: 8rpx;
  margin-bottom: 15rpx;

  .semester-name {
    font-size: $font-size-lg;
    font-weight: bold;
    color: $text-color-secondary;
    border-left: 8rpx solid $primary-color;
    padding-left: 15rpx;
  }
}

.courses-list {
  display: flex;
  flex-direction: column;
  gap: 15rpx;
}

.course-card {
  background-color: $background-color-card;
  border-radius: $border-radius-base;
  border: 1rpx solid $border-color;
  box-shadow: 0 4rpx 12rpx rgba(127, 69, 21, 0.03);
  transition: all 0.2s ease-in-out;

  &.is-custom-mode.is-selected {
    border-color: $primary-color;
    box-shadow: 0 6rpx 18rpx rgba(127, 69, 21, 0.1);
  }
}

.course-main {
  display: flex;
  align-items: center;
  padding: 20rpx;
  cursor: pointer;
}

.course-checkbox-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38rpx;
  height: 38rpx;
  margin-right: 20rpx;
  flex-shrink: 0;

  .checkbox-inner {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 2rpx solid #c0b8b1;
    transition: all 0.2s ease;
    position: relative;

    &.checked {
      background-color: $primary-color;
      border-color: $primary-color;

      &::after {
        content: '';
        position: absolute;
        top: 7rpx;
        left: 13rpx;
        width: 8rpx;
        height: 16rpx;
        border: solid white;
        border-width: 0 4rpx 4rpx 0;
        transform: rotate(45deg);
      }
    }
  }
}

.course-core-info {
  flex-grow: 1;
  min-width: 0;

  .course-name {
    font-size: $font-size-base;
    font-weight: bold;
    color: $text-color-primary;
    margin-bottom: 10rpx;
  }

  .course-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 10rpx;

    .meta-tag {
      font-size: $font-size-xxs;
      padding: 2rpx 10rpx;
      border-radius: 6rpx;

      &.credit {
        background-color: #e3f2fd;
        color: #0d47a1;
      }

      &.gpa {
        background-color: #e8f5e9;
        color: #1b5e20;
      }

      &.attribute {
        background-color: #fff3e0;
        color: #e65100;
      }
    }
  }
}

.course-side {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  margin-left: 15rpx;
}

.course-score {
  text-align: right;
  margin-right: 10rpx;

  .score-text {
    font-size: $font-size-xl;
    font-weight: bold;

    &.score-high {
      color: $score-high;
    }

    &.score-mid {
      color: $score-mid;
    }

    &.score-low {
      color: $score-low;
    }

    &.score-fail {
      color: $score-fail;
    }

    &.score-text-grade {
      color: $primary-color;
    }
  }

  .score-tag {
    font-size: $font-size-xxs;
    color: #adb5bd;
  }
}

.expand-icon {
  transition: transform 0.3s ease;

  &.expanded {
    transform: rotate(180deg);
  }
}

.course-details {
  padding: 0 25rpx 25rpx 25rpx;
  background-color: #fffbf7;
  border-top: 1rpx solid $border-color;

  .detail-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15rpx 25rpx;

    .detail-item {
      .detail-label {
        display: block;
        font-size: $font-size-xs;
        color: $text-color-muted;
        margin-bottom: 2rpx;
      }

      .detail-value {
        display: block;
        font-size: $font-size-sm;
        color: $text-color-primary;
      }
    }
  }
}

/* 悬浮操作栏 */
.custom-gpa-footer {
  position: fixed;
  bottom: 0;
  left: 20rpx;
  right: 20rpx;
  background-color: $background-color-card;
  box-shadow: 0 -10rpx 40rpx rgba(0, 0, 0, 0.06);
  padding: 15rpx 25rpx;
  padding-bottom: calc(15rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(15rpx + env(safe-area-inset-bottom));
  border-top-left-radius: 20rpx;
  border-top-right-radius: 20rpx;
  z-index: 100;
}

.result-display-card {
  background: $background-color-card;
  border: 1rpx solid $border-color;
  border-radius: $border-radius-base;
  margin-bottom: 15rpx;
  box-shadow: 0 8rpx 25rpx rgba(127, 69, 21, 0.05);
  overflow: hidden;

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15rpx 20rpx;
    background-color: $background-color-light;

    .result-title {
      font-size: $font-size-base;
      font-weight: bold;
      color: $text-color-primary;
    }

    .close-result-btn {
      font-size: $font-size-sm;
      color: $text-color-muted;
      padding: 5rpx 15rpx;
      border-radius: 10rpx;

      &:active {
        background-color: $border-color;
      }
    }
  }

  .result-content {
    display: flex;
    align-items: center;
    padding: 25rpx 20rpx;
  }

  .result-gpa {
    flex-shrink: 0;
    text-align: center;
    padding-right: 30rpx;
    margin-right: 30rpx;
    border-right: 1rpx solid $border-color;

    .gpa-value {
      display: block;
      font-size: 60rpx;
      font-weight: bold;
      color: $primary-color;
      line-height: 1;
    }

    .gpa-label {
      display: block;
      font-size: $font-size-xs;
      color: $text-color-muted;
      margin-top: 8rpx;
    }
  }

  .result-stats {
    flex-grow: 1;
    display: flex;
    justify-content: space-around;

    .stat-item {
      text-align: center;

      .stat-value {
        display: block;
        font-size: 34rpx;
        font-weight: bold;
        color: $text-color-primary;
      }

      .stat-label {
        display: block;
        font-size: $font-size-xs;
        color: $text-color-muted;
        margin-top: 4rpx;
      }
    }
  }
}

.footer-actions {
  display: flex;
  flex-direction: column;
  gap: 15rpx;
}

.selection-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 10rpx;

  .info-text {
    font-size: 26rpx;
    color: $text-color-primary;
  }

  .actions {
    display: flex;
    gap: 20rpx;

    .action-btn {
      font-size: $font-size-sm;
      color: $primary-color;
      padding: 8rpx 16rpx;
      background: $primary-color-light;
      border-radius: $border-radius-sm;
    }
  }
}

.calculate-btn {
  width: 100%;
  background: $primary-color;
  color: #ffffff;
  border: none;
  border-radius: $border-radius-base;
  padding: 24rpx;
  font-size: $font-size-lg;
  font-weight: bold;

  &:disabled {
    background: #c0b8b1;
    opacity: 0.7;
  }
}

/* 通用弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-container {
  background: $background-color-card;
  border-radius: 20rpx;
  max-width: 600rpx;
  padding: 30rpx;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.25);
}

.modal-header,
.modal-title {
  font-size: $font-size-lg;
  font-weight: bold;
  color: $text-color-primary;
}

.modal-content {
  font-size: 26rpx;
  color: #555;
  margin: 20rpx 0;
  line-height: 1.6;
}

.modal-footer {
  text-align: right;
  margin-top: 10rpx;
}

.modal-btn {
  background: $primary-color;
  color: #fff;
  border-radius: $border-radius-sm;
  padding: 16rpx 40rpx;
  font-size: $font-size-base;
}

/* 进入/退出动画 */
.modal-enter-active {
  animation: fadeInUp 0.3s ease forwards;
}

.modal-leave-active {
  animation: fadeOutDown 0.25s ease forwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(40rpx);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeOutDown {
  from {
    opacity: 1;
    transform: translateY(0);
  }

  to {
    opacity: 0;
    transform: translateY(40rpx);
  }
}
</style>