<template>
    <ModernCard title="数据状态" class="data-status-card">
        <view class="data-status-container">
            <view class="status-info">
                <view class="status-row">
                    <view class="status-item">
                        <uni-icons type="cloud" size="20" :color="dataSource === 'live' ? '#52c41a' : '#1890ff'" />
                        <text class="status-label">数据来源:</text>
                        <view class="source-chip" :class="dataSource === 'live' ? 'chip-live' : 'chip-cache'">
                            <view class="source-dot" :class="dataSource === 'live' ? 'dot-live' : 'dot-cache'" />
                            <text>{{ dataSource === "live" ? "实时获取" : "缓存数据" }}</text>
                        </view>
                    </view>

                    <view v-if="updatedAt" class="status-item">
                        <uni-icons type="calendar" size="20" color="#666" />
                        <text class="status-label">更新时间:</text>
                        <view class="updated-chip">
                            <text>{{ formatUpdateTime(updatedAt) }}</text>
                        </view>
                    </view>
                </view>

                <view class="refresh-tip">
                    <uni-icons type="info" size="16" color="#faad14" />
                    <text class="tip-text">如果没有新出成绩，无需刷新</text>
                </view>
            </view>

            <view class="refresh-actions">
                <button class="refresh-btn" :class="{ loading: isRefreshing }" :disabled="isRefreshing"
                    @click="handleRefresh">
                    <uni-icons type="refresh" size="16" color="#1890ff" :class="{ spinning: isRefreshing }" />
                    <text>{{ isRefreshing ? "刷新中..." : "刷新数据" }}</text>
                </button>
            </view>
        </view>
    </ModernCard>
</template>

<script setup>
import ModernCard from "../../components/ModernCard/ModernCard.vue";

// 格式化更新时间
const formatUpdateTime = (timeStr) => {
    if (!timeStr) return "未知";
    try {
        const date = new Date(timeStr);
        const now = new Date();
        const diffMs = now - date;
        const diffDays = Math.floor(diffMs / 86400000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffMinutes = Math.floor(diffMs / 60000);
        if (diffDays > 0) return `${diffDays}天前`;
        if (diffHours > 0) return `${diffHours}小时前`;
        if (diffMinutes > 0) return `${diffMinutes}分钟前`;
        return "刚刚";
    } catch (error) {
        return "未知";
    }
};

const props = defineProps({
    dataSource: {
        type: String,
        default: 'cache'
    },
    updatedAt: {
        type: String,
        default: ''
    },
    isRefreshing: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['refresh']);

const handleRefresh = () => {
    emit('refresh');
};
</script>

<style lang="scss" scoped>
.data-status-card {
    margin-bottom: 12rpx;
}

.data-status-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12rpx;
    flex-wrap: wrap;
}

.status-info {
    display: flex;
    flex-direction: column;
    gap: 8rpx;
    flex: 1;
}

.status-row {
    display: flex;
    align-items: center;
    gap: 12rpx;
    flex-wrap: wrap;
}

.status-item {
    display: flex;
    align-items: center;
    gap: 6rpx;
    flex-wrap: wrap;
}

.status-label {
    font-size: 24rpx;
    color: var(--text-secondary);
    font-weight: 500;
}

.source-chip {
    display: inline-flex;
    align-items: center;
    gap: 6rpx;
    padding: 4rpx 10rpx;
    border-radius: 999rpx;
    font-size: 24rpx;
    font-weight: 600;
}

.chip-live {
    background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
    color: #389e0d;
    border: 1rpx solid #95de64;
}

.chip-cache {
    background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
    color: #1890ff;
    border: 1rpx solid #91d5ff;
}

.source-dot {
    width: 10rpx;
    height: 10rpx;
    border-radius: 50%;
}

.dot-live {
    background: #52c41a;
}

.dot-cache {
    background: #1890ff;
}

.updated-chip {
    padding: 4rpx 10rpx;
    border-radius: 8rpx;
    background: #f5f5f5;
    color: #595959;
}

.refresh-tip {
    display: flex;
    align-items: center;
    gap: 6rpx;
}

.tip-text {
    font-size: 22rpx;
    color: #8c8c8c;
}

.refresh-actions {
    flex-shrink: 0;
}

.refresh-btn {
    display: flex;
    align-items: center;
    gap: 6rpx;
    padding: 6rpx 12rpx;
    background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
    color: #1890ff;
    border: 1rpx solid #91d5ff;
    border-radius: 12rpx;
    font-size: 22rpx;
    font-weight: 500;
    transition: all 0.3s ease;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.08);
}

.refresh-btn:not(.loading):active {
    transform: translateY(2rpx);
    box-shadow: 0 1rpx 4rpx rgba(0, 0, 0, 0.1);
}

.spinning {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}
</style>
