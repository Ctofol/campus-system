<template>
  <view class="edit-profile-page">
    <view class="form-section">
      <view class="form-item avatar-item">
        <text class="label">头像</text>
        <!-- #ifdef MP-WEIXIN -->
        <button
          class="avatar-trigger"
          open-type="chooseAvatar"
          @chooseavatar="handleChooseAvatar"
        >
          <view class="avatar-preview">
            <image :src="avatarUrl" mode="aspectFill" class="avatar-img" />
            <text class="change-text">点击更换</text>
          </view>
        </button>
        <!-- #endif -->
        <!-- #ifndef MP-WEIXIN -->
        <view class="avatar-preview" @click="chooseAvatar">
          <image :src="avatarUrl" mode="aspectFill" class="avatar-img" />
          <text class="change-text">点击更换</text>
        </view>
        <!-- #endif -->
        <text class="arrow">></text>
      </view>

      <view class="form-item">
        <text class="label">姓名</text>
        <input
          v-model="formData.name"
          class="input"
          placeholder="请输入姓名"
          maxlength="20"
        />
      </view>

      <view class="form-item">
        <text class="label">手机号</text>
        <input
          v-model="formData.phone"
          class="input"
          placeholder="请输入手机号"
          maxlength="11"
          type="number"
        />
      </view>

      <view class="form-item signature-item">
        <text class="label">个性签名</text>
        <textarea
          v-model="formData.signature"
          class="textarea"
          placeholder="写点什么吧"
          maxlength="100"
        />
      </view>

      <view class="form-item">
        <text class="label">学号</text>
        <text class="value readonly">{{ formData.student_id || '未设置' }}</text>
      </view>

      <view class="form-item">
        <text class="label">班级</text>
        <text class="value readonly">{{ formData.class_name || '未分配' }}</text>
      </view>
    </view>

    <view class="button-section">
      <button class="save-btn" @click="handleSave" :loading="saving">保存</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { request, uploadFile, resolveMediaUrl } from '@/utils/request.js';

const avatarUrl = ref('/static/avatar.png');
const saving = ref(false);

const formData = ref({
  name: '',
  phone: '',
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
        phone: res.phone || '',
        signature: res.signature || '',
        student_id: res.student_id || '',
        class_name: res.class_name || '',
        avatar_url: res.avatar_url || ''
      };

      if (res.avatar_url) {
        avatarUrl.value = resolveMediaUrl(res.avatar_url);
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
      await uploadAvatar(tempFilePath);
    }
  });
};

const uploadAvatar = async (filePath) => {
  if (!filePath) return;
  try {
    uni.showLoading({ title: '上传中...' });
    const uploadResult = await uploadFile(filePath, 'image');
    formData.value.avatar_url = uploadResult.url;
    avatarUrl.value = resolveMediaUrl(uploadResult.url);
    uni.hideLoading();
    uni.showToast({ title: '上传成功', icon: 'success' });
  } catch (e) {
    uni.hideLoading();
    console.error('Upload failed:', e);
    uni.showToast({ title: '上传失败', icon: 'none' });
  }
};

const handleChooseAvatar = async (event) => {
  const filePath = event?.detail?.avatarUrl;
  if (!filePath) return;
  await uploadAvatar(filePath);
};

const handleSave = async () => {
  const name = String(formData.value.name || '').trim();
  const phone = String(formData.value.phone || '').trim();

  if (!name) {
    uni.showToast({ title: '请输入姓名', icon: 'none' });
    return;
  }

  if (!phone) {
    uni.showToast({ title: '请输入手机号', icon: 'none' });
    return;
  }

  if (!/^1\\d{10}$/.test(phone)) {
    uni.showToast({ title: '手机号格式不正确', icon: 'none' });
    return;
  }

  saving.value = true;

  try {
    await request({
      url: '/users/profile',
      method: 'PUT',
      data: {
        name,
        phone,
        signature: formData.value.signature,
        avatar_url: formData.value.avatar_url
      }
    });

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
      name,
      phone,
      signature: formData.value.signature,
      avatar_url: formData.value.avatar_url
    };

    uni.setStorageSync('userInfo', userInfo);
    formData.value.name = name;
    formData.value.phone = phone;

    uni.showToast({ title: '保存成功', icon: 'success' });

    setTimeout(() => {
      uni.navigateBack();
    }, 1200);
  } catch (e) {
    console.error('Save failed:', e);
    uni.showToast({ title: e?.message || '保存失败', icon: 'none' });
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

.avatar-item {
  min-height: 160rpx;
}

.signature-item {
  align-items: flex-start;
}

.label {
  width: 150rpx;
  flex-shrink: 0;
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.input {
  flex: 1;
  min-width: 0;
  font-size: 28rpx;
  color: #333;
  text-align: right;
}

.textarea {
  flex: 1;
  min-height: 120rpx;
  padding: 18rpx 20rpx;
  border-radius: 12rpx;
  background: #f8f9fa;
  font-size: 28rpx;
  color: #333;
  box-sizing: border-box;
}

.value {
  flex: 1;
  min-width: 0;
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

.avatar-trigger {
  flex: 1;
  padding: 0;
  margin: 0;
  background: transparent;
  border: none;
  line-height: 1;
}

.avatar-trigger::after {
  border: none;
}

.avatar-img {
  width: 120rpx;
  height: 120rpx;
  border-radius: 60rpx;
  border: 2rpx solid #f0f0f0;
  background: #f5f5f5;
}

.change-text {
  font-size: 24rpx;
  color: #20c997;
}

.arrow {
  margin-left: 10rpx;
  font-size: 30rpx;
  color: #c7c7c7;
}

.button-section {
  padding: 0 30rpx;
}

.save-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #20c997, #17a589);
  color: #fff;
  border: none;
  border-radius: 44rpx;
  font-size: 32rpx;
  font-weight: 600;
  box-shadow: 0 8rpx 24rpx rgba(32, 201, 151, 0.24);
}

.save-btn:active {
  opacity: 0.86;
}
</style>
