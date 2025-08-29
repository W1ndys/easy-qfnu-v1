<template>
    <!-- 空状态 -->
    <view class="empty-state modern-card" v-if="type === 'empty'">
        <view class="empty-content">
            <view class="empty-icon">
                <uni-icons type="info" size="80" color="#adb5bd"></uni-icons>
            </view>
            <text class="empty-title">未找到相关题目</text>
            <text class="empty-subtitle">{{ emptyMessage }}</text>
            <button class="action-btn primary-btn retry-btn" @click="handleRetry">
                <uni-icons type="refresh" size="20" color="#ffffff"></uni-icons>
                <text>重新搜索</text>
            </button>
        </view>
    </view>

    <!-- 初始状态 -->
    <view class="initial-state modern-card" v-else-if="type === 'initial'">
        <view class="initial-content">
            <view class="initial-icon">
                <uni-icons type="help" size="80" color="#7f4515"></uni-icons>
            </view>
            <text class="initial-title">欢迎使用搜索功能</text>
            <text class="initial-subtitle">输入题目关键词，快速找到相关题目和答案</text>
            <view class="tips-section">
                <view class="tip-item">
                    <uni-icons type="checkmarkempty" size="16" color="#52c41a"></uni-icons>
                    <text class="tip-text">支持关键词搜索</text>
                </view>
                <view class="tip-item">
                    <uni-icons type="checkmarkempty" size="16" color="#52c41a"></uni-icons>
                    <text class="tip-text">智能语义匹配</text>
                </view>
                <view class="tip-item">
                    <uni-icons type="checkmarkempty" size="16" color="#52c41a"></uni-icons>
                    <text class="tip-text">精准答案推荐</text>
                </view>
            </view>
        </view>
    </view>

    <!-- 加载状态 -->
    <view class="loading-state modern-card" v-else-if="type === 'loading'">
        <view class="loading-content">
            <view class="loading-spinner">
                <uni-icons type="spinner-cycle" size="60" color="#7f4515"></uni-icons>
            </view>
            <text class="loading-text">正在搜索题目...</text>
            <text class="loading-subtitle">使用AI语义分析匹配相关内容</text>
        </view>
    </view>
</template>

<script>
export default {
    name: 'StateCards',
    props: {
        type: {
            type: String,
            required: true,
            validator: (value) => ['empty', 'initial', 'loading'].includes(value)
        },
        emptyMessage: {
            type: String,
            default: '未找到相关题目，请尝试其他关键词'
        }
    },
    methods: {
        handleRetry() {
            this.$emit('retry');
        }
    }
}
</script>

<style lang="scss" scoped>
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
    color: #2c3e50;
}

.empty-subtitle,
.initial-subtitle,
.loading-subtitle {
    font-size: 24rpx;
    color: #6c757d;
    text-align: center;
    line-height: 1.5;
}

.retry-btn {
    width: 200rpx;
    margin-top: 20rpx;
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
    background: linear-gradient(135deg, #7f4515, #8c5527);
    color: #ffffff;
    box-shadow: 0 8rpx 24rpx rgba(127, 69, 21, 0.25);

    &::after {
        border: none;
    }

    &:active {
        transform: scale(0.95);
        box-shadow: 0 4rpx 12rpx rgba(127, 69, 21, 0.4);
    }

    text {
        font-weight: inherit;
    }
}

// 提示区域
.tips-section {
    display: flex;
    flex-direction: column;
    gap: 16rpx;
    margin-top: 30rpx;
}

.tip-item {
    display: flex;
    align-items: center;
    gap: 12rpx;
    padding: 12rpx 20rpx;
    background: rgba(127, 69, 21, 0.05);
    border-radius: 12rpx;
    border: 1rpx solid rgba(127, 69, 21, 0.1);
}

.tip-text {
    font-size: 24rpx;
    color: #6c757d;
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
