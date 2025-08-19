<template>
  <view class="empty-state">
    <view class="empty-content">
      <view class="empty-icon">
        <uni-icons :type="iconType" size="80" color="#bdc3c7"></uni-icons>
      </view>
      <text class="empty-title">{{ title }}</text>
      <text v-if="description" class="empty-description">{{
        description
      }}</text>
      <button v-if="showRetry" class="retry-btn" @click="$emit('retry')">
        重试
      </button>
    </view>
  </view>
</template>

<script setup>
defineProps({
  iconType: {
    type: String,
    default: "info-filled",
  },
  title: {
    type: String,
    default: "暂无数据",
  },
  description: {
    type: String,
    default: "",
  },
  showRetry: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["retry"]);
</script>

<style lang="scss" scoped>
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 40rpx;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 500rpx;
}

.empty-icon {
  margin-bottom: 30rpx;
  opacity: 0.6;
}

.empty-title {
  font-size: 32rpx;
  color: #7f8c8d;
  font-weight: 500;
  margin-bottom: 16rpx;
}

.empty-description {
  font-size: 26rpx;
  color: #95a5a6;
  line-height: 1.5;
  margin-bottom: 40rpx;
}

.retry-btn {
  padding: 20rpx 40rpx;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #9b0400 0%, #c41e3a 100%);
  color: #ffffff;
  font-size: 28rpx;
  border: none;

  &::after {
    border: none;
  }
}
</style>
