<template>
  <view class="mine-container">
    <!-- 自定义导航栏 -->
    <view class="custom-nav-bar">
      <view class="nav-status-bar"></view>
      <view class="nav-content">
        <text class="nav-title">个人中心</text>
      </view>
    </view>

    <view class="content-wrapper">
      <view class="user-card">
      <view class="avatar">👮‍♂️</view>
      <view class="info">
        <text class="name">{{ userInfo.name || '教官' }}</text>
        <text class="role">体能教研室</text>
      </view>
    </view>
    
    <view class="menu-list">
      <view class="menu-item" @click="uni.showToast({title: '设置功能开发中', icon:'none'})">
        <text>个人信息设置</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="uni.showToast({title: '安全中心开发中', icon:'none'})">
        <text>账号安全</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="uni.showToast({title: '暂无新通知', icon:'none'})">
        <text>系统通知</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="uni.showToast({title: '请联系管理员', icon:'none'})">
        <text>帮助与反馈</text>
        <text class="arrow">></text>
      </view>
    </view>
    
    <button class="logout-btn" @click="handleLogout">退出登录</button>
    
    <view style="height: 20rpx;"></view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';

const userInfo = ref({});

onShow(() => {
  // 隐藏左上角 Home 按钮，防止跳转到学生端主页
  uni.hideHomeButton && uni.hideHomeButton();

  const storedUser = uni.getStorageSync('userInfo');
  if (storedUser) {
    try {
        userInfo.value = typeof storedUser === 'string' ? JSON.parse(storedUser) : storedUser;
    } catch (e) {
        userInfo.value = {};
    }
  }
});

const handleLogout = () => {
  uni.removeStorageSync('userInfo');
  uni.removeStorageSync('userRole');
  uni.reLaunch({
    url: '/pages/login/login'
  });
};
</script>

<style scoped>
.mine-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

/* 自定义导航栏 */
.custom-nav-bar {
  background: #fff;
  width: 100%;
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid #eee;
}
.nav-status-bar {
  height: var(--status-bar-height);
  width: 100%;
}
.nav-content {
  height: 44px; /* 标准导航栏高度 */
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.nav-title {
  color: #333;
  font-size: 32rpx;
  font-weight: bold;
}

.content-wrapper {
  padding: 30rpx;
  flex: 1;
}

.user-card {
  background: #20C997;
  border-radius: 20rpx;
  padding: 50rpx 40rpx;
  display: flex;
  align-items: center;
  color: #fff;
  margin-bottom: 40rpx;
}
.avatar {
  width: 120rpx;
  height: 120rpx;
  background: rgba(255,255,255,0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 60rpx;
  margin-right: 30rpx;
}
.info {
  display: flex;
  flex-direction: column;
}
.name {
  font-size: 36rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
}
.role {
  font-size: 24rpx;
  opacity: 0.9;
}
.menu-list {
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  margin-bottom: 60rpx;
}
.menu-item {
  padding: 30rpx 40rpx;
  border-bottom: 1px solid #f5f5f5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 30rpx;
  color: #333;
}
.menu-item:last-child {
  border-bottom: none;
}
.arrow {
  color: #ccc;
}
.logout-btn {
  background: #fff;
  color: #ff6b6b;
  font-size: 30rpx;
  border-radius: 20rpx;
}
</style>