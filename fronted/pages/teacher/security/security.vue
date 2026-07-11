<template>
  <view class="security-page">
    <page-tab-header title="账号安全" show-back theme="white" />

    <view class="content page-tab-body">
      <!-- 修改密码 -->
      <view class="menu-item" @click="changePassword">
        <view class="item-left">
          <image class="item-icon" src="/static/叉号图标.png" mode="aspectFit" />
          <text class="item-text">修改密码</text>
        </view>
        <text class="arrow">→</text>
      </view>

      <!-- 绑定手机号 -->
      <view class="menu-item" @click="bindPhone">
        <view class="item-left">
          <image class="item-icon" src="/static/主页GO图标.png" mode="aspectFit" />
          <text class="item-text">绑定手机号</text>
        </view>
        <view class="item-right">
          <text class="item-value">{{ phoneDisplay }}</text>
          <text class="arrow">→</text>
        </view>
      </view>

      <!-- 账号注销 -->
      <view class="menu-item danger" @click="deleteAccount">
        <view class="item-left">
          <image class="item-icon" src="/static/叉号图标.png" mode="aspectFit" />
          <text class="item-text">账号注销</text>
        </view>
        <text class="arrow">→</text>
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
  uni.navigateTo({
    url: '/pages/teacher/profile/edit'
  });
};

const deleteAccount = () => {
  uni.showModal({
    title: '账号注销',
    content: '账号注销需要管理员审核处理。\n\n请联系管理员：\n电话：138-0013-8000\n邮箱：admin@campus.edu.cn',
    showCancel: false,
    confirmText: '我知道了'
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

/* 顶栏已统一为 page-tab-header，以下旧样式保留为空避免引用报错 */

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
  width: 36rpx;
  height: 36rpx;
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
