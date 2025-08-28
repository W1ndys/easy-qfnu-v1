<template>
    <ModernCard title="📊 本周统计">
        <view class="stats-container">
            <!-- 总体统计 -->
            <view class="stats-overview">
                <view class="stat-item">
                    <view class="stat-icon">
                        <uni-icons type="calendar-filled" size="24" color="#7f4515" />
                    </view>
                    <view class="stat-content">
                        <text class="stat-value">{{ stats.total_courses }}</text>
                        <text class="stat-label">总课程数</text>
                    </view>
                </view>

                <view class="stat-item">
                    <view class="stat-icon">
                        <uni-icons type="clock-filled" size="24" color="#e74c3c" />
                    </view>
                    <view class="stat-content">
                        <text class="stat-value">{{ stats.total_hours }}</text>
                        <text class="stat-label">总课时</text>
                    </view>
                </view>

                <view class="stat-item">
                    <view class="stat-icon">
                        <uni-icons type="heart-filled" size="24" color="#27ae60" />
                    </view>
                    <view class="stat-content">
                        <text class="stat-value">{{ averageCoursesPerDay }}</text>
                        <text class="stat-label">日均课程</text>
                    </view>
                </view>
            </view>

            <!-- 每日分布 -->
            <view class="daily-distribution" v-if="stats.courses_by_day">
                <text class="section-title">📅 每日课程分布</text>
                <view class="daily-chart">
                    <view v-for="(count, day) in stats.courses_by_day" :key="day" class="daily-bar-container">
                        <view class="day-label">{{ getDayShort(day) }}</view>
                        <view class="bar-wrapper">
                            <view class="daily-bar" :style="{ height: getBarHeight(count) + 'rpx' }"
                                :class="{ 'has-course': count > 0 }"></view>
                        </view>
                        <text class="course-count">{{ count }}</text>
                    </view>
                </view>
            </view>

            <!-- 课程时间分布提示 -->
            <view class="time-tips" v-if="hasCoursesData">
                <text class="tips-title">💡 时间分布提示</text>
                <view class="tips-content">
                    <text class="tip-item" v-if="busyDay">最忙碌：{{ busyDay }}</text>
                    <text class="tip-item" v-if="freeDay">最清闲：{{ freeDay }}</text>
                    <text class="tip-item" v-if="timeAdvice">{{ timeAdvice }}</text>
                </view>
            </view>
        </view>
    </ModernCard>
</template>

<script>
export default {
    name: 'StatsCard'
};
</script>

<script setup>
import { computed } from 'vue';
import ModernCard from '../../../components/ModernCard/ModernCard.vue';

const props = defineProps({
    stats: {
        type: Object,
        required: true,
        default: () => ({
            total_courses: 0,
            total_hours: 0,
            courses_by_day: {}
        })
    }
});

// 计算属性
const averageCoursesPerDay = computed(() => {
    if (!props.stats.total_courses) return 0;
    const totalDays = Object.keys(props.stats.courses_by_day || {}).length;
    return totalDays > 0 ? Math.round(props.stats.total_courses / totalDays * 10) / 10 : 0;
});

const hasCoursesData = computed(() => {
    return props.stats.total_courses > 0;
});

const busyDay = computed(() => {
    if (!props.stats.courses_by_day) return null;
    const entries = Object.entries(props.stats.courses_by_day);
    if (entries.length === 0) return null;

    const maxEntry = entries.reduce((max, current) =>
        current[1] > max[1] ? current : max
    );
    return maxEntry[1] > 0 ? maxEntry[0] : null;
});

const freeDay = computed(() => {
    if (!props.stats.courses_by_day) return null;
    const entries = Object.entries(props.stats.courses_by_day);
    if (entries.length === 0) return null;

    const minEntry = entries.reduce((min, current) =>
        current[1] < min[1] ? current : min
    );
    return minEntry[1] === 0 ? minEntry[0] : null;
});

const timeAdvice = computed(() => {
    if (!hasCoursesData.value) return null;

    const totalCourses = props.stats.total_courses;
    if (totalCourses <= 10) return '课程安排较轻松 😊';
    if (totalCourses <= 20) return '课程安排适中 📚';
    return '课程安排较紧密，注意休息 💪';
});

// 方法
function getDayShort(dayName) {
    const dayMap = {
        '星期一': '一',
        '星期二': '二',
        '星期三': '三',
        '星期四': '四',
        '星期五': '五',
        '星期六': '六',
        '星期日': '日'
    };
    return dayMap[dayName] || dayName;
}

function getBarHeight(count) {
    if (!props.stats.courses_by_day) return 0;
    const maxCount = Math.max(...Object.values(props.stats.courses_by_day));
    if (maxCount === 0) return 0;

    const minHeight = 20;
    const maxHeight = 120;
    return minHeight + (count / maxCount) * (maxHeight - minHeight);
}
</script>

<style lang="scss" scoped>
@import './StatsCard.scss';
</style>
