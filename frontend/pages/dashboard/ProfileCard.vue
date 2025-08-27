<template>
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
</template>

<script setup>
import ModernCard from "../../components/ModernCard/ModernCard.vue";
import profileCardLogic from "./ProfileCard.js";

defineProps({
  profile: {
    type: Object,
    required: true,
    default: () => ({
      student_name: "W1ndys",
      student_id: "加载中...",
      college: "曲奇学院",
      major: "曲奇专业",
      class_name: "22曲奇班",
    })
  }
});
</script>

<style lang="scss" scoped>
@import "./ProfileCard.scss";
</style>
