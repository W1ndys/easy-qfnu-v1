<template>
  <view class="notice-bar" @click="handleClick">
    <uni-icons class="notice-icon" type="sound" size="20" color="#FF6B35"></uni-icons>
    <text class="notice-text">{{ noticeData.title }}</text>
    <uni-icons type="right" size="16" color="#C0C4CC"></uni-icons>
  </view>
</template>

<script setup>
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
@import "../../styles/common.scss";

.notice-bar {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 16rpx 20rpx;
  margin: 16rpx 0;
  background: linear-gradient(135deg, #fffaf3 0%, #fff7e6 100%);
  border: 1rpx solid rgba(255, 107, 53, 0.2);
  border-radius: var(--radius-medium);
  box-shadow: 0 4rpx 12rpx rgba(255, 107, 53, 0.05);
  transition: all 0.2s ease-in-out;

  &:active {
    transform: scale(0.98);
    box-shadow: none;
  }
}

.notice-icon {
  flex-shrink: 0;
}

.notice-text {
  flex: 1;
  font-size: 26rpx;
  color: #c46a32;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
