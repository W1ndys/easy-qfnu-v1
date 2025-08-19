<template>
  <view class="loading-screen">
    <view class="loading-content">
      <view class="loading-spinner">
        <view class="spinner-circle"></view>
      </view>
      <text class="loading-text">{{ text }}</text>
    </view>
  </view>
</template>

<script setup>
defineProps({
  text: {
    type: String,
    default: "加载中...",
  },
});
</script>

<style lang="scss" scoped>
.loading-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 40rpx;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.loading-spinner {
  margin-bottom: 40rpx;
}

.spinner-circle {
  width: 80rpx;
  height: 80rpx;
  border: 6rpx solid #f3f3f3;
  border-top: 6rpx solid #9b0400;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 28rpx;
  color: #7f8c8d;
  font-weight: 500;
}
</style>
