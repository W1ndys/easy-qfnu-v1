<template>
  <ModernCard class="grid-card">
    <view class="grid-title">核心功能</view>
    <view class="grid-2x2">
      <view v-for="(item, index) in features" :key="index" class="grid-cell" :class="{ disabled: !item.url }"
        @click="handleNavigate(index)">
        <view class="cell-icon">
          <uni-icons :type="item.icon" size="30" :color="item.url ? '#7F4515' : '#C0C6CF'" />
        </view>
        <text class="cell-title">{{ item.text }}</text>
        <text v-if="item.description" class="cell-desc">{{ item.description }}</text>
      </view>
    </view>
  </ModernCard>
</template>

<script setup>
import ModernCard from "../../components/ModernCard/ModernCard.vue";

const props = defineProps({
  features: {
    type: Array,
    required: true,
    default: () => []
  }
});

const emit = defineEmits(['navigate']);

const handleNavigate = (index) => {
  emit('navigate', index);
};
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

.grid-card {
  margin-bottom: 16rpx;

  :deep(.card-content) {
    padding: 12rpx 8rpx !important;
  }
}

.grid-title {
  font-size: 26rpx;
  margin-bottom: 8rpx;
}

.grid-2x2 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300rpx, 1fr));
  gap: 8rpx;

  @media (max-width: 750px) {
    grid-template-columns: repeat(auto-fit, minmax(280rpx, 1fr));
    gap: 12rpx;
  }

  @media (max-width: 500px) {
    grid-template-columns: repeat(auto-fit, minmax(240rpx, 1fr));
    gap: 8rpx;
  }
}

.grid-cell {
  background: #ffffff;
  border: 1rpx solid var(--border-light);
  border-radius: var(--radius-medium);
  padding: 12rpx 8rpx;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8rpx;
  transition: all 0.2s ease;
  min-height: 100rpx;

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
</style>
