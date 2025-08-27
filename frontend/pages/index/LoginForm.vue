<template>
    <view class="login-card page-rounded-container">
        <view class="form-header">
            <text class="form-title">欢迎回来</text>
            <text class="form-subtitle">请登录您的教务系统账号</text>
        </view>

        <uni-forms class="login-form" :modelValue="formData">
            <uni-forms-item class="form-item">
                <uni-easyinput prefixIcon="person" v-model="formData.studentId" placeholder="学号" class="custom-input"
                    :maxlength="11" />
            </uni-forms-item>
            <uni-forms-item class="form-item">
                <uni-easyinput prefixIcon="locked" type="password" v-model="formData.password" placeholder="密码"
                    class="custom-input" />
            </uni-forms-item>
        </uni-forms>

        <!-- 记住密码选项 -->
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

        <!-- 账号激活提示 -->
        <view class="activation-tip">
            <text class="activation-text">新生需要先</text>
            <text class="activation-link" @click="openActivationPage">激活账号</text>
        </view>

        <view class="footer-text">
            <text>© 2025-现在 Easy-QFNU 版权所有</text>
            <text>本应用为第三方教务工具，与学校官方无关</text>
        </view>
    </view>
</template>

<script setup>
import { defineEmits } from 'vue';

// 定义 props 和 emits
const props = defineProps({
    formData: {
        type: Object,
        required: true
    },
    isLoading: {
        type: Boolean,
        required: true
    },
    rememberPassword: {
        type: Boolean,
        required: true
    },
    hasCachedCredentials: {
        type: Boolean,
        required: true
    },
    agreed: {
        type: Boolean,
        required: true
    }
});

const emit = defineEmits([
    'remember-change',
    'agree-change',
    'clear-cache',
    'login',
    'open-agreement',
    'open-activation'
]);

// 记住密码选项变化
const onRememberChange = (e) => {
    emit('remember-change', e);
};

// 同意协议变化
const onAgreeChange = (e) => {
    emit('agree-change', e);
};

// 清除缓存
const clearCachedCredentials = () => {
    emit('clear-cache');
};

// 登录处理
const handleLogin = () => {
    emit('login');
};

// 打开用户协议
const openAgreement = () => {
    emit('open-agreement');
};

// 打开账号激活页面
const openActivationPage = () => {
    emit('open-activation');
};
</script>

<style lang="scss" scoped>
// 登录卡片样式
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

// uni-ui组件的深度样式修改
:deep(.uni-easyinput__content) {
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

:deep(.uni-easyinput__content-input) {
    font-size: 30rpx !important;
    color: #2d3748 !important;

    &::placeholder {
        color: #a0aec0 !important;
    }
}

:deep(.uni-easyinput__content-icon) {
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

// 响应式适配
@media (max-height: 600px) {
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
