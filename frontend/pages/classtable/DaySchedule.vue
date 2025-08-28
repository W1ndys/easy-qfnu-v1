<template>
    <view class="day-schedule">
        <!-- 日程头部 -->
        <view class="schedule-header">
            <view class="schedule-title">
                {{ dayInfo?.formatDate?.full || '课程表' }}
                <text v-if="isToday" class="today-badge">今日</text>
            </view>
            <view class="schedule-stats">
                <view class="stat-item">
                    <uni-icons type="calendar-filled" size="16" color="rgba(255,255,255,0.9)" />
                    <text><span class="stat-value">{{ dayStats.totalCourses }}</span> 节课</text>
                </view>
                <view class="stat-item">
                    <uni-icons type="clock-filled" size="16" color="rgba(255,255,255,0.9)" />
                    <text><span class="stat-value">{{ dayStats.totalHours }}</span> 学时</text>
                </view>
                <view v-if="isToday && currentTime" class="stat-item">
                    <uni-icons type="pulse" size="16" color="rgba(255,255,255,0.9)" />
                    <text>{{ currentTime }}</text>
                </view>
            </view>
        </view>

        <!-- 当前课程指示器 -->
        <view v-if="dayStats.currentCourse" class="current-course-indicator">
            <view class="indicator-icon">
                <uni-icons type="play-filled" size="16" color="#ffffff" />
            </view>
            <view class="indicator-text">
                正在进行：{{ dayStats.currentCourse.name }}
            </view>
            <view class="indicator-time">
                {{ dayStats.currentCourse.time_info?.end_time }} 结束
            </view>
        </view>

        <!-- 下节课程指示器 -->
        <view v-else-if="dayStats.nextCourse && isToday" class="next-course-indicator">
            <view class="indicator-icon">
                <uni-icons type="forward" size="16" color="#212529" />
            </view>
            <view class="indicator-text">
                下节课：{{ dayStats.nextCourse.name }}
            </view>
            <view class="indicator-time">
                {{ dayStats.nextCourse.time_info?.start_time }} 开始
            </view>
        </view>

        <!-- 课程列表 -->
        <view class="courses-container">
            <!-- 有课程时显示课程列表 -->
            <view v-if="dayCourses.length > 0" class="courses-list">
                <template v-for="(course, index) in dayCourses" :key="course.id">
                    <!-- 时间段分隔符 -->
                    <view v-if="shouldShowDivider(course, index)" class="time-slot-divider">
                        <view class="divider-line"></view>
                        <view class="divider-label">
                            {{ course.time_info?.period_name }}
                        </view>
                        <view class="divider-line"></view>
                    </view>

                    <!-- 课程卡片 -->
                    <CourseCard :course="course" :current-time="currentTime" @click="handleCourseClick" />
                </template>

                <!-- 空闲时间提示 -->
                <view v-if="freeTimeSlots.length > 0 && isToday" class="free-time-notice">
                    <view class="notice-icon">
                        <uni-icons type="cup" size="20" color="#ffffff" />
                    </view>
                    <view class="notice-content">
                        <view class="notice-title">空闲时间</view>
                        <view class="notice-desc">
                            今天还有 {{ freeTimeSlots.length }} 个时间段空闲，可以好好休息一下
                        </view>
                    </view>
                </view>
            </view>

            <!-- 无课程时显示空状态 -->
            <view v-else class="empty-schedule">
                <view class="empty-icon">
                    <uni-icons type="calendar" size="48" color="#adb5bd" />
                </view>
                <view class="empty-title">{{ isToday ? '今天' : '当天' }}没有安排课程</view>
                <view class="empty-desc">
                    {{ isToday ? '好好享受这个美好的休息日吧！' : '这天是个自由安排的日子' }}
                </view>

                <view v-if="isToday" class="empty-suggestions">
                    <view class="suggestion-item">
                        <uni-icons type="star" size="14" color="#868e96" />
                        <text>可以复习之前的课程内容</text>
                    </view>
                    <view class="suggestion-item">
                        <uni-icons type="heart" size="14" color="#868e96" />
                        <text>也可以预习明天的课程</text>
                    </view>
                    <view class="suggestion-item">
                        <uni-icons type="smile" size="14" color="#868e96" />
                        <text>或者好好放松休息</text>
                    </view>
                </view>
            </view>
        </view>

        <!-- 加载状态 -->
        <view v-if="loading" class="schedule-loading">
            <view class="loading-spinner"></view>
            <text class="loading-text">正在加载课程数据...</text>
        </view>
    </view>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useDaySchedule } from './DaySchedule.js';
import CourseCard from './CourseCard.vue';

// Props
const props = defineProps({
    selectedDate: {
        type: String,
        required: true
    },
    courses: {
        type: Array,
        default: () => []
    },
    timeSlots: {
        type: Array,
        default: () => []
    },
    loading: {
        type: Boolean,
        default: false
    }
});

// Emits
const emit = defineEmits(['course-click']);

// 使用日程逻辑
const {
    currentTime,
    dayInfo,
    dayCourses,
    dayStats,
    isToday,
    timeSlots,
    freeTimeSlots,
    initTimeUpdate
} = useDaySchedule(props);

// 定时器引用
let timeTimer = null;

// 生命周期
onMounted(() => {
    timeTimer = initTimeUpdate();
});

onUnmounted(() => {
    if (timeTimer) {
        clearInterval(timeTimer);
    }
});

// 判断是否需要显示时间段分隔符
const shouldShowDivider = (course, index) => {
    if (index === 0) return true;

    const prevCourse = dayCourses.value[index - 1];
    if (!prevCourse || !course.time_info || !prevCourse.time_info) return false;

    return course.time_info.period !== prevCourse.time_info.period;
};

// 处理课程点击
const handleCourseClick = (course) => {
    emit('course-click', {
        course,
        dayInfo: dayInfo.value,
        isToday: isToday.value
    });
};
</script>

<style lang="scss" scoped>
@import "./DaySchedule.scss";
</style>
