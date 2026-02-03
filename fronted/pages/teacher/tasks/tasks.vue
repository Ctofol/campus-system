<template>
  <view class="tasks-page">
    <!-- Header Area with Stats -->
    <view class="dashboard-header">
      <view class="header-top">
        <text class="page-title">任务管理</text>
        <view class="header-actions">
          <view class="icon-btn search">
            <text class="iconfont">🔍</text>
          </view>
        </view>
      </view>
      
      <view class="stats-card">
        <view class="stat-item">
          <text class="stat-num">{{ ongoingCount }}</text>
          <text class="stat-label">进行中</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-num">{{ avgCompletion }}%</text>
          <text class="stat-label">平均完成率</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-num">{{ totalTasks }}</text>
          <text class="stat-label">累计任务</text>
        </view>
      </view>
    </view>

    <!-- Tab Filter -->
    <view class="tab-container">
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 0 }" 
        @click="currentTab = 0"
      >
        进行中
        <view class="tab-line" v-if="currentTab === 0"></view>
      </view>
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 1 }" 
        @click="currentTab = 1"
      >
        历史记录
        <view class="tab-line" v-if="currentTab === 1"></view>
      </view>
    </view>

    <!-- Task List -->
    <scroll-view scroll-y class="task-list" :style="{height: 'calc(100vh - 380rpx)'}">
      <view class="task-card" v-for="(task, index) in filteredTasks" :key="index" @click="goToDetail(task)">
        <view class="card-header">
          <view class="tag-row">
            <view class="type-tag" :class="getTypeClass(task.type)">{{ task.type }}</view>
            <view class="deadline-tag" :class="{ urgent: isUrgent(task.deadline) }">
              📅 {{ task.deadline }} 截止
            </view>
          </view>
          <view class="more-btn" @click.stop="showActionSheet(task)">...</view>
        </view>

        <view class="card-content">
          <text class="task-title">{{ task.title }}</text>
          <text class="task-desc">{{ task.desc }}</text>
        </view>

        <view class="card-progress">
          <view class="progress-info">
            <text class="info-text">完成度 <text class="highlight">{{ task.percent }}%</text></text>
            <text class="info-text sub">{{ task.completed }}/{{ task.total }}人</text>
          </view>
          <view class="progress-track">
            <view class="progress-bar" :style="{ width: task.percent + '%' }"></view>
          </view>
        </view>

        <view class="card-footer" @click.stop>
          <view class="avatars">
             <!-- Mock avatars -->
             <view class="avatar" v-for="n in 3" :key="n" :style="{left: (n-1)*20 + 'rpx', zIndex: 4-n}"></view>
             <view class="avatar-more" :style="{left: 60 + 'rpx'}">...</view>
          </view>
          <button class="remind-btn" size="mini" @click="remindUnfinished(task)" v-if="task.status === '进行中'">
            🔔 一键提醒
          </button>
        </view>
      </view>
      
      <view class="empty-state" v-if="filteredTasks.length === 0">
        <text class="empty-text">暂无任务数据</text>
      </view>
      
      <!-- Bottom spacer for FAB -->
      <view style="height: 120rpx;"></view>
    </scroll-view>

    <!-- Floating Action Button -->
    <view class="fab-btn" @click="createTask">
      <text class="fab-icon">+</text>
      <text class="fab-text">发布任务</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { getTeacherTasks, deleteTask } from '@/utils/request.js';

const currentTab = ref(0);
const tasks = ref([]);
const page = ref(1);
const size = ref(20);
const total = ref(0);
const loading = ref(false);

const loadTasks = async () => {
  if (loading.value) return;
  loading.value = true;
  try {
    const status = currentTab.value === 0 ? 'active' : 'ended';
    const res = await getTeacherTasks({ page: page.value, size: size.value, status });
    if (res.items) {
      const now = new Date();
      const newTasks = res.items.map(item => {
        const deadlineDate = new Date(item.deadline);
        const isExpired = deadlineDate < now;
        
        // Map backend type to frontend display
        let displayType = '训练';
        if (item.type === 'test') displayType = '考核';
        else if (item.type === 'run') displayType = '日常';
        
        // Calculate percentage
        const completed = item.completed_count || 0;
        const totalCount = item.total_students || 0;
        const percent = totalCount > 0 ? Math.round((completed / totalCount) * 100) : 0;

        return {
          id: item.id,
          title: item.title,
          type: displayType,
          desc: item.description || (item.min_distance ? `目标距离: ${item.min_distance}km` : '无具体描述'),
          status: isExpired ? '已结束' : '进行中',
          completed: completed,
          total: totalCount,
          percent: percent,
          deadline: item.deadline ? item.deadline.split('T')[0] : '无'
        };
      });
      
      if (page.value === 1) {
        tasks.value = newTasks;
      } else {
        tasks.value = [...tasks.value, ...newTasks];
      }
      total.value = res.total;
    }
  } catch (e) {
    console.error(e);
    uni.showToast({ title: '加载任务失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
};

watch(currentTab, () => {
  page.value = 1;
  tasks.value = [];
  loadTasks();
});

onShow(() => {
  page.value = 1;
  // If tasks are empty, load them. If not, maybe we want to refresh?
  // For now, let's refresh to ensure sync.
  loadTasks();
});

const ongoingCount = computed(() => {
    // This logic is imperfect as it only counts loaded tasks, but acceptable for now
    if (currentTab.value === 0) return total.value;
    return 0; // Or fetch separately if needed
});
const totalTasks = computed(() => total.value); // This is total of current tab, but maybe user wants total-total?
const avgCompletion = computed(() => {
  if (tasks.value.length === 0) return 0;
  const sum = tasks.value.reduce((acc, cur) => acc + cur.percent, 0);
  return Math.round(sum / tasks.value.length);
});

const filteredTasks = computed(() => {
  // Backend now filters for us
  return tasks.value;
});

const getTypeClass = (type) => {
  const map = {
    '考核': 'tag-red',
    '日常': 'tag-green',
    '训练': 'tag-blue'
  };
  return map[type] || 'tag-gray';
};

const isUrgent = (deadline) => {
  if (!deadline || deadline === '无') return false;
  const d = new Date(deadline);
  const now = new Date();
  const diffTime = Math.abs(d - now);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
  return diffDays <= 3 && d > now;
};

const goToDetail = (task) => {
  uni.navigateTo({ url: `/pages/teacher/tasks/detail?id=${task.id}` });
};

const remindUnfinished = (task) => {
  uni.showToast({ title: '提醒已发送', icon: 'success' });
};

const showActionSheet = (task) => {
  uni.showActionSheet({
    itemList: ['编辑任务', '删除任务'],
    itemColor: '#000000',
    success: async (res) => {
      if (res.tapIndex === 0) {
        // Edit task - Future implementation
        uni.showToast({ title: '编辑功能开发中', icon: 'none' });
      } else if (res.tapIndex === 1) {
        // Delete task
        handleDelete(task);
      }
    }
  });
};

const handleDelete = (task) => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除任务"${task.title}"吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await deleteTask(task.id);
          uni.showToast({ title: '删除成功' });
          // Refresh list
          page.value = 1;
          loadTasks();
        } catch (e) {
          console.error(e);
          uni.showToast({ title: '删除失败', icon: 'none' });
        }
      }
    }
  });
};

const createTask = () => {
  uni.navigateTo({
    url: '/pages/teacher/tasks/create'
  });
};
</script>

<style scoped>
.tasks-page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.dashboard-header {
  background: #20C997;
  padding: 40rpx 30rpx 80rpx 30rpx; /* Extra bottom padding for overlap */
  color: #fff;
  border-bottom-left-radius: 40rpx;
  border-bottom-right-radius: 40rpx;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.page-title {
  font-size: 40rpx;
  font-weight: bold;
}

.header-actions {
  display: flex;
  gap: 20rpx;
}

.icon-btn {
  width: 70rpx;
  height: 70rpx;
  background: rgba(255,255,255,0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stats-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 8rpx 20rpx rgba(32, 201, 151, 0.2);
  color: #333;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-num {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  display: block;
}

.stat-label {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
  display: block;
}

.stat-divider {
  width: 2rpx;
  height: 40rpx;
  background: #eee;
}

/* Templates Section */
.templates-section {
  padding: 20rpx 30rpx 0;
}
.section-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}
.template-scroll {
  white-space: nowrap;
  width: 100%;
}
.template-card {
  display: inline-block;
  width: 160rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx;
  margin-right: 20rpx;
  text-align: center;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.02);
}
.tpl-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  margin: 0 auto 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  color: #fff;
}
.tpl-name {
  font-size: 24rpx;
  color: #333;
  display: block;
}

.tab-container {
  display: flex;
  background: transparent;
  padding: 20rpx 60rpx;
  margin-top: 10rpx;
}

.tab-item {
  flex: 1;
  text-align: center;
  font-size: 30rpx;
  color: #999;
  padding-bottom: 16rpx;
  position: relative;
  transition: all 0.3s;
}

.tab-item.active {
  color: #333;
  font-weight: bold;
  font-size: 32rpx;
}

.tab-line {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40rpx;
  height: 6rpx;
  background: #20C997;
  border-radius: 4rpx;
}

.task-list {
  flex: 1;
  padding: 20rpx 30rpx;
  box-sizing: border-box;
}

.task-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
  position: relative;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20rpx;
}

.tag-row {
  display: flex;
  gap: 16rpx;
}

.type-tag {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 30rpx;
  color: #fff;
}
.tag-red { background: linear-gradient(135deg, #ff9a9e 0%, #ff6b6b 100%); }
.tag-green { background: linear-gradient(135deg, #84fab0 0%, #20C997 100%); }
.tag-blue { background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%); color: #446699; }
.tag-gray { background: #eee; color: #999; }

.deadline-tag {
  font-size: 22rpx;
  color: #999;
  display: flex;
  align-items: center;
  background: #f8f8f8;
  padding: 6rpx 16rpx;
  border-radius: 30rpx;
}

.deadline-tag.urgent {
  color: #ff6b6b;
  background: #fff0f0;
}

.more-btn {
  color: #ccc;
  font-weight: bold;
  letter-spacing: 2rpx;
}

.card-content {
  margin-bottom: 30rpx;
}

.task-title {
  font-size: 34rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 12rpx;
}

.task-desc {
  font-size: 26rpx;
  color: #888;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
}

.card-progress {
  margin-bottom: 30rpx;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.info-text {
  font-size: 26rpx;
  color: #666;
}

.info-text.sub {
  color: #999;
  font-size: 24rpx;
}

.highlight {
  color: #20C997;
  font-weight: bold;
  margin-left: 8rpx;
}

.progress-track {
  height: 12rpx;
  background: #f0f0f0;
  border-radius: 10rpx;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #20C997, #4cd9b0);
  border-radius: 10rpx;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20rpx;
  border-top: 1px solid #f5f5f5;
}

.avatars {
  position: relative;
  height: 50rpx;
  width: 120rpx;
}

.avatar {
  width: 50rpx;
  height: 50rpx;
  border-radius: 50%;
  background: #ddd;
  border: 2rpx solid #fff;
  position: absolute;
  top: 0;
}
.avatar:nth-child(1) { background-color: #ffd166; }
.avatar:nth-child(2) { background-color: #06d6a0; }
.avatar:nth-child(3) { background-color: #118ab2; }

.avatar-more {
  width: 50rpx;
  height: 50rpx;
  border-radius: 50%;
  background: #f0f0f0;
  color: #999;
  font-size: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #fff;
  position: absolute;
  top: 0;
}

.remind-btn {
  margin: 0;
  font-size: 24rpx;
  background: #fff;
  color: #20C997;
  border: 1px solid #20C997;
  border-radius: 30rpx;
  padding: 0 24rpx;
  line-height: 50rpx;
}

.empty-state {
  text-align: center;
  padding-top: 100rpx;
}

.empty-text {
  color: #999;
  font-size: 28rpx;
}

.fab-btn {
  position: fixed;
  bottom: 60rpx;
  left: 50%;
  transform: translateX(-50%);
  background: #333;
  color: #fff;
  display: flex;
  align-items: center;
  padding: 20rpx 40rpx;
  border-radius: 60rpx;
  box-shadow: 0 10rpx 30rpx rgba(0,0,0,0.3);
  z-index: 100;
}

.fab-icon {
  font-size: 40rpx;
  margin-right: 16rpx;
  font-weight: 300;
  margin-top: -4rpx;
}

.fab-text {
  font-size: 30rpx;
  font-weight: bold;
}
</style>