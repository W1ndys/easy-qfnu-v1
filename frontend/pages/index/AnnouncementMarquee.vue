<template>
    <view class="announcement-marquee" @click="handleMarqueeClick">
        <view class="marquee-content">
            <text class="marquee-text">
                📢 该程序正在测试阶段，功能可能不稳定 | 加入QQ群获取最新消息：1053432087 |
                开发策划交流群：1057327742 | 欢迎提出建议和意见
            </text>
        </view>
    </view>

</template>

<script setup>
const copyQQGroup = () => {
    uni.setClipboardData({
        data: "1053432087",
        success() {
            uni.showToast({ title: "QQ群号已复制到剪贴板，请自行搜索加群", icon: "success" });
        },
    });
};

const copyDevQQGroup = () => {
    uni.setClipboardData({
        data: "1057327742",
        success() {
            uni.showToast({
                title: "开发交流群号已复制到剪贴板，请自行搜索加群",
                icon: "success",
            });
        },
    });
};

const handleMarqueeClick = () => {
    uni.showActionSheet({
        itemList: ["复制用户群号 1053432087", "复制开发群号 1057327742"],
        success: (res) => {
            if (res.tapIndex === 0) {
                copyQQGroup();
            } else if (res.tapIndex === 1) {
                copyDevQQGroup();
            }
        },
    });
};
</script>

<style lang="scss" scoped>
.announcement-marquee {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 80rpx;
    background: rgba(247, 248, 250, 0.95);
    backdrop-filter: blur(10rpx);
    border-bottom: 1rpx solid rgba(127, 69, 21, 0.1);
    z-index: 999;
    overflow: hidden;
    display: flex;
    align-items: center;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.marquee-content {
    white-space: nowrap;
    animation: marquee 20s linear infinite;
    cursor: pointer;
    line-height: 80rpx;
    height: 80rpx;
    display: flex;
    align-items: center;

    &:hover {
        animation-play-state: paused;
    }
}

.marquee-text {
    font-size: 24rpx;
    color: #7f4515;
    font-weight: 500;
    letter-spacing: 0.5rpx;
    padding: 0 40rpx;
    white-space: nowrap;
    display: inline-block;
}

@keyframes marquee {
    0% {
        transform: translateX(100vw);
    }

    100% {
        transform: translateX(-100%);
    }
}

@media (max-height: 600px) {
    .announcement-marquee {
        height: 60rpx;
    }

    .marquee-content {
        line-height: 60rpx;
        height: 60rpx;
    }

    .marquee-text {
        font-size: 20rpx;
        padding: 0 30rpx;
    }
}
</style>
