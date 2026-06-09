<template>
  <view class="edit-page">
    <view class="form-section">
      <view class="form-item avatar-item">
        <text class="label">跑团头像</text>
        <view class="avatar-picker" @click="chooseAvatar">
          <image class="avatar-img" :src="avatarPreview" mode="aspectFill" />
          <text class="avatar-text">点击更换 · 可裁剪</text>
        </view>
      </view>

      <view class="form-item">
        <text class="label">跑团名称</text>
        <input v-model="formData.name" class="input" maxlength="20" placeholder="请输入跑团名称" />
      </view>

      <view class="form-item">
        <text class="label">跑团简介</text>
        <textarea
          v-model="formData.description"
          class="textarea"
          maxlength="200"
          placeholder="请输入跑团简介"
        />
      </view>
    </view>

    <view class="button-section">
      <button class="save-btn" :loading="saving" @click="handleSave">保存修改</button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { getMyRunGroups, updateRunGroup, uploadFile, resolveMediaUrl } from '@/utils/request.js';
import { pickAvatarFromAlbum } from '@/utils/avatar-picker.js';

const groupId = ref(0);
const saving = ref(false);
const avatarPreview = ref('/static/default-avatar.svg');
const formData = ref({
  name: '',
  description: '',
  avatar: ''
});

const loadGroup = async () => {
  try {
    const res = await getMyRunGroups();
    const groups = Array.isArray(res) ? res : [];
    const current = groups.find((item) => item.id === groupId.value);
    if (!current) {
      uni.showToast({ title: '未找到跑团', icon: 'none' });
      setTimeout(() => uni.navigateBack(), 1000);
      return;
    }

    formData.value = {
      name: current.name || '',
      description: current.description || '',
      avatar: current.avatar || ''
    };
    avatarPreview.value = current.avatar ? resolveMediaUrl(current.avatar) : '/static/default-avatar.svg';
  } catch (e) {
    uni.showToast({ title: e.message || '加载失败', icon: 'none' });
  }
};

const chooseAvatar = async () => {
  try {
    const filePath = await pickAvatarFromAlbum();
    uni.showLoading({ title: '上传中...' });
    const uploadResult = await uploadFile(filePath, 'image');
    formData.value.avatar = uploadResult.url;
    avatarPreview.value = resolveMediaUrl(uploadResult.url);
  } catch (e) {
    if (e?.cancelled) return;
    uni.showToast({ title: e?.message || '上传失败', icon: 'none' });
  } finally {
    uni.hideLoading();
  }
};

const handleSave = async () => {
  const payload = {
    name: String(formData.value.name || '').trim(),
    description: String(formData.value.description || '').trim(),
    avatar: formData.value.avatar || ''
  };

  if (!payload.name) {
    uni.showToast({ title: '请输入跑团名称', icon: 'none' });
    return;
  }

  saving.value = true;
  try {
    await updateRunGroup(groupId.value, payload);
    uni.showToast({ title: '保存成功', icon: 'success' });
    setTimeout(() => {
      uni.redirectTo({ url: `/pages/run-group/detail?groupId=${groupId.value}` });
    }, 900);
  } catch (e) {
    uni.showToast({ title: e.message || '保存失败', icon: 'none' });
  } finally {
    saving.value = false;
  }
};

onLoad((options) => {
  groupId.value = Number(options.groupId || 0);
  if (!groupId.value) {
    uni.showToast({ title: '参数错误', icon: 'none' });
    setTimeout(() => uni.navigateBack(), 1000);
    return;
  }
  loadGroup();
});
</script>

<style scoped>
.edit-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 30rpx;
}

.form-section {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.form-item + .form-item {
  margin-top: 28rpx;
}

.label {
  display: block;
  margin-bottom: 18rpx;
  font-size: 28rpx;
  color: #333;
  font-weight: 600;
}

.avatar-picker {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.avatar-img {
  width: 128rpx;
  height: 128rpx;
  border-radius: 64rpx;
  background: #f1f5f9;
  border: 2rpx solid #e2e8f0;
}

.avatar-text {
  font-size: 26rpx;
  color: #20c997;
}

.input,
.textarea {
  width: 100%;
  box-sizing: border-box;
  background: #f8fafc;
  border-radius: 14rpx;
  font-size: 28rpx;
  color: #333;
}

.input {
  height: 88rpx;
  padding: 0 24rpx;
}

.textarea {
  min-height: 220rpx;
  padding: 20rpx 24rpx;
}

.button-section {
  margin-top: 36rpx;
}

.save-btn {
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 44rpx;
  background: linear-gradient(135deg, #20c997, #17a589);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
}
</style>
