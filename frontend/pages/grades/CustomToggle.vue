<template>
    <view>
        <view class="custom-gpa-toggle-section">
            <view class="toggle-left">
                <text class="toggle-title">自定义GPA计算</text>
                <text class="toggle-desc">勾选课程以计算特定GPA</text>
            </view>
            <switch :checked="isCustomMode" @change="handleToggle" color="#7F4515" />
        </view>

        <view v-if="isCustomMode" class="custom-mode-tip">
            <view class="tip-icon">💡</view>
            <text class="tip-text">请勾选 **需要计入** GPA的课程</text>
        </view>
    </view>
</template>

<script>
import CustomToggleScript from './CustomToggle.js'
export default CustomToggleScript
</script>

<style lang="scss" scoped>
@import './CustomToggle.scss';
</style>
