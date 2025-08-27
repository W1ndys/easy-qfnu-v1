<template>
    <view class="course-card modern-card">
        <view class="course-header">
            <view class="course-info">
                <view class="course-icon">
                    <uni-icons type="book" size="20" color="#7f4515"></uni-icons>
                </view>
                <text class="course-name">{{ courseName }}</text>
            </view>
        </view>

        <view class="course-content">
            <view class="teacher-section" v-for="(teacherName, teacherIndex) in Object.keys(teachers)"
                :key="teacherName">
                <view class="teacher-header">
                    <view class="teacher-info">
                        <view class="teacher-avatar">
                            <uni-icons type="person" size="16" color="#7f4515"></uni-icons>
                        </view>
                        <text class="teacher-name">{{ teacherName }}</text>
                    </view>
                </view>

                <view class="semester-list">
                    <view class="semester-item" v-for="(data, semester) in teachers[teacherName]" :key="semester">
                        <view class="semester-info">
                            <text class="semester-name">{{ semester }}</text>
                            <text class="update-time" v-if="data.update_time">
                                {{ formatTime(data.update_time) }}
                            </text>
                        </view>
                        <view class="score-info">
                            <view class="score-item">
                                <text class="score-label">平均分</text>
                                <text class="score-value primary">{{ data.average_score.toFixed(2) }}</text>
                            </view>
                            <view class="score-item">
                                <text class="score-label">人数</text>
                                <text class="score-value secondary">{{ data.student_count }}</text>
                            </view>
                        </view>
                    </view>
                </view>
            </view>
        </view>
    </view>
</template>

<script src="./CourseCard.js"></script>
<style lang="scss" scoped>
@import "./CourseCard.scss";
</style>
