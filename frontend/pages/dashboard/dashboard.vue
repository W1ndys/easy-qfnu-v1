<template>
  <PageLayout>
    <!-- 用户信息卡片 -->
    <ModernCard class="profile-card" highlight>
      <view class="profile-content">
        <view class="avatar-section">
          <view class="avatar-wrapper">
            <image
              class="avatar"
              src="/static/logo.png"
              mode="aspectFit"></image>
            <view class="status-indicator"></view>
          </view>
        </view>
        <view class="user-info">
          <text class="welcome-text">欢迎回来</text>
          <text class="user-id">{{ studentId }}</text>
          <text class="user-role">曲园er~</text>
        </view>
      </view>
    </ModernCard>

    <!-- 功能模块 -->
    <ModernCard title="核心功能" class="features-card">
      <view class="features-grid">
        <view
          v-for="(item, index) in features"
          :key="index"
          class="feature-item"
          :class="{ disabled: !item.url }"
          @click="handleNavigate(index)">
          <view class="feature-icon">
            <uni-icons
              :type="item.icon"
              size="40"
              :color="item.url ? '#9b0400' : '#bdc3c7'"></uni-icons>
          </view>
          <view class="feature-content">
            <text class="feature-title">{{ item.text }}</text>
            <text v-if="item.description" class="feature-description">{{
              item.description
            }}</text>
          </view>
          <view class="feature-arrow" v-if="item.url">
            <uni-icons type="right" size="16" color="#bdc3c7"></uni-icons>
          </view>
        </view>
      </view>
    </ModernCard>

    <!-- 快捷操作 -->
    <ModernCard title="快捷操作">
      <view class="quick-actions">
        <button class="action-btn refresh-btn" @click="handleRefresh">
          <uni-icons type="refresh" size="20" color="#ffffff"></uni-icons>
          <text>刷新数据</text>
        </button>
        <button class="action-btn logout-btn" @click="handleLogout">
          <uni-icons type="closeempty" size="20" color="#ffffff"></uni-icons>
          <text>退出登录</text>
        </button>
      </view>
    </ModernCard>
  </PageLayout>
</template>

<script setup>
import { ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { decode } from "../../utils/jwt-decode.js";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import ModernCard from "../../components/ModernCard/ModernCard.vue";

// --- 页面数据 ---
const studentId = ref("加载中...");

// 定义功能列表，使用现代化图标
const features = ref([
  {
    text: "成绩查询",
    description: "查看成绩与GPA分析",
    icon: "paperplane",
    url: "/pages/grades/grades",
  },
  {
    text: "课表查询",
    description: "即将推出",
    icon: "calendar",
    url: "",
  },
  {
    text: "课程评价",
    description: "即将推出",
    icon: "star",
    url: "",
  },
  {
    text: "更多功能",
    description: "敬请期待",
    icon: "gear",
    url: "",
  },
]);

// --- 页面生命周期函数 ---
onLoad(() => {
  checkLoginStatus();
});

// 检查登录状态
const checkLoginStatus = () => {
  const token = uni.getStorageSync("token");

  if (!token) {
    uni.showToast({ title: "请先登录", icon: "none" });
    uni.reLaunch({ url: "/pages/index/index" });
  } else {
    try {
      const payload = decode(token);
      studentId.value = payload.sub;
    } catch (error) {
      console.error("Token解析失败", error);
      uni.showToast({ title: "凭证无效,请重新登录", icon: "none" });
      uni.reLaunch({ url: "/pages/index/index" });
    }
  }
};

// --- 事件处理函数 ---
// 处理功能项点击事件
const handleNavigate = (index) => {
  const targetPage = features.value[index];

  if (targetPage.url) {
    console.log("导航到:", targetPage.url);
    uni.navigateTo({ url: targetPage.url });
  } else {
    uni.showToast({ title: "功能正在开发中...", icon: "none" });
  }
};

// 刷新数据
const handleRefresh = () => {
  uni.showToast({ title: "数据已刷新", icon: "success" });
  checkLoginStatus();
};

// 处理退出登录
const handleLogout = () => {
  uni.showModal({
    title: "确认退出",
    content: "确定要退出登录吗？",
    confirmColor: "#9b0400",
    success: (res) => {
      if (res.confirm) {
        uni.removeStorageSync("token");
        uni.showToast({ title: "已退出登录", icon: "success" });
        setTimeout(() => {
          uni.reLaunch({ url: "/pages/index/index" });
        }, 1000);
      }
    },
  });
};
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

// 用户信息卡片
.profile-card {
  margin-bottom: 40rpx;
}

.profile-content {
  display: flex;
  align-items: center;
  gap: 30rpx;
}

.avatar-section {
  position: relative;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(155, 4, 0, 0.1);
  box-shadow: 0 8rpx 24rpx rgba(155, 4, 0, 0.15);
}

.status-indicator {
  position: absolute;
  bottom: 8rpx;
  right: 8rpx;
  width: 24rpx;
  height: 24rpx;
  background: #52c41a;
  border-radius: 50%;
  border: 3rpx solid #ffffff;
}

.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.welcome-text {
  font-size: 28rpx;
  color: var(--text-secondary);
  font-weight: 400;
}

.user-id {
  font-size: 36rpx;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 1rpx;
}

.user-role {
  font-size: 24rpx;
  color: var(--text-light);
  background: rgba(155, 4, 0, 0.1);
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  display: inline-block;
  width: fit-content;
}

// 功能模块
.features-card {
  margin-bottom: 40rpx;
}

.features-grid {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.feature-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  background: #f8fafc;
  border-radius: var(--radius-small);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 2rpx solid transparent;

  &:active {
    transform: scale(0.98);
    background: #f1f5f9;
  }

  &:not(.disabled):hover {
    background: #ffffff;
    border-color: rgba(155, 4, 0, 0.1);
    box-shadow: 0 8rpx 24rpx rgba(155, 4, 0, 0.1);
  }

  &.disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.feature-icon {
  margin-right: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80rpx;
  height: 80rpx;
  background: rgba(155, 4, 0, 0.05);
  border-radius: 50%;
}

.feature-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.feature-title {
  font-size: 30rpx;
  font-weight: 600;
  color: var(--text-primary);
}

.feature-description {
  font-size: 24rpx;
  color: var(--text-secondary);
}

.feature-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.5;
}

// 快捷操作
.quick-actions {
  display: flex;
  gap: 20rpx;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding: 24rpx;
  border-radius: var(--radius-small);
  font-size: 28rpx;
  font-weight: 600;
  border: none;
  transition: all 0.3s ease;

  &::after {
    border: none;
  }

  &:active {
    transform: scale(0.95);
  }

  text {
    font-weight: inherit;
  }
}

.refresh-btn {
  background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
  color: #ffffff;
  box-shadow: 0 8rpx 24rpx rgba(82, 196, 26, 0.3);

  &:active {
    box-shadow: 0 4rpx 12rpx rgba(82, 196, 26, 0.4);
  }
}

.logout-btn {
  background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
  color: #ffffff;
  box-shadow: 0 8rpx 24rpx rgba(255, 77, 79, 0.3);

  &:active {
    box-shadow: 0 4rpx 12rpx rgba(255, 77, 79, 0.4);
  }
}
</style>
