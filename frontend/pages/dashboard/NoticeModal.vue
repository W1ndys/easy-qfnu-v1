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
import { ref } from "vue";
import noticeModalLogic from "./NoticeModal.js";

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
@import "./NoticeModal.scss";
</style>
