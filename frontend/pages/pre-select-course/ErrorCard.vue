<template>
    <ModernCard v-if="debugInfo" title="查询出错">
        <view class="card-section">
            <text class="section-desc">抱歉，查询时遇到问题，请稍后重试。</text>
            <text class="section-desc muted-text">状态码：{{ debugInfo.statusCode }}</text>
            <view v-if="debugInfo.message" class="error-details">
                <text class="error-label">错误详情：</text>
                <text class="error-message">{{ debugInfo.message }}</text>
            </view>
        </view>
        <view class="button-group">
            <button class="action-btn secondary-btn" @click="$emit('copyDebug')">
                <uni-icons type="copy" size="20" color="#495057" />
                <text>复制详细诊断信息</text>
            </button>
        </view>
    </ModernCard>
    <view v-else />
</template>

<script setup>
import { defineProps } from "vue";
import ModernCard from "../../components/ModernCard/ModernCard.vue";

defineProps({
    debugInfo: { type: Object, default: null },
});
</script>

<style lang="scss" scoped>
.card-section .section-desc {
    display: block;
    margin-bottom: 8rpx;
    font-size: 26rpx;
    color: var(--text-primary);
}

.muted-text {
    color: var(--text-secondary);
    font-size: 24rpx;
}

.error-details {
    margin-top: 16rpx;
    padding: 16rpx;
    background: #f8f9fa;
    border-radius: 8rpx;
    border-left: 4rpx solid #dc3545;
}

.error-label {
    display: block;
    font-size: 24rpx;
    font-weight: 600;
    color: #dc3545;
    margin-bottom: 8rpx;
}

.error-message {
    display: block;
    font-size: 24rpx;
    color: #495057;
    line-height: 1.5;
    word-break: break-all;
    white-space: pre-wrap;
}

.action-btn {
    height: 72rpx;
    border-radius: 9999rpx;
    font-size: 26rpx;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12rpx;
    border: none;
    transition: all 0.3s;
}

.action-btn::after {
    border: none;
}

.action-btn:active {
    transform: scale(0.95);
}

.secondary-btn {
    background: #f1f3f5;
    color: var(--text-primary);
    border: 2rpx solid #f1f3f5;
}

.secondary-btn:active {
    background: #e9ecef;
    border-color: #dee2e6;
}

.button-group {
    margin-top: 20rpx;
    display: flex;
    justify-content: center;
}
</style>
