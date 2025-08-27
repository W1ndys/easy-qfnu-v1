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
import systemActionsLogic from "./SystemActions.js";

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
@import "./SystemActions.scss";
</style>
