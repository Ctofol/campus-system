<template>
  <view class="discover-page">
    <page-tab-header
      :title="showCreateForm ? '创建跑团' : '跑团发现'"
      :show-back="showCreateForm"
      :back-handler="goBack"
      theme="white"
    >
      <template #right>
        <text
          v-if="!showCreateForm"
          class="page-tab-header-text-action"
          @click="goToRank"
        >排行榜</text>
      </template>
    </page-tab-header>

    <view class="page-tab-body">

    <view class="create-form" v-if="showCreateForm">
      <view class="form-item avatar-item">
        <text class="label">跑团头像</text>
        <view class="avatar-picker" @click="chooseGroupAvatar">
          <image class="avatar-preview" :src="avatarPreview" mode="aspectFill" />
          <text class="avatar-text">点击上传 · 可裁剪</text>
        </view>
      </view>

      <view class="form-item">
        <text class="label">跑团名称</text>
        <input class="input" v-model="formData.name" placeholder="请输入跑团名称" maxlength="20" />
      </view>

      <view class="form-item">
        <text class="label">跑团简介</text>
        <textarea
          class="textarea"
          v-model="formData.description"
          placeholder="请输入跑团简介"
          maxlength="200"
        />
      </view>

      <button class="submit-btn" @click="handleCreate">创建跑团</button>
    </view>

    <scroll-view
      v-else
      scroll-y
      class="group-list"
      @scrolltolower="loadMore"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
      <view
        class="group-card"
        v-for="(group, index) in groups"
        :key="group.id"
        @click="goToDetail(group.id)"
      >
        <view class="rank-badge" v-if="index < 3" :class="'rank-' + (index + 1)">
          <text>No.{{ index + 1 }}</text>
        </view>
        <image class="avatar" :src="groupAvatar(group.avatar)" mode="aspectFill" />
        <view class="info">
          <text class="name">{{ group.name }}</text>
          <text class="desc">{{ group.description || '暂无描述' }}</text>
          <text class="stats">{{ group.member_count }}人 · {{ (group.total_mileage || 0).toFixed(1) }}km</text>
        </view>
        <button class="join-btn" @click.stop="handleJoin(group.id)">加入</button>
      </view>

      <view class="loading" v-if="loading">
        <text>加载中...</text>
      </view>

      <view class="no-more" v-if="!loading && noMore">
        <text>没有更多了</text>
      </view>

      <view class="empty" v-if="!loading && groups.length === 0">
        <text>暂无跑团</text>
      </view>
    </scroll-view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { getRunGroups, joinRunGroup, createRunGroup, uploadFile, resolveMediaUrl } from '@/utils/request.js';

const groups = ref([]);
const page = ref(1);
const loading = ref(false);
const refreshing = ref(false);
const noMore = ref(false);
const showCreateForm = ref(false);
const avatarPreview = ref('/static/default-avatar.svg');
const formData = ref({
  name: '',
  description: '',
  avatar: ''
});

const groupAvatar = (avatar) => {
  if (!avatar) return '/static/default-avatar.svg';
  return resolveMediaUrl(avatar);
};

onLoad((options) => {
  if (options.action === 'create') {
    showCreateForm.value = true;
  }
});

const loadGroups = async (refresh = false) => {
  if (loading.value) return;

  if (refresh) {
    page.value = 1;
    noMore.value = false;
  }

  loading.value = true;

  try {
    const res = await getRunGroups({
      page: page.value,
      size: 20
    });

    const validGroups = Array.isArray(res) ? res.filter((g) => g && g.id) : [];

    if (refresh) {
      groups.value = validGroups;
    } else {
      groups.value.push(...validGroups);
    }

    if (validGroups.length < 20) {
      noMore.value = true;
    }
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' });
  } finally {
    loading.value = false;
    refreshing.value = false;
  }
};

const onRefresh = () => {
  refreshing.value = true;
  loadGroups(true);
};

const loadMore = () => {
  if (!loading.value && !noMore.value) {
    page.value += 1;
    loadGroups();
  }
};

const chooseGroupAvatar = async () => {
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

const handleJoin = async (groupId) => {
  try {
    const res = await joinRunGroup(groupId);
    if (res && res.joinStatus) {
      uni.showToast({ title: '加入成功', icon: 'success' });
      setTimeout(() => {
        uni.redirectTo({ url: '/pages/run-group/my' });
      }, 1500);
    } else {
      uni.showToast({ title: res?.message || '加入失败', icon: 'none' });
    }
  } catch (e) {
    uni.showToast({ title: e.message || e.detail || '加入失败，请重试', icon: 'none' });
  }
};

const handleCreate = async () => {
  if (!formData.value.name) {
    uni.showToast({ title: '请输入跑团名称', icon: 'none' });
    return;
  }

  if (!formData.value.description) {
    uni.showToast({ title: '请输入跑团简介', icon: 'none' });
    return;
  }

  try {
    uni.showLoading({ title: '创建中...' });
    await createRunGroup(formData.value);
    uni.hideLoading();
    uni.showToast({ title: '创建成功', icon: 'success' });
    setTimeout(() => {
      uni.redirectTo({ url: '/pages/run-group/my' });
    }, 1500);
  } catch (e) {
    uni.hideLoading();
    uni.showToast({ title: e.message || e.detail || '创建失败', icon: 'none' });
  }
};

const goBack = () => {
  showCreateForm.value = false;
  formData.value = {
    name: '',
    description: '',
    avatar: ''
  };
  avatarPreview.value = '/static/default-avatar.svg';
  loadGroups(true);
};

const goToDetail = (groupId) => {
  uni.navigateTo({ url: `/pages/run-group/detail?groupId=${groupId}` });
};

const goToRank = () => {
  uni.navigateTo({ url: '/pages/run-group/rank' });
};

onMounted(() => {
  if (!showCreateForm.value) {
    loadGroups(true);
  }
});
</script>

<style scoped>
.discover-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.create-form {
  padding: 40rpx 30rpx;
}

.form-item {
  margin-bottom: 40rpx;
}

.form-item.avatar-item {
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

.form-item.avatar-item .label {
  margin-bottom: 16rpx;
}

.label {
  display: block;
  font-size: 28rpx;
  color: #333;
  margin-bottom: 16rpx;
  font-weight: bold;
}

.input {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  padding: 0 24rpx;
  background: #fff;
  border-radius: 16rpx;
  font-size: 28rpx;
  border: 2rpx solid #e0e0e0;
  box-sizing: border-box;
}

.textarea {
  width: 100%;
  min-height: 200rpx;
  padding: 24rpx;
  background: #fff;
  border-radius: 16rpx;
  font-size: 28rpx;
  border: 2rpx solid #e0e0e0;
  box-sizing: border-box;
}

.submit-btn {
  width: 100%;
  padding: 28rpx;
  background: #20c997;
  color: #fff;
  border-radius: 50rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
  margin-top: 40rpx;
}

.group-list {
  height: calc(100vh - 80rpx);
  padding: 20rpx 30rpx;
}

.group-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
  position: relative;
}

.rank-badge {
  position: absolute;
  top: 10rpx;
  left: 10rpx;
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
  font-size: 20rpx;
  color: #fff;
}

.rank-1 {
  background: linear-gradient(135deg, #ffd700, #ffa500);
}

.rank-2 {
  background: linear-gradient(135deg, #c0c0c0, #808080);
}

.rank-3 {
  background: linear-gradient(135deg, #cd7f32, #8b4513);
}

.avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  margin-right: 20rpx;
  background: #e0e0e0;
}

.info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.name {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 8rpx;
}

.desc {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 8rpx;
}

.stats {
  font-size: 22rpx;
  color: #666;
}

.avatar-picker {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 24rpx 28rpx;
  background: #fff;
  border-radius: 18rpx;
}

.avatar-preview {
  width: 120rpx;
  height: 120rpx;
  border-radius: 60rpx;
  background: #f1f5f9;
  border: 2rpx solid #e2e8f0;
}

.avatar-text {
  font-size: 26rpx;
  color: #20c997;
  font-weight: 600;
}

.join-btn {
  padding: 12rpx 30rpx;
  background: #20c997;
  color: #fff;
  border-radius: 30rpx;
  font-size: 24rpx;
  border: none;
}

.loading,
.no-more,
.empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
  font-size: 24rpx;
}
</style>
