<template>
	<view class="container">
		<!-- 学期选择器 -->
		<view class="semester-selector">
			<scroll-view scroll-x="true" class="semester-scroll">
				<view class="semester-tabs">
					<view 
						v-for="(semester, index) in semesters" 
						:key="index"
						class="semester-tab"
						:class="{ 'active': selectedSemester === index }"
						@click="selectSemester(index)"
					>
						<text class="semester-text">{{ semester.name }}</text>
					</view>
				</view>
			</scroll-view>
		</view>
		
		<!-- 成绩统计 -->
		<view class="stats-card">
			<view class="stats-row">
				<view class="stat-item">
					<text class="stat-value">{{ currentStats.gpa }}</text>
					<text class="stat-label">学期绩点</text>
				</view>
				<view class="stat-item">
					<text class="stat-value">{{ currentStats.avgScore }}</text>
					<text class="stat-label">平均分</text>
				</view>
				<view class="stat-item">
					<text class="stat-value">{{ currentStats.credits }}</text>
					<text class="stat-label">获得学分</text>
				</view>
			</view>
		</view>
		
		<!-- 成绩列表 -->
		<view class="grades-section">
			<view class="section-header">
				<text class="section-title">成绩详情</text>
				<text class="course-count">共{{ grades.length }}门课程</text>
			</view>
			
			<view v-if="loading" class="loading-state">
				<text class="loading-text">加载中...</text>
			</view>
			
			<view v-else-if="grades.length === 0" class="empty-state">
				<text class="empty-icon">📄</text>
				<text class="empty-text">暂无成绩数据</text>
			</view>
			
			<view v-else class="grades-list">
				<view 
					v-for="(grade, index) in grades" 
					:key="index"
					class="grade-card"
					@click="showGradeDetail(grade)"
				>
					<view class="grade-header">
						<view class="course-info">
							<text class="course-name">{{ grade.courseName }}</text>
							<text class="course-code">{{ grade.courseCode }}</text>
						</view>
						<view class="score-info">
							<text class="score" :class="getScoreClass(grade.score)">{{ grade.score }}</text>
							<text class="score-type">{{ grade.scoreType }}</text>
						</view>
					</view>
					
					<view class="grade-details">
						<view class="detail-item">
							<text class="detail-label">学分</text>
							<text class="detail-value">{{ grade.credits }}</text>
						</view>
						<view class="detail-item">
							<text class="detail-label">绩点</text>
							<text class="detail-value">{{ grade.gpa }}</text>
						</view>
						<view class="detail-item">
							<text class="detail-label">课程性质</text>
							<text class="detail-value">{{ grade.courseType }}</text>
						</view>
						<view class="detail-item">
							<text class="detail-label">考试性质</text>
							<text class="detail-value">{{ grade.examType }}</text>
						</view>
					</view>
					
					<!-- 分析按钮 -->
					<view class="grade-actions">
						<text class="action-btn" @click.stop="showCourseAnalysis(grade)">查看课程分析</text>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			semesters: [
				{ name: '2023-2024-2', id: '20232' },
				{ name: '2023-2024-1', id: '20231' },
				{ name: '2022-2023-2', id: '20222' },
				{ name: '2022-2023-1', id: '20221' }
			],
			selectedSemester: 0,
			loading: true,
			grades: [],
			currentStats: {
				gpa: '0.00',
				avgScore: '0.0',
				credits: '0'
			}
		}
	},
	onLoad() {
		this.loadGrades();
	},
	methods: {
		selectSemester(index) {
			this.selectedSemester = index;
			this.loadGrades();
		},
		
		async loadGrades() {
			this.loading = true;
			
			try {
				// 模拟API调用
				await this.mockLoadGrades();
			} catch (error) {
				uni.showToast({
					title: '加载失败',
					icon: 'none'
				});
			} finally {
				this.loading = false;
			}
		},
		
		mockLoadGrades() {
			return new Promise((resolve) => {
				setTimeout(() => {
					// 模拟成绩数据
					this.grades = [
						{
							courseName: '数据结构与算法',
							courseCode: 'CS1001',
							score: '92',
							scoreType: '百分制',
							credits: '4.0',
							gpa: '4.0',
							courseType: '专业必修',
							examType: '期末考试'
						},
						{
							courseName: '操作系统原理',
							courseCode: 'CS1002',
							score: '88',
							scoreType: '百分制',
							credits: '3.0',
							gpa: '3.7',
							courseType: '专业必修',
							examType: '期末考试'
						},
						{
							courseName: '数据库系统概论',
							courseCode: 'CS1003',
							score: '85',
							scoreType: '百分制',
							credits: '3.0',
							gpa: '3.5',
							courseType: '专业必修',
							examType: '期末考试'
						},
						{
							courseName: '计算机网络',
							courseCode: 'CS1004',
							score: '90',
							scoreType: '百分制',
							credits: '3.0',
							gpa: '3.9',
							courseType: '专业必修',
							examType: '期末考试'
						},
						{
							courseName: '软件工程',
							courseCode: 'CS1005',
							score: '优秀',
							scoreType: '等级制',
							credits: '2.0',
							gpa: '4.0',
							courseType: '专业选修',
							examType: '课程设计'
						}
					];
					
					// 计算统计数据
					this.calculateStats();
					resolve();
				}, 1000);
			});
		},
		
		calculateStats() {
			let totalScore = 0;
			let totalCredits = 0;
			let totalGpaPoints = 0;
			let scoreCount = 0;
			
			this.grades.forEach(grade => {
				const credits = parseFloat(grade.credits);
				totalCredits += credits;
				
				if (grade.scoreType === '百分制') {
					const score = parseFloat(grade.score);
					totalScore += score;
					scoreCount++;
				}
				
				const gpa = parseFloat(grade.gpa);
				totalGpaPoints += gpa * credits;
			});
			
			this.currentStats = {
				gpa: totalCredits > 0 ? (totalGpaPoints / totalCredits).toFixed(2) : '0.00',
				avgScore: scoreCount > 0 ? (totalScore / scoreCount).toFixed(1) : '0.0',
				credits: totalCredits.toString()
			};
		},
		
		getScoreClass(score) {
			if (score === '优秀' || (parseFloat(score) >= 90)) {
				return 'score-excellent';
			} else if (score === '良好' || (parseFloat(score) >= 80)) {
				return 'score-good';
			} else if (score === '中等' || (parseFloat(score) >= 70)) {
				return 'score-medium';
			} else if (score === '及格' || (parseFloat(score) >= 60)) {
				return 'score-pass';
			} else {
				return 'score-fail';
			}
		},
		
		showGradeDetail(grade) {
			uni.showModal({
				title: grade.courseName,
				content: `成绩：${grade.score}\n学分：${grade.credits}\n绩点：${grade.gpa}\n课程性质：${grade.courseType}`,
				showCancel: false
			});
		},
		
		showCourseAnalysis(grade) {
			uni.navigateTo({
				url: `/pages/stats/stats?courseId=${grade.courseCode}&courseName=${grade.courseName}`
			});
		}
	}
}
</script>

<style lang="scss" scoped>
.container {
	min-height: 100vh;
	background: #F8F9FA;
	padding-bottom: 32rpx;
}

.semester-selector {
	background: #FFFFFF;
	padding: 24rpx 0;
	border-bottom: 1rpx solid #E5E7EB;
}

.semester-scroll {
	white-space: nowrap;
}

.semester-tabs {
	display: flex;
	padding: 0 24rpx;
}

.semester-tab {
	flex-shrink: 0;
	padding: 16rpx 24rpx;
	margin-right: 16rpx;
	background: #F8F9FA;
	border-radius: 24rpx;
	border: 2rpx solid transparent;
}

.semester-tab.active {
	background: #9B0400;
	border-color: #9B0400;
}

.semester-text {
	font-size: 26rpx;
	color: #6B7280;
	font-weight: 500;
}

.semester-tab.active .semester-text {
	color: #FFFFFF;
}

.stats-card {
	background: #FFFFFF;
	margin: 24rpx;
	border-radius: 16rpx;
	padding: 32rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.stats-row {
	display: flex;
	justify-content: space-between;
}

.stat-item {
	text-align: center;
	flex: 1;
}

.stat-value {
	font-size: 48rpx;
	font-weight: 700;
	color: #9B0400;
	display: block;
	margin-bottom: 8rpx;
}

.stat-label {
	font-size: 24rpx;
	color: #6B7280;
	display: block;
}

.grades-section {
	margin: 0 24rpx;
}

.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 24rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #374151;
}

.course-count {
	font-size: 24rpx;
	color: #6B7280;
}

.loading-state {
	text-align: center;
	padding: 80rpx 0;
}

.loading-text {
	font-size: 28rpx;
	color: #6B7280;
}

.empty-state {
	text-align: center;
	padding: 80rpx 0;
}

.empty-icon {
	font-size: 80rpx;
	display: block;
	margin-bottom: 24rpx;
}

.empty-text {
	font-size: 28rpx;
	color: #6B7280;
}

.grades-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.grade-card {
	background: #FFFFFF;
	border-radius: 12rpx;
	padding: 24rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
	border: 1rpx solid #E5E7EB;
}

.grade-card:active {
	background: #F8F9FA;
	transform: scale(0.99);
}

.grade-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 16rpx;
}

.course-info {
	flex: 1;
}

.course-name {
	font-size: 32rpx;
	font-weight: 600;
	color: #374151;
	display: block;
	margin-bottom: 4rpx;
}

.course-code {
	font-size: 24rpx;
	color: #6B7280;
	display: block;
}

.score-info {
	text-align: right;
}

.score {
	font-size: 48rpx;
	font-weight: 700;
	display: block;
	margin-bottom: 4rpx;
}

.score-excellent {
	color: #10B981;
}

.score-good {
	color: #3B82F6;
}

.score-medium {
	color: #F59E0B;
}

.score-pass {
	color: #6B7280;
}

.score-fail {
	color: #EF4444;
}

.score-type {
	font-size: 20rpx;
	color: #9CA3AF;
	display: block;
}

.grade-details {
	display: flex;
	flex-wrap: wrap;
	gap: 16rpx;
	margin-bottom: 16rpx;
}

.detail-item {
	display: flex;
	flex-direction: column;
	min-width: 0;
	flex: 1;
}

.detail-label {
	font-size: 20rpx;
	color: #9CA3AF;
	margin-bottom: 4rpx;
	display: block;
}

.detail-value {
	font-size: 24rpx;
	color: #374151;
	font-weight: 500;
	display: block;
}

.grade-actions {
	display: flex;
	justify-content: flex-end;
}

.action-btn {
	font-size: 24rpx;
	color: #9B0400;
	padding: 8rpx 16rpx;
	background: rgba(155, 4, 0, 0.1);
	border-radius: 16rpx;
	border: 1rpx solid rgba(155, 4, 0, 0.2);
}

.action-btn:active {
	background: rgba(155, 4, 0, 0.2);
}
</style>
