/**
 * CourseCard 组件的业务逻辑
 */

import { computed } from 'vue';

export function useCourseCard(props) {
    // 计算课程时间显示
    const timeDisplay = computed(() => {
        if (!props.course?.time_info) return '';

        const timeInfo = props.course.time_info;
        const { start_time, end_time, is_cross_period, actual_periods, period_name } = timeInfo;

        if (is_cross_period && actual_periods && actual_periods.length > 0) {
            // 跨大节课程：显示实际节次范围
            const firstPeriod = actual_periods[0];
            const lastPeriod = actual_periods[actual_periods.length - 1];
            return `第${firstPeriod}-${lastPeriod}节 ${start_time}-${end_time}`;
        } else {
            // 普通课程：显示大节名称
            return `${period_name || ''} ${start_time}-${end_time}`;
        }
    });

    // 统一的课程卡片样式（浅色主题）
    const cardStyle = computed(() => {
        return {
            background: '#ffffff',
            borderLeft: '4rpx solid #d4b896'
        };
    });

    // 获取课程类型标签样式（浅色主题）
    const getTypeTagStyle = (courseType) => {
        const typeStyles = {
            '必修': { background: '#ffebee', color: '#c62828' },
            '选修': { background: '#fff3e0', color: '#ef6c00' },
            '任选': { background: '#f3e5f5', color: '#7b1fa2' },
            '限选': { background: '#fff3e0', color: '#f57c00' },
            '实践': { background: '#e8f5e8', color: '#2e7d32' },
            '通识': { background: '#e3f2fd', color: '#1565c0' }
        };

        return typeStyles[courseType] || { background: '#f5f5f5', color: '#757575' };
    };



    // 格式化班级名称
    const formatClassName = (className) => {
        if (!className) return '';
        // 如果班级名称太长，进行截断
        if (className.length > 20) {
            return className.substring(0, 20) + '...';
        }
        return className;
    };

    // 格式化地点
    const formatLocation = (location) => {
        if (!location) return '';
        // 移除多余的空格和换行
        return location.trim().replace(/\s+/g, ' ');
    };

    return {
        timeDisplay,
        cardStyle,
        getTypeTagStyle,
        formatClassName,
        formatLocation
    };
}
