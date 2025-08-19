<template>
  <view class="modern-card" :class="{ highlight: highlight }">
    <view v-if="title" class="card-header">
      <text class="card-title">{{ title }}</text>
      <view v-if="$slots.headerExtra" class="header-extra">
        <slot name="headerExtra"></slot>
      </view>
    </view>
    <view class="card-content">
      <slot></slot>
    </view>
  </view>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: "",
  },
  highlight: {
    type: Boolean,
    default: false,
  },
});
</script>

<style lang="scss" scoped>
.modern-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24rpx;
  padding: 40rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(20rpx);
  border: 1rpx solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;

  &.highlight {
    border: 2rpx solid rgba(155, 4, 0, 0.2);
    box-shadow: 0 16rpx 48rpx rgba(155, 4, 0, 0.15);
  }

  &:hover {
    transform: translateY(-4rpx);
    box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.12);
  }
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30rpx;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.card-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #2c3e50;
}

.header-extra {
  display: flex;
  align-items: center;
}

.card-content {
  color: #34495e;
}
</style>
