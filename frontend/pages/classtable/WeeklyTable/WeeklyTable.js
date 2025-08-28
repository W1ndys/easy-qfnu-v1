/**
 * 周课程表组件逻辑
 */

import { ref, computed } from 'vue';
import { getCurrentDate, getWeekDates, isToday } from '../utils/dateUtils.js';

/**
 * 课程表数据处理组合式函数
 * @param {Object} props - 组件属性
 */
export function useWeeklyTable(props) {
    // 响应式数据
    const selectedCourse = ref(null);
    const showCourseDetail = ref(false);

    // 计算属性
    const hasCourses = computed(() => {
        return props.courses && props.courses.length > 0;
    });

    const weekDates = computed(() => {
        return getWeekDates(props.currentDate || getCurrentDate());
    });

    const courseMatrix = computed(() => {
        // 创建课程矩阵，便于快速查找
        const matrix = {};

        props.courses.forEach(course => {
            const key = `${course.time_info.period}-${course.time_info.weekday}`;
            if (!matrix[key]) {
                matrix[key] = [];
            }
            matrix[key].push(course);
        });

        return matrix;
    });

    // 方法
    function isCurrentToday(weekdayId) {
        const today = new Date();
        const todayWeekday = today.getDay() === 0 ? 7 : today.getDay();
        return weekdayId === todayWeekday && isToday(props.currentDate || getCurrentDate());
    }

    function getWeekdayDate(weekdayId) {
        if (!weekDates.value || weekDates.value.length === 0) return '';

        const dateIndex = weekdayId - 1;
        if (dateIndex < 0 || dateIndex >= weekDates.value.length) return '';

        const date = new Date(weekDates.value[dateIndex]);
        return `${date.getMonth() + 1}/${date.getDate()}`;
    }

    function getCoursesForSlot(period, weekdayId) {
        const key = `${period}-${weekdayId}`;
        return courseMatrix.value[key] || [];
    }

    function handleCourseClick(course) {
        selectedCourse.value = course;
        showCourseDetail.value = true;
    }

    function closeCourseDetail() {
        showCourseDetail.value = false;
        selectedCourse.value = null;
    }

    function getTimeSlotHeight(timeSlot) {
        // 根据时间段的课程数量调整高度
        const maxCourses = Math.max(...props.weekdays.map(weekday =>
            getCoursesForSlot(timeSlot.period, weekday.id).length
        ));

        const baseHeight = 120; // 基础高度 120rpx
        const additionalHeight = Math.max(0, maxCourses - 1) * 60; // 每增加一门课程增加60rpx

        return baseHeight + additionalHeight;
    }

    return {
        // 响应式数据
        selectedCourse,
        showCourseDetail,

        // 计算属性
        hasCourses,
        weekDates,
        courseMatrix,

        // 方法
        isCurrentToday,
        getWeekdayDate,
        getCoursesForSlot,
        handleCourseClick,
        closeCourseDetail,
        getTimeSlotHeight
    };
}

/**
 * 课程表渲染工具
 */
export const tableRenderUtils = {
    /**
     * 获取课程在单元格中的位置样式
     */
    getCoursePositionStyle(course, coursesInSameSlot) {
        const totalCourses = coursesInSameSlot.length;
        const courseIndex = coursesInSameSlot.findIndex(c => c.id === course.id);

        if (totalCourses === 1) {
            return {
                width: '100%',
                height: '100%',
                top: '0',
                left: '0'
            };
        }

        // 多个课程时的布局
        const height = `${100 / totalCourses}%`;
        const top = `${(courseIndex / totalCourses) * 100}%`;

        return {
            width: '100%',
            height,
            top,
            left: '0',
            position: 'absolute'
        };
    },

    /**
     * 获取时间段的显示文本
     */
    getTimeSlotDisplayText(timeSlot) {
        return {
            name: timeSlot.name || `第${timeSlot.period}节`,
            time: timeSlot.time || '',
            period: timeSlot.period
        };
    },

    /**
     * 获取星期的显示文本
     */
    getWeekdayDisplayText(weekday) {
        return {
            full: weekday.name || `星期${weekday.id}`,
            short: weekday.short || weekday.name || `周${weekday.id}`,
            id: weekday.id
        };
    },

    /**
     * 检查课程是否跨时间段
     */
    isMultiPeriodCourse(course) {
        return course.time_info.time_slots &&
            course.time_info.time_slots.length > 1;
    },

    /**
     * 获取课程的跨度信息
     */
    getCourseSpanInfo(course) {
        const timeSlots = course.time_info.time_slots || [course.time_info.period];
        return {
            startPeriod: Math.min(...timeSlots),
            endPeriod: Math.max(...timeSlots),
            span: timeSlots.length
        };
    }
};

/**
 * 课程表交互工具
 */
export const tableInteractionUtils = {
    /**
     * 处理课程点击事件
     */
    handleCourseClick(course, emit) {
        emit('course-click', course);

        // 触觉反馈
        if (uni.vibrateShort) {
            uni.vibrateShort();
        }
    },

    /**
     * 处理课程长按事件
     */
    handleCourseLongPress(course, emit) {
        emit('course-long-press', course);

        // 显示课程详情菜单
        uni.showActionSheet({
            itemList: ['查看详情', '添加提醒', '分享课程'],
            success: (res) => {
                switch (res.tapIndex) {
                    case 0:
                        emit('course-detail', course);
                        break;
                    case 1:
                        emit('course-reminder', course);
                        break;
                    case 2:
                        emit('course-share', course);
                        break;
                }
            }
        });
    },

    /**
     * 处理空单元格点击事件
     */
    handleEmptyCellClick(period, weekdayId, emit) {
        emit('empty-cell-click', { period, weekdayId });
    },

    /**
     * 滚动到今天
     */
    scrollToToday(tableRef) {
        if (!tableRef) return;

        const todayWeekday = new Date().getDay() || 7;
        const todayElement = tableRef.querySelector(`.weekday-header.today`);

        if (todayElement) {
            todayElement.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
                inline: 'center'
            });
        }
    },

    /**
     * 滚动到指定时间段
     */
    scrollToPeriod(tableRef, period) {
        if (!tableRef) return;

        const periodElement = tableRef.querySelector(`[data-period="${period}"]`);

        if (periodElement) {
            periodElement.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }
    }
};
