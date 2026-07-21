<template>
  <view class="page">
    <view class="header">
      <text class="title">人脸认证</text>
      <text class="subtitle">用于跑步起止照核验和体测本人校验</text>
    </view>

    <view class="status-panel">
      <view class="status-main">
        <text class="status-label">当前状态</text>
        <text class="status-value" :class="'status-' + profile.status">{{ statusText }}</text>
      </view>
      <text v-if="profile.fail_reason" class="error">{{ profile.fail_reason }}</text>
      <text v-if="profile.updated_at" class="meta">更新时间：{{ formatTime(profile.updated_at) }}</text>
    </view>

    <view class="photo-box" @tap="choosePhoto">
      <image v-if="previewUrl" class="photo" :src="previewUrl" mode="aspectFill" />
      <view v-else class="photo-empty">
        <text class="photo-plus">+</text>
        <text class="photo-tip">上传或拍摄本人正脸照</text>
      </view>
    </view>

    <view class="tips">
      <text>请确保画面内只有本人，光线充足，脸部完整清晰。</text>
      <text>系统会在本地模型中提取特征，不接入腾讯云识别服务。</text>
    </view>

    <button class="submit" :disabled="!localPath || submitting" @tap="submit">
      {{ submitting ? '认证中...' : '提交认证' }}
    </button>
  </view>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { getFaceProfile, submitFaceProfile, uploadFile, resolveMediaUrl } from '@/utils/request.js';

const profile = ref({ status: 'not_certified' });
const localPath = ref('');
const previewUrl = ref('');
const submitting = ref(false);

const statusText = computed(() => {
  const map = {
    not_certified: '未认证',
    pending: '待审核',
    verified: '已认证',
    failed: '认证失败',
    needs_reauth: '需重新认证'
  };
  return map[profile.value.status] || profile.value.status || '未认证';
});

const formatTime = (value) => {
  if (!value) return '';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
};

const loadProfile = async () => {
  try {
    const res = await getFaceProfile();
    profile.value = res || { status: 'not_certified' };
    if (res?.image_url) {
      previewUrl.value = resolveMediaUrl(res.image_url);
    }
  } catch (e) {
    uni.showToast({ title: e.message || '读取认证状态失败', icon: 'none' });
  }
};

const choosePhoto = () => {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['camera', 'album'],
    success: (res) => {
      const path = res.tempFilePaths?.[0];
      if (path) {
        localPath.value = path;
        previewUrl.value = path;
      }
    }
  });
};

const submit = async () => {
  if (!localPath.value || submitting.value) return;
  submitting.value = true;
  try {
    const uploaded = await uploadFile(localPath.value, 'image');
    const imageUrl = uploaded?.url || uploaded?.data?.url;
    if (!imageUrl) throw new Error('上传成功但未返回文件地址');
    const res = await submitFaceProfile(imageUrl);
    profile.value = res || profile.value;
    if (res?.image_url) previewUrl.value = resolveMediaUrl(res.image_url);
    uni.showToast({ title: '认证成功', icon: 'success' });
  } catch (e) {
    uni.showToast({ title: e.message || '认证失败，请换一张清晰正脸照', icon: 'none' });
    await loadProfile();
  } finally {
    submitting.value = false;
  }
};

onMounted(loadProfile);
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 64rpx 32rpx;
  background: #f6f8fb;
  box-sizing: border-box;
}
.header {
  margin-bottom: 32rpx;
}
.title {
  display: block;
  font-size: 44rpx;
  line-height: 56rpx;
  font-weight: 700;
  color: #18202a;
}
.subtitle {
  display: block;
  margin-top: 10rpx;
  font-size: 26rpx;
  line-height: 38rpx;
  color: #687381;
}
.status-panel {
  padding: 28rpx;
  border-radius: 8rpx;
  background: #fff;
  margin-bottom: 28rpx;
}
.status-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.status-label {
  font-size: 28rpx;
  color: #596575;
}
.status-value {
  font-size: 28rpx;
  font-weight: 700;
  color: #177a5d;
}
.status-failed,
.status-needs_reauth {
  color: #d94841;
}
.status-not_certified,
.status-pending {
  color: #8a5b00;
}
.error,
.meta {
  display: block;
  margin-top: 16rpx;
  font-size: 24rpx;
  line-height: 34rpx;
  color: #7c8796;
}
.error {
  color: #d94841;
}
.photo-box {
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 8rpx;
  overflow: hidden;
  background: #e8edf3;
  margin-bottom: 24rpx;
}
.photo {
  width: 100%;
  height: 100%;
}
.photo-empty {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #657182;
}
.photo-plus {
  font-size: 72rpx;
  line-height: 80rpx;
}
.photo-tip {
  margin-top: 12rpx;
  font-size: 28rpx;
}
.tips {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  margin-bottom: 32rpx;
  font-size: 24rpx;
  line-height: 36rpx;
  color: #687381;
}
.submit {
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 8rpx;
  color: #fff;
  background: #17b890;
  font-size: 30rpx;
  font-weight: 700;
}
.submit[disabled] {
  color: #fff;
  background: #b9c3cd;
}
</style>
