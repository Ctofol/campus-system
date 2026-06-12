<template>
  <view class="history-tasks-page">
    <page-tab-header title="历史任务" show-back theme="white" />
    <view class="content-wrapper page-tab-body">
      <view class="task-list" v-if="tasks.length > 0">
        <view class="task-item" v-for="(task, index) in tasks" :key="index">
          <view class="task-header">
            <text class="task-title">{{ task.title }}</text>
            <text class="task-status" :class="getStatusClass(task.status)">{{ getStatusText(task.status) }}</text>
          </view>
          <view class="task-desc">{{ task.description || '暂无描述' }}</view>
          <view class="task-meta">
            <text class="meta-item">发布于：{{ formatDate(task.created_at) }}</text>
            <text class="meta-item" v-if="task.deadline">截止：{{ formatDate(task.deadline) }}</text>
          </view>
        </view>
      </view>

      <view class="empty-state" v-else>
        <text class="empty-text">暂无历史任务</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { getStudentTasks } from '@/utils/request.js';

const tasks = ref([]);

onLoad(() => {
  fetchTasks();
});

const fetchTasks = async () => {
  try {
    const res = await getStudentTasks({ page: 1, size: 50 });
    if (res.items) {
      tasks.value = res.items;
    }
  } catch (e) {
    console.error('Fetch history tasks failed', e);
  }
};

const getStatusText = (status) => {
  const map = {
    pending: '待开始',
    not_started: '未开始',
    failed: '未达标',
    in_progress: '进行中',
    completed: '已完成',
    expired: '已过期',
    canceled: '已取消'
  };
  return map[status] || status;
};

const getStatusClass = (status) => {
  if (status === 'completed') return 'status-green';
  if (status === 'expired' || status === 'canceled' || status === 'not_started') return 'status-gray';
  return 'status-orange';
};

const formatDate = (str) => {
  if (!str) return '';
  const date = new Date(str);
  return `${date.getMonth() + 1}-${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
};
</script>

<style scoped>
.history-tasks-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.content-wrapper {
  padding: 24rpx;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.task-item {
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16rpx;
  margin-bottom: 12rpx;
}

.task-title {
  flex: 1;
  font-size: 34rpx;
  font-weight: 700;
  color: #333;
  line-height: 1.4;
}

.task-status {
  flex-shrink: 0;
  font-size: 24rpx;
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
}

.status-green {
  color: #20C997;
  background: #e8f8f2;
}

.status-orange {
  color: #ff9f43;
  background: #fff3e0;
}

.status-gray {
  color: #999;
  background: #f3f4f6;
}

.task-desc {
  font-size: 29rpx;
  color: #666;
  line-height: 1.6;
  margin-bottom: 16rpx;
}

.task-meta {
  display: flex;
  justify-content: space-between;
  gap: 16rpx;
  padding-top: 14rpx;
  border-top: 1rpx solid #f0f0f0;
}

.meta-item {
  font-size: 24rpx;
  color: #999;
}

.empty-state {
  padding-top: 140rpx;
  text-align: center;
}

.empty-text {
  color: #999;
  font-size: 28rpx;
}
</style>