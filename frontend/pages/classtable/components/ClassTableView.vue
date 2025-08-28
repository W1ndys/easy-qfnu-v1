<template>
    <view class="classtable-view">
        <!-- 课程列表 -->
        <view v-if="courses && courses.length > 0" class="courses-container">
            <!-- 日期标题 -->
            <view class="date-header">
                <text class="date-title">{{ formatDate(selectedDate) }}</text>
                <text class="course-count">共 {{ courses.length }} 节课</text>
            </view>
            
            <!-- 课程卡片列表 -->
            <view class="courses-list">
                <CourseCard 
                    v-for="(course, index) in sortedCourses" 
                    :key="index"
                    :course="course"
                    @click="onCourseClick(course)"
                />
            </view>
        </view>
        
        <!-- 空状态 -->
        <view v-else class="empty-state">
            <view class="empty-icon">
                <uni-icons type="calendar" size="80" color="#e0e0e0" />
            </view>
            <text class="empty-title">{{ formatDate(selectedDate) }}</text>
            <text class="empty-desc">今天没有课程安排</text>
            <text class="empty-tip">好好休息吧 🎉</text>
        </view>
        
        <!-- 课程详情弹窗 -->
        <uni-popup ref="courseDetailPopup" type="bottom" background-color="#fff">
            <view class="course-detail-popup" v-if="selectedCourse">
                <view class="popup-header">
                    <text class="popup-title">课程详情</text>
                    <button class="close-btn" @click="closeCourseDetail">
                        <uni-icons type="close" size="24" color="#666" />
                    </button>
                </view>
                
                <view class="popup-content">
                    <view class="detail-item">
                        <text class="detail-label">课程名称</text>
                        <text class="detail-value">{{ selectedCourse.course_name }}</text>
                    </view>
                    
                    <view class="detail-item">
                        <text class="detail-label">学分</text>
                        <text class="detail-value">{{ selectedCourse.course_credits }}学分</text>
                    </view>
                    
                    <view class="detail-item">
                        <text class="detail-label">课程属性</text>
                        <text class="detail-value">{{ selectedCourse.course_property }}</text>
                    </view>
                    
                    <view class="detail-item">
                        <text class="detail-label">上课时间</text>
                        <text class="detail-value">{{ selectedCourse.class_time }}</text>
                    </view>
                    
                    <view class="detail-item">
                        <text class="detail-label">教室</text>
                        <text class="detail-value">{{ selectedCourse.classroom }}</text>
                    </view>
                    
                    <view class="detail-item" v-if="selectedCourse.class_name">
                        <text class="detail-label">班级</text>
                        <text class="detail-value">{{ selectedCourse.class_name }}</text>
                    </view>
                </view>
            </view>
        </uni-popup>
    </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import CourseCard from './CourseCard.vue';

const props = defineProps({
    courses: {
        type: Array,
        default: () => []
    },
    selectedDate: {
        type: String,
        required: true
    }
});

const courseDetailPopup = ref(null);
const selectedCourse = ref(null);

// 按时间节次排序的课程列表
const sortedCourses = computed(() => {
    if (!props.courses || props.courses.length === 0) return [];
    
    return [...props.courses].sort((a, b) => {
        // 提取节次数字进行排序
        const getPeriodNumber = (period) => {
            const match = period.match(/(\d+)/);
            return match ? parseInt(match[1]) : 0;
        };
        
        return getPeriodNumber(a.period) - getPeriodNumber(b.period);
    });
});

// 格式化日期显示
function formatDate(dateStr) {
    if (!dateStr) return '';
    
    const date = new Date(dateStr);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    const weekday = weekdays[date.getDay()];
    
    // 判断是今天、明天还是昨天
    if (dateStr === today.toISOString().split('T')[0]) {
        return `今天 ${weekday}`;
    } else if (dateStr === tomorrow.toISOString().split('T')[0]) {
        return `明天 ${weekday}`;
    } else if (dateStr === yesterday.toISOString().split('T')[0]) {
        return `昨天 ${weekday}`;
    } else {
        const month = date.getMonth() + 1;
        const day = date.getDate();
        return `${month}月${day}日 ${weekday}`;
    }
}

// 点击课程卡片
function onCourseClick(course) {
    selectedCourse.value = course;
    courseDetailPopup.value?.open();
}

// 关闭课程详情
function closeCourseDetail() {
    courseDetailPopup.value?.close();
    selectedCourse.value = null;
}
</script>

<style lang="scss" scoped>
.classtable-view {
    min-height: 400rpx;
}

.courses-container {
    display: flex;
    flex-direction: column;
    gap: 16rpx;
}

.date-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx 0;
    border-bottom: 1rpx solid #f0f0f0;
    margin-bottom: 8rpx;
}

.date-title {
    font-size: 32rpx;
    font-weight: 700;
    color: #2c3e50;
}

.course-count {
    font-size: 24rpx;
    color: #7f4515;
    background: rgba(127, 69, 21, 0.1);
    padding: 4rpx 12rpx;
    border-radius: 20rpx;
}

.courses-list {
    display: flex;
    flex-direction: column;
    gap: 16rpx;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80rpx 40rpx;
    text-align: center;
}

.empty-icon {
    margin-bottom: 24rpx;
    opacity: 0.6;
}

.empty-title {
    font-size: 28rpx;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 12rpx;
}

.empty-desc {
    font-size: 24rpx;
    color: #9e9e9e;
    margin-bottom: 8rpx;
}

.empty-tip {
    font-size: 22rpx;
    color: #7f4515;
    font-style: italic;
}

/* 课程详情弹窗样式 */
.course-detail-popup {
    background: #fff;
    border-radius: 24rpx 24rpx 0 0;
    padding: 0;
    max-height: 80vh;
    overflow: hidden;
}

.popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 32rpx;
    border-bottom: 1rpx solid #f0f0f0;
    background: #fafafa;
}

.popup-title {
    font-size: 32rpx;
    font-weight: 700;
    color: #2c3e50;
}

.close-btn {
    width: 60rpx;
    height: 60rpx;
    border-radius: 50%;
    background: #fff;
    border: 1rpx solid #e0e0e0;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &::after {
        border: none;
    }
}

.popup-content {
    padding: 32rpx;
    max-height: 60vh;
    overflow-y: auto;
}

.detail-item {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 24rpx 0;
    border-bottom: 1rpx solid #f8f9fa;
    
    &:last-child {
        border-bottom: none;
    }
}

.detail-label {
    font-size: 26rpx;
    color: #666;
    font-weight: 600;
    min-width: 140rpx;
}

.detail-value {
    font-size: 26rpx;
    color: #2c3e50;
    flex: 1;
    text-align: right;
    word-break: break-all;
}
</style>
