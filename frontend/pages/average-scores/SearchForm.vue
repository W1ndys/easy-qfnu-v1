<template>
    <view class="search-card modern-card">
        <view class="card-header">
            <view class="header-icon">
                <uni-icons type="search" size="24" color="#7f4515"></uni-icons>
            </view>
            <view class="header-text">
                <text class="card-title">课程信息查询</text>
                <text class="card-subtitle">输入课程信息开始查询</text>
            </view>
        </view>

        <view class="form-content">
            <view class="form-group">
                <view class="input-label">
                    <uni-icons type="book" size="20" color="#495057"></uni-icons>
                    <text>课程名称/代码</text>
                </view>
                <view class="input-wrapper">
                    <input class="modern-input" :class="{
                        'input-error': courseError,
                        'input-focus': courseFocused,
                    }" v-model="form.course" placeholder="请输入课程名称或课程代码（至少3个字符）" @confirm="handleSearch"
                        @input="validateCourse" @focus="onCourseFocus" @blur="onCourseBlur" />
                    <view class="input-line" :class="{ active: courseFocused }"></view>
                </view>
                <text class="input-hint" :class="{ 'hint-error': courseError }">
                    {{ courseHint }}
                </text>
            </view>

            <view class="form-group">
                <view class="input-label">
                    <uni-icons type="person" size="20" color="#495057"></uni-icons>
                    <text>教师姓名（选填）</text>
                </view>
                <view class="input-wrapper">
                    <input class="modern-input" :class="{
                        'input-error': teacherError,
                        'input-focus': teacherFocused,
                    }" v-model="form.teacher" placeholder="不填则查询所有老师（至少2个字符）" @confirm="handleSearch"
                        @input="validateTeacher" @focus="onTeacherFocus" @blur="onTeacherBlur" />
                    <view class="input-line" :class="{ active: teacherFocused }"></view>
                </view>
                <text class="input-hint" :class="{ 'hint-error': teacherError }" v-if="form.teacher.trim()">
                    {{ teacherHint }}
                </text>
            </view>

            <view class="button-group">
                <button class="action-btn primary-btn" @click="handleSearch" :loading="loading" :disabled="!canSearch">
                    <uni-icons type="search" size="20" color="#ffffff" v-if="!loading"></uni-icons>
                    <text>{{ loading ? "查询中..." : "开始查询" }}</text>
                </button>
                <button class="action-btn secondary-btn" @click="handleReset">
                    <uni-icons type="refresh" size="20" color="#495057"></uni-icons>
                    <text>重置</text>
                </button>
            </view>
        </view>
    </view>
</template>

<script setup>
import { ref, reactive, computed } from "vue";

defineProps({
    loading: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['search', 'reset']);

// 状态
const form = reactive({ course: "", teacher: "" });
const courseError = ref(false);
const teacherError = ref(false);
const courseFocused = ref(false);
const teacherFocused = ref(false);

// 计算属性
const courseHint = computed(() => {
    const length = form.course.trim().length;
    if (length === 0) return "请输入课程名称或代码";
    if (length < 3) return `至少需要3个字符，当前${length}个字符`;
    return `已输入${length}个字符`;
});

const teacherHint = computed(() => {
    const length = form.teacher.trim().length;
    if (length === 0) return "";
    if (length < 2) return `至少需要2个字符，当前${length}个字符`;
    return `已输入${length}个字符`;
});

const canSearch = computed(() => {
    const courseLength = form.course.trim().length;
    const teacherLength = form.teacher.trim().length;
    return courseLength >= 3 && (teacherLength === 0 || teacherLength >= 2);
});

// 方法
function onCourseFocus() {
    courseFocused.value = true;
}

function onCourseBlur() {
    courseFocused.value = false;
}

function onTeacherFocus() {
    teacherFocused.value = true;
}

function onTeacherBlur() {
    teacherFocused.value = false;
}

function validateCourse() {
    const length = form.course.trim().length;
    courseError.value = length > 0 && length < 3;
}

function validateTeacher() {
    const length = form.teacher.trim().length;
    teacherError.value = length > 0 && length < 2;
}

function handleSearch() {
    if (!form.course.trim()) {
        uni.showToast({ title: "请输入课程名称或代码", icon: "none" });
        return;
    }
    if (form.course.trim().length < 3) {
        uni.showToast({ title: "课程名称至少需要3个字符", icon: "none" });
        return;
    }
    if (form.teacher.trim() && form.teacher.trim().length < 2) {
        uni.showToast({ title: "教师姓名至少需要2个字符", icon: "none" });
        return;
    }

    const params = { course: form.course.trim() };
    if (form.teacher.trim()) params.teacher = form.teacher.trim();

    emit('search', params);
}

function handleReset() {
    form.course = "";
    form.teacher = "";
    courseError.value = false;
    teacherError.value = false;
    emit('reset');
}
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

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

.modern-input {
    width: 100%;
    height: 88rpx;
    border: 2rpx solid #e9ecef;
    border-radius: var(--radius-small);
    padding: 0 24rpx;
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
        box-shadow: 0 4rpx 12rpx rgba(155, 4, 0, 0.4);
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
