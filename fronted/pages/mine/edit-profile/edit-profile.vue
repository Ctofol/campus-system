<template>
  <view class="edit-profile-page">
    <view class="form-section">
      <!-- 头像 -->
      <view class="form-item" @click="chooseAvatar">
        <text class="label">头像</text>
        <view class="avatar-preview">
          <image :src="avatarUrl" mode="aspectFill" class="avatar-img" />
          <text class="change-text">点击更换</text>
        </view>
        <text class="arrow">›</text>
      </view>
      
      <!-- 昵称 -->
      <view class="form-item">
        <text class="label">昵称</text>
        <input 
          v-model="formData.name" 
          class="input" 
          placeholder="请输入昵称"
          maxlength="20"
        />
      </view>
      
      <!-- 个性签名 -->
      <view class="form-item signature-item">
        <text class="label">个性签名</text>
        <textarea 
          v-model="formData.signature" 
          class="textarea" 
          placeholder="写点什么吧~"
          maxlength="100"
        />
      </view>
      
      <!-- 学号（只读） -->
      <view class="form-item">
        <text class="label">学号</text>
        <text class="value readonly">{{ formData.student_id || '未设置' }}</text>
      </view>
      
      <!-- 班级（只读） -->
      <view class="form-item">
        <text class="label">班级</text>
        <text class="value readonly">{{ formData.class_name || '未分配' }}</text>
      </view>
    </view>
    
    <!-- 保存按钮 -->
    <view class="button-section">
      <button class="save-btn" @click="handleSave" :loading="saving">保存</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { request, uploadFile, BASE_URL } from '@/utils/request.js';

const avatarUrl = ref('/static/avatar.png');
const saving = ref(false);

const formData = ref({
  name: '',
  signature: '',
  student_id: '',
  class_name: '',
  avatar_url: ''
});

onMounted(() => {
  loadUserProfile();
});

const loadUserProfile = async () => {
  try {
    const res = await request({
      url: '/users/profile',
      method: 'GET'
    });
    
    if (res) {
      formData.value = {
        name: res.name || '',
        signature: res.signature || '',
        student_id: res.student_id || '',
        class_name: res.class_name || '',
        avatar_url: res.avatar_url || ''
      };
      
      if (res.avatar_url) {
        avatarUrl.value = res.avatar_url.startsWith('http') 
          ? res.avatar_url 
          : `${BASE_URL}${res.avatar_url}`;
      }
    }
  } catch (e) {
    console.error('Failed to load profile:', e);
    uni.showToast({ title: '加载失败', icon: 'none' });
  }
};

const chooseAvatar = () => {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const tempFilePath = res.tempFilePaths[0];
      
      try {
        uni.showLoading({ title: '上传中...' });
        
        const uploadResult = await uploadFile(tempFilePath, 'image');
        
        formData.value.avatar_url = uploadResult.url;
        avatarUrl.value = uploadResult.url.startsWith('http') 
          ? uploadResult.url 
          : `${BASE_URL}${uploadResult.url}`;
        
        uni.hideLoading();
        uni.showToast({ title: '上传成功', icon: 'success' });
      } catch (e) {
        uni.hideLoading();
        console.error('Upload failed:', e);
        uni.showToast({ title: '上传失败', icon: 'none' });
      }
    }
  });
};

const handleSave = async () => {
  if (!formData.value.name) {
    uni.showToast({ title: '请输入昵称', icon: 'none' });
    return;
  }
  
  saving.value = true;
  
  try {
    await request({
      url: '/users/profile',
      method: 'PUT',
      data: {
        name: formData.value.name,
        signature: formData.value.signature,
        avatar_url: formData.value.avatar_url
      }
    });
    
    // 更新本地存储
    let userInfo = uni.getStorageSync('userInfo');
    if (typeof userInfo === 'string') {
      try {
        userInfo = JSON.parse(userInfo);
      } catch (e) {
        userInfo = {};
      }
    }
    
    userInfo = {
      ...userInfo,
      name: formData.value.name,
      signature: formData.value.signature,
      avatar_url: formData.value.avatar_url
    };
    
    uni.setStorageSync('userInfo', userInfo);
    
    uni.showToast({ title: '保存成功', icon: 'success' });
    
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  } catch (e) {
    console.error('Save failed:', e);
    uni.showToast({ title: '保存失败', icon: 'none' });
  } finally {
    saving.value = false;
  }
};
</script>

<style scoped>
.edit-profile-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 30rpx;
}

.form-section {
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  margin-bottom: 30rpx;
}

.form-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.form-item:last-child {
  border-bottom: none;
}

.signature-item {
  align-items: flex-start;
}

.label {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
  width: 150rpx;
  flex-shrink: 0;
}

.input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
  text-align: right;
}

.textarea {
  flex: 1;
  font-size: 28rpx;
  color: #333;
  min-height: 120rpx;
  padding: 10rpx;
  background: #f8f9fa;
  border-radius: 8rpx;
}

.value {
  flex: 1;
  font-size: 28rpx;
  color: #333;
  text-align: right;
}

.readonly {
  color: #999;
}

.avatar-preview {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 20rpx;
}

.avatar-img {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  border: 2rpx solid #f0f0f0;
}

.change-text {
  font-size: 24rpx;
  color: #20C997;
}

.arrow {
  font-size: 32rpx;
  color: #ddd;
  margin-left: 10rpx;
}

.button-section {
  padding: 0 30rpx;
}

.save-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #20C997, #17a589);
  color: #fff;
  border-radius: 44rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
  box-shadow: 0 8rpx 24rpx rgba(32, 201, 151, 0.3);
}

.save-btn:active {
  opacity: 0.8;
}
</style>
