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
import calendarModalLogic from "./CalendarModal.js";

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
@import "./CalendarModal.scss";
</style>
