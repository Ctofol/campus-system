<script>
	// #ifdef MP-WEIXIN
	import PrivacyPopup from '@/components/privacy-popup/privacy-popup.vue'
	// #endif

	export default {
		// #ifdef MP-WEIXIN
		components: {
			PrivacyPopup
		},
		// #endif
		onLaunch: function() {
			// #ifdef H5
			// H5 仅保留 admin：由入口页 pages/entry/entry 统一处理跳转（admin 登录/后台 或 登录页）
			// #endif
			// #ifndef H5
			// 小程序端：未登录则跳转登录
			try {
				const userInfo = uni.getStorageSync('userInfo');
				if (!userInfo) {
					uni.reLaunch({
						url: '/pages/login/login',
						fail: (err) => {
							console.error('跳转登录页失败:', err);
						}
					});
				}
			} catch (e) {
				console.error('读取缓存失败:', e);
				uni.reLaunch({ url: '/pages/login/login' });
			}
			// #endif
		},
		onShow: function() {
			// console.log('App Show')
		},
		onHide: function() {
			// console.log('App Hide')
		}
	}
</script>

<template>
	<!-- 微信小程序：隐私监听须早于任意页的 getLocation，避免真机定位静默失败、跑步里程为 0 -->
	<!-- #ifdef MP-WEIXIN -->
	<privacy-popup />
	<!-- #endif -->
</template>

<style>
	/*每个页面公共css */
</style>
