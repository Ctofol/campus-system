<template>
  <view class="security-page">
    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="nav-back" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="nav-title">账号安全</text>
    </view>

    <view class="content">
      <!-- 修改密码 -->
      <view class="menu-item" @click="changePassword">
        <view class="item-left">
          <text class="item-icon">🔒</text>
          <text class="item-text">修改密码</text>
        </view>
        <text class="arrow">></text>
      </view>

      <!-- 绑定手机号 -->
      <view class="menu-item" @click="bindPhone">
        <view class="item-left">
          <text class="item-icon">📱</text>
          <text class="item-text">绑定手机号</text>
        </view>
        <view class="item-right">
          <text class="item-value">{{ phoneDisplay }}</text>
          <text class="arrow">></text>
        </view>
      </view>

      <!-- 账号注销 -->
      <view class="menu-item danger" @click="deleteAccount">
        <view class="item-left">
          <text class="item-icon">⚠️</text>
          <text class="item-text">账号注销</text>
        </view>
        <text class="arrow">></text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { request } from '@/utils/request.js';

const userPhone = ref('');

const phoneDisplay = computed(() => {
  if (!userPhone.value) return '未绑定';
  return userPhone.value.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
});

const loadUserInfo = () => {
  const userInfo = uni.getStorageSync('userInfo');
  if (userInfo) {
    const user = typeof userInfo === 'string' ? JSON.parse(userInfo) : userInfo;
    userPhone.value = user.phone || '';
  }
};

const changePassword = () => {
  uni.navigateTo({
    url: '/pages/teacher/security/change-password'
  });
};

const bindPhone = () => {
  uni.showToast({ title: '手机号绑定功能开发中', icon: 'none' });
};

const deleteAccount = () => {
  uni.showModal({
    title: '账号注销',
    content: '注销后将无法恢复，所有数据将被清除。\n\n确认要注销账号吗？',
    confirmText: '确认注销',
    confirmColor: '#ff4d4f',
    success: (res) => {
      if (res.confirm) {
        uni.showModal({
          title: '二次确认',
          content: '这是最后一次确认，注销后无法恢复！',
          confirmText: '我确定',
          confirmColor: '#ff4d4f',
          success: async (res2) => {
            if (res2.confirm) {
              // TODO: 调用注销API
              uni.showToast({ title: '账号注销功能开发中', icon: 'none' });
            }
          }
        });
      }
    }
  });
};

const goBack = () => {
  uni.navigateBack();
};

onMounted(() => {
  loadUserInfo();
});
</script>

<style scoped>
.security-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.nav-bar {
  background: #fff;
  height: 88rpx;
  display: flex;
  align-items: center;
  padding: 0 30rpx;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}

.nav-back {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.back-icon {
  font-size: 40rpx;
  color: #333;
}

.nav-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.content {
  padding: 30rpx;
}

.menu-item {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.menu-item.danger .item-text {
  color: #ff4d4f;
}

.item-left {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.item-icon {
  font-size: 36rpx;
}

.item-text {
  font-size: 30rpx;
  color: #333;
}

.item-right {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.item-value {
  font-size: 26rpx;
  color: #999;
}

.arrow {
  color: #ccc;
  font-size: 28rpx;
}
</style>
