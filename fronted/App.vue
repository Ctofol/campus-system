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
			// 路由由首页 pages/entry/entry 统一处理；勿在 onLaunch 再 reLaunch，
			// 否则与 entry 同时跳转易报 appLaunch with non-empty page stack
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
	/* 每个页面公共 css */
	/* 链接「查看更多」：勿在模板 text 里写半角 >，否则微信端可能显示为 &gt; */
	.link-more {
		display: inline-flex;
		align-items: center;
		gap: 6rpx;
	}
	.link-arrow {
		width: 14rpx;
		height: 14rpx;
		border-top: 3rpx solid currentColor;
		border-right: 3rpx solid currentColor;
		transform: rotate(45deg);
		flex-shrink: 0;
	}
</style>
