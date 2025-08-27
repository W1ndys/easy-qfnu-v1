<template>
  <uni-popup ref="noticePopup" type="center" @change="handleNoticePopupChange">
    <view class="popup-content">
      <view class="popup-header">
        <text class="popup-title">公告详情</text>
        <view class="popup-close-btn" @click="closeNoticeModal">
          <uni-icons type="closeempty" size="22" color="#909399"></uni-icons>
        </view>
      </view>
      <view class="popup-body">
        <rich-text class="status-text" :nodes="noticeData.content"></rich-text>

        <!-- 添加QQ号复制按钮 -->
        <view class="qq-copy-section">
          <text class="copy-label">快速复制QQ号：</text>
          <button class="qq-copy-btn" @click="copyQQNumber">
            <uni-icons type="copy" size="16" color="#7F4515"></uni-icons>
            <text>1053240065</text>
          </button>
        </view>

        <view class="community-content-wrapper">
          <view class="community-groups">
            <view class="group-item">
              <view class="group-info">
                <view class="group-name">
                  <uni-icons type="sound" size="20" color="#7F4515"></uni-icons>
                  <text class="group-title">官方消息群</text>
                </view>
                <text class="group-desc">获取最新消息和通知</text>
              </view>
              <button class="popup-action-btn" @click="openOfficialGroupLink">
                <uni-icons type="copy" size="16" color="#7F4515"></uni-icons>
                <text>加入群聊</text>
              </button>
            </view>
            <view class="group-item">
              <view class="group-info">
                <view class="group-name">
                  <uni-icons type="star" size="20" color="#7F4515"></uni-icons>
                  <text class="group-title">开发交流群</text>
                </view>
                <text class="group-desc">建议反馈、开发想法交流</text>
              </view>
              <button class="popup-action-btn" @click="openDevQQGroupLink">
                <uni-icons type="copy" size="16" color="#7F4515"></uni-icons>
                <text>加入群聊</text>
              </button>
            </view>
          </view>
        </view>
      </view>
    </view>
  </uni-popup>
</template>

<script setup>
import { ref, nextTick } from "vue";

const props = defineProps({
  noticeData: {
    type: Object,
    required: true,
    default: () => ({
      content: "",
      version: "1"
    })
  }
});

const emit = defineEmits(['close', 'popupChange']);

const noticePopup = ref(null);

const openModal = () => {
  if (noticePopup.value) {
    noticePopup.value.open();
  }
};

const closeNoticeModal = () => {
  if (noticePopup.value) {
    noticePopup.value.close();
  }
};

const handleNoticePopupChange = (e) => {
  emit('popupChange', e);
};

const copyQQNumber = () => {
  const qqNumber = "1053240065";
  uni.setClipboardData({
    data: qqNumber,
    success: () => {
      uni.showToast({
        title: `QQ号 ${qqNumber} 已复制`,
        icon: "success",
        duration: 2000
      });
    },
    fail: () => {
      uni.showToast({
        title: "复制失败，请手动复制",
        icon: "none"
      });
    }
  });
};

const openOfficialGroupLink = () => {
  const url = 'https://qm.qq.com/q/jKCk6GtL1e';
  // #ifdef H5
  window.open(url, '_blank');
  // #endif
  // #ifndef H5
  uni.setClipboardData({
    data: url,
    success: () => {
      uni.showToast({ title: '已复制群链接，请在浏览器打开', icon: 'none' });
    }
  });
  // #endif
};

const openDevQQGroupLink = () => {
  const url = 'https://qm.qq.com/q/BBYFdHBDEc';
  // #ifdef H5
  window.open(url, '_blank');
  // #endif
  // #ifndef H5
  uni.setClipboardData({
    data: url,
    success: () => {
      uni.showToast({ title: '已复制群链接，请在浏览器打开', icon: 'none' });
    }
  });
  // #endif
};

// 暴露方法给父组件
defineExpose({
  openModal,
  closeNoticeModal
});
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

.popup-content {
  width: 90vw;
  max-width: 680rpx;
  background-color: #f8f8f8;
  border-radius: 24rpx;
  box-shadow: 0 10rpx 40rpx rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 32rpx;
  border-bottom: 1rpx solid var(--border-light);
}

.popup-title {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--text-primary);
}

.popup-close-btn {
  padding: 8rpx;
  border-radius: 50%;

  &:active {
    background-color: #e0e0e0;
  }
}

.popup-body {
  padding: 12rpx 32rpx;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  max-height: 70vh;
  overflow-y: auto;
}

.status-text {
  font-size: 26rpx;
  color: #8b4513;
  line-height: 1.5;
  margin-top: 0;
  padding-left: 10rpx;
}

.qq-copy-section {
  background: #ffffff;
  padding: 20rpx;
  border-radius: var(--radius-medium);
  border: 1rpx solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.copy-label {
  font-size: 26rpx;
  color: var(--text-secondary);
  font-weight: 500;
}

.qq-copy-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 20rpx;
  background: rgba(127, 69, 21, 0.08);
  border: 1rpx solid rgba(127, 69, 21, 0.15);
  border-radius: 20rpx;
  font-size: 24rpx;
  color: #7f4515;
  font-weight: 600;
  transition: all 0.2s ease;
  min-width: 160rpx;
  justify-content: center;

  &::after {
    border: none;
  }

  &:active {
    background: rgba(127, 69, 21, 0.15);
    transform: scale(0.95);
  }

  text {
    font-weight: inherit;
  }
}

.community-content-wrapper {
  background: #ffffff;
  padding: 20rpx;
  border-radius: var(--radius-medium);
  border: 1rpx solid var(--border-light);
}

.community-groups {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.group-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx;
  background: rgba(127, 69, 21, 0.03);
  border: 1rpx solid rgba(127, 69, 21, 0.08);
  border-radius: 12rpx;
}

.group-info {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
  flex: 1;
}

.group-name {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.group-title {
  font-size: 26rpx;
  color: var(--text-primary);
  font-weight: 600;
}

.group-desc {
  font-size: 22rpx;
  color: var(--text-secondary);
  line-height: 1.4;
  padding-left: 28rpx;
}

.popup-action-btn {
  display: flex;
  align-items: center;
  gap: 6rpx;
  padding: 8rpx 16rpx;
  background: rgba(127, 69, 21, 0.08);
  border: 1rpx solid rgba(127, 69, 21, 0.15);
  border-radius: 20rpx;
  font-size: 22rpx;
  color: #7f4515;
  font-weight: 500;
  transition: all 0.2s ease;
  min-width: 120rpx;
  justify-content: center;

  &::after {
    border: none;
  }

  &:active {
    background: rgba(127, 69, 21, 0.15);
    transform: scale(0.95);
  }

  text {
    font-weight: inherit;
  }
}
</style>
