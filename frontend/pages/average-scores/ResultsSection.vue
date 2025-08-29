<template>
    <view class="results-section" v-if="hasResults">
        <view class="results-header">
            <view class="results-info">
                <text class="results-title">查询结果</text>
                <text class="results-count">
                    共找到 {{ Object.keys(resultData).length }} 门课程
                </text>
            </view>
        </view>

        <CourseCard v-for="(teachers, courseName) in resultData" :key="courseName" :course-name="courseName"
            :teachers="teachers" />
    </view>
</template>

<script setup>
import { computed } from "vue";
import CourseCard from './CourseCard.vue';

const props = defineProps({
    resultData: {
        type: Object,
        default: () => ({})
    }
});

const hasResults = computed(() => Object.keys(props.resultData).length > 0);
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

// 结果区域
.results-header {
    padding: 20rpx 30rpx;
    text-align: center;
    margin-bottom: 20rpx;
}

.results-info {
    display: flex;
    flex-direction: column;
    gap: 6rpx;
}

.results-title {
    font-size: 28rpx;
    font-weight: 600;
    color: var(--text-primary);
}

.results-count {
    font-size: 22rpx;
    color: var(--text-secondary);
}
</style>
