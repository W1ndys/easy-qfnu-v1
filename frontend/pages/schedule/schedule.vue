<template>
	<view class="container">
		<!-- 周选择器 -->
		<view class="week-selector">
			<view class="week-nav">
				<text class="nav-btn" @click="previousWeek">‹</text>
				<text class="week-text">{{ currentWeekText }}</text>
				<text class="nav-btn" @click="nextWeek">›</text>
			</view>
			<text class="week-date">{{ weekDateRange }}</text>
		</view>
		
		<!-- 课表主体 -->
		<view class="schedule-main">
			<!-- 时间轴和星期头部 -->
			<view class="schedule-header">
				<view class="time-axis-header"></view>
				<view class="weekdays">
					<view 
						v-for="(day, index) in weekdays" 
						:key="index"
						class="weekday"
						:class="{ 'today': isToday(index) }"
					>
						<text class="weekday-name">{{ day.name }}</text>
						<text class="weekday-date">{{ day.date }}</text>
					</view>
				</view>
			</view>
			
			<!-- 课表内容区域 -->
			<scroll-view scroll-y="true" class="schedule-content">
				<view class="schedule-grid">
					<!-- 时间轴 -->
					<view class="time-axis">
						<view 
							v-for="(time, index) in timeSlots" 
							:key="index"
							class="time-slot"
							:class="{ 'current-time': isCurrentTime(index) }"
						>
							<text class="time-text">{{ time.start }}</text>
							<text class="time-text">{{ time.end }}</text>
						</view>
					</view>
					
					<!-- 课程网格 -->
					<view class="courses-grid">
						<view 
							v-for="(day, dayIndex) in 7" 
							:key="dayIndex"
							class="day-column"
						>
							<view 
								v-for="(slot, slotIndex) in timeSlots.length" 
								:key="slotIndex"
								class="course-slot"
							>
								<!-- 课程卡片 -->
								<view 
									v-if="getCourseForSlot(dayIndex, slotIndex)"
									class="course-card"
									:class="getCourseClass(getCourseForSlot(dayIndex, slotIndex))"
									@click="showCourseDetail(getCourseForSlot(dayIndex, slotIndex))"
								>
									<text class="course-name">{{ getCourseForSlot(dayIndex, slotIndex).name }}</text>
									<text class="course-location">{{ getCourseForSlot(dayIndex, slotIndex).location }}</text>
									<text class="course-teacher">{{ getCourseForSlot(dayIndex, slotIndex).teacher }}</text>
								</view>
							</view>
						</view>
					</view>
				</view>
			</scroll-view>
		</view>
		
		<!-- 今日课程概览 -->
		<view class="today-overview">
			<view class="overview-header">
				<text class="overview-title">今日课程</text>
				<text class="overview-count">{{ todayCourses.length }}门课程</text>
			</view>
			
			<scroll-view scroll-x="true" class="today-courses">
				<view class="today-course-list">
					<view 
						v-for="(course, index) in todayCourses" 
						:key="index"
						class="today-course-item"
						@click="showCourseDetail(course)"
					>
						<text class="today-course-time">{{ course.timeText }}</text>
						<text class="today-course-name">{{ course.name }}</text>
						<text class="today-course-location">{{ course.location }}</text>
					</view>
					
					<view v-if="todayCourses.length === 0" class="no-courses">
						<text class="no-courses-text">今日无课程安排</text>
					</view>
				</view>
			</scroll-view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			currentWeek: 1,
			weekdays: [],
			timeSlots: [
				{ start: '08:00', end: '08:45' },
				{ start: '08:55', end: '09:40' },
				{ start: '10:00', end: '10:45' },
				{ start: '10:55', end: '11:40' },
				{ start: '14:00', end: '14:45' },
				{ start: '14:55', end: '15:40' },
				{ start: '16:00', end: '16:45' },
				{ start: '16:55', end: '17:40' },
				{ start: '19:00', end: '19:45' },
				{ start: '19:55', end: '20:40' }
			],
			courses: [],
			todayCourses: []
		}
	},
	computed: {
		currentWeekText() {
			return `第${this.currentWeek}周`;
		},
		weekDateRange() {
			if (this.weekdays.length === 0) return '';
			const start = this.weekdays[0].fullDate;
			const end = this.weekdays[6].fullDate;
			return `${start} - ${end}`;
		}
	},
	onLoad() {
		this.initWeekdays();
		this.loadSchedule();
	},
	methods: {
		initWeekdays() {
			const today = new Date();
			const currentDay = today.getDay();
			const mondayOffset = currentDay === 0 ? -6 : 1 - currentDay;
			
			this.weekdays = [];
			const weekNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
			
			for (let i = 0; i < 7; i++) {
				const date = new Date(today);
				date.setDate(today.getDate() + mondayOffset + i);
				
				this.weekdays.push({
					name: weekNames[i],
					date: `${date.getMonth() + 1}/${date.getDate()}`,
					fullDate: `${date.getMonth() + 1}.${date.getDate()}`,
					dateObj: date
				});
			}
			
			this.updateTodayCourses();
		},
		
		previousWeek() {
			this.currentWeek--;
			this.adjustWeekdays(-7);
			this.loadSchedule();
		},
		
		nextWeek() {
			this.currentWeek++;
			this.adjustWeekdays(7);
			this.loadSchedule();
		},
		
		adjustWeekdays(days) {
			this.weekdays.forEach(day => {
				day.dateObj.setDate(day.dateObj.getDate() + days);
				day.date = `${day.dateObj.getMonth() + 1}/${day.dateObj.getDate()}`;
				day.fullDate = `${day.dateObj.getMonth() + 1}.${day.dateObj.getDate()}`;
			});
			this.updateTodayCourses();
		},
		
		isToday(dayIndex) {
			const today = new Date();
			const targetDate = this.weekdays[dayIndex]?.dateObj;
			if (!targetDate) return false;
			
			return today.toDateString() === targetDate.toDateString();
		},
		
		isCurrentTime(slotIndex) {
			const now = new Date();
			const currentTime = now.getHours() * 60 + now.getMinutes();
			const slot = this.timeSlots[slotIndex];
			
			const [startHour, startMin] = slot.start.split(':').map(Number);
			const [endHour, endMin] = slot.end.split(':').map(Number);
			
			const startTime = startHour * 60 + startMin;
			const endTime = endHour * 60 + endMin;
			
			return currentTime >= startTime && currentTime <= endTime;
		},
		
		async loadSchedule() {
			try {
				// 模拟API调用
				await this.mockLoadSchedule();
			} catch (error) {
				uni.showToast({
					title: '加载失败',
					icon: 'none'
				});
			}
		},
		
		mockLoadSchedule() {
			return new Promise((resolve) => {
				setTimeout(() => {
					// 模拟课程数据
					this.courses = [
						{
							name: '数据结构与算法',
							teacher: '张教授',
							location: '教学楼A101',
							day: 0, // 周一
							startSlot: 0, // 第1节课
							duration: 2, // 持续2节课
							type: '必修',
							weeks: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
						},
						{
							name: '操作系统原理',
							teacher: '李教授',
							location: '教学楼B203',
							day: 1, // 周二
							startSlot: 2,
							duration: 2,
							type: '必修',
							weeks: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
						},
						{
							name: '数据库系统概论',
							teacher: '王教授',
							location: '教学楼C305',
							day: 2, // 周三
							startSlot: 4,
							duration: 2,
							type: '必修',
							weeks: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
						},
						{
							name: '计算机网络',
							teacher: '赵教授',
							location: '教学楼A205',
							day: 3, // 周四
							startSlot: 0,
							duration: 2,
							type: '必修',
							weeks: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
						},
						{
							name: '软件工程',
							teacher: '陈教授',
							location: '实验楼501',
							day: 4, // 周五
							startSlot: 6,
							duration: 2,
							type: '选修',
							weeks: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
						}
					];
					
					this.updateTodayCourses();
					resolve();
				}, 800);
			});
		},
		
		updateTodayCourses() {
			const today = new Date();
			const todayIndex = this.weekdays.findIndex(day => 
				day.dateObj.toDateString() === today.toDateString()
			);
			
			if (todayIndex === -1) {
				this.todayCourses = [];
				return;
			}
			
			this.todayCourses = this.courses
				.filter(course => 
					course.day === todayIndex && 
					course.weeks.includes(this.currentWeek)
				)
				.map(course => ({
					...course,
					timeText: `${this.timeSlots[course.startSlot].start}-${this.timeSlots[course.startSlot + course.duration - 1].end}`
				}))
				.sort((a, b) => a.startSlot - b.startSlot);
		},
		
		getCourseForSlot(dayIndex, slotIndex) {
			return this.courses.find(course => 
				course.day === dayIndex && 
				course.startSlot === slotIndex &&
				course.weeks.includes(this.currentWeek)
			);
		},
		
		getCourseClass(course) {
			if (!course) return '';
			return course.type === '必修' ? 'course-required' : 'course-elective';
		},
		
		showCourseDetail(course) {
			if (!course) return;
			
			const timeText = `${this.timeSlots[course.startSlot].start}-${this.timeSlots[course.startSlot + course.duration - 1].end}`;
			
			uni.showModal({
				title: course.name,
				content: `时间：${timeText}\n地点：${course.location}\n教师：${course.teacher}\n类型：${course.type}`,
				showCancel: false
			});
		}
	}
}
</script>

<style lang="scss" scoped>
.container {
	min-height: 100vh;
	background: #F8F9FA;
	display: flex;
	flex-direction: column;
}

.week-selector {
	background: #FFFFFF;
	padding: 24rpx;
	border-bottom: 1rpx solid #E5E7EB;
}

.week-nav {
	display: flex;
	justify-content: center;
	align-items: center;
	margin-bottom: 8rpx;
}

.nav-btn {
	font-size: 36rpx;
	color: #9B0400;
	padding: 8rpx 16rpx;
	font-weight: 600;
}

.nav-btn:active {
	color: #7A0300;
}

.week-text {
	font-size: 32rpx;
	font-weight: 600;
	color: #374151;
	margin: 0 32rpx;
}

.week-date {
	font-size: 24rpx;
	color: #6B7280;
	text-align: center;
	display: block;
}

.schedule-main {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.schedule-header {
	background: #FFFFFF;
	display: flex;
	border-bottom: 1rpx solid #E5E7EB;
}

.time-axis-header {
	width: 120rpx;
	height: 80rpx;
	background: #F8F9FA;
	border-right: 1rpx solid #E5E7EB;
}

.weekdays {
	flex: 1;
	display: flex;
}

.weekday {
	flex: 1;
	text-align: center;
	padding: 16rpx 8rpx;
	border-right: 1rpx solid #E5E7EB;
}

.weekday.today {
	background: rgba(155, 4, 0, 0.05);
}

.weekday-name {
	font-size: 24rpx;
	color: #374151;
	font-weight: 500;
	display: block;
	margin-bottom: 4rpx;
}

.weekday-date {
	font-size: 20rpx;
	color: #6B7280;
	display: block;
}

.weekday.today .weekday-name {
	color: #9B0400;
	font-weight: 600;
}

.schedule-content {
	flex: 1;
	background: #FFFFFF;
}

.schedule-grid {
	display: flex;
	min-height: 800rpx;
}

.time-axis {
	width: 120rpx;
	border-right: 1rpx solid #E5E7EB;
}

.time-slot {
	height: 80rpx;
	padding: 8rpx;
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	border-bottom: 1rpx solid #E5E7EB;
	background: #F8F9FA;
}

.time-slot.current-time {
	background: rgba(155, 4, 0, 0.1);
}

.time-text {
	font-size: 18rpx;
	color: #6B7280;
	line-height: 1.2;
	display: block;
}

.time-slot.current-time .time-text {
	color: #9B0400;
	font-weight: 600;
}

.courses-grid {
	flex: 1;
	display: flex;
}

.day-column {
	flex: 1;
	border-right: 1rpx solid #E5E7EB;
}

.course-slot {
	height: 80rpx;
	border-bottom: 1rpx solid #E5E7EB;
	position: relative;
}

.course-card {
	position: absolute;
	top: 2rpx;
	left: 2rpx;
	right: 2rpx;
	bottom: 2rpx;
	border-radius: 6rpx;
	padding: 8rpx;
	display: flex;
	flex-direction: column;
	justify-content: center;
	overflow: hidden;
}

.course-required {
	background: rgba(155, 4, 0, 0.1);
	border: 2rpx solid #9B0400;
}

.course-elective {
	background: rgba(59, 130, 246, 0.1);
	border: 2rpx solid #3B82F6;
}

.course-name {
	font-size: 20rpx;
	font-weight: 600;
	color: #374151;
	display: block;
	margin-bottom: 2rpx;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.course-required .course-name {
	color: #9B0400;
}

.course-elective .course-name {
	color: #3B82F6;
}

.course-location,
.course-teacher {
	font-size: 16rpx;
	color: #6B7280;
	display: block;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.today-overview {
	background: #FFFFFF;
	border-top: 1rpx solid #E5E7EB;
	padding: 24rpx;
}

.overview-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 16rpx;
}

.overview-title {
	font-size: 28rpx;
	font-weight: 600;
	color: #374151;
}

.overview-count {
	font-size: 24rpx;
	color: #6B7280;
}

.today-courses {
	white-space: nowrap;
}

.today-course-list {
	display: flex;
	gap: 16rpx;
	padding-bottom: 8rpx;
}

.today-course-item {
	flex-shrink: 0;
	background: #F8F9FA;
	border-radius: 12rpx;
	padding: 16rpx;
	border: 2rpx solid #E5E7EB;
	min-width: 200rpx;
}

.today-course-item:active {
	background: rgba(155, 4, 0, 0.05);
	border-color: #9B0400;
}

.today-course-time {
	font-size: 20rpx;
	color: #9B0400;
	font-weight: 600;
	display: block;
	margin-bottom: 4rpx;
}

.today-course-name {
	font-size: 24rpx;
	font-weight: 600;
	color: #374151;
	display: block;
	margin-bottom: 4rpx;
}

.today-course-location {
	font-size: 20rpx;
	color: #6B7280;
	display: block;
}

.no-courses {
	flex-shrink: 0;
	text-align: center;
	padding: 32rpx;
	min-width: 200rpx;
}

.no-courses-text {
	font-size: 24rpx;
	color: #9CA3AF;
}
</style>