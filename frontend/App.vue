<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style lang="scss">
	/*每个页面公共css */
	
	/* 引入自定义主题变量 */
	@import "./uni.scss";
	
	/* 全局重置样式 */
	page {
		background-color: $uni-bg-color-grey;
		font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', SimSun, sans-serif;
		line-height: 1.6;
	}
	
	/* 通用组件样式 */
	.btn-primary {
		background: $brand-primary !important;
		color: $uni-text-color-inverse !important;
		border: none !important;
		border-radius: 8rpx !important;
		font-weight: 600 !important;
	}
	
	.btn-primary:active {
		background: $brand-primary-dark !important;
	}
	
	.btn-secondary {
		background: transparent !important;
		color: $brand-primary !important;
		border: 2rpx solid $brand-primary !important;
		border-radius: 8rpx !important;
		font-weight: 600 !important;
	}
	
	.btn-secondary:active {
		background: rgba(155, 4, 0, 0.1) !important;
	}
	
	.card {
		background: $uni-bg-color !important;
		border-radius: 12rpx !important;
		border: 1rpx solid $uni-border-color !important;
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05) !important;
	}
	
	.text-primary {
		color: $brand-primary !important;
	}
	
	.text-secondary {
		color: $uni-text-color-grey !important;
	}
	
	.text-success {
		color: $uni-color-success !important;
	}
	
	.text-warning {
		color: $uni-color-warning !important;
	}
	
	.text-error {
		color: $uni-color-error !important;
	}
	
	/* 加载状态 */
	.loading {
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 60rpx 0;
	}
	
	/* 空状态 */
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 80rpx 32rpx;
		text-align: center;
	}
	
	.empty-icon {
		font-size: 120rpx;
		color: #E5E7EB;
		margin-bottom: 24rpx;
	}
	
	.empty-text {
		font-size: 28rpx;
		color: $uni-text-color-grey;
	}
	
	/* 通用间距 */
	.mt-xs { margin-top: 8rpx !important; }
	.mt-sm { margin-top: 16rpx !important; }
	.mt-md { margin-top: 24rpx !important; }
	.mt-lg { margin-top: 32rpx !important; }
	.mt-xl { margin-top: 48rpx !important; }
	
	.mb-xs { margin-bottom: 8rpx !important; }
	.mb-sm { margin-bottom: 16rpx !important; }
	.mb-md { margin-bottom: 24rpx !important; }
	.mb-lg { margin-bottom: 32rpx !important; }
	.mb-xl { margin-bottom: 48rpx !important; }
	
	.mx-xs { margin-left: 8rpx !important; margin-right: 8rpx !important; }
	.mx-sm { margin-left: 16rpx !important; margin-right: 16rpx !important; }
	.mx-md { margin-left: 24rpx !important; margin-right: 24rpx !important; }
	.mx-lg { margin-left: 32rpx !important; margin-right: 32rpx !important; }
	.mx-xl { margin-left: 48rpx !important; margin-right: 48rpx !important; }
	
	.p-xs { padding: 8rpx !important; }
	.p-sm { padding: 16rpx !important; }
	.p-md { padding: 24rpx !important; }
	.p-lg { padding: 32rpx !important; }
	.p-xl { padding: 48rpx !important; }
	
	/* 文字对齐 */
	.text-left { text-align: left !important; }
	.text-center { text-align: center !important; }
	.text-right { text-align: right !important; }
	
	/* Flex布局 */
	.flex { display: flex !important; }
	.flex-column { flex-direction: column !important; }
	.flex-center { 
		display: flex !important; 
		align-items: center !important; 
		justify-content: center !important; 
	}
	.flex-between { 
		display: flex !important; 
		justify-content: space-between !important; 
		align-items: center !important; 
	}
	.flex-1 { flex: 1 !important; }
</style>
