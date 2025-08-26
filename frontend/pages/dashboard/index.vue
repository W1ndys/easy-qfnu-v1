<template>
  <view class="user-profile-page-wrapper">
    <PageLayout>
      <view class="page-rounded-container">
        <ModernCard class="profile-card" highlight>
          <view class="profile-content">
            <view class="identity-section">
              <view class="avatar-wrapper">
                <image class="avatar" src="https://pic1.zhimg.com/80/v2-82c1c70c69720aadac79594ea50ed4a7.png"
                  mode="aspectFit"></image>
                <view class="status-indicator"></view>
              </view>
              <view class="identity-info">
                <text class="welcome-text">欢迎回来~</text>
                <text class="user-name">{{ profile.student_name }}</text>
                <text class="user-id">{{ profile.student_id }}</text>
              </view>
            </view>
            <view class="details-section">
              <view class="detail-item">
                <text class="detail-label">学院</text>
                <text class="detail-value">{{ profile.college }}</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">专业</text>
                <text class="detail-value">{{ profile.major }}</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">班级</text>
                <text class="detail-value">{{ profile.class_name }}</text>
              </view>
            </view>
          </view>
        </ModernCard>

        <view class="notice-bar" @click="openNoticeModal">
          <uni-icons class="notice-icon" type="sound" size="20" color="#FF6B35"></uni-icons>
          <text class="notice-text">系统正在测试阶段，点击查看QQ群信息</text>
          <uni-icons type="right" size="16" color="#C0C4CC"></uni-icons>
        </view>

        <ModernCard class="grid-card">
          <view class="grid-title">核心功能</view>
          <view class="grid-2x2">
            <view v-for="(item, index) in features" :key="index" class="grid-cell" :class="{ disabled: !item.url }"
              @click="handleNavigate(index)">
              <view class="cell-icon">
                <uni-icons :type="item.icon" size="30" :color="item.url ? '#7F4515' : '#C0C6CF'" />
              </view>
              <text class="cell-title">{{ item.text }}</text>
              <text v-if="item.description" class="cell-desc">{{
                item.description
              }}</text>
            </view>
          </view>
        </ModernCard>

        <ModernCard title="系统操作">
          <view class="quick-actions">
            <button class="action-btn btn-primary" @click="handleRefresh">
              <uni-icons type="refresh" size="20"></uni-icons>
              <text>刷新数据</text>
            </button>

            <button class="action-btn btn-danger" @click="handleLogout">
              <uni-icons type="closeempty" size="20"></uni-icons>
              <text>退出登录</text>
            </button>

            <button class="action-btn btn-secondary" @click="handleUserAgreement">
              <uni-icons type="paperplane" size="20"></uni-icons>
              <text>用户协议</text>
            </button>

            <button class="action-btn btn-danger" @click="handleClearCache">
              <uni-icons type="trash" size="20"></uni-icons>
              <text>清除缓存</text>
            </button>

            <button class="action-btn btn-secondary" @click="handleChangelog">
              <uni-icons type="list" size="20"></uni-icons>
              <text>更新日志</text>
            </button>

            <button class="action-btn btn-secondary" @click="handleContact">
              <uni-icons type="chatbubble" size="20"></uni-icons>
              <text>联系作者</text>
            </button>

            <button class="action-btn btn-secondary" @click="handleFeedback">
              <uni-icons type="compose" size="20"></uni-icons>
              <text>意见建议</text>
            </button>

            <button class="action-btn btn-secondary" @click="handleSponsorList">
              <uni-icons type="heart" size="20"></uni-icons>
              <text>赞赏名单</text>
            </button>
          </view>
        </ModernCard>

        <ModernCard title="支持开发" class="support-card">
          <view class="support-content">
            <view class="support-text">
              <text class="support-title">助力项目发展</text>
              <text
                class="support-desc">本服务完全免费使用，服务器每日支出约为7元左右（选课高峰期翻2-3倍），以及前期服务器设备等支出几百依赖作者个人支出。如果想支持作者助力开发维护，欢迎赞赏~</text>
            </view>
            <view class="qr-code-container">
              <image class="qr-code"
                src="https://picx.zhimg.com/80/v2-076422270c197b0031c609e47be2e36c_720w.png?source=d16d100b"
                mode="aspectFit" @error="handleImageError" @load="handleImageLoad">
              </image>
              <text class="qr-code-label">微信赞赏</text>
            </view>
          </view>
        </ModernCard>
      </view>
    </PageLayout>

    <uni-popup ref="noticePopup" type="center">
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">公告详情</text>
          <view class="popup-close-btn" @click="closeNoticeModal">
            <uni-icons type="closeempty" size="22" color="#909399"></uni-icons>
          </view>
        </view>
        <view class="popup-body">
          <view class="status-content-wrapper">
            <view class="status-header">
              <view class="status-icon warning">
                <uni-icons type="info" size="20" color="#FF6B35"></uni-icons>
              </view>
              <text class="status-title">系统状态</text>
            </view>
            <text class="status-text">该程序正在测试阶段，功能可能不稳定</text>
          </view>
          <view class="community-content-wrapper">
            <view class="community-header">
              <view class="community-icon">
                <uni-icons type="chatbubble" size="20" color="#7F4515"></uni-icons>
              </view>
              <text class="community-title">加入QQ群</text>
            </view>
            <view class="community-groups">
              <view class="group-item">
                <view class="group-info">
                  <view class="group-name">
                    <uni-icons type="sound" size="20" color="#7F4515"></uni-icons>
                    <text class="group-title">官方消息群</text>
                  </view>
                  <text class="group-desc">获取最新消息和通知</text>
                </view>
                <button class="copy-btn" @click="copyQQGroup">
                  <uni-icons type="copy" size="16" color="#7F4515"></uni-icons>
                  <text>复制群号</text>
                </button>
              </view>
              <view class="group-item">
                <view class="group-info">
                  <view class="group-name">
                    <uni-icons type="star" size="20" color="#7F4515"></uni-icons>
                    <text class="group-title">开发交流群</text>
                  </view>
                  <text class="group-desc">建议反馈、开发想法交流</text>
                </view>
                <button class="copy-btn" @click="copyDevQQGroup">
                  <uni-icons type="copy" size="16" color="#7F4515"></uni-icons>
                  <text>复制群号</text>
                </button>
              </view>
            </view>
          </view>
        </view>
      </view>
    </uni-popup>

    <!-- 校历弹窗 -->
    <uni-popup ref="calendarPopup" type="center">
      <view class="popup-content calendar-popup">
        <view class="popup-header">
          <text class="popup-title">校历</text>
          <view class="popup-close-btn" @click="closeCalendarModal">
            <uni-icons type="closeempty" size="22" color="#909399"></uni-icons>
          </view>
        </view>
        <view class="popup-body">
          <image class="calendar-image" src="https://pic1.zhimg.com/80/v2-495ef4f801960eb4dcbedb73d4514507.jpeg"
            mode="widthFix" @error="handleCalendarImageError" @load="handleCalendarImageLoad">
          </image>
        </view>
      </view>
    </uni-popup>
  </view>
</template>

<script setup>
// Script 部分无需任何改动
import { ref } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import { decode } from "../../utils/jwt-decode.js";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import ModernCard from "../../components/ModernCard/ModernCard.vue";

const noticePopup = ref(null);
const calendarPopup = ref(null);

const profile = ref({
  student_name: "W1ndys",
  student_id: "加载中...",
  college: "曲奇学院",
  major: "曲奇专业",
  class_name: "22曲奇班",
});

const features = ref([
  { text: "成绩查询", description: "查看成绩与GPA分析", icon: "paperplane", url: "/pages/grades/index" },
  { text: "平均分查询", description: "查看课程平均分数据", icon: "bars", url: "/pages/average-scores/index" },
  { text: "选课推荐", description: "智能推荐选课方案", icon: "star", url: "https://doc.easy-qfnu.top/EasySelectCourse/CourseSelectionRecommendation/", external: true },
  { text: "培养方案", description: "查看模块完成进度", icon: "list", url: "/pages/course-plan/index" },
  { text: "预选课查询", description: "支持选课模块探测", icon: "checkmarkempty", url: "/pages/pre-select-course/index" },
  { text: "查看校历", description: "查看最新校历", icon: "calendar", url: "calendar", external: false },
  { text: "课表查询", description: "即将推出", icon: "calendar", url: "" },
  { text: "排名查询", description: "即将推出", icon: "medal", url: "" },
  { text: "更多功能", description: "敬请期待", icon: "gear", url: "" },
]);

onLoad(() => { checkLoginStatus(); });
onShow(() => {
  // 只在需要时检查登录状态，避免重复请求
  const token = uni.getStorageSync("token");
  if (token && (!profile.value.student_id || profile.value.student_id === "加载中...")) {
    checkLoginStatus();
  }
});

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
        // 合并服务器数据，保持默认值作为后备
        const serverData = res.data.data;
        // 如果服务器返回了学号，则使用服务器数据；否则从token中获取
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
      // 不立即显示哈希值，保持默认的"加载中..."状态
      // profile.value.student_id = payload.sub;
      // 只在需要时才获取完整资料
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

const openNoticeModal = () => { if (noticePopup.value) noticePopup.value.open(); };
const closeNoticeModal = () => { if (noticePopup.value) noticePopup.value.close(); };

const openCalendarModal = () => { if (calendarPopup.value) calendarPopup.value.open(); };
const closeCalendarModal = () => { if (calendarPopup.value) calendarPopup.value.close(); };

const handleNavigate = (index) => {
  const targetPage = features.value[index];
  if (targetPage.url) {
    if (targetPage.url === "calendar") {
      // 特殊处理校历功能
      openCalendarModal();
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

const copyQQGroup = () => { uni.setClipboardData({ data: "1053432087", success: () => uni.showToast({ title: "QQ群号已复制", icon: "success" }) }); };
const copyDevQQGroup = () => { uni.setClipboardData({ data: "1057327742", success: () => uni.showToast({ title: "开发群号已复制", icon: "success" }) }); };

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

.profile-card {
  margin-bottom: 10rpx;

  :deep(.card-content) {
    padding: 12rpx 8rpx !important;
  }
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.identity-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24rpx;
  padding: 4rpx 0;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
}

.avatar {
  width: 110rpx;
  height: 110rpx;
  border-radius: 50%;
  border: 3rpx solid rgba(155, 4, 0, 0.1);
  box-shadow: 0 8rpx 20rpx rgba(155, 4, 0, 0.15);
}

.status-indicator {
  position: absolute;
  bottom: 8rpx;
  right: 8rpx;
  width: 22rpx;
  height: 22rpx;
  background: #52c41a;
  border-radius: 50%;
  border: 2rpx solid #ffffff;
}

.identity-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4rpx;
}

.welcome-text {
  font-size: 22rpx;
  color: var(--text-light);
  font-weight: 400;
  margin-bottom: 2rpx;
}

.user-name {
  font-size: 38rpx;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.user-id {
  font-size: 28rpx;
  font-weight: 500;
  color: var(--text-secondary);
  letter-spacing: 1rpx;
}

.details-section {
  border-top: 1rpx solid var(--border-light);
  padding-top: 12rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.detail-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6rpx 8rpx;
  background: rgba(127, 69, 21, 0.03);
  border: 1rpx solid rgba(127, 69, 21, 0.08);
  border-radius: 8rpx;
}

.detail-label {
  font-size: 24rpx;
  color: var(--text-light);
  font-weight: 500;
  min-width: 60rpx;
}

.detail-value {
  font-size: 26rpx;
  color: var(--text-primary);
  font-weight: 600;
  text-align: right;
  flex: 1;
}

.notice-bar {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 16rpx 20rpx;
  margin: 16rpx 0;
  background: linear-gradient(135deg, #fffaf3 0%, #fff7e6 100%);
  border: 1rpx solid rgba(255, 107, 53, 0.2);
  border-radius: var(--radius-medium);
  box-shadow: 0 4rpx 12rpx rgba(255, 107, 53, 0.05);
  transition: all 0.2s ease-in-out;

  &:active {
    transform: scale(0.98);
    box-shadow: none;
  }
}

.notice-icon {
  flex-shrink: 0;
}

.notice-text {
  flex: 1;
  font-size: 26rpx;
  color: #c46a32;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.popup-content {
  width: 90vw;
  max-width: 680rpx;
  background-color: #f8f8f8;
  border-radius: 24rpx;
  box-shadow: 0 10rpx 40rpx rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 32rpx;
  border-bottom: 1rpx solid var(--border-light);
}

.popup-title {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--text-primary);
}

.popup-close-btn {
  padding: 8rpx;
  border-radius: 50%;

  &:active {
    background-color: #e0e0e0;
  }
}

.popup-body {
  padding: 24rpx 32rpx;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  max-height: 70vh;
  overflow-y: auto;
}

.status-content-wrapper {
  background: #ffffff;
  padding: 20rpx;
  border-radius: var(--radius-medium);
  border: 1rpx solid var(--border-light);
}

.status-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.status-icon {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;

  &.warning {
    background: rgba(255, 107, 53, 0.1);
  }
}

.status-title {
  font-size: 28rpx;
  color: #ff6b35;
  font-weight: 700;
}

.status-text {
  font-size: 26rpx;
  color: #8b4513;
  line-height: 1.5;
  margin-top: 8rpx;
  padding-left: 60rpx;
}

.community-content-wrapper {
  background: #ffffff;
  padding: 20rpx;
  border-radius: var(--radius-medium);
  border: 1rpx solid var(--border-light);
}

.community-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid rgba(127, 69, 21, 0.1);
  margin-bottom: 16rpx;
}

.community-icon {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: rgba(127, 69, 21, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
}

.community-title {
  font-size: 28rpx;
  color: var(--text-primary);
  font-weight: 700;
}

.community-groups {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.group-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx;
  background: rgba(127, 69, 21, 0.03);
  border: 1rpx solid rgba(127, 69, 21, 0.08);
  border-radius: 12rpx;
}

.group-info {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
  flex: 1;
}

.group-name {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.group-title {
  font-size: 26rpx;
  color: var(--text-primary);
  font-weight: 600;
}

.group-desc {
  font-size: 22rpx;
  color: var(--text-secondary);
  line-height: 1.4;
  padding-left: 28rpx;
}

.copy-btn {
  display: flex;
  align-items: center;
  gap: 6rpx;
  padding: 8rpx 16rpx;
  background: rgba(127, 69, 21, 0.08);
  border: 1rpx solid rgba(127, 69, 21, 0.15);
  border-radius: 20rpx;
  font-size: 22rpx;
  color: #7f4515;
  font-weight: 500;
  transition: all 0.2s ease;
  min-width: 120rpx;
  justify-content: center;

  &::after {
    border: none;
  }

  &:active {
    background: rgba(127, 69, 21, 0.15);
    transform: scale(0.95);
  }

  text {
    font-weight: inherit;
  }
}

.grid-card {
  margin-bottom: 16rpx;

  :deep(.card-content) {
    padding: 12rpx 8rpx !important;
  }
}

.grid-title {
  font-size: 26rpx;
  margin-bottom: 8rpx;
}

.grid-2x2 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300rpx, 1fr));
  gap: 8rpx;

  @media (max-width: 750px) {
    grid-template-columns: repeat(auto-fit, minmax(280rpx, 1fr));
    gap: 12rpx;
  }

  @media (max-width: 500px) {
    grid-template-columns: repeat(auto-fit, minmax(240rpx, 1fr));
    gap: 8rpx;
  }
}

.grid-cell {
  background: #ffffff;
  border: 1rpx solid var(--border-light);
  border-radius: var(--radius-medium);
  padding: 12rpx 8rpx;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8rpx;
  transition: all 0.2s ease;
  min-height: 100rpx;

  &:active {
    transform: scale(0.98);
  }

  &:not(.disabled):hover {
    box-shadow: 0 12rpx 34rpx var(--shadow-light);
    transform: translateY(-2rpx);
  }

  &.disabled {
    opacity: 0.6;
  }
}

.cell-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  background: rgba(127, 69, 21, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cell-title {
  font-size: 30rpx;
  color: var(--text-primary);
  font-weight: 600;
}

.cell-desc {
  font-size: 24rpx;
  color: var(--text-light);
}

.support-card {
  margin-top: 16rpx;

  :deep(.card-content) {
    padding: 12rpx 8rpx !important;
  }
}

.support-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}

.support-text {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  text-align: center;
}

.support-title {
  font-size: 32rpx;
  color: var(--text-primary);
  font-weight: 600;
}

.support-desc {
  font-size: 26rpx;
  color: var(--text-secondary);
  line-height: 1.6;
  text-align: center;
}

.qr-code-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}

.qr-code {
  width: 220rpx;
  height: 220rpx;
  border-radius: var(--radius-medium);
  border: 1rpx solid var(--border-light);
  box-shadow: 0 8rpx 24rpx var(--shadow-light);
}

.qr-code-label {
  font-size: 24rpx;
  color: var(--text-light);
  text-align: center;
}

/* ==================== 校历弹窗样式 ==================== */
.calendar-popup {
  width: 95vw;
  max-width: 720rpx;
}

.calendar-image {
  width: 100%;
  border-radius: var(--radius-medium);
  box-shadow: 0 8rpx 24rpx var(--shadow-light);
}

/* ==================== MODIFICATION START: 系统操作按钮样式 ==================== */
.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr; // 保持两列布局
  gap: 16rpx; // 统一间距
}

// 按钮基础样式
.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  height: 72rpx; // 增加一些高度
  padding: 0 16rpx;
  border-radius: 16rpx;
  font-size: 26rpx;
  font-weight: 500;
  transition: all 0.2s ease;

  // uniapp 按钮样式重置
  margin: 0;
  line-height: 1;

  &::after {
    border: none;
  }

  // 图标和文字的样式由具体类控制
  .uni-icons,
  text {
    transition: all 0.2s ease;
  }
}

// 1. 主操作按钮 (实心填充)
.btn-primary {
  background-color: #7F4515; // 主题色
  color: #ffffff;
  border: 1px solid #7F4515;

  .uni-icons {
    color: #ffffff !important;
  }

  &:active {
    background-color: #6a3a12; // 点击时加深
    border-color: #6a3a12;
  }
}

// 2. 危险操作按钮 (线框)
.btn-danger {
  background-color: #fff5f5; // 浅红色底
  color: #f56c6c; // 危险红色
  border: 1px solid #fde2e2;

  .uni-icons {
    color: #f56c6c !important;
  }

  &:active {
    background-color: #fef0f0;
    border-color: #f56c6c; // 点击时边框加深
  }
}

// 3. 次要操作按钮 (线框)
.btn-secondary {
  background-color: #f7f7f7; // 极浅的灰色底
  color: #606266; // 中性文字色
  border: 1px solid #e0e0e0;

  .uni-icons {
    color: #606266 !important;
  }

  &:active {
    background-color: #e9e9e9;
    border-color: #c0c0c0;
  }
}

// 删除旧的、基于颜色的按钮样式
// .refresh-btn, .logout-btn, .clear-cache-btn, etc. { ... }
/* ==================== MODIFICATION END ==================== */
</style>