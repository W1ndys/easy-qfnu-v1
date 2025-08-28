<template>
    <view class="date-selector">
        <!-- 今日标识 -->
        <view v-if="isToday" class="today-indicator">今日</view>

        <!-- 日期导航 -->
        <view class="date-header">
            <view class="date-navigation">
                <!-- 前一天按钮 -->
                <button class="nav-btn" @click="handlePreviousDay">
                    <uni-icons type="left" size="20" color="#495057" />
                </button>

                <!-- 日期显示区域 -->
                <view class="date-display" @click="showDatePicker">
                    <view class="main-date">
                        {{ dateInfo.month }}月{{ dateInfo.day }}日
                    </view>
                    <view class="date-detail">
                        <text class="weekday">{{ dateInfo.weekDay }}</text>
                        <text>•</text>
                        <text>{{ dateInfo.year }}</text>
                    </view>
                </view>

                <!-- 后一天按钮 -->
                <button class="nav-btn" @click="handleNextDay">
                    <uni-icons type="right" size="20" color="#495057" />
                </button>
            </view>

            <!-- 日期选择按钮 -->
            <button class="date-picker-btn" @click="showDatePicker">
                <uni-icons type="calendar" size="16" color="#ffffff" />
            </button>
        </view>
    </view>

    <!-- 日期选择器弹窗 -->
    <view v-if="pickerVisible" class="date-picker-overlay" @click="hideDatePicker">
        <view class="date-picker-popup" :class="{ show: pickerVisible }" @click.stop>
            <view class="picker-header">
                <text class="picker-title">选择日期</text>
                <button class="picker-close" @click="hideDatePicker">
                    <uni-icons type="closeempty" size="16" color="#6c757d" />
                </button>
            </view>

            <picker-view :value="pickerValue" @change="onPickerChange" class="date-picker-view">
                <picker-view-column>
                    <view v-for="(year, index) in years" :key="index" class="picker-item">
                        {{ year }}年
                    </view>
                </picker-view-column>
                <picker-view-column>
                    <view v-for="(month, index) in months" :key="index" class="picker-item">
                        {{ month }}月
                    </view>
                </picker-view-column>
                <picker-view-column>
                    <view v-for="(day, index) in days" :key="index" class="picker-item">
                        {{ day }}日
                    </view>
                </picker-view-column>
            </picker-view>

            <view class="picker-actions">
                <button class="picker-btn cancel" @click="hideDatePicker">取消</button>
                <button class="picker-btn confirm" @click="confirmDatePicker">确定</button>
            </view>
        </view>
    </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useDateSelector } from './DateSelector.js';

// Props
const props = defineProps({
    modelValue: {
        type: [String, Date],
        default: () => new Date()
    }
});

// Emits
const emit = defineEmits(['update:modelValue', 'change']);

// 使用日期选择器逻辑
const { selectedDate, dateInfo, goToPreviousDay, goToNextDay, setDate, formatDate } = useDateSelector();

// 弹窗状态
const pickerVisible = ref(false);

// 判断是否为今天
const isToday = computed(() => {
    const today = new Date();
    const selected = selectedDate.value;
    return (
        today.getFullYear() === selected.getFullYear() &&
        today.getMonth() === selected.getMonth() &&
        today.getDate() === selected.getDate()
    );
});

// 日期选择器数据
const years = computed(() => {
    const currentYear = new Date().getFullYear();
    const startYear = currentYear - 5;
    const endYear = currentYear + 5;
    const yearList = [];
    for (let i = startYear; i <= endYear; i++) {
        yearList.push(i);
    }
    return yearList;
});

const months = computed(() => {
    const monthList = [];
    for (let i = 1; i <= 12; i++) {
        monthList.push(i);
    }
    return monthList;
});

const days = computed(() => {
    const year = tempDate.value.getFullYear();
    const month = tempDate.value.getMonth() + 1;
    const daysInMonth = new Date(year, month, 0).getDate();
    const dayList = [];
    for (let i = 1; i <= daysInMonth; i++) {
        dayList.push(i);
    }
    return dayList;
});

// 临时日期（用于选择器）
const tempDate = ref(new Date());

// 选择器当前值
const pickerValue = ref([0, 0, 0]);

// 初始化
watch(() => props.modelValue, (newValue) => {
    if (newValue) {
        setDate(newValue);
    }
}, { immediate: true });

// 监听选中日期变化
watch(selectedDate, (newDate) => {
    emit('update:modelValue', formatDate(newDate));
    emit('change', {
        date: formatDate(newDate),
        dateInfo: dateInfo.value
    });
}, { immediate: true });

// 更新选择器值
const updatePickerValue = (date) => {
    const yearIndex = years.value.findIndex(year => year === date.getFullYear());
    const monthIndex = date.getMonth();
    const dayIndex = date.getDate() - 1;
    pickerValue.value = [
        Math.max(0, yearIndex),
        Math.max(0, monthIndex),
        Math.max(0, dayIndex)
    ];
};

// 处理前一天
const handlePreviousDay = () => {
    goToPreviousDay();
};

// 处理后一天
const handleNextDay = () => {
    goToNextDay();
};

// 显示日期选择器
const showDatePicker = () => {
    tempDate.value = new Date(selectedDate.value);
    updatePickerValue(tempDate.value);
    pickerVisible.value = true;
};

// 隐藏日期选择器
const hideDatePicker = () => {
    pickerVisible.value = false;
};

// 选择器值变化
const onPickerChange = (e) => {
    const [yearIndex, monthIndex, dayIndex] = e.detail.value;
    pickerValue.value = e.detail.value;

    const year = years.value[yearIndex];
    const month = monthIndex + 1;
    const day = days.value[dayIndex];

    tempDate.value = new Date(year, month - 1, day);
};

// 确认日期选择
const confirmDatePicker = () => {
    setDate(tempDate.value);
    hideDatePicker();
};
</script>

<style lang="scss" scoped>
@import "./DateSelector.scss";

.date-picker-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 999;
    display: flex;
    align-items: flex-end;
}

.date-picker-view {
    height: 400rpx;
    margin: 20rpx 0;
}

.picker-item {
    height: 80rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28rpx;
    color: #2c3e50;
}
</style>
