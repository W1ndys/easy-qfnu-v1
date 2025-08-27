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
import GradesScript from './grades.js'
export default GradesScript
</script>

<style lang="scss" scoped>
@import './grades.scss';
</style>