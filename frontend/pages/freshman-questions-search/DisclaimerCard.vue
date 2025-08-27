<template>
    <view class="disclaimer-card modern-card">
        <view class="disclaimer-header">
            <view class="disclaimer-icon">
                <uni-icons type="info-filled" size="24" color="#ff6b35"></uni-icons>
            </view>
            <text class="disclaimer-title">重要声明</text>
        </view>
        <view class="disclaimer-content">
            <text class="disclaimer-text">
                本题库由新生手册根据大模型生成，仅供参考。使用前请确保您已充分阅读并学习曲阜师范大学新生手册内容并遵守相关规定。使用本程序造成的一切后果与本程序无关，使用本程序即代表您同意上方声明内容。
            </text>
        </view>
    </view>
</template>

<script>
export default {
    name: 'DisclaimerCard'
}
</script>

<style lang="scss" scoped>
@import "./DisclaimerCard.scss";
</style>
