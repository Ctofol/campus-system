<template>
  <view class="change-password-page">
    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="nav-back" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="nav-title">修改密码</text>
    </view>

    <view class="content">
      <view class="form-card">
        <!-- 原密码 -->
        <view class="form-item">
          <text class="label">原密码</text>
          <input 
            class="input" 
            v-model="formData.oldPassword" 
            placeholder="请输入原密码"
            password
          />
        </view>

        <!-- 新密码 -->
        <view class="form-item">
          <text class="label">新密码</text>
          <input 
            class="input" 
            v-model="formData.newPassword" 
            placeholder="请输入新密码（6-20位）"
            password
          />
        </view>

        <!-- 确认新密码 -->
        <view class="form-item">
          <text class="label">确认新密码</text>
          <input 
            class="input" 
            v-model="formData.confirmPassword" 
            placeholder="请再次输入新密码"
            password
          />
        </view>

        <button class="submit-btn" @click="submitChange">确认修改</button>
      </view>

      <view class="tips-card">
        <text class="tips-title">密码要求：</text>
        <text class="tips-item">• 长度为6-20位</text>
        <text class="tips-item">• 建议包含字母和数字</text>
        <text class="tips-item">• 不要使用过于简单的密码</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { request } from '@/utils/request.js';

const formData = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const submitChange = async () => {
  // 验证
  if (!formData.value.oldPassword) {
    uni.showToast({ title: '请输入原密码', icon: 'none' });
    return;
  }
  if (!formData.value.newPassword) {
    uni.showToast({ title: '请输入新密码', icon: 'none' });
    return;
  }
  if (formData.value.newPassword.length < 6 || formData.value.newPassword.length > 20) {
    uni.showToast({ title: '密码长度为6-20位', icon: 'none' });
    return;
  }
  if (formData.value.newPassword !== formData.value.confirmPassword) {
    uni.showToast({ title: '两次密码输入不一致', icon: 'none' });
    return;
  }

  uni.showLoading({ title: '修改中...' });
  try {
    await request({
      url: '/users/change-password',
      method: 'POST',
      data: {
        old_password: formData.value.oldPassword,
        new_password: formData.value.newPassword
      }
    });

    uni.hideLoading();
    uni.showModal({
      title: '修改成功',
      content: '密码已修改，请重新登录',
      showCancel: false,
      success: () => {
        // 清除登录信息
        uni.removeStorageSync('token');
        uni.removeStorageSync('userInfo');
        uni.removeStorageSync('userRole');
        uni.reLaunch({ url: '/pages/login/login' });
      }
    });
  } catch (e) {
    uni.hideLoading();
    console.error('Change password failed:', e);
    const errorMsg = e.data?.detail || '修改失败，请检查原密码是否正确';
    uni.showToast({ title: errorMsg, icon: 'none' });
  }
};

const goBack = () => {
  uni.navigateBack();
};
</script>

<style scoped>
.change-password-page {
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

.form-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.form-item {
  margin-bottom: 30rpx;
}

.form-item:last-of-type {
  margin-bottom: 40rpx;
}

.label {
  font-size: 28rpx;
  color: #666;
  display: block;
  margin-bottom: 16rpx;
}

.input {
  width: 100%;
  height: 80rpx;
  border: 1px solid #e0e0e0;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
}

.submit-btn {
  width: 100%;
  height: 88rpx;
  background: #20C997;
  color: #fff;
  border-radius: 12rpx;
  font-size: 30rpx;
  border: none;
}

.tips-card {
  background: #fff9e6;
  border-radius: 16rpx;
  padding: 30rpx;
  border-left: 4rpx solid #ff9800;
}

.tips-title {
  font-size: 28rpx;
  color: #333;
  font-weight: bold;
  display: block;
  margin-bottom: 16rpx;
}

.tips-item {
  font-size: 26rpx;
  color: #666;
  display: block;
  margin-bottom: 8rpx;
  line-height: 1.6;
}
</style>
