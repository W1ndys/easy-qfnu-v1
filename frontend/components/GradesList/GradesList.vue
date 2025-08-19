<template>
  <view class="grades-list">
    <ModernCard
      v-for="item in semesters"
      :key="item.semesterName"
      :title="item.semesterName">
      <template #headerExtra>
        <view class="semester-stats">
          <text class="stats-text">{{ item.grades.length }}门课程</text>
        </view>
      </template>

      <view class="grades-grid">
        <view
          v-for="grade in item.grades"
          :key="grade.courseCode"
          class="grade-item"
          :class="getGradeClass(grade.score)">
          <view class="grade-header">
            <text class="course-name">{{ grade.courseName }}</text>
            <view class="grade-score" :class="getScoreClass(grade.score)">
              {{ grade.score }}
            </view>
          </view>
          <view class="grade-details">
            <view class="detail-item">
              <uni-icons
                type="creditcard"
                size="14"
                color="#9b0400"></uni-icons>
              <text>{{ grade.credit }}学分</text>
            </view>
            <view class="detail-item">
              <uni-icons type="star" size="14" color="#9b0400"></uni-icons>
              <text>{{ grade.gpa }}绩点</text>
            </view>
            <view class="detail-item" v-if="grade.courseCode">
              <uni-icons type="list" size="14" color="#9b0400"></uni-icons>
              <text>{{ grade.courseCode }}</text>
            </view>
          </view>
        </view>
      </view>
    </ModernCard>
  </view>
</template>

<script setup>
import ModernCard from "../ModernCard/ModernCard.vue";

defineProps({
  semesters: {
    type: Array,
    required: true,
  },
});

// 根据成绩获取样式类
const getGradeClass = (score) => {
  const numScore = parseFloat(score);
  if (isNaN(numScore)) return "grade-other";
  if (numScore >= 90) return "grade-excellent";
  if (numScore >= 80) return "grade-good";
  if (numScore >= 70) return "grade-fair";
  if (numScore >= 60) return "grade-pass";
  return "grade-fail";
};

// 根据分数获取分数样式类
const getScoreClass = (score) => {
  const numScore = parseFloat(score);
  if (isNaN(numScore)) return "score-other";
  if (numScore >= 90) return "score-excellent";
  if (numScore >= 80) return "score-good";
  if (numScore >= 70) return "score-fair";
  if (numScore >= 60) return "score-pass";
  return "score-fail";
};
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

.semester-stats {
  display: flex;
  align-items: center;
}

.stats-text {
  font-size: 24rpx;
  color: var(--text-light);
  background: rgba(155, 4, 0, 0.1);
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
}

.grades-grid {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.grade-item {
  background: #f8fafc;
  border-radius: var(--radius-small);
  padding: 24rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s ease;

  &:hover {
    background: #ffffff;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
  }

  // 根据成绩等级设置边框颜色
  &.grade-excellent {
    border-color: rgba(82, 196, 26, 0.3);
    background: linear-gradient(135deg, #f6ffed 0%, #f0f9ff 100%);
  }

  &.grade-good {
    border-color: rgba(24, 144, 255, 0.3);
    background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  }

  &.grade-fair {
    border-color: rgba(250, 173, 20, 0.3);
    background: linear-gradient(135deg, #fffbe6 0%, #fff7e6 100%);
  }

  &.grade-pass {
    border-color: rgba(155, 4, 0, 0.2);
    background: linear-gradient(135deg, #fff2f0 0%, #fff1f0 100%);
  }

  &.grade-fail {
    border-color: rgba(255, 77, 79, 0.4);
    background: linear-gradient(135deg, #fff2f0 0%, #ffebee 100%);
  }
}

.grade-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.course-name {
  flex: 1;
  font-size: 28rpx;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
  margin-right: 20rpx;
}

.grade-score {
  font-size: 32rpx;
  font-weight: 700;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  min-width: 80rpx;
  text-align: center;

  &.score-excellent {
    background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
    color: #ffffff;
    box-shadow: 0 4rpx 12rpx rgba(82, 196, 26, 0.3);
  }

  &.score-good {
    background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
    color: #ffffff;
    box-shadow: 0 4rpx 12rpx rgba(24, 144, 255, 0.3);
  }

  &.score-fair {
    background: linear-gradient(135deg, #faad14 0%, #ffc53d 100%);
    color: #ffffff;
    box-shadow: 0 4rpx 12rpx rgba(250, 173, 20, 0.3);
  }

  &.score-pass {
    background: linear-gradient(135deg, #9b0400 0%, #c41e3a 100%);
    color: #ffffff;
    box-shadow: 0 4rpx 12rpx rgba(155, 4, 0, 0.3);
  }

  &.score-fail {
    background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
    color: #ffffff;
    box-shadow: 0 4rpx 12rpx rgba(255, 77, 79, 0.3);
  }

  &.score-other {
    background: #f0f0f0;
    color: var(--text-secondary);
  }
}

.grade-details {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  color: var(--text-secondary);
  background: rgba(155, 4, 0, 0.05);
  padding: 8rpx 12rpx;
  border-radius: 16rpx;

  text {
    font-weight: 500;
  }
}
</style>
