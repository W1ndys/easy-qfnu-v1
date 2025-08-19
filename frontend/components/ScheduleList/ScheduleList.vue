<template>
  <view class="schedule-list">
    <ModernCard
      v-for="(day, idx) in schedule"
      :key="day.weekday"
      :title="day.weekday">
      <template #headerExtra>
        <view class="day-stats">
          <text class="stats-text">{{ day.courses.length }}节课</text>
        </view>
      </template>

      <view class="courses-grid">
        <view
          v-for="course in day.courses"
          :key="course.courseCode"
          class="course-item">
          <view class="course-header">
            <text class="course-name">{{ course.courseName }}</text>
            <view class="course-time">{{ course.time }}</view>
          </view>
          <view class="course-details">
            <view class="detail-row">
              <view class="detail-item">
                <uni-icons
                  type="location"
                  size="14"
                  color="#9b0400"></uni-icons>
                <text>{{ course.location || "待安排" }}</text>
              </view>
              <view class="detail-item teacher">
                <uni-icons type="contact" size="14" color="#9b0400"></uni-icons>
                <text>{{ course.teacher || "待安排" }}</text>
              </view>
            </view>
            <view class="detail-row" v-if="course.courseCode">
              <view class="detail-item code">
                <uni-icons type="list" size="14" color="#9b0400"></uni-icons>
                <text>{{ course.courseCode }}</text>
              </view>
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
  schedule: {
    type: Array,
    required: true,
  },
});
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

.day-stats {
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

.courses-grid {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.course-item {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: var(--radius-small);
  padding: 24rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;

  &::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 6rpx;
    height: 100%;
    background: linear-gradient(135deg, #9b0400 0%, #c41e3a 100%);
  }

  &:hover {
    background: #ffffff;
    box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
    transform: translateY(-2rpx);
    border-color: rgba(155, 4, 0, 0.2);
  }
}

.course-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16rpx;
  gap: 20rpx;
}

.course-name {
  flex: 1;
  font-size: 30rpx;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
}

.course-time {
  font-size: 24rpx;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #9b0400 0%, #c41e3a 100%);
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  white-space: nowrap;
  box-shadow: 0 4rpx 12rpx rgba(155, 4, 0, 0.3);
}

.course-details {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.detail-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  align-items: center;
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
  min-width: 0;
  flex: 1;

  text {
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  &.teacher {
    background: rgba(82, 196, 26, 0.1);
  }

  &.code {
    background: rgba(24, 144, 255, 0.1);
    flex: none;
    width: 100%;
  }
}

// 响应式优化
@media (max-width: 750rpx) {
  .course-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12rpx;
  }

  .course-time {
    align-self: flex-end;
  }

  .detail-row {
    flex-direction: column;
    gap: 8rpx;
  }

  .detail-item {
    flex: none;
    width: 100%;
  }
}
</style>
