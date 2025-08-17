<template>
	<view class="container">
		<!-- 个人统计概览 -->
		<view class="overview-section">
			<text class="section-title">学业统计</text>
			<view class="stats-grid">
				<view class="stat-card">
					<text class="stat-value">{{ personalStats.totalGpa }}</text>
					<text class="stat-label">总绩点</text>
					<view class="stat-trend positive">
						<text class="trend-icon">↗</text>
						<text class="trend-text">+0.12</text>
					</view>
				</view>
				
				<view class="stat-card">
					<text class="stat-value">{{ personalStats.avgScore }}</text>
					<text class="stat-label">平均分</text>
					<view class="stat-trend positive">
						<text class="trend-icon">↗</text>
						<text class="trend-text">+2.3</text>
					</view>
				</view>
				
				<view class="stat-card">
					<text class="stat-value">{{ personalStats.totalCredits }}</text>
					<text class="stat-label">获得学分</text>
					<view class="stat-trend neutral">
						<text class="trend-text">-</text>
					</view>
				</view>
				
				<view class="stat-card">
					<text class="stat-value">{{ personalStats.rank }}</text>
					<text class="stat-label">班级排名</text>
					<view class="stat-trend positive">
						<text class="trend-icon">↗</text>
						<text class="trend-text">+2</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 课程分析 -->
		<view class="course-analysis-section">
			<view class="section-header">
				<text class="section-title">课程分析</text>
				<text class="section-subtitle">基于众包数据</text>
			</view>
			
			<view class="analysis-tabs">
				<view 
					class="tab-item" 
					:class="{ active: activeTab === 'ranking' }"
					@click="setActiveTab('ranking')"
				>
					<text class="tab-text">成绩排名</text>
				</view>
				<view 
					class="tab-item" 
					:class="{ active: activeTab === 'analysis' }"
					@click="setActiveTab('analysis')"
				>
					<text class="tab-text">课程分析</text>
				</view>
			</view>
			
			<!-- 成绩排名标签页 -->
			<view v-if="activeTab === 'ranking'" class="ranking-content">
				<view v-if="!hasContributed" class="contribute-prompt">
					<view class="prompt-card">
						<text class="prompt-title">💡 贡献数据，解锁排名功能</text>
						<text class="prompt-desc">分享您的成绩数据（匿名处理），即可查看班级排名和课程分析</text>
						<button class="contribute-btn" @click="showContributeDialog">贡献我的数据</button>
					</view>
				</view>
				
				<view v-else class="ranking-list">
					<view 
						v-for="(course, index) in rankingData" 
						:key="index"
						class="ranking-item"
					>
						<view class="course-info">
							<text class="course-name">{{ course.courseName }}</text>
							<text class="course-score">{{ course.myScore }}分</text>
						</view>
						<view class="ranking-info">
							<text class="rank-text">{{ course.rank }}</text>
							<text class="percentile">{{ course.percentile }}</text>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 课程分析标签页 -->
			<view v-if="activeTab === 'analysis'" class="analysis-content">
				<view class="course-selector">
					<picker 
						:value="selectedCourseIndex" 
						:range="courseList" 
						range-key="name"
						@change="onCourseChange"
					>
						<view class="selector-display">
							<text class="selector-text">{{ selectedCourse.name || '选择课程' }}</text>
							<text class="selector-arrow">▼</text>
						</view>
					</picker>
				</view>
				
				<view v-if="selectedCourse.name" class="course-stats">
					<view class="stats-header">
						<text class="stats-title">{{ selectedCourse.name }}</text>
						<text class="stats-subtitle">历史数据分析</text>
					</view>
					
					<view class="stats-cards">
						<view class="stats-card">
							<text class="stats-value">{{ selectedCourse.avgScore }}</text>
							<text class="stats-label">平均分</text>
						</view>
						<view class="stats-card">
							<text class="stats-value">{{ selectedCourse.maxScore }}</text>
							<text class="stats-label">最高分</text>
						</view>
						<view class="stats-card">
							<text class="stats-value">{{ selectedCourse.minScore }}</text>
							<text class="stats-label">最低分</text>
						</view>
						<view class="stats-card">
							<text class="stats-value">{{ selectedCourse.passRate }}%</text>
							<text class="stats-label">及格率</text>
						</view>
					</view>
					
					<!-- 分数分布 -->
					<view class="distribution-section">
						<text class="distribution-title">分数分布</text>
						<view class="distribution-chart">
							<view 
								v-for="(item, index) in selectedCourse.distribution" 
								:key="index"
								class="distribution-bar"
							>
								<view 
									class="bar-fill" 
									:style="{ height: item.percentage + '%' }"
								></view>
								<text class="bar-label">{{ item.range }}</text>
								<text class="bar-count">{{ item.count }}人</text>
							</view>
						</view>
					</view>
					
					<!-- 教师评价 -->
					<view class="teacher-section">
						<text class="teacher-title">教师评价</text>
						<view class="teacher-card">
							<view class="teacher-info">
								<text class="teacher-name">{{ selectedCourse.teacher }}</text>
								<text class="teacher-rating">评分: {{ selectedCourse.teacherRating }}/5.0</text>
							</view>
							<view class="teacher-tags">
								<text 
									v-for="(tag, index) in selectedCourse.teacherTags" 
									:key="index"
									class="teacher-tag"
								>
									{{ tag }}
								</text>
							</view>
						</view>
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
			activeTab: 'ranking',
			hasContributed: false,
			personalStats: {
				totalGpa: '3.85',
				avgScore: '86.2',
				totalCredits: '132',
				rank: '5/35'
			},
			rankingData: [],
			courseList: [
				{ 
					name: '数据结构与算法',
					code: 'CS1001',
					avgScore: '82.5',
					maxScore: '96',
					minScore: '45',
					passRate: '92',
					teacher: '张教授',
					teacherRating: '4.6',
					teacherTags: ['讲解清晰', '要求严格', '作业较多'],
					distribution: [
						{ range: '90-100', count: 8, percentage: 80 },
						{ range: '80-89', count: 15, percentage: 100 },
						{ range: '70-79', count: 7, percentage: 60 },
						{ range: '60-69', count: 3, percentage: 30 },
						{ range: '<60', count: 2, percentage: 20 }
					]
				},
				{ 
					name: '操作系统原理',
					code: 'CS1002',
					avgScore: '78.3',
					maxScore: '92',
					minScore: '38',
					passRate: '85',
					teacher: '李教授',
					teacherRating: '4.2',
					teacherTags: ['理论深入', '实验有趣', '考试较难'],
					distribution: [
						{ range: '90-100', count: 3, percentage: 40 },
						{ range: '80-89', count: 12, percentage: 90 },
						{ range: '70-79', count: 10, percentage: 75 },
						{ range: '60-69', count: 6, percentage: 50 },
						{ range: '<60', count: 4, percentage: 35 }
					]
				}
			],
			selectedCourseIndex: 0
		}
	},
	computed: {
		selectedCourse() {
			return this.courseList[this.selectedCourseIndex] || {};
		}
	},
	onLoad(options) {
		// 检查是否从成绩页面跳转过来
		if (options.courseId && options.courseName) {
			this.activeTab = 'analysis';
			const courseIndex = this.courseList.findIndex(course => 
				course.code === options.courseId || course.name === options.courseName
			);
			if (courseIndex !== -1) {
				this.selectedCourseIndex = courseIndex;
			}
		}
		
		this.checkContributionStatus();
		this.loadRankingData();
	},
	methods: {
		setActiveTab(tab) {
			this.activeTab = tab;
		},
		
		checkContributionStatus() {
			// 模拟检查用户是否已贡献数据
			const contributed = uni.getStorageSync('has_contributed');
			this.hasContributed = contributed === 'true';
		},
		
		showContributeDialog() {
			uni.showModal({
				title: '数据贡献授权',
				content: '您的成绩数据将被匿名处理，仅用于计算课程平均分和班级排名。我们承诺保护您的隐私安全。',
				confirmText: '同意贡献',
				cancelText: '暂不贡献',
				success: (res) => {
					if (res.confirm) {
						this.contributeData();
					}
				}
			});
		},
		
		async contributeData() {
			uni.showLoading({
				title: '上传中...'
			});
			
			try {
				// 模拟上传数据
				await this.mockContributeData();
				
				uni.setStorageSync('has_contributed', 'true');
				this.hasContributed = true;
				
				uni.hideLoading();
				uni.showToast({
					title: '贡献成功',
					icon: 'success'
				});
				
				this.loadRankingData();
			} catch (error) {
				uni.hideLoading();
				uni.showToast({
					title: '贡献失败',
					icon: 'none'
				});
			}
		},
		
		mockContributeData() {
			return new Promise((resolve) => {
				setTimeout(() => {
					resolve();
				}, 2000);
			});
		},
		
		loadRankingData() {
			if (!this.hasContributed) return;
			
			// 模拟排名数据
			this.rankingData = [
				{
					courseName: '数据结构与算法',
					myScore: 92,
					rank: '3/35',
					percentile: '第91百分位'
				},
				{
					courseName: '操作系统原理',
					myScore: 88,
					rank: '5/35',
					percentile: '第85百分位'
				},
				{
					courseName: '数据库系统概论',
					myScore: 85,
					rank: '8/35',
					percentile: '第77百分位'
				},
				{
					courseName: '计算机网络',
					myScore: 90,
					rank: '4/35',
					percentile: '第88百分位'
				}
			];
		},
		
		onCourseChange(e) {
			this.selectedCourseIndex = e.detail.value;
		}
	}
}
</script>

<style lang="scss" scoped>
.container {
	min-height: 100vh;
	background: #F8F9FA;
	padding: 24rpx;
}

.overview-section {
	margin-bottom: 32rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #374151;
	display: block;
	margin-bottom: 24rpx;
}

.stats-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 16rpx;
}

.stat-card {
	background: #FFFFFF;
	border-radius: 12rpx;
	padding: 24rpx;
	text-align: center;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
	position: relative;
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
	margin-bottom: 8rpx;
}

.stat-trend {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 4rpx;
}

.stat-trend.positive {
	color: #10B981;
}

.stat-trend.negative {
	color: #EF4444;
}

.stat-trend.neutral {
	color: #6B7280;
}

.trend-icon {
	font-size: 20rpx;
	font-weight: 600;
}

.trend-text {
	font-size: 20rpx;
	font-weight: 500;
}

.course-analysis-section {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 32rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.section-header {
	margin-bottom: 24rpx;
}

.section-subtitle {
	font-size: 24rpx;
	color: #6B7280;
	display: block;
	margin-top: 4rpx;
}

.analysis-tabs {
	display: flex;
	background: #F8F9FA;
	border-radius: 8rpx;
	padding: 8rpx;
	margin-bottom: 32rpx;
}

.tab-item {
	flex: 1;
	text-align: center;
	padding: 16rpx;
	border-radius: 6rpx;
}

.tab-item.active {
	background: #9B0400;
}

.tab-text {
	font-size: 28rpx;
	color: #6B7280;
	font-weight: 500;
}

.tab-item.active .tab-text {
	color: #FFFFFF;
}

.contribute-prompt {
	text-align: center;
	padding: 48rpx 24rpx;
}

.prompt-card {
	background: linear-gradient(135deg, rgba(155, 4, 0, 0.05) 0%, rgba(155, 4, 0, 0.02) 100%);
	border: 2rpx solid rgba(155, 4, 0, 0.1);
	border-radius: 16rpx;
	padding: 48rpx 32rpx;
}

.prompt-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #374151;
	display: block;
	margin-bottom: 16rpx;
}

.prompt-desc {
	font-size: 26rpx;
	color: #6B7280;
	line-height: 1.5;
	display: block;
	margin-bottom: 32rpx;
}

.contribute-btn {
	background: #9B0400;
	color: #FFFFFF;
	border: none;
	border-radius: 8rpx;
	padding: 24rpx 48rpx;
	font-size: 28rpx;
	font-weight: 600;
}

.contribute-btn:active {
	background: #7A0300;
}

.ranking-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.ranking-item {
	background: #F8F9FA;
	border-radius: 12rpx;
	padding: 24rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
	border: 1rpx solid #E5E7EB;
}

.course-info {
	flex: 1;
}

.course-name {
	font-size: 28rpx;
	font-weight: 600;
	color: #374151;
	display: block;
	margin-bottom: 4rpx;
}

.course-score {
	font-size: 24rpx;
	color: #9B0400;
	font-weight: 500;
	display: block;
}

.ranking-info {
	text-align: right;
}

.rank-text {
	font-size: 32rpx;
	font-weight: 700;
	color: #9B0400;
	display: block;
	margin-bottom: 4rpx;
}

.percentile {
	font-size: 20rpx;
	color: #6B7280;
	display: block;
}

.course-selector {
	margin-bottom: 32rpx;
}

.selector-display {
	background: #F8F9FA;
	border: 2rpx solid #E5E7EB;
	border-radius: 8rpx;
	padding: 24rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.selector-text {
	font-size: 28rpx;
	color: #374151;
}

.selector-arrow {
	font-size: 24rpx;
	color: #6B7280;
}

.course-stats {
	margin-bottom: 32rpx;
}

.stats-header {
	margin-bottom: 24rpx;
}

.stats-title {
	font-size: 28rpx;
	font-weight: 600;
	color: #374151;
	display: block;
	margin-bottom: 4rpx;
}

.stats-subtitle {
	font-size: 22rpx;
	color: #6B7280;
	display: block;
}

.stats-cards {
	display: grid;
	grid-template-columns: 1fr 1fr 1fr 1fr;
	gap: 12rpx;
	margin-bottom: 32rpx;
}

.stats-card {
	background: #F8F9FA;
	border-radius: 8rpx;
	padding: 16rpx;
	text-align: center;
}

.stats-value {
	font-size: 32rpx;
	font-weight: 700;
	color: #9B0400;
	display: block;
	margin-bottom: 4rpx;
}

.stats-label {
	font-size: 20rpx;
	color: #6B7280;
	display: block;
}

.distribution-section {
	margin-bottom: 32rpx;
}

.distribution-title {
	font-size: 26rpx;
	font-weight: 600;
	color: #374151;
	display: block;
	margin-bottom: 16rpx;
}

.distribution-chart {
	display: flex;
	align-items: flex-end;
	justify-content: space-between;
	height: 200rpx;
	padding: 16rpx;
	background: #F8F9FA;
	border-radius: 8rpx;
}

.distribution-bar {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	height: 100%;
	position: relative;
}

.bar-fill {
	width: 60%;
	background: linear-gradient(to top, #9B0400, #B91C1C);
	border-radius: 4rpx 4rpx 0 0;
	margin-top: auto;
	margin-bottom: 8rpx;
}

.bar-label {
	font-size: 18rpx;
	color: #6B7280;
	margin-bottom: 2rpx;
	text-align: center;
}

.bar-count {
	font-size: 16rpx;
	color: #9CA3AF;
	text-align: center;
}

.teacher-section {
	margin-bottom: 16rpx;
}

.teacher-title {
	font-size: 26rpx;
	font-weight: 600;
	color: #374151;
	display: block;
	margin-bottom: 16rpx;
}

.teacher-card {
	background: #F8F9FA;
	border-radius: 8rpx;
	padding: 24rpx;
}

.teacher-info {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 16rpx;
}

.teacher-name {
	font-size: 26rpx;
	font-weight: 600;
	color: #374151;
}

.teacher-rating {
	font-size: 24rpx;
	color: #F59E0B;
	font-weight: 500;
}

.teacher-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 8rpx;
}

.teacher-tag {
	background: rgba(155, 4, 0, 0.1);
	color: #9B0400;
	font-size: 20rpx;
	padding: 8rpx 12rpx;
	border-radius: 12rpx;
	border: 1rpx solid rgba(155, 4, 0, 0.2);
}
</style>
