<template>
  <view class="webview-page">
    <web-view v-if="targetUrl" :src="targetUrl" @error="handleError"></web-view>
    <view v-else class="empty-state">
      <text class="empty-text">链接地址无效</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';

const targetUrl = ref('');

const copyLink = () => {
  if (!targetUrl.value) return;
  uni.setClipboardData({
    data: targetUrl.value,
    success: () => {
      uni.showToast({
        title: '链接已复制',
        icon: 'none'
      });
    }
  });
};

const handleError = () => {
  uni.showModal({
    title: '打开失败',
    content: '请确认该链接已配置到微信小程序业务域名，或稍后重试。',
    confirmText: '复制链接',
    cancelText: '关闭',
    success: (res) => {
      if (res.confirm) {
        copyLink();
      }
    }
  });
};

onLoad((options) => {
  const url = options?.url ? decodeURIComponent(options.url) : '';
  if (/^https?:\/\//i.test(url)) {
    targetUrl.value = url;
    return;
  }

  uni.showToast({
    title: '链接无效',
    icon: 'none'
  });
});
</script>

<style scoped>
.webview-page {
  min-height: 100vh;
  background: #fff;
}

.empty-state {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-text {
  font-size: 28rpx;
  color: #666;
}
</style>
