<template>
  <view class="notifications-page">
    <page-tab-header title="系统通知" show-back theme="white">
      <template #right>
        <text
          class="page-tab-header-text-action page-tab-header-text-action--plain"
          @click="markAllRead"
        >全部已读</text>
      </template>
    </page-tab-header>

    <view class="content page-tab-body">
      <view 
        class="notification-item" 
        v-for="item in notifications" 
        :key="item.id"
        :class="{ unread: !item.is_read }"
        @click="viewDetail(item)"
      >
        <view class="item-header">
          <text class="item-title">{{ item.title }}</text>
          <text class="item-time">{{ formatTime(item.created_at) }}</text>
        </view>
        <text class="item-content">{{ item.content }}</text>
        <view class="item-footer">
          <text class="item-type">{{ getTypeLabel(item.type) }}</text>
          <view class="unread-dot" v-if="!item.is_read"></view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-if="notifications.length === 0 && !loading">
        <image class="empty-icon-img" src="/static/通知图标.png" mode="aspectFit" />
        <text class="empty-text">暂无通知</text>
      </view>

      <!-- 加载中 -->
      <view class="loading" v-if="loading">
        <text>加载中...</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { request } from '@/utils/request.js';

const notifications = ref([]);
const loading = ref(false);

const loadNotifications = async () => {
  loading.value = true;
  try {
    const res = await request({
      url: '/student/notifications',
      method: 'GET'
    });
    notifications.value = (res || []).map(item => ({
      id: item.id,
      title: item.title || '通知',
      content: item.content || item.message || '',
      type: item.ntype || item.type || 'system',
      is_read: !!item.is_read,
      created_at: item.created_at || new Date().toISOString()
    }));
  } catch (e) {
    console.error('Load notifications failed:', e);
    notifications.value = [];
  } finally {
    loading.value = false;
  }
};

const formatTime = (timeStr) => {
  const date = new Date(timeStr);
  const now = new Date();
  const diff = now - date;
  const days = Math.floor(diff / (24 * 60 * 60 * 1000));
  
  if (days === 0) return '今天';
  if (days === 1) return '昨天';
  if (days < 7) return `${days}天前`;
  if (days < 30) return `${Math.floor(days / 7)}周前`;
  return `${date.getMonth() + 1}-${date.getDate()}`;
};

const getTypeLabel = (type) => {
  const map = {
    system: '系统通知',
    update: '功能更新',
    task: '任务提醒',
    score: '成绩通知'
  };
  return map[type] || '通知';
};

const viewDetail = (item) => {
  uni.showModal({
    title: item.title,
    content: item.content,
    showCancel: false,
    confirmText: '我知道了'
  });

  if (!item.is_read) {
    item.is_read = true;
    request({ url: `/student/notifications/${item.id}/read`, method: 'PUT' }).catch(() => {});
  }
};

const markAllRead = () => {
  request({ url: '/student/notifications/read-all', method: 'PUT' }).then(() => {
    notifications.value.forEach(item => { item.is_read = true; });
    uni.showToast({ title: '已全部标记为已读', icon: 'success' });
  }).catch(() => {
    uni.showToast({ title: '操作失败', icon: 'none' });
  });
};

const goBack = () => {
  uni.navigateBack();
};

onMounted(() => {
  loadNotifications();
});
</script>

<style scoped>
.notifications-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.nav-bar {
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}

.nav-bar-inner {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30rpx;
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
  width: 120rpx;
  display: flex;
  justify-content: flex-end;
}

.action-text {
  font-size: 26rpx;
  color: #20C997;
}

.content {
  padding: 30rpx;
}

.notification-item {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  position: relative;
}

.notification-item.unread {
  background: #f0f9ff;
  border-left: 4rpx solid #20C997;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.item-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  flex: 1;
}

.item-time {
  font-size: 24rpx;
  color: #999;
  margin-left: 20rpx;
}

.item-content {
  font-size: 26rpx;
  color: #666;
  line-height: 1.6;
  display: block;
  margin-bottom: 16rpx;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-type {
  font-size: 24rpx;
  color: #20C997;
  background: rgba(32, 201, 151, 0.1);
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
}

.unread-dot {
  width: 16rpx;
  height: 16rpx;
  background: #ff4d4f;
  border-radius: 50%;
}

.empty-state {
  padding: 200rpx 60rpx;
  text-align: center;
}

.empty-icon {
  font-size: 120rpx;
  display: block;
  margin-bottom: 30rpx;
}
.empty-icon-img { width: 120rpx; height: 120rpx; display: block; margin-bottom: 30rpx; }

.empty-text {
  font-size: 28rpx;
  color: #999;
}

.loading {
  padding: 100rpx 0;
  text-align: center;
  color: #999;
}
</style>
