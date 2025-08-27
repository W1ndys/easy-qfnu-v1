<template>
    <view>
        <EmptyState v-if="!hasData" icon-type="info-filled" title="暂无结果" description="请先输入课程名/编号或教师名进行查询"
            :show-retry="false" style="margin-top: -120rpx;" />
        <view v-else class="results-container">
            <view class="results-summary">
                <text>查询到 {{ totalCount }} 门相关课程，已按模块分组</text>
            </view>
            <uni-collapse :modelValue="activeNames" @update:modelValue="onActiveChange" class="results-collapse">
                <uni-collapse-item v-for="m in data.modules" :key="m.module" :name="m.module"
                    :title="`${m.module_name} (${m.count || 0})`">
                    <view v-if="m.courses && m.courses.length" class="course-list">
                        <view class="course-item" v-for="c in m.courses"
                            :key="`${m.module}-${c.course_id}-${c.group_name}`">
                            <view class="course-header">
                                <view class="course-title-group">
                                    <view class="course-name clickable" @click="emitCopy(c.course_name, '课程名称')">
                                        <text>{{ c.course_name }}</text>
                                        <uni-icons type="copy" size="14" color="#868e96" class="copy-icon" />
                                    </view>
                                    <view class="course-meta clickable"
                                        @click="emitCopy(`${c.course_id} / ${c.group_name}`, '课程信息')">
                                        <text>{{ c.course_id }} / {{ c.group_name }}</text>
                                        <uni-icons type="copy" size="14" color="#868e96" class="copy-icon" />
                                    </view>
                                </view>
                                <view class="meta-tags">
                                    <text class="pill pill-ghost" v-if="c.credits">{{ c.credits }} 学分</text>
                                    <text class="pill" :class="c.remain_count > 0 ? 'pill-success' : 'pill-danger'">
                                        余量 {{ c.remain_count ?? "未知" }}
                                    </text>
                                </view>
                            </view>
                            <view class="course-details">
                                <view class="detail-item clickable" @click="emitCopy(c.teacher_name, '教师姓名')">
                                    <uni-icons type="person" size="16" color="#868e96" />
                                    <text>{{ c.teacher_name }}</text>
                                    <uni-icons type="copy" size="14" color="#868e96" class="copy-icon" />
                                </view>
                                <view class="detail-item clickable"
                                    @click="emitCopy(`${c.location} @ ${c.campus_name}`, '上课地点')">
                                    <uni-icons type="location" size="16" color="#868e96" />
                                    <text>{{ c.location }} @ {{ c.campus_name }}</text>
                                    <uni-icons type="copy" size="14" color="#868e96" class="copy-icon" />
                                </view>
                                <view class="detail-item full-width clickable" @click="emitCopy(c.time_text, '上课时间')">
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
    <view />
</template>

<script setup>
import { defineProps, defineEmits } from "vue";
import EmptyState from "../../components/EmptyState/EmptyState.vue";

const props = defineProps({
    data: { type: Object, required: true },
    hasData: { type: Boolean, default: false },
    totalCount: { type: Number, default: 0 },
    activeNames: { type: Array, default: () => [] },
});
const emit = defineEmits(["update:activeNames", "copy"]);

function onActiveChange(val) {
    emit("update:activeNames", val || []);
}
function emitCopy(text, label) {
    emit("copy", text, label);
}
</script>

<style lang="scss" scoped>
.results-container {
    margin-top: 30rpx;
}

.results-summary {
    font-size: 24rpx;
    color: var(--text-secondary);
    text-align: center;
    margin-bottom: 10rpx;
}

.results-collapse ::v-deep .uni-collapse-item__title-box {
    background-color: #fff !important;
    border-radius: 16rpx;
    box-shadow: 0 6rpx 20rpx rgba(0, 0, 0, 0.05);
}

.results-collapse ::v-deep .uni-collapse-item__content {
    background-color: transparent !important;
}

.results-collapse ::v-deep .uni-collapse-item {
    margin-bottom: 20rpx;
}

.course-list {
    display: flex;
    flex-direction: column;
    gap: 16rpx;
    padding: 16rpx 0;
}

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
}

.course-name.clickable {
    cursor: pointer;
    transition: all 0.2s ease;
}

.course-name.clickable:active {
    transform: scale(0.98);
}

.course-meta {
    font-size: 22rpx;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 8rpx;
}

.course-meta.clickable {
    cursor: pointer;
    transition: all 0.2s ease;
}

.course-meta.clickable:active {
    transform: scale(0.98);
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
}

.detail-item.full-width {
    flex-basis: 100%;
}

.detail-item.clickable {
    cursor: pointer;
    user-select: text;
    position: relative;
}

.detail-item.clickable:active {
    transform: translateY(0);
    background-color: #dee2e6;
}

.copy-icon {
    margin-left: 8rpx;
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
}

.detail-item.clickable:hover .copy-icon {
    opacity: 1;
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

.muted-text {
    color: var(--text-secondary);
    font-size: 24rpx;
}

.empty-module {
    padding: 40rpx;
    text-align: center;
}
</style>
