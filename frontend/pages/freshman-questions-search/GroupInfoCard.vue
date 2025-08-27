<template>
    <view class="group-info-card modern-card">
        <view class="group-header">
            <view class="group-icon">
                <uni-icons type="chat-filled" size="24" color="#1890ff"></uni-icons>
            </view>
            <text class="group-title">学习交流群</text>
        </view>
        <view class="group-content">
            <text class="group-description">曲师大25级选课学习交流群</text>
            <view class="group-number" @click="copyGroupNumber">
                <text class="group-label">群号：</text>
                <text class="group-id">1046961227</text>
                <view class="copy-icon">
                    <uni-icons type="copy" size="16" color="#1890ff"></uni-icons>
                </view>
            </view>
            <text class="group-hint">点击群号可复制</text>
        </view>
    </view>
</template>

<script>
export default {
    name: 'GroupInfoCard',
    methods: {
        copyGroupNumber() {
            uni.setClipboardData({
                data: '1046961227',
                success: () => {
                    uni.showToast({
                        title: '群号已复制',
                        icon: 'success',
                        duration: 2000
                    });
                },
                fail: () => {
                    uni.showToast({
                        title: '复制失败',
                        icon: 'none',
                        duration: 2000
                    });
                }
            });
        }
    }
}
</script>

<style lang="scss" scoped>
@import "./GroupInfoCard.scss";
</style>
