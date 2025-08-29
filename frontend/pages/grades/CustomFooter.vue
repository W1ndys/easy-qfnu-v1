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
import { computed } from 'vue'

export default {
    name: 'CustomFooter',
    props: {
        isCustomMode: {
            type: Boolean,
            default: false
        },
        customGPAResult: {
            type: Object,
            default: null
        },
        selectedCourses: {
            type: Array,
            default: () => []
        },
        allCourses: {
            type: Array,
            default: () => []
        },
        isCalculating: {
            type: Boolean,
            default: false
        }
    },
    emits: ['clearResult', 'selectAll', 'clearSelection', 'calculate'],
    setup(props, { emit }) {
        const selectionInfoText = computed(() => `已选 ${props.selectedCourses.length} / ${props.allCourses.length} 门`)
        const isCalculateDisabled = computed(() => props.isCalculating || props.selectedCourses.length === 0)

        return {
            selectionInfoText,
            isCalculateDisabled
        }
    }
}
</script>

<style lang="scss" scoped>
/* 主题变量 */
$primary-color: #7F4515;
$primary-color-light: #F5EFE6;
$text-color-primary: #343a40;
$text-color-muted: #8c7d70;
$border-color: #f0e9e4;
$background-color-card: #ffffff;
$background-color-light: #fdfcfa;
$border-radius-base: 16rpx;
$border-radius-sm: 12rpx;
$font-size-lg: 30rpx;
$font-size-base: 28rpx;
$font-size-sm: 24rpx;
$font-size-xs: 22rpx;

/* 悬浮操作栏 */
.custom-gpa-footer {
    position: fixed;
    bottom: 0;
    left: 20rpx;
    right: 20rpx;
    background-color: $background-color-card;
    box-shadow: 0 -10rpx 40rpx rgba(0, 0, 0, 0.06);
    padding: 15rpx 25rpx;
    padding-bottom: calc(15rpx + constant(safe-area-inset-bottom));
    padding-bottom: calc(15rpx + env(safe-area-inset-bottom));
    border-top-left-radius: 20rpx;
    border-top-right-radius: 20rpx;
    z-index: 100;
}

.result-display-card {
    background: $background-color-card;
    border: 1rpx solid $border-color;
    border-radius: $border-radius-base;
    margin-bottom: 15rpx;
    box-shadow: 0 8rpx 25rpx rgba(127, 69, 21, 0.05);
    overflow: hidden;

    .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15rpx 20rpx;
        background-color: $background-color-light;

        .result-title {
            font-size: $font-size-base;
            font-weight: bold;
            color: $text-color-primary;
        }

        .close-result-btn {
            font-size: $font-size-sm;
            color: $text-color-muted;
            padding: 5rpx 15rpx;
            border-radius: 10rpx;

            &:active {
                background-color: $border-color;
            }
        }
    }

    .result-content {
        display: flex;
        align-items: center;
        padding: 25rpx 20rpx;
    }

    .result-gpa {
        flex-shrink: 0;
        text-align: center;
        padding-right: 30rpx;
        margin-right: 30rpx;
        border-right: 1rpx solid $border-color;

        .gpa-value {
            display: block;
            font-size: 60rpx;
            font-weight: bold;
            color: $primary-color;
            line-height: 1;
        }

        .gpa-label {
            display: block;
            font-size: $font-size-xs;
            color: $text-color-muted;
            margin-top: 8rpx;
        }
    }

    .result-stats {
        flex-grow: 1;
        display: flex;
        justify-content: space-around;

        .stat-item {
            text-align: center;

            .stat-value {
                display: block;
                font-size: 34rpx;
                font-weight: bold;
                color: $text-color-primary;
            }

            .stat-label {
                display: block;
                font-size: $font-size-xs;
                color: $text-color-muted;
                margin-top: 4rpx;
            }
        }
    }
}

.footer-actions {
    display: flex;
    flex-direction: column;
    gap: 15rpx;
}

.selection-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 10rpx;

    .info-text {
        font-size: 26rpx;
        color: $text-color-primary;
    }

    .actions {
        display: flex;
        gap: 20rpx;

        .action-btn {
            font-size: $font-size-sm;
            color: $primary-color;
            padding: 8rpx 16rpx;
            background: $primary-color-light;
            border-radius: $border-radius-sm;
        }
    }
}

.calculate-btn {
    width: 100%;
    background: $primary-color;
    color: #ffffff;
    border: none;
    border-radius: $border-radius-base;
    padding: 24rpx;
    font-size: $font-size-lg;
    font-weight: bold;

    &:disabled {
        background: #c0b8b1;
        opacity: 0.7;
    }
}
</style>
