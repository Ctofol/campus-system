<template>
  <view class="todos-container">
    <view class="todos-header">
      <text class="header-title">今日待办</text>
      <text class="header-date">{{ currentDate }}</text>
    </view>
    
    <view class="todos-list">
      <view class="todo-item" v-for="(todo, index) in todos" :key="index" @click="handleTodoClick(todo)">
        <view class="todo-icon" :class="getTodoIconClass(todo.type)">
          <text class="icon-text">{{ getTodoIcon(todo.type) }}</text>
        </view>
        <view class="todo-content">
          <text class="todo-title">{{ todo.title }}</text>
          <text class="todo-desc">{{ todo.desc }}</text>
          <text class="todo-time">{{ todo.time }}</text>
        </view>
        <view class="todo-priority" :class="'priority-' + todo.priority">
          <text class="priority-text">{{ getPriorityText(todo.priority) }}</text>
        </view>
      </view>
      
      <view class="empty-state" v-if="todos.length === 0 && !loading">
        <text class="empty-icon">✓</text>
        <text class="empty-text">暂无待办事项</text>
        <text class="empty-desc">所有任务已完成</text>
      </view>
      
      <view class="loading-state" v-if="loading">
        <text class="loading-text">加载中...</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onLoad, onShow } from '@dcloudio/uni-app';
import { request } from '@/utils/request.js';

const todos = ref([]);
const loading = ref(false);

const currentDate = computed(() => {
  const now = new Date();
  const month = now.getMonth() + 1;
  const day = now.getDate();
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  const weekday = weekdays[now.getDay()];
  return `${month}月${day}日 ${weekday}`;
});

const fetchTodos = async () => {
  loading.value = true;
  try {
    const res = await request({
      url: '/teacher/dashboard/stats',
      method: 'GET'
    });
    
    if (res.todos && Array.isArray(res.todos)) {
      todos.value = res.todos;
    }
  } catch (e) {
    console.error('Failed to fetch todos:', e);
    uni.showToast({ title: '加载失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
};

const getTodoIcon = (type) => {
  const icons = {
    'approval': '✓',
    'task': '📝',
    'alert': '⚠️'
  };
  return icons[type] || '•';
};

const getTodoIconClass = (type) => {
  return `icon-${type}`;
};

const getPriorityText = (priority) => {
  const texts = {
    'high': '紧急',
    'medium': '重要',
    'normal': '普通'
  };
  return texts[priority] || '普通';
};

const handleTodoClick = (todo) => {
  if (todo.path) {
    uni.navigateTo({ url: todo.path });
  }
};

onShow(() => {
  fetchTodos();
});
</script>

<style scoped>
.todos-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20rpx;
}

.todos-header {
  background: linear-gradient(135deg, #20C997 0%, #17a2b8 100%);
  border-radius: 24rpx;
  padding: 40rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 8rpx 24rpx rgba(32, 201, 151, 0.2);
}

.header-title {
  font-size: 44rpx;
  font-weight: bold;
  color: #fff;
  display: block;
  margin-bottom: 12rpx;
}

.header-date {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.9);
}

.todos-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.todo-item {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
  transition: transform 0.2s ease;
}

.todo-item:active {
  transform: translateY(2rpx);
}

.todo-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
  flex-shrink: 0;
}

.icon-approval {
  background: linear-gradient(135deg, #20C997 0%, #17a2b8 100%);
}

.icon-task {
  background: linear-gradient(135deg, #4dabf7 0%, #3b8fd9 100%);
}

.icon-alert {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff5252 100%);
}

.icon-text {
  font-size: 36rpx;
  color: #fff;
}

.todo-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.todo-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.todo-desc {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.todo-time {
  font-size: 22rpx;
  color: #999;
}

.todo-priority {
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  flex-shrink: 0;
}

.priority-high {
  background: #ffe3e3;
}

.priority-high .priority-text {
  color: #ff6b6b;
}

.priority-medium {
  background: #fff3e0;
}

.priority-medium .priority-text {
  color: #ff9f43;
}

.priority-normal {
  background: #f0f0f0;
}

.priority-normal .priority-text {
  color: #999;
}

.priority-text {
  font-size: 22rpx;
  font-weight: 500;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 40rpx;
}

.empty-icon {
  font-size: 120rpx;
  color: #20C997;
  margin-bottom: 30rpx;
}

.empty-text {
  font-size: 32rpx;
  color: #333;
  font-weight: bold;
  margin-bottom: 12rpx;
}

.empty-desc {
  font-size: 26rpx;
  color: #999;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 80rpx 0;
}

.loading-text {
  font-size: 28rpx;
  color: #999;
}
</style>
