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
import featureGridLogic from "./FeatureGrid.js";

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
@import "./FeatureGrid.scss";
</style>
