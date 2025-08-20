<template>
  <PageLayout>
    <view class="page-rounded-container">
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

      <!-- 测试阶段提示 -->
      <ModernCard class="test-notice-card">
        <view class="test-notice">
          <view class="notice-header">
            <uni-icons type="info" size="16" color="#ff9500"></uni-icons>
            <text class="notice-title">测试阶段</text>
          </view>
          <view class="notice-content">
            <text class="notice-text">该程序正在测试阶段，功能可能不稳定</text>
            <view class="qq-group">
              <text class="qq-label">加入QQ群获取最新消息：</text>
              <text class="qq-number" @click="copyQQGroup">1053432087</text>
            </view>
          </view>
        </view>
      </ModernCard>

      <!-- 2×2 导航网格 -->
      <ModernCard class="grid-card">
        <view class="grid-title">核心功能</view>
        <view class="grid-2x2">
          <view
            v-for="(item, index) in features"
            :key="index"
            class="grid-cell"
            :class="{ disabled: !item.url }"
            @click="handleNavigate(index)">
            <view class="cell-icon">
              <uni-icons
                :type="item.icon"
                size="30"
                :color="item.url ? '#7F4515' : '#C0C6CF'" />
            </view>
            <text class="cell-title">{{ item.text }}</text>
            <text v-if="item.description" class="cell-desc">{{
              item.description
            }}</text>
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
    </view>
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
    url: "/pages/grades/index",
  },
  {
    text: "平均分查询",
    description: "查看课程平均分数据",
    icon: "bars",
    url: "/pages/average-scores/index",
  },
  {
    text: "选课推荐",
    description: "智能推荐选课方案",
    icon: "star",
    url: "https://doc.easy-qfnu.top/EasySelectCourse/CourseSelectionRecommendation/",
    external: true, // 标记为外部链接
  },
  {
    text: "课表查询",
    description: "即将推出",
    icon: "calendar",
    url: "",
  },
  {
    text: "培养计划",
    description: "即将推出",
    icon: "list",
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

    // 检查是否为外部链接
    if (targetPage.external) {
      // 处理外部链接
      // #ifdef APP-PLUS
      plus.runtime.openURL(targetPage.url);
      // #endif

      // #ifdef H5
      window.open(targetPage.url, "_blank");
      // #endif

      // #ifdef MP
      // 小程序环境下复制链接到剪贴板
      uni.setClipboardData({
        data: targetPage.url,
        success: () => {
          uni.showToast({
            title: "链接已复制到剪贴板",
            icon: "success",
          });
        },
      });
      // #endif
    } else {
      // 内部页面导航
      uni.navigateTo({ url: targetPage.url });
    }
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
    confirmColor: "#7F4515",
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

// 复制QQ群号
const copyQQGroup = () => {
  uni.setClipboardData({
    data: "1053432087",
    success: () => {
      uni.showToast({
        title: "QQ群号已复制",
        icon: "success",
      });
    },
    fail: (err) => {
      console.error("复制失败:", err);
      uni.showToast({
        title: "复制失败",
        icon: "none",
      });
    },
  });
};
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

// 页外层统一圆角白卡容器
.page-rounded-container {
  background: #ffffff;
  border-radius: 40rpx;
  padding: 30rpx;
  box-shadow: 0 20rpx 60rpx var(--shadow-light);
  border: 1rpx solid var(--border-light);
}

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

// 测试阶段提示卡片
.test-notice-card {
  margin-bottom: 40rpx;
  background: #fffbe6;
  border: 1rpx solid #ffe58f;
  border-radius: var(--radius-medium);
  padding: 28rpx;
  display: flex;
  flex-direction: column;
  gap: 15rpx;
}

.test-notice {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.notice-header {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.notice-title {
  font-size: 28rpx;
  color: #faad14;
  font-weight: 600;
}

.notice-content {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.notice-text {
  font-size: 24rpx;
  color: var(--text-secondary);
  line-height: 1.5;
}

.qq-group {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.qq-label {
  font-size: 24rpx;
  color: var(--text-secondary);
}

.qq-number {
  font-size: 24rpx;
  color: #1890ff;
  text-decoration: underline;
  cursor: pointer;
}

// 2×2 导航网格样式
.grid-card {
  margin-bottom: 40rpx;
}

.grid-title {
  font-size: 28rpx;
  color: var(--text-secondary);
  margin-bottom: 20rpx;
}

.grid-2x2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}

.grid-cell {
  background: #ffffff;
  border: 1rpx solid var(--border-light);
  border-radius: var(--radius-medium);
  padding: 28rpx;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10rpx;
  transition: all 0.2s ease;

  &:active {
    transform: scale(0.98);
  }
  &:not(.disabled):hover {
    box-shadow: 0 12rpx 34rpx var(--shadow-light);
    transform: translateY(-2rpx);
  }
  &.disabled {
    opacity: 0.6;
  }
}

.cell-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  background: rgba(127, 69, 21, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cell-title {
  font-size: 30rpx;
  color: var(--text-primary);
  font-weight: 600;
}

.cell-desc {
  font-size: 24rpx;
  color: var(--text-light);
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
  height: 72rpx;
  padding: 16rpx 24rpx;
  border-radius: 9999rpx;
  font-size: 26rpx;
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
