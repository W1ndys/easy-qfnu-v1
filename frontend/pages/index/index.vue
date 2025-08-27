<template>
    <scroll-view class="container" scroll-y="true" @scrolltoupper="onPullRefresh">
        <!-- 顶部公告弹幕组件 -->
        <AnnouncementMarquee />

        <!-- 背景装饰 -->
        <view class="background-decoration">
            <view class="circle circle-1"></view>
            <view class="circle circle-2"></view>
            <view class="circle circle-3"></view>
        </view>

        <!-- 主内容区域 -->
        <view class="content-wrapper">
            <!-- Logo区域组件 -->
            <LogoSection />

            <!-- 登录表单组件 -->
            <LoginForm :formData="formData" :isLoading="isLoading" :rememberPassword="rememberPassword"
                :hasCachedCredentials="hasCachedCredentials" :agreed="agreed" @remember-change="onRememberChange"
                @agree-change="onAgreeChange" @clear-cache="clearCachedCredentials" @login="handleLoginClick"
                @open-agreement="openAgreement" @open-activation="openActivationPage" />
        </view>
    </scroll-view>
</template>

<script setup>
import { onLoad } from "@dcloudio/uni-app";
import AnnouncementMarquee from './AnnouncementMarquee.vue';
import LogoSection from './LogoSection.vue';
import LoginForm from './LoginForm.vue';
import { useLogin } from './useLogin.js';
import { useCredentialsCache } from './useCredentialsCache.js';
import { useExternalLinks } from './useExternalLinks.js';

// 使用组合式函数
const {
    formData,
    isLoading,
    agreed,
    checkLoginStatus,
    onAgreeChange,
    handleLogin,
    onPullRefresh
} = useLogin();

const {
    rememberPassword,
    hasCachedCredentials,
    loadCachedCredentials,
    saveCachedCredentials,
    clearCachedCredentials,
    onRememberChange
} = useCredentialsCache();

const {
    openAgreement,
    openActivationPage
} = useExternalLinks();

// 页面加载时初始化
onLoad(() => {
    checkLoginStatus();
    loadCachedCredentials(formData);
});

// 登录点击处理（包装原始登录函数并传入缓存保存函数）
const handleLoginClick = () => {
    handleLogin(rememberPassword.value, () => saveCachedCredentials(formData));
};
</script>

<style lang="scss" scoped>
@import './styles.scss';
</style>