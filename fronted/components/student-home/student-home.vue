<template>
  <view class="home-container">
    <!-- 顶部导航栏：用于填充状态栏区域，避免全屏时顶部留白 -->
    <view class="top-nav">
      <text class="top-nav-title">首页</text>
    </view>
    <view class="content-wrapper">
      <view class="student-dashboard">
      
      <!-- Hero Section: 开始运动 -->
      <view class="hero-card">
        <!-- 中间大圆形按钮 -->
        <view class="center-button" @click="showExerciseActionSheet">
          <view class="go-circle">
            <text class="go-text">GO</text>
            <text class="go-label">开始运动</text>
          </view>
        </view>
        
        <!-- 底部3个操作按钮 -->
        <view class="action-buttons">
          <view class="action-btn-item" @click="startOutdoorRun">
            <text class="btn-icon">🏃</text>
            <text class="btn-label">户外跑</text>
          </view>
          <view class="action-btn-item" @click="startPhysicalTest">
            <text class="btn-icon">💪</text>
            <text class="btn-label">体能测试</text>
          </view>
          <view class="action-btn-item" @click="uni.switchTab({url: '/pages/tab/learn'})">
            <text class="btn-icon">📚</text>
            <text class="btn-label">课程</text>
          </view>
        </view>
      </view>
      
      <!-- Task Stream: 任务流 -->
      <view class="section-container" v-if="teacherTasks.length > 0">
        <view class="section-header">
          <text class="section-title">我的任务</text>
          <text class="section-more" @click="handleTaskClick()">查看全部 ›</text>
        </view>
        <view class="task-stream">
          <view class="task-card" v-for="task in teacherTasks.slice(0, 3)" :key="task.id" @click="handleTaskClick(task)">
            <view class="task-type-icon" :class="getTaskTypeClass(task)">
              <text>{{ getTaskTypeIcon(task) }}</text>
            </view>
            <view class="task-info">
              <text class="task-name">{{ task.title }}</text>
              <text class="task-meta">{{ task.desc }}</text>
            </view>
            <view class="task-status-badge" :class="getTaskStatusClass(task)">
              <text>{{ getTaskStatusText(task) }}</text>
            </view>
          </view>
        </view>
      </view>
      
      <!-- Run Group Alliance: 跑团联盟 -->
      <view class="section-container">
        <view class="section-header-enhanced">
          <text class="section-title-main">跑团联盟</text>
          <view class="section-actions">
            <text class="action-link" @click="createRunGroup">创建</text>
            <text class="action-divider">|</text>
            <text class="action-link" @click="joinRunGroup">加入</text>
            <text class="action-divider">|</text>
            <text class="action-link" @click="browseActivities">活动浏览</text>
          </view>
        </view>
        
        <!-- 跑团核心数据卡片 -->
        <view class="run-group-card" v-if="myRunGroup" @click="goToRunGroupDetail">
          <view class="card-gradient-bg"></view>
          <view class="card-content">
            <view class="group-info">
              <view class="group-header">
                <text class="group-name">{{ myRunGroup.name }}</text>
                <view class="rank-badge" v-if="myRunGroup.rank">
                  <text class="rank-text">No.{{ myRunGroup.rank }}</text>
                </view>
              </view>
              <view class="group-stats">
                <view class="stat-item">
                  <text class="stat-value">{{ myRunGroup.member_count }}</text>
                  <text class="stat-label">成员数</text>
                </view>
                <view class="stat-item">
                  <text class="stat-value">{{ myRunGroup.total_mileage.toFixed(1) }}km</text>
                  <text class="stat-label">总里程</text>
                </view>
                <view class="stat-item">
                  <text class="stat-value">{{ myRunGroup.month_activity_count }}</text>
                  <text class="stat-label">本月活动</text>
                </view>
              </view>
            </view>
            <view class="rank-action" @click.stop="showRankList">
              <text class="rank-icon">🏆</text>
              <text class="rank-label">排行榜</text>
            </view>
          </view>
        </view>
        
        <!-- 未加入跑团提示 -->
        <view class="no-group-tip" v-else>
          <text class="tip-text">您还未加入跑团</text>
          <view class="tip-actions">
            <button class="tip-btn primary" @click="createRunGroup">创建跑团</button>
            <button class="tip-btn" @click="joinRunGroup">加入跑团</button>
          </view>
        </view>
        
        <!-- 最新动态列表 -->
        <view class="activity-section">
          <view class="activity-header">
            <view class="header-decorator"></view>
            <text class="activity-title">最新动态</text>
          </view>
          <scroll-view scroll-x class="activity-scroll" v-if="latestActivities.length > 0">
            <view 
              class="activity-card" 
              v-for="activity in latestActivities" 
              :key="activity.id"
              @click="goToActivityDetail(activity.id)"
            >
              <view class="activity-status-badge" :class="getActivityStatusClass(activity.status)">
                <text class="badge-text">{{ getActivityStatusText(activity.status) }}</text>
              </view>
              <text class="activity-name">{{ activity.title }}</text>
              <view class="activity-time">
                <text class="time-icon">📅</text>
                <text class="time-text">{{ formatActivityTime(activity.activity_time) }}</text>
              </view>
              <view class="activity-apply">
                <text class="apply-text">{{ activity.apply_count }}人已报名</text>
                <view class="apply-progress">
                  <view class="progress-fill" :style="{width: (activity.apply_count / activity.total_quota * 100) + '%'}"></view>
                </view>
              </view>
            </view>
          </scroll-view>
          <view class="no-activity" v-else>
            <text class="no-activity-text">暂无活动</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部占位 -->
    <view style="height: 20rpx;"></view>
    
    <!-- 任务提醒弹窗 -->
    <view class="modal-overlay" v-if="showTaskModal" @click="closeTaskModal">
      <view class="task-modal" @click.stop>
        <view class="modal-header">
            <text class="modal-title">🔔 您有新的任务</text>
            <text class="close-btn" @click="closeTaskModal">×</text>
        </view>
        <view class="task-list"> 
           <view class="task-modal-item" v-for="task in teacherTasks" :key="task.id" @click="handleTaskClick(task)">
              <view class="task-icon-box">
                <text class="task-icon">{{ getTaskTypeIcon(task) }}</text>
              </view>
              <view class="task-content">
                <text class="task-title">{{ task.title }}</text>
                <text class="task-desc">{{ task.desc }}</text>
              </view>
              <view class="task-action">
                <text class="btn-text">去完成</text>
              </view>
           </view>
        </view>
        <view style="margin-top: 20rpx; text-align: center;">
            <button size="mini" type="primary" @click="closeTaskModal" style="background-color: #20C997;">我知道了</button>
        </view>
      </view>
    </view>
  </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { request } from '@/utils/request.js';

// 状态栏高度
const statusBarHeight = ref(20);

// 角色状态
const role = ref('student');
const userInfo = ref({});

// 任务数据
const teacherTasks = ref([]);
const showTaskModal = ref(false);

// 跑团数据
const myRunGroup = ref(null);
const latestActivities = ref([]);

const fetchTasks = async () => {
  try {
    // 对接真实API GET /student/tasks
    const res = await request({
      url: '/student/tasks',
      method: 'GET',
      data: { page: 1, size: 20 }
    });
    
    if (res.items && res.items.length > 0) {
      const ongoingStatuses = ['pending', 'in_progress', 'uncompleted']; 
      teacherTasks.value = res.items
        .filter(task => ongoingStatuses.includes(task.status))
        .map(task => ({
         id: task.id,
         title: task.title,
         status: task.status, 
         type: task.type || task.task_type || 'run',
         deadline: task.deadline,
         urgent: task.urgent || false,
         desc: task.description || (task.min_distance ? `目标: ${task.min_distance}km` : '请查看详情')
      }));
      
      if (teacherTasks.value.length > 0) {
        const viewedIds = uni.getStorageSync('viewed_task_ids') || [];
        const hasNewTask = teacherTasks.value.some(task => !viewedIds.includes(task.id));
        
        if (hasNewTask) {
           showTaskModal.value = true;
        }
      }
    } else {
        teacherTasks.value = [];
    }
  } catch (e) {
    if (!uni.getStorageSync('token')) return;
    console.error('Fetch tasks failed', e);
    // 优雅降级：使用空数组
    teacherTasks.value = [];
  }
};

// Exposed method for parent to call onShow
const onPageShow = () => {
  statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 20;
  
  const token = uni.getStorageSync('token');
  if (!token) {
    uni.reLaunch({ url: '/pages/login/login' });
    return;
  }

  const userRole = uni.getStorageSync('userRole') || uni.getStorageSync('role');
  if (userRole) role.value = userRole;
  
  const storedUser = uni.getStorageSync('userInfo');
  if (storedUser) {
    try {
        userInfo.value = typeof storedUser === 'string' ? JSON.parse(storedUser) : storedUser;
    } catch (e) {
        console.error('JSON parse error', e);
        userInfo.value = {};
    }
  }
  
  fetchTasks();
  loadRunGroupData(); // 每次显示页面时重新加载跑团数据
};

// Initial load
onMounted(() => {
  statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 20;
  onPageShow();
  loadRunGroupData(); // 加载跑团数据
});

// Expose methods
defineExpose({
  onPageShow
});

// 任务类型相关
const getTaskTypeIcon = (task) => {
  if (task.type === 'learn' || task.type === 'learning' || task.title.includes('课程') || task.title.includes('学习')) {
    return '📚';
  }
  return '🏃';
};

const getTaskTypeClass = (task) => {
  if (task.type === 'learn' || task.type === 'learning' || task.title.includes('课程') || task.title.includes('学习')) {
    return 'task-type-learning';
  }
  return 'task-type-exercise';
};

const getTaskStatusClass = (task) => {
  if (task.urgent) return 'status-urgent';
  if (task.status === 'pending') return 'status-pending';
  if (task.status === 'in_progress') return 'status-progress';
  return 'status-uncompleted';
};

const getTaskStatusText = (task) => {
  if (task.urgent) return '紧急';
  if (task.status === 'pending') return '待开始';
  if (task.status === 'in_progress') return '进行中';
  return '未完成';
};

// 运动选项 - 使用 ActionSheet
const startOutdoorRun = () => {
  uni.navigateTo({ url: '/pages/run/run' });
};

const startPhysicalTest = () => {
  uni.navigateTo({ url: '/pages/test/test' });
};

const startAiTest = () => {
  uni.navigateTo({ url: '/pages/test/test' });
};

const startFreeExercise = () => {
  uni.navigateTo({ url: '/pages/sport/free-practice' });
};

// 显示运动选项 ActionSheet
const showExerciseActionSheet = () => {
  uni.showActionSheet({
    itemList: ['户外跑步', '体测', '自由练习'],
    success: (res) => {
      if (res.tapIndex === 0) {
        startOutdoorRun();
      } else if (res.tapIndex === 1) {
        startAiTest();
      } else if (res.tapIndex === 2) {
        startFreeExercise();
      }
    },
    fail: (err) => {
      console.log('ActionSheet cancelled', err);
    }
  });
};

// 任务操作
const handleTaskClick = (task) => { 
  if (task) {
    uni.navigateTo({
      url: `/pages/student/tasks/list?taskId=${task.id}`
    });
  } else {
    uni.navigateTo({
      url: '/pages/student/tasks/list'
    });
  }
};

const closeTaskModal = () => { 
  showTaskModal.value = false; 
  const viewedIds = uni.getStorageSync('viewed_task_ids') || [];
  const newIds = teacherTasks.value.map(t => t.id);
  const updatedIds = [...new Set([...viewedIds, ...newIds])];
  uni.setStorageSync('viewed_task_ids', updatedIds);
};

// 快捷功能
const browseActivities = () => { 
  uni.navigateTo({url: '/pages/activity/list'}); 
};

const viewHistory = () => {
  uni.navigateTo({url: '/pages/history/history'});
};

// 跑团功能
const createRunGroup = () => {
  uni.navigateTo({url: '/pages/run-group/discover?action=create'});
};

const joinRunGroup = () => {
  uni.navigateTo({url: '/pages/run-group/discover'});
};

const goToRunGroupDetail = () => {
  if (myRunGroup.value) {
    uni.navigateTo({url: `/pages/run-group/detail?groupId=${myRunGroup.value.id}`});
  }
};

const showRankList = () => {
  uni.navigateTo({url: '/pages/run-group/rank'});
};

const goToActivityDetail = (activityId) => {
  uni.navigateTo({url: `/pages/run-group/activity-detail?activityId=${activityId}`});
};

const getActivityStatusClass = (status) => {
  const classMap = {
    'upcoming': 'status-upcoming',
    'ongoing': 'status-ongoing',
    'finished': 'status-finished'
  };
  return classMap[status] || 'status-upcoming';
};

const getActivityStatusText = (status) => {
  const textMap = {
    'upcoming': '报名中',
    'ongoing': '进行中',
    'finished': '已结束'
  };
  return textMap[status] || '报名中';
};

const formatActivityTime = (timeStr) => {
  const date = new Date(timeStr);
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const hour = date.getHours().toString().padStart(2, '0');
  const minute = date.getMinutes().toString().padStart(2, '0');
  return `${month}月${day}日 ${hour}:${minute}`;
};

// 加载跑团数据
const loadRunGroupData = async () => {
  try {
    // 加载我的跑团
    const groupRes = await request({
      url: '/run-group/my',
      method: 'GET'
    });
    myRunGroup.value = groupRes;
  } catch (e) {
    console.log('未加入跑团或加载失败:', e);
    myRunGroup.value = null;
  }
  
  try {
    // 加载最新活动
    const activityRes = await request({
      url: '/run-group/activity/list',
      method: 'GET',
      data: { page: 1, size: 5 }
    });
    latestActivities.value = activityRes.items || [];
  } catch (e) {
    console.error('加载活动失败:', e);
    latestActivities.value = [];
  }
};

</script>

<style scoped>
@import './run-group-styles.scss';

.home-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
  max-width: 750rpx;
  margin: 0 auto;
}

.top-nav {
  padding-top: 40rpx;
  padding-bottom: 20rpx;
  padding-left: 30rpx;
  padding-right: 30rpx;
  background-color: #f5f7fa;
  display: flex;
  justify-content: center;
}

.top-nav-title {
  font-size: 34rpx;
  font-weight: bold;
  color: #333;
}

.student-dashboard {
  padding-bottom: 20rpx;
}

/* Hero Card */
.hero-card {
  background: linear-gradient(180deg, #20C997 0%, #17a589 100%);
  margin: 20rpx 30rpx 30rpx;
  padding: 40rpx 30rpx 50rpx;
  border-radius: 40rpx;
  box-shadow: 0 10rpx 40rpx rgba(32, 201, 151, 0.3);
  position: relative;
  overflow: hidden;
}

.hero-card::before {
  content: '';
  position: absolute;
  top: -100rpx;
  right: -100rpx;
  width: 300rpx;
  height: 300rpx;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 50%;
}

.center-button {
  display: flex;
  justify-content: center;
  margin-bottom: 45rpx;
  position: relative;
  z-index: 1;
}

.go-circle {
  width: 180rpx;
  height: 180rpx;
  background: #fff;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.12);
  transition: transform 0.2s ease;
}

.go-circle:active {
  transform: scale(0.95);
}

.go-text {
  font-size: 52rpx;
  font-weight: bold;
  color: #20C997;
  font-family: Arial, sans-serif;
  letter-spacing: 2rpx;
  line-height: 1;
}

.go-label {
  font-size: 24rpx;
  color: #666;
  margin-top: 6rpx;
}

.action-buttons {
  display: flex;
  justify-content: space-around;
  gap: 20rpx;
  position: relative;
  z-index: 1;
  padding: 0 10rpx;
}

.action-btn-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 24rpx;
  padding: 20rpx 16rpx;
  min-height: 120rpx;
  transition: all 0.2s ease;
}

.action-btn-item:active {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(2rpx);
}

.btn-icon {
  font-size: 44rpx;
  margin-bottom: 6rpx;
}

.btn-label {
  font-size: 22rpx;
  color: #fff;
  font-weight: 500;
}

/* Section Container */
.section-container {
  background: #fff;
  border-radius: 20rpx;
  margin: 0 30rpx 20rpx;
  padding: 30rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  border-left: 6rpx solid #20C997;
  padding-left: 12rpx;
}

.section-more {
  font-size: 24rpx;
  color: #999;
}

/* Task Stream */
.task-stream {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.task-card {
  display: flex;
  align-items: center;
  padding: 20rpx;
  background: #f8f9fa;
  border-radius: 16rpx;
  border-left: 4rpx solid #20C997;
}

.task-type-icon {
  width: 70rpx;
  height: 70rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  margin-right: 16rpx;
  flex-shrink: 0;
}

.task-type-exercise {
  background: linear-gradient(135deg, #20C997, #17a589);
}

.task-type-learning {
  background: linear-gradient(135deg, #4dabf7, #3b8fd9);
}

.task-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.task-name {
  font-size: 26rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 6rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-meta {
  font-size: 22rpx;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-status-badge {
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  font-size: 20rpx;
  color: #fff;
  white-space: nowrap;
  flex-shrink: 0;
}

.status-pending {
  background: #ff9f43;
}

.status-progress {
  background: #20C997;
}

.status-uncompleted {
  background: #adb5bd;
}

.status-urgent {
  background: #ff6b6b;
}

/* Quick Actions */
.quick-actions {
  display: flex;
  justify-content: space-between;
  gap: 16rpx;
}

.action-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24rpx 16rpx;
  background: #f8f9fa;
  border-radius: 16rpx;
}

.action-icon {
  width: 70rpx;
  height: 70rpx;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  margin-bottom: 12rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.action-name {
  font-size: 22rpx;
  color: #666;
  font-weight: 500;
}

/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 30rpx;
  align-items: center;
}

.modal-title {
  font-size: 32rpx;
  font-weight: bold;
}

.close-btn {
  font-size: 40rpx;
  color: #999;
  line-height: 1;
}

/* Task Modal */
.task-modal {
  width: 600rpx;
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  max-height: 80vh;
  overflow-y: auto;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.task-modal-item {
  display: flex;
  align-items: center;
  padding: 20rpx;
  background: #f9f9f9;
  border-radius: 12rpx;
}

.task-icon-box {
  width: 60rpx;
  height: 60rpx;
  background: #e8f5e9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.task-icon {
  font-size: 32rpx;
}

.task-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.task-title {
  font-size: 26rpx;
  font-weight: bold;
  color: #333;
}

.task-desc {
  font-size: 22rpx;
  color: #666;
  margin-top: 4rpx;
}

.task-action {
  background: #ff6b6b;
  padding: 8rpx 20rpx;
  border-radius: 30rpx;
}

.btn-text {
  color: #fff;
  font-size: 22rpx;
  font-weight: bold;
}
</style>