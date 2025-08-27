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
import CourseListScript from './CourseList.js'
export default CourseListScript
</script>

<style lang="scss" scoped>
@import './CourseList.scss';
</style>
