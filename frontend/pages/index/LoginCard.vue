<template>
    <>
        <view class="logo-section">
            <image class="logo" src="https://pic1.zhimg.com/80/v2-82c1c70c69720aadac79594ea50ed4a7.png"
                mode="aspectFit"></image>
            <view class="app-title">曲奇教务</view>
            <view class="app-subtitle">让你的QFNU更简单</view>

            <view class="freshman-entry" @click="goToFreshmanSearch">
                <uni-icons type="help" size="14" color="#7f4515"></uni-icons>
                <text class="entry-text">新生入学考试辅助</text>
                <uni-icons type="arrowright" size="12" color="#7f4515"></uni-icons>
            </view>
        </view>

        <view class="login-card page-rounded-container">
            <view class="form-header">
                <text class="form-title">欢迎回来</text>
                <text class="form-subtitle">请登录您的教务系统账号</text>
            </view>

            <uni-forms class="login-form" :modelValue="formData">
                <uni-forms-item class="form-item">
                    <uni-easyinput prefixIcon="person" v-model="formData.studentId" placeholder="学号"
                        class="custom-input" :maxlength="11" />
                </uni-forms-item>
                <uni-forms-item class="form-item">
                    <uni-easyinput prefixIcon="locked" type="password" v-model="formData.password" placeholder="密码"
                        class="custom-input" />
                </uni-forms-item>
            </uni-forms>

            <view class="remember-section">
                <checkbox-group @change="onRememberChange">
                    <label class="remember-label">
                        <checkbox value="remember" :checked="rememberPassword" />
                        <text class="remember-text">记住账号密码</text>
                    </label>
                </checkbox-group>
                <text class="clear-cache" @click="clearCachedCredentials" v-if="hasCachedCredentials">清除缓存</text>
            </view>

            <view class="agreement">
                <checkbox-group @change="onAgreeChange">
                    <label class="agree-label">
                        <checkbox value="agree" :checked="agreed" />
                        <text class="agree-text">我已阅读并同意</text>
                        <text class="agreement-link" @click="openAgreement">《用户协议》</text>
                    </label>
                </checkbox-group>
            </view>

            <button class="login-btn" @click="handleLogin" :loading="isLoading">
                <text v-if="!isLoading">登录</text>
                <text v-else>登录中...</text>
            </button>

            <view class="activation-tip">
                <text class="activation-text">新生需要先</text>
                <text class="activation-link" @click="openActivationPage">激活账号</text>
            </view>

            <view class="footer-text">
                <text>© 2025-现在 Easy-QFNU 版权所有</text>
                <text>本应用为第三方教务工具，与学校官方无关</text>
            </view>
        </view>
    </>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";

const formData = ref({
    studentId: "",
    password: "",
});
const isLoading = ref(false);
const rememberPassword = ref(false);
const hasCachedCredentials = ref(false);
const agreed = ref(false);

const goToFreshmanSearch = () => {
    uni.navigateTo({
        url: "/pages/freshman-questions-search/freshman-questions-search",
    });
};

const onAgreeChange = (e) => {
    try {
        agreed.value = Array.isArray(e.detail.value) && e.detail.value.includes("agree");
    } catch (err) {
        agreed.value = false;
    }
};

const onRememberChange = (e) => {
    try {
        rememberPassword.value = Array.isArray(e.detail.value) && e.detail.value.includes("remember");
    } catch (err) {
        rememberPassword.value = false;
    }
};

const loadCachedCredentials = () => {
    try {
        const cachedCredentials = uni.getStorageSync("cached_credentials");
        if (cachedCredentials) {
            const { studentId, password, remember } = JSON.parse(cachedCredentials);
            formData.value.studentId = studentId || "";
            formData.value.password = password || "";
            rememberPassword.value = remember || false;
            hasCachedCredentials.value = !!(studentId || password);
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
        } else {
            uni.removeStorageSync("cached_credentials");
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
                } catch (error) {
                    console.error("清除缓存失败:", error);
                    uni.showToast({ title: "清除缓存失败", icon: "none" });
                }
            }
        },
    });
};

const STUDENT_ID_REGEX = /^\d{8,11}$/;

watch(
    () => formData.value.studentId,
    (val) => {
        const digits = (val || "").replace(/\D/g, "").slice(0, 11);
        if (digits !== val) formData.value.studentId = digits;
    }
);

const AGREEMENT_URL = "https://cq4hqujcxu3.feishu.cn/docx/EYE6d5ufAoQt5Axx7MFc4XMrnAf";
const openAgreement = () => {
    uni.showModal({
        title: "用户协议",
        content: `即将跳转到用户协议页面：\n${AGREEMENT_URL}\n\n是否继续？`,
        confirmText: "前往",
        cancelText: "复制链接",
        confirmColor: "#7F4515",
        success: (res) => {
            if (res.confirm) {
                if (typeof window !== "undefined" && window.open) {
                    window.open(AGREEMENT_URL, "_blank");
                } else {
                    uni.setClipboardData({
                        data: AGREEMENT_URL,
                        success() {
                            uni.showToast({
                                title: "链接已复制，请在浏览器中打开",
                                icon: "success",
                                duration: 3000,
                            });
                        },
                    });
                }
                // #ifdef APP-PLUS
                // eslint-disable-next-line no-undef
                if (typeof plus !== "undefined" && plus.runtime && plus.runtime.openURL) {
                    // eslint-disable-next-line no-undef
                    plus.runtime.openURL(AGREEMENT_URL);
                }
                // #endif
                // #ifdef MP
                uni.setClipboardData({
                    data: AGREEMENT_URL,
                    success() {
                        uni.showToast({
                            title: "链接已复制，请在浏览器中打开",
                            icon: "success",
                            duration: 3000,
                        });
                    },
                });
                // #endif
            } else if (res.cancel) {
                uni.setClipboardData({
                    data: AGREEMENT_URL,
                    success() {
                        uni.showToast({ title: "协议链接已复制到剪贴板", icon: "success", duration: 2000 });
                    },
                });
            }
        },
    });
};

const ACTIVATION_URL = "http://ids.qfnu.edu.cn/retrieve-password/activationMobile/index.html";
const openActivationPage = () => {
    uni.showModal({
        title: "账号激活",
        content: `即将跳转到账号激活页面：\n${ACTIVATION_URL}\n\n是否继续？`,
        confirmText: "前往",
        cancelText: "复制链接",
        confirmColor: "#7F4515",
        success: (res) => {
            if (res.confirm) {
                if (typeof window !== "undefined" && window.open) {
                    window.open(ACTIVATION_URL, "_blank");
                } else {
                    uni.setClipboardData({
                        data: ACTIVATION_URL,
                        success() {
                            uni.showToast({ title: "链接已复制，请在浏览器中打开", icon: "success", duration: 3000 });
                        },
                    });
                }
                // #ifdef APP-PLUS
                // eslint-disable-next-line no-undef
                if (typeof plus !== "undefined" && plus.runtime && plus.runtime.openURL) {
                    // eslint-disable-next-line no-undef
                    plus.runtime.openURL(ACTIVATION_URL);
                }
                // #endif
                // #ifdef MP
                uni.setClipboardData({
                    data: ACTIVATION_URL,
                    success() {
                        uni.showToast({ title: "链接已复制，请在浏览器中打开", icon: "success", duration: 3000 });
                    },
                });
                // #endif
            } else if (res.cancel) {
                uni.setClipboardData({
                    data: ACTIVATION_URL,
                    success() {
                        uni.showToast({ title: "激活链接已复制到剪贴板", icon: "success", duration: 2000 });
                    },
                });
            }
        },
    });
};

const handleLogin = async () => {
    if (!formData.value.studentId || !formData.value.password) {
        uni.showToast({ title: "学号和密码不能为空", icon: "none" });
        return;
    }

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
            data: { student_id: sid, password: formData.value.password },
        });

        if (res.statusCode === 200 && res.data.access_token) {
            saveCachedCredentials();
            uni.showToast({ title: "登录成功", icon: "success" });
            uni.setStorageSync("token", res.data.access_token);
            setTimeout(() => {
                uni.reLaunch({ url: "/pages/dashboard/dashboard" });
            }, 1500);
        } else {
            const errorMessage = res.data.detail || "学号或密码错误";
            uni.showToast({ title: errorMessage, icon: "none" });
        }
    } catch (error) {
        console.error("请求失败", error);
        uni.showToast({ title: "服务器连接失败", icon: "none" });
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
    loadCachedCredentials();
});
</script>

<style lang="scss" scoped>
.logo-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 50rpx;
}

.logo {
    width: 120rpx;
    height: 120rpx;
    margin-bottom: 30rpx;
    border-radius: 24rpx;
    box-shadow: 0 8rpx 24rpx rgba(127, 69, 21, 0.15);
}

.app-title {
    font-size: 48rpx;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 16rpx;
    letter-spacing: 2rpx;
}

.app-subtitle {
    font-size: 28rpx;
    color: #7f8c8d;
    font-weight: 400;
    margin-bottom: 20rpx;
}

.freshman-entry {
    display: flex;
    align-items: center;
    gap: 8rpx;
    padding: 12rpx 20rpx;
    background: rgba(127, 69, 21, 0.08);
    border-radius: 20rpx;
    border: 1rpx solid rgba(127, 69, 21, 0.15);
    transition: all 0.3s ease;
    cursor: pointer;

    &:active {
        background: rgba(127, 69, 21, 0.15);
        transform: scale(0.95);
    }
}

.entry-text {
    font-size: 22rpx;
    color: #7f4515;
    font-weight: 500;
}

.login-card {
    width: 100%;
    max-width: 680rpx;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 32rpx;
    padding: 60rpx 50rpx 40rpx;
    box-shadow: none;
    backdrop-filter: blur(20rpx);
    border: none;
    margin-bottom: 40rpx;
}

.form-header {
    text-align: center;
    margin-bottom: 60rpx;
}

.form-title {
    display: block;
    font-size: 36rpx;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 16rpx;
}

.form-subtitle {
    display: block;
    font-size: 26rpx;
    color: #7f8c8d;
    font-weight: 400;
}

.login-form {
    width: 100%;
    margin-bottom: 50rpx;
}

.remember-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30rpx;
    font-size: 24rpx;
}

.remember-label {
    display: flex;
    align-items: center;
}

.remember-text {
    margin-left: 12rpx;
    color: #4a5568;
    font-size: 24rpx;
}

.clear-cache {
    color: #7f4515;
    font-size: 22rpx;
    text-decoration: underline;
    cursor: pointer;
    padding: 8rpx 12rpx;
    border-radius: 8rpx;
    background: rgba(127, 69, 21, 0.08);
    transition: all 0.3s ease;
}

.clear-cache:active {
    background: rgba(127, 69, 21, 0.15);
    transform: scale(0.95);
}

.agreement {
    display: flex;
    align-items: center;
    margin-bottom: 30rpx;
    font-size: 24rpx;
    color: #4a5568;
}

.agree-label {
    display: flex;
    align-items: center;
}

.agree-text {
    margin-left: 12rpx;
    color: #4a5568;
}

.agreement-link {
    margin-left: 6rpx;
    color: #7f4515;
    text-decoration: underline;
}

.form-item {
    margin-bottom: 30rpx;

    &:last-child {
        margin-bottom: 0;
    }
}

::v-deep(.uni-easyinput__content) {
    height: 96rpx !important;
    border-radius: 16rpx !important;
    background-color: #f8fafc !important;
    border: 2rpx solid #e2e8f0 !important;
    transition: all 0.3s ease !important;

    &:focus-within {
        border-color: #7f4515 !important;
        background-color: #ffffff !important;
        box-shadow: 0 0 0 6rpx rgba(127, 69, 21, 0.1) !important;
    }
}

::v-deep(.uni-easyinput__content-input) {
    font-size: 30rpx !important;
    color: #2d3748 !important;

    &::placeholder {
        color: #a0aec0 !important;
    }
}

::v-deep(.uni-easyinput__content-icon) {
    color: #7f4515 !important;
}

.login-btn {
    width: 100%;
    height: 72rpx;
    line-height: 72rpx;
    border-radius: 24rpx;
    background: linear-gradient(135deg, #7f4515 0%, #8c5527 100%);
    color: #ffffff;
    font-size: 28rpx;
    font-weight: 600;
    margin-bottom: 20rpx;
    transition: all 0.3s ease;
    box-shadow: 0 8rpx 24rpx rgba(127, 69, 21, 0.25);

    &:active {
        transform: translateY(2rpx);
        box-shadow: 0 4rpx 12rpx rgba(127, 69, 21, 0.35);
    }

    &::after {
        border: none;
    }

    &[loading] {
        background: linear-gradient(135deg, #7f4515 0%, #8c5527 100%);
        opacity: 0.8;
    }
}

.activation-tip {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 30rpx;
    font-size: 24rpx;
}

.activation-text {
    color: #7f8c8d;
    margin-right: 6rpx;
}

.activation-link {
    color: #7f4515;
    text-decoration: underline;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s ease;
}

.activation-link:active {
    color: #8c5527;
    transform: scale(0.95);
}

.footer-text {
    text-align: center;
    margin-top: 20rpx;
    padding-top: 20rpx;
    border-top: 1rpx solid #e2e8f0;

    text {
        font-size: 22rpx;
        color: #9ca3af;
        line-height: 1.4;
        font-weight: 400;
        display: block;
        margin-bottom: 8rpx;

        &:last-child {
            margin-bottom: 0;
        }
    }
}

@media (max-height: 600px) {
    .logo-section {
        margin-bottom: 30rpx;
    }

    .logo {
        width: 100rpx;
        height: 100rpx;
    }

    .app-title {
        font-size: 40rpx;
    }

    .login-card {
        padding: 40rpx 40rpx 30rpx;
    }
}

@media (min-width: 768px) {
    .login-card {
        max-width: 600rpx;
    }
}
</style>
