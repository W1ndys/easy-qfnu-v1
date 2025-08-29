<template>
    <ModernCard title="培养方案模块">
        <view class="modules-list">
            <view v-for="(m, idx) in sortedModules" :key="m.module_name" class="module-card" :class="{
                incomplete: isIncomplete(m),
                expanded: expanded[getOriginalIndex(m)],
            }">
                <view class="module-header" @click="toggleModule(getOriginalIndex(m))">
                    <view class="header-info">
                        <view class="header-top">
                            <text class="module-title">{{ m.module_name }}</text>
                            <view class="status-chip" :class="isIncomplete(m)
                                ? 'chip-module-incomplete'
                                : 'chip-module-complete'
                                ">
                                <text>{{ isIncomplete(m) ? "未修满" : "已修满" }}</text>
                            </view>
                        </view>

                        <view class="header-middle">
                            <view class="credits-info">
                                <text class="credits-text">{{ formatNumber(m.completed_credits) }}/{{
                                    formatNumber(m.required_credits)
                                }}
                                    学分</text>
                                <text class="course-count-text">共 {{ (m.courses || []).length }} 门课程</text>
                                <text v-if="isIncomplete(m)" class="shortage-text">差
                                    {{
                                        formatNumber(
                                            Number(m.required_credits) - Number(m.completed_credits)
                                        )
                                    }}
                                    学分</text>
                            </view>

                            <view class="expand-action">
                                <text class="hint-text" v-if="!expanded[getOriginalIndex(m)]">点击展开</text>
                                <text class="hint-text" v-else>点击收起</text>
                                <uni-icons class="chevron-icon" :class="{ expanded: expanded[getOriginalIndex(m)] }"
                                    type="arrowdown" size="20" color="#7F4515" />
                            </view>
                        </view>

                        <view class="progress-container">
                            <view class="progress-bar">
                                <view class="progress-fill" :style="{ width: getProgress(m) + '%' }"
                                    :class="{ danger: isIncomplete(m) }"></view>
                            </view>
                            <text class="progress-text">{{ getProgress(m) }}%</text>
                        </view>
                    </view>
                </view>
                <view class="course-details">
                    <view v-if="m.subtotal" class="module-subtotal">
                        <text class="subtotal-title">模块要求小计</text>
                        <text class="subtotal-credits">要求学分 {{ m.subtotal.total_credits }}</text>
                        <text class="subtotal-hours">要求总学时 {{ m.subtotal.hours?.total || 0 }}</text>

                        <view class="subtotal-divider"></view>

                        <text class="subtotal-title">已修课程小计</text>
                        <view class="subtotal-completed-group">
                            <text class="subtotal-hours">
                                已修总学时 {{ calculateCompletedHours(m).total || 0 }}
                            </text>
                            <template v-for="hourInfo in formatHours(calculateCompletedHours(m))" :key="hourInfo">
                                <text class="subtotal-meta">{{ hourInfo }}</text>
                            </template>
                        </view>
                    </view>

                    <view class="course-sort-hint">
                        <view class="sort-hint-text">
                            <uni-icons type="info" size="16" color="#666" />
                            <text>{{
                                isIncomplete(m)
                                    ? "未修课程已置顶显示，本学期课程优先"
                                    : "已修课程已置顶显示"
                            }}</text>
                        </view>
                    </view>
                    <view class="course-list">
                        <view v-for="c in m.courses || []" :key="(c.course_code || '') + (c.course_name || '')"
                            class="course-item" :class="{ completed: isCourseCompleted(c) }">
                            <view class="course-main">
                                <view class="course-title-section">
                                    <view class="course-name-wrapper">
                                        <text class="course-name">{{ c.course_name }}</text>
                                        <text v-if="isCurrentSemesterCourse(c) && !isCourseCompleted(c)"
                                            class="current-semester-tag">本学期可选</text>
                                    </view>
                                    <text v-if="c.course_code" class="course-code"
                                        @click.stop="copyCourseCode(c.course_code)">代码:
                                        {{ c.course_code
                                        }}</text>
                                </view>
                                <view class="chips">
                                    <text class="chip completion-chip" :class="isCourseCompleted(c) ? 'chip-completed' : 'chip-incomplete'
                                        ">{{ c.completion_status || "未修" }}</text>
                                    <text v-if="c.course_nature" class="chip chip-neutral">{{
                                        c.course_nature
                                    }}</text>
                                    <text v-if="c.course_attribute" class="chip chip-neutral">{{
                                        c.course_attribute
                                    }}</text>
                                </view>
                            </view>
                            <view class="course-meta">
                                <text class="meta">学分 {{ c.credits }}</text>
                                <text class="meta" v-if="c.semester">学期 {{ c.semester }}</text>
                                <text class="meta" v-if="c.hours?.total">总学时 {{ c.hours.total }}</text>
                                <template v-for="hourInfo in formatHours(c.hours)" :key="hourInfo">
                                    <text class="meta">{{ hourInfo }}</text>
                                </template>
                            </view>
                        </view>
                    </view>
                </view>
            </view>
        </view>
    </ModernCard>
</template>

<script setup>
import { ref, computed } from 'vue';
import ModernCard from "../../components/ModernCard/ModernCard.vue";

// 格式化数字
const formatNumber = (n) => {
    const v = Number(n);
    if (isNaN(v)) return "0";
    return v % 1 === 0 ? String(v) : v.toFixed(1);
};

// 计算已修学时
const calculateCompletedHours = (module) => {
    if (!module.courses?.length) return { total: 0 };
    return module.courses.filter(course => !!course.completion_status?.includes("已修")).reduce((acc, course) => {
        if (course.hours && typeof course.hours === "object") {
            for (const [key, value] of Object.entries(course.hours)) {
                acc[key] = (acc[key] || 0) + (Number(value) || 0);
            }
        }
        return acc;
    }, {});
};

// 格式化学时信息
const formatHours = (hours) => {
    if (!hours || typeof hours !== "object") return [];
    const hourTypes = {
        lecture: "讲授",
        practice: "实践",
        seminar: "研讨",
        experiment: "实验",
        design: "设计",
        computer: "上机",
        discussion: "讨论",
        extracurricular: "课外",
        online: "在线",
    };
    return Object.entries(hours)
        .filter(([key, value]) => key !== "total" && Number(value) > 0)
        .map(([key, value]) => `${hourTypes[key] || key}: ${value}`);
};

const props = defineProps({
    modules: {
        type: Array,
        default: () => []
    },
    currentSemester: {
        type: [String, Number],
        default: null
    }
});

const emit = defineEmits(['copy-course-code']);

const expanded = ref([]);

// 初始化展开状态
const initExpanded = () => {
    expanded.value = props.modules.map(() => false);
};

// 监听模块变化，重新初始化展开状态
computed(() => {
    if (props.modules.length !== expanded.value.length) {
        initExpanded();
    }
    return props.modules;
});

const sortedModules = computed(() => {
    return [...props.modules]
        .sort((a, b) => {
            const aIncomplete = isIncomplete(a);
            const bIncomplete = isIncomplete(b);
            if (aIncomplete && !bIncomplete) return -1;
            if (!aIncomplete && bIncomplete) return 1;
            return 0;
        })
        .map((module) => {
            const moduleIncomplete = isIncomplete(module);
            return {
                ...module,
                courses: [...(module.courses || [])].sort((a, b) => {
                    const aCompleted = isCourseCompleted(a);
                    const bCompleted = isCourseCompleted(b);
                    if (moduleIncomplete) {
                        if (!aCompleted && bCompleted) return -1;
                        if (aCompleted && !bCompleted) return 1;
                        if (!aCompleted && !bCompleted) {
                            const aIsCurrent = isCurrentSemesterCourse(a);
                            const bIsCurrent = isCurrentSemesterCourse(b);
                            if (aIsCurrent && !bIsCurrent) return -1;
                            if (!aIsCurrent && bIsCurrent) return 1;
                        }
                    } else {
                        if (aCompleted && !bCompleted) return -1;
                        if (!aCompleted && bCompleted) return 1;
                    }
                    const semesterA = Number(a.semester) || 0;
                    const semesterB = Number(b.semester) || 0;
                    if (semesterA !== semesterB) {
                        return semesterB - semesterA;
                    }
                    return 0;
                }),
            };
        });
});

const toggleModule = (index) => {
    expanded.value[index] = !expanded.value[index];
};

const getOriginalIndex = (module) => {
    return props.modules.findIndex((m) => m.module_name === module.module_name);
};

const copyCourseCode = (code) => {
    emit('copy-course-code', code);
};

const isCourseCompleted = (course) => !!course.completion_status?.includes("已修");

const isCurrentSemesterCourse = (course) => {
    if (!course.semester || !props.currentSemester) return false;
    const courseSemester = Number(course.semester);
    return (
        courseSemester <= props.currentSemester &&
        courseSemester % 2 === props.currentSemester % 2
    );
};

const isIncomplete = (module) => {
    return (
        (Number(module?.completed_credits) || 0) < (Number(module?.required_credits) || 0)
    );
};

const getProgress = (module) => {
    const need = Number(module?.required_credits) || 0;
    const done = Number(module?.completed_credits) || 0;
    if (need <= 0) return 0;
    return Math.min(100, Math.max(0, Math.round((done / need) * 100)));
};

// 初始化展开状态
initExpanded();
</script>

<style lang="scss" scoped>
.modules-list {
    display: flex;
    flex-direction: column;
    gap: 16rpx;
}

/* CSS Grid 动画方案 */
.module-card {
    border: 1rpx solid #e8e8e8;
    border-radius: 16rpx;
    background: #ffffff;

    /* Grid 容器 */
    display: grid;
    /* 定义两行：第一行高度自适应，第二行（课程详情）初始高度为0 */
    grid-template-rows: auto 0fr;
    /* 对行高变化添加过渡动画 */
    transition: grid-template-rows 0.35s ease-in-out;

    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.module-card.expanded {
    /* 展开时，第二行的高度变为 1fr，占据所有可用空间 */
    grid-template-rows: auto 1fr;
    box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.12);
    transform: translateY(-4rpx);
}

.module-card.incomplete {
    border-color: #ffaaa5;
    background: linear-gradient(135deg, #fff7f7 0%, #ffffff 100%);
}

.module-header {
    cursor: pointer;
    padding: 16rpx 14rpx;
    transition: background-color 0.2s ease;
}

.module-header:active {
    background: rgba(127, 69, 21, 0.08);
}

.course-details {
    /* 必须设置为 overflow: hidden，否则内容会在 0fr 时溢出 */
    overflow: hidden;
    background: linear-gradient(180deg, #fafbfc 0%, #f5f6fa 100%);
    border-top: 1rpx solid #e8e8e8;
    min-height: 0;
}

.header-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12rpx;
}

.module-title {
    font-size: 30rpx;
    font-weight: 600;
    flex: 1;
    margin-right: 16rpx;
}

.header-middle {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16rpx;
}

.credits-info {
    display: flex;
    flex-direction: column;
    gap: 8rpx;
}

.credits-text {
    font-size: 28rpx;
    color: var(--text-secondary);
    font-weight: 500;
}

.course-count-text {
    font-size: 22rpx;
    color: #595959;
    font-weight: 400;
}

.shortage-text {
    font-size: 24rpx;
    color: #e74c3c;
    font-weight: 500;
}

.expand-action {
    display: flex;
    align-items: center;
    gap: 6rpx;
    padding: 6rpx 10rpx;
    background: rgba(127, 69, 21, 0.08);
    border-radius: 16rpx;
}

.hint-text {
    font-size: 22rpx;
    color: var(--text-light);
}

.chevron-icon {
    transition: transform 0.35s ease;
}

.chevron-icon.expanded {
    transform: rotate(180deg);
}

.progress-container {
    display: flex;
    align-items: center;
    gap: 12rpx;
}

.progress-bar {
    flex: 1;
    height: 20rpx;
    background: #f5f5f5;
    border-radius: 10rpx;
    overflow: hidden;
    box-shadow: inset 0 2rpx 4rpx rgba(0, 0, 0, 0.1);
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #52c41a 0%, #73d13d 100%);
    border-radius: 10rpx;
    transition: width 0.6s ease;
}

.progress-fill.danger {
    background: linear-gradient(90deg, #ff4d4f 0%, #ff7875 100%);
}

.progress-text {
    font-size: 24rpx;
    font-weight: 500;
    min-width: 60rpx;
    text-align: right;
}

.status-chip {
    padding: 6rpx 12rpx;
    border-radius: 16rpx;
    font-size: 22rpx;
    font-weight: 500;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.chip-module-complete,
.chip-completed {
    background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
    color: #389e0d;
    border: 1rpx solid #95de64;
}

.chip-module-incomplete,
.chip-incomplete {
    background: linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%);
    color: #cf1322;
    border: 1rpx solid #ff7875;
}

.chip-neutral {
    background: linear-gradient(135deg, #f0f0f0 0%, #d9d9d9 100%);
    color: #595959;
    border: 1rpx solid #bfbfbf;
}

.course-sort-hint {
    padding: 8rpx 12rpx 4rpx;
    text-align: center;
}

.sort-hint-text {
    font-size: 20rpx;
    color: #8c8c8c;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6rpx;

    text {
        font-size: 20rpx;
        color: #8c8c8c;
    }
}

.course-list {
    display: flex;
    flex-direction: column;
    gap: 8rpx;
    padding: 12rpx;
}

.course-item {
    border: 1rpx solid #e8e8e8;
    border-radius: 10rpx;
    padding: 8rpx 12rpx;
    background: #ffffff;
    display: flex;
    flex-direction: column;
    gap: 8rpx;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
    transition: all 0.3s ease;
    position: relative;
}

.course-item.completed {
    border-color: #87d068;
    background: linear-gradient(135deg, #f6ffed 0%, #ffffff 100%);
}

.course-item.completed::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 6rpx;
    height: 100%;
    background: linear-gradient(180deg, #52c41a 0%, #73d13d 100%);
    border-radius: 12rpx 0 0 12rpx;
    transition: opacity 0.3s ease;
}

.course-item:not(.completed) {
    border-color: #ffb3ba;
    background: linear-gradient(135deg, #fff2f0 0%, #ffffff 100%);
}

.course-item:not(.completed)::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 6rpx;
    height: 100%;
    background: linear-gradient(180deg, #ff4d4f 0%, #ff7875 100%);
    border-radius: 12rpx 0 0 12rpx;
    transition: opacity 0.3s ease;
}

.course-main {
    display: flex;
    flex-direction: column;
    gap: 8rpx;
}

.course-title-section {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 8rpx;
}

.course-name-wrapper {
    display: flex;
    flex-direction: column;
    gap: 4rpx;
    flex: 1;
}

.course-name {
    font-size: 26rpx;
    font-weight: 600;
}

.current-semester-tag {
    font-size: 18rpx;
    color: #1890ff;
    background: #e6f7ff;
    padding: 2rpx 8rpx;
    border-radius: 6rpx;
    border: 1rpx solid #91d5ff;
    font-weight: 600;
    white-space: nowrap;
    align-self: flex-start;
}

.course-code {
    font-size: 20rpx;
    color: #8c8c8c;
    background: #f5f5f5;
    padding: 2rpx 8rpx;
    border-radius: 6rpx;
    align-self: flex-start;
    cursor: pointer;
}

.chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6rpx;
}

.chip {
    padding: 3rpx 8rpx;
    border-radius: 10rpx;
    font-size: 18rpx;
}

.course-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 4rpx 8rpx;
    padding-top: 6rpx;
    border-top: 1rpx solid #f5f5f5;
}

.meta {
    font-size: 20rpx;
    color: #595959;
    padding: 2rpx 6rpx;
    background: #f0f2f5;
    border-radius: 6rpx;
    border: 1rpx solid #e8e8e8;
}

.module-subtotal {
    margin: 8rpx 12rpx;
    padding: 10rpx;
    border-bottom: 1rpx solid #e8e8e8;
    background: linear-gradient(135deg, #f0f8ff 0%, #ffffff 100%);
    border-radius: 10rpx;
    display: flex;
    flex-wrap: wrap;
    gap: 8rpx;
    font-size: 22rpx;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.subtotal-title {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 24rpx;
    width: 100%;
    text-align: center;
    margin-bottom: 2rpx;
}

.subtotal-divider {
    width: 100%;
    height: 1rpx;
    background-color: #e8e8e8;
    margin: 6rpx 0;
}

.subtotal-credits,
.subtotal-hours {
    color: var(--text-secondary);
    padding: 4rpx 8rpx;
    background: rgba(127, 69, 21, 0.05);
    border-radius: 6rpx;
    text-align: center;
    min-width: 80rpx;
    flex: 1;
}

.subtotal-completed-group {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: 8rpx;
}

.subtotal-completed-group .subtotal-hours {
    flex: initial;
}

.subtotal-meta {
    font-size: 20rpx;
    color: var(--text-secondary);
    padding: 2rpx 4rpx;
    background: #f8f9fa;
    border: 1rpx solid #e8e8e8;
    border-radius: 6rpx;
}

.sort-hint-text {
    font-size: 20rpx;
    color: #8c8c8c;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6rpx;

    text {
        font-size: 20rpx;
        color: #8c8c8c;
    }
}
</style>
