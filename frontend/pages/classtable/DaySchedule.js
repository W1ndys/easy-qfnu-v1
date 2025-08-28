/**
 * DaySchedule 组件的业务逻辑
 */

import { computed, ref } from 'vue';

export function useDaySchedule(props) {
    // 当前时间（用于判断课程状态）
    const currentTime = ref('');

    // 更新当前时间
    const updateCurrentTime = () => {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        currentTime.value = `${hours}:${minutes}`;
    };

    // 初始化时间并设置定时器
    const initTimeUpdate = () => {
        updateCurrentTime();
        // 每分钟更新一次时间
        const timer = setInterval(updateCurrentTime, 60000);
        return timer;
    };

    // 获取指定日期的课程
    const dayInfo = computed(() => {
        if (!props.selectedDate) return null;

        const date = new Date(props.selectedDate);
        const weekday = date.getDay() === 0 ? 7 : date.getDay(); // 周日转为7

        return {
            date: props.selectedDate,
            weekday,
            weekdayName: getWeekdayName(weekday),
            formatDate: formatDisplayDate(date)
        };
    });

    // 过滤当天的课程
    const dayCourses = computed(() => {
        if (!props.courses || !dayInfo.value) return [];

        const { weekday } = dayInfo.value;

        // 筛选当天的课程
        const courses = props.courses.filter(course => {
            return course.time_info && course.time_info.weekday === weekday;
        });

        // 按上课时间排序
        return courses.sort((a, b) => {
            const timeA = a.time_info?.start_time || '00:00';
            const timeB = b.time_info?.start_time || '00:00';
            return timeA.localeCompare(timeB);
        });
    });

    // 课程统计信息
    const dayStats = computed(() => {
        const courses = dayCourses.value;
        if (courses.length === 0) {
            return {
                totalCourses: 0,
                totalHours: 0,
                firstCourse: null,
                lastCourse: null,
                currentCourse: null,
                nextCourse: null
            };
        }

        // 计算总学时
        const totalHours = courses.reduce((sum, course) => {
            // 使用实际节次数量或display_periods长度
            const periodCount = course.time_info?.period_count ||
                course.time_info?.display_periods?.length ||
                course.time_info?.time_slots?.length || 0;
            return sum + periodCount;
        }, 0);

        // 获取当前正在进行的课程
        const now = currentTime.value;
        const currentCourse = courses.find(course => {
            const { start_time, end_time } = course.time_info || {};
            return now >= start_time && now <= end_time;
        });

        // 获取下一节课程
        const nextCourse = courses.find(course => {
            const { start_time } = course.time_info || {};
            return now < start_time;
        });

        return {
            totalCourses: courses.length,
            totalHours,
            firstCourse: courses[0],
            lastCourse: courses[courses.length - 1],
            currentCourse,
            nextCourse
        };
    });

    // 获取星期名称
    const getWeekdayName = (weekday) => {
        const weekdays = {
            1: '星期一',
            2: '星期二',
            3: '星期三',
            4: '星期四',
            5: '星期五',
            6: '星期六',
            7: '星期日'
        };
        return weekdays[weekday] || '';
    };

    // 格式化显示日期
    const formatDisplayDate = (date) => {
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const weekday = getWeekdayName(date.getDay() === 0 ? 7 : date.getDay());

        return {
            month,
            day,
            weekday,
            full: `${month}月${day}日 ${weekday}`
        };
    };

    // 判断是否为今天
    const isToday = computed(() => {
        if (!props.selectedDate) return false;

        const today = new Date();
        const selected = new Date(props.selectedDate);

        return (
            today.getFullYear() === selected.getFullYear() &&
            today.getMonth() === selected.getMonth() &&
            today.getDate() === selected.getDate()
        );
    });

    // 生成时间段列表（用于显示空档期）
    const timeSlots = computed(() => {
        if (!props.timeSlots) return [];

        return props.timeSlots.map(slot => {
            const courses = dayCourses.value.filter(course => {
                return course.time_info?.period === slot.period;
            });

            return {
                ...slot,
                courses,
                isEmpty: courses.length === 0
            };
        });
    });

    // 获取空闲时间段
    const freeTimeSlots = computed(() => {
        return timeSlots.value.filter(slot => slot.isEmpty);
    });

    return {
        currentTime,
        dayInfo,
        dayCourses,
        dayStats,
        isToday,
        timeSlots,
        freeTimeSlots,
        initTimeUpdate,
        updateCurrentTime,
        getWeekdayName,
        formatDisplayDate
    };
}
