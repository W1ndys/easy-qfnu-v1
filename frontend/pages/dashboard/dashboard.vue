<template>
  <view class="container">
    <view class="profile-header">
      <image class="avatar" src="/static/images/avatar.png"></image>
      <view class="user-info">
        <text class="welcome-text">欢迎你</text>
        <text class="user-id">{{ studentId }}</text>
      </view>
    </view>

    <view class="grid-title">核心功能</view>
    <uni-grid
      :column="2"
      :show-border="false"
      :square="false"
      @change="handleNavigate">
      <uni-grid-item
        v-for="(item, index) in features"
        :key="index"
        :index="index">
        <view class="grid-item-box">
          <image class="grid-icon" :src="item.icon"></image>
          <text class="grid-text">{{ item.text }}</text>
        </view>
      </uni-grid-item>
    </uni-grid>

    <button class="logout-btn" @click="handleLogout">退出登录</button>
  </view>
</template>

<script setup>
import { ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
// 确保你的 jwt-decode.js 文件放在了项目的 utils 目录中
import { decode } from "../../utils/jwt-decode.js";

// --- 页面数据 ---
// ref() 创建的是响应式变量，当 .value 改变时，<template>会自动更新
const studentId = ref("加载中...");

// 定义功能列表，数据驱动UI
const features = ref([
  {
    text: "成绩查询 & GPA",
    icon: "/static/images/grades-icon.png",
    url: "/pages/grades/grades",
  },
  {
    text: "课表查询",
    icon: "/static/images/schedule-icon.png",
    url: "/pages/schedule/schedule",
  },
  { text: "课程评价", icon: "/static/images/review-icon.png", url: "" },
  { text: "更多功能", icon: "/static/images/more-icon.png", url: "" }, // 预留给未来功能
]);

// --- 页面生命周期函数 ---
// onLoad 会在页面首次加载时执行一次
onLoad(() => {
  // 检查登录状态
  const token = uni.getStorageSync("token");

  if (!token) {
    // 如果没有Token，直接踢回登录页
    uni.showToast({ title: "请先登录", icon: "none" });
    uni.reLaunch({ url: "/pages/index/index" }); // 登录页是 index
  } else {
    try {
      // 解析Token获取学号
      const payload = decode(token);
      // 更新 studentId 的值
      studentId.value = payload.sub;
    } catch (error) {
      console.error("Token解析失败", error);
      uni.showToast({ title: "凭证无效,请重新登录", icon: "none" });
      uni.reLaunch({ url: "/pages/index/index" });
    }
  }
});

// --- 事件处理函数 ---
// 处理宫格点击事件
const handleNavigate = (e) => {
  // ⬇️⬇️⬇️ 在这里加上第一句日志 ⬇️⬇️⬇️
  console.log("handleNavigate 函数被触发了！收到的事件对象是:", e);

  const index = e.detail.index;
  const targetPage = features.value[index];

  if (targetPage.url) {
    uni.navigateTo({ url: targetPage.url });
  } else {
    uni.showToast({ title: "功能正在开发中...", icon: "none" });
  }
};

// 处理退出登录点击事件
const handleLogout = () => {
  uni.showModal({
    title: "提示",
    content: "确定要退出登录吗？",
    success: (res) => {
      if (res.confirm) {
        uni.removeStorageSync("token");
        uni.reLaunch({ url: "/pages/index/index" });
      }
    },
  });
};
</script>

<style lang="scss" scoped>
.container {
  padding: 40rpx;
}

.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 60rpx;
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  margin-right: 30rpx;
  border: 4rpx solid #eee;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.welcome-text {
  font-size: 32rpx;
  color: #666;
}

.user-id {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
}

.grid-title {
  font-size: 34rpx;
  font-weight: bold;
  margin-bottom: 30rpx;
  padding-left: 10rpx;
}

// Grid样式
.grid-item-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 220rpx;
  width: 100%;
  background-color: #f7f8fa;
  border-radius: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);

  // 通过 uni-grid-item 的属性来判断是否未开放
  .uni-grid-item[data-url=""] & {
    opacity: 0.5;
  }
}

.grid-icon {
  width: 80rpx;
  height: 80rpx;
  margin-bottom: 20rpx;
}

.grid-text {
  font-size: 28rpx;
  color: #333;
}

.logout-btn {
  margin-top: 80rpx;
  background-color: #f5f5f5;
  color: #e64340;
  &::after {
    border: none;
  }
}
</style>
