<template>
  <ModernCard title="支持开发" class="support-card">
    <view class="support-content">
      <view class="support-text">
        <text class="support-title">助力项目发展</text>
        <text class="support-desc">本服务完全免费使用，服务器每日支出约为7元左右（选课高峰期翻2-3倍），以及前期服务器设备等支出几百依赖作者个人支出。如果想支持作者助力开发维护，欢迎赞赏~</text>
      </view>
      <view class="qr-code-container">
        <image class="qr-code"
          src="https://picx.zhimg.com/80/v2-076422270c197b0031c609e47be2e36c_720w.png?source=d16d100b" mode="aspectFit"
          @error="handleImageError" @load="handleImageLoad">
        </image>
        <text class="qr-code-label">微信赞赏</text>
      </view>
    </view>
  </ModernCard>
</template>

<script setup>
import ModernCard from "../../components/ModernCard/ModernCard.vue";
import supportCardLogic from "./SupportCard.js";

const emit = defineEmits(['imageError', 'imageLoad']);

const handleImageError = () => {
  emit('imageError');
};

const handleImageLoad = () => {
  emit('imageLoad');
};
</script>

<style lang="scss" scoped>
@import "./SupportCard.scss";
</style>
