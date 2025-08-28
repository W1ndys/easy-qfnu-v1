<template>
    <view class="course-card" :class="{ 'course-card--empty': isEmpty }">
        <view v-if="!isEmpty" class="course-content">
            <!-- 课程名称和学分 -->
            <view class="course-header">
                <text class="course-name">{{ course.course_name }}</text>
                <text class="course-credits">{{ course.course_credits }}学分</text>
            </view>

            <!-- 课程属性 -->
            <view class="course-property">
                <text class="property-tag" :class="getPropertyClass(course.course_property)">
                    {{ course.course_property }}
                </text>
            </view>

            <!-- 时间和节次 -->
            <view class="course-time">
                <uni-icons type="clock" size="16" color="#7f4515" />
                <text class="time-text">{{ course.period }}节</text>
            </view>

            <!-- 教室 -->
            <view class="course-location">
                <uni-icons type="location" size="16" color="#7f4515" />
                <text class="location-text">{{ course.classroom }}</text>
            </view>

            <!-- 班级信息 -->
            <view class="course-class" v-if="course.class_name">
                <text class="class-text">{{ course.class_name }}</text>
            </view>
        </view>

        <!-- 空课程状态 -->
        <view v-else class="empty-content">
            <text class="empty-text">无课程</text>
        </view>
    </view>
</template>

<script setup>
const props = defineProps({
    course: {
        type: Object,
        default: null
    },
    isEmpty: {
        type: Boolean,
        default: false
    }
});

// 获取课程属性样式类
function getPropertyClass(property) {
    switch (property) {
        case '必修':
            return 'property-required';
        case '选修':
            return 'property-elective';
        case '实践':
            return 'property-practice';
        default:
            return 'property-default';
    }
}
</script>

<style lang="scss" scoped>
.course-card {
    background: linear-gradient(135deg, #ffffff 0%, #fefefe 100%);
    border-radius: 20rpx;
    padding: 24rpx;
    margin-bottom: 16rpx;
    box-shadow: 0 8rpx 24rpx rgba(127, 69, 21, 0.08);
    border: 1rpx solid rgba(127, 69, 21, 0.1);
    transition: all 0.3s ease;

    &:active {
        transform: scale(0.98);
    }

    &--empty {
        background: linear-gradient(135deg, #f8f9fa 0%, #f1f3f4 100%);
        border: 1rpx dashed #dee2e6;

        .empty-content {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 80rpx;

            .empty-text {
                color: #9e9e9e;
                font-size: 24rpx;
            }
        }
    }
}

.course-content {
    display: flex;
    flex-direction: column;
    gap: 12rpx;
}

.course-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8rpx;
}

.course-name {
    font-size: 30rpx;
    font-weight: 700;
    color: #2c3e50;
    line-height: 1.4;
    flex: 1;
    margin-right: 16rpx;
}

.course-credits {
    font-size: 22rpx;
    color: #7f4515;
    background: rgba(127, 69, 21, 0.1);
    padding: 4rpx 12rpx;
    border-radius: 20rpx;
    white-space: nowrap;
}

.course-property {
    margin-bottom: 4rpx;
}

.property-tag {
    font-size: 20rpx;
    padding: 4rpx 12rpx;
    border-radius: 12rpx;
    font-weight: 600;

    &.property-required {
        background: linear-gradient(135deg, #ff6b6b 0%, #ff5252 100%);
        color: #fff;
    }

    &.property-elective {
        background: linear-gradient(135deg, #4ecdc4 0%, #26a69a 100%);
        color: #fff;
    }

    &.property-practice {
        background: linear-gradient(135deg, #ffe066 0%, #ffd54f 100%);
        color: #5d4037;
    }

    &.property-default {
        background: linear-gradient(135deg, #90a4ae 0%, #78909c 100%);
        color: #fff;
    }
}

.course-time,
.course-location {
    display: flex;
    align-items: center;
    gap: 8rpx;
}

.time-text,
.location-text {
    font-size: 24rpx;
    color: #495057;
    font-weight: 500;
}

.course-class {
    margin-top: 4rpx;
    padding: 8rpx 0;
    border-top: 1rpx solid #f1f3f4;
}

.class-text {
    font-size: 22rpx;
    color: #6c757d;
    font-style: italic;
}
</style>
