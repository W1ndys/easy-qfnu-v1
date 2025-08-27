<template>
  <view class="page-container page-rounded-container">
    <!-- 背景装饰 -->
    <view class="background-decoration">
      <view class="circle circle-1"></view>
      <view class="circle circle-2"></view>
      <view class="circle circle-3"></view>
    </view>

    <!-- 页面头部 -->
    <view class="page-header">
      <view class="header-content">
        <text class="page-title">平均分查询</text>
        <text class="page-subtitle">Academic Score Analysis</text>
      </view>
    </view>

    <!-- 主内容区域 -->
    <view class="content-wrapper">
      <!-- 搜索表单组件 -->
      <SearchForm :loading="loading" @search="handleSearch" @reset="handleReset" />

      <!-- 查询结果组件 -->
      <ResultsSection v-if="hasResults" :result-data="resultData" />

      <!-- 状态组件 -->
      <StateComponents v-else-if="searched && !loading" type="empty" :message="emptyMessage" @retry="handleReset" />

      <StateComponents v-else-if="!searched && !loading" type="initial" />

      <StateComponents v-else-if="loading" type="loading" />
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import SearchForm from './SearchForm.vue';
import ResultsSection from './ResultsSection.vue';
import StateComponents from './StateComponents.vue';
import { queryAverageScores, checkLoginStatus } from './api.js';
import { getErrorMessage } from './utils.js';

// 状态
const resultData = ref({});
const loading = ref(false);
const searched = ref(false);
const emptyMessage = ref("未找到相关数据");

// 计算属性
const hasResults = computed(() => Object.keys(resultData.value).length > 0);

// 方法
async function handleSearch(params) {
  if (!checkLoginStatus()) return;

  loading.value = true;
  searched.value = true;

  try {
    const response = await queryAverageScores(params);
    if (response.code === 200) {
      resultData.value = response.data;
      if (!hasResults.value) emptyMessage.value = "未找到相关数据";
    } else {
      resultData.value = {};
      emptyMessage.value = response.message || "查询失败";
      uni.showToast({ title: emptyMessage.value, icon: "none" });
    }
  } catch (error) {
    console.error("查询平均分失败:", error);
    resultData.value = {};
    const errorMessage = getErrorMessage(error);
    emptyMessage.value = errorMessage;
    uni.showToast({ title: errorMessage, icon: "none", duration: 3000 });
  } finally {
    loading.value = false;
  }
}

function handleReset() {
  resultData.value = {};
  searched.value = false;
}

// 生命周期
onMounted(() => {
  uni.setNavigationBarTitle({ title: "平均分查询" });
  checkLoginStatus();
  console.log("用户进入平均分查询页面");
});
</script>


<style lang="scss" scoped>
@import "../../styles/common.scss";

// 页面容器
.page-container {
  min-height: 100vh;
  background: #f7f8fa;
  position: relative;
  overflow: hidden;
}

// 外层圆角容器（与其他页面一致）
.page-rounded-container {
  background: #ffffff;
  border-radius: 40rpx;
  padding: 20rpx 20rpx 30rpx;
  box-shadow: 0 20rpx 60rpx var(--shadow-light);
  border: 1rpx solid var(--border-light);
}

// 背景装饰
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
    transform: translateY(0px) rotate(0deg);
  }

  50% {
    transform: translateY(-20rpx) rotate(180deg);
  }
}

// 页面头部
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

// 内容区域
.content-wrapper {
  padding: 0 30rpx 30rpx;
  position: relative;
  z-index: 1;
}

// 现代化卡片
.modern-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20rpx);
  border-radius: var(--radius-large);
  border: 1rpx solid var(--border-light);
  box-shadow: 0 20rpx 60rpx var(--shadow-light);
  margin-bottom: 40rpx;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4rpx);
    box-shadow: 0 24rpx 80rpx var(--shadow-medium);
  }
}

// 响应式适配
@media (max-width: 600rpx) {
  .content-wrapper {
    padding: 0 15rpx 30rpx;
  }

  .page-title {
    font-size: 36rpx;
  }
}
</style>
