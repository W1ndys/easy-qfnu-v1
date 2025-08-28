<template>
    <uni-popup ref="warningPopup" type="center" background-color="rgba(0, 0, 0, 0.5)" :mask-click="false">
        <view class="warning-modal">
            <!-- 警告图标 -->
            <view class="warning-icon">
                <uni-icons type="info" size="60" color="#ff9500" />
            </view>

            <!-- 标题 -->
            <view class="modal-title">
                <text class="title-text">功能测试提醒</text>
            </view>

            <!-- 内容 -->
            <view class="modal-content">
                <text class="content-text">
                    本课程表功能尚未经过充分测试，可能存在数据不准确或功能不稳定的情况，请勿完全依赖。
                </text>
                <text class="content-text">
                    使用过程中遇到任何问题，欢迎随时反馈。
                </text>
            </view>

            <!-- 按钮组 -->
            <view class="modal-actions">
                <button class="action-btn primary-btn" @click="handleConfirm">
                    我已知晓
                </button>
            </view>
        </view>
    </uni-popup>
</template>

<script setup>
import { ref } from 'vue';

const emit = defineEmits(['confirm']);

const warningPopup = ref(null);

// 显示弹窗
function show() {
    warningPopup.value?.open();
}

// 隐藏弹窗
function hide() {
    warningPopup.value?.close();
}

// 确认
function handleConfirm() {
    hide();
    emit('confirm');
}

// 暴露方法给父组件
defineExpose({
    show,
    hide
});
</script>

<style lang="scss" scoped>
.warning-modal {
    width: 600rpx;
    background: #fff;
    border-radius: 24rpx;
    padding: 40rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
    box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.15);
    position: relative;
}

.warning-icon {
    margin-bottom: 24rpx;
    animation: bounce 2s infinite;
}

@keyframes bounce {

    0%,
    20%,
    50%,
    80%,
    100% {
        transform: translateY(0);
    }

    40% {
        transform: translateY(-10rpx);
    }

    60% {
        transform: translateY(-5rpx);
    }
}

.modal-title {
    margin-bottom: 24rpx;
}

.title-text {
    font-size: 32rpx;
    font-weight: 700;
    color: #2c3e50;
    text-align: center;
}

.modal-content {
    margin-bottom: 32rpx;
    text-align: center;
}

.content-text {
    display: block;
    font-size: 26rpx;
    color: #495057;
    line-height: 1.6;
    margin-bottom: 16rpx;

    &:last-child {
        margin-bottom: 0;
    }
}

.highlight-text {
    color: #7f4515;
    font-weight: 600;
}

.modal-actions {
    display: flex;
    gap: 16rpx;
    width: 100%;
}

.action-btn {
    flex: 1;
    height: 80rpx;
    border-radius: 16rpx;
    font-size: 28rpx;
    font-weight: 600;
    border: none;
    transition: all 0.3s ease;

    &::after {
        border: none;
    }

    &:active {
        transform: scale(0.95);
    }
}

.primary-btn {
    background: linear-gradient(135deg, #7f4515 0%, #8c5527 100%);
    color: #fff;

    &:active {
        background: linear-gradient(135deg, #6d3a12 0%, #7a4a20 100%);
    }
}

.secondary-btn {
    background: #f8f9fa;
    color: #495057;
    border: 2rpx solid #dee2e6;

    &:active {
        background: #e9ecef;
    }
}

.no-remind-option {
    width: 100%;
}

.checkbox-label {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8rpx;
}

.checkbox-text {
    font-size: 24rpx;
    color: #6c757d;
}

/* 自定义checkbox样式 */
checkbox {
    transform: scale(0.8);
}
</style>
