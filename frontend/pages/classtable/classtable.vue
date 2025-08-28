<template>
	<PageLayout>
		<!-- 加载 -->
		<LoadingScreen v-if="isLoading" text="正在加载课程表..." />

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
				<!-- 空状态 -->
				<EmptyState v-if="!hasData" icon-type="calendar" title="暂无课程表数据" description="请检查网络或稍后重试"
					:show-retry="true" @retry="fetchClassTable" />

				<!-- 业务内容 -->
				<view v-else>
					<!-- 日期选择器 -->
					<DatePicker :current-date="currentDate" :week-info="classTableData.week_info"
						@date-change="handleDateChange" />

					<!-- 统计信息 -->
					<StatsCard :stats="classTableData.stats" />

					<!-- 课程表 -->
					<WeeklyTable :time-slots="classTableData.time_slots" :weekdays="classTableData.weekdays"
						:courses="classTableData.courses" />
				</view>
			</view>
		</view>
	</PageLayout>
</template>

<script setup>
import { ref, computed } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import LoadingScreen from "../../components/LoadingScreen/LoadingScreen.vue";
import EmptyState from "../../components/EmptyState/EmptyState.vue";
import DatePicker from "./DatePicker/DatePicker.vue";
import StatsCard from "./StatsCard/StatsCard.vue";
import WeeklyTable from "./WeeklyTable/WeeklyTable.vue";
import { classTableService } from "./services/classTableService.js";
import { formatDate } from "./utils/dateUtils.js";

const isLoading = ref(true);
const classTableData = ref(null);
const currentDate = ref(formatDate(new Date()));

const hasData = computed(() => !!classTableData.value);

onLoad(() => {
	if (!ensureLogin()) return;
	uni.setNavigationBarTitle({ title: "课程表" });
	fetchClassTable();
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

async function fetchClassTable(date = currentDate.value) {
	isLoading.value = true;

	try {
		const result = await classTableService.getClassTable(date);
		classTableData.value = result;
	} catch (error) {
		console.error("获取课程表失败", error);
		uni.showToast({ title: error.message || "获取课程表失败", icon: "none" });
		classTableData.value = null;
	} finally {
		isLoading.value = false;
	}
}

function handleDateChange(newDate) {
	currentDate.value = newDate;
	fetchClassTable(newDate);
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
	display: flex;
	flex-direction: column;
	gap: 30rpx;
}
</style>