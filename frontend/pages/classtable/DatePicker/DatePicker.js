/**
 * 日期选择器组件逻辑
 */

import { ref, computed } from 'vue';
import { formatDate, getCurrentDate, addDays, isToday } from '../utils/dateUtils.js';

/**
 * 日期选择器组合式函数
 * @param {Object} props - 组件属性
 * @param {Function} emit - 事件发射器
 */
export function useDatePicker(props, emit) {
    // 响应式数据
    const showPicker = ref(false);

    // 计算属性
    const formattedDate = computed(() => {
        const date = new Date(props.currentDate);
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const weekDays = ['日', '一', '二', '三', '四', '五', '六'];
        const weekDay = weekDays[date.getDay()];

        return `${year}年${month}月${day}日 周${weekDay}`;
    });

    const isCurrentToday = computed(() => {
        return isToday(props.currentDate);
    });

    const weekProgress = computed(() => {
        if (!props.weekInfo) return 0;
        return Math.round((props.weekInfo.current_week / props.weekInfo.total_weeks) * 100);
    });

    // 方法
    function handleDatePicker() {
        showPicker.value = true;

        // 使用uni-app的日期选择器
        uni.showModal({
            title: '选择查看日期',
            content: '点击确定打开日期选择器',
            success: (res) => {
                if (res.confirm) {
                    // 这里可以集成第三方日期选择器
                    // 或者使用uni-app的picker组件
                    showSimpleDateInput();
                }
            }
        });
    }

    function showSimpleDateInput() {
        uni.showModal({
            title: '输入日期',
            content: '请输入日期(格式：YYYY-MM-DD)',
            editable: true,
            placeholderText: props.currentDate,
            success: (res) => {
                if (res.confirm && res.content) {
                    if (validateDateFormat(res.content)) {
                        emit('date-change', res.content);
                    } else {
                        uni.showToast({
                            title: '日期格式错误',
                            icon: 'none'
                        });
                    }
                }
            }
        });
    }

    function validateDateFormat(dateStr) {
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!dateRegex.test(dateStr)) return false;

        // 检查日期是否有效
        const date = new Date(dateStr);
        return date instanceof Date && !isNaN(date);
    }

    function selectToday() {
        const today = getCurrentDate();
        if (today !== props.currentDate) {
            emit('date-change', today);
            uni.showToast({
                title: '已切换到今天',
                icon: 'success'
            });
        }
    }

    function goToPrevWeek() {
        const newDate = addDays(props.currentDate, -7);
        emit('date-change', newDate);
    }

    function goToNextWeek() {
        const newDate = addDays(props.currentDate, 7);
        emit('date-change', newDate);
    }

    function goToPrevDay() {
        const newDate = addDays(props.currentDate, -1);
        emit('date-change', newDate);
    }

    function goToNextDay() {
        const newDate = addDays(props.currentDate, 1);
        emit('date-change', newDate);
    }

    return {
        // 响应式数据
        showPicker,

        // 计算属性
        formattedDate,
        isCurrentToday,
        weekProgress,

        // 方法
        handleDatePicker,
        selectToday,
        goToPrevWeek,
        goToNextWeek,
        goToPrevDay,
        goToNextDay
    };
}

/**
 * 日期格式化工具
 */
export const dateFormatter = {
    /**
     * 格式化为完整显示格式
     */
    toFullDisplay(dateStr) {
        const date = new Date(dateStr);
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const weekDays = ['日', '一', '二', '三', '四', '五', '六'];
        const weekDay = weekDays[date.getDay()];

        return `${year}年${month}月${day}日 周${weekDay}`;
    },

    /**
     * 格式化为简短显示格式
     */
    toShortDisplay(dateStr) {
        const date = new Date(dateStr);
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const weekDays = ['日', '一', '二', '三', '四', '五', '六'];
        const weekDay = weekDays[date.getDay()];

        return `${month}/${day} 周${weekDay}`;
    },

    /**
     * 格式化周信息
     */
    formatWeekInfo(weekInfo) {
        if (!weekInfo) return '';
        return `第${weekInfo.current_week}周 / 共${weekInfo.total_weeks}周`;
    }
};
