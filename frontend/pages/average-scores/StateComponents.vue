<template>
    <!-- 空状态 -->
    <view class="empty-state modern-card" v-if="type === 'empty'">
        <view class="empty-content">
            <view class="empty-icon">
                <uni-icons type="info" size="80" color="#adb5bd"></uni-icons>
            </view>
            <text class="empty-title">未找到相关数据</text>
            <text class="empty-subtitle">{{ message }}</text>
            <button class="action-btn primary-btn retry-btn" @click="$emit('retry')">
                <uni-icons type="refresh" size="20" color="#ffffff"></uni-icons>
                <text>重新搜索</text>
            </button>
        </view>
    </view>

    <!-- 初始状态 -->
    <view class="initial-state modern-card" v-else-if="type === 'initial'">
        <view class="initial-content">
            <view class="initial-icon">
                <uni-icons type="search" size="80" color="#7f4515"></uni-icons>
            </view>
            <text class="initial-title">欢迎使用平均分查询</text>
            <text class="initial-subtitle">请输入课程信息开始查询学术数据</text>
        </view>
    </view>

    <!-- 加载状态 -->
    <view class="loading-state modern-card" v-else-if="type === 'loading'">
        <view class="loading-content">
            <view class="loading-spinner">
                <uni-icons type="spinner-cycle" size="60" color="#7f4515"></uni-icons>
            </view>
            <text class="loading-text">正在查询数据...</text>
        </view>
    </view>
</template>

<script setup>
defineProps({
    type: {
        type: String,
        required: true,
        validator: (value) => ['empty', 'initial', 'loading'].includes(value)
    },
    message: {
        type: String,
        default: '未找到相关数据'
    }
});

defineEmits(['retry']);
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

// 状态页面样式
.empty-state,
.initial-state,
.loading-state {
    padding: 80rpx 40rpx;
}

.empty-content,
.initial-content,
.loading-content {
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 30rpx;
}

.empty-icon,
.initial-icon,
.loading-spinner {
    opacity: 0.6;
}

.empty-title,
.initial-title,
.loading-text {
    font-size: 32rpx;
    font-weight: 600;
    color: var(--text-primary);
}

.empty-subtitle,
.initial-subtitle {
    font-size: 24rpx;
    color: var(--text-secondary);
    text-align: center;
    line-height: 1.5;
}

.retry-btn {
    width: 200rpx;
    margin-top: 20rpx;
}

.action-btn {
    height: 72rpx;
    border-radius: 9999rpx;
    font-size: 26rpx;
    padding: 16rpx 24rpx;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12rpx;
    transition: all 0.3s ease;
    border: none;

    &::after {
        border: none;
    }

    &:active {
        transform: scale(0.95);
    }

    text {
        font-weight: inherit;
    }
}

.primary-btn {
    background: linear-gradient(135deg, #7f4515, #8c5527);
    color: #ffffff;
    box-shadow: 0 8rpx 24rpx rgba(127, 69, 21, 0.25);

    &:active {
        box-shadow: 0 4rpx 12rpx rgba(155, 4, 0, 0.4);
    }
}

// 加载动画
@keyframes spin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

.loading-spinner {
    animation: spin 1s linear infinite;
}
</style>
