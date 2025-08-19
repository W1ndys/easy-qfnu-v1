<template>
  <view class="container">
    <view v-if="isLoading" class="loading-container">
      <uni-load-more
        status="loading"
        :show-text="true"
        content-text="正在加载课表..."></uni-load-more>
    </view>

    <view v-else>
      <view v-if="schedule.length === 0" class="empty-container">
        <uni-icons type="info-filled" size="60" color="#999"></uni-icons>
        <text class="empty-text">没有查询到任何课表信息</text>
      </view>

      <uni-card
        v-for="(day, idx) in schedule"
        :key="day.weekday"
        :title="day.weekday"
        margin="12px 0">
        <uni-list>
          <uni-list-item
            v-for="course in day.courses"
            :key="course.courseCode"
            :title="course.courseName"
            :note="`时间: ${course.time} | 地点: ${course.location}`"
            :right-text="course.teacher"></uni-list-item>
        </uni-list>
      </uni-card>
    </view>
  </view>
</template>

<script setup>
import { ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";

// --- 页面数据 ---
const isLoading = ref(true); // 页面初始为加载状态
const schedule = ref([]); // 用于存放课表数据

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
      url: "http://127.0.0.1:8000/api/v1/schedule",
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
.container {
  padding: 20rpx;
  background-color: #f7f8fa;
  min-height: 100vh;
}

.loading-container {
  padding-top: 200rpx;
}

.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 200rpx;
  color: #999;
}
.empty-text {
  margin-top: 20rpx;
  font-size: 28rpx;
}

// 深度修改 uni-list-item 的样式
:deep(.uni-list-item__content-title) {
  font-size: 30rpx !important;
  color: #333 !important;
}
:deep(.uni-list-item__content-note) {
  font-size: 24rpx !important;
  color: #999 !important;
}
:deep(.uni-list-item__extra-text) {
  font-size: 28rpx !important;
  color: #07c160 !important;
}
</style>
