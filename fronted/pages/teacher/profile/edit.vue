<template>
  <view class="edit-profile-page">
    <view class="form-section">
      <view class="form-item avatar-item">
        <view class="avatar-row">
          <text class="label">头像</text>
          <view class="avatar-preview" @click="chooseAvatar">
            <image :src="avatarUrl" mode="aspectFill" class="avatar-img" />
            <view class="change-copy">
              <text class="change-text">点击更换</text>
              <text class="change-sub">相册 / 拍照</text>
            </view>
          </view>
        </view>
      </view>

      <view class="form-item">
        <text class="label">姓名</text>
        <input v-model="formData.name" class="input" maxlength="20" placeholder="请输入姓名" />
      </view>

      <view class="form-item">
        <text class="label">手机号</text>
        <input v-model="formData.phone" class="input" type="number" maxlength="11" placeholder="请输入手机号" />
      </view>

      <view class="form-item signature-item">
        <text class="label">个性签名</text>
        <textarea v-model="formData.signature" class="textarea" maxlength="100" placeholder="写点什么吧" />
      </view>
    </view>

    <view class="button-section">
      <button class="save-btn" :loading="saving" @click="saveProfile">保存</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { request, uploadFile, resolveMediaUrl } from '@/utils/request.js';
import { pickAvatarFromAlbum } from '@/utils/avatar-picker.js';

const avatarUrl = ref('/static/avatar.png');
const saving = ref(false);
const formData = ref({
  name: '',
  phone: '',
  signature: '',
  avatar_url: ''
});

const loadProfile = async () => {
  try {
    const res = await request({
      url: '/users/profile',
      method: 'GET'
    });

    if (!res) return;
    formData.value = {
      name: res.name || '',
      phone: res.phone || '',
      signature: res.signature || '',
      avatar_url: res.avatar_url || ''
    };
    avatarUrl.value = res.avatar_url ? resolveMediaUrl(res.avatar_url) : '/static/avatar.png';
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' });
  }
};

const uploadAvatar = async (filePath) => {
  if (!filePath) return;
  try {
    uni.showLoading({ title: '上传中...' });
    const uploadResult = await uploadFile(filePath, 'image');
    formData.value.avatar_url = uploadResult.url;
    avatarUrl.value = resolveMediaUrl(uploadResult.url);
  } catch (e) {
    uni.showToast({ title: '上传失败', icon: 'none' });
  } finally {
    uni.hideLoading();
  }
};

const chooseAvatar = async () => {
  try {
    const filePath = await pickAvatarFromAlbum();
    await uploadAvatar(filePath);
  } catch (e) {
    // 已在 pickAvatarFromAlbum 内提示隐私配置
  }
};

const saveProfile = async () => {
  const name = String(formData.value.name || '').trim();
  const phone = String(formData.value.phone || '').trim();

  if (!name) {
    uni.showToast({ title: '请输入姓名', icon: 'none' });
    return;
  }

  if (!/^1\d{10}$/.test(phone)) {
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

    uni.showToast({ title: '保存成功', icon: 'success' });
    setTimeout(() => uni.navigateBack(), 1000);
  } catch (e) {
    uni.showToast({ title: e?.message || '保存失败', icon: 'none' });
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  loadProfile();
});
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
  flex-direction: column;
  align-items: stretch;
  padding-top: 28rpx;
  padding-bottom: 28rpx;
}

.avatar-row {
  display: flex;
  align-items: center;
}

.avatar-item .label {
  align-self: flex-start;
  padding-top: 36rpx;
}

.signature-item {
  align-items: flex-start;
}

.label {
  width: 160rpx;
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

.avatar-preview {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 24rpx;
  padding-right: 200rpx;
  box-sizing: border-box;
}

.change-copy {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6rpx;
}

.change-sub {
  font-size: 22rpx;
  color: #999;
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
}
</style>
