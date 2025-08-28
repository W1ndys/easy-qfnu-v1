<template>
    <view v-if="course" class="course-card" :class="courseStatus" :style="cardStyle" @click="handleCardClick">
        <!-- 课程头部 -->
        <view class="course-header">
            <view class="course-title">{{ course.name }}</view>
            <view class="course-meta">
                <view class="time-info">
                    <uni-icons type="clock" size="16" color="rgba(127,69,21,0.7)" />
                    <text>{{ timeDisplay }}</text>
                </view>
                <view class="course-type-tag" :style="getTypeTagStyle(course.course_type)">
                    {{ course.course_type }}
                </view>
            </view>
        </view>

        <!-- 课程详情 -->
        <view class="course-body">
            <view class="course-details">
                <!-- 地点信息 -->
                <view class="detail-row">
                    <view class="detail-icon">
                        <uni-icons type="location" size="16" color="#6c757d" />
                    </view>
                    <text class="detail-text location">{{ formatLocation(course.location) }}</text>
                </view>

                <!-- 班级信息 -->
                <view v-if="course.class_name" class="detail-row">
                    <view class="detail-icon">
                        <uni-icons type="home" size="16" color="#495057" />
                    </view>
                    <text class="detail-text class-name">{{ formatClassName(course.class_name) }}</text>
                </view>
            </view>

            <!-- 学分信息 -->
            <view v-if="course.credits" class="credits-info">
                <view class="credits-label">
                    <uni-icons type="star" size="14" color="#6c757d" />
                    <text>学分</text>
                </view>
                <text class="credits-value">{{ course.credits }}</text>
            </view>
        </view>
    </view>

    <!-- 空状态卡片 -->
    <view v-else class="empty-course-card">
        <view class="empty-icon">
            <uni-icons type="calendar" size="32" color="#adb5bd" />
        </view>
        <view class="empty-title">暂无课程</view>
        <view class="empty-desc">今天没有安排课程，好好休息吧！</view>
    </view>
</template>

<script setup>
import { computed } from 'vue';
import { useCourseCard } from './CourseCard.js';

// Props
const props = defineProps({
    course: {
        type: Object,
        default: null
    },
    currentTime: {
        type: String,
        default: ''
    }
});

// Emits
const emit = defineEmits(['click']);

// 使用课程卡片逻辑
const {
    timeDisplay,
    cardStyle,
    getTypeTagStyle,
    formatClassName,
    formatLocation
} = useCourseCard(props);

// 计算课程状态
const courseStatus = computed(() => {
    if (!props.course?.time_info || !props.currentTime) return '';

    const { start_time, end_time } = props.course.time_info;
    const current = props.currentTime;

    if (current >= start_time && current <= end_time) {
        return 'current'; // 正在进行
    } else if (current < start_time) {
        // 判断是否即将开始（30分钟内）
        const startTimeMinutes = timeToMinutes(start_time);
        const currentTimeMinutes = timeToMinutes(current);
        if (startTimeMinutes - currentTimeMinutes <= 30 && startTimeMinutes - currentTimeMinutes > 0) {
            return 'upcoming'; // 即将开始
        }
    } else if (current > end_time) {
        return 'finished'; // 已结束
    }

    return '';
});

// 时间转换为分钟数
const timeToMinutes = (timeStr) => {
    const [hours, minutes] = timeStr.split(':').map(Number);
    return hours * 60 + minutes;
};

// 处理卡片点击
const handleCardClick = () => {
    if (props.course) {
        emit('click', props.course);
    }
};
</script>

<style lang="scss" scoped>
@import "./CourseCard.scss";
</style>
