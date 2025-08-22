<template>
    <view class="page-container page-rounded-container">
        <!-- 背景装饰 -->
        <view class="background-decoration">
            <view class="circle circle-1"></view>
            <view class="circle circle-2"></view>
            <view class="circle circle-3"></view>
        </view>

        <!-- 页面头部 -->
        <view class="page-header">
            <view class="header-content">
                <text class="page-title">新生入学考试辅助</text>
                <text class="page-subtitle">Freshman Examination Q&A</text>
            </view>
        </view>

        <!-- 免责声明 -->
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

        <!-- 主内容区域 -->
        <view class="content-wrapper">
            <!-- 搜索表单卡片 -->
            <view class="search-card modern-card">
                <view class="card-header">
                    <view class="header-icon">
                        <uni-icons type="search" size="24" color="#7f4515"></uni-icons>
                    </view>
                    <view class="header-text">
                        <text class="card-title">智能搜题</text>
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
                                @input="validateQuestion" @focus="questionFocused = true"
                                @blur="questionFocused = false" />
                            <view class="input-line" :class="{ active: questionFocused }"></view>
                        </view>
                        <text class="input-hint" :class="{ 'hint-error': questionError }">
                            {{ questionHint }}
                        </text>
                    </view>

                    <view class="button-group">
                        <button class="action-btn primary-btn" @click="handleSearch" :loading="loading"
                            :disabled="!canSearch">
                            <uni-icons type="search" size="20" color="#ffffff" v-if="!loading"></uni-icons>
                            <text>{{ loading ? "搜索中..." : "开始搜题" }}</text>
                        </button>
                        <button class="action-btn secondary-btn" @click="handleReset">
                            <uni-icons type="refresh" size="20" color="#495057"></uni-icons>
                            <text>重置</text>
                        </button>
                    </view>
                </view>
            </view>

            <!-- 搜索结果 -->
            <view class="results-section" v-if="hasResults">
                <view class="results-header">
                    <view class="results-info">
                        <text class="results-title">搜索结果</text>
                        <text class="results-count">找到 {{ searchResults.length }} 个相关题目</text>
                    </view>
                </view>

                <view class="question-card modern-card" v-for="(result, index) in searchResults" :key="index">
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
                            <text class="section-label">题目内容：</text>
                            <text class="question-text">{{ result.question }}</text>
                        </view>

                        <!-- 选项显示 -->
                        <view class="options-section" v-if="result.options">
                            <text class="section-label">选项：</text>
                            <view class="options-list">
                                <view class="option-item"
                                    :class="{ 'correct-option': result.answer && option.key === result.answer.letter }"
                                    v-for="option in formatOptions(result.options)" :key="option.key">
                                    <text class="option-label">{{ option.key }}.</text>
                                    <text class="option-text">{{ option.value }}</text>
                                    <view class="correct-mark"
                                        v-if="result.answer && option.key === result.answer.letter">
                                        <uni-icons type="checkmarkempty" size="16" color="#52c41a"></uni-icons>
                                    </view>
                                </view>
                            </view>
                        </view>

                        <view class="answer-section" v-if="result.answer">
                            <text class="section-label">参考答案：</text>
                            <view class="answer-content">
                                <view class="answer-item">
                                    <text class="answer-letter">{{ result.answer.letter }}</text>
                                    <text class="answer-text">{{ result.answer.text }}</text>
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
            </view>

            <!-- 空状态 -->
            <view class="empty-state modern-card" v-else-if="searched && !loading">
                <view class="empty-content">
                    <view class="empty-icon">
                        <uni-icons type="info" size="80" color="#adb5bd"></uni-icons>
                    </view>
                    <text class="empty-title">未找到相关题目</text>
                    <text class="empty-subtitle">{{ emptyMessage }}</text>
                    <button class="action-btn primary-btn retry-btn" @click="handleReset">
                        <uni-icons type="refresh" size="20" color="#ffffff"></uni-icons>
                        <text>重新搜索</text>
                    </button>
                </view>
            </view>

            <!-- 初始状态 -->
            <view class="initial-state modern-card" v-else-if="!searched && !loading">
                <view class="initial-content">
                    <view class="initial-icon">
                        <uni-icons type="help" size="80" color="#7f4515"></uni-icons>
                    </view>
                    <text class="initial-title">欢迎使用搜题功能</text>
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
            <view class="loading-state modern-card" v-else-if="loading">
                <view class="loading-content">
                    <view class="loading-spinner">
                        <uni-icons type="spinner-cycle" size="60" color="#7f4515"></uni-icons>
                    </view>
                    <text class="loading-text">正在搜索题目...</text>
                    <text class="loading-subtitle">使用AI语义分析匹配相关内容</text>
                </view>
            </view>
        </view>
    </view>
</template>

<script>
export default {
    data() {
        return {
            searchForm: {
                question: "",
            },
            searchResults: [],
            loading: false,
            searched: false,
            emptyMessage: "未找到相关题目",
            questionError: false,
            questionFocused: false,
        };
    },

    computed: {
        hasResults() {
            return this.searchResults.length > 0;
        },

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
        },
    },

    onLoad() {
        uni.setNavigationBarTitle({
            title: "新生考试搜题",
        });
    },

    methods: {
        validateQuestion() {
            const length = this.searchForm.question.trim().length;
            this.questionError = length > 0 && length < 2;
        },

        async handleSearch() {
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

            this.loading = true;
            this.searched = true;

            try {
                const response = await this.searchQuestions({
                    query: this.searchForm.question.trim(),
                    topk: 3,
                    threshold: 0.55
                });

                if (response.ok) {
                    this.searchResults = response.results || [];
                    if (!this.hasResults) {
                        this.emptyMessage = "未找到相关题目，请尝试其他关键词";
                    }
                } else {
                    this.searchResults = [];
                    this.emptyMessage = response.message || "搜索失败";
                    uni.showToast({
                        title: this.emptyMessage,
                        icon: "none",
                    });
                }
            } catch (error) {
                console.error("搜索题目失败:", error);
                this.searchResults = [];

                let errorMessage = "网络错误，请重试";
                if (error.message) {
                    if (error.message.includes("HTTP 422")) {
                        errorMessage = "输入参数格式错误，请检查输入内容";
                    } else if (error.message.includes("HTTP 400")) {
                        errorMessage = "请求参数错误，请检查输入内容";
                    } else if (error.message.includes("HTTP 500")) {
                        errorMessage = "服务器内部错误，请稍后重试";
                    } else if (error.message.includes("HTTP")) {
                        errorMessage = `请求失败: ${error.message}`;
                    }
                }

                this.emptyMessage = errorMessage;
                uni.showToast({
                    title: errorMessage,
                    icon: "none",
                    duration: 3000,
                });
            } finally {
                this.loading = false;
            }
        },

        handleReset() {
            this.searchForm = {
                question: "",
            };
            this.searchResults = [];
            this.searched = false;
            this.questionError = false;
        },

        async searchQuestions(params) {
            const baseURL = getApp().globalData.apiBaseURL;

            return new Promise((resolve, reject) => {
                uni.request({
                    url: `${baseURL}/api/v1/question/freshman-question-search`,
                    method: "POST",
                    data: params,
                    header: {
                        "Content-Type": "application/json",
                    },
                    success: (res) => {
                        if (res.statusCode !== 200) {
                            console.error("API请求失败:", res);
                            reject(
                                new Error(
                                    `HTTP ${res.statusCode}: ${res.data?.message || "请求失败"}`
                                )
                            );
                            return;
                        }

                        resolve(res.data);
                    },
                    fail: (err) => {
                        reject(err);
                    },
                });
            });
        },

        formatOptions(options) {
            if (!options || typeof options !== 'object') {
                return [];
            }

            return Object.keys(options).map(key => ({
                key: key,
                value: options[key]
            })).sort((a, b) => a.key.localeCompare(b.key));
        },
    },
};
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

// 页面容器
.page-container {
    min-height: 100vh;
    background: #f7f8fa;
    position: relative;
    overflow: hidden;
}

// 外层圆角容器
.page-rounded-container {
    background: #ffffff;
    border-radius: 40rpx;
    padding: 20rpx 20rpx 30rpx;
    box-shadow: 0 20rpx 60rpx var(--shadow-light);
    border: 1rpx solid var(--border-light);
}

// 背景装饰
.background-decoration {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
}

.circle {
    position: absolute;
    border-radius: 50%;
    background: rgba(127, 69, 21, 0.06);

    &.circle-1 {
        width: 200rpx;
        height: 200rpx;
        top: 10%;
        right: -50rpx;
        animation: float 6s ease-in-out infinite;
    }

    &.circle-2 {
        width: 150rpx;
        height: 150rpx;
        bottom: 20%;
        left: -30rpx;
        animation: float 8s ease-in-out infinite reverse;
    }

    &.circle-3 {
        width: 100rpx;
        height: 100rpx;
        top: 30%;
        left: 20%;
        animation: float 4s ease-in-out infinite;
    }
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0px) rotate(0deg);
    }

    50% {
        transform: translateY(-20rpx) rotate(180deg);
    }
}

// 页面头部
.page-header {
    padding: 40rpx 30rpx 30rpx;
    position: relative;
    z-index: 1;
}

.header-content {
    text-align: center;
}

.page-title {
    display: block;
    font-size: 44rpx;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 12rpx;
    letter-spacing: 1rpx;
}

.page-subtitle {
    display: block;
    font-size: 24rpx;
    color: #7f8c8d;
    font-style: italic;
}

// 免责声明样式
.disclaimer-card {
    margin: 0 30rpx 20rpx;
    padding: 30rpx;
    background: linear-gradient(135deg, rgba(255, 107, 53, 0.05), rgba(255, 107, 53, 0.08));
    border: 1rpx solid rgba(255, 107, 53, 0.2);
    border-left: 6rpx solid #ff6b35;
}

.disclaimer-header {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-bottom: 20rpx;
}

.disclaimer-icon {
    width: 40rpx;
    height: 40rpx;
    display: flex;
    align-items: center;
    justify-content: center;
}

.disclaimer-title {
    font-size: 28rpx;
    font-weight: 700;
    color: #ff6b35;
}

.disclaimer-content {
    padding-left: 56rpx;
}

.disclaimer-text {
    font-size: 24rpx;
    color: #495057;
    line-height: 1.6;
    word-break: break-word;
}

// 内容区域
.content-wrapper {
    padding: 0 30rpx 30rpx;
    position: relative;
    z-index: 1;
}

// 现代化卡片
.modern-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20rpx);
    border-radius: var(--radius-large);
    border: 1rpx solid var(--border-light);
    box-shadow: 0 20rpx 60rpx var(--shadow-light);
    margin-bottom: 40rpx;
    transition: all 0.3s ease;

    &:hover {
        transform: translateY(-4rpx);
        box-shadow: 0 24rpx 80rpx var(--shadow-medium);
    }
}

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
    color: var(--text-primary);
    margin-bottom: 8rpx;
}

.card-subtitle {
    display: block;
    font-size: 24rpx;
    color: var(--text-secondary);
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
    color: var(--text-primary);
}

.input-wrapper {
    position: relative;
}

.modern-textarea {
    width: 100%;
    min-height: 120rpx;
    border: 2rpx solid #e9ecef;
    border-radius: var(--radius-small);
    padding: 24rpx;
    font-size: 28rpx;
    color: var(--text-primary);
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
    color: var(--text-light);
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
    color: var(--text-primary);
    border: 2rpx solid #e9ecef;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);

    &:active {
        background: #e9ecef;
        border-color: #dee2e6;
    }
}

// 结果区域
.results-header {
    padding: 20rpx 30rpx;
    text-align: center;
    margin-bottom: 20rpx;
}

.results-info {
    display: flex;
    flex-direction: column;
    gap: 6rpx;
}

.results-title {
    font-size: 28rpx;
    font-weight: 600;
    color: var(--text-primary);
}

.results-count {
    font-size: 22rpx;
    color: var(--text-secondary);
}

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
.options-section,
.answer-section {
    margin-bottom: 30rpx;

    &:last-child {
        margin-bottom: 0;
    }
}

.section-label {
    display: block;
    font-size: 26rpx;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 16rpx;
}

.question-text {
    font-size: 28rpx;
    color: var(--text-primary);
    line-height: 1.6;
    word-break: break-word;
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
    border-radius: var(--radius-small);
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
    color: var(--text-primary);
    min-width: 32rpx;
}

.option-text {
    font-size: 26rpx;
    color: var(--text-secondary);
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

// 答案样式
.answer-content {
    background: linear-gradient(135deg, rgba(127, 69, 21, 0.05), rgba(127, 69, 21, 0.08));
    border-radius: var(--radius-small);
    padding: 20rpx;
    border-left: 6rpx solid #7f4515;
}

.answer-item {
    display: flex;
    align-items: center;
    gap: 16rpx;
}

.answer-letter {
    width: 48rpx;
    height: 48rpx;
    background: linear-gradient(135deg, #7f4515, #8c5527);
    color: #ffffff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24rpx;
    font-weight: 700;
    flex-shrink: 0;
}

.answer-text {
    font-size: 26rpx;
    color: var(--text-primary);
    line-height: 1.6;
    font-weight: 500;
    flex: 1;
}

// 状态页面样式
.empty-state,
.initial-state,
.loading-state {
    padding: 80rpx 40rpx;
}

.empty-content,
.initial-content,
.loading-content {
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 30rpx;
}

.empty-icon,
.initial-icon,
.loading-spinner {
    opacity: 0.6;
}

.empty-title,
.initial-title,
.loading-text {
    font-size: 32rpx;
    font-weight: 600;
    color: var(--text-primary);
}

.empty-subtitle,
.initial-subtitle,
.loading-subtitle {
    font-size: 24rpx;
    color: var(--text-secondary);
    text-align: center;
    line-height: 1.5;
}

.retry-btn {
    width: 200rpx;
    margin-top: 20rpx;
}

// 提示区域
.tips-section {
    display: flex;
    flex-direction: column;
    gap: 16rpx;
    margin-top: 30rpx;
}

.tip-item {
    display: flex;
    align-items: center;
    gap: 12rpx;
    padding: 12rpx 20rpx;
    background: rgba(127, 69, 21, 0.05);
    border-radius: 12rpx;
    border: 1rpx solid rgba(127, 69, 21, 0.1);
}

.tip-text {
    font-size: 24rpx;
    color: var(--text-secondary);
}

// 加载动画
@keyframes spin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

.loading-spinner {
    animation: spin 1s linear infinite;
}

// 响应式适配
@media (max-width: 600rpx) {
    .disclaimer-card {
        margin: 0 15rpx 20rpx;
        padding: 24rpx;
    }

    .disclaimer-content {
        padding-left: 0;
        margin-top: 16rpx;
    }

    .disclaimer-text {
        font-size: 22rpx;
    }

    .content-wrapper {
        padding: 0 15rpx 30rpx;
    }

    .search-card {
        padding: 25rpx;
    }

    .button-group {
        flex-direction: column;
    }

    .page-title {
        font-size: 36rpx;
    }

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

    .answer-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 12rpx;
    }

    .answer-letter {
        align-self: flex-start;
    }
}
</style>