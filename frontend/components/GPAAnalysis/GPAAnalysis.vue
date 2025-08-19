<template>
  <view class="gpa-analysis">
    <!-- 主要GPA指标 -->
    <ModernCard title="GPA综合分析" highlight>
      <view class="main-gpa-container">
        <view class="main-gpa-item highlight">
          <view class="gpa-label">有效GPA</view>
          <view class="gpa-value primary" v-if="effectiveGpa">{{
            effectiveGpa.weighted_gpa
          }}</view>
          <view class="gpa-detail" v-if="effectiveGpa">
            学分: {{ effectiveGpa.total_credit }} | 课程:
            {{ effectiveGpa.course_count }}
          </view>
          <view class="gpa-note">去重修补考，取最高成绩</view>
        </view>
        <view class="gpa-divider"></view>
        <view class="main-gpa-item">
          <view class="gpa-label">基础GPA</view>
          <view class="gpa-value">{{
            gpaAnalysis.basic_gpa.weighted_gpa
          }}</view>
          <view class="gpa-detail">
            学分: {{ gpaAnalysis.basic_gpa.total_credit }} | 课程:
            {{ gpaAnalysis.basic_gpa.course_count }}
          </view>
          <view class="gpa-note">包含所有成绩</view>
        </view>
      </view>
      <view class="total-courses">总课程数: {{ totalCourses }}</view>
    </ModernCard>

    <!-- 按学年GPA分析 -->
    <ModernCard title="按学年GPA分析" v-if="yearlyGpa">
      <view class="yearly-gpa-container">
        <view v-for="(gpa, year) in yearlyGpa" :key="year" class="yearly-item">
          <view class="year-title">{{ year }}学年</view>
          <view class="year-gpa">{{ gpa.weighted_gpa }}</view>
          <view class="year-detail">
            学分: {{ gpa.total_credit }} | 课程: {{ gpa.course_count }}
          </view>
        </view>
      </view>
    </ModernCard>

    <!-- 按学期GPA分析 -->
    <ModernCard title="按学期GPA分析" v-if="semesterGpa">
      <view class="semester-gpa-container">
        <view
          v-for="(gpa, semester) in semesterGpa"
          :key="semester"
          class="semester-item">
          <view class="semester-title">{{ semester }}</view>
          <view class="semester-gpa">{{ gpa.weighted_gpa }}</view>
          <view class="semester-detail">
            学分: {{ gpa.total_credit }} | 课程: {{ gpa.course_count }}
          </view>
        </view>
      </view>
    </ModernCard>
  </view>
</template>

<script setup>
import ModernCard from "../ModernCard/ModernCard.vue";

defineProps({
  gpaAnalysis: {
    type: Object,
    required: true,
  },
  effectiveGpa: {
    type: Object,
    default: null,
  },
  yearlyGpa: {
    type: Object,
    default: null,
  },
  semesterGpa: {
    type: Object,
    default: null,
  },
  totalCourses: {
    type: Number,
    default: 0,
  },
});
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

.gpa-analysis {
  margin-bottom: 30rpx;
}

// 主要GPA指标样式
.main-gpa-container {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
}

.main-gpa-item {
  flex: 1;
  text-align: center;

  &.highlight {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border-radius: var(--radius-small);
    padding: 30rpx 20rpx;
    margin: 0 10rpx;
    border: 2rpx solid rgba(155, 4, 0, 0.1);
  }
}

.gpa-label {
  font-size: 26rpx;
  color: var(--text-secondary);
  margin-bottom: 12rpx;
  font-weight: 500;
}

.gpa-value {
  font-size: 48rpx;
  font-weight: 700;
  color: #52c41a;
  margin-bottom: 8rpx;

  &.primary {
    color: #9b0400;
    font-size: 56rpx;
    text-shadow: 0 2rpx 8rpx rgba(155, 4, 0, 0.2);
  }
}

.gpa-detail {
  font-size: 22rpx;
  color: var(--text-light);
  margin-bottom: 8rpx;
}

.gpa-note {
  font-size: 20rpx;
  color: var(--text-light);
  background: rgba(155, 4, 0, 0.05);
  padding: 8rpx 12rpx;
  border-radius: 20rpx;
  display: inline-block;
}

.gpa-divider {
  width: 2rpx;
  height: 120rpx;
  background: linear-gradient(
    to bottom,
    transparent,
    var(--border-light),
    transparent
  );
  margin: 0 20rpx;
}

.total-courses {
  text-align: center;
  font-size: 24rpx;
  color: var(--text-secondary);
  padding-top: 20rpx;
  margin-top: 20rpx;
  border-top: 1rpx solid var(--border-light);
  font-weight: 500;
}

// 按学年GPA样式
.yearly-gpa-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300rpx, 1fr));
  gap: 20rpx;
  padding: 10rpx 0;
}

.yearly-item {
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  border-radius: var(--radius-small);
  padding: 30rpx 25rpx;
  text-align: center;
  border: 1rpx solid var(--border-light);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2rpx);
    box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.08);
  }
}

.year-title {
  font-size: 26rpx;
  color: var(--text-secondary);
  margin-bottom: 12rpx;
  font-weight: 500;
}

.year-gpa {
  font-size: 42rpx;
  font-weight: 700;
  color: #9b0400;
  margin-bottom: 8rpx;
}

.year-detail {
  font-size: 22rpx;
  color: var(--text-light);
}

// 按学期GPA样式
.semester-gpa-container {
  display: flex;
  flex-direction: column;
  gap: 15rpx;
  padding: 10rpx 0;
}

.semester-item {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  border-radius: var(--radius-small);
  padding: 25rpx;
  border: 1rpx solid var(--border-light);
  transition: all 0.3s ease;

  &:hover {
    background: #ffffff;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
  }
}

.semester-title {
  flex: 1;
  font-size: 28rpx;
  font-weight: 600;
  color: var(--text-primary);
}

.semester-gpa {
  font-size: 36rpx;
  font-weight: 700;
  color: #52c41a;
  margin-right: 20rpx;
}

.semester-detail {
  font-size: 22rpx;
  color: var(--text-secondary);
  text-align: right;
  min-width: 150rpx;
}
</style>
