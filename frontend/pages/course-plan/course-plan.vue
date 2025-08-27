<template>
  <PageLayout>
    <LoadingScreen v-if="isLoading" text="正在获取培养方案..." />

    <view v-else class="page-rounded-container">
      <EmptyState v-if="modules.length === 0" icon-type="info-filled" title="暂无培养方案数据" description="请稍后重试或下拉刷新"
        :show-retry="true" @retry="fetchCoursePlan" />

      <view v-else>
        <DataStatusCard :data-source="dataSource" :updated-at="updatedAt" :is-refreshing="isRefreshing"
          @refresh="refreshCache" />

        <EnrollmentSettings :enrollment-year="enrollmentYear" :current-semester="currentSemester"
          @year-change="onYearChange" />

        <TotalProgressCard :modules="modules" />

        <ModuleList :modules="modules" :current-semester="currentSemester" @copy-course-code="copyCourseCode" />
      </view>
    </view>

    <NoticeModal :visible="showNoticeModal" @close="closeModal" @confirm="handleConfirm" />
  </PageLayout>
</template>

<script setup>
import { ref, computed } from "vue";
import { onLoad, onShow, onPullDownRefresh } from "@dcloudio/uni-app";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import LoadingScreen from "../../components/LoadingScreen/LoadingScreen.vue";
import EmptyState from "../../components/EmptyState/EmptyState.vue";
import DataStatusCard from "./DataStatusCard.vue";
import EnrollmentSettings from "./EnrollmentSettings.vue";
import TotalProgressCard from "./TotalProgressCard.vue";
import ModuleList from "./ModuleList.vue";
import NoticeModal from "./NoticeModal.vue";

const isLoading = ref(true);
const modules = ref([]);
const showNoticeModal = ref(false);

// 学籍与学期状态
const enrollmentYear = ref(null);
const currentSemester = ref(null);

const dataSource = ref("cache");
const updatedAt = ref("");
const isRefreshing = ref(false);

onLoad(async () => {
  const savedYear = uni.getStorageSync("enrollmentYear");
  if (savedYear) {
    enrollmentYear.value = savedYear;
    await fetchCurrentSemester(savedYear);
  }
  checkLoginAndFetch();
});

onShow(() => {
  const token = uni.getStorageSync("token");
  if (!token) {
    uni.showToast({ title: "请先登录", icon: "none" });
    uni.reLaunch({ url: "/pages/index/index" });
  }
});

onPullDownRefresh(async () => {
  const token = uni.getStorageSync("token");
  if (!token) {
    uni.showToast({ title: "请先登录", icon: "none" });
    uni.reLaunch({ url: "/pages/index/index" });
    uni.stopPullDownRefresh();
    return;
  }
  await refreshCache(true);
  uni.stopPullDownRefresh();
});

const checkLoginAndFetch = () => {
  const token = uni.getStorageSync("token");
  if (!token) {
    uni.showToast({ title: "请先登录", icon: "none" });
    uni.reLaunch({ url: "/pages/index/index" });
    return;
  }
  fetchCoursePlan();
};

const fetchCurrentSemester = async (year) => {
  if (!year) {
    currentSemester.value = null;
    return;
  }
  try {
    const token = uni.getStorageSync("token");
    const res = await uni.request({
      url: `${getApp().globalData.apiBaseURL}/api/v1/semester-info/${year}`,
      method: "GET",
      header: { Authorization: "Bearer " + token },
    });
    if (res.statusCode === 200 && res.data?.success) {
      currentSemester.value = res.data.data.current_semester;
    } else {
      throw new Error(res.data?.message || "获取学期信息失败");
    }
  } catch (err) {
    console.error("获取当前学期失败", err);
    uni.showToast({ title: err.message || "获取学期信息失败", icon: "none" });
    currentSemester.value = null;
  }
};

const fetchCoursePlan = async () => {
  const token = uni.getStorageSync("token");
  if (!token) {
    uni.showToast({ title: "请先登录", icon: "none" });
    uni.reLaunch({ url: "/pages/index/index" });
    return;
  }

  isLoading.value = true;
  try {
    const res = await uni.request({
      url: `${getApp().globalData.apiBaseURL}/api/v1/course-plan`,
      method: "GET",
      header: { Authorization: "Bearer " + token },
    });

    let payload = null;
    if (res.statusCode === 200) {
      if (res.data?.success) {
        payload = res.data.data;
        dataSource.value = res.data.source || "cache";
        updatedAt.value = res.data.updated_at || "";
        if (dataSource.value === "live" && !isRefreshing.value) {
          uni.showToast({ title: "已获取最新数据", icon: "success", duration: 2000 });
        }
      } else {
        payload = res.data;
      }
    } else if (res.statusCode === 401) {
      uni.removeStorageSync("token");
      uni.showToast({ title: "登录已过期，请重新登录", icon: "none" });
      setTimeout(() => uni.reLaunch({ url: "/pages/index/index" }), 1500);
      return;
    } else {
      const errorDetail = res.data?.detail || res.data?.message || "未知错误";
      throw new Error(`请求错误：${res.statusCode} - ${errorDetail}`);
    }

    if (!payload || !Array.isArray(payload.modules)) {
      uni.showToast({ title: "培养方案格式异常", icon: "none" });
      modules.value = [];
      return;
    }

    modules.value = payload.modules;

    if (modules.value.length > 0) {
      checkShowNotice();
    }
  } catch (err) {
    console.error("获取培养方案失败", err);
    uni.showToast({
      title: err.message || "获取培养方案失败，请稍后重试",
      icon: "none",
      duration: 2000,
    });
  } finally {
    isLoading.value = false;
  }
};

const refreshCache = async (isPullDown = false) => {
  const token = uni.getStorageSync("token");
  if (!token) {
    uni.showToast({ title: "请先登录", icon: "none" });
    uni.reLaunch({ url: "/pages/index/index" });
    return;
  }

  isRefreshing.value = true;
  if (!isPullDown) isLoading.value = true;

  try {
    const refreshRes = await uni.request({
      url: `${getApp().globalData.apiBaseURL}/api/v1/course-plan/refresh`,
      method: "POST",
      header: { Authorization: "Bearer " + token },
    });

    if (refreshRes.statusCode === 200 && refreshRes.data?.success) {
      await fetchCoursePlan();
      uni.showToast({ title: "数据已刷新", icon: "success", duration: 2000 });
    } else if (refreshRes.statusCode === 401) {
      uni.removeStorageSync("token");
      uni.showToast({ title: "登录已过期，请重新登录", icon: "none" });
      setTimeout(() => uni.reLaunch({ url: "/pages/index/index" }), 1500);
    } else {
      throw new Error(refreshRes.data?.detail || refreshRes.data?.message || "刷新失败");
    }
  } catch (err) {
    console.error("刷新缓存失败", err);
    uni.showToast({
      title: err.message || "刷新失败，请稍后重试",
      icon: "none",
      duration: 2000,
    });
  } finally {
    isRefreshing.value = false;
    if (!isPullDown) isLoading.value = false;
  }
};

const checkShowNotice = () => {
  setTimeout(() => {
    showNoticeModal.value = true;
  }, 500);
};

const copyCourseCode = (code) => {
  if (!code) return;
  uni.setClipboardData({
    data: code,
    success: () => uni.showToast({ title: "课程代码已复制", icon: "none" }),
  });
};

const onYearChange = async (newYear) => {
  enrollmentYear.value = newYear;
  uni.setStorageSync("enrollmentYear", newYear);
  await fetchCurrentSemester(newYear);
  uni.showToast({ title: `学籍已设置为 ${newYear} 级`, icon: "none" });
};

const handleConfirm = () => {
  showNoticeModal.value = false;
};
const closeModal = () => {
  showNoticeModal.value = false;
};
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

.page-rounded-container {
  background: linear-gradient(180deg, #ffffff 0%, #fafbfc 100%);
  border-radius: 20rpx;
  padding: 16rpx 12rpx;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.08);
  border: 1rpx solid #e8e8e8;
  margin: 6rpx;
}

/* 全局卡片样式 */
.settings-card,
.data-status-card,
.total-progress-card {
  margin-bottom: 12rpx;
}
</style>
