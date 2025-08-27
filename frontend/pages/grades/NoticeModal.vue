<template>
    <transition name="modal">
        <view v-if="showModal" class="modal-overlay" @click.self="$emit('close')">
            <view class="modal-container">
                <view class="modal-header">
                    <text class="modal-title">成绩查询与GPA分析提示</text>
                </view>
                <view class="modal-content">
                    <text>
                        因不同专业或不同目标院校的要求不同，保研所需要的绩点要求不同，如有需求，请前往底部自定义GPA计算自行计算
                    </text>
                </view>
                <view class="modal-footer">
                    <button class="modal-btn" @click="$emit('close')">我已知晓</button>
                </view>
            </view>
        </view>
    </transition>
</template>

<script setup>
defineProps({
    showModal: {
        type: Boolean,
        default: false
    }
})

defineEmits(['close'])
</script>

<style lang="scss" scoped>
/* 主题变量 */
$primary-color: #7F4515;
$text-color-primary: #343a40;
$background-color-card: #ffffff;
$border-radius-base: 16rpx;
$border-radius-sm: 12rpx;
$font-size-lg: 30rpx;
$font-size-base: 28rpx;

/* 通用弹窗样式 */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

.modal-container {
    background: $background-color-card;
    border-radius: 20rpx;
    max-width: 600rpx;
    padding: 30rpx;
    box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.25);
}

.modal-header,
.modal-title {
    font-size: $font-size-lg;
    font-weight: bold;
    color: $text-color-primary;
}

.modal-content {
    font-size: 26rpx;
    color: #555;
    margin: 20rpx 0;
    line-height: 1.6;
}

.modal-footer {
    text-align: right;
    margin-top: 10rpx;
}

.modal-btn {
    background: $primary-color;
    color: #fff;
    border-radius: $border-radius-sm;
    padding: 16rpx 40rpx;
    font-size: $font-size-base;
}

/* 进入/退出动画 */
.modal-enter-active {
    animation: fadeInUp 0.3s ease forwards;
}

.modal-leave-active {
    animation: fadeOutDown 0.25s ease forwards;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(40rpx);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeOutDown {
    from {
        opacity: 1;
        transform: translateY(0);
    }

    to {
        opacity: 0;
        transform: translateY(40rpx);
    }
}
</style>
