<template>
  <view class="edit-profile-page">
    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="nav-back" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="nav-title">个人信息设置</text>
      <view class="nav-action" @click="saveProfile">
        <text class="action-text">保存</text>
      </view>
    </view>

    <view class="content">
      <!-- 头像 -->
      <view class="form-item">
        <text class="label">头像</text>
        <view class="avatar-box" @click="chooseAvatar">
          <text class="avatar-emoji">{{ formData.avatar || '👮‍♂️' }}</text>
          <text class="change-hint">点击更换</text>
        </view>
      </view>

      <!-- 姓名 -->
      <view class="form-item">
        <text class="label">姓名</text>
        <input 
          class="input" 
          v-model="formData.name" 
          placeholder="请输入姓名"
        />
      </view>

      <!-- 手机号 -->
      <view class="form-item">
        <text class="label">手机号</text>
        <input 
          class="input" 
          v-model="formData.phone" 
          placeholder="请输入手机号"
          type="number"
          disabled
        />
        <text class="hint">手机号不可修改</text>
      </view>

      <!-- 所属部门 -->
      <view class="form-item">
        <text class="label">所属部门</text>
        <input 
          class="input" 
          v-model="formData.department" 
          placeholder="请输入所属部门"
        />
      </view>

      <!-- 个人签名 -->
      <view class="form-item">
        <text class="label">个人签名</text>
        <textarea 
          class="textarea" 
          v-model="formData.signature" 
          placeholder="请输入个人签名"
          maxlength="100"
        />
        <text class="char-count">{{ formData.signature.length }}/100</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { request } from '@/utils/request.js';

const formData = ref({
  avatar: '👮‍♂️',
  name: '',
  phone: '',
  department: '公共体育教研部',
  signature: ''
});

const loadProfile = () => {
  const userInfo = uni.getStorageSync('userInfo');
  if (userInfo) {
    const user = typeof userInfo === 'string' ? JSON.parse(userInfo) : userInfo;
    formData.value = {
      avatar: user.avatar || '👮‍♂️',
      name: user.name || '',
      phone: user.phone || '',
      department: user.department || '公共体育教研部',
      signature: user.signature || ''
    };
  }
};

const chooseAvatar = () => {
  const avatars = ['👮‍♂️', '👨‍🏫', '👩‍🏫', '🧑‍💼', '👨‍💼', '👩‍💼', '🧑‍🎓', '👨‍🎓', '👩‍🎓'];
  uni.showActionSheet({
    itemList: avatars,
    success: (res) => {
      formData.value.avatar = avatars[res.tapIndex];
    }
  });
};

const saveProfile = async () => {
  if (!formData.value.name) {
    uni.showToast({ title: '请输入姓名', icon: 'none' });
    return;
  }

  uni.showLoading({ title: '保存中...' });
  try {
    await request({
      url: '/users/profile',
      method: 'PUT',
      data: {
        name: formData.value.name,
        avatar: formData.value.avatar,
        department: formData.value.department,
        signature: formData.value.signature
      }
    });

    // 更新本地存储
    const userInfo = uni.getStorageSync('userInfo');
    const user = typeof userInfo === 'string' ? JSON.parse(userInfo) : userInfo;
    const updatedUser = { ...user, ...formData.value };
    uni.setStorageSync('userInfo', updatedUser);

    uni.hideLoading();
    uni.showToast({ title: '保存成功', icon: 'success' });
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  } catch (e) {
    uni.hideLoading();
    console.error('Save profile failed:', e);
    uni.showToast({ title: '保存失败', icon: 'none' });
  }
};

const goBack = () => {
  uni.navigateBack();
};

onMounted(() => {
  loadProfile();
});
</script>

<style scoped>
.edit-profile-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.nav-bar {
  background: #fff;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.nav-action {
  width: 80rpx;
  display: flex;
  justify-content: flex-end;
}

.action-text {
  font-size: 28rpx;
  color: #20C997;
}

.content {
  padding: 30rpx;
}

.form-item {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.label {
  font-size: 28rpx;
  color: #666;
  display: block;
  margin-bottom: 20rpx;
}

.avatar-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40rpx 0;
}

.avatar-emoji {
  font-size: 120rpx;
  margin-bottom: 20rpx;
}

.change-hint {
  font-size: 24rpx;
  color: #20C997;
}

.input {
  width: 100%;
  height: 80rpx;
  border: 1px solid #e0e0e0;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
}

.hint {
  font-size: 24rpx;
  color: #999;
  margin-top: 10rpx;
  display: block;
}

.textarea {
  width: 100%;
  min-height: 200rpx;
  border: 1px solid #e0e0e0;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 28rpx;
}

.char-count {
  font-size: 24rpx;
  color: #999;
  text-align: right;
  display: block;
  margin-top: 10rpx;
}
</style>
