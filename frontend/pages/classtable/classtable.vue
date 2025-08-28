<template>
    <PageLayout>
        <!-- 加载 -->
        <LoadingScreen v-if="isLoading" text="正在加载课程表数据..." />

        <!-- 内容 -->
        <view v-else class="page-container page-rounded-container">
            <!-- 背景装饰（系统统一） -->
            <view class="background-decoration">
                <view class="circle circle-1"></view>
                <view class="circle circle-2"></view>
                <view class="circle circle-3"></view>
            </view>

            <!-- 页面头部 -->
            <view class="page-header">
                <view class="header-content">
                    <text class="page-title">课程表</text>
                    <text class="page-subtitle">Class Schedule</text>
                </view>
            </view>

            <view class="content-wrapper">
                <!-- 简易日期导航 -->
                <view class="simple-date-nav">
                    <button class="nav-btn" @click="goToPreviousDay">
                        <uni-icons type="left" size="20" color="#495057" />
                    </button>

                    <view class="date-info">
                        <view class="main-date">{{ formatDisplayDate.month }}月{{ formatDisplayDate.day }}日</view>
                        <view class="sub-date">{{ formatDisplayDate.weekDay }} • {{ formatDisplayDate.year }}</view>
                    </view>

                    <button class="nav-btn" @click="goToNextDay">
                        <uni-icons type="right" size="20" color="#495057" />
                    </button>
                </view>

                <!-- 网络错误状态 -->
                <EmptyState v-if="error && !classTableData" icon-type="wifi-off" title="加载失败" :description="error"
                    :show-retry="true" @retry="retryFetch" />

                <!-- 课程表内容 -->
                <DaySchedule v-else :selected-date="selectedDate" :courses="classTableData?.courses || []"
                    :time-slots="classTableData?.time_slots || []" :loading="isLoading" @course-click="onCourseClick" />

                <!-- 数据统计卡片（可选显示） -->
                <ModernCard v-if="showStats && classTableData?.stats" title="本周统计" class="stats-card">
                    <view class="stats-grid">
                        <view class="stat-item">
                            <text class="stat-value">{{ classTableData.stats.total_courses }}</text>
                            <text class="stat-label">总课程数</text>
                        </view>
                        <view class="stat-item">
                            <text class="stat-value">{{ classTableData.stats.total_hours }}</text>
                            <text class="stat-label">总学时</text>
                        </view>
                    </view>
                </ModernCard>
            </view>
        </view>

        <!-- 课程详情弹窗 -->
        <view v-if="selectedCourse" class="course-detail-modal" :class="{ show: modalVisible }"
            @click="closeCourseDetail">
            <view class="modal-content" :class="{ show: modalVisible }" @click.stop>
                <view class="modal-header">
                    <text class="modal-title">{{ selectedCourse.name }}</text>
                    <button class="modal-close" @click="closeCourseDetail">
                        <uni-icons type="closeempty" size="20" color="#6c757d" />
                    </button>
                </view>

                <view class="modal-body">
                    <view class="detail-section">
                        <view class="section-title">课程信息</view>
                        <view class="detail-row">
                            <text class="label">上课地点：</text>
                            <text class="value">{{ selectedCourse.location }}</text>
                        </view>
                        <view class="detail-row">
                            <text class="label">课程类型：</text>
                            <text class="value">{{ selectedCourse.course_type }}</text>
                        </view>
                        <view class="detail-row">
                            <text class="label">学分：</text>
                            <text class="value">{{ selectedCourse.credits }}</text>
                        </view>
                        <view v-if="selectedCourse.class_name" class="detail-row">
                            <text class="label">上课班级：</text>
                            <text class="value">{{ selectedCourse.class_name }}</text>
                        </view>
                    </view>

                    <view v-if="selectedCourse.time_info" class="detail-section">
                        <view class="section-title">时间安排</view>
                        <view class="detail-row">
                            <text class="label">上课时间：</text>
                            <text class="value">{{ selectedCourse.time_info.weekday_name }} {{
                                selectedCourse.time_info.period_name }}</text>
                        </view>
                        <view class="detail-row">
                            <text class="label">具体时段：</text>
                            <text class="value">{{ selectedCourse.time_info.start_time }} - {{
                                selectedCourse.time_info.end_time }}</text>
                        </view>
                        <view class="detail-row">
                            <text class="label">上课周次：</text>
                            <text class="value">第{{ selectedCourse.weeks?.join('、') || '未知' }}周</text>
                        </view>
                    </view>
                </view>

                <view class="modal-footer">
                    <button class="modal-btn" @click="closeCourseDetail">确定</button>
                </view>
            </view>
        </view>
    </PageLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import ModernCard from "../../components/ModernCard/ModernCard.vue";
import LoadingScreen from "../../components/LoadingScreen/LoadingScreen.vue";
import EmptyState from "../../components/EmptyState/EmptyState.vue";

import DaySchedule from "./DaySchedule.vue";
import {
    fetchClassTable,
    getCachedClassTable,
    setCachedClassTable,
    isSameWeek
} from "./api.js";

// 响应式数据
const isLoading = ref(true);
const classTableData = ref(null);
const error = ref('');
const selectedDate = ref(formatDateToString(new Date()));
const selectedCourse = ref(null);
const modalVisible = ref(false);
const showStats = ref(false);

// 缓存相关状态
const lastRequestDate = ref(null); // 记录上次请求的日期

// 计算属性
const hasData = computed(() => !!classTableData.value);

// 解析日期字符串为Date对象
function parseDate(dateStr) {
    if (!dateStr) return new Date();
    const parts = dateStr.split('-');
    if (parts.length !== 3) return new Date();
    return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
}

// 获取星期名称
function getWeekDay(date) {
    const weekDays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
    return weekDays[date.getDay()];
}

// 格式化显示日期
const formatDisplayDate = computed(() => {
    const date = parseDate(selectedDate.value);
    return {
        year: date.getFullYear(),
        month: date.getMonth() + 1,
        day: date.getDate(),
        weekDay: getWeekDay(date)
    };
});

// 格式化日期为字符串
function formatDateToString(date) {
    if (typeof date === 'string') {
        return date;
    }
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// 页面生命周期
onLoad(() => {
    if (!ensureLogin()) return;
    uni.setNavigationBarTitle({ title: "课程表" });
    fetchData();
});

onShow(() => {
    if (!ensureLogin()) return;
    // 如果是今天且数据可能过期，重新获取
    const today = formatDateToString(new Date());
    if (selectedDate.value === today && classTableData.value) {
        const cacheTime = classTableData.value.processed_at;
        if (cacheTime && Date.now() - new Date(cacheTime).getTime() > 5 * 60 * 1000) {
            fetchData(false); // 静默刷新
        }
    }
});

// 组件生命周期
onMounted(() => {
    // 可以添加一些初始化逻辑
});

onUnmounted(() => {
    // 清理资源
});

// 登录检查
function ensureLogin() {
    const token = uni.getStorageSync("token");
    if (!token) {
        uni.showToast({ title: "请先登录", icon: "none" });
        uni.reLaunch({ url: "/pages/index/index" });
        return false;
    }
    return true;
}

// 获取课程表数据 - 智能缓存版本
async function fetchData(showLoading = true, forceRefresh = false) {
    if (showLoading) {
        isLoading.value = true;
    }
    error.value = '';

    try {
        // 检查是否需要从API获取数据
        let needApiRequest = forceRefresh;

        if (!forceRefresh) {
            // 检查是否有可用缓存
            const cachedData = getCachedClassTable(selectedDate.value);

            if (cachedData) {
                console.log(`使用缓存数据，日期: ${selectedDate.value}`);
                classTableData.value = cachedData;
                lastRequestDate.value = selectedDate.value;

                if (showLoading) {
                    isLoading.value = false;
                }
                return;
            }

            // 检查是否与上次请求在同一周
            if (lastRequestDate.value && isSameWeek(selectedDate.value, lastRequestDate.value)) {
                console.log(`在同一周内切换日期，不需要重新请求: ${selectedDate.value}`);
                // 如果当前已有数据，直接使用
                if (classTableData.value) {
                    if (showLoading) {
                        isLoading.value = false;
                    }
                    return;
                }
            }

            needApiRequest = true;
        }

        if (needApiRequest) {
            // 从API获取数据
            console.log(`从API获取课程表数据: ${selectedDate.value}`);
            const data = await fetchClassTable(selectedDate.value);

            classTableData.value = data;
            lastRequestDate.value = selectedDate.value;

            // 缓存数据
            setCachedClassTable(selectedDate.value, data);

            console.log('课程表数据加载成功', data);
        }

    } catch (e) {
        console.error("获取课程表失败", e);
        error.value = e.message || "获取课程表失败";

        // 如果有缓存数据，显示缓存数据但提示错误
        const cachedData = getCachedClassTable(selectedDate.value);
        if (cachedData) {
            classTableData.value = cachedData;
            lastRequestDate.value = selectedDate.value;
            uni.showToast({
                title: "网络错误，已显示缓存数据",
                icon: "none",
                duration: 2000
            });
        } else {
            classTableData.value = null;
            if (showLoading) {
                uni.showToast({ title: error.value, icon: "none" });
            }
        }
    } finally {
        if (showLoading) {
            isLoading.value = false;
        }
    }
}

// 重试获取数据 - 强制刷新
function retryFetch() {
    fetchData(true, true);
}

// 前一天
function goToPreviousDay() {
    const current = parseDate(selectedDate.value);
    current.setDate(current.getDate() - 1);
    selectedDate.value = formatDateToString(current);
    fetchData();
}

// 后一天
function goToNextDay() {
    const current = parseDate(selectedDate.value);
    current.setDate(current.getDate() + 1);
    selectedDate.value = formatDateToString(current);
    fetchData();
}

// 课程点击处理
function onCourseClick(event) {
    console.log('课程点击:', event);
    selectedCourse.value = event.course;

    // 延迟显示弹窗，创建入场动画效果
    setTimeout(() => {
        modalVisible.value = true;
    }, 10);
}

// 关闭课程详情
function closeCourseDetail() {
    // 先触发退场动画
    modalVisible.value = false;

    // 延迟移除元素，等待动画完成
    setTimeout(() => {
        selectedCourse.value = null;
    }, 300);
}

// 切换统计显示
function toggleStats() {
    showStats.value = !showStats.value;
}
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

/* 最外层容器统一 */
.page-container {
    min-height: 100vh;
    background: #f7f8fa;
    position: relative;
    overflow: hidden;
}

.page-rounded-container {
    background: #ffffff;
    border-radius: 40rpx;
    padding: 20rpx 20rpx 30rpx;
    box-shadow: 0 20rpx 60rpx var(--shadow-light);
    border: 1rpx solid var(--border-light);
}

/* 背景装饰统一 */
.background-decoration {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
}

.circle {
    position: absolute;
    border-radius: 50%;
    background: rgba(127, 69, 21, 0.06);

    &.circle-1 {
        width: 200rpx;
        height: 200rpx;
        top: 10%;
        right: -50rpx;
        animation: float 6s ease-in-out infinite;
    }

    &.circle-2 {
        width: 150rpx;
        height: 150rpx;
        bottom: 20%;
        left: -30rpx;
        animation: float 8s ease-in-out infinite reverse;
    }

    &.circle-3 {
        width: 100rpx;
        height: 100rpx;
        top: 30%;
        left: 20%;
        animation: float 4s ease-in-out infinite;
    }
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0) rotate(0)
    }

    50% {
        transform: translateY(-20rpx) rotate(180deg)
    }
}

/* 页面头部（可选） */
.page-header {
    padding: 40rpx 30rpx 30rpx;
    position: relative;
    z-index: 1;
}

.header-content {
    text-align: center;
}

.page-title {
    display: block;
    font-size: 44rpx;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 12rpx;
    letter-spacing: 1rpx;
}

.page-subtitle {
    display: block;
    font-size: 24rpx;
    color: #7f8c8d;
    font-style: italic;
}

/* 主体内容容器 */
.content-wrapper {
    padding: 0 30rpx 30rpx;
    position: relative;
    z-index: 1;
}

/* 卡片内常用区块 */
.card-section {
    display: flex;
    flex-direction: column;
    gap: 8rpx;
}

.section-title {
    font-size: 28rpx;
    font-weight: 700;
    color: var(--text-primary);
}

.section-desc {
    font-size: 24rpx;
    color: var(--text-secondary);
}

/* 统一按钮样式（与现有页面一致） */
.button-group {
    display: flex;
    gap: 24rpx;
}

.action-btn {
    flex: 1;
    height: 72rpx;
    border-radius: 9999rpx;
    font-size: 26rpx;
    padding: 16rpx 24rpx;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12rpx;
    border: none;
    transition: all .3s;

    &::after {
        border: none;
    }

    &:active {
        transform: scale(0.95);
    }

    text {
        font-weight: inherit;
    }
}

.primary-btn {
    background: linear-gradient(135deg, #7f4515, #8c5527);
    color: #fff;
    box-shadow: 0 8rpx 24rpx rgba(127, 69, 21, .25);

    &:disabled {
        background: #adb5bd;
        color: #6c757d;
        box-shadow: none;
    }
}

.secondary-btn {
    background: #f8f9fa;
    color: var(--text-primary);
    border: 2rpx solid #e9ecef;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, .05);

    &:active {
        background: #e9ecef;
        border-color: #dee2e6;
    }
}

/* 统计卡片样式 */
.stats-card {
    margin-top: 24rpx;
}

.stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32rpx;
    padding: 8rpx 0;
}

.stat-item {
    text-align: center;

    .stat-value {
        display: block;
        font-size: 36rpx;
        font-weight: 700;
        color: #7f4515;
        margin-bottom: 8rpx;
    }

    .stat-label {
        font-size: 22rpx;
        color: #6c757d;
    }
}

/* 课程详情弹窗样式 */
.course-detail-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40rpx;
    transition: all 0.3s ease;
    opacity: 0;

    &.show {
        background: rgba(0, 0, 0, 0.5);
        opacity: 1;
    }
}

.modal-content {
    background: #ffffff;
    border-radius: 24rpx;
    width: 100%;
    max-width: 640rpx;
    max-height: 80vh;
    overflow: hidden;
    box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.3);
    transform: scale(0.7) translateY(50rpx);
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    opacity: 0;

    &.show {
        transform: scale(1) translateY(0);
        opacity: 1;
    }
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 32rpx 32rpx 24rpx;
    border-bottom: 1rpx solid #f0f0f0;

    .modal-title {
        font-size: 32rpx;
        font-weight: 700;
        color: #2c3e50;
        flex: 1;
        margin-right: 20rpx;
    }

    .modal-close {
        width: 48rpx;
        height: 48rpx;
        border-radius: 50%;
        background: #f8f9fa;
        border: none;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;

        &::after {
            border: none;
        }

        &:active {
            background: #e9ecef;
            transform: scale(0.95);
        }

        &:hover {
            background: #e9ecef;
        }
    }
}

.modal-body {
    padding: 32rpx;
    max-height: 60vh;
    overflow-y: auto;
}

.detail-section {
    margin-bottom: 32rpx;

    &:last-child {
        margin-bottom: 0;
    }

    .section-title {
        font-size: 26rpx;
        font-weight: 700;
        color: #7f4515;
        margin-bottom: 20rpx;
        padding-bottom: 12rpx;
        border-bottom: 2rpx solid #f0f0f0;
    }
}

.detail-row {
    display: flex;
    align-items: flex-start;
    margin-bottom: 16rpx;

    &:last-child {
        margin-bottom: 0;
    }

    .label {
        width: 140rpx;
        font-size: 24rpx;
        color: #6c757d;
        font-weight: 600;
        flex-shrink: 0;
    }

    .value {
        font-size: 24rpx;
        color: #2c3e50;
        line-height: 1.5;
        flex: 1;
    }
}

.modal-footer {
    padding: 24rpx 32rpx 32rpx;
    border-top: 1rpx solid #f0f0f0;

    .modal-btn {
        width: 100%;
        height: 72rpx;
        background: linear-gradient(135deg, #7f4515, #8c5527);
        color: #ffffff;
        border: none;
        border-radius: 16rpx;
        font-size: 26rpx;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 4rpx 12rpx rgba(127, 69, 21, 0.25);

        &::after {
            border: none;
        }

        &:active {
            transform: scale(0.98);
            box-shadow: 0 2rpx 8rpx rgba(127, 69, 21, 0.3);
        }

        &:hover {
            transform: translateY(-2rpx);
            box-shadow: 0 6rpx 16rpx rgba(127, 69, 21, 0.3);
        }
    }
}

/* 简易日期导航样式 */
.simple-date-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #ffffff;
    border-radius: 20rpx;
    padding: 24rpx;
    margin-bottom: 24rpx;
    box-shadow: 0 8rpx 32rpx rgba(127, 69, 21, 0.08);
    border: 1rpx solid #f0f0f0;
    position: relative;
    overflow: hidden;

    &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4rpx;
        background: linear-gradient(135deg, #7f4515, #8c5527);
    }
}

.nav-btn {
    width: 64rpx;
    height: 64rpx;
    border-radius: 50%;
    background: #f8f9fa;
    border: 2rpx solid #e9ecef;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;

    &::after {
        border: none;
    }

    &:active {
        transform: scale(0.95);
        background: #e9ecef;
    }
}

.date-info {
    flex: 1;
    text-align: center;
    padding: 0 20rpx;
}

.main-date {
    font-size: 32rpx;
    font-weight: 700;
    color: #2c3e50;
    line-height: 1.2;
    margin-bottom: 8rpx;
}

.sub-date {
    font-size: 24rpx;
    color: #7f8c8d;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8rpx;
}
</style>