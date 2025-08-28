<template>
    <PageLayout>
        <!-- 加载 -->
        <LoadingScreen v-if="isLoading" text="正在加载课表数据..." />

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
                <!-- 日期导航 -->
                <DateNavigator :selected-date="selectedDate" @date-change="onDateChange" />

                <!-- 课表视图 -->
                <ClassTableView :courses="currentCourses" :selected-date="selectedDate" />
            </view>
        </view>
    </PageLayout>
</template>

<script setup>
import { ref, computed } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import LoadingScreen from "../../components/LoadingScreen/LoadingScreen.vue";
import DateNavigator from "./components/DateNavigator.vue";
import ClassTableView from "./components/ClassTableView.vue";

const isLoading = ref(true);
const selectedDate = ref(new Date().toISOString().split('T')[0]); // 默认今天
const coursesData = ref({}); // 缓存不同日期的课程数据

// 当前选中日期的课程
const currentCourses = computed(() => {
    return coursesData.value[selectedDate.value] || [];
});

onLoad(() => {
    if (!ensureLogin()) return;
    uni.setNavigationBarTitle({ title: "课程表" });
    fetchTodayCourses();
});

onShow(() => {
    if (!ensureLogin()) return;
});

function ensureLogin() {
    const token = uni.getStorageSync("token");
    if (!token) {
        uni.showToast({ title: "请先登录", icon: "none" });
        uni.reLaunch({ url: "/pages/index/index" });
        return false;
    }
    return true;
}

// 日期变化事件
async function onDateChange(newDate) {
    selectedDate.value = newDate;

    // 如果该日期的数据不存在，则获取
    if (!coursesData.value[newDate]) {
        await fetchCoursesByDate(newDate);
    }

    // 预加载相邻日期的数据（异步进行，不阻塞当前操作）
    setTimeout(() => {
        preloadAdjacentDates(newDate);
    }, 500);
}

// 获取今日课程
async function fetchTodayCourses() {
    isLoading.value = true;
    const token = uni.getStorageSync("token");
    const baseURL = getApp().globalData.apiBaseURL;

    try {
        const { statusCode, data: res } = await uni.request({
            url: `${baseURL}/api/v1/classtable/today`,
            method: "GET",
            header: { Authorization: "Bearer " + token },
        });

        if (statusCode === 200 && res.success) {
            const todayDate = res.data.date;
            coursesData.value[todayDate] = res.data.courses || [];
            selectedDate.value = todayDate;

            // 标记今日所在周已加载
            loadedWeeks.add(getWeekKey(todayDate));

            // 异步预加载相邻日期
            setTimeout(() => {
                preloadAdjacentDates(todayDate);
            }, 1000);
        } else if (statusCode === 401) {
            handleAuthError();
        } else {
            uni.showToast({
                title: res.detail || res.message || "获取课程表失败",
                icon: "none"
            });
        }
    } catch (e) {
        console.error("获取今日课程失败", e);
        uni.showToast({ title: "网络连接失败", icon: "none" });
    } finally {
        isLoading.value = false;
    }
}

// 根据日期获取课程（批量获取一周的数据）
async function fetchCoursesByDate(date) {
    // 检查是否已经在加载该周的数据
    const weekKey = getWeekKey(date);
    if (loadingWeeks.has(weekKey)) {
        return;
    }

    const token = uni.getStorageSync("token");
    const baseURL = getApp().globalData.apiBaseURL;

    try {
        loadingWeeks.add(weekKey);
        uni.showLoading({ title: "加载中..." });

        const { statusCode, data: res } = await uni.request({
            url: `${baseURL}/api/v1/classtable/week`,
            method: "GET",
            header: { Authorization: "Bearer " + token },
            data: { query_date: date }
        });

        if (statusCode === 200 && res.success) {
            // 处理周课程表数据
            if (res.data && res.data.days) {
                res.data.days.forEach(day => {
                    coursesData.value[day.date] = day.courses || [];
                });

                // 标记该周已加载
                loadedWeeks.add(weekKey);
            }
        } else if (statusCode === 401) {
            handleAuthError();
        } else {
            uni.showToast({
                title: res.detail || res.message || "获取课程表失败",
                icon: "none"
            });
        }
    } catch (e) {
        console.error("获取课程失败", e);
        uni.showToast({ title: "网络连接失败", icon: "none" });
    } finally {
        uni.hideLoading();
        loadingWeeks.delete(weekKey);
    }
}

// 批量预加载相邻日期的课程数据
async function preloadAdjacentDates(centerDate) {
    const dates = [];
    const center = new Date(centerDate);

    // 预加载前后各3天的数据（如果尚未加载）
    for (let i = -3; i <= 3; i++) {
        const date = new Date(center);
        date.setDate(center.getDate() + i);
        const dateStr = date.toISOString().split('T')[0];
        const weekKey = getWeekKey(dateStr);

        if (!loadedWeeks.has(weekKey) && !coursesData.value[dateStr]) {
            dates.push(dateStr);
        }
    }

    // 去重并批量加载
    const uniqueWeeks = [...new Set(dates.map(date => getWeekKey(date)))];
    for (const weekKey of uniqueWeeks) {
        const sampleDate = dates.find(date => getWeekKey(date) === weekKey);
        if (sampleDate) {
            await fetchCoursesByDate(sampleDate);
        }
    }
}

// 获取日期所在周的标识符
function getWeekKey(dateStr) {
    const date = new Date(dateStr);
    const startOfWeek = new Date(date);
    const day = date.getDay();
    const diff = date.getDate() - day + (day === 0 ? -6 : 1); // 周一作为一周的开始
    startOfWeek.setDate(diff);
    return startOfWeek.toISOString().split('T')[0];
}

// 添加加载状态跟踪
const loadingWeeks = new Set();
const loadedWeeks = new Set();

// 处理认证错误
function handleAuthError() {
    uni.removeStorageSync("token");
    uni.showToast({ title: "登录已过期，请重新登录", icon: "none" });
    setTimeout(() => uni.reLaunch({ url: "/pages/index/index" }), 1500);
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
        transform: translateY(0) rotate(0);
    }

    50% {
        transform: translateY(-20rpx) rotate(180deg);
    }
}

/* 页面头部 */
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
</style>