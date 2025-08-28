/**
 * 统计卡片组件逻辑
 */

import { computed } from 'vue';

/**
 * 统计数据处理组合式函数
 * @param {Object} stats - 统计数据
 */
export function useStatsData(stats) {
    // 计算平均每日课程数
    const averageCoursesPerDay = computed(() => {
        if (!stats.value?.total_courses) return 0;
        const totalDays = Object.keys(stats.value.courses_by_day || {}).length;
        return totalDays > 0 ? Math.round(stats.value.total_courses / totalDays * 10) / 10 : 0;
    });

    // 判断是否有课程数据
    const hasCoursesData = computed(() => {
        return stats.value?.total_courses > 0;
    });

    // 最忙碌的一天
    const busyDay = computed(() => {
        if (!stats.value?.courses_by_day) return null;
        const entries = Object.entries(stats.value.courses_by_day);
        if (entries.length === 0) return null;

        const maxEntry = entries.reduce((max, current) =>
            current[1] > max[1] ? current : max
        );
        return maxEntry[1] > 0 ? maxEntry[0] : null;
    });

    // 最清闲的一天
    const freeDay = computed(() => {
        if (!stats.value?.courses_by_day) return null;
        const entries = Object.entries(stats.value.courses_by_day);
        if (entries.length === 0) return null;

        const minEntry = entries.reduce((min, current) =>
            current[1] < min[1] ? current : min
        );
        return minEntry[1] === 0 ? minEntry[0] : null;
    });

    // 时间安排建议
    const timeAdvice = computed(() => {
        if (!hasCoursesData.value) return null;

        const totalCourses = stats.value.total_courses;
        const totalHours = stats.value.total_hours;

        if (totalCourses <= 8) return '课程安排较轻松，可以安排更多自习时间 😊';
        if (totalCourses <= 15) return '课程安排适中，注意劳逸结合 📚';
        if (totalCourses <= 20) return '课程安排较满，合理规划时间 ⏰';
        return '课程安排很紧密，注意身体健康 💪';
    });

    // 课程强度分析
    const courseIntensity = computed(() => {
        if (!hasCoursesData.value) return 'low';

        const totalCourses = stats.value.total_courses;
        if (totalCourses <= 8) return 'low';
        if (totalCourses <= 15) return 'medium';
        if (totalCourses <= 20) return 'high';
        return 'very-high';
    });

    return {
        averageCoursesPerDay,
        hasCoursesData,
        busyDay,
        freeDay,
        timeAdvice,
        courseIntensity
    };
}

/**
 * 图表数据处理工具
 */
export const chartUtils = {
    /**
     * 获取星期简称
     */
    getDayShort(dayName) {
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
    },

    /**
     * 计算柱状图高度
     */
    getBarHeight(count, coursesByDay) {
        if (!coursesByDay) return 0;
        const maxCount = Math.max(...Object.values(coursesByDay));
        if (maxCount === 0) return 0;

        const minHeight = 20;
        const maxHeight = 120;
        return minHeight + (count / maxCount) * (maxHeight - minHeight);
    },

    /**
     * 获取柱状图颜色
     */
    getBarColor(count, maxCount) {
        if (count === 0) return '#dee2e6';

        const intensity = count / maxCount;
        if (intensity <= 0.3) return '#27ae60';
        if (intensity <= 0.6) return '#f39c12';
        if (intensity <= 0.8) return '#e67e22';
        return '#e74c3c';
    },

    /**
     * 格式化统计数字
     */
    formatStatNumber(num) {
        if (num === 0) return '0';
        if (num < 10) return num.toString();
        if (num < 100) return num.toString();
        return '99+';
    }
};

/**
 * 统计数据验证工具
 */
export const statsValidator = {
    /**
     * 验证统计数据结构
     */
    validateStats(stats) {
        if (!stats || typeof stats !== 'object') {
            return false;
        }

        // 检查必需字段
        const requiredFields = ['total_courses', 'total_hours', 'courses_by_day'];
        for (const field of requiredFields) {
            if (!(field in stats)) {
                console.warn(`Missing required field: ${field}`);
                return false;
            }
        }

        // 检查数据类型
        if (typeof stats.total_courses !== 'number' || stats.total_courses < 0) {
            console.warn('Invalid total_courses value');
            return false;
        }

        if (typeof stats.total_hours !== 'number' || stats.total_hours < 0) {
            console.warn('Invalid total_hours value');
            return false;
        }

        if (typeof stats.courses_by_day !== 'object') {
            console.warn('Invalid courses_by_day value');
            return false;
        }

        return true;
    },

    /**
     * 修复统计数据
     */
    fixStats(stats) {
        const defaultStats = {
            total_courses: 0,
            total_hours: 0,
            courses_by_day: {}
        };

        if (!stats || typeof stats !== 'object') {
            return defaultStats;
        }

        return {
            total_courses: Math.max(0, Number(stats.total_courses) || 0),
            total_hours: Math.max(0, Number(stats.total_hours) || 0),
            courses_by_day: stats.courses_by_day && typeof stats.courses_by_day === 'object'
                ? stats.courses_by_day
                : {}
        };
    }
};
