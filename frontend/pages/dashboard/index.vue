<template>
  <PageLayout>
    <view class="page-rounded-container">
      <!-- 用户信息卡片 -->
      <ModernCard class="profile-card" highlight>
        <view class="profile-content">
          <view class="avatar-section">
            <view class="avatar-wrapper">
              <image class="avatar" src="https://pic1.zhimg.com/80/v2-82c1c70c69720aadac79594ea50ed4a7.png"
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

      <!-- 公告栏 -->
      <ModernCard class="announcement-card">
        <view class="announcement-header">
          <uni-icons type="sound" size="16" color="#1890ff"></uni-icons>
          <text class="announcement-title">公告栏</text>
        </view>

        <text class="announcement-text">该程序正在测试阶段，功能可能不稳定</text>
        <text class="announcement-text">加入QQ群获取最新消息：<text class="qq-link" @click="copyQQGroup">1053432087</text></text>

        <text class="announcement-text">如有对Easy-QFNU（曲奇教务）有建议意见或开发想法或其他相关内容的欢迎添加Easy-QFNU开发策划交流群：<text class="qq-link"
            @click="copyDevQQGroup">1057327742</text></text>
      </ModernCard>

      <!-- 2×2 导航网格 -->
      <ModernCard class="grid-card">
        <view class="grid-title">核心功能</view>
        <view class="grid-2x2">
          <view v-for="(item, index) in features" :key="index" class="grid-cell" :class="{ disabled: !item.url }"
            @click="handleNavigate(index)">
            <view class="cell-icon">
              <uni-icons :type="item.icon" size="30" :color="item.url ? '#7F4515' : '#C0C6CF'" />
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
          <button class="action-btn clear-cache-btn" @click="handleClearCache">
            <uni-icons type="trash" size="20" color="#ffffff"></uni-icons>
            <text>清除缓存</text>
          </button>
          <button class="action-btn agreement-btn" @click="handleUserAgreement">
            <uni-icons type="paperplane" size="20" color="#ffffff"></uni-icons>
            <text>用户协议</text>
          </button>
          <button class="action-btn changelog-btn" @click="handleChangelog">
            <uni-icons type="list" size="20" color="#ffffff"></uni-icons>
            <text>更新日志</text>
          </button>
          <button class="action-btn contact-btn" @click="handleContact">
            <uni-icons type="chatbubble" size="20" color="#ffffff"></uni-icons>
            <text>联系作者</text>
          </button>
        </view>
      </ModernCard>

      <!-- 赞赏支持 -->
      <ModernCard title="支持开发" class="support-card">
        <view class="support-content">
          <view class="support-text">
            <text class="support-title">助力项目发展</text>
            <text class="support-desc">本服务完全免费试用，服务器每日支出约为7元左右，以及前期服务器设备等支出几百依赖作者个人支出。如果想支持作者助力开发维护，欢迎赞赏~</text>
          </view>
          <view class="qr-code-container">
            <image class="qr-code"
              src="https://picx.zhimg.com/80/v2-076422270c197b0031c609e47be2e36c_720w.png?source=d16d100b"
              mode="aspectFit" @error="handleImageError" @load="handleImageLoad">
            </image>
            <text class="qr-code-label">微信赞赏</text>
          </view>
        </view>
      </ModernCard>
    </view>
  </PageLayout>
</template>

<script setup>
import { ref } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
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
    text: "培养方案",
    description: "查看模块完成进度",
    icon: "list",
    url: "/pages/course-plan/index",
  },
  {
    text: "预选课查询",
    description: "夫子校园提供技术支持",
    icon: "checkmarkempty",
    url: "http://xk.s.fz.z-xin.net/",
    external: true, // 标记为外部链接
  },
  {
    text: "课表查询",
    description: "即将推出",
    icon: "calendar",
    url: "",
  },
  {
    text: "排名查询",
    description: "即将推出",
    icon: "medal",
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

onShow(() => {
  // 页面显示时也检查登录状态
  checkLoginStatus();
});

// 检查登录状态
const checkLoginStatus = () => {
  const token = uni.getStorageSync("token");

  if (!token) {
    uni.showToast({ title: "请先登录", icon: "none" });
    uni.reLaunch({ url: "/pages/index/index" });
    return;
  } else {
    try {
      const payload = decode(token);
      studentId.value = payload.sub;
    } catch (error) {
      console.error("Token解析失败", error);
      uni.removeStorageSync("token");
      uni.showToast({ title: "凭证无效,请重新登录", icon: "none" });
      uni.reLaunch({ url: "/pages/index/index" });
      return;
    }
  }
};

// --- 事件处理函数 ---
// 处理功能项点击事件
const handleNavigate = (index) => {
  const targetPage = features.value[index];

  if (targetPage.url) {
    // 外部链接处理
    if (targetPage.external) {
      // #ifdef H5
      window.open(targetPage.url, "_blank");
      // #endif

      // #ifdef MP
      uni.setClipboardData({
        data: targetPage.url,
        success: () => {
          uni.showToast({
            title: "外链已复制，请在浏览器中打开",
            icon: "success",
            duration: 3000
          });
        },
      });
      // #endif

      // #ifdef APP-PLUS
      plus.runtime.openURL(targetPage.url);
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

// 清除缓存
const handleClearCache = () => {
  uni.showModal({
    title: "清除缓存",
    content: "确定要清除所有本地缓存数据吗？这将清除除登录凭证外的所有本地数据。",
    confirmText: "清除",
    cancelText: "取消",
    confirmColor: "#ff4d4f",
    success: (res) => {
      if (res.confirm) {
        try {
          // 获取当前token，避免清除登录状态
          const currentToken = uni.getStorageSync("token");

          // 清除所有存储
          uni.clearStorageSync();

          // 恢复token，保持登录状态
          if (currentToken) {
            uni.setStorageSync("token", currentToken);
          }

          uni.showToast({
            title: "缓存已清除",
            icon: "success",
            duration: 2000
          });
        } catch (error) {
          console.error("清除缓存失败:", error);
          uni.showToast({
            title: "清除缓存失败",
            icon: "error"
          });
        }
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
        title: "QQ群号已复制到剪贴板，请自行搜索加群",
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

// 复制开发QQ群号
const copyDevQQGroup = () => {
  uni.setClipboardData({
    data: "1057327742",
    success: () => {
      uni.showToast({
        title: "开发交流群号已复制到剪贴板，请自行搜索加群",
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

// 处理用户协议
const handleUserAgreement = () => {
  const url = "https://cq4hqujcxu3.feishu.cn/docx/EYE6d5ufAoQt5Axx7MFc4XMrnAf";
  handleExternalLink("用户协议", url);
};

// 处理更新日志
const handleChangelog = () => {
  const url = "https://cq4hqujcxu3.feishu.cn/docx/BO2od7OI8omtmTxGkB0cn305nFl";
  handleExternalLink("更新日志", url);
};

// 处理联系作者
const handleContact = () => {
  const qqNumber = "2769731875";
  uni.showModal({
    title: "联系作者",
    content: `作者QQ号：${qqNumber}\n\n选择操作：`,
    confirmText: "复制QQ号",
    cancelText: "取消",
    confirmColor: "#7F4515",
    success: (res) => {
      if (res.confirm) {
        uni.setClipboardData({
          data: qqNumber,
          success: () => {
            uni.showToast({
              title: "QQ号已复制到剪贴板",
              icon: "success",
            });
          },
        });
      }
    },
  });
};

// 统一处理外部链接
const handleExternalLink = (title, url) => {
  // #ifdef H5
  window.open(url, "_blank");
  // #endif

  // #ifdef MP
  uni.setClipboardData({
    data: url,
    success: () => {
      uni.showToast({
        title: "外链已复制，请在浏览器中打开",
        icon: "success",
        duration: 3000
      });
    },
  });
  // #endif

  // #ifdef APP-PLUS
  plus.runtime.openURL(url);
  // #endif
};

// 处理图片加载错误
const handleImageError = () => {
  uni.showToast({
    title: "赞赏码加载失败",
    icon: "none"
  });
};

// 处理图片加载成功
const handleImageLoad = () => {
  console.log("赞赏码加载成功");
};
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

// 页外层统一圆角白卡容器
.page-rounded-container {
  background: #fff;
  border-radius: 32rpx; // 缩小圆角
  padding: 18rpx 12rpx; // 减少整体 padding
  box-shadow: 0 8rpx 24rpx var(--shadow-light);
  border: 1rpx solid var(--border-light);
}

// 用户信息卡片
.profile-card {
  margin-bottom: 24rpx; // 减少间距

  :deep(.card-content) {
    padding: 18rpx 12rpx !important; // 减少内容 padding
  }
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

// 公告栏卡片
.announcement-card {
  margin-bottom: 24rpx;

  :deep(.card-content) {
    background: #f0f9ff !important;
    border: 1rpx solid #bae7ff !important;
    border-radius: var(--radius-medium) !important;
    padding: 16rpx 12rpx !important; // 缩小 padding
  }
}

.announcement-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.announcement-title {
  font-size: 28rpx;
  color: #1890ff;
  font-weight: 600;
  margin-left: 8rpx;
}

.announcement-text {
  font-size: 26rpx;
  color: #1890ff;
  line-height: 1.6;
  margin-bottom: 16rpx;
  display: block;

  &:last-child {
    margin-bottom: 0;
  }
}

.qq-link {
  color: #1890ff;
  text-decoration: underline;
  font-weight: 600;
  padding: 2rpx 4rpx;
  background: rgba(24, 144, 255, 0.1);
  border-radius: 4rpx;
}

// 2×2 导航网格样式
.grid-card {
  margin-bottom: 24rpx;

  :deep(.card-content) {
    padding: 16rpx 12rpx !important;
  }
}

.grid-title {
  font-size: 26rpx;
  margin-bottom: 12rpx;
}

.grid-2x2 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300rpx, 1fr));
  gap: 12rpx; // 缩小网格间距

  // 响应式调整
  @media (max-width: 750px) {
    grid-template-columns: repeat(auto-fit, minmax(280rpx, 1fr));
    gap: 16rpx;
  }

  @media (max-width: 500px) {
    grid-template-columns: repeat(auto-fit, minmax(240rpx, 1fr));
    gap: 12rpx;
  }
}

.grid-cell {
  background: #ffffff;
  border: 1rpx solid var(--border-light);
  border-radius: var(--radius-medium);
  padding: 18rpx 12rpx; // 缩小卡片内容 padding
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10rpx;
  transition: all 0.2s ease;
  min-height: 120rpx;

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
  flex-wrap: wrap;
  gap: 10rpx;
}

.action-btn {
  flex: 1;
  min-width: calc(50% - 5rpx);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  height: 56rpx;
  padding: 10rpx 12rpx;
  border-radius: 9999rpx;
  font-size: 22rpx;
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

.clear-cache-btn {
  background: linear-gradient(135deg, #f5222d 0%, #ff4d4f 100%);
  color: #ffffff;
  box-shadow: 0 8rpx 24rpx rgba(245, 34, 45, 0.3);

  &:active {
    box-shadow: 0 4rpx 12rpx rgba(245, 34, 45, 0.4);
  }
}

.agreement-btn {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: #ffffff;
  box-shadow: 0 8rpx 24rpx rgba(24, 144, 255, 0.3);

  &:active {
    box-shadow: 0 4rpx 12rpx rgba(24, 144, 255, 0.4);
  }
}

.changelog-btn {
  background: linear-gradient(135deg, #722ed1 0%, #9254de 100%);
  color: #ffffff;
  box-shadow: 0 8rpx 24rpx rgba(114, 46, 209, 0.3);

  &:active {
    box-shadow: 0 4rpx 12rpx rgba(114, 46, 209, 0.4);
  }
}

.contact-btn {
  background: linear-gradient(135deg, #fa8c16 0%, #ffa940 100%);
  color: #ffffff;
  box-shadow: 0 8rpx 24rpx rgba(250, 140, 22, 0.3);

  &:active {
    box-shadow: 0 4rpx 12rpx rgba(250, 140, 22, 0.4);
  }
}

// 赞赏支持卡片
.support-card {
  margin-top: 24rpx;

  :deep(.card-content) {
    padding: 16rpx 12rpx !important;
  }
}

.support-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18rpx;
}

.support-text {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  text-align: center;
}

.support-title {
  font-size: 32rpx;
  color: var(--text-primary);
  font-weight: 600;
}

.support-desc {
  font-size: 26rpx;
  color: var(--text-secondary);
  line-height: 1.6;
  text-align: center;
}

.qr-code-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}

.qr-code {
  width: 220rpx;
  height: 220rpx;
  border-radius: var(--radius-medium);
  border: 1rpx solid var(--border-light);
  box-shadow: 0 8rpx 24rpx var(--shadow-light);
}

.qr-code-label {
  font-size: 24rpx;
  color: var(--text-light);
  text-align: center;
}
</style>