<template>
    <PageLayout>
        <LoadingScreen v-if="isLoading" text="正在加载数据，加载完成后会在下方显示..." />

        <!-- 使用提示弹窗 -->
        <view v-if="showTipModal" class="tip-modal-overlay" :class="{ closing: isClosing }" @click="closeTipModal">
            <view class="tip-modal" @click.stop>
                <view class="tip-header">
                    <text class="tip-title">使用提示</text>
                    <view class="tip-close" @click="closeTipModal">
                        <uni-icons type="close" size="20" color="#868e96" />
                    </view>
                </view>
                <view class="tip-content" style="flex-direction: row; flex-wrap: wrap; justify-content: center;">
                    <text class="tip-text">
                        本数据基于
                        <text style="font-weight: bold; color: #7F4515;">你个人的学生身份</text>
                        和
                        <text style="font-weight: bold; color: #7F4515;">当前开放的</text>
                        选课年级库进行搜索，如果搜索没有结果，但你从夫子校园或其他地方搜到了开课数据，说明当前教务系统的开课数据对你
                        <text style="font-weight: bold; color: #f56c6c;">不开放</text>
                        搜索权限。由于教学安排和教务系统限制，本页面搜索结果不保证准确。
                        <text style="font-weight: bold; color: #f56c6c;">仅供参考</text>
                        ，请以实际为准。
                        <br />
                        <text style="font-weight: bold; color: #198754;">公选课数据一般是准确的</text>，因为本模块与培养方案无关，公选课开放情况以教务系统为准。
                    </text>
                </view>
                <view class="tip-footer">
                    <button class="tip-btn" @click="closeTipModal">我已知晓</button>
                </view>
            </view>
        </view>

        <view v-else class="page-container">
            <view class="background-decoration">
                <view class="circle circle-1"></view>
                <view class="circle circle-2"></view>
                <view class="circle circle-3"></view>
            </view>

            <view class="page-header">
                <view class="header-content">
                    <text class="page-title">预选课查询</text>
                    <text class="page-subtitle">Pre-select Course Search</text>
                </view>
            </view>

            <view class="content-wrapper">
                <ModernCard title="筛选与操作">
                    <view class="filters-grid">
                        <view class="form-item">
                            <text class="label">课程名/编号</text>
                            <input class="input" v-model.trim="query.course_id_or_name" placeholder="如 大学英语 或 g1234" />
                        </view>
                        <view class="form-item">
                            <text class="label">教师名</text>
                            <input class="input" v-model.trim="query.teacher_name" placeholder="如 张三" />
                        </view>
                        <view class="form-item">
                            <text class="label">星期</text>
                            <picker mode="selector" :range="weekOptions" @change="onWeekChange">
                                <view class="picker-value" :class="{ 'is-selected': query.week_day }">
                                    {{
                                        query.week_day
                                            ? `星期${query.week_day}`
                                            : "选择星期（可选）"
                                    }}
                                </view>
                            </picker>
                        </view>
                        <view class="form-item">
                            <text class="label">节次</text>
                            <picker mode="selector" :range="classPeriodOptionsDisplay" @change="onClassPeriodChange">
                                <view class="picker-value" :class="{ 'is-selected': query.class_period }">
                                    {{
                                        query.class_period
                                            ? `${query.class_period}节`
                                            : "选择节次（可选）"
                                    }}
                                </view>
                            </picker>
                        </view>
                    </view>

                    <view class="search-tip"
                        style="margin: 12rpx 0 0 0; color: #868e96; font-size: 24rpx; line-height: 1.7;">
                        <view>支持模糊搜索，建议使用课程代码，速度更快，结果更精准。</view>
                        <view>如果课余量显示-，大概率是选修课，原因是选修课模块教务系统后端没有提供课余量数据，请使用我们的友情网站 <a href="http://xk.s.fz.z-xin.net"
                                target="_blank" rel="noopener" style="color:#007aff;text-decoration:underline;">夫子校园</a>
                            辅助查询</view>
                    </view>

                    <view class="card-actions-wrapper">
                        <button class="action-btn secondary-btn" @click="handleSecondary">
                            <uni-icons type="refresh" size="20" color="#495057" />
                            <text>重置</text>
                        </button>
                        <button class="action-btn primary-btn" @click="handlePrimary">
                            <uni-icons type="paperplane" size="20" color="#fff" />
                            <text>查询</text>
                        </button>
                    </view>
                </ModernCard>

                <ModernCard v-if="debugInfo" title="查询出错">
                    <view class="card-section">
                        <text class="section-desc">抱歉，查询时遇到问题，请稍后重试。</text>
                        <text class="section-desc muted-text">状态码：{{ debugInfo.statusCode }}</text>

                        <!-- 显示具体错误信息 -->
                        <view v-if="debugInfo.message" class="error-details">
                            <text class="error-label">错误详情：</text>
                            <text class="error-message">{{ debugInfo.message }}</text>
                        </view>
                    </view>
                    <view class="button-group" style="margin-top: -500rpx">
                        <button class="action-btn secondary-btn" @click="copyDebug">
                            <uni-icons type="copy" size="20" color="#495057" />
                            <text>复制详细诊断信息</text>
                        </button>
                    </view>
                </ModernCard>

                <EmptyState v-if="!hasData" icon-type="info-filled" title="暂无结果" description="请先输入课程名/编号或教师名进行查询"
                    :show-retry="false" style="margin-top: -120rpx;" />

                <view v-else class="results-container">
                    <view class="results-summary">
                        <text>查询到 {{ totalCount }} 门相关课程，已按模块分组</text>
                    </view>

                    <uni-collapse v-model="activeCollapseItems" class="results-collapse">
                        <uni-collapse-item v-for="m in data.modules" :key="m.module" :name="m.module"
                            :title="`${m.module_name} (${m.count || 0})`">
                            <view v-if="m.courses && m.courses.length" class="course-list">
                                <view class="course-item" v-for="c in m.courses"
                                    :key="`${m.module}-${c.course_id}-${c.group_name}`">
                                    <view class="course-header">
                                        <view class="course-title-group">
                                            <view class="course-name clickable"
                                                @click="copyToClipboard(c.course_name, '课程名称')">
                                                <text>{{ c.course_name }}</text>
                                                <uni-icons type="copy" size="14" color="#868e96" class="copy-icon" />
                                            </view>
                                            <view class="course-meta clickable"
                                                @click="copyToClipboard(c.course_id + ' / ' + c.group_name, '课程信息')">
                                                <text>{{ c.course_id }} / {{ c.group_name }}</text>
                                                <uni-icons type="copy" size="14" color="#868e96" class="copy-icon" />
                                            </view>
                                        </view>
                                        <view class="meta-tags">
                                            <text class="pill pill-ghost" v-if="c.credits">{{ c.credits }} 学分</text>
                                            <text class="pill" :class="c.remain_count > 0 ? 'pill-success' : 'pill-danger'
                                                ">
                                                余量 {{ c.remain_count ?? "未知" }}
                                            </text>
                                        </view>
                                    </view>

                                    <view class="course-details">
                                        <view class="detail-item clickable"
                                            @click="copyToClipboard(c.teacher_name, '教师姓名')">
                                            <uni-icons type="person" size="16" color="#868e96" />
                                            <text>{{ c.teacher_name }}</text>
                                            <uni-icons type="copy" size="14" color="#868e96" class="copy-icon" />
                                        </view>
                                        <view class="detail-item clickable"
                                            @click="copyToClipboard(c.location + ' @ ' + c.campus_name, '上课地点')">
                                            <uni-icons type="location" size="16" color="#868e96" />
                                            <text>{{ c.location }} @ {{ c.campus_name }}</text>
                                            <uni-icons type="copy" size="14" color="#868e96" class="copy-icon" />
                                        </view>
                                        <view class="detail-item full-width clickable"
                                            @click="copyToClipboard(c.time_text, '上课时间')">
                                            <uni-icons type="calendar" size="16" color="#868e96" />
                                            <text>{{ c.time_text }}</text>
                                            <uni-icons type="copy" size="14" color="#868e96" class="copy-icon" />
                                        </view>
                                    </view>

                                    <view class="conflict-box" v-if="c.time_conflict">
                                        <uni-icons type="info" size="18" color="#c92a2a" />
                                        <text class="conflict-text">{{ c.time_conflict }}</text>
                                    </view>
                                </view>
                            </view>
                            <view v-else class="empty-module">
                                <text class="muted-text">本模块无相关课程</text>
                            </view>
                        </uni-collapse-item>
                    </uni-collapse>
                </view>
            </view>
        </view>
    </PageLayout>
</template>

<script setup>
import { ref, computed } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import PageLayout from "../../components/PageLayout/PageLayout.vue";
import ModernCard from "../../components/ModernCard/ModernCard.vue";
import LoadingScreen from "../../components/LoadingScreen/LoadingScreen.vue";
import EmptyState from "../../components/EmptyState/EmptyState.vue";
// uni-collapse 和 uni-icons 通常通过 uni-ui 的 easycom 自动引入，无需手动 import

const isLoading = ref(true);
const data = ref(null);
const debugInfo = ref(null);
const activeCollapseItems = ref([]); // 控制手风琴展开项
const showTipModal = ref(true); // 控制提示弹窗显示

const query = ref({
    course_id_or_name: "",
    teacher_name: "",
    week_day: "",
    class_period: "",
});
const weekOptions = ["1", "2", "3", "4", "5", "6", "7"];
const classPeriodOptions = ["1-2", "3-4", "5-6", "7-8", "9-11", "12-13"];
const classPeriodOptionsDisplay = classPeriodOptions.map((s) => `${s}节`);

const hasData = computed(() => {
    const d = data.value;
    if (!d || !Array.isArray(d.modules)) return false;
    return d.modules.some(
        (m) => Array.isArray(m.courses) && m.courses.length > 0
    );
});

const totalCount = computed(() => {
    const d = data.value;
    if (!d || !Array.isArray(d.modules)) return 0;
    return d.modules.reduce((sum, m) => sum + (m.count || 0), 0);
});

onLoad(() => {
    if (!ensureLogin()) return;
    uni.setNavigationBarTitle({ title: "预选课查询" });
    isLoading.value = false;
    // 显示使用提示弹窗
    showTipModal.value = true;
});

onShow(() => {
    if (!ensureLogin()) return;
});

function ensureLogin() {
    const token = uni.getStorageSync("token");
    if (!token) {
        uni.showToast({ title: "请先登录", icon: "none" });
        uni.reLaunch({ url: "/pages/index/index" });
        return false;
    }
    return true;
}

function onWeekChange(e) {
    query.value.week_day = weekOptions[e.detail.value];
}
function onClassPeriodChange(e) {
    query.value.class_period = classPeriodOptions[e.detail.value];
}



function buildPayload() {
    const q = {
        course_id_or_name: query.value.course_id_or_name?.trim(),
        teacher_name: query.value.teacher_name?.trim(),
        week_day: query.value.week_day?.trim(),
        class_period: query.value.class_period?.trim(),
    };
    return Object.fromEntries(Object.entries(q).filter(([, v]) => !!v));
}

async function fetchData() {
    if (!ensureLogin()) return;
    const payload = buildPayload();
    if (!payload.course_id_or_name && !payload.teacher_name) {
        uni.showToast({ title: "请填写课程名/编号或教师名", icon: "none" });
        return;
    }

    isLoading.value = true;
    const token = uni.getStorageSync("token");
    const baseURL = getApp().globalData.apiBaseURL;
    const url = `${baseURL}/api/v1/pre-select-course/query`;

    try {
        const {
            statusCode,
            data: res,
            header,
        } = await uni.request({
            url,
            method: "POST",
            header: {
                "Content-Type": "application/json",
                ...(token ? { Authorization: "Bearer " + token } : {}),
            },
            data: payload,
        });

        if (statusCode === 200 && res && res.ok) {
            data.value = res.data || { modules: [], errors: [] };
            if (!Array.isArray(data.value.modules)) data.value.modules = [];
            if (!Array.isArray(data.value.errors)) data.value.errors = [];
            debugInfo.value = null;
            // MODIFIED: 默认展开所有有结果的模块
            if (hasData.value) {
                activeCollapseItems.value = data.value.modules
                    .filter((m) => m.courses && m.courses.length > 0)
                    .map((m) => m.module);
            } else {
                activeCollapseItems.value = [];
            }
        } else if (statusCode === 401 || statusCode === 403) {
            uni.removeStorageSync("token");
            uni.showToast({ title: "登录已过期，请重新登录", icon: "none" });
            setTimeout(() => uni.reLaunch({ url: "/pages/index/index" }), 1200);
        } else {
            const allow = header?.Allow || header?.allow;
            const message = (res && (res.detail || res.message)) || "查询失败";
            uni.showToast({ title: message, icon: "none" });
            data.value = { modules: [], errors: [] };
            debugInfo.value = {
                url,
                method: "POST",
                payload: JSON.stringify(payload),
                statusCode,
                allow: allow || "",
                message: typeof res === "string" ? res : JSON.stringify(res),
            };
            console.warn("预选课查询失败", debugInfo.value);
        }
    } catch (e) {
        console.error("请求失败", e);
        uni.showToast({ title: "网络连接失败", icon: "none" });
        data.value = { modules: [], errors: [] };
        debugInfo.value = {
            url,
            method: "POST",
            payload: JSON.stringify(payload),
            statusCode: -1,
            allow: "",
            message: String(e?.message || e),
        };
    } finally {
        isLoading.value = false;
    }
}

function copyDebug() {
    if (!debugInfo.value) return;
    const text = JSON.stringify(debugInfo.value, null, 2);
    uni.setClipboardData({
        data: text,
        success: () => uni.showToast({ title: "已复制", icon: "none" }),
    });
}

function handlePrimary() {
    fetchData();
}

function handleSecondary() {
    query.value = {
        course_id_or_name: "",
        teacher_name: "",
        week_day: "",
        class_period: "",
    };
    data.value = null;
    activeCollapseItems.value = [];
}

const isClosing = ref(false);

function closeTipModal() {
    if (isClosing.value) return;
    isClosing.value = true;
    setTimeout(() => {
        showTipModal.value = false;
        isClosing.value = false;
    }, 200);
}

function copyToClipboard(text, label) {
    uni.setClipboardData({
        data: text,
        success: () => {
            uni.showToast({
                title: `${label}已复制`,
                icon: "none",
            });
        },
        fail: () => {
            uni.showToast({
                title: "复制失败",
                icon: "none",
            });
        },
    });
}
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

/* 整体页面容器 */
.page-container {
    background: #f7f8fa;
    padding-bottom: 40rpx; // 给底部留出空间
}

/* 背景装饰 (无变化) */
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
    background: rgba(127, 69, 21, 0.05);

    &.circle-1 {
        width: 220rpx;
        height: 220rpx;
        top: 8%;
        right: -60rpx;
        animation: float 6s ease-in-out infinite;
    }

    &.circle-2 {
        width: 150rpx;
        height: 150rpx;
        bottom: 15%;
        left: -40rpx;
        animation: float 8s ease-in-out infinite reverse;
    }

    &.circle-3 {
        width: 100rpx;
        height: 100rpx;
        top: 40%;
        left: 20%;
        animation: float 4s ease-in-out infinite;
    }
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-20rpx);
    }
}

/* 页面头部 (MODIFIED: 减小了边距) */
.page-header {
    padding: 24rpx 30rpx 20rpx;
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
    margin-bottom: 8rpx;
}

.page-subtitle {
    display: block;
    font-size: 24rpx;
    color: #7f8c8d;
}

/* 主体内容 */
.content-wrapper {
    padding: 0 24rpx;
    position: relative;
    z-index: 1;
}

/* 筛选表单 (无大变化) */
.filters-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24rpx;
}

.form-item {
    display: flex;
    flex-direction: column;
    gap: 8rpx;

    .label {
        font-size: 24rpx;
        color: var(--text-secondary);
    }

    .input,
    .picker-value {
        height: 76rpx;
        border: 2rpx solid #e9ecef;
        border-radius: 12rpx;
        padding: 0 20rpx;
        font-size: 26rpx;
        display: flex;
        align-items: center;
        background: #fff;
    }

    .picker-value {
        color: var(--text-placeholder);

        &.is-selected {
            color: var(--text-primary);
        }
    }
}

/* MODIFIED: 卡片内操作区 */
.card-actions-wrapper {
    display: flex;
    gap: 20rpx;
    margin-top: 30rpx;
    padding-top: 24rpx;
    border-top: 1rpx solid #f1f3f5;
}

/* 按钮组 (无大变化) */
.action-btn {
    flex: 1;
    height: 72rpx;
    border-radius: 9999rpx;
    font-size: 26rpx;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12rpx;
    border: none;
    transition: all 0.3s;

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
    color: #fff;
    box-shadow: 0 8rpx 24rpx rgba(127, 69, 21, 0.25);
}

.secondary-btn {
    background: #f1f3f5;
    color: var(--text-primary);
    border: 2rpx solid #f1f3f5;

    &:active {
        background: #e9ecef;
        border-color: #dee2e6;
    }
}

/* MODIFIED: 查询结果区 */
.results-container {
    margin-top: 30rpx;
}

.results-summary {
    font-size: 24rpx;
    color: var(--text-secondary);
    text-align: center;
    margin-bottom: 20rpx;
}

// 定制 uni-collapse 样式
.results-collapse {
    ::v-deep .uni-collapse-item__title-box {
        background-color: #fff !important;
        border-radius: 16rpx;
        box-shadow: 0 6rpx 20rpx rgba(0, 0, 0, 0.05);
    }

    ::v-deep .uni-collapse-item__content {
        background-color: transparent !important;
    }

    ::v-deep .uni-collapse-item {
        margin-bottom: 20rpx;
    }
}

/* 课程列表 */
.course-list {
    display: flex;
    flex-direction: column;
    gap: 16rpx;
    padding: 16rpx 0; // 给手风琴内容一些呼吸空间
}

/* MODIFIED: 课程项卡片 - 全新紧凑设计 */
.course-item {
    padding: 20rpx;
    border: 1rpx solid #f1f3f5;
    border-radius: 16rpx;
    background: #fff;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.03);
    display: flex;
    flex-direction: column;
    gap: 16rpx;
}

.course-header {
    display: flex;
    justify-content: space-between;
    gap: 12rpx;
}

.course-title-group {
    display: flex;
    flex-direction: column;
    gap: 4rpx;
    flex: 1;
    min-width: 0;
}

.course-name {
    font-weight: 700;
    font-size: 30rpx;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 8rpx;

    &.clickable {
        cursor: pointer;
        transition: all 0.2s ease;

        &:hover {
            color: #7f4515;
        }

        &:active {
            transform: scale(0.98);
        }
    }
}

.course-meta {
    font-size: 22rpx;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 8rpx;

    &.clickable {
        cursor: pointer;
        transition: all 0.2s ease;

        &:hover {
            color: #495057;
        }

        &:active {
            transform: scale(0.98);
        }
    }
}

.meta-tags {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 8rpx;
    flex-shrink: 0;
}

.pill {
    padding: 6rpx 12rpx;
    border-radius: 8rpx;
    font-size: 22rpx;
    font-weight: 600;
    line-height: 1;
    border: 2rpx solid transparent;
}

.pill-ghost {
    background: #f8f9fa;
    color: #495057;
    border-color: #e9ecef;
}

.pill-success {
    background: #e6fcf5;
    color: #2b8a3e;
    border-color: #c3fae8;
}

.pill-danger {
    background: #fff5f5;
    color: #c92a2a;
    border-color: #ffe3e3;
}

.course-details {
    display: flex;
    flex-wrap: wrap;
    gap: 12rpx;
    padding-top: 12rpx;
    border-top: 1rpx solid #f1f3f5;
}

.detail-item {
    display: flex;
    align-items: center;
    gap: 8rpx;
    font-size: 24rpx;
    color: #495057;
    background-color: #f8f9fa;
    padding: 6rpx 12rpx;
    border-radius: 8rpx;
    transition: all 0.2s ease;

    &.full-width {
        flex-basis: 100%;
    }

    &.clickable {
        cursor: pointer;
        user-select: text; // 允许文本被选中
        position: relative;

        &:hover {
            background-color: #e9ecef;
            transform: translateY(-1rpx);
            box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
        }

        &:active {
            transform: translateY(0);
            background-color: #dee2e6;
        }
    }
}

.copy-icon {
    margin-left: 8rpx;
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
}

.detail-item.clickable:hover .copy-icon {
    opacity: 1;
}

/* 添加点击反馈动画 */
.detail-item.clickable:active {
    animation: clickPulse 0.15s ease-out;
}

@keyframes clickPulse {
    0% {
        transform: scale(1);
    }

    50% {
        transform: scale(0.98);
    }

    100% {
        transform: scale(1);
    }
}

.conflict-box {
    margin-top: 4rpx;
    padding: 12rpx;
    border-radius: 10rpx;
    border: 2rpx dashed #ffc9c9;
    background: #fff5f5;
    display: flex;
    align-items: flex-start;
    gap: 8rpx;
}

.conflict-text {
    font-size: 24rpx;
    color: #c92a2a;
    line-height: 1.5;
}

/* 其他通用样式 */
.muted-text {
    color: var(--text-secondary);
    font-size: 24rpx;
}

.empty-module {
    padding: 40rpx;
    text-align: center;
}

.card-section {
    .section-desc {
        display: block;
        margin-bottom: 8rpx;
        font-size: 26rpx;
        color: var(--text-primary);
    }
}

/* 错误详情样式 */
.error-details {
    margin-top: 16rpx;
    padding: 16rpx;
    background: #f8f9fa;
    border-radius: 8rpx;
    border-left: 4rpx solid #dc3545;
}

.error-label {
    display: block;
    font-size: 24rpx;
    font-weight: 600;
    color: #dc3545;
    margin-bottom: 8rpx;
}

.error-message {
    display: block;
    font-size: 24rpx;
    color: #495057;
    line-height: 1.5;
    word-break: break-all;
    white-space: pre-wrap;
}

/* 使用提示弹窗样式 */
/* 覆盖 tip-modal-overlay，确保严格铺满并栅格居中 */
.tip-modal-overlay {
    position: fixed;
    inset: 0;
    /* 等价于 top/right/bottom/left: 0，更稳 */
    box-sizing: border-box;
    /* 含 padding 也不会影响居中 */
    padding: 40rpx env(safe-area-inset-right) 40rpx env(safe-area-inset-left);
    display: grid;
    /* 栅格居中，不受子元素尺寸波动影响 */
    place-items: center;
    z-index: 9999;
    background: rgba(0, 0, 0, 0);
    animation: fadeIn 0.3s ease-out forwards;
}

/* 弹窗本体：移除最终位置的位移，只保留缩放淡入；并限制最大高，避免撑开导致看着偏移 */
.tip-modal {
    background: #fff;
    border-radius: 20rpx;
    width: 100%;
    max-width: 600rpx;
    max-height: 80vh;
    /* 高度保护，避免高度过大影响居中 */
    overflow: auto;
    /* 内容多时内部滚动 */
    box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.2);
    transform: scale(0.92);
    /* 初始仅缩放，不做 Y 位移 */
    opacity: 0;
    animation: slideIn 0.28s ease-out 0.08s forwards;
}


.tip-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 30rpx 30rpx 20rpx;
    border-bottom: 1rpx solid #f1f3f5;
}

.tip-title {
    font-size: 32rpx;
    font-weight: 700;
    color: var(--text-primary);
}

.tip-close {
    width: 60rpx;
    height: 60rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: #f8f9fa;
    cursor: pointer;
    transition: all 0.2s ease;

    &:active {
        background: #e9ecef;
        transform: scale(0.95);
    }
}

.tip-content {
    padding: 30rpx;
    min-height: 200rpx;
    display: flex;
    align-items: center;
    justify-content: center;
}

.tip-text {
    font-size: 28rpx;
    color: var(--text-primary);
    line-height: 1.6;
    text-align: center;
}

.tip-footer {
    padding: 20rpx 30rpx 30rpx;
    border-top: 1rpx solid #f1f3f5;
}

.tip-btn {
    width: 100%;
    height: 80rpx;
    background: linear-gradient(135deg, #7f4515, #8c5527);
    color: #fff;
    border: none;
    border-radius: 12rpx;
    font-size: 28rpx;
    font-weight: 600;
    transition: all 0.3s ease;
    transform: translateY(0);

    &::after {
        border: none;
    }

    &:active {
        transform: translateY(2rpx) scale(0.98);
        box-shadow: 0 4rpx 12rpx rgba(127, 69, 21, 0.3);
    }
}

/* 弹窗动画关键帧 */
@keyframes fadeIn {
    from {
        background: rgba(0, 0, 0, 0);
    }

    to {
        background: rgba(0, 0, 0, 0.5);
    }
}

@keyframes slideIn {
    from {
        transform: scale(0.92);
        opacity: 0;
    }

    to {
        transform: scale(1);
        opacity: 1;
    }
}

.tip-modal-overlay.closing {
    animation: fadeOut 0.2s ease-in forwards;
}

.tip-modal-overlay.closing .tip-modal {
    animation: slideOut 0.2s ease-in forwards;
}

@keyframes slideOut {
    from {
        transform: scale(1) translateY(0);
        opacity: 1;
    }

    to {
        transform: scale(0.8) translateY(40rpx);
        opacity: 0;
    }
}

@keyframes slideOut {
    from {
        transform: scale(1) translateY(0);
        opacity: 1;
    }

    to {
        transform: scale(0.8) translateY(40rpx);
        opacity: 0;
    }
}
</style>