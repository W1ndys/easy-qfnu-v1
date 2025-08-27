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
                        <text class="sort-hint-text">
                            <uni-icons type="info" size="16" color="#666" />
                            {{
                                isIncomplete(m)
                                    ? "未修课程已置顶显示，本学期课程优先"
                                    : "已修课程已置顶显示"
                            }}
                        </text>
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
import { formatNumber, formatHours, calculateCompletedHours } from './utils.js';
import ModernCard from "../../components/ModernCard/ModernCard.vue";

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
@import './ModuleList.scss';
</style>
