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
        <DisclaimerCard />

        <!-- 交流群信息 -->
        <GroupInfoCard />

        <!-- 主内容区域 -->
        <view class="content-wrapper">
            <!-- 搜索表单卡片 -->
            <SearchCard :loading="loading" @search="handleSearch" @reset="handleReset" />

            <!-- 搜索结果 -->
            <view class="results-section" v-if="hasResults">
                <view class="results-header">
                    <view class="results-info">
                        <text class="results-title">搜索结果</text>
                        <text class="results-count">找到 {{ searchResults.length }} 个相关题目</text>
                    </view>
                </view>

                <QuestionCard v-for="(result, index) in searchResults" :key="index" :result="result" :index="index" />
            </view>

            <!-- 空状态 -->
            <StateCards v-else-if="searched && !loading" type="empty" :empty-message="emptyMessage"
                @retry="handleReset" />

            <!-- 初始状态 -->
            <StateCards v-else-if="!searched && !loading" type="initial" />

            <!-- 加载状态 -->
            <StateCards v-else-if="loading" type="loading" />
        </view>
    </view>
</template>

<script>
import DisclaimerCard from './DisclaimerCard.vue';
import GroupInfoCard from './GroupInfoCard.vue';
import SearchCard from './SearchCard.vue';
import QuestionCard from './QuestionCard.vue';
import StateCards from './StateCards.vue';

export default {
    components: {
        DisclaimerCard,
        GroupInfoCard,
        SearchCard,
        QuestionCard,
        StateCards
    },
    data() {
        return {
            searchResults: [],
            loading: false,
            searched: false,
            emptyMessage: "未找到相关题目"
        };
    },

    computed: {
        hasResults() {
            return this.searchResults.length > 0;
        }
    },

    onLoad() {
        uni.setNavigationBarTitle({
            title: "新生入学考试辅助",
        });
    },

    methods: {
        async handleSearch(params) {
            this.loading = true;
            this.searched = true;

            try {
                const response = await this.searchQuestions({
                    query: params.query,
                    topk: 3,
                    threshold: 0.2
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
            this.searchResults = [];
            this.searched = false;
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
        }
    }
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
    margin-bottom: 24rpx;
    transition: all 0.3s ease;

    &:hover {
        transform: translateY(-4rpx);
        box-shadow: 0 24rpx 80rpx var(--shadow-medium);
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







// 响应式适配
@media (max-width: 600rpx) {
    .content-wrapper {
        padding: 0 15rpx 30rpx;
    }

    .page-title {
        font-size: 36rpx;
    }
}
</style>