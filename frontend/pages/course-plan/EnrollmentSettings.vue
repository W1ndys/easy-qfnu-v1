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
@import './EnrollmentSettings.scss';
</style>
