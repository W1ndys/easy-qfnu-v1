<template>
  <view class="user-profile-page-wrapper">
    <PageLayout>
      <view class="page-rounded-container">
        <!-- 用户信息卡片 -->
        <ProfileCard :profile="profile" />

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

// 导入模块化组件
import ProfileCard from "./ProfileCard.vue";
import NoticeBar from "./NoticeBar.vue";
import FeatureGrid from "./FeatureGrid.vue";
import SystemActions from "./SystemActions.vue";
import SupportCard from "./SupportCard.vue";
import NoticeModal from "./NoticeModal.vue";
import CalendarModal from "./CalendarModal.vue";

// 弹窗引用
const noticeModalRef = ref(null);
const calendarModalRef = ref(null);

// ==================== 公告机制 ====================
const noticeData = ref({
  version: "5",
  title: "重要通知：请加用户群防走丢！",
  content: `<div style="line-height: 1.6;">
    <p style="margin-bottom: 16rpx;">我们新增了用户QQ群，欢迎加入</p>
    <p style="margin-bottom: 16rpx;">后期很有可能会推出QQ号强绑定，需要加群使用，请尽快加群，群额度有限</p>
    <p style="margin-bottom: 16rpx; color: red;">仪表盘下方新增了分享本站功能，欢迎分享给朋友</p>
    <br>
    <p style="margin-bottom: 16rpx;">
      帮朋友转出奥创健身年卡，需要请联系QQ 
      <span style="color: #7F4515; font-weight: 600; user-select: all;">1053240065</span>
      （长按QQ号可复制，备注曲奇教务来的）
    </p>
  </div>`,
  timestamp: Date.now(),
  forceShow: false
});

const NOTICE_READ_KEY = "notice_read_version";

const checkNoticeUpdate = () => {
  const remoteNotice = noticeData.value;
  const lastReadVersion = uni.getStorageSync(NOTICE_READ_KEY);
  console.log(`当前公告版本: ${remoteNotice.version}, 已读版本: ${lastReadVersion}`);

  if (remoteNotice.version !== lastReadVersion || remoteNotice.forceShow) {
    console.log("检测到新公告或强制公告，准备弹窗。");
    nextTick(() => {
      openNoticeModal();
    });
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
    console.log(`公告版本 ${noticeData.value.version} 已通过关闭操作标记为已读。`);
  }
};

// ==================== 用户数据 ====================
const profile = ref({
  student_name: "W1ndys",
  student_id: "加载中...",
  college: "曲奇学院",
  major: "曲奇专业",
  class_name: "22曲奇班",
});

const features = ref([
  { text: "成绩查询", description: "查看成绩与GPA分析", icon: "paperplane", url: "/pages/grades/grades" },
  { text: "平均分查询", description: "查看课程平均分数据", icon: "bars", url: "/pages/average-scores/average-scores" },
  { text: "选课推荐", description: "智能推荐选课方案", icon: "star", url: "https://doc.easy-qfnu.top/EasySelectCourse/CourseSelectionRecommendation/", external: true },
  { text: "培养方案", description: "查看模块完成进度", icon: "list", url: "/pages/course-plan/course-plan" },
  { text: "预选课查询", description: "支持选课模块探测", icon: "checkmarkempty", url: "/pages/pre-select-course/pre-select-course" },
  { text: "查看校历", description: "查看最新校历", icon: "calendar", url: "calendar", external: false },
  { text: "课表查询", description: "即将推出", icon: "calendar", url: "" },
  { text: "排名查询", description: "即将推出", icon: "medal", url: "" },
  { text: "更多功能", description: "敬请期待", icon: "gear", url: "" },
]);

// ==================== 生命周期 ====================
onLoad(() => {
  checkLoginStatus();
  checkNoticeUpdate();
});

onShow(() => {
  const token = uni.getStorageSync("token");
  if (token && (!profile.value.student_id || profile.value.student_id === "加载中...")) {
    checkLoginStatus();
  }
});

// ==================== 数据获取 ====================
const fetchProfile = async () => {
  const token = uni.getStorageSync("token");
  if (!token) return;
  const baseURL = getApp().globalData.apiBaseURL;
  uni.request({
    url: `${baseURL}/api/v1/profile`,
    method: "GET",
    header: { Authorization: `Bearer ${token}` },
    success: (res) => {
      if (res.statusCode === 200 && res.data.success) {
        const serverData = res.data.data;
        const studentId = serverData.student_id || (() => {
          try {
            const payload = decode(token);
            return payload.sub;
          } catch (e) {
            return profile.value.student_id;
          }
        })();

        profile.value = {
          student_name: serverData.student_name || profile.value.student_name,
          student_id: studentId,
          college: serverData.college || profile.value.college,
          major: serverData.major || profile.value.major,
          class_name: serverData.class_name || profile.value.class_name,
        };
      } else {
        uni.showToast({ title: res.data.message || `获取信息失败 (${res.statusCode})`, icon: "none" });
        if (res.statusCode === 401) {
          uni.removeStorageSync("token");
          setTimeout(() => { uni.reLaunch({ url: "/pages/index/index" }); }, 1500);
        }
      }
    },
    fail: (err) => {
      console.error("获取个人信息请求失败", err);
      uni.showToast({ title: "网络请求失败，请稍后重试", icon: "none" });
    },
  });
};

const checkLoginStatus = () => {
  const token = uni.getStorageSync("token");
  if (!token) {
    uni.showToast({ title: "请先登录", icon: "none" });
    uni.reLaunch({ url: "/pages/index/index" });
    return;
  } else {
    try {
      const payload = decode(token);
      if (!profile.value.student_name || profile.value.student_name === "W1ndys") {
        fetchProfile();
      }
    } catch (error) {
      console.error("Token解析失败", error);
      uni.removeStorageSync("token");
      uni.showToast({ title: "凭证无效,请重新登录", icon: "none" });
      uni.reLaunch({ url: "/pages/index/index" });
      return;
    }
  }
};

// ==================== 事件处理 ====================
const handleNavigate = (index) => {
  const targetPage = features.value[index];
  if (targetPage.url) {
    if (targetPage.url === "calendar") {
      if (calendarModalRef.value) {
        calendarModalRef.value.openModal();
      }
    } else if (targetPage.external) {
      if (typeof window !== 'undefined') window.open(targetPage.url, "_blank");
      else if (typeof plus !== 'undefined') plus.runtime.openURL(targetPage.url);
      else uni.setClipboardData({ data: targetPage.url, success: () => uni.showToast({ title: "外链已复制,请在浏览器中打开", icon: "success", duration: 3000 }) });
    } else {
      uni.navigateTo({ url: targetPage.url });
    }
  } else {
    uni.showToast({ title: "功能正在开发中...", icon: "none" });
  }
};

const handleRefresh = () => {
  uni.showLoading({ title: "正在刷新..." });
  fetchProfile().finally(() => {
    uni.hideLoading();
    uni.showToast({ title: "数据已刷新", icon: "success" });
  });
};

const handleLogout = () => {
  uni.showModal({
    title: "确认退出", content: "确定要退出登录吗？", confirmColor: "#7F4515",
    success: (res) => {
      if (res.confirm) {
        uni.removeStorageSync("token");
        uni.showToast({ title: "已退出登录", icon: "success" });
        setTimeout(() => { uni.reLaunch({ url: "/pages/index/index" }); }, 1000);
      }
    },
  });
};

const handleClearCache = () => {
  uni.showModal({
    title: "清除缓存", content: "确定要清除所有本地缓存数据吗？这将清除除登录凭证外的所有本地数据。",
    confirmText: "清除", cancelText: "取消", confirmColor: "#ff4d4f",
    success: (res) => {
      if (res.confirm) {
        try {
          const token = uni.getStorageSync("token");
          uni.clearStorageSync();
          if (token) uni.setStorageSync("token", token);
          uni.showToast({ title: "缓存已清除", icon: "success", duration: 2000 });
        } catch (e) {
          uni.showToast({ title: "清除缓存失败", icon: "error" });
        }
      }
    },
  });
};

const handleUserAgreement = () => {
  const url = "https://cq4hqujcxu3.feishu.cn/docx/EYE6d5ufAoQt5Axx7MFc4XMrnAf";
  handleExternalLink("用户协议", url);
};

const handleChangelog = () => {
  const url = "https://cq4hqujcxu3.feishu.cn/docx/BO2od7OI8omtmTxGkB0cn305nFl";
  handleExternalLink("更新日志", url);
};

const handleContact = () => {
  const qqAddUrl = "https://qm.qq.com/q/WBCJEU82A2";
  handleExternalLink("添加QQ好友", qqAddUrl);
};

const handleFeedback = () => {
  const feedbackUrl = "https://cq4hqujcxu3.feishu.cn/share/base/form/shrcnojLq3xgJ5m5Gzn5V87poHZ";
  handleExternalLink("意见建议反馈", feedbackUrl);
};

const handleSponsorList = () => {
  const sponsorUrl = "https://cq4hqujcxu3.feishu.cn/docx/DE9Ed1l5iofB0exEYZncwMeenvd";
  handleExternalLink("赞赏名单", sponsorUrl);
};

const handleShareSite = () => {
  const shareText = `我发现一个超级好用的曲师大教务工具，你也来看看吧
多维度成绩分析、历史平均分查询、选课推荐、培养方案解析、预选课查询，各种功能~
地址：https://easy-qfnu.top`;

  uni.setClipboardData({
    data: shareText,
    success: () => {
      uni.showToast({
        title: "分享内容已复制到剪贴板",
        icon: "success",
        duration: 2000
      });
    },
    fail: () => {
      uni.showToast({
        title: "复制失败，请手动复制",
        icon: "none"
      });
    }
  });
};

const handleExternalLink = (title, url) => {
  if (typeof window !== 'undefined') window.open(url, "_blank");
  else if (typeof plus !== 'undefined') plus.runtime.openURL(url);
  else uni.setClipboardData({ data: url, success: () => uni.showToast({ title: "外链已复制,请在浏览器中打开", icon: "success", duration: 3000 }) });
};

const handleImageError = () => { uni.showToast({ title: "赞赏码加载失败", icon: "none" }); };
const handleImageLoad = () => { console.log("赞赏码加载成功"); };

const handleCalendarImageError = () => { uni.showToast({ title: "校历图片加载失败", icon: "none" }); };
const handleCalendarImageLoad = () => { console.log("校历图片加载成功"); };
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