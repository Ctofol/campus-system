<template>
  <view class="entry-container">
    <view class="loading-wrap">
      <text class="loading-text">正在进入...</text>
    </view>
  </view>
</template>

<script setup>
import { onLoad } from '@dcloudio/uni-app';

onLoad(() => {
  const token = uni.getStorageSync('token');
  const userRole = uni.getStorageSync('userRole');

  if (!token || !userRole) {
    uni.reLaunch({ url: '/pages/login/login' });
    return;
  }

  if (userRole === 'admin') {
    uni.reLaunch({ url: '/pages/admin/dashboard/index' });
  } else {
    uni.reLaunch({ url: '/pages/tab/home' });
  }
});
</script>

<style scoped>
.entry-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.loading-wrap {
  text-align: center;
}
.loading-text {
  font-size: 14px;
  color: #999;
}
</style>
