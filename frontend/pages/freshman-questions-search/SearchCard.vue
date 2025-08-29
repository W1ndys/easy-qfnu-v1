<template>
    <view class="search-card modern-card">
        <view class="card-header">
            <view class="header-icon">
                <uni-icons type="search" size="24" color="#7f4515"></uni-icons>
            </view>
            <view class="header-text">
                <text class="card-title">智能搜索</text>
                <text class="card-subtitle">输入题目关键词进行语义搜索</text>
            </view>
        </view>

        <view class="form-content">
            <view class="form-group">
                <view class="input-label">
                    <uni-icons type="help" size="20" color="#495057"></uni-icons>
                    <text>题目内容</text>
                </view>
                <view class="input-wrapper">
                    <textarea class="modern-textarea" :class="{
                        'input-error': questionError,
                        'input-focus': questionFocused,
                    }" v-model="searchForm.question" placeholder="请输入题目关键词或完整题目" auto-height @input="validateQuestion"
                        @focus="questionFocused = true" @blur="questionFocused = false" />
                    <view class="input-line" :class="{ active: questionFocused }"></view>
                </view>
                <text class="input-hint" :class="{ 'hint-error': questionError }">
                    {{ questionHint }}
                </text>
            </view>

            <view class="button-group">
                <button class="action-btn primary-btn" @click="handleSearch" :loading="loading" :disabled="!canSearch">
                    <uni-icons type="search" size="20" color="#ffffff" v-if="!loading"></uni-icons>
                    <text>{{ loading ? "搜索中..." : "开始搜索" }}</text>
                </button>
                <button class="action-btn secondary-btn" @click="handleReset">
                    <uni-icons type="refresh" size="20" color="#495057"></uni-icons>
                    <text>重置</text>
                </button>
            </view>
        </view>
    </view>
</template>

<script>
export default {
    name: 'SearchCard',
    props: {
        loading: {
            type: Boolean,
            default: false
        }
    },
    data() {
        return {
            searchForm: {
                question: ""
            },
            questionError: false,
            questionFocused: false
        }
    },
    computed: {
        questionHint() {
            const length = this.searchForm.question.trim().length;
            if (length === 0) {
                return "请输入题目内容或关键词";
            } else if (length < 2) {
                return `至少需要2个字符，当前${length}个字符`;
            } else {
                return `已输入${length}个字符`;
            }
        },
        canSearch() {
            const questionLength = this.searchForm.question.trim().length;
            return questionLength >= 2;
        }
    },
    methods: {
        validateQuestion() {
            const length = this.searchForm.question.trim().length;
            this.questionError = length > 0 && length < 2;
        },
        handleSearch() {
            if (!this.searchForm.question.trim()) {
                uni.showToast({
                    title: "请输入题目内容",
                    icon: "none",
                });
                return;
            }

            if (this.searchForm.question.trim().length < 2) {
                uni.showToast({
                    title: "题目内容至少需要2个字符",
                    icon: "none",
                });
                return;
            }

            this.$emit('search', {
                query: this.searchForm.question.trim()
            });
        },
        handleReset() {
            this.searchForm = {
                question: ""
            };
            this.questionError = false;
            this.$emit('reset');
        }
    }
}
</script>

<style lang="scss" scoped>
// 搜索卡片
.search-card {
    padding: 40rpx;
}

.card-header {
    display: flex;
    align-items: center;
    gap: 24rpx;
    margin-bottom: 50rpx;
}

.header-icon {
    width: 80rpx;
    height: 80rpx;
    background: rgba(127, 69, 21, 0.08);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.header-text {
    flex: 1;
}

.card-title {
    display: block;
    font-size: 32rpx;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 8rpx;
}

.card-subtitle {
    display: block;
    font-size: 24rpx;
    color: #6c757d;
}

// 表单样式
.form-group {
    margin-bottom: 50rpx;

    &:last-child {
        margin-bottom: 0;
    }
}

.input-label {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 20rpx;
    font-size: 28rpx;
    font-weight: 600;
    color: #2c3e50;
}

.input-wrapper {
    position: relative;
}

.modern-textarea {
    width: 100%;
    min-height: 120rpx;
    border: 2rpx solid #e9ecef;
    border-radius: 12rpx;
    padding: 24rpx;
    font-size: 28rpx;
    color: #2c3e50;
    background: #f8fafc;
    transition: all 0.3s ease;
    box-sizing: border-box;

    &:focus {
        border-color: #7f4515;
        background: #ffffff;
        box-shadow: 0 0 0 6rpx rgba(127, 69, 21, 0.1);
    }

    &.input-error {
        border-color: #dc3545;
        background: rgba(220, 53, 69, 0.05);
    }
}

.input-line {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 4rpx;
    background: linear-gradient(90deg, #7f4515, #8c5527);
    border-radius: 2rpx;
    transform: scaleX(0);
    transition: transform 0.3s ease;

    &.active {
        transform: scaleX(1);
    }
}

.input-hint {
    display: block;
    font-size: 22rpx;
    color: #8c8c8c;
    margin-top: 12rpx;
    transition: color 0.3s ease;

    &.hint-error {
        color: #dc3545;
    }
}

// 按钮组
.button-group {
    display: flex;
    gap: 24rpx;
    margin-top: 60rpx;
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
    transition: all 0.3s ease;
    border: none;

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
    color: #ffffff;
    box-shadow: 0 8rpx 24rpx rgba(127, 69, 21, 0.25);

    &:disabled {
        background: #adb5bd;
        color: #6c757d;
        box-shadow: none;
    }

    &:active:not(:disabled) {
        box-shadow: 0 4rpx 12rpx rgba(127, 69, 21, 0.4);
    }
}

.secondary-btn {
    background: #f8f9fa;
    color: #2c3e50;
    border: 2rpx solid #e9ecef;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);

    &:active {
        background: #e9ecef;
        border-color: #dee2e6;
    }
}

// 响应式适配
@media (max-width: 600rpx) {
    .search-card {
        padding: 25rpx;
    }

    .button-group {
        flex-direction: column;
    }
}
</style>
