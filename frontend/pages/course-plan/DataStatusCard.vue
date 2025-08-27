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
import { formatUpdateTime } from './utils.js';
import ModernCard from "../../components/ModernCard/ModernCard.vue";

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
@import './DataStatusCard.scss';
</style>
