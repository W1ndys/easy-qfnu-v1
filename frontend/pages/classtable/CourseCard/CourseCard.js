/**
 * 课程卡片组件逻辑
 */

import { computed } from 'vue';

/**
 * 课程卡片组合式函数
 * @param {Object} props - 组件属性
 * @param {Function} emit - 事件发射器
 */
export function useCourseCard(props, emit) {
    // 计算属性
    const courseStyle = computed(() => {
        const course = props.course;
        const baseStyle = {
            backgroundColor: course.style?.color || '#3498db',
            borderLeft: `4rpx solid ${course.style?.color || '#3498db'}`,
            color: getTextColor(course.style?.color)
        };

        // 根据紧凑模式调整样式
        if (props.compact) {
            baseStyle.padding = '8rpx';
            baseStyle.minHeight = '60rpx';
        }

        return baseStyle;
    });

    const iconColor = computed(() => {
        return isLightColor(props.course.style?.color) ? '#666' : 'rgba(255,255,255,0.8)';
    });

    const textColor = computed(() => {
        return getTextColor(props.course.style?.color);
    });

    const isMultiWeek = computed(() => {
        return props.course.weeks && props.course.weeks.length > 1;
    });

    const courseTypeClass = computed(() => {
        return `course-type-${props.course.course_type || 'default'}`;
    });

    // 方法
    function handleClick() {
        emit('course-click', props.course);

        // 触觉反馈
        if (uni.vibrateShort) {
            uni.vibrateShort();
        }
    }

    function handleLongPress() {
        emit('course-long-press', props.course);

        // 强触觉反馈
        if (uni.vibrateLong) {
            uni.vibrateLong();
        }
    }

    function formatLocation(location) {
        if (!location) return '';

        // 简化地点显示规则
        let formatted = location
            .replace(/实验室/g, '室')
            .replace(/教学楼/g, '楼')
            .replace(/校区/g, '')
            .trim();

        // 限制长度
        if (formatted.length > 10) {
            formatted = formatted.substring(0, 8) + '...';
        }

        return formatted;
    }

    function getBadgeColor(courseType) {
        const colorMap = {
            '必修': '#e74c3c',
            '选修': '#3498db',
            '任选': '#27ae60',
            '限选': '#f39c12',
            '实践': '#9b59b6',
            '通选': '#1abc9c',
            '专选': '#e67e22'
        };
        return colorMap[courseType] || '#95a5a6';
    }

    function getWeekText() {
        if (!props.course.weeks || props.course.weeks.length === 0) return '';

        const weeks = props.course.weeks.sort((a, b) => a - b);

        if (weeks.length === 1) {
            return `第${weeks[0]}周`;
        } else if (weeks.length <= 3) {
            return `第${weeks.join(',')}周`;
        } else {
            // 检查是否为连续周次
            const isConsecutive = weeks.every((week, index) =>
                index === 0 || week === weeks[index - 1] + 1
            );

            if (isConsecutive) {
                return `第${weeks[0]}-${weeks[weeks.length - 1]}周`;
            } else {
                return `第${weeks[0]}-${weeks[weeks.length - 1]}周等`;
            }
        }
    }

    function getCourseDuration() {
        const timeInfo = props.course.time_info;
        if (!timeInfo?.start_time || !timeInfo?.end_time) return '';

        const start = new Date(`2000-01-01 ${timeInfo.start_time}`);
        const end = new Date(`2000-01-01 ${timeInfo.end_time}`);
        const duration = (end - start) / (1000 * 60); // 分钟

        if (duration >= 60) {
            const hours = Math.floor(duration / 60);
            const mins = duration % 60;
            return mins > 0 ? `${hours}h${mins}m` : `${hours}h`;
        } else {
            return `${duration}m`;
        }
    }

    return {
        // 计算属性
        courseStyle,
        iconColor,
        textColor,
        isMultiWeek,
        courseTypeClass,

        // 方法
        handleClick,
        handleLongPress,
        formatLocation,
        getBadgeColor,
        getWeekText,
        getCourseDuration
    };
}

/**
 * 颜色工具函数
 */
export const colorUtils = {
    /**
     * 判断是否为浅色
     */
    isLightColor(hexColor) {
        if (!hexColor) return true;

        const color = hexColor.replace('#', '');
        if (color.length !== 6) return true;

        const r = parseInt(color.substr(0, 2), 16);
        const g = parseInt(color.substr(2, 2), 16);
        const b = parseInt(color.substr(4, 2), 16);

        // 使用相对亮度公式
        const brightness = (r * 299 + g * 587 + b * 114) / 1000;
        return brightness > 128;
    },

    /**
     * 获取合适的文字颜色
     */
    getTextColor(backgroundColor) {
        return this.isLightColor(backgroundColor) ? '#333' : '#fff';
    },

    /**
     * 获取对比色
     */
    getContrastColor(hexColor) {
        return this.isLightColor(hexColor) ? '#000' : '#fff';
    },

    /**
     * 调整颜色亮度
     */
    adjustBrightness(hexColor, percent) {
        if (!hexColor) return '#3498db';

        const color = hexColor.replace('#', '');
        const num = parseInt(color, 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = (num >> 8 & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;

        return '#' + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
    }
};

/**
 * 课程数据格式化工具
 */
export const courseFormatter = {
    /**
     * 格式化课程时间
     */
    formatCourseTime(timeInfo) {
        if (!timeInfo) return '';

        const { start_time, end_time, period_name } = timeInfo;

        if (start_time && end_time) {
            return `${start_time}-${end_time}`;
        }

        if (period_name) {
            return period_name;
        }

        return '';
    },

    /**
     * 格式化课程地点
     */
    formatCourseLocation(location, maxLength = 10) {
        if (!location) return '';

        let formatted = location
            .replace(/实验室/g, '室')
            .replace(/教学楼/g, '楼')
            .replace(/校区/g, '')
            .replace(/分校/g, '')
            .trim();

        if (formatted.length > maxLength) {
            formatted = formatted.substring(0, maxLength - 3) + '...';
        }

        return formatted;
    },

    /**
     * 格式化教师姓名
     */
    formatTeacherName(teacher) {
        if (!teacher) return '';

        // 处理多个教师的情况
        if (teacher.includes(',') || teacher.includes('，')) {
            const teachers = teacher.split(/[,，]/).map(t => t.trim());
            if (teachers.length > 2) {
                return `${teachers[0]}等${teachers.length}人`;
            }
            return teachers.join(',');
        }

        return teacher;
    },

    /**
     * 格式化学分
     */
    formatCredits(credits) {
        if (!credits) return '';

        const num = parseFloat(credits);
        if (isNaN(num)) return credits;

        return num === Math.floor(num) ? num.toString() : num.toFixed(1);
    },

    /**
     * 获取课程简介
     */
    getCourseShortInfo(course) {
        const parts = [];

        if (course.teacher) {
            parts.push(this.formatTeacherName(course.teacher));
        }

        if (course.location) {
            parts.push(this.formatCourseLocation(course.location, 8));
        }

        if (course.time_info) {
            parts.push(this.formatCourseTime(course.time_info));
        }

        return parts.join(' · ');
    }
};

// 导出工具函数
function isLightColor(hexColor) {
    return colorUtils.isLightColor(hexColor);
}

function getTextColor(backgroundColor) {
    return colorUtils.getTextColor(backgroundColor);
}
