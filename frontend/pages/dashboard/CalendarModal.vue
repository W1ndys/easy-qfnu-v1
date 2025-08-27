<template>
  <uni-popup ref="calendarPopup" type="center">
    <view class="popup-content calendar-popup">
      <view class="popup-header">
        <text class="popup-title">校历</text>
        <view class="popup-close-btn" @click="closeCalendarModal">
          <uni-icons type="closeempty" size="22" color="#909399"></uni-icons>
        </view>
      </view>
      <view class="popup-body">
        <image class="calendar-image" src="https://picx.zhimg.com/80/v2-1c7d66141af0cd26e90ab42dda86acee.png"
          mode="widthFix" @error="handleCalendarImageError" @load="handleCalendarImageLoad">
        </image>
      </view>
    </view>
  </uni-popup>
</template>

<script setup>
import { ref } from "vue";

const emit = defineEmits(['imageError', 'imageLoad']);

const calendarPopup = ref(null);

const openModal = () => {
  if (calendarPopup.value) {
    calendarPopup.value.open();
  }
};

const closeCalendarModal = () => {
  if (calendarPopup.value) {
    calendarPopup.value.close();
  }
};

const handleCalendarImageError = () => {
  emit('imageError');
};

const handleCalendarImageLoad = () => {
  emit('imageLoad');
};

// 暴露方法给父组件
defineExpose({
  openModal,
  closeCalendarModal
});
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

.calendar-popup {
  width: 95vw;
  max-width: 720rpx;
}

.popup-content {
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

.calendar-image {
  width: 100%;
  border-radius: var(--radius-medium);
  box-shadow: 0 8rpx 24rpx var(--shadow-light);
}
</style>
