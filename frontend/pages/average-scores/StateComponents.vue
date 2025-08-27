<template>
    <!-- 空状态 -->
    <view class="empty-state modern-card" v-if="type === 'empty'">
        <view class="empty-content">
            <view class="empty-icon">
                <uni-icons type="info" size="80" color="#adb5bd"></uni-icons>
            </view>
            <text class="empty-title">未找到相关数据</text>
            <text class="empty-subtitle">{{ message }}</text>
            <button class="action-btn primary-btn retry-btn" @click="$emit('retry')">
                <uni-icons type="refresh" size="20" color="#ffffff"></uni-icons>
                <text>重新搜索</text>
            </button>
        </view>
    </view>

    <!-- 初始状态 -->
    <view class="initial-state modern-card" v-else-if="type === 'initial'">
        <view class="initial-content">
            <view class="initial-icon">
                <uni-icons type="search" size="80" color="#7f4515"></uni-icons>
            </view>
            <text class="initial-title">欢迎使用平均分查询</text>
            <text class="initial-subtitle">请输入课程信息开始查询学术数据</text>
        </view>
    </view>

    <!-- 加载状态 -->
    <view class="loading-state modern-card" v-else-if="type === 'loading'">
        <view class="loading-content">
            <view class="loading-spinner">
                <uni-icons type="spinner-cycle" size="60" color="#7f4515"></uni-icons>
            </view>
            <text class="loading-text">正在查询数据...</text>
        </view>
    </view>
</template>

<script src="./StateComponents.js"></script>
<style lang="scss" scoped>
@import "./StateComponents.scss";
</style>
