<template>
    <view class="logo-section">
        <image class="logo" src="https://pic1.zhimg.com/80/v2-82c1c70c69720aadac79594ea50ed4a7.png" mode="aspectFit">
        </image>
        <view class="app-title">曲奇教务</view>
        <view class="app-subtitle">让你的QFNU更简单</view>

        <!-- 新生搜索小入口 -->
        <view class="freshman-entry" @click="goToFreshmanSearch">
            <uni-icons type="help" size="14" color="#7f4515"></uni-icons>
            <text class="entry-text">新生入学考试辅助</text>
            <uni-icons type="arrowright" size="12" color="#7f4515"></uni-icons>
        </view>
    </view>
</template>

<script setup>
// 跳转到新生搜索页面
const goToFreshmanSearch = () => {
    uni.navigateTo({
        url: "/pages/freshman-questions-search/freshman-questions-search",
    });
};
</script>

<style lang="scss" scoped>
.logo-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 50rpx;
}

.logo {
    width: 120rpx;
    height: 120rpx;
    margin-bottom: 30rpx;
    border-radius: 24rpx;
    box-shadow: 0 8rpx 24rpx rgba(127, 69, 21, 0.15);
}

.app-title {
    font-size: 48rpx;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 16rpx;
    letter-spacing: 2rpx;
}

.app-subtitle {
    font-size: 28rpx;
    color: #7f8c8d;
    font-weight: 400;
    margin-bottom: 20rpx;
}

// 新生搜索小入口样式
.freshman-entry {
    display: flex;
    align-items: center;
    gap: 8rpx;
    padding: 12rpx 20rpx;
    background: rgba(127, 69, 21, 0.08);
    border-radius: 20rpx;
    border: 1rpx solid rgba(127, 69, 21, 0.15);
    transition: all 0.3s ease;
    cursor: pointer;

    &:active {
        background: rgba(127, 69, 21, 0.15);
        transform: scale(0.95);
    }
}

.entry-text {
    font-size: 22rpx;
    color: #7f4515;
    font-weight: 500;
}

// 响应式适配
@media (max-height: 600px) {
    .logo-section {
        margin-bottom: 30rpx;
    }

    .logo {
        width: 100rpx;
        height: 100rpx;
    }

    .app-title {
        font-size: 40rpx;
    }
}
</style>
