<template>
    <ModernCard title="筛选与操作" style="padding: 20rpx;">
        <view class="filters-grid">
            <view class="form-item">
                <text class="label">课程名/编号</text>
                <input class="input" :value="courseIdOrName" @input="onCourseInput" placeholder="如 大学英语 或 g1234" />
            </view>
            <view class="form-item">
                <text class="label">教师名</text>
                <input class="input" :value="teacherName" @input="onTeacherInput" placeholder="如 张三" />
            </view>
            <view class="form-item">
                <text class="label">星期</text>
                <picker mode="selector" :range="weekOptions" @change="onWeekChangeInternal">
                    <view class="picker-value" :class="{ 'is-selected': query.week_day }">
                        {{ query.week_day ? `星期${query.week_day}` : "选择星期（可选）" }}
                    </view>
                </picker>
            </view>
            <view class="form-item">
                <text class="label">节次</text>
                <picker mode="selector" :range="classPeriodOptionsDisplay" @change="onClassPeriodChangeInternal">
                    <view class="picker-value" :class="{ 'is-selected': query.class_period }">
                        {{ query.class_period ? `${query.class_period}节` : "选择节次（可选）" }}
                    </view>
                </picker>
            </view>
        </view>
        <view class="card-actions-wrapper">
            <button class="action-btn secondary-btn" @click="$emit('secondary')">
                <uni-icons type="refresh" size="20" color="#495057" />
                <text>重置</text>
            </button>
            <button class="action-btn primary-btn" @click="$emit('primary')">
                <uni-icons type="paperplane" size="20" color="#fff" />
                <text>查询</text>
            </button>
        </view>
    </ModernCard>
    <view />
</template>

<script setup>
import { defineProps, defineEmits, computed } from "vue";
import ModernCard from "../../components/ModernCard/ModernCard.vue";

const props = defineProps({
    query: { type: Object, required: true },
    weekOptions: { type: Array, default: () => [] },
    classPeriodOptionsDisplay: { type: Array, default: () => [] },
});
const emit = defineEmits([
    "update:course_id_or_name",
    "update:teacher_name",
    "weekChange",
    "classPeriodChange",
    "primary",
    "secondary",
]);

const courseIdOrName = computed(() => props.query.course_id_or_name || "");
const teacherName = computed(() => props.query.teacher_name || "");

function onCourseInput(e) {
    emit("update:course_id_or_name", e.detail.value || "");
}
function onTeacherInput(e) {
    emit("update:teacher_name", e.detail.value || "");
}
function onWeekChangeInternal(e) {
    emit("weekChange", e);
}
function onClassPeriodChangeInternal(e) {
    emit("classPeriodChange", e);
}
</script>

<style lang="scss" scoped>
/* 复用父页面样式类名，保持外观一致 */
.filters-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24rpx;
}

.form-item {
    display: flex;
    flex-direction: column;
    gap: 8rpx;
}

.form-item .label {
    font-size: 24rpx;
    color: var(--text-secondary);
}

.form-item .input,
.form-item .picker-value {
    height: 76rpx;
    border: 2rpx solid #e9ecef;
    border-radius: 12rpx;
    padding: 0 20rpx;
    font-size: 26rpx;
    display: flex;
    align-items: center;
    background: #fff;
}

.form-item .picker-value {
    color: var(--text-placeholder);
}

.form-item .picker-value.is-selected {
    color: var(--text-primary);
}

.card-actions-wrapper {
    display: flex;
    gap: 20rpx;
    margin-top: 30rpx;
    padding-top: 24rpx;
    border-top: 1rpx solid #f1f3f5;
}

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
}

.action-btn::after {
    border: none;
}

.action-btn:active {
    transform: scale(0.95);
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
}

.secondary-btn:active {
    background: #e9ecef;
    border-color: #dee2e6;
}
</style>
