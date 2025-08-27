<template>
  <scroll-view class="container" scroll-y="true" @scrolltoupper="onPullRefresh">
    <!-- 顶部公告弹幕 -->
    <AnnouncementMarquee />

    <!-- 背景装饰 -->
    <BackgroundDecoration />

    <!-- 主内容区域 -->
    <view class="content-wrapper">
      <!-- 登录卡片 -->
      <LoginCard />
    </view>
  </scroll-view>
</template>

<script setup>
import { ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { isTokenValid } from "../../utils/jwt-decode.js";
import AnnouncementMarquee from "./AnnouncementMarquee.vue";
import BackgroundDecoration from "./BackgroundDecoration.vue";
import LoginCard from "./LoginCard.vue";

// 新增：下拉刷新处理
const onPullRefresh = () => {
  console.log("下拉刷新");
  // 这里可以添加刷新逻辑，比如重新检查登录状态
  checkLoginStatus();
  // 停止下拉刷新
  uni.stopPullDownRefresh();
};

// 页面加载时检查缓存的token
onLoad(() => {
  checkLoginStatus();
});

// 检查登录状态函数
const checkLoginStatus = () => {
  const token = uni.getStorageSync("token");

  if (token) {
    console.log("检测到缓存的token，开始验证有效性");

    try {
      if (isTokenValid(token)) {
        console.log("Token验证通过，准备跳转到dashboard");
        uni.reLaunch({
          url: "/pages/dashboard/dashboard",
        });
      } else {
        console.log("Token无效，清除并停留在登录页");
        uni.removeStorageSync("token");
        uni.showToast({
          title: "登录已过期，请重新登录",
          icon: "none",
        });
      }
    } catch (error) {
      console.error("Token验证过程中出错:", error);
      // 如果验证过程有问题，为安全起见清除token
      uni.removeStorageSync("token");
      uni.showToast({
        title: "登录状态异常，请重新登录",
        icon: "none",
      });
    }
  }
};
</script>

<style lang="scss" scoped>
.container {
  position: relative;
  width: 100%;
  height: 100vh;
  background: #f7f8fa;
  padding-top: 30rpx;
  /* 调整为新的弹幕高度 */
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-height: calc(100vh - 80rpx);
  /* 调整为新的弹幕高度 */
  padding: 60rpx 60rpx 40rpx;
  box-sizing: border-box;
  position: relative;
  z-index: 1;
}

// 响应式适配
@media (max-height: 600px) {
  .content-wrapper {
    padding: 30rpx 60rpx 30rpx;
    min-height: calc(100vh + 200rpx - 80rpx); // 使用新的弹幕高度
  }
}

// 新增：支持更大屏幕的适配
@media (min-width: 768px) {
  .content-wrapper {
    padding: 80rpx 120rpx 60rpx;
    max-width: 1200rpx;
    margin: 0 auto;
  }
}

@media (min-width: 1024px) {
  .content-wrapper {
    padding: 100rpx 200rpx 80rpx;
  }
}
</style>
