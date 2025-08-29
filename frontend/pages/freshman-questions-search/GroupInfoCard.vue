<template>
    <view class="group-info-card modern-card">
        <view class="group-header">
            <view class="group-icon">
                <uni-icons type="chat-filled" size="24" color="#1890ff"></uni-icons>
            </view>
            <text class="group-title">学习交流群</text>
        </view>
        <view class="group-content">
            <text class="group-description">曲师大25级选课学习交流群</text>
            <view class="group-number" @click="copyGroupNumber">
                <text class="group-label">群号：</text>
                <text class="group-id">1046961227</text>
                <view class="copy-icon">
                    <uni-icons type="copy" size="16" color="#1890ff"></uni-icons>
                </view>
            </view>
            <text class="group-hint">点击群号可复制</text>
        </view>
    </view>
</template>

<script>
export default {
    name: 'GroupInfoCard',
    methods: {
        copyGroupNumber() {
            uni.setClipboardData({
                data: '1046961227',
                success: () => {
                    uni.showToast({
                        title: '群号已复制',
                        icon: 'success',
                        duration: 2000
                    });
                },
                fail: () => {
                    uni.showToast({
                        title: '复制失败',
                        icon: 'none',
                        duration: 2000
                    });
                }
            });
        }
    }
}
</script>

<style lang="scss" scoped>
// 交流群信息样式
.group-info-card {
    margin: 0 30rpx 15rpx;
    padding: 30rpx;
    background: linear-gradient(135deg, rgba(24, 144, 255, 0.05), rgba(24, 144, 255, 0.08));
    border: 1rpx solid rgba(24, 144, 255, 0.2);
    border-left: 6rpx solid #1890ff;
}

.group-header {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-bottom: 20rpx;
}

.group-icon {
    width: 40rpx;
    height: 40rpx;
    display: flex;
    align-items: center;
    justify-content: center;
}

.group-title {
    font-size: 28rpx;
    font-weight: 700;
    color: #1890ff;
}

.group-content {
    padding-left: 56rpx;
}

.group-description {
    display: block;
    font-size: 26rpx;
    color: #495057;
    line-height: 1.6;
    margin-bottom: 16rpx;
}

.group-number {
    display: flex;
    align-items: center;
    gap: 8rpx;
    padding: 12rpx 16rpx;
    background: rgba(24, 144, 255, 0.1);
    border-radius: 8rpx;
    margin-bottom: 12rpx;
    cursor: pointer;
    transition: all 0.3s ease;

    &:active {
        transform: scale(0.98);
        background: rgba(24, 144, 255, 0.15);
    }
}

.group-label {
    font-size: 24rpx;
    color: #495057;
    font-weight: 500;
}

.group-id {
    font-size: 26rpx;
    color: #1890ff;
    font-weight: 700;
    letter-spacing: 1rpx;
    flex: 1;
}

.copy-icon {
    width: 24rpx;
    height: 24rpx;
    display: flex;
    align-items: center;
    justify-content: center;
}

.group-hint {
    font-size: 22rpx;
    color: #8c8c8c;
    font-style: italic;
}

// 响应式适配
@media (max-width: 600rpx) {
    .group-info-card {
        margin: 0 15rpx 12rpx;
        padding: 24rpx;
    }

    .group-content {
        padding-left: 0;
        margin-top: 16rpx;
    }

    .group-description {
        font-size: 24rpx;
    }

    .group-number {
        padding: 10rpx 14rpx;
    }

    .group-label {
        font-size: 22rpx;
    }

    .group-id {
        font-size: 24rpx;
    }

    .group-hint {
        font-size: 20rpx;
    }
}
</style>
