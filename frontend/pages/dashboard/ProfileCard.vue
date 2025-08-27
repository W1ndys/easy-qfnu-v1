<template>
  <ModernCard class="profile-card" highlight>
    <view class="profile-content">
      <view class="identity-section">
        <view class="avatar-wrapper">
          <image class="avatar" src="https://pic1.zhimg.com/80/v2-82c1c70c69720aadac79594ea50ed4a7.png"
            mode="aspectFit"></image>
          <view class="status-indicator"></view>
        </view>
        <view class="identity-info">
          <text class="welcome-text">欢迎回来~</text>
          <text class="user-name">{{ profile.student_name }}</text>
          <text class="user-id">{{ profile.student_id }}</text>
        </view>
      </view>
      <view class="details-section">
        <view class="detail-item">
          <text class="detail-label">学院</text>
          <text class="detail-value">{{ profile.college }}</text>
        </view>
        <view class="detail-item">
          <text class="detail-label">专业</text>
          <text class="detail-value">{{ profile.major }}</text>
        </view>
        <view class="detail-item">
          <text class="detail-label">班级</text>
          <text class="detail-value">{{ profile.class_name }}</text>
        </view>
      </view>
    </view>
  </ModernCard>
</template>

<script setup>
import ModernCard from "../../components/ModernCard/ModernCard.vue";

defineProps({
  profile: {
    type: Object,
    required: true,
    default: () => ({
      student_name: "W1ndys",
      student_id: "加载中...",
      college: "曲奇学院",
      major: "曲奇专业",
      class_name: "22曲奇班",
    })
  }
});
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

.profile-card {
  margin-bottom: 10rpx;

  :deep(.card-content) {
    padding: 12rpx 8rpx !important;
  }
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.identity-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24rpx;
  padding: 4rpx 0;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
}

.avatar {
  width: 110rpx;
  height: 110rpx;
  border-radius: 50%;
  border: 3rpx solid rgba(155, 4, 0, 0.1);
  box-shadow: 0 8rpx 20rpx rgba(155, 4, 0, 0.15);
}

.status-indicator {
  position: absolute;
  bottom: 8rpx;
  right: 8rpx;
  width: 22rpx;
  height: 22rpx;
  background: #52c41a;
  border-radius: 50%;
  border: 2rpx solid #ffffff;
}

.identity-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4rpx;
}

.welcome-text {
  font-size: 22rpx;
  color: var(--text-light);
  font-weight: 400;
  margin-bottom: 2rpx;
}

.user-name {
  font-size: 38rpx;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.user-id {
  font-size: 28rpx;
  font-weight: 500;
  color: var(--text-secondary);
  letter-spacing: 1rpx;
}

.details-section {
  border-top: 1rpx solid var(--border-light);
  padding-top: 12rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.detail-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6rpx 8rpx;
  background: rgba(127, 69, 21, 0.03);
  border: 1rpx solid rgba(127, 69, 21, 0.08);
  border-radius: 8rpx;
}

.detail-label {
  font-size: 24rpx;
  color: var(--text-light);
  font-weight: 500;
  min-width: 60rpx;
}

.detail-value {
  font-size: 26rpx;
  color: var(--text-primary);
  font-weight: 600;
  text-align: right;
  flex: 1;
}
</style>
