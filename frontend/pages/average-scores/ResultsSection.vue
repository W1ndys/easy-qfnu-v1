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

<script src="./ResultsSection.js"></script>
<style lang="scss" scoped>
@import "./ResultsSection.scss";
</style>
