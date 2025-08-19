<template>
  <view class="page-container">
    <!-- 背景装饰 -->
    <view class="background-decoration">
      <view class="circle circle-1"></view>
      <view class="circle circle-2"></view>
      <view class="circle circle-3"></view>
    </view>

    <!-- 页面内容 -->
    <view class="content-wrapper">
      <slot></slot>
    </view>
  </view>
</template>

<script setup>
// 页面布局组件，提供统一的背景和布局
</script>

<style lang="scss" scoped>
.page-container {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  overflow: hidden;
}

// 背景装饰圆圈
.background-decoration {
  position: absolute;
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
  background: rgba(155, 4, 0, 0.08);

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

.content-wrapper {
  position: relative;
  z-index: 1;
  padding: 40rpx;
  min-height: 100vh;
  box-sizing: border-box;
}
</style>
