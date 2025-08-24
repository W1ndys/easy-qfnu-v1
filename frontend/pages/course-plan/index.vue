<template>
  <PageLayout>
    <LoadingScreen v-if="isLoading" text="正在获取培养方案..." />

    <view v-else class="page-rounded-container">
      <EmptyState
        v-if="modules.length === 0"
        icon-type="info-filled"
        title="暂无培养方案数据"
        description="请稍后重试或下拉刷新"
        :show-retry="true"
        @retry="fetchCoursePlan"
      />

      <view v-else>
        <ModernCard title="数据状态" class="data-status-card">
          <view class="data-status-container">
            <view class="status-info">
              <view class="status-item">
                <uni-icons
                  type="cloud"
                  size="20"
                  :color="dataSource === 'live' ? '#52c41a' : '#1890ff'"
                />
                <text class="status-label">数据来源:</text>
                <text
                  class="status-value"
                  :class="dataSource === 'live' ? 'status-live' : 'status-cache'"
                >
                  {{ dataSource === "live" ? "实时获取" : "缓存数据" }}
                </text>
              </view>

              <view v-if="updatedAt" class="status-item">
                <uni-icons type="calendar" size="20" color="#666" />
                <text class="status-label">更新时间:</text>
                <text class="status-value">{{ formatUpdateTime(updatedAt) }}</text>
              </view>
            </view>

            <view class="refresh-actions">
              <button
                class="refresh-btn"
                :class="{ loading: isRefreshing }"
                :disabled="isRefreshing"
                @click="refreshCache"
              >
                <uni-icons
                  type="refresh"
                  size="18"
                  color="#1890ff"
                  :class="{ spinning: isRefreshing }"
                />
                <text>{{ isRefreshing ? "刷新中..." : "刷新数据" }}</text>
              </button>
            </view>
          </view>
        </ModernCard>

        <ModernCard title="学籍设置" class="settings-card">
          <view class="enrollment-notice">
            <uni-icons type="info" size="16" color="#1890ff" />
            <text class="notice-text">入伍、留级等学生请选择你所在班级的入学年份</text>
          </view>
          <view class="setting-item">
            <text class="setting-label">入学年份:</text>
            <picker
              mode="selector"
              :range="enrollmentYearRange"
              :value="enrollmentYearIndex"
              @change="onYearChange"
            >
              <view class="picker-value">
                <text>{{ enrollmentYear || "请选择" }}</text>
                <uni-icons type="bottom" size="16" color="#666" />
              </view>
            </picker>
          </view>
          <view class="setting-item">
            <text class="setting-label">当前学期:</text>
            <text class="setting-value">{{
              currentSemester ? `第 ${currentSemester} 学期` : "请先选择入学年份"
            }}</text>
          </view>
        </ModernCard>

        <ModernCard title="总学分进度" class="total-progress-card">
          <view class="total-progress-container">
            <view class="total-header">
              <view class="total-title-section">
                <text class="total-title">培养方案总进度</text>
                <view
                  class="status-chip"
                  :class="
                    isTotalIncomplete ? 'chip-module-incomplete' : 'chip-module-complete'
                  "
                >
                  <text>{{ isTotalIncomplete ? "未修满" : "已修满" }}</text>
                </view>
              </view>

              <view class="total-credits-info">
                <text class="total-credits-text"
                  >{{ formatNumber(totalCompletedCredits) }}/{{
                    formatNumber(totalRequiredCredits)
                  }}
                  学分</text
                >
                <text v-if="isTotalIncomplete" class="total-shortage-text"
                  >差
                  {{ formatNumber(totalRequiredCredits - totalCompletedCredits) }}
                  学分</text
                >
              </view>

              <view class="total-progress-bar-container">
                <view class="progress-bar total-progress-bar">
                  <view
                    class="progress-fill"
                    :style="{ width: totalProgress + '%' }"
                    :class="{ danger: isTotalIncomplete }"
                  ></view>
                </view>
                <text class="progress-text total-progress-text"
                  >{{ totalProgress }}%</text
                >
              </view>
            </view>
          </view>
        </ModernCard>

        <ModernCard title="培养方案模块">
          <view class="modules-list">
            <view
              v-for="(m, idx) in sortedModules"
              :key="m.module_name"
              class="module-card"
              :class="{
                incomplete: isIncomplete(m),
                expanded: expanded[getOriginalIndex(m)],
              }"
            >
              <view class="module-header" @click="toggleModule(getOriginalIndex(m))">
                <view class="header-info">
                  <view class="header-top">
                    <text class="module-title">{{ m.module_name }}</text>
                    <view
                      class="status-chip"
                      :class="
                        isIncomplete(m)
                          ? 'chip-module-incomplete'
                          : 'chip-module-complete'
                      "
                    >
                      <text>{{ isIncomplete(m) ? "未修满" : "已修满" }}</text>
                    </view>
                  </view>

                  <view class="header-middle">
                    <view class="credits-info">
                      <text class="credits-text"
                        >{{ formatNumber(m.completed_credits) }}/{{
                          formatNumber(m.required_credits)
                        }}
                        学分</text
                      >
                      <text class="course-count-text"
                        >共 {{ (m.courses || []).length }} 门课程</text
                      >
                      <text v-if="isIncomplete(m)" class="shortage-text"
                        >差
                        {{
                          formatNumber(
                            Number(m.required_credits) - Number(m.completed_credits)
                          )
                        }}
                        学分</text
                      >
                    </view>

                    <view class="expand-action">
                      <text class="hint-text" v-if="!expanded[getOriginalIndex(m)]"
                        >点击展开</text
                      >
                      <text class="hint-text" v-else>点击收起</text>
                      <uni-icons
                        class="chevron-icon"
                        :class="{ expanded: expanded[getOriginalIndex(m)] }"
                        type="arrowdown"
                        size="20"
                        color="#7F4515"
                      />
                    </view>
                  </view>

                  <view class="progress-container">
                    <view class="progress-bar">
                      <view
                        class="progress-fill"
                        :style="{ width: getProgress(m) + '%' }"
                        :class="{ danger: isIncomplete(m) }"
                      ></view>
                    </view>
                    <text class="progress-text">{{ getProgress(m) }}%</text>
                  </view>
                </view>
              </view>
              <view class="course-details">
                <view v-if="m.subtotal" class="module-subtotal">
                  <text class="subtotal-title">模块要求小计</text>
                  <text class="subtotal-credits"
                    >要求学分 {{ m.subtotal.total_credits }}</text
                  >
                  <text class="subtotal-hours"
                    >要求总学时 {{ m.subtotal.hours?.total || 0 }}</text
                  >

                  <view class="subtotal-divider"></view>

                  <text class="subtotal-title">已修课程小计</text>
                  <view class="subtotal-completed-group">
                    <text class="subtotal-hours">
                      已修总学时 {{ calculateCompletedHours(m).total || 0 }}
                    </text>
                    <template
                      v-for="hourInfo in formatHours(calculateCompletedHours(m))"
                      :key="hourInfo"
                    >
                      <text class="subtotal-meta">{{ hourInfo }}</text>
                    </template>
                  </view>
                </view>

                <view class="course-sort-hint">
                  <text class="sort-hint-text">
                    <uni-icons type="info" size="16" color="#666" />
                    {{
                      isIncomplete(m)
                        ? "未修课程已置顶显示，本学期课程优先"
                        : "已修课程已置顶显示"
                    }}
                  </text>
                </view>
                <view class="course-list">
                  <view
                    v-for="c in m.courses || []"
                    :key="(c.course_code || '') + (c.course_name || '')"
                    class="course-item"
                    :class="{ completed: isCourseCompleted(c) }"
                  >
                    <view class="course-main">
                      <view class="course-title-section">
                        <view class="course-name-wrapper">
                          <text class="course-name">{{ c.course_name }}</text>
                          <text
                            v-if="isCurrentSemesterCourse(c) && !isCourseCompleted(c)"
                            class="current-semester-tag"
                            >本学期可选</text
                          >
                        </view>
                        <text
                          v-if="c.course_code"
                          class="course-code"
                          @click.stop="copyCourseCode(c.course_code)"
                          >代码: {{ c.course_code }}</text
                        >
                      </view>
                      <view class="chips">
                        <text
                          class="chip completion-chip"
                          :class="
                            isCourseCompleted(c) ? 'chip-completed' : 'chip-incomplete'
                          "
                          >{{ c.completion_status || "未修" }}</text
                        >
                        <text v-if="c.course_nature" class="chip chip-neutral">{{
                          c.course_nature
                        }}</text>
                        <text v-if="c.course_attribute" class="chip chip-neutral">{{
                          c.course_attribute
                        }}</text>
                      </view>
                    </view>
                    <view class="course-meta">
                      <text class="meta">学分 {{ c.credits }}</text>
                      <text class="meta" v-if="c.semester">学期 {{ c.semester }}</text>
                      <text class="meta" v-if="c.hours?.total"
                        >总学时 {{ c.hours.total }}</text
                      >
                      <template v-for="hourInfo in formatHours(c.hours)" :key="hourInfo">
                        <text class="meta">{{ hourInfo }}</text>
                      </template>
                    </view>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </ModernCard>
      </view>
    </view>

    <view v-if="showNoticeModal" class="modal-overlay" @click="closeModal">
      <view class="modal-container" @click.stop>
        <view class="modal-header">
          <uni-icons type="info-filled" size="24" color="#1890ff" />
          <text class="modal-title">培养方案说明</text>
        </view>

        <view class="modal-content">
          <text class="notice-text">
            本页面由教务系统培养方案表格直接生成，大部分专业的应修是160或170或175，该培养方案总和大部分都不足够（22级是），少的那些分就是你应该选的公选课的分。如果不够，请及时与对应负责老师沟通。
          </text>
          <text class="notice-text" style="margin-top: 24rpx">
            根据教务处官方规定：培养方案毕业学分原则上145-170学分，其中人文社会科学类专业毕业学分≤160学分，理科类专业毕业学分≤165学分，工科类专业毕业学分≤170学分，辅修学士学位专业毕业学分70学分左右。
          </text>
          <text
            class="notice-text"
            style="margin-top: 16rpx; font-size: 24rpx; color: #8c8c8c"
          >
            来源：https://jwc.qfnu.edu.cn/info/1068/7039.htm
          </text>
        </view>

        <view class="modal-actions">
          <button class="action-btn primary-btn" @click="handleConfirm">我已阅读</button>
        </view>
      </view>
    </view>
  </PageLayout>
</template>

<script setup>
import { ref, computed } from "vue";
import { onLoad, onShow, onPullDownRefresh } from "@dcloudio/uni-app";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import ModernCard from "../../components/ModernCard/ModernCard.vue";
import LoadingScreen from "../../components/LoadingScreen/LoadingScreen.vue";
import EmptyState from "../../components/EmptyState/EmptyState.vue";

const isLoading = ref(true);
const modules = ref([]);
const expanded = ref([]);
const showNoticeModal = ref(false);

// 【清理】不再需要 isAnimating 状态
// const isAnimating = ref(new Set());

// 学籍与学期状态
const enrollmentYear = ref(null);
const currentSemester = ref(null);

const enrollmentYearRange = computed(() => {
  const currentYear = new Date().getFullYear();
  return Array.from({ length: 5 }, (_, i) => String(currentYear - i));
});
const enrollmentYearIndex = computed(() => {
  return enrollmentYearRange.value.indexOf(String(enrollmentYear.value));
});

const dataSource = ref("cache");
const updatedAt = ref("");
const isRefreshing = ref(false);

const sortedModules = computed(() => {
  return [...modules.value]
    .sort((a, b) => {
      const aIncomplete = isIncomplete(a);
      const bIncomplete = isIncomplete(b);
      if (aIncomplete && !bIncomplete) return -1;
      if (!aIncomplete && bIncomplete) return 1;
      return 0;
    })
    .map((module) => {
      const moduleIncomplete = isIncomplete(module);
      return {
        ...module,
        courses: [...(module.courses || [])].sort((a, b) => {
          const aCompleted = isCourseCompleted(a);
          const bCompleted = isCourseCompleted(b);
          if (moduleIncomplete) {
            if (!aCompleted && bCompleted) return -1;
            if (aCompleted && !bCompleted) return 1;
            if (!aCompleted && !bCompleted) {
              const aIsCurrent = isCurrentSemesterCourse(a);
              const bIsCurrent = isCurrentSemesterCourse(b);
              if (aIsCurrent && !bIsCurrent) return -1;
              if (!aIsCurrent && bIsCurrent) return 1;
            }
          } else {
            if (aCompleted && !bCompleted) return -1;
            if (!aCompleted && bCompleted) return 1;
          }
          const semesterA = Number(a.semester) || 0;
          const semesterB = Number(b.semester) || 0;
          if (semesterA !== semesterB) {
            return semesterB - semesterA;
          }
          return 0;
        }),
      };
    });
});

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
    expanded.value = modules.value.map(() => false);

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

const formatUpdateTime = (timeStr) => {
  if (!timeStr) return "未知";
  try {
    const date = new Date(timeStr);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / 86400000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffMinutes = Math.floor(diffMs / 60000);
    if (diffDays > 0) return `${diffDays}天前`;
    if (diffHours > 0) return `${diffHours}小时前`;
    if (diffMinutes > 0) return `${diffMinutes}分钟前`;
    return "刚刚";
  } catch (error) {
    return "未知";
  }
};

const checkShowNotice = () => {
  setTimeout(() => {
    showNoticeModal.value = true;
  }, 500);
};

// 【清理】简化回最原始的 toggleModule
const toggleModule = (index) => {
  expanded.value[index] = !expanded.value[index];
};

const getOriginalIndex = (module) => {
  return modules.value.findIndex((m) => m.module_name === module.module_name);
};

const copyCourseCode = (code) => {
  if (!code) return;
  uni.setClipboardData({
    data: code,
    success: () => uni.showToast({ title: "课程代码已复制", icon: "none" }),
  });
};

const isCourseCompleted = (course) => !!course.completion_status?.includes("已修");

const isCurrentSemesterCourse = (course) => {
  if (!course.semester || !currentSemester.value) return false;
  const courseSemester = Number(course.semester);
  return (
    courseSemester <= currentSemester.value &&
    courseSemester % 2 === currentSemester.value % 2
  );
};

const isIncomplete = (module) => {
  return (
    (Number(module?.completed_credits) || 0) < (Number(module?.required_credits) || 0)
  );
};

const getProgress = (module) => {
  const need = Number(module?.required_credits) || 0;
  const done = Number(module?.completed_credits) || 0;
  if (need <= 0) return 0;
  return Math.min(100, Math.max(0, Math.round((done / need) * 100)));
};

const calculateCompletedHours = (module) => {
  if (!module.courses?.length) return { total: 0 };
  return module.courses.filter(isCourseCompleted).reduce((acc, course) => {
    if (course.hours && typeof course.hours === "object") {
      for (const [key, value] of Object.entries(course.hours)) {
        acc[key] = (acc[key] || 0) + (Number(value) || 0);
      }
    }
    return acc;
  }, {});
};

const formatHours = (hours) => {
  if (!hours || typeof hours !== "object") return [];
  const hourTypes = {
    lecture: "讲授",
    practice: "实践",
    seminar: "研讨",
    experiment: "实验",
    design: "设计",
    computer: "上机",
    discussion: "讨论",
    extracurricular: "课外",
    online: "在线",
  };
  return Object.entries(hours)
    .filter(([key, value]) => key !== "total" && Number(value) > 0)
    .map(([key, value]) => `${hourTypes[key] || key}: ${value}`);
};

const formatNumber = (n) => {
  const v = Number(n);
  if (isNaN(v)) return "0";
  return v % 1 === 0 ? String(v) : v.toFixed(1);
};

const totalRequiredCredits = computed(() =>
  modules.value.reduce((sum, m) => sum + (Number(m.required_credits) || 0), 0)
);
const totalCompletedCredits = computed(() =>
  modules.value.reduce((sum, m) => sum + (Number(m.completed_credits) || 0), 0)
);

const totalProgress = computed(() => {
  if (totalRequiredCredits.value <= 0) return 0;
  return Math.min(
    100,
    Math.max(
      0,
      Math.round((totalCompletedCredits.value / totalRequiredCredits.value) * 100)
    )
  );
});

const isTotalIncomplete = computed(
  () => totalCompletedCredits.value < totalRequiredCredits.value
);

const onYearChange = async (e) => {
  const newYear = enrollmentYearRange.value[e.detail.value];
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

/* ... 其他基础样式保持不变 ... */
.settings-card,
.data-status-card,
.total-progress-card {
  margin-bottom: 12rpx;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8rpx 0;
  font-size: 26rpx;
}

.setting-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.picker-value {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 6rpx 12rpx;
  border: 1rpx solid #d9d9d9;
  border-radius: 8rpx;
  background-color: #fafafa;
  color: var(--text-primary);
}

.setting-value {
  color: var(--text-primary);
  font-weight: 600;
}

.data-status-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12rpx;
  flex-wrap: wrap;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  flex: 1;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 6rpx;
  flex-wrap: wrap;
}

.status-label {
  font-size: 24rpx;
  color: var(--text-secondary);
  font-weight: 500;
}

.status-value {
  font-size: 24rpx;
  font-weight: 600;
  padding: 4rpx 8rpx;
  border-radius: 8rpx;
}

.status-live {
  color: #389e0d;
  background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
  border: 1rpx solid #95de64;
}

.status-cache {
  color: #1890ff;
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  border: 1rpx solid #91d5ff;
}

.refresh-actions {
  flex-shrink: 0;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 6rpx;
  padding: 8rpx 16rpx;
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #1890ff;
  border: 1rpx solid #91d5ff;
  border-radius: 12rpx;
  font-size: 24rpx;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.08);
}

.refresh-btn:not(.loading):active {
  transform: translateY(2rpx);
  box-shadow: 0 1rpx 4rpx rgba(0, 0, 0, 0.1);
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

.modules-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.total-progress-card {
  margin-bottom: 12rpx;
}

.total-progress-container {
  padding: 0;
}

.total-header {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.total-title-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.total-title {
  font-size: 32rpx;
  color: var(--text-primary);
  font-weight: 700;
  line-height: 1.4;
}

.total-credits-info {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  align-items: center;
}

.total-credits-text {
  font-size: 36rpx;
  color: var(--text-primary);
  font-weight: 600;
  text-align: center;
}

.total-shortage-text {
  font-size: 28rpx;
  color: #e74c3c;
  font-weight: 600;
  text-align: center;
}

.total-progress-bar-container {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.total-progress-bar {
  height: 24rpx;
  border-radius: 12rpx;
  box-shadow: inset 0 2rpx 6rpx rgba(0, 0, 0, 0.12);
}

.total-progress-text {
  font-size: 28rpx;
  color: var(--text-primary);
  font-weight: 600;
  min-width: 70rpx;
  text-align: right;
}

/* 【最终修复方案】使用 CSS Grid 动画，彻底替换 max-height 方案 */
.module-card {
  border: 1rpx solid #e8e8e8;
  border-radius: 16rpx;
  background: #ffffff;
  /* 移除 overflow: hidden，交由内部的 .course-details 处理 */

  /* 1. 将卡片设为 Grid 容器 */
  display: grid;
  /* 2. 定义两行：第一行高度自适应，第二行（课程详情）初始高度为0 */
  grid-template-rows: auto 0fr;
  /* 3. 对行高变化添加过渡动画 */
  transition: grid-template-rows 0.35s ease-in-out;

  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.module-card.expanded {
  /* 4. 展开时，第二行的高度变为 1fr，占据所有可用空间 */
  grid-template-rows: auto 1fr;
  box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.12);
  transform: translateY(-4rpx);
}

.module-card.incomplete {
  border-color: #ffaaa5;
  background: linear-gradient(135deg, #fff7f7 0%, #ffffff 100%);
}

.module-header {
  cursor: pointer;
  padding: 16rpx 14rpx;
  transition: background-color 0.2s ease;
}

.module-header:active {
  background: rgba(127, 69, 21, 0.08);
}

.course-details {
  /* 5. 必须设置为 overflow: hidden，否则内容会在 0fr 时溢出 */
  overflow: hidden;
  background: linear-gradient(180deg, #fafbfc 0%, #f5f6fa 100%);
  border-top: 1rpx solid #e8e8e8;
  min-height: 0;
  /* 兼容性设置 */
}

/* 因为点击事件放到了 .module-card，所以移除这里的 pointer-events */
.course-title-section .course-code {
  cursor: pointer;
}

/* 删除了所有 course-details 上的动画属性，因为动画已由父级 grid 控制 */

.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.module-title {
  font-size: 30rpx;
  font-weight: 600;
  flex: 1;
  margin-right: 16rpx;
}

.header-middle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.credits-info {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.credits-text {
  font-size: 28rpx;
  color: var(--text-secondary);
  font-weight: 500;
}

.course-count-text {
  font-size: 22rpx;
  color: #595959;
  font-weight: 400;
}

.shortage-text {
  font-size: 24rpx;
  color: #e74c3c;
  font-weight: 500;
}

.expand-action {
  display: flex;
  align-items: center;
  gap: 6rpx;
  padding: 6rpx 10rpx;
  background: rgba(127, 69, 21, 0.08);
  border-radius: 16rpx;
}

.hint-text {
  font-size: 22rpx;
  color: var(--text-light);
}

.chevron-icon {
  transition: transform 0.35s ease;
}

.chevron-icon.expanded {
  transform: rotate(180deg);
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.progress-bar {
  flex: 1;
  height: 20rpx;
  background: #f5f5f5;
  border-radius: 10rpx;
  overflow: hidden;
  box-shadow: inset 0 2rpx 4rpx rgba(0, 0, 0, 0.1);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #52c41a 0%, #73d13d 100%);
  border-radius: 10rpx;
  transition: width 0.6s ease;
}

.progress-fill.danger {
  background: linear-gradient(90deg, #ff4d4f 0%, #ff7875 100%);
}

.progress-text {
  font-size: 24rpx;
  font-weight: 500;
  min-width: 60rpx;
  text-align: right;
}

.status-chip {
  padding: 6rpx 12rpx;
  border-radius: 16rpx;
  font-size: 22rpx;
  font-weight: 500;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.chip-module-complete,
.chip-completed {
  background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
  color: #389e0d;
  border: 1rpx solid #95de64;
}

.chip-module-incomplete,
.chip-incomplete {
  background: linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%);
  color: #cf1322;
  border: 1rpx solid #ff7875;
}

.chip-neutral {
  background: linear-gradient(135deg, #f0f0f0 0%, #d9d9d9 100%);
  color: #595959;
  border: 1rpx solid #bfbfbf;
}

.course-sort-hint {
  padding: 8rpx 12rpx 4rpx;
  text-align: center;
}

.sort-hint-text {
  font-size: 20rpx;
  color: #8c8c8c;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  padding: 12rpx;
}

/* 移除了 ::after 伪元素方案，因为 Grid 方案不需要它 */
.course-item {
  border: 1rpx solid #e8e8e8;
  border-radius: 10rpx;
  padding: 8rpx 12rpx;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  position: relative;
}

.course-item.completed {
  border-color: #87d068;
  background: linear-gradient(135deg, #f6ffed 0%, #ffffff 100%);
}

.course-item.completed::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 6rpx;
  height: 100%;
  background: linear-gradient(180deg, #52c41a 0%, #73d13d 100%);
  border-radius: 12rpx 0 0 12rpx;
  transition: opacity 0.3s ease;
}

.course-item:not(.completed) {
  border-color: #ffb3ba;
  background: linear-gradient(135deg, #fff2f0 0%, #ffffff 100%);
}

.course-item:not(.completed)::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 6rpx;
  height: 100%;
  background: linear-gradient(180deg, #ff4d4f 0%, #ff7875 100%);
  border-radius: 12rpx 0 0 12rpx;
  transition: opacity 0.3s ease;
}

.course-name {
  font-size: 26rpx;
  font-weight: 600;
}

.current-semester-tag {
  font-size: 18rpx;
  color: #1890ff;
  background: #e6f7ff;
  padding: 2rpx 8rpx;
  border-radius: 6rpx;
  border: 1rpx solid #91d5ff;
  font-weight: 600;
  white-space: nowrap;
  align-self: center;
}

.course-code {
  font-size: 20rpx;
  color: #8c8c8c;
  background: #f5f5f5;
  padding: 2rpx 8rpx;
  border-radius: 6rpx;
  align-self: flex-start;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6rpx;
}

.chip {
  padding: 3rpx 8rpx;
  border-radius: 10rpx;
  font-size: 18rpx;
}

.course-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4rpx 8rpx;
  padding-top: 6rpx;
  border-top: 1rpx solid #f5f5f5;
}

.meta {
  font-size: 20rpx;
  color: #595959;
  padding: 2rpx 6rpx;
  background: #f0f2f5;
  border-radius: 6rpx;
  border: 1rpx solid #e8e8e8;
}

.module-subtotal {
  margin: 8rpx 12rpx;
  padding: 10rpx;
  border-bottom: 1rpx solid #e8e8e8;
  background: linear-gradient(135deg, #f0f8ff 0%, #ffffff 100%);
  border-radius: 10rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
  font-size: 22rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.subtotal-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 24rpx;
  width: 100%;
  text-align: center;
  margin-bottom: 2rpx;
}

.subtotal-divider {
  width: 100%;
  height: 1rpx;
  background-color: #e8e8e8;
  margin: 6rpx 0;
}

.subtotal-credits,
.subtotal-hours {
  color: var(--text-secondary);
  padding: 4rpx 8rpx;
  background: rgba(127, 69, 21, 0.05);
  border-radius: 6rpx;
  text-align: center;
  min-width: 80rpx;
  flex: 1;
}

.subtotal-completed-group {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
}

.subtotal-completed-group .subtotal-hours {
  flex: initial;
}

.subtotal-meta {
  font-size: 20rpx;
  color: var(--text-secondary);
  padding: 2rpx 4rpx;
  background: #f8f9fa;
  border: 1rpx solid #e8e8e8;
  border-radius: 6rpx;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 32rpx;
  animation: fadeIn 0.3s ease-out;
}

.modal-container {
  background: #ffffff;
  border-radius: 20rpx;
  max-width: 600rpx;
  width: 100%;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(100rpx);
    opacity: 0;
  }

  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 24rpx 24rpx 16rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.modal-title {
  font-size: 32rpx;
  font-weight: 600;
}

.modal-content {
  padding: 24rpx;
}

.notice-text {
  font-size: 28rpx;
  line-height: 1.6;
  color: var(--text-secondary);
}

.modal-actions {
  display: flex;
  padding: 16rpx 24rpx 24rpx;
  justify-content: flex-end;
}
</style>
