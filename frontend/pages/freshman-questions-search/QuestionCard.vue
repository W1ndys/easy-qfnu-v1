<template>
    <view class="question-card modern-card">
        <view class="question-header">
            <view class="question-info">
                <view class="question-icon">
                    <uni-icons type="help-filled" size="20" color="#7f4515"></uni-icons>
                </view>
                <text class="question-number">题目 {{ index + 1 }}</text>
                <view class="type-badge" v-if="result.type">
                    <text class="type-text">{{ result.type }}</text>
                </view>
                <view class="similarity-badge">
                    <text class="similarity-text">相似度: {{ (result.score * 100).toFixed(1) }}%</text>
                </view>
            </view>
        </view>

        <view class="question-content">
            <view class="question-text-section">
                <text class="question-text">{{ result.question }}</text>
            </view>

            <!-- 选项显示 -->
            <view class="options-section" v-if="result.options">
                <view class="options-list">
                    <view class="option-item"
                        :class="{ 'correct-option': result.answer && option.key === result.answer.letter }"
                        v-for="option in formatOptions(result.options)" :key="option.key">
                        <text class="option-label">{{ option.key }}.</text>
                        <text class="option-text">{{ option.value }}</text>
                        <view class="correct-mark" v-if="result.answer && option.key === result.answer.letter">
                            <uni-icons type="checkmarkempty" size="16" color="#52c41a"></uni-icons>
                        </view>
                    </view>
                </view>
            </view>

            <view class="question-meta" v-if="result.category || result.difficulty || result.type">
                <view class="meta-item" v-if="result.type">
                    <text class="meta-label">类型</text>
                    <text class="meta-value">{{ result.type }}</text>
                </view>
                <view class="meta-item" v-if="result.category">
                    <text class="meta-label">分类</text>
                    <text class="meta-value">{{ result.category }}</text>
                </view>
                <view class="meta-item" v-if="result.difficulty">
                    <text class="meta-label">难度</text>
                    <text class="meta-value">{{ result.difficulty }}</text>
                </view>
            </view>
        </view>
    </view>
</template>

<script>
export default {
    name: 'QuestionCard',
    props: {
        result: {
            type: Object,
            required: true
        },
        index: {
            type: Number,
            required: true
        }
    },
    methods: {
        formatOptions(options) {
            if (!options || typeof options !== 'object') {
                return [];
            }

            return Object.keys(options).map(key => ({
                key: key,
                value: options[key]
            })).sort((a, b) => a.key.localeCompare(b.key));
        }
    }
}
</script>

<style lang="scss" scoped>
// 题目卡片
.question-card {
    padding: 0;
    overflow: hidden;
    margin-bottom: 24rpx;
}

.question-header {
    background: linear-gradient(135deg, #7f4515, #8c5527);
    padding: 24rpx 30rpx;
}

.question-info {
    display: flex;
    align-items: center;
    gap: 16rpx;
    flex-wrap: wrap;
}

.question-icon {
    width: 44rpx;
    height: 44rpx;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.question-number {
    font-size: 28rpx;
    font-weight: 600;
    color: #ffffff;
    flex: 1;
    min-width: 120rpx;
}

.type-badge {
    background: rgba(255, 255, 255, 0.25);
    padding: 6rpx 12rpx;
    border-radius: 16rpx;
    border: 1rpx solid rgba(255, 255, 255, 0.3);
}

.type-text {
    font-size: 20rpx;
    color: #ffffff;
    font-weight: 500;
}

.similarity-badge {
    background: rgba(255, 255, 255, 0.2);
    padding: 8rpx 16rpx;
    border-radius: 20rpx;
    border: 1rpx solid rgba(255, 255, 255, 0.3);
}

.similarity-text {
    font-size: 22rpx;
    color: #ffffff;
    font-weight: 500;
}

.question-content {
    padding: 30rpx;
}

.question-text-section,
.options-section {
    margin-bottom: 30rpx;

    &:last-child {
        margin-bottom: 0;
    }
}

.question-text {
    font-size: 28rpx;
    color: #2c3e50;
    line-height: 1.6;
    word-break: break-word;
    margin-bottom: 24rpx;
}

// 选项样式
.options-list {
    display: flex;
    flex-direction: column;
    gap: 12rpx;
}

.option-item {
    display: flex;
    align-items: center;
    gap: 12rpx;
    padding: 16rpx 20rpx;
    background: #f8f9fa;
    border-radius: 12rpx;
    border: 2rpx solid transparent;
    transition: all 0.3s ease;
    position: relative;

    &.correct-option {
        background: rgba(82, 196, 26, 0.08);
        border-color: rgba(82, 196, 26, 0.3);
        box-shadow: 0 2rpx 8rpx rgba(82, 196, 26, 0.15);
    }
}

.option-label {
    font-size: 26rpx;
    font-weight: 600;
    color: #2c3e50;
    min-width: 32rpx;
}

.option-text {
    font-size: 26rpx;
    color: #6c757d;
    line-height: 1.5;
    flex: 1;
}

.correct-mark {
    margin-left: auto;
    width: 28rpx;
    height: 28rpx;
    background: rgba(82, 196, 26, 0.1);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

// 元信息样式
.question-meta {
    display: flex;
    gap: 16rpx;
    flex-wrap: wrap;
    padding-top: 20rpx;
    border-top: 1rpx solid #f0f0f0;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 8rpx;
    padding: 8rpx 12rpx;
    background: #f8f9fa;
    border-radius: 8rpx;
    border: 1rpx solid #e9ecef;
}

.meta-label {
    font-size: 22rpx;
    color: #8c8c8c;
    font-weight: 500;
}

.meta-value {
    font-size: 22rpx;
    color: #2c3e50;
    font-weight: 600;
}

// 响应式适配
@media (max-width: 600rpx) {
    .question-card {
        margin-bottom: 20rpx;
    }

    .question-header {
        padding: 20rpx 24rpx;
    }

    .question-content {
        padding: 24rpx;
    }

    .question-info {
        flex-direction: column;
        align-items: flex-start;
        gap: 12rpx;
    }

    .question-number {
        flex: none;
        width: 100%;
    }

    .type-badge,
    .similarity-badge {
        align-self: flex-start;
    }

    .question-meta {
        flex-direction: column;
        align-items: flex-start;
    }

    .option-item {
        padding: 12rpx 16rpx;
    }
}
</style>
