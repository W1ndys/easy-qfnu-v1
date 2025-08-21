<template>
  <PageLayout>
    <!-- 加载状态 -->
    <LoadingScreen v-if="isLoading" text="正在从教务系统同步成绩..." />

    <!-- 内容区域：卡片容器（圆角）-->
    <view v-else class="page-rounded-container">
      <!-- 空状态 -->
      <EmptyState
        v-if="semesters.length === 0"
        icon-type="info-filled"
        title="没有查询到任何成绩记录"
        description="请检查网络连接或稍后重试"
        :show-retry="true"
        @retry="fetchGrades" />

      <!-- 有数据时显示 -->
      <view v-else>
        <!-- GPA分析模块 -->
        <GPAAnalysis
          v-if="gpaAnalysis"
          :gpa-analysis="gpaAnalysis"
          :effective-gpa="effectiveGpa"
          :yearly-gpa="yearlyGpa"
          :semester-gpa="semesterGpa"
          :total-courses="totalCourses" />

        <!-- 自定义GPA计算区域 -->
        <view class="custom-gpa-section">
          <view class="custom-gpa-header" @click="toggleCustomGPA">
            <view class="header-left">
              <text class="custom-gpa-title">自定义GPA计算（有bug暂时不要用）</text>
              <text class="custom-gpa-desc">排除指定课程重新计算GPA</text>
            </view>
            <view class="header-right">
              <text class="toggle-icon" :class="{ 'expanded': showCustomGPA }">
                {{ showCustomGPA ? '收起' : '展开' }}
              </text>
            </view>
          </view>

          <!-- 自定义GPA计算内容 -->
          <view v-if="showCustomGPA" class="custom-gpa-content">
            <!-- 提示信息 -->
            <view class="tip-section">
              <view class="tip-icon">⚠️</view>
              <text class="tip-text">勾选的课程将被排除，不参与GPA计算</text>
            </view>

            <!-- 选项设置 -->
            <view class="options-section">
              <view class="option-item">
                <checkbox-group @change="onRemoveDuplicatesChange">
                  <checkbox value="remove" :checked="removeDuplicates" />
                  <text class="option-text">去除重修补考记录（只保留最高成绩）</text>
                </checkbox-group>
              </view>
            </view>

            <!-- 课程选择列表 -->
            <view class="courses-section">
              <view class="section-header">
                <text class="section-title">选择要排除的课程：</text>
                <view class="selection-actions">
                  <text class="action-btn" @click="selectAll">全选</text>
                  <text class="action-btn" @click="clearAll">清空</text>
                </view>
              </view>
              
              <view class="courses-grid">
                <view 
                  v-for="(course, index) in allCourses" 
                  :key="course.index || index"
                  class="course-card"
                  :class="{ 'excluded': excludedCourses.includes(index) }"
                  @click="toggleCourse(index)">
                  <view class="course-checkbox">
                    <checkbox :value="index.toString()" :checked="excludedCourses.includes(index)" />
                  </view>
                  <view class="course-content">
                    <text class="course-name">{{ course.courseName }}</text>
                    <view class="course-info">
                      <text class="info-item">{{ course.credit }}学分</text>
                      <text class="info-item grade">{{ course.score }}</text>
                      <text class="info-item semester">{{ course.semester }}</text>
                    </view>
                  </view>
                </view>
              </view>
            </view>

            <!-- 计算操作区 -->
            <view class="calculate-section">
              <view class="exclude-summary">
                <text class="summary-text">
                  已选择排除 {{ excludedCourses.length }} 门课程
                </text>
              </view>
              <button 
                class="calculate-btn" 
                @click="calculateCustomGPA"
                :disabled="isCalculating">
                {{ isCalculating ? '计算中...' : '重新计算GPA' }}
              </button>
            </view>

            <!-- 计算结果显示 -->
            <view v-if="customGPAResult" class="result-section">
              <view class="result-header">
                <text class="result-title">自定义计算结果</text>
              </view>
              <view class="result-content">
                <view class="gpa-display">
                  <text class="gpa-label">加权平均GPA</text>
                  <text class="gpa-value">{{ customGPAResult.weighted_gpa?.toFixed(2) || '0.00' }}</text>
                </view>
                <view class="result-stats">
                  <view class="stat-item">
                    <text class="stat-label">总学分</text>
                    <text class="stat-value">{{ customGPAResult.total_credit || 0 }}</text>
                  </view>
                  <view class="stat-item">
                    <text class="stat-label">课程数量</text>
                    <text class="stat-value">{{ customGPAResult.course_count || 0 }}</text>
                  </view>
                  <view class="stat-item">
                    <text class="stat-label">排除课程</text>
                    <text class="stat-value">{{ excludedCourses.length }}</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>

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

// 自定义GPA计算相关状态
const showCustomGPA = ref(false);
const allCourses = ref([]);
const excludedCourses = ref([]);
const removeDuplicates = ref(true);
const isCalculating = ref(false);
const customGPAResult = ref(null);

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
      url: `${getApp().globalData.apiBaseURL}/api/v1/grades`,
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

      // 更新所有课程列表，用于自定义GPA计算
      allCourses.value = rawGrades || [];
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

// 显示自定义GPA计算区域
const toggleCustomGPA = () => {
  showCustomGPA.value = !showCustomGPA.value;
  if (showCustomGPA.value) {
    // 展开时重置状态
    excludedCourses.value = [];
    customGPAResult.value = null;
  }
};

// 切换课程选择状态
const toggleCourse = (index) => {
  const excludedIndex = excludedCourses.value.indexOf(index);
  if (excludedIndex > -1) {
    excludedCourses.value.splice(excludedIndex, 1);
  } else {
    excludedCourses.value.push(index);
  }
  // 选择状态改变时清除之前的计算结果
  customGPAResult.value = null;
};

// 全选课程
const selectAll = () => {
  excludedCourses.value = allCourses.value.map((_, index) => index);
  customGPAResult.value = null;
};

// 清空选择
const clearAll = () => {
  excludedCourses.value = [];
  customGPAResult.value = null;
};

// 去重修补考选项变化
const onRemoveDuplicatesChange = (e) => {
  removeDuplicates.value = e.detail.value.includes('remove');
  customGPAResult.value = null;
};

// 计算自定义GPA
const calculateCustomGPA = async () => {
  const token = uni.getStorageSync("token");
  if (!token) {
    uni.showToast({ title: "请先登录", icon: "none" });
    return;
  }

  isCalculating.value = true;

  try {
    const res = await uni.request({
      url: `${getApp().globalData.apiBaseURL}/api/v1/gpa/calculate`,
      method: "POST",
      header: {
        Authorization: "Bearer " + token,
        "Content-Type": "application/json"
      },
      data: {
        exclude_indices: excludedCourses.value,
        remove_duplicates: removeDuplicates.value
      }
    });

    if (res.statusCode === 200 && res.data.success) {
      customGPAResult.value = res.data.data;
      uni.showToast({ title: "GPA计算完成", icon: "success" });
    } else if (res.statusCode === 401) {
      uni.removeStorageSync("token");
      uni.showToast({ title: "登录已过期，请重新登录", icon: "none" });
      setTimeout(() => {
        uni.reLaunch({ url: "/pages/index/index" });
      }, 1500);
    } else {
      const errorMessage = res.data.detail || "GPA计算失败";
      uni.showToast({ title: errorMessage, icon: "none" });
    }
  } catch (error) {
    console.error("GPA计算请求失败", error);
    uni.showToast({ title: "网络连接失败", icon: "none" });
  } finally {
    isCalculating.value = false;
  }
};
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

// 成绩页外层圆角容器
.page-rounded-container {
  background: #ffffff;
  border-radius: 40rpx;
  padding: 30rpx;
  box-shadow: 0 20rpx 60rpx var(--shadow-light);
  border: 1rpx solid var(--border-light);
}

// 自定义GPA计算区域
.custom-gpa-section {
  margin: 30rpx 0;
  background: #ffffff;
  border-radius: 20rpx;
  border: 1rpx solid #e9ecef;
  overflow: hidden;
  
  .custom-gpa-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 30rpx;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    cursor: pointer;
    
    .header-left {
      .custom-gpa-title {
        display: block;
        font-size: 36rpx;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 8rpx;
      }
      
      .custom-gpa-desc {
        font-size: 26rpx;
        color: rgba(255, 255, 255, 0.8);
      }
    }
    
    .header-right {
      .toggle-icon {
        font-size: 28rpx;
        color: rgba(255, 255, 255, 0.9);
        padding: 15rpx 25rpx;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 20rpx;
        border: 1rpx solid rgba(255, 255, 255, 0.3);
        
        &.expanded {
          background: rgba(255, 255, 255, 0.3);
        }
      }
    }
  }
  
  .custom-gpa-content {
    padding: 30rpx;
  }
}

// 提示信息
.tip-section {
  display: flex;
  align-items: center;
  padding: 20rpx;
  background: #fff3cd;
  border-radius: 12rpx;
  margin-bottom: 30rpx;
  border-left: 6rpx solid #ffc107;
  
  .tip-icon {
    font-size: 28rpx;
    margin-right: 12rpx;
  }
  
  .tip-text {
    color: #856404;
    font-size: 26rpx;
    line-height: 1.4;
  }
}

// 选项设置
.options-section {
  margin-bottom: 30rpx;
  
  .option-item {
    display: flex;
    align-items: center;
    padding: 20rpx;
    background: #f8f9fa;
    border-radius: 12rpx;
    
    .option-text {
      margin-left: 15rpx;
      font-size: 28rpx;
      color: #333333;
    }
  }
}

// 课程选择区域
.courses-section {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
    
    .section-title {
      font-size: 30rpx;
      font-weight: bold;
      color: #333333;
    }
    
    .selection-actions {
      display: flex;
      gap: 15rpx;
      
      .action-btn {
        font-size: 26rpx;
        color: #007bff;
        padding: 8rpx 16rpx;
        background: #e3f2fd;
        border-radius: 15rpx;
        
        &:active {
          background: #bbdefb;
        }
      }
    }
  }
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300rpx, 1fr));
  gap: 20rpx;
  max-height: 600rpx;
  overflow-y: auto;
}

.course-card {
  display: flex;
  align-items: flex-start;
  padding: 20rpx;
  background: #f8f9fa;
  border-radius: 12rpx;
  border: 2rpx solid transparent;
  transition: all 0.2s ease;
  
  &.excluded {
    background: #ffe6e6;
    border-color: #ff6b6b;
  }
  
  .course-checkbox {
    margin-right: 15rpx;
    margin-top: 5rpx;
  }
  
  .course-content {
    flex: 1;
    min-width: 0;
    
    .course-name {
      display: block;
      font-size: 28rpx;
      font-weight: bold;
      color: #333333;
      margin-bottom: 12rpx;
      line-height: 1.3;
      word-break: break-all;
    }
    
    .course-info {
      display: flex;
      flex-wrap: wrap;
      gap: 8rpx;
      
      .info-item {
        font-size: 22rpx;
        padding: 6rpx 10rpx;
        background: #ffffff;
        border-radius: 8rpx;
        color: #666666;
        
        &.grade {
          color: #28a745;
          font-weight: bold;
        }
        
        &.semester {
          color: #6c757d;
        }
      }
    }
  }
}

// 计算操作区
.calculate-section {
  margin: 30rpx 0;
  padding: 25rpx;
  background: #f8f9fa;
  border-radius: 12rpx;
  
  .exclude-summary {
    margin-bottom: 20rpx;
    text-align: center;
    
    .summary-text {
      font-size: 28rpx;
      color: #666666;
    }
  }
  
  .calculate-btn {
    width: 100%;
    background: linear-gradient(135deg, #28a745, #20c997);
    color: #ffffff;
    border: none;
    border-radius: 12rpx;
    padding: 28rpx;
    font-size: 32rpx;
    font-weight: bold;
    
    &:disabled {
      background: #6c757d;
    }
    
    &:active:not(:disabled) {
      opacity: 0.8;
    }
  }
}

// 计算结果显示
.result-section {
  margin-top: 30rpx;
  background: #e8f5e8;
  border-radius: 12rpx;
  border: 1rpx solid #28a745;
  
  .result-header {
    padding: 20rpx 25rpx;
    border-bottom: 1rpx solid #c3e6cb;
    
    .result-title {
      font-size: 30rpx;
      font-weight: bold;
      color: #155724;
    }
  }
  
  .result-content {
    padding: 25rpx;
  }
  
  .gpa-display {
    text-align: center;
    margin-bottom: 30rpx;
    
    .gpa-label {
      display: block;
      font-size: 26rpx;
      color: #666666;
      margin-bottom: 10rpx;
    }
    
    .gpa-value {
      display: block;
      font-size: 72rpx;
      font-weight: bold;
      color: #28a745;
    }
  }
  
  .result-stats {
    display: flex;
    justify-content: space-around;
    
    .stat-item {
      text-align: center;
      
      .stat-label {
        display: block;
        font-size: 22rpx;
        color: #666666;
        margin-bottom: 8rpx;
      }
      
      .stat-value {
        display: block;
        font-size: 36rpx;
        font-weight: bold;
        color: #333333;
      }
    }
  }
}
</style>
