<template>
  <view class="notifications-page">
    <page-tab-header title="我的通知" show-back theme="white">
      <template #right>
        <view v-if="notifications.length" class="nav-action" @click="markAllRead">
          <text class="action-text">全部已读</text>
        </view>
      </template>
    </page-tab-header>

    <view class="content page-tab-body">
      <view
        v-for="item in notifications"
        :key="item.id"
        class="notification-item"
        :class="{ unread: !item.is_read }"
        @click="openItem(item)"
      >
        <view class="item-header">
          <text class="item-title">{{ item.title }}</text>
          <text class="item-time">{{ formatTime(item.created_at) }}</text>
        </view>
        <text class="item-content">{{ item.body || '' }}</text>
        <view class="item-footer">
          <text class="item-type">{{ getTypeLabel(item.ntype) }}</text>
          <view v-if="!item.is_read" class="unread-dot" />
        </view>
      </view>

      <view v-if="notifications.length === 0 && !loading" class="empty-state">
        <text class="empty-icon">🔔</text>
        <text class="empty-text">暂无通知</text>
        <text class="empty-hint">审批结果、任务提醒会显示在这里</text>
      </view>

      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { request } from '@/utils/request.js';

const notifications = ref([]);
const loading = ref(false);

const loadNotifications = async () => {
  loading.value = true;
  try {
    const res = await request('/student/notifications?limit=50');
    notifications.value = Array.isArray(res) ? res : [];
  } catch (e) {
    console.error('Load notifications failed:', e);
    uni.showToast({ title: '加载通知失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
};

const formatTime = (timeStr) => {
  if (!timeStr) return '';
  const date = new Date(timeStr);
  const now = new Date();
  const diff = now - date;
  const days = Math.floor(diff / (24 * 60 * 60 * 1000));
  if (days === 0) return '今天';
  if (days === 1) return '昨天';
  if (days < 7) return `${days}天前`;
  return `${date.getMonth() + 1}-${date.getDate()}`;
};

const getTypeLabel = (type) => {
  const map = {
    health_review: '健康报备',
    task: '任务',
    system: '系统'
  };
  return map[type] || '通知';
};

const markRead = async (id) => {
  try {
    await request(`/student/notifications/${id}/read`, { method: 'PUT' });
  } catch (e) {
    console.error(e);
  }
};

const openItem = async (item) => {
  if (!item.is_read) {
    item.is_read = true;
    await markRead(item.id);
  }
  if (item.ntype === 'health_review') {
    uni.navigateTo({ url: '/pages/health/request' });
    return;
  }
  uni.showModal({
    title: item.title,
    content: item.body || '',
    showCancel: false
  });
};

const markAllRead = async () => {
  try {
    await request('/student/notifications/read-all', { method: 'PUT' });
    notifications.value.forEach((n) => {
      n.is_read = true;
    });
    uni.showToast({ title: '已全部标为已读', icon: 'none' });
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' });
  }
};

onShow(() => {
  loadNotifications();
});
</script>

<style scoped>
.notifications-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.nav-action .action-text {
  font-size: 26rpx;
  color: #20c997;
}

.content {
  padding: 0 30rpx 40rpx;
}

.notification-item {
  background: #fff;
  border-radius: 16rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.notification-item.unread {
  border-left: 6rpx solid #20c997;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16rpx;
  margin-bottom: 12rpx;
}

.item-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  flex: 1;
}

.item-time {
  font-size: 24rpx;
  color: #999;
  flex-shrink: 0;
}

.item-content {
  font-size: 28rpx;
  color: #666;
  line-height: 1.5;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16rpx;
}

.item-type {
  font-size: 24rpx;
  color: #20c997;
}

.unread-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #ff4d4f;
}

.empty-state {
  padding: 120rpx 0;
  text-align: center;
}

.empty-icon {
  font-size: 80rpx;
  display: block;
  margin-bottom: 24rpx;
}

.empty-text {
  font-size: 30rpx;
  color: #666;
}

.empty-hint {
  display: block;
  margin-top: 12rpx;
  font-size: 26rpx;
  color: #999;
}

.loading {
  text-align: center;
  padding: 40rpx;
  color: #999;
}
</style>
