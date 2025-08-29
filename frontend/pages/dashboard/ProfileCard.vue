<template>
  <ModernCard class="profile-card" highlight>
    <view class="profile-content" :class="{ 'loading': loading }">
      <view class="identity-section">
        <view class="avatar-wrapper">
          <image class="avatar" src="https://pic1.zhimg.com/80/v2-82c1c70c69720aadac79594ea50ed4a7.png"
            mode="aspectFit"></image>
          <view class="status-indicator" :class="{ 'loading-pulse': loading }"></view>
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
import { onMounted, ref } from "vue";
import ModernCard from "../../components/ModernCard/ModernCard.vue";
import { decode } from "../../utils/jwt-decode.js";

// ==================== Profile Management ====================
class ProfileCache {
  static CACHE_KEY = "user_profile_cache";
  static CACHE_EXPIRE_TIME = 30 * 60 * 1000; // 30分钟过期时间

  // 获取当前用户的唯一标识
  static getCurrentUserKey() {
    const token = uni.getStorageSync("token");
    if (!token) return null;

    try {
      const payload = decode(token);
      return payload.sub || payload.user_id || payload.id || token.substring(0, 32);
    } catch (error) {
      return token.substring(0, 32);
    }
  }

  // 保存个人信息到缓存
  static save(profileData) {
    try {
      const userKey = this.getCurrentUserKey();
      if (!userKey) {
        console.warn("无法获取用户标识，跳过缓存");
        return;
      }
      const cacheData = {
        profile: profileData,
        timestamp: Date.now(),
        version: "1.1",
        userKey: userKey,
        tokenHash: this.getTokenHash()
      };
      uni.setStorageSync(this.CACHE_KEY, JSON.stringify(cacheData));
    } catch (error) {
      console.error("缓存个人信息失败", error);
    }
  }

  static getTokenHash() {
    const token = uni.getStorageSync("token");
    if (!token) return null;
    let hash = 0;
    for (let i = 0; i < token.length; i++) {
      const char = token.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return hash.toString();
  }

  static get() {
    try {
      const cacheString = uni.getStorageSync(this.CACHE_KEY);
      if (!cacheString) return null;
      const cacheData = JSON.parse(cacheString);
      if (this.isExpired(cacheData.timestamp) || this.userKeyChanged(cacheData) || this.tokenChanged(cacheData)) {
        this.clear();
        return null;
      }
      return cacheData.profile;
    } catch (error) {
      this.clear();
      return null;
    }
  }

  static isExpired(timestamp) {
    return Date.now() - timestamp > this.CACHE_EXPIRE_TIME;
  }

  static userKeyChanged(cacheData) {
    return cacheData.userKey !== this.getCurrentUserKey();
  }

  static tokenChanged(cacheData) {
    return cacheData.tokenHash && cacheData.tokenHash !== this.getTokenHash();
  }

  static isValid() {
    const cacheString = uni.getStorageSync(this.CACHE_KEY);
    if (!cacheString) return false;
    try {
      const cacheData = JSON.parse(cacheString);
      return !this.isExpired(cacheData.timestamp) && !this.userKeyChanged(cacheData) && !this.tokenChanged(cacheData);
    } catch {
      return false;
    }
  }

  static clear() {
    uni.removeStorageSync(this.CACHE_KEY);
  }

  static clearAll() {
    uni.removeStorageSync(this.CACHE_KEY);
  }
}

// 用户资料数据
const profile = ref({
  student_name: "W1ndys",
  student_id: "加载中...",
  college: "曲奇学院",
  major: "曲奇专业",
  class_name: "22曲奇班",
});

// 加载状态
const loading = ref(false);

// 从缓存加载个人信息
const loadFromCache = () => {
  const cachedProfile = ProfileCache.get();
  if (cachedProfile) {
    profile.value = { ...cachedProfile };
    return true;
  }
  return false;
};

// 获取用户资料
const fetchProfile = async () => {
  const token = uni.getStorageSync("token");
  if (!token) {
    console.warn("未找到登录凭证");
    return;
  }

  loading.value = true;
  const baseURL = getApp().globalData.apiBaseURL;

  try {
    const res = await new Promise((resolve, reject) => {
      uni.request({
        url: `${baseURL}/api/v1/profile`,
        method: "GET",
        header: { Authorization: `Bearer ${token}` },
        success: resolve,
        fail: reject,
      });
    });

    if (res.statusCode === 200 && res.data.success) {
      const serverData = res.data.data;

      const studentId = serverData.student_id || (() => {
        try {
          const payload = decode(token);
          return payload.sub;
        } catch (e) {
          console.error("Token解析失败", e);
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

      // 使用 ProfileAPI.clearProfile 和 ProfileAPI.getCachedProfile 来管理缓存
      ProfileCache.save(profile.value);


      console.log("用户资料获取成功", profile.value);
    } else {
      const errorMsg = res.data.message || `获取信息失败 (${res.statusCode})`;
      console.error("获取用户资料失败", errorMsg);

      uni.showToast({
        title: errorMsg,
        icon: "none"
      });

      if (res.statusCode === 401) {
        uni.removeStorageSync("token");
        setTimeout(() => {
          uni.reLaunch({ url: "/pages/index/index" });
        }, 1500);
      }
    }
  } catch (err) {
    console.error("获取个人信息请求失败", err);
    uni.showToast({
      title: "网络请求失败，请稍后重试",
      icon: "none"
    });
  } finally {
    loading.value = false;
  }
};

// 刷新用户资料
const refreshProfile = async () => {
  uni.showLoading({ title: "正在刷新..." });
  try {
    await fetchProfile();
    uni.showToast({
      title: "资料已刷新",
      icon: "success"
    });
  } finally {
    uni.hideLoading();
  }
};

// 检查并初始化用户资料
const initProfile = () => {
  const token = uni.getStorageSync("token");
  if (!token) {
    ProfileCache.clearAll();
    return;
  }

  if (!ProfileCache.isValid()) {
    ProfileCache.clear();
  }

  const cacheLoaded = loadFromCache();

  if (!cacheLoaded) {
    console.log("缓存不可用，从服务器获取个人信息");
    fetchProfile();
  } else {
    if (profile.value.student_name === "W1ndys" ||
      profile.value.student_id === "加载中...") {
      console.log("缓存数据不完整，从服务器重新获取");
      fetchProfile();
    }
  }
};

// 组件挂载时初始化用户资料
onMounted(() => {
  initProfile();
});

// 暴露方法给父组件使用
defineExpose({
  refreshProfile,
  fetchProfile,
  profile,
  clearProfile: ProfileCache.clear,
  clearAllProfiles: ProfileCache.clearAll
});
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

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

// 加载状态样式
.profile-content.loading {
  opacity: 0.7;
}

.loading-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0% {
    background: #52c41a;
    transform: scale(1);
  }

  50% {
    background: #faad14;
    transform: scale(1.1);
  }

  100% {
    background: #52c41a;
    transform: scale(1);
  }
}
</style>
