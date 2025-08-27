<template>
    <view>
        <view class="custom-gpa-toggle-section">
            <view class="toggle-left">
                <text class="toggle-title">自定义GPA计算</text>
                <text class="toggle-desc">勾选课程以计算特定GPA</text>
            </view>
            <switch :checked="isCustomMode" @change="handleToggle" color="#7F4515" />
        </view>

        <view v-if="isCustomMode" class="custom-mode-tip">
            <view class="tip-icon">💡</view>
            <text class="tip-text">请勾选 **需要计入** GPA的课程</text>
        </view>
    </view>
</template>

<script setup>
const props = defineProps({
    isCustomMode: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['toggle'])

const handleToggle = (e) => {
    emit('toggle', e.detail.value)
}
</script>

<style lang="scss" scoped>
/* 主题变量 */
$primary-color: #7F4515;
$primary-color-light: #F5EFE6;
$text-color-primary: #343a40;
$text-color-muted: #8c7d70;
$border-color: #f0e9e4;
$background-color-card: #ffffff;
$border-radius-base: 16rpx;
$border-radius-sm: 12rpx;
$font-size-lg: 30rpx;
$font-size-sm: 24rpx;

/* 自定义GPA切换 */
.custom-gpa-toggle-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: $background-color-card;
    padding: 20rpx;
    border-radius: $border-radius-base;
    margin: 25rpx 0;
    border: 1rpx solid $border-color;

    .toggle-left {
        .toggle-title {
            display: block;
            font-size: $font-size-lg;
            font-weight: bold;
            color: $text-color-primary;
            margin-bottom: 4rpx;
        }

        .toggle-desc {
            font-size: $font-size-sm;
            color: $text-color-muted;
        }
    }
}

/* 自定义模式提示 */
.custom-mode-tip {
    display: flex;
    align-items: center;
    padding: 16rpx;
    background: $primary-color-light;
    border-radius: $border-radius-sm;
    margin-bottom: 25rpx;
    border-left: 6rpx solid $primary-color;

    .tip-icon {
        font-size: 26rpx;
        margin-right: 12rpx;
    }

    .tip-text {
        color: $primary-color;
        font-size: $font-size-sm;
        line-height: 1.4;
    }
}
</style>
