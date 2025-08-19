<template>
  <PageLayout>
    <!-- 加载状态 -->
    <LoadingScreen v-if="isLoading" text="正在加载课表..." />

    <!-- 内容区域 -->
    <view v-else>
      <!-- 空状态 -->
      <EmptyState
        v-if="schedule.length === 0"
        icon-type="calendar"
        title="没有查询到任何课表信息"
        description="请检查当前学期是否有课程安排"
        :show-retry="true"
        @retry="fetchSchedule" />

      <!-- 有数据时显示 -->
      <view v-else>
        <!-- 课表概览卡片 -->
        <ModernCard title="课表概览" highlight class="overview-card">
          <view class="overview-stats">
            <view class="stat-item">
              <view class="stat-value">{{ totalDays }}</view>
              <view class="stat-label">有课天数</view>
            </view>
            <view class="stat-item">
              <view class="stat-value">{{ totalCourses }}</view>
              <view class="stat-label">总课程数</view>
            </view>
            <view class="stat-item">
              <view class="stat-value">{{ currentWeek }}</view>
              <view class="stat-label">当前周次</view>
            </view>
          </view>
        </ModernCard>

        <!-- 课表列表 -->
        <ScheduleList :schedule="schedule" />
      </view>
    </view>
  </PageLayout>
</template>

<script setup>
import { ref, computed } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import LoadingScreen from "../../components/LoadingScreen/LoadingScreen.vue";
import EmptyState from "../../components/EmptyState/EmptyState.vue";
import ModernCard from "../../components/ModernCard/ModernCard.vue";
import ScheduleList from "../../components/ScheduleList/ScheduleList.vue";

// --- 页面数据 ---
const isLoading = ref(true); // 页面初始为加载状态
const schedule = ref([]); // 用于存放课表数据

// 计算属性
const totalDays = computed(() => schedule.value.length);
const totalCourses = computed(() =>
  schedule.value.reduce((total, day) => total + day.courses.length, 0)
);
const currentWeek = computed(() => {
  // 这里可以根据实际情况计算当前周次
  const now = new Date();
  const startOfYear = new Date(now.getFullYear(), 0, 1);
  const weekNumber = Math.ceil((now - startOfYear) / (7 * 24 * 60 * 60 * 1000));
  return weekNumber;
});

// --- 页面生命周期 ---
onLoad(() => {
  fetchSchedule(); // 页面一加载就调用获取课表的函数
});

// --- 核心逻辑函数 ---
const fetchSchedule = async () => {
  const token = uni.getStorageSync("token");
  if (!token) {
    uni.showToast({ title: "请先登录", icon: "none" });
    uni.reLaunch({ url: "/pages/index/index" });
    return;
  }

  isLoading.value = true; // 开始加载

  try {
    // 这里的URL和接口需要根据实际后端API调整
    const res = await uni.request({
      url: "https://api.easy-qfnu.top/api/v1/schedule",
      method: "GET",
      header: {
        Authorization: "Bearer " + token,
      },
    });

    if (res.statusCode === 200 && res.data.success) {
      const rawSchedule = res.data.data;
      // 调用辅助函数，对课表按星期分组
      const groupedSchedule = groupScheduleByWeekday(rawSchedule);
      schedule.value = groupedSchedule;
    } else {
      const errorMessage = res.data.detail || "获取课表失败";
      uni.showToast({ title: errorMessage, icon: "none" });
    }
  } catch (error) {
    console.error("请求失败", error);
    uni.showToast({ title: "服务器连接失败", icon: "none" });
  } finally {
    isLoading.value = false;
  }
};

/**
 * 辅助函数：将平铺的课表列表按星期分组
 * @param {Array} courses - 从后端获取的原始课表数组
 */
const groupScheduleByWeekday = (courses) => {
  if (!courses || courses.length === 0) {
    return [];
  }
  const weekdayMap = {};
  courses.forEach((course) => {
    const weekday = course.weekday; // 假设后端返回 weekday 字段
    if (!weekdayMap[weekday]) {
      weekdayMap[weekday] = [];
    }
    weekdayMap[weekday].push(course);
  });
  // 保证星期顺序
  const weekdayOrder = [
    "星期一",
    "星期二",
    "星期三",
    "星期四",
    "星期五",
    "星期六",
    "星期日",
  ];
  const result = weekdayOrder
    .map((weekday) => {
      return {
        weekday: weekday,
        courses: weekdayMap[weekday] || [],
      };
    })
    .filter((day) => day.courses.length > 0);
  return result;
};
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

.overview-card {
  margin-bottom: 40rpx;
}

.overview-stats {
  display: flex;
  justify-content: space-between;
  gap: 20rpx;
}

.stat-item {
  flex: 1;
  text-align: center;
  padding: 20rpx;
  background: linear-gradient(135deg, rgba(155, 4, 0, 0.05) 0%, rgba(155, 4, 0, 0.1) 100%);
  border-radius: var(--radius-small);
  border: 1rpx solid rgba(155, 4, 0, 0.1);
}

.stat-value {
  font-size: 36rpx;
  font-weight: 700;
  color: #9b0400;
  margin-bottom: 8rpx;
}

.stat-label {
  font-size: 24rpx;
  color: var(--text-secondary);
  font-weight: 500;
}
</style>
