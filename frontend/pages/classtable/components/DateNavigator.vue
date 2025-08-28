<template>
    <view class="date-navigator">
        <!-- 日期导航头部 -->
        <view class="date-header">
            <button class="nav-arrow nav-arrow--prev" @click="gotoPrevDay">
                <uni-icons type="arrowleft" size="24" color="#7f4515" />
            </button>

            <view class="date-display" @click="showDatePicker">
                <view class="date-main">
                    <text class="current-day">{{ currentDateInfo.day }}</text>
                    <view class="date-meta">
                        <text class="current-month">{{ currentDateInfo.month }}</text>
                        <text class="current-weekday">{{ currentDateInfo.weekday }}</text>
                    </view>
                </view>
                <uni-icons type="calendar" size="20" color="#7f4515" />
            </view>

            <button class="nav-arrow nav-arrow--next" @click="gotoNextDay">
                <uni-icons type="arrowright" size="24" color="#7f4515" />
            </button>
        </view>

        <!-- 日期滑动选择器 -->
        <view class="date-slider">
            <scroll-view class="date-scroll" scroll-x :scroll-into-view="'date-' + currentIndex" scroll-with-animation
                enhanced :show-scrollbar="false">
                <view class="date-list">
                    <view v-for="(dateInfo, index) in displayDateList" :key="dateInfo.date" :id="'date-' + index"
                        class="date-option" :class="{
                            'date-option--active': index === currentDisplayIndex,
                            'date-option--today': dateInfo.isToday
                        }" @click="selectDate(index)">
                        <text class="option-day">{{ dateInfo.day }}</text>
                        <text class="option-weekday">{{ dateInfo.weekday.replace('周', '') }}</text>
                    </view>
                </view>
            </scroll-view>
        </view>

        <!-- 今日快速返回按钮 -->
        <view class="quick-actions" v-if="!isToday">
            <button class="today-btn" @click="gotoToday">
                <uni-icons type="home" size="16" color="#fff" />
                <text>今日</text>
            </button>
        </view>

        <!-- 日期选择弹窗 -->
        <picker mode="date" :value="selectedDate" @change="onDatePickerChange" :start="minDate" :end="maxDate">
            <view class="date-picker-trigger" ref="datePickerTrigger"></view>
        </picker>
    </view>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';

const props = defineProps({
    selectedDate: {
        type: String,
        required: true
    }
});

const emit = defineEmits(['dateChange']);

const currentIndex = ref(7); // 默认选中中间的日期
const dateList = ref([]);
const datePickerTrigger = ref(null);

// 日期范围设置（可根据需要调整）
const minDate = '2020-01-01';
const maxDate = '2030-12-31';

// 当前日期信息
const currentDateInfo = computed(() => {
    if (dateList.value.length === 0) return { day: '', month: '', weekday: '' };
    return dateList.value[currentIndex.value] || { day: '', month: '', weekday: '' };
});

// 显示的日期列表（当前日期前后各显示5天）
const displayDateList = computed(() => {
    const current = currentIndex.value;
    const start = Math.max(0, current - 5);
    const end = Math.min(dateList.value.length, current + 6);
    return dateList.value.slice(start, end);
});

// 当前在显示列表中的索引
const currentDisplayIndex = computed(() => {
    const current = currentIndex.value;
    const start = Math.max(0, current - 5);
    return current - start;
});

// 是否为今天
const isToday = computed(() => {
    const today = new Date().toISOString().split('T')[0];
    return props.selectedDate === today;
});

// 初始化日期列表（默认生成前后7天，共15天）
function initDateList(centerDate = null) {
    const dates = [];
    const center = centerDate ? new Date(centerDate) : new Date();

    // 生成前后7天的日期列表，共15天
    for (let i = -7; i <= 7; i++) {
        const date = new Date(center);
        date.setDate(center.getDate() + i);

        dates.push(createDateInfo(date));
    }

    dateList.value = dates;

    // 设置当前索引
    if (centerDate) {
        const targetIndex = dateList.value.findIndex(item => item.date === centerDate);
        if (targetIndex !== -1) {
            currentIndex.value = targetIndex;
        }
    } else {
        currentIndex.value = 7; // 今天在中间位置
    }
}

// 创建日期信息对象
function createDateInfo(date) {
    const dateStr = date.toISOString().split('T')[0];
    const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
    const today = new Date().toISOString().split('T')[0];

    return {
        date: dateStr,
        day: date.getDate().toString(),
        month: `${date.getMonth() + 1}月`,
        weekday: `周${weekdays[date.getDay()]}`,
        isToday: dateStr === today
    };
}

// 扩展日期列表（向前或向后添加更多日期）
function extendDateList(direction = 'forward', count = 7) {
    if (direction === 'forward') {
        // 向后添加日期
        const lastDate = new Date(dateList.value[dateList.value.length - 1].date);
        for (let i = 1; i <= count; i++) {
            const newDate = new Date(lastDate);
            newDate.setDate(lastDate.getDate() + i);
            dateList.value.push(createDateInfo(newDate));
        }
    } else {
        // 向前添加日期
        const firstDate = new Date(dateList.value[0].date);
        const newDates = [];
        for (let i = count; i >= 1; i--) {
            const newDate = new Date(firstDate);
            newDate.setDate(firstDate.getDate() - i);
            newDates.push(createDateInfo(newDate));
        }
        dateList.value = [...newDates, ...dateList.value];
        // 调整当前索引
        currentIndex.value += count;
    }
}

// 选择日期
function selectDate(displayIndex) {
    const current = currentIndex.value;
    const start = Math.max(0, current - 5);
    const realIndex = start + displayIndex;

    if (realIndex >= 0 && realIndex < dateList.value.length) {
        currentIndex.value = realIndex;
        const selectedDateInfo = dateList.value[realIndex];
        emit('dateChange', selectedDateInfo.date);
    }
}

// 前一天
function gotoPrevDay() {
    if (currentIndex.value > 0) {
        currentIndex.value--;
    } else {
        // 如果已经是第一个，扩展前面的日期
        extendDateList('backward', 7);
        currentIndex.value = 6; // 移到新扩展的日期中
    }
    const selectedDateInfo = dateList.value[currentIndex.value];
    emit('dateChange', selectedDateInfo.date);
}

// 后一天
function gotoNextDay() {
    if (currentIndex.value < dateList.value.length - 1) {
        currentIndex.value++;
    } else {
        // 如果已经是最后一个，扩展后面的日期
        extendDateList('forward', 7);
        currentIndex.value++;
    }
    const selectedDateInfo = dateList.value[currentIndex.value];
    emit('dateChange', selectedDateInfo.date);
}

// 跳转到今天
function gotoToday() {
    const todayDate = new Date().toISOString().split('T')[0];
    jumpToDate(todayDate);
}

// 跳转到指定日期
function jumpToDate(targetDate) {
    const existingIndex = dateList.value.findIndex(item => item.date === targetDate);

    if (existingIndex !== -1) {
        // 日期已存在，直接跳转
        currentIndex.value = existingIndex;
    } else {
        // 日期不存在，重新初始化以该日期为中心的列表
        initDateList(targetDate);
    }

    emit('dateChange', targetDate);
}

// 显示日期选择器
function showDatePicker() {
    // 触发原生日期选择器
    nextTick(() => {
        const pickerElement = datePickerTrigger.value;
        if (pickerElement) {
            pickerElement.click();
        }
    });
}

// 日期选择器变化事件
function onDatePickerChange(event) {
    const selectedDate = event.detail.value;
    jumpToDate(selectedDate);
}

// 监听外部日期变化
watch(() => props.selectedDate, (newDate) => {
    const index = dateList.value.findIndex(item => item.date === newDate);
    if (index !== -1) {
        currentIndex.value = index;
    } else {
        jumpToDate(newDate);
    }
});

// 监听当前索引变化，检查是否需要扩展
watch(currentIndex, (newIndex) => {
    // 接近边界时自动扩展
    if (newIndex <= 2) {
        extendDateList('backward', 7);
    } else if (newIndex >= dateList.value.length - 3) {
        extendDateList('forward', 7);
    }
});

// 初始化
initDateList();
</script>

<style lang="scss" scoped>
.date-navigator {
    background: linear-gradient(135deg, #ffffff 0%, #fefefe 100%);
    border-radius: 24rpx;
    margin-bottom: 24rpx;
    box-shadow: 0 8rpx 24rpx rgba(127, 69, 21, 0.08);
    border: 1rpx solid rgba(127, 69, 21, 0.1);
    overflow: hidden;
}

/* 日期导航头部 */
.date-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24rpx 20rpx;
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    border-bottom: 1rpx solid #f0f0f0;
}

.nav-arrow {
    width: 64rpx;
    height: 64rpx;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.8);
    border: 1rpx solid rgba(127, 69, 21, 0.15);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;

    &::after {
        border: none;
    }

    &:active {
        transform: scale(0.95);
        background: rgba(127, 69, 21, 0.1);
    }
}

.date-display {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16rpx;
    padding: 16rpx;
    border-radius: 16rpx;
    transition: all 0.3s ease;

    &:active {
        background: rgba(127, 69, 21, 0.05);
    }
}

.date-main {
    display: flex;
    align-items: center;
    gap: 16rpx;
}

.current-day {
    font-size: 48rpx;
    font-weight: 700;
    color: #2c3e50;
    line-height: 1;
}

.date-meta {
    display: flex;
    flex-direction: column;
    gap: 4rpx;
}

.current-month {
    font-size: 22rpx;
    color: #7f4515;
    font-weight: 600;
    line-height: 1;
}

.current-weekday {
    font-size: 20rpx;
    color: #9e9e9e;
    font-weight: 500;
    line-height: 1;
}

/* 日期滑动选择器 */
.date-slider {
    padding: 20rpx 0 24rpx;
}

.date-scroll {
    width: 100%;
    white-space: nowrap;
}

.date-list {
    display: flex;
    padding: 0 20rpx;
    gap: 12rpx;
}

.date-option {
    flex-shrink: 0;
    width: 80rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 16rpx 8rpx;
    border-radius: 16rpx;
    transition: all 0.3s ease;

    &:active {
        transform: scale(0.95);
    }

    &--active {
        background: linear-gradient(135deg, #7f4515 0%, #8c5527 100%);
        transform: scale(1.05);

        .option-day,
        .option-weekday {
            color: #fff;
        }
    }

    &--today:not(.date-option--active) {
        background: rgba(127, 69, 21, 0.1);
        border: 1rpx solid rgba(127, 69, 21, 0.2);

        .option-day {
            color: #7f4515;
            font-weight: 700;
        }
    }
}

.option-day {
    font-size: 28rpx;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 4rpx;
    line-height: 1;
}

.option-weekday {
    font-size: 18rpx;
    color: #9e9e9e;
    font-weight: 500;
    line-height: 1;
}

/* 快速操作按钮 */
.quick-actions {
    position: absolute;
    top: 20rpx;
    right: 20rpx;
    z-index: 10;
}

.today-btn {
    background: linear-gradient(135deg, #7f4515 0%, #8c5527 100%);
    color: #fff;
    border: none;
    border-radius: 20rpx;
    padding: 8rpx 16rpx;
    font-size: 20rpx;
    font-weight: 600;
    box-shadow: 0 4rpx 12rpx rgba(127, 69, 21, 0.25);
    display: flex;
    align-items: center;
    gap: 6rpx;

    &::after {
        border: none;
    }

    &:active {
        transform: scale(0.95);
    }
}

.date-picker-trigger {
    display: none;
}
</style>