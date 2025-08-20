<template>
  <PageLayout>
    <LoadingScreen v-if="isLoading" text="正在获取培养计划..." />

    <view v-else class="page-rounded-container">
      <EmptyState
        v-if="modules.length === 0"
        icon-type="info-filled"
        title="暂无培养计划数据"
        description="请稍后重试或下拉刷新"
        :show-retry="true"
        @retry="fetchCoursePlan" />

      <view v-else>
        <ModernCard title="培养计划模块">
          <view class="modules-list">
            <view
              v-for="(m, idx) in sortedModules"
              :key="m.module_name"
              class="module-card"
              :class="{ 
                incomplete: isIncomplete(m),
                expanded: expanded[getOriginalIndex(m)]
              }">
              <!-- 模块头部，点击可展开 -->
              <view class="module-header" @click="toggleModule(getOriginalIndex(m))">
                <view class="header-info">
                  <view class="header-top">
                    <text class="module-title">{{ m.module_name }}</text>
                    <view
                      class="status-chip"
                      :class="isIncomplete(m) ? 'chip-danger' : 'chip-success'">
                      <text>{{ isIncomplete(m) ? "未修满" : "已修满" }}</text>
                    </view>
                  </view>
                  
                  <view class="header-middle">
                    <view class="credits-info">
                      <text class="credits-text"
                        >{{ formatNumber(m.completed_credits) }}/{{
                          formatNumber(m.required_credits)
                        }} 学分</text
                      >
                      <text 
                        v-if="isIncomplete(m)" 
                        class="shortage-text"
                        >差 {{ formatNumber(Number(m.required_credits) - Number(m.completed_credits)) }} 学分</text
                      >
                    </view>
                    
                    <view class="expand-action">
                      <text class="hint-text" v-if="!expanded[getOriginalIndex(m)]">点击展开</text>
                      <text class="hint-text" v-else>点击收起</text>
                      <uni-icons
                        class="chevron-icon"
                        :class="{ expanded: expanded[getOriginalIndex(m)] }"
                        type="arrowdown"
                        size="20"
                        color="#7F4515" />
                    </view>
                  </view>
                  
                  <!-- 进度条 -->
                  <view class="progress-container">
                    <view class="progress-bar">
                      <view
                        class="progress-fill"
                        :style="{ width: getProgress(m) + '%' }"
                        :class="{ danger: isIncomplete(m) }"></view>
                    </view>
                    <text class="progress-text">{{ getProgress(m) }}%</text>
                  </view>
                </view>
              </view>

              <!-- 课程详情，展开时显示 -->
              <view v-show="expanded[getOriginalIndex(m)]" class="course-details">
                <view class="course-list">
                  <view
                    v-for="c in m.courses || []"
                    :key="(c.course_code || '') + (c.course_name || '')"
                    class="course-item"
                    :class="{ completed: c.completion_status === '已修' }">
                    <view class="course-main">
                      <text class="course-name">{{ c.course_name }}</text>
                      <view class="chips">
                        <text
                          class="chip"
                          :class="
                            c.completion_status === '已修'
                              ? 'chip-success'
                              : 'chip-muted'
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
                      <text class="meta" v-if="c.semester"
                        >学期 {{ c.semester }}</text
                      >
                      <text class="meta" v-if="c.hours?.total"
                        >学时 {{ c.hours.total }}</text
                      >
                    </view>
                  </view>
                </view>

                <view
                  v-if="m.subtotal"
                  class="module-subtotal">
                  <text class="subtotal-title">小计</text>
                  <text class="subtotal-credits"
                    >学分 {{ m.subtotal.total_credits }}</text
                  >
                  <text class="subtotal-hours"
                    >总学时 {{ m.subtotal.hours?.total }}</text
                  >
                </view>
              </view>
            </view>
          </view>
        </ModernCard>
      </view>
    </view>
  </PageLayout>
</template>

<script setup>
import { ref, computed } from "vue";
import { onLoad, onPullDownRefresh } from "@dcloudio/uni-app";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import ModernCard from "../../components/ModernCard/ModernCard.vue";
import LoadingScreen from "../../components/LoadingScreen/LoadingScreen.vue";
import EmptyState from "../../components/EmptyState/EmptyState.vue";

const isLoading = ref(true);
const modules = ref([]);
const expanded = ref([]); // 每个模块的折叠状态

// 计算属性：按未修满状态排序的模块列表
const sortedModules = computed(() => {
  return [...modules.value].sort((a, b) => {
    const aIncomplete = isIncomplete(a);
    const bIncomplete = isIncomplete(b);
    
    // 未修满的排在前面
    if (aIncomplete && !bIncomplete) return -1;
    if (!aIncomplete && bIncomplete) return 1;
    
    // 同样状态下保持原顺序
    return 0;
  });
});

onLoad(() => {
  fetchCoursePlan();
});

onPullDownRefresh(async () => {
  await fetchCoursePlan();
  uni.stopPullDownRefresh();
});

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
      header: {
        Authorization: "Bearer " + token,
      },
    });

    let payload = null;
    if (res.statusCode === 200) {
      // 兼容两种返回：带 success 的结构或直接返回数据
      payload = res.data?.success ? res.data.data : res.data;
    }

    if (!payload) {
      throw new Error("无有效数据");
    }

    modules.value = Array.isArray(payload.modules) ? payload.modules : [];

    // 初始化折叠状态：全部折叠
    expanded.value = modules.value.map(() => false);
  } catch (err) {
    console.error("获取培养计划失败", err);
    uni.showToast({ title: "获取培养计划失败", icon: "none" });
  } finally {
    isLoading.value = false;
  }
};

const toggleModule = (index) => {
  expanded.value[index] = !expanded.value[index];
};

// 获取模块在原始数组中的索引（用于展开状态映射）
const getOriginalIndex = (module) => {
  return modules.value.findIndex(m => m.module_name === module.module_name);
};

const isIncomplete = (module) => {
  const need = Number(module?.required_credits) || 0;
  const done = Number(module?.completed_credits) || 0;
  return done < need;
};

const getProgress = (module) => {
  const need = Number(module?.required_credits) || 0;
  const done = Number(module?.completed_credits) || 0;
  if (need <= 0) return 0;
  const pct = Math.min(100, Math.max(0, Math.round((done / need) * 100)));
  return pct;
};

const formatNumber = (n) => {
  const v = Number(n);
  if (Number.isNaN(v)) return "0";
  return v % 1 === 0 ? String(v) : v.toFixed(1);
};
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

.page-rounded-container {
  background: linear-gradient(180deg, #ffffff 0%, #fafbfc 100%);
  border-radius: 40rpx;
  padding: 40rpx 30rpx;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.08);
  border: 1rpx solid #e8e8e8;
  margin: 20rpx;
}

/* 模块列表容器 */
.modules-list {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
}

/* 单个模块卡片 */
.module-card {
  border: 1rpx solid #e8e8e8;
  border-radius: 20rpx;
  background: #ffffff;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.module-card.incomplete {
  border-color: #ffaaa5;
  background: linear-gradient(135deg, #fff7f7 0%, #ffffff 100%);
  box-shadow: 0 6rpx 24rpx rgba(255, 77, 79, 0.15);
}

.module-card.expanded {
  box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.12);
  transform: translateY(-4rpx);
}

/* 模块头部 */
.module-header {
  padding: 32rpx 28rpx;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.module-header:active {
  background: rgba(127, 69, 21, 0.08);
}

.header-info {
  width: 100%;
}

.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.module-title {
  font-size: 30rpx;
  color: var(--text-primary);
  font-weight: 600;
  flex: 1;
  line-height: 1.4;
  margin-right: 16rpx;
}

.header-middle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
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

.shortage-text {
  font-size: 24rpx;
  color: #e74c3c;
  font-weight: 500;
}

.expand-action {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 8rpx 12rpx;
  background: rgba(127, 69, 21, 0.08);
  border-radius: 20rpx;
}

.hint-text {
  font-size: 22rpx;
  color: var(--text-light);
}

.chevron-icon {
  transition: transform 0.3s ease;
}

.chevron-icon.expanded {
  transform: rotate(180deg);
}

/* 进度条容器 */
.progress-container {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

/* 进度条 */
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
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.progress-fill.danger {
  background: linear-gradient(90deg, #ff4d4f 0%, #ff7875 100%);
}

.progress-text {
  font-size: 24rpx;
  color: var(--text-secondary);
  font-weight: 500;
  min-width: 60rpx;
  text-align: right;
}

/* 展开动画 */
.course-details {
  animation: slideDown 0.3s ease-out;
}

.module-card {
  animation: fadeIn 0.5s ease-out;
}

/* 状态标签 */
.status-chip {
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  white-space: nowrap;
  font-weight: 500;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.chip-success {
  background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
  color: #389e0d;
  border: 1rpx solid #b7eb8f;
}

.chip-danger {
  background: linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%);
  color: #cf1322;
  border: 1rpx solid #ffa39e;
}

.chip-muted {
  background: linear-gradient(135deg, #fafafa 0%, #f0f0f0 100%);
  color: #8c8c8c;
  border: 1rpx solid #d9d9d9;
}

.chip-neutral {
  background: linear-gradient(135deg, #f9f9f9 0%, #f0f0f0 100%);
  color: #666;
  border: 1rpx solid #e0e0e0;
}

/* 课程详情区域 */
.course-details {
  border-top: 1rpx solid #e8e8e8;
  background: linear-gradient(180deg, #fafbfc 0%, #f5f6fa 100%);
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  padding: 32rpx 28rpx;
}

.course-item {
  border: 1rpx solid #e8e8e8;
  border-radius: 16rpx;
  padding: 24rpx;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.course-item:active {
  transform: translateY(2rpx);
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.course-item.completed {
  border-color: #b7eb8f;
  background: linear-gradient(135deg, #f6ffed 0%, #ffffff 100%);
  box-shadow: 0 4rpx 12rpx rgba(82, 196, 26, 0.1);
}

.course-main {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20rpx;
}

.course-name {
  flex: 1;
  font-size: 28rpx;
  color: var(--text-primary);
  font-weight: 600;
  line-height: 1.5;
  word-break: break-word;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  justify-content: flex-end;
  max-width: 45%;
}

.chip {
  padding: 8rpx 12rpx;
  border-radius: 16rpx;
  font-size: 20rpx;
  font-weight: 500;
}

.course-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120rpx, 1fr));
  gap: 16rpx 24rpx;
  padding: 16rpx 0 0;
  border-top: 1rpx solid #f0f0f0;
}

.meta {
  font-size: 24rpx;
  color: var(--text-secondary);
  line-height: 1.4;
  padding: 8rpx 12rpx;
  background: #f8f9fa;
  border-radius: 12rpx;
  text-align: center;
}

.module-subtotal {
  margin: 24rpx 28rpx;
  padding: 24rpx;
  border-top: 2rpx solid #e8e8e8;
  background: linear-gradient(135deg, #f0f8ff 0%, #ffffff 100%);
  border-radius: 16rpx;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120rpx, 1fr));
  gap: 16rpx;
  font-size: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.subtotal-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 26rpx;
  grid-column: 1 / -1;
  text-align: center;
  margin-bottom: 8rpx;
}

.subtotal-credits,
.subtotal-hours {
  color: var(--text-secondary);
  text-align: center;
  padding: 8rpx;
  background: rgba(127, 69, 21, 0.05);
  border-radius: 12rpx;
}
</style>
