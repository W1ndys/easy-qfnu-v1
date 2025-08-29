<template>
    <ModernCard title="学籍设置" class="settings-card">
        <view class="enrollment-notice">
            <uni-icons type="info" size="16" color="#1890ff" />
            <text class="notice-text">入伍、留级等学生请选择你所在班级的入学年份</text>
        </view>
        <view class="setting-item">
            <text class="setting-label">入学年份:</text>
            <picker mode="selector" :range="enrollmentYearRange" :value="enrollmentYearIndex"
                @change="handleYearChange">
                <view class="picker-value">
                    <text>{{ enrollmentYear || "请选择" }}</text>
                    <uni-icons type="bottom" size="16" color="#666" />
                </view>
            </picker>
        </view>
        <view class="setting-item">
            <text class="setting-label">当前学期:</text>
            <text class="setting-value">{{
                currentSemester ? `第 ${currentSemester} 学期` : "请先选择入学年份"
            }}</text>
        </view>
    </ModernCard>
</template>

<script setup>
import { computed } from 'vue';
import ModernCard from "../../components/ModernCard/ModernCard.vue";

const props = defineProps({
    enrollmentYear: {
        type: [String, Number],
        default: null
    },
    currentSemester: {
        type: [String, Number],
        default: null
    }
});

const emit = defineEmits(['year-change']);

const enrollmentYearRange = computed(() => {
    const currentYear = new Date().getFullYear();
    return Array.from({ length: 5 }, (_, i) => String(currentYear - i));
});

const enrollmentYearIndex = computed(() => {
    return enrollmentYearRange.value.indexOf(String(props.enrollmentYear));
});

const handleYearChange = (e) => {
    const newYear = enrollmentYearRange.value[e.detail.value];
    emit('year-change', newYear);
};
</script>

<style lang="scss" scoped>
.settings-card {
    margin-bottom: 12rpx;
}

.enrollment-notice {
    display: flex;
    align-items: center;
    gap: 8rpx;
    margin-bottom: 16rpx;
    padding: 8rpx 12rpx;
    background: linear-gradient(135deg, #e6f7ff 0%, #f0f8ff 100%);
    border-radius: 8rpx;
    border: 1rpx solid #91d5ff;
}

.notice-text {
    font-size: 24rpx;
    color: #1890ff;
    line-height: 1.4;
}

.setting-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8rpx 0;
    font-size: 26rpx;
}

.setting-label {
    color: var(--text-secondary);
    font-weight: 500;
}

.picker-value {
    display: flex;
    align-items: center;
    gap: 8rpx;
    padding: 6rpx 12rpx;
    border: 1rpx solid #d9d9d9;
    border-radius: 8rpx;
    background-color: #fafafa;
    color: var(--text-primary);
    min-width: 120rpx;
    justify-content: space-between;
}

.setting-value {
    color: var(--text-primary);
    font-weight: 600;
}
</style>
