<template>
  <view class="notice-bar" @click="handleClick">
    <uni-icons class="notice-icon" type="sound" size="20" color="#FF6B35"></uni-icons>
    <text class="notice-text">{{ noticeData.title }}</text>
    <uni-icons type="right" size="16" color="#C0C4CC"></uni-icons>
  </view>
</template>

<script setup>
import noticeBarLogic from "./NoticeBar.js";

defineProps({
  noticeData: {
    type: Object,
    required: true,
    default: () => ({
      title: "重要通知：请加用户群防走丢！"
    })
  }
});

const emit = defineEmits(['click']);

const handleClick = () => {
  emit('click');
};
</script>

<style lang="scss" scoped>
@import "./NoticeBar.scss";
</style>
