<template>
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

      <button class="action-btn btn-secondary" @click="handleShareSite">
        <uni-icons type="redo" size="20"></uni-icons>
        <text>分享本站</text>
      </button>
    </view>
  </ModernCard>
</template>

<script setup>
import ModernCard from "../../components/ModernCard/ModernCard.vue";

const emit = defineEmits([
  'refresh',
  'logout',
  'userAgreement',
  'clearCache',
  'changelog',
  'contact',
  'feedback',
  'sponsorList',
  'shareSite'
]);

const handleRefresh = () => emit('refresh');
const handleLogout = () => emit('logout');
const handleUserAgreement = () => emit('userAgreement');
const handleClearCache = () => emit('clearCache');
const handleChangelog = () => emit('changelog');
const handleContact = () => emit('contact');
const handleFeedback = () => emit('feedback');
const handleSponsorList = () => emit('sponsorList');
const handleShareSite = () => emit('shareSite');
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  height: 72rpx;
  padding: 0 16rpx;
  border-radius: 16rpx;
  font-size: 26rpx;
  font-weight: 500;
  transition: all 0.2s ease;
  margin: 0;
  line-height: 1;

  &::after {
    border: none;
  }

  .uni-icons,
  text {
    transition: all 0.2s ease;
  }
}

.btn-primary {
  background-color: #7F4515;
  color: #ffffff;
  border: 1px solid #7F4515;

  .uni-icons {
    color: #ffffff !important;
  }

  &:active {
    background-color: #6a3a12;
    border-color: #6a3a12;
  }
}

.btn-danger {
  background-color: #fff5f5;
  color: #f56c6c;
  border: 1px solid #fde2e2;

  .uni-icons {
    color: #f56c6c !important;
  }

  &:active {
    background-color: #fef0f0;
    border-color: #f56c6c;
  }
}

.btn-secondary {
  background-color: #f7f7f7;
  color: #606266;
  border: 1px solid #e0e0e0;

  .uni-icons {
    color: #606266 !important;
  }

  &:active {
    background-color: #e9e9e9;
    border-color: #c0c0c0;
  }
}
</style>
