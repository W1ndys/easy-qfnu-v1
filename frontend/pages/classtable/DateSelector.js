/**
 * DateSelector 组件的业务逻辑
 */

import { ref, computed } from 'vue';

export function useDateSelector() {
    const selectedDate = ref(new Date());

    // 格式化日期为 YYYY-MM-DD
    const formatDate = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    // 获取中文星期
    const getWeekDay = (date) => {
        const weekDays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
        return weekDays[date.getDay()];
    };

    // 计算显示的日期信息
    const dateInfo = computed(() => {
        const date = selectedDate.value;
        return {
            date: formatDate(date),
            weekDay: getWeekDay(date),
            month: date.getMonth() + 1,
            day: date.getDate(),
            year: date.getFullYear()
        };
    });

    // 前一天
    const goToPreviousDay = () => {
        const newDate = new Date(selectedDate.value);
        newDate.setDate(newDate.getDate() - 1);
        selectedDate.value = newDate;
    };

    // 后一天
    const goToNextDay = () => {
        const newDate = new Date(selectedDate.value);
        newDate.setDate(newDate.getDate() + 1);
        selectedDate.value = newDate;
    };

    // 设置具体日期
    const setDate = (date) => {
        if (typeof date === 'string') {
            selectedDate.value = new Date(date);
        } else {
            selectedDate.value = date;
        }
    };

    // 回到今天
    const goToToday = () => {
        selectedDate.value = new Date();
    };

    return {
        selectedDate,
        dateInfo,
        goToPreviousDay,
        goToNextDay,
        setDate,
        goToToday,
        formatDate
    };
}
