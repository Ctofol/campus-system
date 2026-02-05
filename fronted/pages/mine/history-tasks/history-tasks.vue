<template>
  <view class="history-tasks-page">
    <view class="custom-navbar" :style="{paddingTop: statusBarHeight + 'px'}">
      <view class="navbar-content">
        <view class="back-btn" @click="goBack">
          <text class="back-arrow">←</text>
        </view>
        <text class="navbar-title">历史任务</text>
      </view>
    </view>
    
    <view class="content-wrapper" :style="{paddingTop: (statusBarHeight + 44) + 'px'}">
      <view class="task-list" v-if="tasks.length > 0">
        <view class="task-item" v-for="(task, index) in tasks" :key="index">
          <view class="task-header">
            <text class="task-title">{{ task.title }}</text>
            <text class="task-status" :class="getStatusClass(task.status)">{{ getStatusText(task.status) }}</text>
          </view>
          <view class="task-desc">{{ task.description || '暂无描述' }}</view>
          <view class="task-meta">
            <text class="meta-item">发布于: {{ formatDate(task.created_at) }}</text>
            <text class="meta-item" v-if="task.deadline">截止: {{ formatDate(task.deadline) }}</text>
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

const statusBarHeight = ref(20);
const tasks = ref([]);

onLoad(() => {
  statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 20;
  fetchTasks();
});

const goBack = () => {
  uni.navigateBack();
};

const fetchTasks = async () => {
  try {
    // Fetch all tasks including completed/expired
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
    'pending': '待开始',
    'in_progress': '进行中',
    'completed': '已完成',
    'expired': '已过期',
    'canceled': '已取消'
  };
  return map[status] || status;
};

const getStatusClass = (status) => {
  if (status === 'completed') return 'status-green';
  if (status === 'expired' || status === 'canceled') return 'status-gray';
  return 'status-orange';
};

const formatDate = (str) => {
  if (!str) return '';
  const date = new Date(str);
  return `${date.getMonth()+1}-${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
};
</script>

<style scoped>
.history-tasks-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}
.custom-navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: #fff;
  z-index: 999;
  border-bottom: 1rpx solid #eee;
}
.navbar-content {
  height: 44px;
  display: flex;
  align-items: center;
  padding: 0 15px;
}
.back-btn {
  padding: 10px;
  margin-left: -10px;
}
.back-arrow {
  font-size: 20px;
  color: #333;
}
.navbar-title {
  font-size: 17px;
  font-weight: bold;
  color: #333;
  flex: 1;
  text-align: center;
  margin-right: 30px; /* Balance back button */
}

.content-wrapper {
  padding: 15px;
}

.task-item {
  background: #fff;
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.task-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
}

.task-status {
  font-size: 24rpx;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}
.status-green { color: #20C997; background: #e8f5e9; }
.status-orange { color: #ff9f43; background: #fff3e0; }
.status-gray { color: #999; background: #f5f5f5; }

.task-desc {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 16rpx;
  line-height: 1.4;
}

.task-meta {
  display: flex;
  justify-content: space-between;
  border-top: 1rpx solid #f0f0f0;
  padding-top: 12rpx;
}

.meta-item {
  font-size: 22rpx;
  color: #999;
}

.empty-state {
  padding-top: 100rpx;
  text-align: center;
}
.empty-text {
  color: #999;
  font-size: 28rpx;
}
</style>