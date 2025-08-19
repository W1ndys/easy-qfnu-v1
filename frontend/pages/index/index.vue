<template>
	<view class="container">
		<image class="logo" src="/static/logo.png" mode="aspectFit"></image>
		
		<uni-forms class="login-form" :modelValue="formData">
			<uni-forms-item>
				<uni-easyinput 
					prefixIcon="person" 
					v-model="formData.studentId" 
					placeholder="请输入学号" 
				/>
			</uni-forms-item>
			<uni-forms-item>
				<uni-easyinput 
					prefixIcon="locked" 
					type="password" 
					v-model="formData.password" 
					placeholder="请输入教务系统密码"
				/>
			</uni-forms-item>
		</uni-forms>
		
		<button class="login-btn" @click="handleLogin" :loading="isLoading">
			登 录
		</button>
		
		<view class="footer-text">
			<text>本程序为第三方应用，非学校官方出品</text>
		</view>
	</view>
</template>

<script setup>
	import { ref } from 'vue';

	// 1. 使用 ref 创建“响应式”数据
	// 这等同于原生小程序里的 this.data
	// 当你修改 .value 时，template 里的界面会自动更新
	const formData = ref({
		studentId: '',
		password: ''
	});
	const isLoading = ref(false);

	// 2. 定义登录函数 (使用 async/await 语法，更现代)
	const handleLogin = async () => {
		// 简单的输入校验
		if (!formData.value.studentId || !formData.value.password) {
			uni.showToast({ title: '学号和密码不能为空', icon: 'none' });
			return;
		}

		isLoading.value = true; // 显示加载状态

		try {
			// 3. 使用 uni.request 发起网络请求
			const res = await uni.request({
				url: 'http://127.0.0.1:8000/api/v1/login', // 确保后端在运行
				method: 'POST',
				data: {
					student_id: formData.value.studentId,
					password: formData.value.password
				}
			});
			
			// uni.request 返回的是一个数组 [error, response]
			if (res.statusCode === 200 && res.data.access_token) {
				console.log("登录成功, Token:", res.data.access_token);
				uni.showToast({ title: '登录成功', icon: 'success' });
				uni.setStorageSync('token', res.data.access_token);

				// 延时后跳转
				setTimeout(() => {
					uni.reLaunch({
						url: '/pages/dashboard/dashboard' 
					});
				}, 1500);

			} else {
				// 处理后端返回的业务错误
				const errorMessage = res.data.detail || '学号或密码错误';
				uni.showToast({ title: errorMessage, icon: 'none' });
			}
			
		} catch (error) {
			// 处理网络层面的错误
			console.error("请求失败", error);
			uni.showToast({ title: '服务器连接失败', icon: 'none' });
		} finally {
			// 无论成功失败，都隐藏加载状态
			isLoading.value = false;
		}
	};
</script>

<style lang="scss" scoped>
.container {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	height: 100vh;
	padding: 0 40rpx;
	box-sizing: border-box;
}

.logo {
	width: 180rpx;
	height: 180rpx;
	margin-bottom: 80rpx;
}

.login-form {
	width: 100%;
	margin-bottom: 60rpx;
}

// uni-ui组件的深度样式修改
:deep(.uni-easyinput__content) {
	height: 100rpx;
	border-radius: 50rpx !important;
	background-color: #f7f7f7 !important;
	border: none !important;
}

.login-btn {
	width: 100%;
	height: 100rpx;
	line-height: 100rpx;
	border-radius: 50rpx;
	background-color: #07c160;
	color: #ffffff;
	font-size: 34rpx;
	font-weight: bold;
	// uni-app的按钮样式微调
	&::after {
		border: none;
	}
}

.footer-text {
	position: absolute;
	bottom: 40rpx;
	font-size: 24rpx;
	color: #aaa;
}
</style>