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
                      :class="isIncomplete(m) ? 'chip-module-incomplete' : 'chip-module-complete'">
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
                <view class="course-sort-hint">
                  <text class="sort-hint-text">
                  <uni-icons type="info" size="16" color="#666" />
                  未修课程已置顶显示
                  </text>
                </view>
                <view class="course-list">
                  <view
                  v-for="c in m.courses || []"
                  :key="(c.course_code || '') + (c.course_name || '')"
                  class="course-item"
                  :class="{ completed: isCourseCompleted(c) }">
                  <view class="course-main">
                    <view class="course-title-section">
                    <text class="course-name">{{ c.course_name }}</text>
                    </view>
                    <view class="chips">
                    <text
                      class="chip completion-chip"
                      :class="isCourseCompleted(c) ? 'chip-completed' : 'chip-incomplete'"
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
  }).map(module => ({
    ...module,
    // 为每个模块的课程进行排序：未修的排在前面
    courses: [...(module.courses || [])].sort((a, b) => {
      const aCompleted = isCourseCompleted(a);
      const bCompleted = isCourseCompleted(b);
      
      // 未修的排在前面
      if (!aCompleted && bCompleted) return -1;
      if (aCompleted && !bCompleted) return 1;
      
      // 同样状态下保持原顺序
      return 0;
    })
  }));
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
      console.log("培养计划数据获取成功", payload);
    } else if (res.statusCode === 401) {
      console.error("身份验证失败，请重新登录");
      uni.showToast({ title: "身份验证失败，请重新登录", icon: "none" });
      setTimeout(() => {
      uni.reLaunch({ url: "/pages/index/index" });
      }, 1500);
      return;
    } else if (res.statusCode === 404) {
      console.error("未找到培养计划数据");
      uni.showToast({ title: "未找到培养计划数据", icon: "none" });
      return;
    } else {
      // 获取详细的错误信息
      const errorDetail = res.data?.detail || res.data?.message || '未知错误';
      console.error(`请求错误：${res.statusCode}`, res.data, errorDetail);
      throw new Error(`请求错误：${res.statusCode} - ${errorDetail}`);
    }

    if (!payload) {
      throw new Error("无有效数据");
    }

    if (!Array.isArray(payload.modules)) {
      console.warn("返回的培养计划格式异常", payload);
      uni.showToast({ title: "培养计划格式异常", icon: "none" });
      modules.value = [];
      return;
    }

    modules.value = payload.modules;
    console.log(`成功加载了${modules.value.length}个培养计划模块`);

    // 初始化折叠状态：全部折叠
    expanded.value = modules.value.map(() => false);
    
    if (modules.value.length === 0) {
      uni.showToast({ title: "暂无培养计划数据", icon: "none" });
    }
    } catch (err) {
    console.error("获取培养计划失败", err);
    uni.showToast({ 
      title: err.message || "获取培养计划失败，请稍后重试", 
      icon: "none", 
      duration: 2000 
    });
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

// 判断课程是否已完成
const isCourseCompleted = (course) => {
  if (!course.completion_status) return false;
  return course.completion_status.includes('已修');
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
  border-radius: 20rpx;
  padding: 20rpx 16rpx;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.08);
  border: 1rpx solid #e8e8e8;
  margin: 8rpx;
}

/* 在小屏设备上进一步减少边距 */
@media (max-width: 750rpx) {
  .page-rounded-container {
    margin: 6rpx;
    padding: 16rpx 12rpx;
    border-radius: 16rpx;
  }
}

/* 模块列表容器 */
.modules-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
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
  padding: 20rpx 18rpx;
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
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #0958d9;
  border: 1rpx solid #91d5ff;
}

.chip-danger {
  background: linear-gradient(135deg, #fff1f0 0%, #ffccc7 100%);
  color: #cf1322;
  border: 1rpx solid #ffa39e;
}

.chip-muted {
  background: linear-gradient(135deg, #fff7e6 0%, #ffe7ba 100%);
  color: #d46b08;
  border: 1rpx solid #ffd591;
}

.chip-neutral {
  background: linear-gradient(135deg, #f0f0f0 0%, #d9d9d9 100%);
  color: #595959;
  border: 1rpx solid #bfbfbf;
}

/* 课程完成状态专用样式 */
.completion-chip {
  font-weight: 600;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.15);
}

.chip-completed {
  background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
  color: #389e0d;
  border: 1rpx solid #95de64;
  box-shadow: 0 4rpx 12rpx rgba(82, 196, 26, 0.2);
}

.chip-incomplete {
  background: linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%);
  color: #cf1322;
  border: 1rpx solid #ff7875;
  box-shadow: 0 4rpx 12rpx rgba(255, 77, 79, 0.2);
}

/* 模块状态专用样式 */
.chip-module-complete {
  background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
  color: #389e0d;
  border: 1rpx solid #95de64;
  box-shadow: 0 4rpx 12rpx rgba(82, 196, 26, 0.2);
  font-weight: 600;
}

.chip-module-incomplete {
  background: linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%);
  color: #cf1322;
  border: 1rpx solid #ff7875;
  box-shadow: 0 4rpx 12rpx rgba(255, 77, 79, 0.2);
  font-weight: 600;
}

/* 课程详情区域 */
.course-details {
  border-top: 1rpx solid #e8e8e8;
  background: linear-gradient(180deg, #fafbfc 0%, #f5f6fa 100%);
}

/* 课程排序提示 */
.course-sort-hint {
  padding: 12rpx 16rpx 6rpx;
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
  gap: 12rpx;
  padding: 16rpx;
}

.course-item {
  border: 1rpx solid #e8e8e8;
  border-radius: 12rpx;
  padding: 12rpx 16rpx;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.course-item:active {
  transform: translateY(2rpx);
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.course-item.completed {
  border-color: #87d068;
  background: linear-gradient(135deg, #f6ffed 0%, #ffffff 100%);
  box-shadow: 0 2rpx 8rpx rgba(82, 196, 26, 0.12);
  position: relative;
}

.course-item.completed::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 6rpx;
  height: 100%;
  background: linear-gradient(180deg, #52c41a 0%, #73d13d 100%);
  border-radius: 12rpx 0 0 12rpx;
}

/* 新增：未修课程的样式 */
.course-item:not(.completed) {
  border-color: #ffb3ba;
  background: linear-gradient(135deg, #fff2f0 0%, #ffffff 100%);
  box-shadow: 0 2rpx 8rpx rgba(255, 77, 79, 0.08);
  position: relative;
}

.course-item:not(.completed)::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 6rpx;
  height: 100%;
  background: linear-gradient(180deg, #ff4d4f 0%, #ff7875 100%);
  border-radius: 12rpx 0 0 12rpx;
}

.course-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.course-title-section {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.course-name {
  font-size: 26rpx;
  color: var(--text-primary);
  font-weight: 600;
  line-height: 1.4;
  word-break: break-word;
}

/* 未修课程指示器 */
.incomplete-indicator {
  flex-shrink: 0;
}

.indicator-text {
  font-size: 16rpx;
  color: #cf1322;
  background: linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%);
  padding: 2rpx 8rpx;
  border-radius: 8rpx;
  border: 1rpx solid #ff7875;
  font-weight: 600;
  box-shadow: 0 2rpx 6rpx rgba(255, 77, 79, 0.15);
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
  justify-content: flex-end;
  max-width: 45%;
}

.chip {
  padding: 4rpx 10rpx;
  border-radius: 12rpx;
  font-size: 18rpx;
  font-weight: 500;
}

.course-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6rpx 12rpx;
  padding: 6rpx 0 0;
  border-top: 1rpx solid #f5f5f5;
}

.meta {
  font-size: 20rpx;
  color: var(--text-secondary);
  line-height: 1.3;
  padding: 3rpx 6rpx;
  background: #f8f9fa;
  border-radius: 6rpx;
  white-space: nowrap;
}

.module-subtotal {
  margin: 12rpx 16rpx;
  padding: 12rpx;
  border-top: 1rpx solid #e8e8e8;
  background: linear-gradient(135deg, #f0f8ff 0%, #ffffff 100%);
  border-radius: 12rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  font-size: 22rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.subtotal-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 24rpx;
  width: 100%;
  text-align: center;
  margin-bottom: 4rpx;
}

.subtotal-credits,
.subtotal-hours {
  color: var(--text-secondary);
  padding: 6rpx 10rpx;
  background: rgba(127, 69, 21, 0.05);
  border-radius: 8rpx;
  flex: 1;
  text-align: center;
  min-width: 80rpx;
}
</style>
