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
                    }" v-model="form.course" placeholder="请输入课程名称或课程代码（至少3个字符）" @confirm="handleSearch" @input="validateCourse"
                        @focus="onCourseFocus" @blur="onCourseBlur" />
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
                    }" v-model="form.teacher" placeholder="不填则查询所有老师（至少2个字符）" @confirm="handleSearch" @input="validateTeacher"
                        @focus="onTeacherFocus" @blur="onTeacherBlur" />
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

<script src="./SearchForm.js"></script>
<style lang="scss" scoped>
@import "./SearchForm.scss";
</style>
