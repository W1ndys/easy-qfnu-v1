<template>
    <view class="course-card" :style="courseStyle" @click="handleClick" @longpress="handleLongPress">
        <!-- 课程名称 -->
        <text class="course-name">{{ course.name }}</text>

        <!-- 课程信息 -->
        <view class="course-info">
            <view class="info-row" v-if="course.teacher">
                <uni-icons type="person" size="12" :color="iconColor" />
                <text class="info-text">{{ course.teacher }}</text>
            </view>

            <view class="info-row" v-if="course.location">
                <uni-icons type="location" size="12" :color="iconColor" />
                <text class="info-text">{{ formatLocation(course.location) }}</text>
            </view>

            <view class="info-row" v-if="course.time_info">
                <uni-icons type="clock" size="12" :color="iconColor" />
                <text class="info-text">{{ course.time_info.start_time }}-{{ course.time_info.end_time }}</text>
            </view>
        </view>

        <!-- 课程类型标签 -->
        <view class="course-badges" v-if="showBadges">
            <text v-if="course.course_type" class="course-badge type-badge"
                :style="{ background: getBadgeColor(course.course_type) }">
                {{ course.course_type }}
            </text>

            <text v-if="course.credits" class="course-badge credits-badge">
                {{ course.credits }}学分
            </text>
        </view>

        <!-- 多周标识 -->
        <view class="week-indicator" v-if="isMultiWeek">
            <text class="week-text">{{ getWeekText() }}</text>
        </view>
    </view>
</template>

<script>
export default {
    name: 'CourseCard'
};
</script>

<script setup>
import { computed } from 'vue';

const props = defineProps({
    course: {
        type: Object,
        required: true
    },
    compact: {
        type: Boolean,
        default: false
    },
    showBadges: {
        type: Boolean,
        default: true
    }
});

const emit = defineEmits(['course-click', 'course-long-press']);

// 计算属性
const courseStyle = computed(() => {
    const baseStyle = {
        backgroundColor: props.course.style?.color || '#3498db',
        borderLeft: `4rpx solid ${props.course.style?.color || '#3498db'}`,
    };

    // 根据紧凑模式调整样式
    if (props.compact) {
        baseStyle.padding = '8rpx';
        baseStyle.minHeight = '60rpx';
    }

    return baseStyle;
});

const iconColor = computed(() => {
    // 根据背景色自动调整图标颜色
    return isLightColor(props.course.style?.color) ? '#666' : 'rgba(255,255,255,0.8)';
});

const textColor = computed(() => {
    // 根据背景色自动调整文字颜色
    return isLightColor(props.course.style?.color) ? '#333' : '#fff';
});

const isMultiWeek = computed(() => {
    return props.course.weeks && props.course.weeks.length > 1;
});

// 方法
function handleClick() {
    emit('course-click', props.course);
}

function handleLongPress() {
    emit('course-long-press', props.course);
}

function formatLocation(location) {
    if (!location) return '';
    // 简化地点显示，去掉重复信息
    return location.replace(/实验室/g, '室').substring(0, 8);
}

function getBadgeColor(courseType) {
    const colorMap = {
        '必修': '#e74c3c',
        '选修': '#3498db',
        '任选': '#27ae60',
        '限选': '#f39c12',
        '实践': '#9b59b6'
    };
    return colorMap[courseType] || '#95a5a6';
}

function getWeekText() {
    if (!props.course.weeks) return '';
    const weeks = props.course.weeks;
    if (weeks.length <= 3) {
        return `第${weeks.join(',')}周`;
    }
    return `第${weeks[0]}-${weeks[weeks.length - 1]}周`;
}

function isLightColor(hexColor) {
    if (!hexColor) return true;

    // 移除#号
    const color = hexColor.replace('#', '');

    // 转换为RGB
    const r = parseInt(color.substr(0, 2), 16);
    const g = parseInt(color.substr(2, 2), 16);
    const b = parseInt(color.substr(4, 2), 16);

    // 计算亮度
    const brightness = (r * 299 + g * 587 + b * 114) / 1000;

    return brightness > 128;
}
</script>

<style lang="scss" scoped>
@import './CourseCard.scss';
</style>
