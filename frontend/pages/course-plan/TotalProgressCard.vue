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
import { formatNumber } from './utils.js';
import ModernCard from "../../components/ModernCard/ModernCard.vue";

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
@import './TotalProgressCard.scss';
</style>
