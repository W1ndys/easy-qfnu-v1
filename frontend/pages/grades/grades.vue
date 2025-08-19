<template>
  <view class="container">
    <view v-if="isLoading" class="loading-container">
      <uni-load-more
        status="loading"
        :show-text="true"
        content-text="正在从教务系统同步成绩..."></uni-load-more>
    </view>

    <view v-else>
      <view v-if="semesters.length === 0" class="empty-container">
        <uni-icons type="info-filled" size="60" color="#999"></uni-icons>
        <text class="empty-text">没有查询到任何成绩记录</text>
      </view>

      <!-- GPA综合分析卡片 -->
      <view v-if="gpaAnalysis" class="gpa-section">
        <!-- 主要GPA指标 -->
        <uni-card title="GPA综合分析" margin="12px 0">
          <view class="main-gpa-container">
            <view class="main-gpa-item highlight">
              <view class="gpa-label">有效GPA</view>
              <view class="gpa-value primary" v-if="effectiveGpa">{{
                effectiveGpa.weighted_gpa
              }}</view>
              <view class="gpa-detail" v-if="effectiveGpa">
                学分: {{ effectiveGpa.total_credit }} | 课程:
                {{ effectiveGpa.course_count }}
              </view>
              <view class="gpa-note">去重修补考，取最高成绩</view>
            </view>
            <view class="gpa-divider"></view>
            <view class="main-gpa-item">
              <view class="gpa-label">基础GPA</view>
              <view class="gpa-value">{{
                gpaAnalysis.basic_gpa.weighted_gpa
              }}</view>
              <view class="gpa-detail">
                学分: {{ gpaAnalysis.basic_gpa.total_credit }} | 课程:
                {{ gpaAnalysis.basic_gpa.course_count }}
              </view>
              <view class="gpa-note">包含所有成绩</view>
            </view>
          </view>
          <view class="total-courses">总课程数: {{ totalCourses }}</view>
        </uni-card>

        <!-- 按学年GPA分析 -->
        <uni-card title="按学年GPA分析" margin="12px 0" v-if="yearlyGpa">
          <view class="yearly-gpa-container">
            <view
              v-for="(gpa, year) in yearlyGpa"
              :key="year"
              class="yearly-item">
              <view class="year-title">{{ year }}学年</view>
              <view class="year-gpa">{{ gpa.weighted_gpa }}</view>
              <view class="year-detail">
                学分: {{ gpa.total_credit }} | 课程: {{ gpa.course_count }}
              </view>
            </view>
          </view>
        </uni-card>

        <!-- 按学期GPA分析 -->
        <uni-card title="按学期GPA分析" margin="12px 0" v-if="semesterGpa">
          <view class="semester-gpa-container">
            <view
              v-for="(gpa, semester) in semesterGpa"
              :key="semester"
              class="semester-item">
              <view class="semester-title">{{ semester }}</view>
              <view class="semester-gpa">{{ gpa.weighted_gpa }}</view>
              <view class="semester-detail">
                学分: {{ gpa.total_credit }} | 课程: {{ gpa.course_count }}
              </view>
            </view>
          </view>
        </uni-card>
      </view>

      <!-- 成绩列表 -->
      <uni-card
        v-for="item in semesters"
        :key="item.semesterName"
        :title="item.semesterName"
        margin="12px 0">
        <uni-list>
          <uni-list-item
            v-for="grade in item.grades"
            :key="grade.courseCode"
            :title="grade.courseName"
            :note="`学分: ${grade.credit} | 绩点: ${grade.gpa}`"
            :right-text="grade.score"></uni-list-item>
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

// GPA分析样式
.gpa-section {
  margin-bottom: 20rpx;
}

// 主要GPA指标样式
.main-gpa-container {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
}

.main-gpa-item {
  flex: 1;
  text-align: center;

  &.highlight {
    background-color: #f0f9ff;
    border-radius: 12rpx;
    padding: 20rpx 10rpx;
    margin: 0 10rpx;
  }
}

.gpa-label {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 10rpx;
}

.gpa-value {
  font-size: 48rpx;
  font-weight: bold;
  color: #07c160;
  margin-bottom: 8rpx;

  &.primary {
    color: #1890ff;
    font-size: 52rpx;
  }
}

.gpa-detail {
  font-size: 22rpx;
  color: #999;
}

.gpa-note {
  font-size: 20rpx;
  color: #999;
  margin-top: 5rpx;
}

.gpa-divider {
  width: 2rpx;
  height: 100rpx;
  background-color: #eee;
  margin: 0 15rpx;
}

.total-courses {
  text-align: center;
  font-size: 24rpx;
  color: #666;
  padding-top: 15rpx;
  border-top: 1px solid #eee;
}

// 按学年GPA样式
.yearly-gpa-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  padding: 10rpx 0;
}

.yearly-item {
  flex: 1;
  min-width: calc(50% - 10rpx);
  background-color: #fafafa;
  border-radius: 12rpx;
  padding: 25rpx 20rpx;
  text-align: center;
}

.year-title {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 12rpx;
}

.year-gpa {
  font-size: 42rpx;
  font-weight: bold;
  color: #1890ff;
  margin-bottom: 8rpx;
}

.year-detail {
  font-size: 22rpx;
  color: #999;
}

// 按学期GPA样式
.semester-gpa-container {
  display: flex;
  flex-direction: column;
  gap: 15rpx;
  padding: 10rpx 0;
}

.semester-item {
  display: flex;
  align-items: center;
  background-color: #fafafa;
  border-radius: 8rpx;
  padding: 20rpx;
}

.semester-title {
  flex: 1;
  font-size: 28rpx;
  font-weight: 500;
  color: #333;
}

.semester-gpa {
  font-size: 36rpx;
  font-weight: bold;
  color: #52c41a;
  margin-right: 15rpx;
}

.semester-detail {
  font-size: 22rpx;
  color: #999;
  text-align: right;
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
  font-size: 36rpx !important;
  font-weight: bold !important;
  color: #07c160 !important;
}
</style>
