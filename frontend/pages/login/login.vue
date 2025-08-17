<template>
	<view class="login-container">
		<view class="header">
			<view class="logo-container">
				<image 
					class="logo" 
					src="../../static/logo.png" 
					mode="aspectFit"
					@error="onLogoError"
					v-if="showLogo"
				></image>
				<view v-else class="logo-fallback">
					<text class="logo-text">📚</text>
				</view>
			</view>
			<text class="app-title">Easy-QFNUJW</text>
			<text class="app-subtitle">曲阜师范大学教务辅助工具</text>
			<text class="disclaimer">非官方应用</text>
		</view>
		
		<view class="form-container">
			<view class="input-group">
				<text class="label">学号</text>
				<input 
					class="input" 
					type="text" 
					v-model="studentId" 
					placeholder="请输入学号"
					:disabled="isLoading"
				/>
			</view>
			
			<view class="input-group">
				<text class="label">密码</text>
				<input 
					class="input" 
					type="password" 
					v-model="password" 
					placeholder="请输入教务系统密码"
					:disabled="isLoading"
				/>
			</view>
			
			<view class="test-account-section">
				<text class="test-label">测试账号</text>
				<view class="test-buttons">
					<button class="test-btn" @click="useTestAccount">使用测试账号</button>
				</view>
			</view>
			
			<button 
				class="login-btn" 
				:class="{ 'login-btn-disabled': isLoading }"
				@click="login"
				:disabled="isLoading"
			>
				<text v-if="!isLoading">登录</text>
				<text v-else>登录中...</text>
			</button>
		</view>
		
		<view class="footer">
			<text class="privacy-text">登录即表示同意</text>
			<text class="privacy-link">《用户协议》</text>
			<text class="privacy-text">和</text>
			<text class="privacy-link">《隐私政策》</text>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			studentId: '',
			password: '',
			isLoading: false,
			showLogo: true
		}
	},
	onLoad() {
		// 检查是否已登录
		const token = uni.getStorageSync('access_token');
		if (token) {
			uni.redirectTo({
				url: '/pages/index/index'
			});
		}
	},
	methods: {
		useTestAccount() {
			this.studentId = 'test2024';
			this.password = 'test123456';
			uni.showToast({
				title: '已填入测试账号',
				icon: 'success',
				duration: 1500
			});
		},
		
		async login() {
			if (!this.studentId || !this.password) {
				uni.showToast({
					title: '请填写完整信息',
					icon: 'none'
				});
				return;
			}
			
			this.isLoading = true;
			
			try {
				// 模拟登录API调用
				await this.mockLogin();
				
				uni.showToast({
					title: '登录成功',
					icon: 'success'
				});
				
				setTimeout(() => {
					uni.redirectTo({
						url: '/pages/index/index'
					});
				}, 1500);
				
			} catch (error) {
				uni.showToast({
					title: error.message || '登录失败',
					icon: 'none'
				});
			} finally {
				this.isLoading = false;
			}
		},
		
		mockLogin() {
			return new Promise((resolve, reject) => {
				setTimeout(() => {
					if (this.studentId === 'test2024' && this.password === 'test123456') {
						// 模拟保存token
						uni.setStorageSync('access_token', 'mock_jwt_token_123456');
						uni.setStorageSync('student_id', this.studentId);
						uni.setStorageSync('user_info', {
							studentId: this.studentId,
							name: '张三',
							class: '计算机科学与技术2021级1班'
						});
						resolve();
					} else {
						reject(new Error('学号或密码错误'));
					}
				}, 2000);
			});
		},
		
		onLogoError() {
			console.log('Logo图片加载失败，使用文字替代');
			this.showLogo = false;
		}
	}
}
</script>

<style lang="scss" scoped>
.login-container {
	min-height: 100vh;
	background: linear-gradient(135deg, #9B0400 0%, #7A0300 100%);
	display: flex;
	flex-direction: column;
	padding: 0 32rpx;
}

.header {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	margin-top: 100rpx;
	margin-bottom: 60rpx;
}

.logo-container {
	width: 120rpx;
	height: 120rpx;
	margin-bottom: 32rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.logo {
	width: 120rpx;
	height: 120rpx;
}

.logo-fallback {
	width: 120rpx;
	height: 120rpx;
	background: rgba(255, 255, 255, 0.2);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
}

.logo-text {
	font-size: 60rpx;
}

.app-title {
	font-size: 48rpx;
	font-weight: 600;
	color: #FFFFFF;
	margin-bottom: 16rpx;
}

.app-subtitle {
	font-size: 28rpx;
	color: rgba(255, 255, 255, 0.8);
	margin-bottom: 8rpx;
}

.disclaimer {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.6);
	background: rgba(255, 255, 255, 0.1);
	padding: 8rpx 16rpx;
	border-radius: 16rpx;
}

.form-container {
	background: #FFFFFF;
	border-radius: 24rpx;
	padding: 48rpx 32rpx;
	margin-bottom: 32rpx;
	box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
}

.input-group {
	margin-bottom: 32rpx;
}

.label {
	font-size: 28rpx;
	color: #374151;
	font-weight: 500;
	margin-bottom: 16rpx;
	display: block;
}

.input {
	width: 100%;
	height: 88rpx;
	background: #F8F9FA;
	border: 2rpx solid #E5E7EB;
	border-radius: 8rpx;
	padding: 0 24rpx;
	font-size: 28rpx;
	color: #374151;
	box-sizing: border-box;
}

.input:focus {
	border-color: #9B0400;
	background: #FFFFFF;
}

.test-account-section {
	margin-bottom: 32rpx;
	padding: 24rpx;
	background: #F8F9FA;
	border-radius: 12rpx;
	border: 1rpx solid #E5E7EB;
}

.test-label {
	font-size: 24rpx;
	color: #6B7280;
	margin-bottom: 16rpx;
	display: block;
}

.test-buttons {
	display: flex;
	justify-content: center;
}

.test-btn {
	background: rgba(155, 4, 0, 0.1);
	color: #9B0400;
	border: 2rpx solid #9B0400;
	border-radius: 8rpx;
	padding: 16rpx 32rpx;
	font-size: 24rpx;
	font-weight: 500;
}

.test-btn:active {
	background: rgba(155, 4, 0, 0.2);
}

.login-btn {
	width: 100%;
	height: 88rpx;
	background: #9B0400;
	color: #FFFFFF;
	border: none;
	border-radius: 8rpx;
	font-size: 32rpx;
	font-weight: 600;
	display: flex;
	align-items: center;
	justify-content: center;
}

.login-btn:active {
	background: #7A0300;
}

.login-btn-disabled {
	background: #6B7280 !important;
	color: rgba(255, 255, 255, 0.7) !important;
}

.footer {
	display: flex;
	justify-content: center;
	align-items: center;
	flex-wrap: wrap;
	margin-bottom: 32rpx;
}

.privacy-text {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.7);
}

.privacy-link {
	font-size: 24rpx;
	color: #FFFFFF;
	text-decoration: underline;
	margin: 0 8rpx;
}
</style>
