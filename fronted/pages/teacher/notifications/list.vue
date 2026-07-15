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
      <view class="filter-row">
        <view
          v-for="tab in filterTabs"
          :key="tab.key"
          class="filter-chip"
          :class="{ active: activeFilter === tab.key }"
          @click="activeFilter = tab.key"
        >
          <text>{{ tab.label }}</text>
        </view>
      </view>

      <view
        class="notification-item"
        v-for="item in filteredNotifications"
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
      <view class="empty-state" v-if="filteredNotifications.length === 0 && !loading">
        <view class="empty-mark"></view>
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
import { computed, ref, onMounted } from 'vue';
import { request } from '@/utils/request.js';

const notifications = ref([]);
const loading = ref(false);
const activeFilter = ref('all');

const filterTabs = [
  { key: 'all', label: '全部' },
  { key: 'student', label: '学生' },
  { key: 'task', label: '任务' },
  { key: 'run_group', label: '跑团' },
  { key: 'system', label: '系统' }
];

const mapFilter = (type) => {
  if (['student_message'].includes(type)) return 'student';
  if (['task', 'task_reminder'].includes(type)) return 'task';
  if (['run_group', 'run_group_activity', 'run_group_apply'].includes(type)) return 'run_group';
  return 'system';
};

const filteredNotifications = computed(() => {
  if (activeFilter.value === 'all') return notifications.value;
  return notifications.value.filter(item => mapFilter(item.type) === activeFilter.value);
});

const loadNotifications = async () => {
  loading.value = true;
  try {
    const res = await request({
      url: '/teacher/notifications',
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
    task_reminder: '任务提醒',
    teacher_message: '教师通知',
    student_message: '学生消息',
    run_group_activity: '跑团活动',
    run_group_apply: '报名提醒',
    health_review: '健康审批',
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
    request({ url: `/teacher/notifications/${item.id}/read`, method: 'PUT' }).catch(() => {});
  }
};

const markAllRead = () => {
  request({ url: '/teacher/notifications/read-all', method: 'PUT' }).then(() => {
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

.filter-row {
  display: flex;
  gap: 14rpx;
  overflow-x: auto;
  margin-bottom: 22rpx;
}

.filter-chip {
  flex-shrink: 0;
  padding: 12rpx 22rpx;
  border-radius: 999rpx;
  background: #fff;
  color: #718094;
  font-size: 25rpx;
  border: 1rpx solid rgba(24, 35, 46, 0.06);
}

.filter-chip.active {
  color: #24bfa2;
  background: #eef9f6;
  border-color: rgba(36, 191, 162, 0.18);
  font-weight: 700;
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

.empty-mark {
  width: 96rpx;
  height: 8rpx;
  border-radius: 999rpx;
  background: #dfe5ea;
  margin: 0 auto 30rpx;
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
