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
        @retry="fetchCoursePlan" />

      <view v-else>
        <!-- 总学分进度显示 -->
        <ModernCard title="总学分进度" class="total-progress-card">
          <view class="total-progress-container">
            <view class="total-header">
              <view class="total-title-section">
                <text class="total-title">培养方案总进度</text>
                <view
                  class="status-chip"
                  :class="isTotalIncomplete ? 'chip-module-incomplete' : 'chip-module-complete'">
                  <text>{{ isTotalIncomplete ? "未修满" : "已修满" }}</text>
                </view>
              </view>
              
                <view class="total-credits-info">
                <text class="total-credits-text"
                  >{{ formatNumber(totalCompletedCredits) }}/{{
                  formatNumber(totalRequiredCredits)
                  }} 学分</text
                >
                <text 
                  v-if="isTotalIncomplete" 
                  class="total-shortage-text"
                  >差 {{ formatNumber(totalRequiredCredits - totalCompletedCredits) }} 学分</text
                >
                <text class="total-hint-text">
                  (相对于系统内方案，实际差值要看总学分要求，大部分专业是少几分的)
                </text>
                </view>
                
              <!-- 总进度条 -->
              <view class="total-progress-bar-container">
                <view class="progress-bar total-progress-bar">
                  <view
                    class="progress-fill"
                    :style="{ width: totalProgress + '%' }"
                    :class="{ danger: isTotalIncomplete }"></view>
                </view>
                <text class="progress-text total-progress-text">{{ totalProgress }}%</text>
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
                <view
                  v-if="m.subtotal"
                  class="module-subtotal">
                  <text class="subtotal-title">模块要求小计</text>
                  <text class="subtotal-credits"
                    >要求学分 {{ m.subtotal.total_credits }}</text
                  >
                  <text class="subtotal-hours"
                    >要求总学时 {{ m.subtotal.hours?.total || 0 }}</text
                  >
                  
                  <view class="subtotal-divider"></view>
                  
                  <text class="subtotal-title">已修课程小计</text>
                  <text class="subtotal-hours">
                    已修总学时 {{ calculateCompletedHours(m).total || 0 }}
                  </text>
                  <template v-for="hourInfo in formatHours(calculateCompletedHours(m))" :key="hourInfo">
                    <text class="subtotal-meta">{{ hourInfo }}</text>
                  </template>
                </view>

                <view class="course-sort-hint">
                  <text class="sort-hint-text">
                  <uni-icons type="info" size="16" color="#666" />
                  {{ isIncomplete(m) ? '未修课程已置顶显示' : '已修课程已置顶显示' }}
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
                      <text v-if="c.course_code" class="course-code">代码: {{ c.course_code }}</text>
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
                    <text class="meta" v-if="c.semester">学期 {{ c.semester }}</text>
                    <text class="meta" v-if="c.hours?.total">总学时 {{ c.hours.total }}</text>
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

    <!-- 培养方案提示弹窗 -->
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
          <text class="notice-text" style="margin-top: 24rpx;">
            根据教务处官方规定：培养方案毕业学分原则上145-170学分，其中人文社会科学类专业毕业学分≤160学分，理科类专业毕业学分≤165学分，工科类专业毕业学分≤170学分，辅修学士学位专业毕业学分70学分左右。
          </text>
          <text class="notice-text" style="margin-top: 16rpx; font-size: 24rpx; color: #8c8c8c;">
            来源：https://jwc.qfnu.edu.cn/info/1068/7039.htm
          </text>
        </view>
        
        <view class="modal-actions">
          <button class="action-btn primary-btn" @click="handleConfirm">
            我已阅读
          </button>
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
const expanded = ref([]); // 每个模块的折叠状态
const showNoticeModal = ref(false);

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
  }).map(module => {
    const moduleIncomplete = isIncomplete(module);
    
    return {
      ...module,
      // 根据模块完成状态进行不同的课程排序
      courses: [...(module.courses || [])].sort((a, b) => {
        const aCompleted = isCourseCompleted(a);
        const bCompleted = isCourseCompleted(b);
        
        if (moduleIncomplete) {
          // 未修满的模块：未修课程置顶
          if (!aCompleted && bCompleted) return -1;
          if (aCompleted && !bCompleted) return 1;
        } else {
          // 已修满的模块：已修课程置顶
          if (aCompleted && !bCompleted) return -1;
          if (!aCompleted && bCompleted) return 1;
        }
        
        // 同样状态下保持原顺序
        return 0;
      })
    };
  });
});

onLoad(() => {
  checkLoginAndFetch();
});

onShow(() => {
  // 页面显示时检查登录状态
  const token = uni.getStorageSync("token");
  if (!token) {
    uni.showToast({ title: "请先登录", icon: "none" });
    uni.reLaunch({ url: "/pages/index/index" });
    return;
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
  await fetchCoursePlan();
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
      console.log("培养方案数据获取成功", payload);
    } else if (res.statusCode === 401) {
      console.error("身份验证失败，请重新登录");
      uni.removeStorageSync("token");
      uni.showToast({ title: "登录已过期，请重新登录", icon: "none" });
      setTimeout(() => {
        uni.reLaunch({ url: "/pages/index/index" });
      }, 1500);
      return;
    } else if (res.statusCode === 404) {
      console.error("未找到培养方案数据");
      uni.showToast({ title: "未找到培养方案数据", icon: "none" });
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
      console.warn("返回的培养方案格式异常", payload);
      uni.showToast({ title: "培养方案格式异常", icon: "none" });
      modules.value = [];
      return;
    }

    modules.value = payload.modules;
    console.log(`成功加载了${modules.value.length}个培养方案模块`);

    // 初始化折叠状态：全部折叠
    expanded.value = modules.value.map(() => false);
    
    if (modules.value.length === 0) {
      uni.showToast({ title: "暂无培养方案数据", icon: "none" });
    } else {
      // 数据加载成功后检查是否需要显示提示
      checkShowNotice();
    }
    } catch (err) {
    console.error("获取培养方案失败", err);
    uni.showToast({ 
      title: err.message || "获取培养方案失败，请稍后重试", 
      icon: "none", 
      duration: 2000 
    });
    } finally {
    isLoading.value = false;
    }
  };

// 检查是否需要显示培养方案说明
const checkShowNotice = () => {
  // 每次都显示培养方案说明，因为这是必读内容
  setTimeout(() => {
    showNoticeModal.value = true;
  }, 500);
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

const calculateCompletedHours = (module) => {
  if (!module.courses || module.courses.length === 0) {
    return { total: 0 };
  }

  const completedCourses = module.courses.filter(isCourseCompleted);
  
  const completedHours = completedCourses.reduce((acc, course) => {
    if (course.hours && typeof course.hours === 'object') {
      for (const [key, value] of Object.entries(course.hours)) {
        acc[key] = (acc[key] || 0) + (Number(value) || 0);
      }
    }
    return acc;
  }, {});

  return completedHours;
};

const formatHours = (hours) => {
  if (!hours || typeof hours !== 'object') return [];
  
  const hourTypes = {
    lecture: '讲授',
    practice: '实践',
    seminar: '研讨',
    experiment: '实验',
    design: '设计',
    computer: '上机',
    discussion: '讨论',
    extracurricular: '课外',
    online: '在线',
  };

  return Object.entries(hours)
    .filter(([key, value]) => key !== 'total' && Number(value) > 0)
    .map(([key, value]) => `${hourTypes[key] || key}: ${value}`);
};

const formatNumber = (n) => {
  const v = Number(n);
  if (Number.isNaN(v)) return "0";
  return v % 1 === 0 ? String(v) : v.toFixed(1);
};

// 计算总学分相关数据
const totalRequiredCredits = computed(() => {
  return modules.value.reduce((sum, module) => {
    return sum + (Number(module.required_credits) || 0);
  }, 0);
});

const totalCompletedCredits = computed(() => {
  return modules.value.reduce((sum, module) => {
    return sum + (Number(module.completed_credits) || 0);
  }, 0);
});

const totalProgress = computed(() => {
  if (totalRequiredCredits.value <= 0) return 0;
  const progress = Math.min(100, Math.max(0, Math.round((totalCompletedCredits.value / totalRequiredCredits.value) * 100)));
  return progress;
});

const isTotalIncomplete = computed(() => {
  return totalCompletedCredits.value < totalRequiredCredits.value;
});

// 处理确定按钮
const handleConfirm = () => {
  showNoticeModal.value = false;
};

// 点击遮罩关闭弹窗
const closeModal = () => {
  showNoticeModal.value = false;
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

/* 总学分进度卡片 */
.total-progress-card {
  margin-bottom: 24rpx;
}

.total-progress-container {
  padding: 8rpx 0;
}

.total-header {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
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
  gap: 8rpx;
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
  gap: 20rpx;
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
  flex-direction: column;
  align-items: flex-start;
  gap: 10rpx;
}

.course-title-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.course-name {
  font-size: 26rpx;
  color: var(--text-primary);
  font-weight: 600;
  line-height: 1.4;
  word-break: break-word;
}

.course-code {
  font-size: 20rpx;
  color: var(--text-light);
  font-weight: 400;
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
  width: 100%;
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
  padding: 8rpx 0 0;
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
  border-bottom: 1rpx solid #e8e8e8;
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

.subtotal-divider {
  width: 100%;
  height: 1rpx;
  background-color: #e8e8e8;
  margin: 8rpx 0;
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

.subtotal-meta {
  font-size: 20rpx;
  color: var(--text-secondary);
  line-height: 1.3;
  padding: 3rpx 6rpx;
  background: #f8f9fa;
  border: 1rpx solid #e8e8e8;
  border-radius: 6rpx;
  white-space: nowrap;
}

/* 弹窗样式 */
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
  padding: 40rpx;
  animation: fadeIn 0.3s ease-out;
}

.modal-container {
  background: #ffffff;
  border-radius: 24rpx;
  max-width: 600rpx;
  width: 100%;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
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
  gap: 12rpx;
  padding: 32rpx 32rpx 24rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.modal-title {
  font-size: 32rpx;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-content {
  padding: 32rpx;
}

.notice-text {
  font-size: 28rpx;
  line-height: 1.6;
  color: var(--text-secondary);
  text-align: justify;
}

.modal-actions {
  display: flex;
  gap: 16rpx;
  padding: 24rpx 32rpx 32rpx;
  justify-content: flex-end;
}

.action-btn {
  padding: 16rpx 32rpx;
  border-radius: 16rpx;
  font-size: 28rpx;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 120rpx;
}

.primary-btn {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: #ffffff;
  box-shadow: 0 4rpx 12rpx rgba(24, 144, 255, 0.3);
}

.primary-btn:active {
  transform: translateY(2rpx);
  box-shadow: 0 2rpx 8rpx rgba(24, 144, 255, 0.4);
}

.secondary-btn {
  background: #f5f5f5;
  color: var(--text-secondary);
  border: 1rpx solid #d9d9d9;
}

.secondary-btn:active {
  background: #e8e8e8;
  transform: translateY(2rpx);
}
</style>
