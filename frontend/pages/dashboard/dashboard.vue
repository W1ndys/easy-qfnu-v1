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
import { ref, nextTick } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import { decode } from "../../utils/jwt-decode.js";

import PageLayout from "../../components/PageLayout/PageLayout.vue";
import ProfileCard from "./ProfileCard.vue";
import NoticeBar from "./NoticeBar.vue";
import FeatureGrid from "./FeatureGrid.vue";
import SystemActions from "./SystemActions.vue";
import SupportCard from "./SupportCard.vue";
import NoticeModal from "./NoticeModal.vue";
import CalendarModal from "./CalendarModal.vue";

// ==================== Dashboard Logic ====================
const noticeModalRef = ref(null);
const calendarModalRef = ref(null);
const profileCardRef = ref(null);

const noticeData = ref({
  version: "8",
  title: "重要通知：请加用户群防走丢！",
  content: `<div style="line-height: 1.6;">
            <p style="margin-bottom: 16rpx;">我们新增了用户QQ群，欢迎加入</p>
            <p style="margin-bottom: 16rpx;">后期很有可能会推出QQ号强绑定，需要加群使用，请尽快加群，群额度有限</p>
            <p style="margin-bottom: 16rpx; color: red;">仪表盘下方新增了分享本站功能，欢迎分享给朋友</p>
            <p style="margin-bottom: 16rpx;">时间紧张，本网站即将面临四个月的暂停开发，2025年12月后左右恢复开发进度</p>
            <p style="margin-bottom: 16rpx; color: red;">开学快乐！</p>
            <p style="margin-bottom: 16rpx; color: red;">七夕快乐！</p>
        </div>`,
  timestamp: Date.now(),
  forceShow: false
});

const NOTICE_READ_KEY = "notice_read_version";

const checkNoticeUpdate = () => {
  const remoteNotice = noticeData.value;
  const lastReadVersion = uni.getStorageSync(NOTICE_READ_KEY);
  if (remoteNotice.version !== lastReadVersion || remoteNotice.forceShow) {
    nextTick(() => openNoticeModal());
  }
};

const openNoticeModal = () => {
  if (noticeModalRef.value) {
    noticeModalRef.value.openModal();
  }
};

const handleNoticePopupChange = (e) => {
  if (!e.show) {
    uni.setStorageSync(NOTICE_READ_KEY, noticeData.value.version);
  }
};

const features = ref([
  { text: "今日课表", description: "实时查看今日课表", icon: "calendar", url: "/pages/classtable/classtable" },
  { text: "成绩分析", description: "查看成绩与GPA分析", icon: "paperplane", url: "/pages/grades/grades" },
  { text: "平均分查询", description: "查看课程平均分数据", icon: "bars", url: "/pages/average-scores/average-scores" },
  { text: "选课推荐", description: "智能推荐选课方案", icon: "star", url: "https://doc.easy-qfnu.top/EasySelectCourse/CourseSelectionRecommendation/", external: true },
  { text: "培养方案", description: "查看模块完成进度", icon: "list", url: "/pages/course-plan/course-plan" },
  { text: "选课查询", description: "支持选课模块探测", icon: "checkmarkempty", url: "/pages/pre-select-course/pre-select-course" },
  { text: "查看校历", description: "查看最新校历", icon: "calendar", url: "calendar", external: false },
  { text: "无课教室", description: "查询空闲教室", icon: "home", url: "" },
  { text: "无考教室", description: "查询无考试教室", icon: "compose", url: "" },
  { text: "排名查询", description: "即将推出", icon: "medal", url: "" },
  { text: "更多功能", description: "敬请期待", icon: "gear", url: "" },
]);

const checkLoginStatus = () => {
  const token = uni.getStorageSync("token");
  if (!token) {
    uni.reLaunch({ url: "/pages/index/index" });
    return;
  }
  try {
    decode(token);
  } catch (error) {
    uni.removeStorageSync("token");
    uni.reLaunch({ url: "/pages/index/index" });
  }
};

const handleNavigate = (index) => {
  const targetPage = features.value[index];
  if (targetPage.url === "calendar") {
    calendarModalRef.value.openModal();
  } else if (targetPage.external) {
    handleExternalLink(targetPage.url);
  } else if (targetPage.url) {
    uni.navigateTo({ url: targetPage.url });
  } else {
    uni.showToast({ title: "功能正在开发中...", icon: "none" });
  }
};

const handleRefresh = () => {
  if (profileCardRef.value) {
    profileCardRef.value.refreshProfile();
  }
};

const handleLogout = () => {
  uni.showModal({
    title: "确认退出",
    content: "确定要退出登录吗？",
    success: (res) => {
      if (res.confirm) {
        uni.removeStorageSync("token");
        if (profileCardRef.value) {
          profileCardRef.value.clearAllProfiles();
        }
        uni.reLaunch({ url: "/pages/index/index" });
      }
    },
  });
};

const handleClearCache = () => {
  uni.showModal({
    title: "清除缓存",
    content: "确定要清除所有本地缓存数据吗？",
    success: (res) => {
      if (res.confirm) {
        const token = uni.getStorageSync("token");
        uni.clearStorageSync();
        if (token) {
          uni.setStorageSync("token", token);
        }
        if (profileCardRef.value) {
          profileCardRef.value.clearProfile();
        }
        uni.showToast({ title: "缓存已清除", icon: "success" });
      }
    },
  });
};

const handleExternalLink = (url) => {
  if (typeof window !== 'undefined') {
    window.open(url, "_blank");
  } else if (typeof plus !== 'undefined') {
    plus.runtime.openURL(url);
  } else {
    uni.setClipboardData({
      data: url,
      success: () => {
        uni.showToast({
          title: "外链已复制,请在浏览器中打开",
          icon: "success",
          duration: 3000
        });
      }
    });
  }
};
const handleUserAgreement = () => handleExternalLink("https://cq4hqujcxu3.feishu.cn/docx/EYE6d5ufAoQt5Axx7MFc4XMrnAf");
const handleChangelog = () => handleExternalLink("https://cq4hqujcxu3.feishu.cn/docx/BO2od7OI8omtmTxGkB0cn305nFl");
const handleContact = () => handleExternalLink("https://qm.qq.com/q/WBCJEU82A2");
const handleFeedback = () => handleExternalLink("https://cq4hqujcxu3.feishu.cn/share/base/form/shrcnojLq3xgJ5m5Gzn5V87poHZ");
const handleSponsorList = () => handleExternalLink("https://cq4hqujcxu3.feishu.cn/docx/DE9Ed1l5iofB0exEYZncwMeenvd");

const handleShareSite = () => {
  uni.setClipboardData({ data: '我发现一个超级好用的曲师大教务工具... https://easy-qfnu.top' });
};

const handleImageError = () => { };
const handleImageLoad = () => { };
const handleCalendarImageError = () => { };
const handleCalendarImageLoad = () => { };

onLoad(() => {
  checkLoginStatus();
  checkNoticeUpdate();
});

onShow(() => {
  checkLoginStatus();
});

</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

.user-profile-page-wrapper {
  width: 100%;
  min-height: 100vh;
}

.page-rounded-container {
  background: #fff;
  border-radius: 32rpx;
  padding: 12rpx 8rpx;
  box-shadow: 0 8rpx 24rpx var(--shadow-light);
  border: 1rpx solid var(--border-light);
}
</style>