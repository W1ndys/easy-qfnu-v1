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
export default {
    name: 'GPAAnalysis',
    props: {
        gpaAnalysis: {
            type: Object,
            default: null
        },
        effectiveGpa: {
            type: Object,
            default: null
        },
        totalCourses: {
            type: Number,
            default: 0
        },
        yearlyGpa: {
            type: Object,
            default: null
        },
        semesterGpa: {
            type: Object,
            default: null
        }
    }
}
</script>

<style lang="scss" scoped>
/* 主题变量 */
$primary-color: #7F4515;
$text-color-primary: #343a40;
$text-color-secondary: #495057;
$text-color-muted: #8c7d70;
$border-color: #f0e9e4;
$background-color-light: #fdfcfa;
$background-color-card: #ffffff;
$border-radius-base: 16rpx;
$border-radius-xs: 8rpx;
$font-size-xxl: 40rpx;
$font-size-xs: 22rpx;
$font-size-xxs: 20rpx;

/* GPA分析模块 */
.analysis-container {
    background-color: $background-color-card;
    border-radius: $border-radius-base;
    padding: 20rpx;
    margin-bottom: 25rpx;
    border: 1rpx solid $border-color;
}

.main-gpa-section {
    display: flex;
    justify-content: space-around;
    text-align: center;
    padding-bottom: 20rpx;
    margin-bottom: 20rpx;
    border-bottom: 1rpx solid $border-color;

    .gpa-item {
        .gpa-value {
            display: block;
            font-size: $font-size-xxl;
            font-weight: bold;
            color: $primary-color;
            line-height: 1.2;
        }

        .gpa-label {
            display: block;
            font-size: $font-size-xs;
            color: $text-color-muted;
            margin-top: 4rpx;
        }
    }
}

.detailed-gpa-section {
    .section-header {
        margin-bottom: 10rpx;

        .section-title {
            font-size: 26rpx;
            font-weight: bold;
            color: $text-color-primary;
        }
    }
}

.details-flex-container {
    display: flex;
    flex-wrap: wrap;
    gap: 15rpx;

    .detail-item-flex {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: $background-color-light;
        padding: 10rpx 15rpx;
        border-radius: $border-radius-xs;
        flex-grow: 1;
        min-width: calc(50% - 15rpx);

        .detail-label {
            font-size: 24rpx;
            color: $text-color-secondary;
            white-space: nowrap;
        }

        .detail-sub-info {
            font-size: $font-size-xxs;
            color: #a09387;
            margin: 0 10rpx;
            white-space: nowrap;
        }

        .detail-value {
            font-size: 26rpx;
            font-weight: bold;
            color: $primary-color;
            flex-shrink: 0;
            margin-left: auto;
        }
    }
}
</style>
