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
import { ref, watch } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import AnnouncementMarquee from "./AnnouncementMarquee.vue";
import LogoSection from "./LogoSection.vue";
import LoginForm from "./LoginForm.vue";
import { isTokenValid } from "../../utils/jwt-decode.js";

// 使用组合式函数
// from useLogin
const formData = ref({
    studentId: "",
    password: "",
});
const isLoading = ref(false);
const agreed = ref(false);

// from useCredentialsCache
const rememberPassword = ref(false);
const hasCachedCredentials = ref(false);

// from useExternalLinks
const AGREEMENT_URL = "https://cq4hqujcxu3.feishu.cn/docx/EYE6d5ufAoQt5Axx7MFc4XMrnAf";
const ACTIVATION_URL = "http://ids.qfnu.edu.cn/retrieve-password/activationMobile/index.html";

// --- from useLogin.js ---
const STUDENT_ID_REGEX = /^\d{8,11}$/;

watch(
    () => formData.value.studentId,
    (val) => {
        const digits = (val || "").replace(/\D/g, "").slice(0, 11);
        if (digits !== val) formData.value.studentId = digits;
    }
);

const checkLoginStatus = () => {
    const token = uni.getStorageSync("token");

    if (token) {
        console.log("检测到缓存的token，开始验证有效性");

        try {
            if (isTokenValid(token)) {
                console.log("Token验证通过，准备跳转到dashboard");
                uni.reLaunch({
                    url: "/pages/dashboard/dashboard",
                });
            } else {
                console.log("Token无效，清除并停留在登录页");
                uni.removeStorageSync("token");
                uni.showToast({
                    title: "登录已过期，请重新登录",
                    icon: "none",
                });
            }
        } catch (error) {
            console.error("Token验证过程中出错:", error);
            uni.removeStorageSync("token");
            uni.showToast({
                title: "登录状态异常，请重新登录",
                icon: "none",
            });
        }
    }
};

const onAgreeChange = (e) => {
    try {
        agreed.value = Array.isArray(e.detail.value) && e.detail.value.includes("agree");
    } catch (err) {
        agreed.value = false;
    }
};

const handleLogin = async () => {
    // 简单的输入校验
    if (!formData.value.studentId || !formData.value.password) {
        uni.showToast({ title: "学号和密码不能为空", icon: "none" });
        return;
    }

    // 学号格式校验
    const sid = (formData.value.studentId || "").trim();
    if (!STUDENT_ID_REGEX.test(sid)) {
        uni.showToast({ title: "学号格式不正确", icon: "none" });
        return;
    }

    if (!agreed.value) {
        uni.showToast({ title: "请先阅读并同意用户协议", icon: "none" });
        return;
    }

    isLoading.value = true;

    try {
        const res = await uni.request({
            url: `${getApp().globalData.apiBaseURL}/api/v1/login`,
            method: "POST",
            data: {
                student_id: sid,
                password: formData.value.password,
            },
        });

        if (res.statusCode === 200 && res.data.access_token) {
            console.log("登录成功, Token:", res.data.access_token);

            // 保存账号密码到缓存（在登录成功后）
            saveCachedCredentials();

            uni.showToast({ title: "登录成功", icon: "success" });
            uni.setStorageSync("token", res.data.access_token);

            // 延时后跳转
            setTimeout(() => {
                uni.reLaunch({
                    url: "/pages/dashboard/dashboard",
                });
            }, 1500);
        } else {
            const errorMessage = res.data.detail || "学号或密码错误";
            uni.showToast({ title: errorMessage, icon: "none" });
        }
    } catch (error) {
        console.error("请求失败", error);
        uni.showToast({ title: "服务器连接失败，请前往QQ群查看是否有新通知", icon: "none" });
    } finally {
        isLoading.value = false;
    }
};

const onPullRefresh = () => {
    console.log("下拉刷新");
    checkLoginStatus();
    uni.stopPullDownRefresh();
};


// --- from useCredentialsCache.js ---
const loadCachedCredentials = () => {
    try {
        const cachedCredentials = uni.getStorageSync("cached_credentials");
        if (cachedCredentials) {
            const { studentId, password, remember } = JSON.parse(cachedCredentials);
            formData.value.studentId = studentId || "";
            formData.value.password = password || "";
            rememberPassword.value = remember || false;
            hasCachedCredentials.value = !!(studentId || password);

            console.log("已加载缓存的账号信息", {
                studentId: studentId ? "***" + studentId.slice(-4) : "",
                hasPassword: !!password,
                remember,
            });
        }
    } catch (error) {
        console.error("加载缓存账号密码失败:", error);
    }
};

const saveCachedCredentials = () => {
    try {
        if (rememberPassword.value) {
            const credentials = {
                studentId: formData.value.studentId,
                password: formData.value.password,
                remember: true,
                saveTime: new Date().getTime(),
            };
            uni.setStorageSync("cached_credentials", JSON.stringify(credentials));
            console.log("账号密码已保存到缓存");
        } else {
            // 如果不记住密码，清除缓存
            uni.removeStorageSync("cached_credentials");
            console.log("已清除账号密码缓存");
        }
    } catch (error) {
        console.error("保存账号密码到缓存失败:", error);
    }
};

const clearCachedCredentials = () => {
    uni.showModal({
        title: "确认清除",
        content: "确定要清除缓存的账号密码吗？",
        success: (res) => {
            if (res.confirm) {
                try {
                    uni.removeStorageSync("cached_credentials");
                    formData.value.studentId = "";
                    formData.value.password = "";
                    rememberPassword.value = false;
                    hasCachedCredentials.value = false;
                    uni.showToast({ title: "缓存已清除", icon: "success" });
                    console.log("用户手动清除了账号密码缓存");
                } catch (error) {
                    console.error("清除缓存失败:", error);
                    uni.showToast({ title: "清除缓存失败", icon: "none" });
                }
            }
        },
    });
};

const onRememberChange = (e) => {
    try {
        rememberPassword.value =
            Array.isArray(e.detail.value) && e.detail.value.includes("remember");
    } catch (err) {
        rememberPassword.value = false;
    }
};

// --- from useExternalLinks.js ---
const openExternalUrl = (url, fallbackMessage) => {
    // #ifdef H5
    if (typeof window !== "undefined" && window.open) {
        window.open(url, "_blank");
    } else {
        uni.setClipboardData({
            data: url,
            success() {
                uni.showToast({
                    title: fallbackMessage,
                    icon: "success",
                    duration: 3000,
                });
            },
        });
    }
    // #endif

    // #ifdef APP-PLUS
    plus.runtime.openURL(url);
    // #endif

    // #ifdef MP
    uni.setClipboardData({
        data: url,
        success() {
            uni.showToast({
                title: fallbackMessage,
                icon: "success",
                duration: 3000,
            });
        },
    });
    // #endif
};

const openAgreement = () => {
    // #ifdef H5
    // H5 环境直接跳转
    if (typeof window !== "undefined" && window.open) {
        window.open(AGREEMENT_URL, "_blank");
        return;
    }
    // #endif

    // 其他平台显示选择弹窗
    uni.showModal({
        title: "用户协议",
        content: `即将跳转到用户协议页面：\n${AGREEMENT_URL}\n\n是否继续？`,
        confirmText: "前往",
        cancelText: "复制链接",
        confirmColor: "#7F4515",
        success: (res) => {
            if (res.confirm) {
                // 用户选择前往
                openExternalUrl(AGREEMENT_URL, "链接已复制，请在浏览器中打开");
            } else if (res.cancel) {
                // 用户选择复制链接
                uni.setClipboardData({
                    data: AGREEMENT_URL,
                    success() {
                        uni.showToast({
                            title: "协议链接已复制到剪贴板",
                            icon: "success",
                            duration: 2000,
                        });
                    },
                });
            }
        },
    });
};

const openActivationPage = () => {
    // #ifdef H5
    // H5 环境直接跳转
    if (typeof window !== "undefined" && window.open) {
        window.open(ACTIVATION_URL, "_blank");
        return;
    }
    // #endif

    // 其他平台显示选择弹窗
    uni.showModal({
        title: "账号激活",
        content: `即将跳转到账号激活页面：\n${ACTIVATION_URL}\n\n是否继续？`,
        confirmText: "前往",
        cancelText: "复制链接",
        confirmColor: "#7F4515",
        success: (res) => {
            if (res.confirm) {
                // 用户选择前往
                openExternalUrl(ACTIVATION_URL, "链接已复制，请在浏览器中打开");
            } else if (res.cancel) {
                // 用户选择复制链接
                uni.setClipboardData({
                    data: ACTIVATION_URL,
                    success() {
                        uni.showToast({
                            title: "激活链接已复制到剪贴板",
                            icon: "success",
                            duration: 2000,
                        });
                    },
                });
            }
        },
    });
};


// 页面加载时初始化
onLoad(() => {
    checkLoginStatus();
    loadCachedCredentials();
});

// 登录点击处理（包装原始登录函数并传入缓存保存函数）
const handleLoginClick = () => {
    handleLogin();
};
</script>

<style lang="scss" scoped>
// 通用容器样式
.container {
    position: relative;
    width: 100%;
    height: 100vh;
    background: #f7f8fa;
    padding-top: 30rpx;
}

// 背景装饰圆圈
.background-decoration {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
}

.circle {
    position: absolute;
    border-radius: 50%;
    background: rgba(127, 69, 21, 0.06);

    &.circle-1 {
        width: 200rpx;
        height: 200rpx;
        top: 5%;
        right: -50rpx;
        animation: float 6s ease-in-out infinite;
    }

    &.circle-2 {
        width: 150rpx;
        height: 150rpx;
        bottom: 25%;
        left: -30rpx;
        animation: float 8s ease-in-out infinite reverse;
    }

    &.circle-3 {
        width: 100rpx;
        height: 100rpx;
        top: 25%;
        left: 20%;
        animation: float 4s ease-in-out infinite;
    }
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0px) rotate(0deg);
    }

    50% {
        transform: translateY(-20rpx) rotate(180deg);
    }
}

// 主内容区域
.content-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    min-height: calc(100vh - 80rpx);
    padding: 60rpx 60rpx 40rpx;
    box-sizing: border-box;
    position: relative;
    z-index: 1;
}

// 响应式适配
@media (max-height: 600px) {
    .content-wrapper {
        padding: 30rpx 60rpx 30rpx;
        min-height: calc(100vh + 200rpx - 80rpx);
    }
}

@media (min-width: 768px) {
    .content-wrapper {
        padding: 80rpx 120rpx 60rpx;
        max-width: 1200rpx;
        margin: 0 auto;
    }
}

@media (min-width: 1024px) {
    .content-wrapper {
        padding: 100rpx 200rpx 80rpx;
    }
}
</style>