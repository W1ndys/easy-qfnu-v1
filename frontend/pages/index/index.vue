<template>
  <view class="container">
    <!-- 背景装饰 -->
    <view class="background-decoration">
      <view class="circle circle-1"></view>
      <view class="circle circle-2"></view>
      <view class="circle circle-3"></view>
    </view>

    <!-- 主内容区域 -->
    <view class="content-wrapper">
      <!-- Logo区域 -->
      <view class="logo-section">
        <image class="logo" src="/static/logo.png" mode="aspectFit"></image>
        <view class="app-title">Easy-QFNU</view>
        <view class="app-subtitle">让你的QFNU更简单</view>
      </view>

      <!-- 登录表单 -->
      <view class="login-card page-rounded-container">
        <view class="form-header">
          <text class="form-title">欢迎回来</text>
          <text class="form-subtitle">请登录您的教务系统账号</text>
        </view>

        <uni-forms class="login-form" :modelValue="formData">
          <uni-forms-item class="form-item">
            <uni-easyinput
              prefixIcon="person"
              v-model="formData.studentId"
              placeholder="学号"
              class="custom-input" />
          </uni-forms-item>
          <uni-forms-item class="form-item">
            <uni-easyinput
              prefixIcon="locked"
              type="password"
              v-model="formData.password"
              placeholder="密码"
              class="custom-input" />
          </uni-forms-item>
        </uni-forms>

        <view class="agreement">
          <checkbox-group @change="onAgreeChange">
            <label class="agree-label">
              <checkbox value="agree" :checked="agreed" />
              <text class="agree-text">我已阅读并同意</text>
              <text class="agreement-link" @click="openAgreement"
                >《用户协议》</text
              >
            </label>
          </checkbox-group>
        </view>

        <button class="login-btn" @click="handleLogin" :loading="isLoading">
          <text v-if="!isLoading">登录</text>
          <text v-else>登录中...</text>
        </button>

        <view class="footer-text">
          <text>本程序为第三方应用，非学校官方出品</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { isTokenValid } from "../../utils/jwt-decode.js";

// 1. 使用 ref 创建"响应式"数据
// 这等同于原生小程序里的 this.data
// 当你修改 .value 时，template 里的界面会自动更新
const formData = ref({
  studentId: "",
  password: "",
});
const isLoading = ref(false);

// 同意协议
const agreed = ref(false);
const AGREEMENT_URL =
  "https://cq4hqujcxu3.feishu.cn/docx/XvdmdJ5eIo3hxMxPJA9cODcYnhb";
const onAgreeChange = (e) => {
  try {
    agreed.value =
      Array.isArray(e.detail.value) && e.detail.value.includes("agree");
  } catch (err) {
    agreed.value = false;
  }
};
const openAgreement = () => {
  if (typeof window !== "undefined" && window.open) {
    window.open(AGREEMENT_URL, "_blank");
  } else {
    uni.setClipboardData({
      data: AGREEMENT_URL,
      success() {
        uni.showToast({ title: "链接已复制，请在浏览器中打开", icon: "none" });
      },
    });
  }
};

// 页面加载时检查缓存的token
onLoad(() => {
  checkLoginStatus();
});

// 检查登录状态函数
const checkLoginStatus = () => {
  const token = uni.getStorageSync("token");

  if (token) {
    console.log("检测到缓存的token，开始验证有效性");

    try {
      if (isTokenValid(token)) {
        console.log("Token验证通过，准备跳转到dashboard");
        uni.reLaunch({
          url: "/pages/dashboard/index",
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
      // 如果验证过程有问题，为安全起见清除token
      uni.removeStorageSync("token");
      uni.showToast({
        title: "登录状态异常，请重新登录",
        icon: "none",
      });
    }
  }
};

// 2. 定义登录函数 (使用 async/await 语法，更现代)
const handleLogin = async () => {
  // 简单的输入校验
  if (!formData.value.studentId || !formData.value.password) {
    uni.showToast({ title: "学号和密码不能为空", icon: "none" });
    return;
  }

  if (!agreed.value) {
    uni.showToast({ title: "请先阅读并同意用户协议", icon: "none" });
    return;
  }

  isLoading.value = true; // 显示加载状态

  try {
    // 3. 使用 uni.request 发起网络请求
    const res = await uni.request({
      url: "http://127.0.0.1:8000/api/v1/login", // 确保后端在运行
      method: "POST",
      data: {
        student_id: formData.value.studentId,
        password: formData.value.password,
      },
    });

    // uni.request 返回的是一个数组 [error, response]
    if (res.statusCode === 200 && res.data.access_token) {
      console.log("登录成功, Token:", res.data.access_token);
      uni.showToast({ title: "登录成功", icon: "success" });
      uni.setStorageSync("token", res.data.access_token);

      // 延时后跳转
      setTimeout(() => {
        uni.reLaunch({
          url: "/pages/dashboard/index",
        });
      }, 1500);
    } else {
      // 处理后端返回的业务错误
      const errorMessage = res.data.detail || "学号或密码错误";
      uni.showToast({ title: errorMessage, icon: "none" });
    }
  } catch (error) {
    // 处理网络层面的错误
    console.error("请求失败", error);
    uni.showToast({ title: "服务器连接失败", icon: "none" });
  } finally {
    // 无论成功失败，都隐藏加载状态
    isLoading.value = false;
  }
};
</script>

<style lang="scss" scoped>
.container {
  position: relative;
  width: 100%;
  height: 100vh;
  background: #f7f8fa;
  overflow: hidden;
}

// 背景装饰圆圈
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(127, 69, 21, 0.06);

  &.circle-1 {
    width: 200rpx;
    height: 200rpx;
    top: 10%;
    right: -50rpx;
    animation: float 6s ease-in-out infinite;
  }

  &.circle-2 {
    width: 150rpx;
    height: 150rpx;
    bottom: 20%;
    left: -30rpx;
    animation: float 8s ease-in-out infinite reverse;
  }

  &.circle-3 {
    width: 100rpx;
    height: 100rpx;
    top: 30%;
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

.content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  height: 100vh;
  padding: 120rpx 60rpx 0;
  box-sizing: border-box;
  position: relative;
  z-index: 1;
}

// Logo区域样式
.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 80rpx;
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
}

// 登录卡片
.login-card {
  width: 100%;
  max-width: 680rpx;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 32rpx;
  padding: 60rpx 50rpx 40rpx;
  box-shadow: none;
  backdrop-filter: blur(20rpx);
  border: none;
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
  border-radius: 9999rpx;
  background: linear-gradient(135deg, #7f4515 0%, #8c5527 100%);
  color: #ffffff;
  font-size: 28rpx;
  font-weight: 600;
  margin-bottom: 40rpx;
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

.footer-text {
  text-align: center;
  font-size: 22rpx;
  color: #a0aec0;
  font-weight: 400;

  text {
    opacity: 0.8;
  }
}

// 统一外层圆角白卡容器
.page-rounded-container {
  background: #ffffff;
  border-radius: 40rpx;
  box-shadow: 0 20rpx 60rpx var(--shadow-light);
  border: 1rpx solid var(--border-light);
}

// 响应式适配
@media (max-height: 600px) {
  .content-wrapper {
    padding: 40rpx 60rpx 0;
  }

  .logo-section {
    margin-bottom: 40rpx;
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
</style>
