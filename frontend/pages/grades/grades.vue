<template>
  <PageLayout>
    <LoadingScreen v-if="isLoading" text="正在从教务系统同步成绩..." />

    <view v-else class="page-container page-rounded-container">
      <view class="background-decoration">
        <view class="circle circle-1"></view>
        <view class="circle circle-2"></view>
        <view class="circle circle-3"></view>
      </view>

      <view class="content-wrapper">
        <EmptyState v-if="isEmpty" icon-type="info-filled" title="没有查询到任何成绩记录" description="请检查网络连接或稍后重试"
          :show-retry="true" @retry="fetchGrades" />

        <view v-else>
          <!-- GPA分析模块 -->
          <GPAAnalysis :gpaAnalysis="gpaAnalysis" :effectiveGpa="effectiveGpa" :totalCourses="totalCourses"
            :yearlyGpa="yearlyGpa" :semesterGpa="semesterGpa" />

          <!-- 自定义GPA切换模块 -->
          <CustomToggle :isCustomMode="isCustomMode" @toggle="toggleCustomMode" />

          <!-- 课程列表模块 -->
          <CourseList :semesters="semesters" :isCustomMode="isCustomMode" :selectedCourses="selectedCourses"
            :expandedCourses="expandedCourses" @courseClick="handleCourseClick" />
        </view>
      </view>
    </view>

    <!-- 自定义GPA计算底部栏 -->
    <CustomFooter :isCustomMode="isCustomMode" :customGPAResult="customGPAResult" :selectedCourses="selectedCourses"
      :allCourses="allCourses" :isCalculating="isCalculating" @clearResult="clearCustomResult"
      @selectAll="selectAllCourses" @clearSelection="clearSelection" @calculate="calculateCustomGPA" />

    <!-- 提示弹窗 -->
    <NoticeModal :showModal="showNoticeModal" @close="closeNoticeModal" />
  </PageLayout>
</template>

<script>
import { ref, computed } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import LoadingScreen from "../../components/LoadingScreen/LoadingScreen.vue";
import EmptyState from "../../components/EmptyState/EmptyState.vue";

// 引入模块化组件
import GPAAnalysis from "./GPAAnalysis.vue";
import CustomToggle from "./CustomToggle.vue";
import CourseList from "./CourseList.vue";
import CustomFooter from "./CustomFooter.vue";
import NoticeModal from "./NoticeModal.vue";

// 引入API服务
import { fetchGradesData, calculateCustomGPA as apiCalculateGPA, groupGradesBySemester, checkLoginStatus } from "./api.js";

export default {
  name: 'Grades',
  components: {
    PageLayout,
    LoadingScreen,
    EmptyState,
    GPAAnalysis,
    CustomToggle,
    CourseList,
    CustomFooter,
    NoticeModal
  },
  setup() {
    // --- 基础页面状态 ---
    const isLoading = ref(true);
    const semesters = ref([]);
    const gpaAnalysis = ref(null);
    const semesterGpa = ref(null);
    const yearlyGpa = ref(null);
    const effectiveGpa = ref(null);
    const totalCourses = ref(0);
    const allCourses = ref([]);

    // --- 自定义GPA计算状态 ---
    const isCustomMode = ref(false);
    const selectedCourses = ref([]); // 存储选中的课程 `index`
    const isCalculating = ref(false);
    const customGPAResult = ref(null); // 用于存储计算结果

    // --- UI交互状态 ---
    const expandedCourses = ref(new Set()); // 存储展开的课程 `index`
    const showNoticeModal = ref(false);

    // --- 计算属性 ---
    const isEmpty = computed(() => semesters.value.length === 0);
    const selectionInfoText = computed(() => `已选 ${selectedCourses.value.length} / ${allCourses.value.length} 门`);
    const isCalculateDisabled = computed(() => isCalculating.value || selectedCourses.value.length === 0);

    // --- 生命周期钩子 ---
    onLoad(() => {
      // 1. 检查登录并获取数据
      checkLoginAndFetch();
      // 2. 延迟500ms后弹出提示窗口
      setTimeout(() => {
        // 可选: 增加判断条件，例如仅在有成绩数据时显示
        if (semesters.value.length > 0 || !isLoading.value) {
          showNoticeModal.value = true;
        }
      }, 500);
      console.log("用户进入成绩分析页面");
    });

    onShow(() => {
      // 每次页面显示时检查 token，防止在其他页面退出登录后，返回此页面时状态不正确
      if (!uni.getStorageSync("token")) {
        uni.showToast({ title: "请先登录", icon: "none" });
        uni.reLaunch({ url: "/pages/index/index" });
      }
    });

    // --- 数据获取与处理 ---
    const checkLoginAndFetch = () => {
      if (!checkLoginStatus()) return;
      fetchGrades();
    };

    const fetchGrades = async () => {
      isLoading.value = true;
      try {
        const result = await fetchGradesData();
        if (result.success) {
          allCourses.value = result.data.allCourses;
          semesters.value = groupGradesBySemester(allCourses.value);
          gpaAnalysis.value = result.data.gpaAnalysis;
          semesterGpa.value = result.data.semesterGpa;
          yearlyGpa.value = result.data.yearlyGpa;
          effectiveGpa.value = result.data.effectiveGpa;
          totalCourses.value = allCourses.value.length;
        }
      } finally {
        isLoading.value = false;
      }
    };

    // --- UI交互与辅助函数 ---

    const toggleExpand = (courseIndex) => {
      if (expandedCourses.value.has(courseIndex)) {
        expandedCourses.value.delete(courseIndex);
      } else {
        expandedCourses.value.add(courseIndex);
      }
    };

    const handleCourseClick = (course) => {
      if (isCustomMode.value) {
        toggleCourseSelection(course.index);
      } else {
        toggleExpand(course.index);
      }
    };

    const closeNoticeModal = () => {
      showNoticeModal.value = false;
    };

    // --- 自定义GPA计算逻辑 ---
    const toggleCustomMode = (value) => {
      isCustomMode.value = value;
      if (!isCustomMode.value) {
        clearSelection();
        clearCustomResult();
      }
    };

    const toggleCourseSelection = (courseIndex) => {
      const idx = selectedCourses.value.indexOf(courseIndex);
      if (idx > -1) {
        selectedCourses.value.splice(idx, 1);
      } else {
        selectedCourses.value.push(courseIndex);
      }
      clearCustomResult(); // 每次选择变化时，清除旧的计算结果
    };

    const selectAllCourses = () => {
      selectedCourses.value = allCourses.value.map(c => c.index);
      clearCustomResult();
    };

    const clearSelection = () => {
      selectedCourses.value = [];
      clearCustomResult();
    };

    const clearCustomResult = () => {
      customGPAResult.value = null;
    };

    const calculateCustomGPA = async () => {
      if (selectedCourses.value.length === 0) {
        uni.showToast({ title: "请至少选择一门课程", icon: "none" });
        return;
      }
      isCalculating.value = true;

      try {
        const result = await apiCalculateGPA(selectedCourses.value);
        if (result.success) {
          customGPAResult.value = result.data;
        }
      } finally {
        isCalculating.value = false;
      }
    };

    return {
      // 基础状态
      isLoading,
      semesters,
      gpaAnalysis,
      semesterGpa,
      yearlyGpa,
      effectiveGpa,
      totalCourses,
      allCourses,

      // 自定义GPA状态
      isCustomMode,
      selectedCourses,
      isCalculating,
      customGPAResult,

      // UI状态
      expandedCourses,
      showNoticeModal,

      // 计算属性
      isEmpty,
      selectionInfoText,
      isCalculateDisabled,

      // 方法
      fetchGrades,
      handleCourseClick,
      closeNoticeModal,
      toggleCustomMode,
      selectAllCourses,
      clearSelection,
      calculateCustomGPA,
      clearCustomResult
    };
  }
}
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

/* 主题变量 */
$background-color: #f7f8fa;
$background-color-card: #ffffff;
$border-radius-lg: 40rpx;

/* 页面基本布局 */
.page-container {
  min-height: 100vh;
  background: $background-color;
  position: relative;
  overflow: hidden;
}

.page-rounded-container {
  background: $background-color-card;
  border-radius: $border-radius-lg;
  padding: 20rpx 20rpx 30rpx;
  box-shadow: 0 20rpx 60rpx var(--shadow-light);
  border: 1rpx solid var(--border-light);
}

.content-wrapper {
  position: relative;
  z-index: 1;
}

/* 背景装饰 */
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
</style>