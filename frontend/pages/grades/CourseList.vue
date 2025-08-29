<template>
    <view class="grades-list-container">
        <view v-for="semester in semesters" :key="semester.semesterName" class="semester-block">
            <view class="semester-header">
                <text class="semester-name">{{ semester.semesterName }}</text>
            </view>
            <view class="courses-list">
                <view v-for="course in semester.grades" :key="course.index" class="course-card" :class="{
                    'is-custom-mode': isCustomMode,
                    'is-selected': isCourseSelected(course.index)
                }">
                    <view class="course-main" @click="$emit('courseClick', course)">
                        <view v-if="isCustomMode" class="course-checkbox-wrapper">
                            <view class="checkbox-inner" :class="{ 'checked': isCourseSelected(course.index) }"></view>
                        </view>

                        <view class="course-core-info">
                            <text class="course-name">{{ course.courseName }}</text>
                            <view class="course-meta">
                                <view class="meta-tag credit">学分: {{ course.credit }}</view>
                                <view class="meta-tag gpa">绩点: {{ course.gpa }}</view>
                                <view v-if="course.courseAttribute" class="meta-tag attribute">{{ course.courseAttribute
                                }}</view>
                            </view>
                        </view>

                        <view class="course-side">
                            <view class="course-score">
                                <text class="score-text" :class="getScoreClass(course.score)">
                                    {{ course.score }}
                                </text>
                                <text v-if="course.scoreTag" class="score-tag">{{ course.scoreTag }}</text>
                            </view>
                            <view class="expand-icon" :class="{ 'expanded': isCourseExpanded(course.index) }">
                                <uni-icons type="down" size="16" color="#868e96"></uni-icons>
                            </view>
                        </view>
                    </view>

                    <transition name="course-details">
                        <view v-show="isCourseExpanded(course.index)" class="course-details">
                            <view class="detail-grid">
                                <view class="detail-item">
                                    <text class="detail-label">课程代码</text>
                                    <text class="detail-value">{{ course.courseCode }}</text>
                                </view>
                                <view class="detail-item">
                                    <text class="detail-label">总学时</text>
                                    <text class="detail-value">{{ course.totalHours }}</text>
                                </view>
                                <view class="detail-item">
                                    <text class="detail-label">课程性质</text>
                                    <text class="detail-value">{{ course.courseNature }}</text>
                                </view>
                                <view class="detail-item">
                                    <text class="detail-label">课程类别</text>
                                    <text class="detail-value">{{ course.courseCategory }}</text>
                                </view>
                                <view class="detail-item">
                                    <text class="detail-label">考核方式</text>
                                    <text class="detail-value">{{ course.assessmentMethod }}</text>
                                </view>
                                <view class="detail-item">
                                    <text class="detail-label">考试类型</text>
                                    <text class="detail-value">{{ course.examType }}</text>
                                </view>
                                <view v-if="course.groupName" class="detail-item">
                                    <text class="detail-label">课程分组</text>
                                    <text class="detail-value">{{ course.groupName }}</text>
                                </view>
                                <view v-if="course.retakeSemester" class="detail-item">
                                    <text class="detail-label">重修学期</text>
                                    <text class="detail-value">{{ course.retakeSemester }}</text>
                                </view>
                            </view>
                        </view>
                    </transition>
                </view>
            </view>
        </view>
    </view>
</template>

<script>
export default {
    name: 'CourseList',
    props: {
        semesters: {
            type: Array,
            default: () => []
        },
        isCustomMode: {
            type: Boolean,
            default: false
        },
        selectedCourses: {
            type: Array,
            default: () => []
        },
        expandedCourses: {
            type: Set,
            default: () => new Set()
        }
    },
    emits: ['courseClick'],
    setup(props, { emit }) {
        const isCourseSelected = (courseIndex) => props.selectedCourses.includes(courseIndex)
        const isCourseExpanded = (courseIndex) => props.expandedCourses.has(courseIndex)

        const getScoreClass = (score) => {
            const numScore = parseFloat(score)
            if (isNaN(numScore)) return 'score-text-grade' // 用于"优秀"、"良好"等文本成绩
            if (numScore >= 90) return 'score-high'
            if (numScore >= 75) return 'score-mid'
            if (numScore >= 60) return 'score-low'
            return 'score-fail'
        }

        return {
            isCourseSelected,
            isCourseExpanded,
            getScoreClass
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
$background-color-card: #ffffff;
$score-high: #28a745;
$score-mid: #17a2b8;
$score-low: #ffc107;
$score-fail: #dc3545;
$border-radius-base: 16rpx;
$font-size-xl: 36rpx;
$font-size-lg: 30rpx;
$font-size-base: 28rpx;
$font-size-sm: 24rpx;
$font-size-xs: 22rpx;
$font-size-xxs: 20rpx;

/* 成绩列表 */
.grades-list-container {
    padding-bottom: 250rpx; // 为悬浮操作栏留出空间
}

.semester-block {
    margin-bottom: 30rpx;
}

.semester-header {
    padding-left: 8rpx;
    margin-bottom: 15rpx;

    .semester-name {
        font-size: $font-size-lg;
        font-weight: bold;
        color: $text-color-secondary;
        border-left: 8rpx solid $primary-color;
        padding-left: 15rpx;
    }
}

.courses-list {
    display: flex;
    flex-direction: column;
    gap: 15rpx;
}

.course-card {
    background-color: $background-color-card;
    border-radius: $border-radius-base;
    border: 1rpx solid $border-color;
    box-shadow: 0 4rpx 12rpx rgba(127, 69, 21, 0.03);
    transition: all 0.2s ease-in-out;
    overflow: hidden;

    &.is-custom-mode.is-selected {
        border-color: $primary-color;
        box-shadow: 0 6rpx 18rpx rgba(127, 69, 21, 0.1);
    }
}

.course-main {
    display: flex;
    align-items: center;
    padding: 20rpx;
    cursor: pointer;
}

.course-checkbox-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 38rpx;
    height: 38rpx;
    margin-right: 20rpx;
    flex-shrink: 0;

    .checkbox-inner {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        border: 2rpx solid #c0b8b1;
        transition: all 0.2s ease;
        position: relative;

        &.checked {
            background-color: $primary-color;
            border-color: $primary-color;

            &::after {
                content: '';
                position: absolute;
                top: 7rpx;
                left: 13rpx;
                width: 8rpx;
                height: 16rpx;
                border: solid white;
                border-width: 0 4rpx 4rpx 0;
                transform: rotate(45deg);
            }
        }
    }
}

.course-core-info {
    flex-grow: 1;
    min-width: 0;

    .course-name {
        font-size: $font-size-base;
        font-weight: bold;
        color: $text-color-primary;
        margin-bottom: 10rpx;
    }

    .course-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 10rpx;

        .meta-tag {
            font-size: $font-size-xxs;
            padding: 2rpx 10rpx;
            border-radius: 6rpx;

            &.credit {
                background-color: #e3f2fd;
                color: #0d47a1;
            }

            &.gpa {
                background-color: #e8f5e9;
                color: #1b5e20;
            }

            &.attribute {
                background-color: #fff3e0;
                color: #e65100;
            }
        }
    }
}

.course-side {
    display: flex;
    align-items: center;
    flex-shrink: 0;
    margin-left: 15rpx;
}

.course-score {
    text-align: right;
    margin-right: 10rpx;

    .score-text {
        font-size: $font-size-xl;
        font-weight: bold;

        &.score-high {
            color: $score-high;
        }

        &.score-mid {
            color: $score-mid;
        }

        &.score-low {
            color: $score-low;
        }

        &.score-fail {
            color: $score-fail;
        }

        &.score-text-grade {
            color: $primary-color;
        }
    }

    .score-tag {
        font-size: $font-size-xxs;
        color: #adb5bd;
    }
}

.expand-icon {
    transition: transform 0.3s ease;

    &.expanded {
        transform: rotate(180deg);
    }
}

.course-details {
    padding: 0 25rpx 25rpx 25rpx;
    background-color: #fffbf7;
    border-top: 1rpx solid $border-color;
    overflow: hidden;

    .detail-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15rpx 25rpx;

        .detail-item {
            animation: fadeInUp 0.4s ease-out;
            animation-fill-mode: both;

            .detail-label {
                display: block;
                font-size: $font-size-xs;
                color: $text-color-muted;
                margin-bottom: 2rpx;
            }

            .detail-value {
                display: block;
                font-size: $font-size-sm;
                color: $text-color-primary;
            }

            // 为不同的item添加延迟，创造层次感
            &:nth-child(1) {
                animation-delay: 0.05s;
            }

            &:nth-child(2) {
                animation-delay: 0.1s;
            }

            &:nth-child(3) {
                animation-delay: 0.15s;
            }

            &:nth-child(4) {
                animation-delay: 0.2s;
            }

            &:nth-child(5) {
                animation-delay: 0.25s;
            }

            &:nth-child(6) {
                animation-delay: 0.3s;
            }

            &:nth-child(7) {
                animation-delay: 0.35s;
            }

            &:nth-child(8) {
                animation-delay: 0.4s;
            }
        }
    }
}

/* 展开收起动画 */
.course-details-enter-active {
    transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
    animation: slideDown 0.35s ease-out;
}

.course-details-leave-active {
    transition: all 0.25s cubic-bezier(0.4, 0, 1, 1);
    animation: slideUp 0.25s ease-in;
}

.course-details-enter-from {
    max-height: 0;
    opacity: 0;
    padding-top: 0;
    padding-bottom: 0;
    transform: translateY(-10rpx);
}

.course-details-leave-to {
    max-height: 0;
    opacity: 0;
    padding-top: 0;
    padding-bottom: 0;
    transform: translateY(-10rpx);
}

@keyframes slideDown {
    0% {
        max-height: 0;
        opacity: 0;
        transform: translateY(-10rpx);
    }

    50% {
        opacity: 0.6;
    }

    100% {
        max-height: 500rpx;
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideUp {
    0% {
        max-height: 500rpx;
        opacity: 1;
        transform: translateY(0);
    }

    50% {
        opacity: 0.6;
    }

    100% {
        max-height: 0;
        opacity: 0;
        transform: translateY(-10rpx);
    }
}

@keyframes fadeInUp {
    0% {
        opacity: 0;
        transform: translateY(20rpx);
    }

    100% {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
