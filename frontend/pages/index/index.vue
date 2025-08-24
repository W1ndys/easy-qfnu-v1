<template>
  <scroll-view class="container" scroll-y="true" @scrolltoupper="onPullRefresh">
    <!-- 顶部公告弹幕 -->
    <view class="announcement-marquee" @click="handleMarqueeClick">
      <view class="marquee-content">
        <text class="marquee-text">
          📢 该程序正在测试阶段，功能可能不稳定 | 加入QQ群获取最新消息：1053432087 |
          开发策划交流群：1057327742 | 欢迎提出建议和意见
        </text>
      </view>
    </view>

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
        <image
          class="logo"
          src="https://pic1.zhimg.com/80/v2-82c1c70c69720aadac79594ea50ed4a7.png"
          mode="aspectFit"
        ></image>
        <view class="app-title">曲奇教务</view>
        <view class="app-subtitle">让你的QFNU更简单</view>

        <!-- 新生搜索小入口 -->
        <view class="freshman-entry" @click="goToFreshmanSearch">
          <uni-icons type="help" size="14" color="#7f4515"></uni-icons>
          <text class="entry-text">新生入学考试辅助</text>
          <uni-icons type="arrowright" size="12" color="#7f4515"></uni-icons>
        </view>
      </view>

      <!-- 登录卡片 -->
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
              class="custom-input"
            />
          </uni-forms-item>
          <uni-forms-item class="form-item">
            <uni-easyinput
              prefixIcon="locked"
              type="password"
              v-model="formData.password"
              placeholder="密码"
              class="custom-input"
            />
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
          <text
            class="clear-cache"
            @click="clearCachedCredentials"
            v-if="hasCachedCredentials"
            >清除缓存</text
          >
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
    </view>
  </scroll-view>
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
const rememberPassword = ref(false);
const hasCachedCredentials = ref(false);
const agreed = ref(false);

// 新增：跳转到新生搜索页面
const goToFreshmanSearch = () => {
  uni.navigateTo({
    url: "/pages/freshman-questions-search/index",
  });
};

// 记住密码相关
const onAgreeChange = (e) => {
  try {
    agreed.value = Array.isArray(e.detail.value) && e.detail.value.includes("agree");
  } catch (err) {
    agreed.value = false;
  }
};

// 记住密码选项变化
const onRememberChange = (e) => {
  try {
    rememberPassword.value =
      Array.isArray(e.detail.value) && e.detail.value.includes("remember");
  } catch (err) {
    rememberPassword.value = false;
  }
};

// 新增：下拉刷新处理
const onPullRefresh = () => {
  console.log("下拉刷新");
  // 这里可以添加刷新逻辑，比如重新检查登录状态
  checkLoginStatus();
  // 停止下拉刷新
  uni.stopPullDownRefresh();
};

// 页面加载时检查缓存的token
onLoad(() => {
  checkLoginStatus();
  loadCachedCredentials();
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

// 加载缓存的账号密码
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

// 保存账号密码到缓存
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

// 清除缓存的账号密码
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
      url: `${getApp().globalData.apiBaseURL}/api/v1/login`, // 统一读取全局域名
      method: "POST",
      data: {
        student_id: formData.value.studentId,
        password: formData.value.password,
      },
    });

    // uni.request 返回的是一个数组 [error, response]
    if (res.statusCode === 200 && res.data.access_token) {
      console.log("登录成功, Token:", res.data.access_token);

      // 保存账号密码到缓存（在登录成功后）
      saveCachedCredentials();

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
        // 用户选择前往
        // #ifdef H5
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
        // #endif

        // #ifdef APP-PLUS
        plus.runtime.openURL(AGREEMENT_URL);
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

// 复制QQ群号
const copyQQGroup = () => {
  uni.setClipboardData({
    data: "1053432087",
    success() {
      uni.showToast({ title: "QQ群号已复制到剪贴板，请自行搜索加群", icon: "success" });
    },
  });
};

// 复制开发QQ群号
const copyDevQQGroup = () => {
  uni.setClipboardData({
    data: "1057327742",
    success() {
      uni.showToast({
        title: "开发交流群号已复制到剪贴板，请自行搜索加群",
        icon: "success",
      });
    },
  });
};

const ACTIVATION_URL =
  "http://ids.qfnu.edu.cn/retrieve-password/activationMobile/index.html";

// 打开账号激活页面
const openActivationPage = () => {
  uni.showModal({
    title: "账号激活",
    content: `即将跳转到账号激活页面：\n${ACTIVATION_URL}\n\n是否继续？`,
    confirmText: "前往",
    cancelText: "复制链接",
    confirmColor: "#7F4515",
    success: (res) => {
      if (res.confirm) {
        // 用户选择前往
        // #ifdef H5
        if (typeof window !== "undefined" && window.open) {
          window.open(ACTIVATION_URL, "_blank");
        } else {
          uni.setClipboardData({
            data: ACTIVATION_URL,
            success() {
              uni.showToast({
                title: "链接已复制，请在浏览器中打开",
                icon: "success",
                duration: 3000,
              });
            },
          });
        }
        // #endif

        // #ifdef APP-PLUS
        plus.runtime.openURL(ACTIVATION_URL);
        // #endif

        // #ifdef MP
        uni.setClipboardData({
          data: ACTIVATION_URL,
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

// 新增：点击弹幕处理QQ群复制
const handleMarqueeClick = () => {
  uni.showActionSheet({
    itemList: ["复制用户群号 1053432087", "复制开发群号 1057327742"],
    success: (res) => {
      if (res.tapIndex === 0) {
        copyQQGroup();
      } else if (res.tapIndex === 1) {
        copyDevQQGroup();
      }
    },
  });
};
</script>

<style lang="scss" scoped>
// 顶部公告弹幕样式
.announcement-marquee {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 80rpx; // 增加高度确保文本有足够空间
  background: rgba(247, 248, 250, 0.95);
  backdrop-filter: blur(10rpx);
  border-bottom: 1rpx solid rgba(127, 69, 21, 0.1);
  z-index: 999;
  overflow: hidden;
  display: flex;
  align-items: center;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.marquee-content {
  white-space: nowrap; // 确保不换行
  animation: marquee 20s linear infinite; // 稍微放慢速度
  cursor: pointer;
  line-height: 80rpx; // 与容器高度保持一致
  height: 80rpx; // 明确设置高度
  display: flex;
  align-items: center;

  &:hover {
    animation-play-state: paused;
  }
}

.marquee-text {
  font-size: 24rpx; // 稍微增大字体
  color: #7f4515;
  font-weight: 500;
  letter-spacing: 0.5rpx;
  padding: 0 40rpx; // 增加左右间距
  white-space: nowrap; // 确保文本不换行
  display: inline-block; // 确保内联块级显示
}

@keyframes marquee {
  0% {
    transform: translateX(100vw);
  }
  100% {
    transform: translateX(-100%);
  }
}

.container {
  position: relative;
  width: 100%;
  height: 100vh;
  background: #f7f8fa;
  padding-top: 30rpx; /* 调整为新的弹幕高度 */
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

.content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-height: calc(100vh - 80rpx); /* 调整为新的弹幕高度 */
  padding: 60rpx 60rpx 40rpx;
  box-sizing: border-box;
  position: relative;
  z-index: 1;
}

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

// 新增：新生搜索小入口样式
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
  .content-wrapper {
    padding: 30rpx 60rpx 30rpx;
    min-height: calc(100vh + 200rpx - 80rpx); // 使用新的弹幕高度
  }

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

  .announcement-marquee {
    height: 60rpx; // 小屏幕稍微减小高度
  }

  .marquee-content {
    line-height: 60rpx;
    height: 60rpx;
  }

  .marquee-text {
    font-size: 20rpx; // 小屏幕减小字体
    padding: 0 30rpx; // 减小间距
  }
}

// 新增：支持更大屏幕的适配
@media (min-width: 768px) {
  .content-wrapper {
    padding: 80rpx 120rpx 60rpx;
    max-width: 1200rpx;
    margin: 0 auto;
  }

  .login-card {
    max-width: 600rpx;
  }
}

@media (min-width: 1024px) {
  .content-wrapper {
    padding: 100rpx 200rpx 80rpx;
  }
}
</style>
