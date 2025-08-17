<template>
	<view class="container">
		<!-- 用户信息卡片 -->
		<view class="user-card">
			<view class="user-info">
				<text class="user-name">{{ userInfo.name }}</text>
				<text class="user-class">{{ userInfo.class }}</text>
				<text class="user-id">学号：{{ userInfo.studentId }}</text>
			</view>
			<view class="user-avatar">
				<text class="avatar-text">{{ getAvatarText() }}</text>
			</view>
		</view>
		
		<!-- 快速统计 -->
		<view class="stats-section">
			<text class="section-title">学业概览</text>
			<view class="stats-grid">
				<view class="stat-item">
					<text class="stat-value">{{ stats.gpa }}</text>
					<text class="stat-label">总绩点</text>
				</view>
				<view class="stat-item">
					<text class="stat-value">{{ stats.avgScore }}</text>
					<text class="stat-label">平均分</text>
				</view>
				<view class="stat-item">
					<text class="stat-value">{{ stats.totalCredits }}</text>
					<text class="stat-label">总学分</text>
				</view>
			</view>
		</view>
		
		<!-- 功能导航 -->
		<view class="nav-section">
			<text class="section-title">主要功能</text>
			<view class="nav-grid">
				<view class="nav-item" @click="navigateTo('/pages/grades/grades')">
					<view class="nav-icon grades-icon">
						<text class="icon-text">📊</text>
					</view>
					<text class="nav-title">成绩查询</text>
					<text class="nav-desc">查看个人成绩单</text>
				</view>
				
				<view class="nav-item" @click="navigateTo('/pages/schedule/schedule')">
					<view class="nav-icon schedule-icon">
						<text class="icon-text">📅</text>
					</view>
					<text class="nav-title">课表查询</text>
					<text class="nav-desc">查看本周课程安排</text>
				</view>
				
				<view class="nav-item" @click="navigateTo('/pages/stats/stats')">
					<view class="nav-icon stats-icon">
						<text class="icon-text">📈</text>
					</view>
					<text class="nav-title">数据分析</text>
					<text class="nav-desc">成绩分析与排名</text>
				</view>
				
				<view class="nav-item" @click="showFeature('course-quota')">
					<view class="nav-icon quota-icon">
						<text class="icon-text">📋</text>
					</view>
					<text class="nav-title">课余量查询</text>
					<text class="nav-desc">查看课程剩余名额</text>
				</view>
			</view>
		</view>
		
		<!-- 底部操作 -->
		<view class="bottom-actions">
			<button class="logout-btn" @click="logout">退出登录</button>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			userInfo: {
				name: '张三',
				class: '计算机科学与技术2021级1班',
				studentId: 'test2024'
			},
			stats: {
				gpa: '3.8',
				avgScore: '85.6',
				totalCredits: '128'
			}
		}
	},
	onLoad() {
		this.checkAuth();
		this.loadUserInfo();
		this.loadStats();
	},
	onShow() {
		// 页面显示时刷新数据
		this.loadStats();
	},
	methods: {
		checkAuth() {
			const token = uni.getStorageSync('access_token');
			if (!token) {
				uni.redirectTo({
					url: '/pages/login/login'
				});
				return;
			}
		},
		
		loadUserInfo() {
			const userInfo = uni.getStorageSync('user_info');
			if (userInfo) {
				this.userInfo = {
					...userInfo,
					// 确保用户名存在，避免图片路径错误
					name: userInfo.name || '用户'
				};
			}
		},
		
		loadStats() {
			// 模拟加载统计数据
			setTimeout(() => {
				this.stats = {
					gpa: '3.85',
					avgScore: '86.2',
					totalCredits: '132'
				};
			}, 500);
		},
		
		navigateTo(url) {
			uni.navigateTo({
				url: url
			});
		},
		
		showFeature(feature) {
			uni.showToast({
				title: '功能开发中',
				icon: 'none'
			});
		},
		
		getAvatarText() {
			// 安全获取用户名首字符，避免图片路径错误
			try {
				const name = this.userInfo.name || '用户';
				if (name && typeof name === 'string' && name.length > 0) {
					return name.charAt(0).toUpperCase();
				}
				return 'U';
			} catch (error) {
				console.log('获取头像字符出错:', error);
				return 'U';
			}
		},
		
		logout() {
			uni.showModal({
				title: '确认退出',
				content: '确定要退出登录吗？',
				success: (res) => {
					if (res.confirm) {
						uni.removeStorageSync('access_token');
						uni.removeStorageSync('user_info');
						uni.redirectTo({
							url: '/pages/login/login'
						});
					}
				}
			});
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

.user-card {
	background: linear-gradient(135deg, #9B0400 0%, #B91C1C 100%);
	border-radius: 16rpx;
	padding: 32rpx;
	margin-bottom: 32rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
	box-shadow: 0 4rpx 16rpx rgba(155, 4, 0, 0.2);
}

.user-info {
	flex: 1;
}

.user-name {
	font-size: 36rpx;
	font-weight: 600;
	color: #FFFFFF;
	display: block;
	margin-bottom: 8rpx;
}

.user-class {
	font-size: 26rpx;
	color: rgba(255, 255, 255, 0.9);
	display: block;
	margin-bottom: 8rpx;
}

.user-id {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
	display: block;
}

.user-avatar {
	width: 80rpx;
	height: 80rpx;
	background: rgba(255, 255, 255, 0.2);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
}

.avatar-text {
	font-size: 32rpx;
	font-weight: 600;
	color: #FFFFFF;
}

.stats-section {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 32rpx;
	margin-bottom: 32rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.section-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #374151;
	display: block;
	margin-bottom: 24rpx;
}

.stats-grid {
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

.nav-section {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 32rpx;
	margin-bottom: 32rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.nav-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 24rpx;
}

.nav-item {
	background: #F8F9FA;
	border-radius: 12rpx;
	padding: 32rpx 24rpx;
	text-align: center;
	border: 2rpx solid transparent;
	transition: all 0.3s ease;
}

.nav-item:active {
	background: rgba(155, 4, 0, 0.05);
	border-color: #9B0400;
	transform: scale(0.98);
}

.nav-icon {
	width: 64rpx;
	height: 64rpx;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	margin: 0 auto 16rpx;
	background: rgba(155, 4, 0, 0.1);
}

.icon-text {
	font-size: 32rpx;
}

.nav-title {
	font-size: 28rpx;
	font-weight: 600;
	color: #374151;
	display: block;
	margin-bottom: 8rpx;
}

.nav-desc {
	font-size: 22rpx;
	color: #6B7280;
	display: block;
}

.bottom-actions {
	display: flex;
	justify-content: center;
	margin-top: 48rpx;
	margin-bottom: 32rpx;
}

.logout-btn {
	background: transparent;
	color: #6B7280;
	border: 2rpx solid #E5E7EB;
	border-radius: 8rpx;
	padding: 24rpx 48rpx;
	font-size: 28rpx;
}

.logout-btn:active {
	background: #F8F9FA;
	border-color: #D1D5DB;
}
</style>
