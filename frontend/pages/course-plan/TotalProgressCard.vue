<template>
    <ModernCard title="总学分进度" class="total-progress-card">
        <view class="total-progress-container">
            <view class="total-header">
                <view class="total-title-section">
                    <text class="total-title">培养方案总进度</text>
                    <view class="status-chip"
                        :class="isTotalIncomplete ? 'chip-module-incomplete' : 'chip-module-complete'">
                        <text>{{ isTotalIncomplete ? "未修满" : "已修满" }}</text>
                    </view>
                </view>

                <view class="total-credits-info">
                    <text class="total-credits-text">{{ formatNumber(totalCompletedCredits) }}/{{
                        formatNumber(totalRequiredCredits)
                    }}
                        学分</text>
                    <text v-if="isTotalIncomplete" class="total-shortage-text">差
                        {{ formatNumber(totalRequiredCredits - totalCompletedCredits) }}
                        学分</text>
                </view>

                <view class="total-progress-bar-container">
                    <view class="progress-bar total-progress-bar">
                        <view class="progress-fill" :style="{ width: totalProgress + '%' }"
                            :class="{ danger: isTotalIncomplete }"></view>
                    </view>
                    <text class="progress-text total-progress-text">{{ totalProgress }}%</text>
                </view>
            </view>
        </view>
    </ModernCard>
</template>

<script setup>
import { computed } from 'vue';
import ModernCard from "../../components/ModernCard/ModernCard.vue";

// 格式化数字
const formatNumber = (n) => {
    const v = Number(n);
    if (isNaN(v)) return "0";
    return v % 1 === 0 ? String(v) : v.toFixed(1);
};

const props = defineProps({
    modules: {
        type: Array,
        default: () => []
    }
});

const totalRequiredCredits = computed(() =>
    props.modules.reduce((sum, m) => sum + (Number(m.required_credits) || 0), 0)
);

const totalCompletedCredits = computed(() =>
    props.modules.reduce((sum, m) => sum + (Number(m.completed_credits) || 0), 0)
);

const totalProgress = computed(() => {
    if (totalRequiredCredits.value <= 0) return 0;
    return Math.min(
        100,
        Math.max(
            0,
            Math.round((totalCompletedCredits.value / totalRequiredCredits.value) * 100)
        )
    );
});

const isTotalIncomplete = computed(
    () => totalCompletedCredits.value < totalRequiredCredits.value
);
</script>

<style lang="scss" scoped>
.total-progress-card {
    margin-bottom: 12rpx;
}

.total-progress-container {
    padding: 0;
}

.total-header {
    display: flex;
    flex-direction: column;
    gap: 12rpx;
}

.total-title-section {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.total-title {
    font-size: 32rpx;
    color: var(--text-primary);
    font-weight: 700;
    line-height: 1.4;
}

.total-credits-info {
    display: flex;
    flex-direction: column;
    gap: 6rpx;
    align-items: center;
}

.total-credits-text {
    font-size: 36rpx;
    color: var(--text-primary);
    font-weight: 600;
    text-align: center;
}

.total-shortage-text {
    font-size: 28rpx;
    color: #e74c3c;
    font-weight: 600;
    text-align: center;
}

.total-progress-bar-container {
    display: flex;
    align-items: center;
    gap: 16rpx;
}

.total-progress-bar {
    height: 24rpx;
    border-radius: 12rpx;
    box-shadow: inset 0 2rpx 6rpx rgba(0, 0, 0, 0.12);
}

.total-progress-text {
    font-size: 28rpx;
    color: var(--text-primary);
    font-weight: 600;
    min-width: 70rpx;
    text-align: right;
}

.progress-bar {
    flex: 1;
    height: 20rpx;
    background: #f5f5f5;
    border-radius: 10rpx;
    overflow: hidden;
    box-shadow: inset 0 2rpx 4rpx rgba(0, 0, 0, 0.1);
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #52c41a 0%, #73d13d 100%);
    border-radius: 10rpx;
    transition: width 0.6s ease;
}

.progress-fill.danger {
    background: linear-gradient(90deg, #ff4d4f 0%, #ff7875 100%);
}

.status-chip {
    padding: 6rpx 12rpx;
    border-radius: 16rpx;
    font-size: 22rpx;
    font-weight: 500;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.chip-module-complete {
    background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
    color: #389e0d;
    border: 1rpx solid #95de64;
}

.chip-module-incomplete {
    background: linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%);
    color: #cf1322;
    border: 1rpx solid #ff7875;
}
</style>
