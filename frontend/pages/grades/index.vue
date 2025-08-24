<template>
  <PageLayout>
    <!-- 加载状态 -->
    <LoadingScreen v-if="isLoading" text="正在从教务系统同步成绩..." />

    <!-- 内容区域 -->
    <view v-else class="page-container">
      <!-- 空状态 -->
      <EmptyState v-if="semesters.length === 0" icon-type="info-filled" title="没有查询到任何成绩记录" description="请检查网络连接或稍后重试"
        :show-retry="true" @retry="fetchGrades" />

      <!-- 有数据时显示 -->
      <view v-else>
        <!-- GPA分析模块 -->
        <GPAAnalysis v-if="gpaAnalysis" :gpa-analysis="gpaAnalysis" :effective-gpa="effectiveGpa"
          :yearly-gpa="yearlyGpa" :semester-gpa="semesterGpa" :total-courses="totalCourses" />

        <!-- 自定义GPA计算模式切换 -->
        <view class="custom-gpa-toggle-section">
          <view class="toggle-left">
            <text class="toggle-title">自定义GPA计算</text>
            <text class="toggle-desc">勾选课程以计算特定GPA</text>
          </view>
          <switch :checked="isCustomMode" @change="toggleCustomMode" color="#667eea" />
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
                      <view v-if="course.courseAttribute" class="meta-tag attribute">{{ course.courseAttribute }}</view>
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
  </PageLayout>
</template>

<script setup>
import { ref } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import LoadingScreen from "../../components/LoadingScreen/LoadingScreen.vue";
import EmptyState from "../../components/EmptyState/EmptyState.vue";
import GPAAnalysis from "../../components/GPAAnalysis/GPAAnalysis.vue";

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
      gpaAnalysis.value = data.gpa_analysis;
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
  // 只要选择变化，就清除旧结果
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

  // 说明：后端当前使用 exclude_indices 字段接收“选中的课程索引”，内部按 include 模式处理
  const payload = {
    exclude_indices: selectedCourses.value,
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
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

.page-container {
  padding: 30rpx;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.grades-list-container {
  padding-bottom: 250rpx; // 为底部悬浮栏留出足够空间
}

.custom-gpa-toggle-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #ffffff;
  padding: 25rpx;
  border-radius: 20rpx;
  margin: 30rpx 0;
  border: 1rpx solid #e9ecef;

  .toggle-left {
    .toggle-title {
      display: block;
      font-size: 32rpx;
      font-weight: bold;
      color: #333;
      margin-bottom: 5rpx;
    }

    .toggle-desc {
      font-size: 24rpx;
      color: #6c757d;
    }
  }
}

.custom-mode-tip {
  display: flex;
  align-items: center;
  padding: 20rpx;
  background: #e3f2fd;
  border-radius: 12rpx;
  margin-bottom: 30rpx;
  border-left: 6rpx solid #2196f3;

  .tip-icon {
    font-size: 28rpx;
    margin-right: 12rpx;
  }

  .tip-text {
    color: #0d47a1;
    font-size: 26rpx;
    line-height: 1.4;
  }
}

.semester-block {
  margin-bottom: 40rpx;
}

.semester-header {
  padding-left: 10rpx;
  margin-bottom: 20rpx;

  .semester-name {
    font-size: 32rpx;
    font-weight: bold;
    color: #495057;
    border-left: 8rpx solid #667eea;
    padding-left: 20rpx;
  }
}

.courses-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.course-card {
  background-color: #ffffff;
  border-radius: 24rpx;
  border: 2rpx solid #e9ecef;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.02);
  transition: all 0.2s ease-in-out;

  &.is-custom-mode.is-selected {
    border-color: #667eea;
    box-shadow: 0 8rpx 20rpx rgba(102, 126, 234, 0.15);
  }
}

.course-main {
  display: flex;
  align-items: center;
  padding: 25rpx;
  cursor: pointer;
}

.course-checkbox-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40rpx;
  height: 40rpx;
  margin-right: 25rpx;
  flex-shrink: 0;

  .checkbox-inner {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 2rpx solid #adb5bd;
    transition: all 0.2s ease;
    position: relative;

    &.checked {
      background-color: #667eea;
      border-color: #667eea;

      &::after {
        content: '';
        position: absolute;
        top: 8rpx;
        left: 14rpx;
        width: 10rpx;
        height: 20rpx;
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
    font-size: 30rpx;
    font-weight: bold;
    color: #343a40;
    margin-bottom: 12rpx;
  }

  .course-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 10rpx;

    .meta-tag {
      font-size: 22rpx;
      padding: 4rpx 12rpx;
      border-radius: 8rpx;

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
  margin-left: 20rpx;
}

.course-score {
  text-align: right;
  margin-right: 15rpx;

  .score-text {
    font-size: 38rpx;
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
      color: #667eea;
    }
  }

  .score-tag {
    font-size: 22rpx;
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
  padding: 0 30rpx 30rpx 30rpx;
  background-color: #fafbff;
  border-top: 1rpx solid #e9ecef;

  .detail-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20rpx 30rpx;

    .detail-item {
      .detail-label {
        display: block;
        font-size: 22rpx;
        color: #868e96;
        margin-bottom: 4rpx;
      }

      .detail-value {
        display: block;
        font-size: 26rpx;
        color: #343a40;
      }
    }
  }
}

.custom-gpa-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #ffffff;
  box-shadow: 0 -10rpx 40rpx rgba(0, 0, 0, 0.08);
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  border-top-left-radius: 40rpx;
  border-top-right-radius: 40rpx;
  z-index: 100;
}

.result-display-card {
  background: #ffffff;
  border: 1rpx solid #e9ecef;
  border-radius: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
  overflow: hidden;

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx 25rpx;
    background-color: #f8f9fa;

    .result-title {
      font-size: 30rpx;
      font-weight: bold;
      color: #333;
    }

    .close-result-btn {
      font-size: 26rpx;
      color: #6c757d;
      padding: 5rpx 15rpx;
      border-radius: 10rpx;

      &:active {
        background-color: #e9ecef;
      }
    }
  }

  .result-content {
    display: flex;
    align-items: center;
    padding: 30rpx 25rpx;
  }

  .result-gpa {
    flex-shrink: 0;
    text-align: center;
    padding-right: 40rpx;
    margin-right: 40rpx;
    border-right: 1rpx solid #dee2e6;

    .gpa-value {
      display: block;
      font-size: 64rpx;
      font-weight: bold;
      color: #667eea;
      line-height: 1;
    }

    .gpa-label {
      display: block;
      font-size: 24rpx;
      color: #6c757d;
      margin-top: 10rpx;
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
        font-size: 36rpx;
        font-weight: bold;
        color: #333;
      }

      .stat-label {
        display: block;
        font-size: 22rpx;
        color: #6c757d;
        margin-top: 5rpx;
      }
    }
  }
}

.footer-actions {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.selection-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 10rpx;

  .info-text {
    font-size: 28rpx;
    color: #333;
  }

  .actions {
    display: flex;
    gap: 20rpx;

    .action-btn {
      font-size: 26rpx;
      color: #667eea;
      padding: 8rpx 16rpx;
      background: #f0f2ff;
      border-radius: 15rpx;
    }
  }
}

.calculate-btn {
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border: none;
  border-radius: 20rpx;
  padding: 28rpx;
  font-size: 32rpx;
  font-weight: bold;

  &:disabled {
    background: #ced4da;
    opacity: 0.7;
  }
}
</style>