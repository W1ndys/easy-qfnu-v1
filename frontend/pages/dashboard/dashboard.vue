<template>
  <view class="user-profile-page-wrapper">
    <PageLayout>
      <view class="page-rounded-container">
        <!-- 用户信息卡片 -->
        <ProfileCard ref="profileCardRef" />

        <!-- 公告栏 -->
        <NoticeBar :notice-data="noticeData" @click="openNoticeModal" />

        <!-- 功能网格 -->
        <FeatureGrid :features="features" @navigate="handleNavigate" />

        <!-- 系统操作 -->
        <SystemActions @refresh="handleRefresh" @logout="handleLogout" @userAgreement="handleUserAgreement"
          @clearCache="handleClearCache" @changelog="handleChangelog" @contact="handleContact"
          @feedback="handleFeedback" @sponsorList="handleSponsorList" @shareSite="handleShareSite" />

        <!-- 支持开发卡片 -->
        <SupportCard @imageError="handleImageError" @imageLoad="handleImageLoad" />
      </view>
    </PageLayout>

    <!-- 公告弹窗 -->
    <NoticeModal ref="noticeModalRef" :notice-data="noticeData" @popupChange="handleNoticePopupChange" />

    <!-- 校历弹窗 -->
    <CalendarModal ref="calendarModalRef" @imageError="handleCalendarImageError" @imageLoad="handleCalendarImageLoad" />
  </view>
</template>

<script setup>
import PageLayout from "../../components/PageLayout/PageLayout.vue";

// 导入模块化组件
import ProfileCard from "./ProfileCard.vue";
import NoticeBar from "./NoticeBar.vue";
import FeatureGrid from "./FeatureGrid.vue";
import SystemActions from "./SystemActions.vue";
import SupportCard from "./SupportCard.vue";
import NoticeModal from "./NoticeModal.vue";
import CalendarModal from "./CalendarModal.vue";

// 导入业务逻辑
import { useDashboard } from "./dashboard.js";

// 使用业务逻辑
const {
  // 数据
  noticeModalRef,
  calendarModalRef,
  profileCardRef,
  noticeData,
  features,

  // 方法
  openNoticeModal,
  handleNoticePopupChange,
  handleNavigate,
  handleRefresh,
  handleLogout,
  handleUserAgreement,
  handleClearCache,
  handleChangelog,
  handleContact,
  handleFeedback,
  handleSponsorList,
  handleShareSite,
  handleImageError,
  handleImageLoad,
  handleCalendarImageError,
  handleCalendarImageLoad,

  // 初始化
  initDashboard
} = useDashboard();

// 初始化
initDashboard();
</script>

<style lang="scss" scoped>
@import "./dashboard.scss";
</style>