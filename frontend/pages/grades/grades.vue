<template>
  <PageLayout>
    <!-- 加载状态 -->
    <LoadingScreen v-if="isLoading" text="正在从教务系统同步成绩..." />

    <!-- 内容区域 -->
    <view v-else class="page-container page-rounded-container">
      <!-- 背景装饰（与其它页面一致） -->
      <view class="background-decoration">
        <view class="circle circle-1"></view>
        <view class="circle circle-2"></view>
        <view class="circle circle-3"></view>
      </view>

      <!-- 次外层内容容器，避免装饰遮挡 -->
      <view class="content-wrapper">
        <!-- 空状态 -->
        <EmptyState v-if="semesters.length === 0" icon-type="info-filled" title="没有查询到任何成绩记录" description="请检查网络连接或稍后重试"
          :show-retry="true" @retry="fetchGrades" />

        <!-- 有数据时显示 -->
        <view v-else>
          <!-- GPA分析模块 (已内联) -->
          <view v-if="gpaAnalysis" class="analysis-container">
            <!-- 主GPA显示区域 -->
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

            <!-- 学年与学期GPA流式布局 -->
            <view class="detailed-gpa-section">
              <view class="section-header">
                <text class="section-title">详细GPA分布</text>
              </view>
              <view class="details-flex-container">
                <!-- 学年GPA -->
                <template v-if="yearlyGpa && Object.keys(yearlyGpa).length > 0">
                  <view v-for="(gpa, year) in yearlyGpa" :key="year" class="detail-item-flex">
                    <text class="detail-label">{{ year }}学年</text>
                    <text class="detail-sub-info">{{ gpa.course_count }}门 / {{ gpa.total_credit.toFixed(1) }}学分</text>
                    <text class="detail-value">{{ gpa.weighted_gpa.toFixed(2) }}</text>
                  </view>
                </template>
                <!-- 学期GPA -->
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

          <!-- 自定义GPA计算模式切换 -->
          <view class="custom-gpa-toggle-section">
            <view class="toggle-left">
              <text class="toggle-title">自定义GPA计算</text>
              <text class="toggle-desc">勾选课程以计算特定GPA</text>
            </view>
            <switch :checked="isCustomMode" @change="toggleCustomMode" color="#7F4515" />
          </view>

          <!-- 提示信息 -->
          <view v-if="isCustomMode" class="custom-mode-tip">
            <view class="tip-icon">💡</view>
            <text class="tip-text">请勾选 **需要计入** GPA的课程</text>
          </view>

          <!-- 成绩列表 -->
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
                  <!-- 卡片主区域 (用于点击) -->
                  <view class="course-main" @click="handleCourseClick(course)">
                    <!-- 复选框 -->
                    <view v-if="isCustomMode" class="course-checkbox-wrapper">
                      <view class="checkbox-inner" :class="{ 'checked': isCourseSelected(course.index) }"></view>
                    </view>

                    <!-- 核心信息 -->
                    <view class="course-core-info">
                      <text class="course-name">{{ course.courseName }}</text>
                      <view class="course-meta">
                        <view class="meta-tag credit">学分: {{ course.credit }}</view>
                        <view class="meta-tag gpa">绩点: {{ course.gpa }}</view>
                        <view v-if="course.courseAttribute" class="meta-tag attribute">{{ course.courseAttribute }}
                        </view>
                      </view>
                    </view>

                    <!-- 成绩与展开按钮 -->
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

                  <!-- 可展开的详细信息 -->
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

    <!-- 自定义计算悬浮操作栏 -->
    <view v-if="isCustomMode" class="custom-gpa-footer">
      <!-- 计算结果展示 -->
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

      <!-- 操作按钮区域 -->
      <view class="footer-actions">
        <view class="selection-info">
          <text class="info-text">已选 {{ selectedCourses.length }} / {{ allCourses.length }} 门</text>
          <view class="actions">
            <text class="action-btn" @click="selectAllCourses">全选</text>
            <text class="action-btn" @click="clearSelection">清空</text>
          </view>
        </view>
        <button class="calculate-btn" @click="calculateCustomGPA"
          :disabled="isCalculating || selectedCourses.length === 0">
          {{ isCalculating ? '计算中...' : '计算自定义GPA' }}
        </button>
      </view>
    </view>
    <!-- 成绩页面信息提醒弹窗 -->
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
import { ref } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import LoadingScreen from "../../components/LoadingScreen/LoadingScreen.vue";
import EmptyState from "../../components/EmptyState/EmptyState.vue";

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

onLoad(() => checkLoginAndFetch());
onShow(() => {
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
      url: `${getApp().globalData.apiBaseURL}/api/v1/grades`,
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
  if (isNaN(numScore)) return 'score-text-grade';
  if (numScore >= 90) return 'score-high';
  if (numScore >= 75) return 'score-mid';
  if (numScore >= 60) return 'score-low';
  return 'score-fail';
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
  clearCustomResult();
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
      url: `${getApp().globalData.apiBaseURL}/api/v1/gpa/calculate`,
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

// --- 弹窗提醒状态 ---

const showNoticeModal = ref(false);

onLoad(() => {
  checkLoginAndFetch();
  setTimeout(() => { showNoticeModal.value = true }, 500);
});

const closeNoticeModal = () => {
  showNoticeModal.value = false;
};


</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

// 定义主色调
$primary-color: #7F4515;
$primary-color-light: #F5EFE6;

/* 最外层背景（与其它页面统一） */
.page-container {
  min-height: 100vh;
  background: #f7f8fa;
  position: relative;
  overflow: hidden;
}

/* 次外层圆角容器（与其它页面统一） */
.page-rounded-container {
  background: #ffffff;
  border-radius: 40rpx;
  padding: 20rpx 20rpx 30rpx;
  box-shadow: 0 20rpx 60rpx var(--shadow-light);
  border: 1rpx solid var(--border-light);
}

/* 内容主体容器，避免装饰覆盖 */
.content-wrapper {
  position: relative;
  z-index: 1;
  padding: 0; // 保持原有子模块的内边距与间距
}

/* 背景装饰（与其它页面统一） */
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

/* 下方为原有样式，去除 page-container 上的宽度/居中/圆角，保持模块间距 */
.analysis-container {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 20rpx;
  margin-bottom: 25rpx;
  border: 1rpx solid #f0e9e4;
}

.main-gpa-section {
  display: flex;
  justify-content: space-around;
  text-align: center;
  padding-bottom: 20rpx;
  margin-bottom: 20rpx;
  border-bottom: 1rpx solid #f0e9e4;

  .gpa-item {
    .gpa-value {
      display: block;
      font-size: 40rpx;
      font-weight: bold;
      color: $primary-color;
      line-height: 1.2;
    }

    .gpa-label {
      display: block;
      font-size: 22rpx;
      color: #8c7d70;
      margin-top: 4rpx;
    }
  }
}

// 流式布局
.detailed-gpa-section {
  .section-header {
    margin-bottom: 10rpx;

    .section-title {
      font-size: 26rpx;
      font-weight: bold;
      color: #333;
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
    background-color: #fdfcfa;
    padding: 10rpx 15rpx;
    border-radius: 8rpx;
    flex-grow: 1; // 允许项目拉伸填充
    min-width: calc(50% - 15rpx); // 最小宽度，保证一行最多两个

    .detail-label {
      font-size: 24rpx;
      color: #5c524a;
      white-space: nowrap;
    }

    .detail-sub-info {
      font-size: 20rpx;
      color: #a09387;
      margin: 0 10rpx;
      white-space: nowrap;
    }

    .detail-value {
      font-size: 26rpx;
      font-weight: bold;
      color: $primary-color;
      flex-shrink: 0;
      margin-left: auto; // 将GPA值推到最右侧
    }
  }
}


.grades-list-container {
  padding-bottom: 250rpx;
}

.custom-gpa-toggle-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #ffffff;
  padding: 20rpx;
  border-radius: 16rpx;
  margin: 25rpx 0;
  border: 1rpx solid #f0e9e4;

  .toggle-left {
    .toggle-title {
      display: block;
      font-size: 30rpx;
      font-weight: bold;
      color: #333;
      margin-bottom: 4rpx;
    }

    .toggle-desc {
      font-size: 24rpx;
      color: #8c7d70;
    }
  }
}

.custom-mode-tip {
  display: flex;
  align-items: center;
  padding: 16rpx;
  background: $primary-color-light;
  border-radius: 12rpx;
  margin-bottom: 25rpx;
  border-left: 6rpx solid $primary-color;

  .tip-icon {
    font-size: 26rpx;
    margin-right: 12rpx;
  }

  .tip-text {
    color: $primary-color;
    font-size: 24rpx;
    line-height: 1.4;
  }
}

.semester-block {
  margin-bottom: 30rpx;
}

.semester-header {
  padding-left: 8rpx;
  margin-bottom: 15rpx;

  .semester-name {
    font-size: 30rpx;
    font-weight: bold;
    color: #495057;
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
  background-color: #ffffff;
  border-radius: 16rpx;
  border: 1rpx solid #f0e9e4;
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
    font-size: 28rpx;
    font-weight: bold;
    color: #343a40;
    margin-bottom: 10rpx;
  }

  .course-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 10rpx;

    .meta-tag {
      font-size: 20rpx;
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
    font-size: 36rpx;
    font-weight: bold;

    &.score-high {
      color: #28a745;
    }

    &.score-mid {
      color: #17a2b8;
    }

    &.score-low {
      color: #ffc107;
    }

    &.score-fail {
      color: #dc3545;
    }

    &.score-text-grade {
      color: $primary-color;
    }
  }

  .score-tag {
    font-size: 20rpx;
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
  border-top: 1rpx solid #f0e9e4;

  .detail-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15rpx 25rpx;

    .detail-item {
      .detail-label {
        display: block;
        font-size: 22rpx;
        color: #8c7d70;
        margin-bottom: 2rpx;
      }

      .detail-value {
        display: block;
        font-size: 24rpx;
        color: #343a40;
      }
    }
  }
}

/* 悬浮操作栏与容器左右边距对齐 */
.custom-gpa-footer {
  position: fixed;
  bottom: 0;
  left: 20rpx;
  right: 20rpx;
  background-color: #ffffff;
  box-shadow: 0 -10rpx 40rpx rgba(0, 0, 0, 0.06);
  padding: 15rpx 25rpx;
  padding-bottom: calc(15rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(15rpx + env(safe-area-inset-bottom));
  border-top-left-radius: 20rpx;
  border-top-right-radius: 20rpx;
  z-index: 100;
  // 删除此前的水平居中 transform/固定宽度，改为与页面内边距对齐
  // width/transform/left:50% 均不再需要
}

.result-display-card {
  background: #ffffff;
  border: 1rpx solid #f0e9e4;
  border-radius: 16rpx;
  margin-bottom: 15rpx;
  box-shadow: 0 8rpx 25rpx rgba(127, 69, 21, 0.05);
  overflow: hidden;

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15rpx 20rpx;
    background-color: #fdfcfa;

    .result-title {
      font-size: 28rpx;
      font-weight: bold;
      color: #333;
    }

    .close-result-btn {
      font-size: 24rpx;
      color: #8c7d70;
      padding: 5rpx 15rpx;
      border-radius: 10rpx;

      &:active {
        background-color: #f0e9e4;
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
    border-right: 1rpx solid #f0e9e4;

    .gpa-value {
      display: block;
      font-size: 60rpx;
      font-weight: bold;
      color: $primary-color;
      line-height: 1;
    }

    .gpa-label {
      display: block;
      font-size: 22rpx;
      color: #8c7d70;
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
        color: #333;
      }

      .stat-label {
        display: block;
        font-size: 22rpx;
        color: #8c7d70;
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
    color: #333;
  }

  .actions {
    display: flex;
    gap: 20rpx;

    .action-btn {
      font-size: 24rpx;
      color: $primary-color;
      padding: 8rpx 16rpx;
      background: $primary-color-light;
      border-radius: 12rpx;
    }
  }
}

.calculate-btn {
  width: 100%;
  background: $primary-color;
  color: #ffffff;
  border: none;
  border-radius: 16rpx;
  padding: 24rpx;
  font-size: 30rpx;
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
  background: #fff;
  border-radius: 20rpx;
  max-width: 600rpx;
  width: 80%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.modal-header {
  padding: 24rpx;
  border-bottom: 1rpx solid #f0e9e4;

  .modal-title {
    font-size: 32rpx;
    font-weight: bold;
    color: #333;
  }
}

.modal-content {
  padding: 30rpx;
  font-size: 26rpx;
  color: #555;
  line-height: 1.6;
  flex: 1;
}

.modal-footer {
  padding: 20rpx;
  border-top: 1rpx solid #f0e9e4;
  display: flex;
  justify-content: flex-end;

  .confirm-btn {
    background: $primary-color;
    color: #fff;
    border-radius: 12rpx;
    padding: 14rpx 30rpx;
    font-size: 28rpx;
  }
}

/* 弹窗动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: translateY(40rpx);
}

/* 样式追加到 <style scoped> */
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
  background: #fff;
  border-radius: 20rpx;
  max-width: 600rpx;
  padding: 30rpx;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.25);
  animation: fadeInUp 0.3s ease;
}

.modal-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.modal-content {
  font-size: 26rpx;
  color: #555;
  margin: 20rpx 0;
  line-height: 1.6;
}

.modal-footer {
  text-align: right;
}

.modal-btn {
  background: $primary-color;
  color: #fff;
  border-radius: 12rpx;
  padding: 16rpx 40rpx;
  font-size: 28rpx;
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
