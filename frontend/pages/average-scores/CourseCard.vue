<template>
    <view class="course-card modern-card">
        <view class="course-header">
            <view class="course-info">
                <view class="course-icon">
                    <uni-icons type="book" size="20" color="#7f4515"></uni-icons>
                </view>
                <text class="course-name">{{ courseName }}</text>
            </view>
        </view>

        <view class="course-content">
            <view class="teacher-section" v-for="(teacherName, teacherIndex) in Object.keys(teachers)"
                :key="teacherName">
                <view class="teacher-header">
                    <view class="teacher-info">
                        <view class="teacher-avatar">
                            <uni-icons type="person" size="16" color="#7f4515"></uni-icons>
                        </view>
                        <text class="teacher-name">{{ teacherName }}</text>
                    </view>
                </view>

                <view class="semester-list">
                    <view class="semester-item" v-for="(data, semester) in teachers[teacherName]" :key="semester">
                        <view class="semester-info">
                            <text class="semester-name">{{ semester }}</text>
                            <text class="update-time" v-if="data.update_time">
                                {{ formatTime(data.update_time) }}
                            </text>
                        </view>
                        <view class="score-info">
                            <view class="score-item">
                                <text class="score-label">平均分</text>
                                <text class="score-value primary">{{ data.average_score.toFixed(2) }}</text>
                            </view>
                            <view class="score-item">
                                <text class="score-label">人数</text>
                                <text class="score-value secondary">{{ data.student_count }}</text>
                            </view>
                        </view>
                    </view>
                </view>
            </view>
        </view>
    </view>
</template>

<script setup>
defineProps({
    courseName: {
        type: String,
        required: true
    },
    teachers: {
        type: Object,
        required: true
    }
});

/**
 * 格式化时间字符串
 * @param {string} timeStr - 时间字符串
 * @returns {string} 格式化后的时间
 */
function formatTime(timeStr) {
    if (!timeStr) return "";
    return timeStr.replace("T", " ").split(".")[0];
}
</script>

<style lang="scss" scoped>
@import "../../styles/common.scss";

// 课程卡片
.course-card {
    padding: 0;
    overflow: hidden;
    margin-bottom: 24rpx;
}

.course-header {
    background: linear-gradient(135deg, #7f4515, #8c5527);
    padding: 24rpx 30rpx;
}

.course-info {
    display: flex;
    align-items: center;
    gap: 16rpx;
}

.course-icon {
    width: 44rpx;
    height: 44rpx;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.course-name {
    font-size: 28rpx;
    font-weight: 600;
    color: #ffffff;
    flex: 1;
}

.course-content {
    padding: 20rpx 30rpx 30rpx;
}

// 教师区域
.teacher-section {
    margin-bottom: 24rpx;

    &:last-child {
        margin-bottom: 0;
    }
}

.teacher-header {
    margin-bottom: 16rpx;
}

.teacher-info {
    display: flex;
    align-items: center;
    gap: 12rpx;
}

.teacher-avatar {
    width: 36rpx;
    height: 36rpx;
    background: rgba(127, 69, 21, 0.1);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.teacher-name {
    font-size: 24rpx;
    font-weight: 500;
    color: var(--text-primary);
}

// 学期列表
.semester-list {
    display: flex;
    flex-direction: column;
    gap: 12rpx;
}

.semester-item {
    background: #f8f9fa;
    border-radius: var(--radius-small);
    padding: 16rpx 20rpx;
    border: 1rpx solid #e9ecef;
    transition: all 0.2s ease;

    &:hover {
        background: #ffffff;
        border-color: rgba(127, 69, 21, 0.2);
    }
}

.semester-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12rpx;
}

.semester-name {
    background: linear-gradient(135deg, #7f4515, #8c5527);
    color: #ffffff;
    padding: 4rpx 12rpx;
    border-radius: 12rpx;
    font-size: 20rpx;
    font-weight: 500;
}

.update-time {
    font-size: 18rpx;
    color: var(--text-light);
}

// 分数信息
.score-info {
    display: flex;
    gap: 24rpx;
}

.score-item {
    flex: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.score-label {
    font-size: 20rpx;
    color: var(--text-secondary);
    font-weight: 400;
}

.score-value {
    font-size: 22rpx;
    font-weight: 600;

    &.primary {
        color: #7f4515;
    }

    &.secondary {
        color: #6c757d;
    }
}

// 响应式适配
@media (max-width: 600rpx) {
    .score-info {
        flex-direction: column;
        gap: 8rpx;
    }

    .course-card {
        margin-bottom: 20rpx;
    }

    .course-header {
        padding: 20rpx 24rpx;
    }

    .course-content {
        padding: 16rpx 24rpx 24rpx;
    }
}
</style>
