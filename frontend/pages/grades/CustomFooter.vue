<template>
    <view v-if="isCustomMode" class="custom-gpa-footer">
        <view v-if="customGPAResult" class="result-display-card">
            <view class="result-header">
                <text class="result-title">自定义计算结果</text>
                <text class="close-result-btn" @click="$emit('clearResult')">关闭</text>
            </view>
            <view class="result-content">
                <view class="result-gpa">
                    <text class="gpa-value">{{ customGPAResult.weighted_gpa?.toFixed(2) || '0.00' }}</text>
                    <text class="gpa-label">加权平均GPA</text>
                </view>
                <view class="result-stats">
                    <view class="stat-item">
                        <text class="stat-value">{{ customGPAResult.total_credit || 0 }}</text>
                        <text class="stat-label">总学分</text>
                    </view>
                    <view class="stat-item">
                        <text class="stat-value">{{ customGPAResult.course_count || 0 }}</text>
                        <text class="stat-label">课程数</text>
                    </view>
                </view>
            </view>
        </view>

        <view class="footer-actions">
            <view class="selection-info">
                <text class="info-text">{{ selectionInfoText }}</text>
                <view class="actions">
                    <text class="action-btn" @click="$emit('selectAll')">全选</text>
                    <text class="action-btn" @click="$emit('clearSelection')">清空</text>
                </view>
            </view>
            <button class="calculate-btn" @click="$emit('calculate')" :disabled="isCalculateDisabled">
                {{ isCalculating ? '计算中...' : '计算自定义GPA' }}
            </button>
        </view>
    </view>
</template>

<script>
import CustomFooterScript from './CustomFooter.js'
export default CustomFooterScript
</script>

<style lang="scss" scoped>
@import './CustomFooter.scss';
</style>
