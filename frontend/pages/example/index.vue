<template>
    <PageLayout>
        <!-- 加载 -->
        <LoadingScreen v-if="isLoading" text="正在加载数据..." />

        <!-- 内容 -->
        <view v-else class="page-container page-rounded-container">
            <!-- 背景装饰（系统统一） -->
            <view class="background-decoration">
                <view class="circle circle-1"></view>
                <view class="circle circle-2"></view>
                <view class="circle circle-3"></view>
            </view>

            <!-- 页面头部（可选） -->
            <view class="page-header">
                <view class="header-content">
                    <text class="page-title">新功能页面标题</text>
                    <text class="page-subtitle">New Feature Subtitle</text>
                </view>
            </view>

            <view class="content-wrapper">
                <!-- 空状态 -->
                <EmptyState v-if="!hasData" icon-type="info-filled" title="暂无数据" description="请检查网络或稍后重试"
                    :show-retry="true" @retry="fetchData" />

                <!-- 业务内容 -->
                <view v-else>
                    <ModernCard title="示例卡片">
                        <view class="card-section">
                            <text class="section-title">数据概览</text>
                            <text class="section-desc">这里放置你的数据摘要或图表</text>
                        </view>
                    </ModernCard>

                    <ModernCard title="操作">
                        <view class="button-group">
                            <button class="action-btn primary-btn" @click="handlePrimary">
                                <uni-icons type="paperplane" size="20" color="#fff" />
                                <text>主操作</text>
                            </button>
                            <button class="action-btn secondary-btn" @click="handleSecondary">
                                <uni-icons type="refresh" size="20" color="#495057" />
                                <text>次要操作</text>
                            </button>
                        </view>
                    </ModernCard>
                </view>
            </view>
        </view>
    </PageLayout>
</template>

<script setup>
import { ref, computed } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import ModernCard from "../../components/ModernCard/ModernCard.vue";
import LoadingScreen from "../../components/LoadingScreen/LoadingScreen.vue";
import EmptyState from "../../components/EmptyState/EmptyState.vue";

const isLoading = ref(true);
const data = ref(null);

const hasData = computed(() => !!data.value);

onLoad(() => {
    if (!ensureLogin()) return;
    uni.setNavigationBarTitle({ title: "新功能页面标题" });
    fetchData();
});

onShow(() => {
    if (!ensureLogin()) return;
});

function ensureLogin() {
    const token = uni.getStorageSync("token");
    if (!token) {
        uni.showToast({ title: "请先登录", icon: "none" });
        uni.reLaunch({ url: "/pages/index/index" });
        return false;
    }
    return true;
}

async function fetchData() {
    isLoading.value = true;
    const token = uni.getStorageSync("token");
    const baseURL = getApp().globalData.apiBaseURL;

    try {
        const { statusCode, data: res } = await uni.request({
            url: `${baseURL}/api/v1/your-endpoint`,
            method: "GET",
            header: { Authorization: "Bearer " + token },
        });

        if (statusCode === 200 && (res.success || res.code === 200)) {
            data.value = res.data || res.result || {};
        } else if (statusCode === 401) {
            uni.removeStorageSync("token");
            uni.showToast({ title: "登录已过期，请重新登录", icon: "none" });
            setTimeout(() => uni.reLaunch({ url: "/pages/index/index" }), 1500);
        } else {
            uni.showToast({ title: res.detail || res.message || "获取数据失败", icon: "none" });
            data.value = null;
        }
    } catch (e) {
        console.error("请求失败", e);
        uni.showToast({ title: "网络连接失败", icon: "none" });
        data.value = null;
    } finally {
        isLoading.value = false;
    }
}

function handlePrimary() {
    uni.showToast({ title: "已执行主操作", icon: "success" });
}

function handleSecondary() {
    fetchData();
}
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

/* 最外层容器统一 */
.page-container {
    min-height: 100vh;
    background: #f7f8fa;
    position: relative;
    overflow: hidden;
}

.page-rounded-container {
    background: #ffffff;
    border-radius: 40rpx;
    padding: 20rpx 20rpx 30rpx;
    box-shadow: 0 20rpx 60rpx var(--shadow-light);
    border: 1rpx solid var(--border-light);
}

/* 背景装饰统一 */
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
        transform: translateY(0) rotate(0)
    }

    50% {
        transform: translateY(-20rpx) rotate(180deg)
    }
}

/* 页面头部（可选） */
.page-header {
    padding: 40rpx 30rpx 30rpx;
    position: relative;
    z-index: 1;
}

.header-content {
    text-align: center;
}

.page-title {
    display: block;
    font-size: 44rpx;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 12rpx;
    letter-spacing: 1rpx;
}

.page-subtitle {
    display: block;
    font-size: 24rpx;
    color: #7f8c8d;
    font-style: italic;
}

/* 主体内容容器 */
.content-wrapper {
    padding: 0 30rpx 30rpx;
    position: relative;
    z-index: 1;
}

/* 卡片内常用区块 */
.card-section {
    display: flex;
    flex-direction: column;
    gap: 8rpx;
}

.section-title {
    font-size: 28rpx;
    font-weight: 700;
    color: var(--text-primary);
}

.section-desc {
    font-size: 24rpx;
    color: var(--text-secondary);
}

/* 统一按钮样式（与现有页面一致） */
.button-group {
    display: flex;
    gap: 24rpx;
}

.action-btn {
    flex: 1;
    height: 72rpx;
    border-radius: 9999rpx;
    font-size: 26rpx;
    padding: 16rpx 24rpx;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12rpx;
    border: none;
    transition: all .3s;

    &::after {
        border: none;
    }

    &:active {
        transform: scale(0.95);
    }

    text {
        font-weight: inherit;
    }
}

.primary-btn {
    background: linear-gradient(135deg, #7f4515, #8c5527);
    color: #fff;
    box-shadow: 0 8rpx 24rpx rgba(127, 69, 21, .25);

    &:disabled {
        background: #adb5bd;
        color: #6c757d;
        box-shadow: none;
    }
}

.secondary-btn {
    background: #f8f9fa;
    color: var(--text-primary);
    border: 2rpx solid #e9ecef;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, .05);

    &:active {
        background: #e9ecef;
        border-color: #dee2e6;
    }
}
</style>