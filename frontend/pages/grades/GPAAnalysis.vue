<template>
    <view v-if="gpaAnalysis" class="analysis-container">
        <view class="main-gpa-section">
            <view class="gpa-item">
                <text class="gpa-value">{{ gpaAnalysis?.weighted_gpa?.toFixed(2) || 'N/A' }}</text>
                <text class="gpa-label">总加权平均GPA</text>
            </view>
            <view class="gpa-item">
                <text class="gpa-value">{{ effectiveGpa?.weighted_gpa?.toFixed(2) || 'N/A' }}</text>
                <text class="gpa-label">有效GPA (去重修)</text>
            </view>
            <view class="gpa-item">
                <text class="gpa-value">{{ totalCourses || 0 }}</text>
                <text class="gpa-label">总课程数</text>
            </view>
        </view>

        <view class="detailed-gpa-section">
            <view class="section-header">
                <text class="section-title">详细GPA分布</text>
            </view>
            <view class="details-flex-container">
                <template v-if="yearlyGpa && Object.keys(yearlyGpa).length > 0">
                    <view v-for="(gpa, year) in yearlyGpa" :key="year" class="detail-item-flex">
                        <text class="detail-label">{{ year }}学年</text>
                        <text class="detail-sub-info">{{ gpa.course_count }}门 / {{ gpa.total_credit.toFixed(1)
                        }}学分</text>
                        <text class="detail-value">{{ gpa.weighted_gpa.toFixed(2) }}</text>
                    </view>
                </template>
                <template v-if="semesterGpa && Object.keys(semesterGpa).length > 0">
                    <view v-for="(gpa, semester) in semesterGpa" :key="semester" class="detail-item-flex">
                        <text class="detail-label">{{ semester }}</text>
                        <text class="detail-sub-info">{{ gpa.course_count }}门 / {{ gpa.total_credit.toFixed(1)
                        }}学分</text>
                        <text class="detail-value">{{ gpa.weighted_gpa.toFixed(2) }}</text>
                    </view>
                </template>
            </view>
        </view>
    </view>
</template>

<script>
import GPAAnalysisScript from './GPAAnalysis.js'
export default GPAAnalysisScript
</script>

<style lang="scss" scoped>
@import './GPAAnalysis.scss';
</style>
