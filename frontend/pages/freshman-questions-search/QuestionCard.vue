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
@import "./QuestionCard.scss";
</style>
