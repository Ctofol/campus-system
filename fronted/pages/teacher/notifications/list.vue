<template>
  <view class="notifications-page">
    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="nav-back" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="nav-title">系统通知</text>
      <view class="nav-action" @click="markAllRead">
        <text class="action-text">全部已读</text>
      </view>
    </view>

    <!-- 通知列表 -->
    <view class="content">
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
        <text class="empty-icon">🔔</text>
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
    // TODO: 替换为实际的通知API
    // const res = await request({
    //   url: '/notifications',
    //   method: 'GET'
    // });
    // notifications.value = res.items || [];
    
    // 模拟数据
    notifications.value = [
      {
        id: 1,
        title: '系统维护通知',
        content: '系统将于今晚22:00-24:00进行维护，期间可能无法访问',
        type: 'system',
        is_read: true,
        created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 2,
        title: '功能更新提醒',
        content: '新增数据导出功能，可导出学生成绩和任务完成情况',
        type: 'update',
        is_read: true,
        created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
      }
    ];
  } catch (e) {
    console.error('Load notifications failed:', e);
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
  
  // 标记为已读
  if (!item.is_read) {
    item.is_read = true;
    // TODO: 调用标记已读API
  }
};

const markAllRead = () => {
  notifications.value.forEach(item => {
    item.is_read = true;
  });
  uni.showToast({ title: '已全部标记为已读', icon: 'success' });
  // TODO: 调用批量标记已读API
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
