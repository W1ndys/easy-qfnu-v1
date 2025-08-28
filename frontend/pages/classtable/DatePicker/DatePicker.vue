<template>
    <ModernCard title="📅 日期选择">
        <view class="date-picker-container">
            <!-- 周信息显示 -->
            <view class="week-info" v-if="weekInfo">
                <view class="week-display">
                    <text class="week-label">第</text>
                    <text class="week-number">{{ weekInfo.current_week }}</text>
                    <text class="week-label">周</text>
                    <text class="week-total">/{{ weekInfo.total_weeks }}周</text>
                </view>
            </view>

            <!-- 日期选择器 -->
            <view class="date-selector">
                <view class="date-display" @click="showDatePicker">
                    <uni-icons type="calendar" size="20" color="#7f4515" />
                    <text class="selected-date">{{ formattedDate }}</text>
                    <uni-icons type="arrowdown" size="16" color="#999" />
                </view>

                <!-- 快捷选择按钮 -->
                <view class="quick-actions">
                    <button class="quick-btn" :class="{ active: isToday }" @click="selectToday">
                        <uni-icons type="location" size="16" color="#7f4515" />
                        <text>今天</text>
                    </button>
                    <button class="quick-btn" @click="goToPrevWeek">
                        <uni-icons type="arrowleft" size="16" color="#666" />
                        <text>上周</text>
                    </button>
                    <button class="quick-btn" @click="goToNextWeek">
                        <uni-icons type="arrowright" size="16" color="#666" />
                        <text>下周</text>
                    </button>
                </view>
            </view>
        </view>
    </ModernCard>
</template>

<script>
export default {
    name: 'DatePicker'
};
</script>

<script setup>
import { computed } from 'vue';
import { formatDate, getCurrentDate, addDays, isToday as checkIsToday } from '../utils/dateUtils.js';
import ModernCard from '../../../components/ModernCard/ModernCard.vue';

const props = defineProps({
    currentDate: {
        type: String,
        required: true
    },
    weekInfo: {
        type: Object,
        default: null
    }
});

const emit = defineEmits(['date-change']);

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

const isToday = computed(() => {
    return checkIsToday(props.currentDate);
});

// 方法
function showDatePicker() {
    uni.showModal({
        title: '选择日期',
        content: '点击确定打开日期选择器',
        success: (res) => {
            if (res.confirm) {
                // 在实际应用中，这里可以使用更好的日期选择器组件
                // 暂时使用简单的输入框
                uni.showModal({
                    title: '输入日期',
                    content: '请输入日期(YYYY-MM-DD格式)',
                    editable: true,
                    placeholderText: props.currentDate,
                    success: (inputRes) => {
                        if (inputRes.confirm && inputRes.content) {
                            const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
                            if (dateRegex.test(inputRes.content)) {
                                emit('date-change', inputRes.content);
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
        }
    });
}

function selectToday() {
    emit('date-change', getCurrentDate());
}

function goToPrevWeek() {
    const newDate = addDays(props.currentDate, -7);
    emit('date-change', newDate);
}

function goToNextWeek() {
    const newDate = addDays(props.currentDate, 7);
    emit('date-change', newDate);
}
</script>

<style lang="scss" scoped>
@import './DatePicker.scss';
</style>
