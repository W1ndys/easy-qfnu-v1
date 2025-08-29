<template>
    <view class="disclaimer-card modern-card">
        <view class="disclaimer-header">
            <view class="disclaimer-icon">
                <uni-icons type="info-filled" size="24" color="#ff6b35"></uni-icons>
            </view>
            <text class="disclaimer-title">重要声明</text>
        </view>
        <view class="disclaimer-content">
            <text class="disclaimer-text">
                本题库由新生手册根据大模型生成，仅供参考。使用前请确保您已充分阅读并学习曲阜师范大学新生手册内容并遵守相关规定。使用本程序造成的一切后果与本程序无关，使用本程序即代表您同意上方声明内容。
            </text>
        </view>
    </view>
</template>

<script>
export default {
    name: 'DisclaimerCard'
}
</script>

<style lang="scss" scoped>
// 免责声明样式
.disclaimer-card {
    margin: 0 30rpx 15rpx;
    padding: 30rpx;
    background: linear-gradient(135deg, rgba(255, 107, 53, 0.05), rgba(255, 107, 53, 0.08));
    border: 1rpx solid rgba(255, 107, 53, 0.2);
    border-left: 6rpx solid #ff6b35;
}

.disclaimer-header {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-bottom: 20rpx;
}

.disclaimer-icon {
    width: 40rpx;
    height: 40rpx;
    display: flex;
    align-items: center;
    justify-content: center;
}

.disclaimer-title {
    font-size: 28rpx;
    font-weight: 700;
    color: #ff6b35;
}

.disclaimer-content {
    padding-left: 56rpx;
}

.disclaimer-text {
    font-size: 24rpx;
    color: #495057;
    line-height: 1.6;
    word-break: break-word;
}

// 响应式适配
@media (max-width: 600rpx) {
    .disclaimer-card {
        margin: 0 15rpx 12rpx;
        padding: 24rpx;
    }

    .disclaimer-content {
        padding-left: 0;
        margin-top: 16rpx;
    }

    .disclaimer-text {
        font-size: 22rpx;
    }
}
</style>
