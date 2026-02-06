<script>
	export default {
		onLaunch: function() {
			// console.log('App Launch')
			
			// 检查登录状态
			try {
				const userInfo = uni.getStorageSync('userInfo');
				// console.log('App Launch - 检查用户信息:', userInfo);
				
				if (!userInfo) {
					// console.log('用户未登录，即将跳转至登录页');
					uni.reLaunch({
						url: '/pages/login/login',
						success: () => {
							// console.log('跳转登录页成功');
						},
						fail: (err) => {
							console.error('跳转登录页失败:', err);
						}
					});
				} else {
					// console.log('用户已登录');
				}
			} catch (e) {
				console.error('读取缓存失败:', e);
				// 出错时也建议跳转登录作为兜底
				uni.reLaunch({ url: '/pages/login/login' });
			}
		},
		onShow: function() {
			// console.log('App Show')
		},
		onHide: function() {
			// console.log('App Hide')
		}
	}
</script>

<style>
	/*每个页面公共css */
</style>
