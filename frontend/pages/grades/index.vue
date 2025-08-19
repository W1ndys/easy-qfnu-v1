<template>
  <PageLayout>
    <!-- 加载状态 -->
    <LoadingScreen v-if="isLoading" text="正在从教务系统同步成绩..." />

    <!-- 内容区域 -->
    <view v-else>
      <!-- 空状态 -->
      <EmptyState
        v-if="semesters.length === 0"
        icon-type="info-filled"
        title="没有查询到任何成绩记录"
        description="请检查网络连接或稍后重试"
        :show-retry="true"
        @retry="fetchGrades"
      />

      <!-- 有数据时显示 -->
      <view v-else>
        <!-- GPA分析模块 -->
        <GPAAnalysis
          v-if="gpaAnalysis"
          :gpa-analysis="gpaAnalysis"
          :effective-gpa="effectiveGpa"
          :yearly-gpa="yearlyGpa"
          :semester-gpa="semesterGpa"
          :total-courses="totalCourses"
        />

        <!-- 成绩列表 -->
        <GradesList :semesters="semesters" />
      </view>
    </view>
  </PageLayout>
</template>

<script setup>
import { ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import LoadingScreen from "../../components/LoadingScreen/LoadingScreen.vue";
import EmptyState from "../../components/EmptyState/EmptyState.vue";
import GPAAnalysis from "../../components/GPAAnalysis/GPAAnalysis.vue";
import GradesList from "../../components/GradesList/GradesList.vue";

// --- 页面数据 ---
const isLoading = ref(true); // 页面初始为加载状态
const semesters = ref([]); // 用于存放按学期分组后的成绩
const gpaAnalysis = ref(null); // 用于存放GPA分析数据
const semesterGpa = ref(null); // 用于存放按学期的GPA分析
const yearlyGpa = ref(null); // 用于存放按学年的GPA分析
const effectiveGpa = ref(null); // 用于存放有效GPA（去重修补考）
const totalCourses = ref(0); // 总课程数

// --- 页面生命周期 ---
onLoad(() => {
  fetchGrades(); // 页面一加载就调用获取成绩的函数
});

// --- 核心逻辑函数 ---
const fetchGrades = async () => {
  const token = uni.getStorageSync("token");
  if (!token) {
    uni.showToast({ title: "请先登录", icon: "none" });
    uni.reLaunch({ url: "/pages/index/index" });
    return;
  }

  isLoading.value = true; // 开始加载

  try {
    const res = await uni.request({
      url: "http://127.0.0.1:8000/api/v1/grades",
      method: "GET",
      // 【核心】在请求头中带上Token，用于身份认证
      header: {
        Authorization: "Bearer " + token,
      },
    });

    if (res.statusCode === 200 && res.data.success) {
      const rawGrades = res.data.data;
      // 调用辅助函数，对成绩按学期进行分组
      const groupedGrades = groupGradesBySemester(rawGrades);
      // 更新页面数据
      semesters.value = groupedGrades;

      // 更新GPA分析数据
      gpaAnalysis.value = res.data.gpa_analysis;
      semesterGpa.value = res.data.semester_gpa;
      yearlyGpa.value = res.data.yearly_gpa;
      effectiveGpa.value = res.data.effective_gpa;
      totalCourses.value = res.data.total_courses;
    } else if (res.statusCode === 401) {
      // token无效或过期
      console.log("Token无效，清除缓存并跳转到登录页");
      uni.removeStorageSync("token");
      uni.showToast({ title: "登录已过期，请重新登录", icon: "none" });
      setTimeout(() => {
        uni.reLaunch({ url: "/pages/index/index" });
      }, 1500);
    } else {
      const errorMessage = res.data.detail || "获取成绩失败";
      uni.showToast({ title: errorMessage, icon: "none" });
    }
  } catch (error) {
    console.error("请求失败", error);
    uni.showToast({ title: "服务器连接失败", icon: "none" });
  } finally {
    // 请求完成后（无论成功失败），都结束加载状态
    isLoading.value = false;
  }
};

/**
 * 辅助函数：将平铺的成绩列表按学期分组
 * @param {Array} grades - 从后端获取的原始成绩数组
 */
const groupGradesBySemester = (grades) => {
  if (!grades || grades.length === 0) {
    return [];
  }
  const semesterMap = {};
  grades.forEach((grade) => {
    const semesterName = grade.semester; // 使用英文键名
    if (!semesterMap[semesterName]) {
      semesterMap[semesterName] = [];
    }
    semesterMap[semesterName].push(grade);
  });
  const result = Object.keys(semesterMap).map((semesterName) => {
    return {
      semesterName: semesterName,
      grades: semesterMap[semesterName],
    };
  });
  result.sort((a, b) => b.semesterName.localeCompare(a.semesterName));
  return result;
};
</script>

<style lang="scss" scoped>
// 成绩页面已完全组件化，样式已移至相应组件中
</style>
