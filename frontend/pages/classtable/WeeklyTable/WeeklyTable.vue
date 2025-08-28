<template>
    <ModernCard title="📚 本周课程表">
        <view class="weekly-table-container">
            <!-- 课程表头部 -->
            <view class="table-header">
                <view class="time-column-header">时间</view>
                <view class="weekday-headers">
                    <view v-for="weekday in weekdays" :key="weekday.id" class="weekday-header"
                        :class="{ 'today': isToday(weekday.id) }">
                        <text class="weekday-name">{{ weekday.short }}</text>
                        <text class="weekday-date">{{ getWeekdayDate(weekday.id) }}</text>
                    </view>
                </view>
            </view>

            <!-- 课程表主体 -->
            <view class="table-body">
                <view v-for="timeSlot in timeSlots" :key="timeSlot.period" class="time-row">
                    <!-- 时间列 -->
                    <view class="time-column">
                        <text class="period-name">{{ timeSlot.name }}</text>
                        <text class="time-range">{{ timeSlot.time }}</text>
                    </view>

                    <!-- 课程列 -->
                    <view class="course-columns">
                        <view v-for="weekday in weekdays" :key="`${timeSlot.period}-${weekday.id}`" class="course-cell"
                            :class="{ 'today': isToday(weekday.id) }">
                            <CourseCard v-for="course in getCoursesForSlot(timeSlot.period, weekday.id)"
                                :key="course.id" :course="course" @course-click="handleCourseClick" />
                        </view>
                    </view>
                </view>
            </view>

            <!-- 空状态 -->
            <view v-if="!hasCourses" class="empty-table">
                <uni-icons type="calendar" size="48" color="#ccc" />
                <text class="empty-text">本周暂无课程安排</text>
            </view>
        </view>
    </ModernCard>
</template>

<script>
export default {
    name: 'WeeklyTable'
};
</script>

<script setup>
import { computed } from 'vue';
import { getCurrentDate, getWeekDates, isToday as checkIsToday } from '../utils/dateUtils.js';
import ModernCard from '../../../components/ModernCard/ModernCard.vue';
import CourseCard from '../CourseCard/CourseCard.vue';

const props = defineProps({
    timeSlots: {
        type: Array,
        required: true,
        default: () => []
    },
    weekdays: {
        type: Array,
        required: true,
        default: () => []
    },
    courses: {
        type: Array,
        required: true,
        default: () => []
    },
    currentDate: {
        type: String,
        default: () => getCurrentDate()
    }
});

const emit = defineEmits(['course-click']);

// 计算属性
const hasCourses = computed(() => {
    return props.courses.length > 0;
});

const weekDates = computed(() => {
    return getWeekDates(props.currentDate);
});

// 方法
function isToday(weekdayId) {
    const today = new Date();
    const todayWeekday = today.getDay() === 0 ? 7 : today.getDay(); // 转换为1-7格式
    return weekdayId === todayWeekday && checkIsToday(props.currentDate);
}

function getWeekdayDate(weekdayId) {
    if (!weekDates.value || weekDates.value.length === 0) return '';

    // weekdayId: 1=周一, 7=周日
    const dateIndex = weekdayId - 1;
    if (dateIndex < 0 || dateIndex >= weekDates.value.length) return '';

    const date = new Date(weekDates.value[dateIndex]);
    return `${date.getMonth() + 1}/${date.getDate()}`;
}

function getCoursesForSlot(period, weekdayId) {
    return props.courses.filter(course => {
        return course.time_info.period === period &&
            course.time_info.weekday === weekdayId;
    });
}

function handleCourseClick(course) {
    emit('course-click', course);
}</script>

<style lang="scss" scoped>
@import './WeeklyTable.scss';
</style>
