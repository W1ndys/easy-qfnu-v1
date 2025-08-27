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
                    }" v-model="searchForm.question" placeholder="请输入题目关键词或完整题目" auto-height
                        @input="validateQuestion" @focus="questionFocused = true" @blur="questionFocused = false" />
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
@import "./SearchCard.scss";
</style>
