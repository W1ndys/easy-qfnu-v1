<template>
    <!-- 空状态 -->
    <view class="empty-state modern-card" v-if="type === 'empty'">
        <view class="empty-content">
            <view class="empty-icon">
                <uni-icons type="info" size="80" color="#adb5bd"></uni-icons>
            </view>
            <text class="empty-title">未找到相关题目</text>
            <text class="empty-subtitle">{{ emptyMessage }}</text>
            <button class="action-btn primary-btn retry-btn" @click="handleRetry">
                <uni-icons type="refresh" size="20" color="#ffffff"></uni-icons>
                <text>重新搜索</text>
            </button>
        </view>
    </view>

    <!-- 初始状态 -->
    <view class="initial-state modern-card" v-else-if="type === 'initial'">
        <view class="initial-content">
            <view class="initial-icon">
                <uni-icons type="help" size="80" color="#7f4515"></uni-icons>
            </view>
            <text class="initial-title">欢迎使用搜索功能</text>
            <text class="initial-subtitle">输入题目关键词，快速找到相关题目和答案</text>
            <view class="tips-section">
                <view class="tip-item">
                    <uni-icons type="checkmarkempty" size="16" color="#52c41a"></uni-icons>
                    <text class="tip-text">支持关键词搜索</text>
                </view>
                <view class="tip-item">
                    <uni-icons type="checkmarkempty" size="16" color="#52c41a"></uni-icons>
                    <text class="tip-text">智能语义匹配</text>
                </view>
                <view class="tip-item">
                    <uni-icons type="checkmarkempty" size="16" color="#52c41a"></uni-icons>
                    <text class="tip-text">精准答案推荐</text>
                </view>
            </view>
        </view>
    </view>

    <!-- 加载状态 -->
    <view class="loading-state modern-card" v-else-if="type === 'loading'">
        <view class="loading-content">
            <view class="loading-spinner">
                <uni-icons type="spinner-cycle" size="60" color="#7f4515"></uni-icons>
            </view>
            <text class="loading-text">正在搜索题目...</text>
            <text class="loading-subtitle">使用AI语义分析匹配相关内容</text>
        </view>
    </view>
</template>

<script>
export default {
    name: 'StateCards',
    props: {
        type: {
            type: String,
            required: true,
            validator: (value) => ['empty', 'initial', 'loading'].includes(value)
        },
        emptyMessage: {
            type: String,
            default: '未找到相关题目，请尝试其他关键词'
        }
    },
    methods: {
        handleRetry() {
            this.$emit('retry');
        }
    }
}
</script>

<style lang="scss" scoped>
@import "./StateCards.scss";
</style>
