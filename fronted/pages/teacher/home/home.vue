<template>
  <view class="home-container">
    <view class="teacher-dashboard">
      <!-- 自定义导航栏 -->
      <view class="custom-nav-bar">
        <view class="nav-status-bar"></view>
        <view class="nav-content">
          <text class="nav-title">教师工作台</text>
        </view>
      </view>
      
      <!-- 1. 教师头部信息 -->
      <view class="teacher-header">
        <view class="teacher-info">
          <text class="teacher-name">{{ userInfo.name || '教师' }}</text>
          <text class="teacher-title">公共体育教研部</text>
        </view>
        <view class="teacher-avatar">
          <image class="avatar-img" src="/static/avatar.png" mode="aspectFill"></image>
        </view>
      </view>
      
      <!-- 2. 核心数据概览 - 功能打通：重命名 + 跳转 -->
      <view class="dashboard-stats">
        <view class="stat-card">
          <text class="stat-num">{{ teacherStats.todayCheckin }}</text>
          <text class="stat-label">今日打卡</text>
        </view>
        <view class="stat-card" @click="goToLeaveApproval">
          <view class="badge-wrapper">
            <text class="stat-num">{{ teacherStats.pendingHealth }}</text>
          </view>
          <text class="stat-label">请假待处理</text>
        </view>
        <view class="stat-card" @click="goToActivityApproval">
          <view class="badge-wrapper">
            <text class="stat-num">{{ teacherStats.pendingActivities }}</text>
          </view>
          <text class="stat-label">运动待审批</text>
        </view>
      </view>

      <!-- 3. 待办事项 - 功能打通：全部按钮跳转 -->
      <view class="section-card todo-section">
        <view class="section-header">
          <text class="section-title">今日待办</text>
          <text class="section-more" @click="goToTodos">全部 ></text>
        </view>
        <view class="todo-list" v-if="todos.length > 0">
          <view class="todo-item" v-for="(todo, index) in todos.slice(0, 3)" :key="index" @click="handleTodoClick(todo)">
            <view class="todo-check"></view>
            <view class="todo-content">
              <text class="todo-text">{{ todo.title }}</text>
              <text class="todo-time">{{ todo.desc }}</text>
            </view>
          </view>
        </view>
        <view class="empty-todo" v-else>
          <text class="empty-text">暂无待办事项</text>
        </view>
      </view>

      <!-- 4. 学员体能概览 -->
      <view class="section-card chart-section">
        <view class="section-header">
          <text class="section-title">学员体能概览</text>
        </view>
        <view class="overview-chart">
          <view class="chart-col">
            <view class="chart-ring ring-green">
              <text class="ring-val">{{ teacherStats.qualifiedRate }}%</text>
              <text class="ring-label">达标率</text>
            </view>
            <text class="chart-name">体能达标</text>
          </view>
          <view class="chart-col">
            <view class="chart-ring ring-blue">
              <text class="ring-val">{{ teacherStats.completionRate }}%</text>
              <text class="ring-label">完成率</text>
            </view>
            <text class="chart-name">本周任务</text>
          </view>
          <view class="chart-col">
            <view class="chart-ring ring-red">
              <text class="ring-val">{{ teacherStats.avgPace }}</text>
              <text class="ring-label">平均配速</text>
            </view>
            <text class="chart-name">跑步状态</text>
          </view>
        </view>
        
        <!-- 本周阳光跑趋势（点击可查看详情） -->
        <view class="trend-chart" @click="goToSunshineBoard">
          <text class="trend-title">本周阳光跑趋势</text>
          <view class="trend-bars">
            <view class="t-bar-group" v-for="(d, i) in weeklyTrend" :key="i">
              <view class="t-bar" :style="{height: d.val + '%', background: d.color}"></view>
              <text class="t-day">{{ d.day }}</text>
            </view>
          </view>
        </view>
      </view>

      
      <view style="height: 20rpx;"></view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { request } from '@/utils/request.js';

const userInfo = ref({});
const todos = ref([]);

// 功能打通：跳转到请假审批列表
const goToLeaveApproval = () => {
  uni.navigateTo({ url: '/pages/teacher/students/students?showHealth=true' });
};

// 功能打通：跳转到运动审批列表
const goToActivityApproval = () => {
  uni.navigateTo({ url: '/pages/teacher/exceptions/exceptions' });
};

// 功能打通：跳转到待办事项列表
const goToTodos = () => {
  uni.navigateTo({ url: '/pages/teacher/todos/index' });
};

const handleTodoClick = (todo) => {
  if (todo.path) {
    uni.navigateTo({ url: todo.path });
  }
};

const fetchTeacherStats = async () => {
  try {
    const res = await request({
      url: '/teacher/dashboard/stats',
      method: 'GET'
    });
    
    teacherStats.value = {
      studentCount: res.stats?.student_count || 0,
      todayCheckin: res.stats?.today_checkin || 0,
      abnormalCount: res.stats?.abnormal_count || 0,
      pendingApprovals: res.stats?.pending_approvals || 0,
      pendingHealth: res.stats?.pending_health || 0,
      pendingActivities: res.stats?.pending_activities || 0,
      avgPace: res.stats?.avg_pace || '--',
      taskCount: res.stats?.task_count || 0,
      complianceRate: res.stats?.compliance_rate || 0,
      qualifiedRate: res.stats?.qualified_rate !== undefined ? res.stats.qualified_rate : 0,
      completionRate: res.stats?.completion_rate !== undefined ? res.stats.completion_rate : 0
    };
    
    if (res.todos && Array.isArray(res.todos)) {
      todos.value = res.todos;
    }
  } catch (e) {
    if (!uni.getStorageSync('token')) return;
    console.error('Failed to fetch teacher stats:', e);
    teacherStats.value = {
      studentCount: 0,
      todayCheckin: 0,
      abnormalCount: 0,
      pendingApprovals: 0,
      pendingHealth: 0,
      pendingActivities: 0,
      avgPace: '--',
      taskCount: 0,
      complianceRate: 0,
      qualifiedRate: 0,
      completionRate: 0
    };
    todos.value = [];
  }
};

// 阳光跑趋势：针对当前教师绑定班级的阳光跑统计
const fetchWeeklyTrend = async () => {
  try {
    const res = await request({
      url: '/teacher/weekly-sunshine-trend',
      method: 'GET'
    });
    if (Array.isArray(res) && res.length) {
      // 找最大值做归一化，最低显示 5% 的柱子高度
      const maxVal = Math.max(...res.map(d => d.value || 0), 1);
      weeklyTrend.value = res.map(d => ({
        day: d.day,
        raw: d.value || 0,
        val: d.value > 0 ? Math.max(5, Math.round((d.value / maxVal) * 100)) : 0,
        color: d.value > 0
          ? 'linear-gradient(180deg, #20C997 0%, #63e6be 100%)'
          : 'linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)'
      }));
    } else {
      weeklyTrend.value = defaultWeeklyTrend();
    }
  } catch (e) {
    if (!uni.getStorageSync('token')) return;
    console.error('Failed to fetch weekly sunshine trend:', e);
    weeklyTrend.value = defaultWeeklyTrend();
  }
};

// 跳转到班级阳光跑详情（班级排行看板）
const goToSunshineBoard = () => {
  uni.navigateTo({
    url: '/pages/teacher/class-rank/class-rank'
  });
};

const fetchAbnormalAlerts = async () => {
  try {
    const res = await request({
      url: '/teacher/students/abnormal',
      method: 'GET'
    });
    if (Array.isArray(res)) {
      abnormalAlerts.value = res.map((s, index) => ({
        id: s.id || index,
        student: s.name,
        type: s.health_status === 'injured' ? '受伤' : (s.health_status === 'leave' ? '请假' : '异常'),
        value: s.abnormal_reason || '未说明',
        time: s.updated_at ? new Date(s.updated_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) : '--:--'
      })).slice(0, 5);
    }
  } catch (e) {
    if (!uni.getStorageSync('token')) return;
    console.error('Failed to fetch abnormal alerts:', e);
  }
};

onShow(() => {
  uni.hideHomeButton && uni.hideHomeButton();

  const storedUser = uni.getStorageSync('userInfo');
  if (storedUser) {
    try {
      userInfo.value = typeof storedUser === 'string' ? JSON.parse(storedUser) : storedUser;
    } catch (e) {
      console.error('JSON parse error', e);
      userInfo.value = {};
    }
  }
  
  if (!uni.getStorageSync('token')) {
    uni.reLaunch({ url: '/pages/login/login' });
    return;
  }
  
  fetchTeacherStats();
  fetchWeeklyTrend();
  fetchAbnormalAlerts();
});

const teacherStats = ref({
  studentCount: 0,
  todayCheckin: 0,
  abnormalCount: 0,
  pendingApprovals: 0,
  pendingHealth: 0,
  pendingActivities: 0,
  avgPace: "--",
  taskCount: 0,
  complianceRate: 0,
  qualifiedRate: 0,
  completionRate: 0
});

const defaultWeeklyTrend = () => ([
  { day: '周一', val: 0, raw: 0, color: 'linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)' },
  { day: '周二', val: 0, raw: 0, color: 'linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)' },
  { day: '周三', val: 0, raw: 0, color: 'linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)' },
  { day: '周四', val: 0, raw: 0, color: 'linear-gradient(180deg, #20C997 0%, #63e6be 100%)' },
  { day: '周五', val: 0, raw: 0, color: 'linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)' },
  { day: '周六', val: 0, raw: 0, color: 'linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)' },
  { day: '周日', val: 0, raw: 0, color: 'linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)' }
]);

const weeklyTrend = ref(defaultWeeklyTrend());

const abnormalAlerts = ref([]);

const handleResolveAlert = (index) => {
  uni.showActionSheet({
    itemList: ['联系学生', '标记已处理', '查看详情'],
    success: (res) => {
      if (res.tapIndex === 1) {
        abnormalAlerts.value.splice(index, 1);
        teacherStats.value.abnormalCount = Math.max(0, teacherStats.value.abnormalCount - 1);
        uni.showToast({ title: '已处理', icon: 'success' });
      } else if (res.tapIndex === 0) {
        uni.showToast({ title: '已发送通知', icon: 'none' });
      } else {
        uni.navigateTo({ url: '/pages/teacher/exceptions/exceptions' });
      }
    }
  });
};
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

/* 自定义导航栏 */
.custom-nav-bar {
  background: #20C997;
  width: 100%;
  position: sticky;
  top: 0;
  z-index: 100;
}
.nav-status-bar {
  height: var(--status-bar-height);
  width: 100%;
}
.nav-content {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.nav-title {
  color: #fff;
  font-size: 32rpx;
  font-weight: bold;
}

/* 教师端样式 */
.teacher-header {
  background: linear-gradient(135deg, #20C997 0%, #17a2b8 100%);
  padding: 40rpx 40rpx 80rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom-left-radius: 48rpx;
  border-bottom-right-radius: 48rpx;
  color: #fff;
  margin-bottom: 20rpx;
  box-shadow: 0 10rpx 30rpx rgba(32, 201, 151, 0.2);
}
.teacher-info {
  display: flex;
  flex-direction: column;
}
.teacher-name { 
  font-size: 44rpx; 
  font-weight: bold; 
  display: block; 
  margin-bottom: 12rpx;
  text-shadow: 0 2rpx 4rpx rgba(0,0,0,0.1);
}
.teacher-title { 
  font-size: 24rpx; 
  background: rgba(255,255,255,0.2);
  padding: 6rpx 20rpx;
  border-radius: 30rpx;
  display: inline-block;
  align-self: flex-start;
  backdrop-filter: blur(4px);
}
.teacher-avatar { 
  width: 120rpx; 
  height: 120rpx; 
  border-radius: 50%; 
  background: #fff;
  padding: 6rpx;
  box-shadow: 0 6rpx 16rpx rgba(0,0,0,0.15);
  display: flex; 
  align-items: center; 
  justify-content: center; 
  overflow: hidden; 
}
.avatar-img { width: 100%; height: 100%; border-radius: 50%; }

/* Dashboard Stats - 功能打通：可点击 */
.dashboard-stats {
  display: flex;
  justify-content: space-between;
  padding: 0 30rpx;
  margin-top: -60rpx;
  margin-bottom: 40rpx;
  position: relative;
  z-index: 10;
}
.stat-card {
  width: 31%;
  background: #fff;
  border-radius: 24rpx;
  padding: 36rpx 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 8rpx 24rpx rgba(0,0,0,0.06);
  box-sizing: border-box;
  transition: transform 0.2s ease;
}
.stat-card:active {
  transform: translateY(4rpx);
}
.badge-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stat-num {
  font-size: 44rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 12rpx;
  font-family: DINAlternate-Bold, sans-serif;
}
.stat-label {
  font-size: 24rpx;
  color: #888;
}

/* Todo List */
.todo-list {
  display: flex;
  flex-direction: column;
}
.todo-item {
  display: flex;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1px solid #f5f5f5;
  transition: background 0.2s;
}
.todo-item:active {
  background: #fafafa;
}
.todo-item:last-child {
  border-bottom: none;
}
.todo-check {
  width: 36rpx;
  height: 36rpx;
  border: 3rpx solid #ddd;
  border-radius: 50%;
  margin-right: 24rpx;
  box-sizing: border-box;
  position: relative;
}
.todo-content {
  display: flex;
  flex-direction: column;
}
.todo-text {
  font-size: 30rpx;
  color: #333;
  margin-bottom: 6rpx;
  font-weight: 500;
}
.todo-time {
  font-size: 24rpx;
  color: #999;
}

.empty-todo {
  text-align: center;
  padding: 60rpx 0;
}

.empty-text {
  font-size: 26rpx;
  color: #999;
}

.section-card {
  background: #fff;
  border-radius: 24rpx;
  margin: 0 30rpx 30rpx;
  padding: 36rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.03);
}

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30rpx; }
.section-title { font-size: 34rpx; font-weight: bold; color: #333; }
.section-more { font-size: 26rpx; color: #20C997; padding: 10rpx 0; }

.overview-chart { display: flex; justify-content: space-around; }
.chart-col { text-align: center; }
.chart-ring { 
  width: 130rpx; 
  height: 130rpx; 
  border-radius: 50%; 
  border: 10rpx solid #eee; 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  justify-content: center; 
  margin-bottom: 16rpx;
  position: relative;
}
.ring-green { border-color: #20C997; }
.ring-blue { border-color: #4dabf7; }
.ring-red { border-color: #ff6b6b; }
.ring-val { font-size: 32rpx; font-weight: bold; color: #333; font-family: DINAlternate-Bold, sans-serif; }
.ring-label { font-size: 20rpx; color: #999; margin-top: 4rpx; }
.chart-name { font-size: 26rpx; color: #666; font-weight: 500; }

/* Trend Chart */
.trend-chart {
  margin-top: 30rpx;
  border-top: 1px solid #f0f0f0;
  padding-top: 30rpx;
}
.trend-title { 
  font-size: 28rpx; 
  color: #333; 
  font-weight: bold; 
  margin-bottom: 24rpx; 
  display: flex;
  align-items: center;
}
.trend-title::before {
  content: '';
  width: 6rpx;
  height: 24rpx;
  background: #20C997;
  border-radius: 4rpx;
  margin-right: 12rpx;
}
.trend-bars {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  height: 140rpx;
  padding: 0 10rpx;
}
.t-bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 60rpx;
  height: 100%;
  justify-content: flex-end;
}
.t-bar {
  width: 16rpx;
  border-radius: 8rpx;
  transition: height 0.3s ease;
}
.t-day { 
  font-size: 22rpx; 
  color: #999; 
  margin-top: 12rpx; 
  font-weight: 500;
}

/* Alert Feed */
.alert-feed { display: flex; flex-direction: column; gap: 24rpx; }
.feed-item { 
  display: flex; 
  justify-content: space-between; 
  align-items: flex-start; 
  padding: 24rpx; 
  background: #fff; 
  border-radius: 16rpx; 
  border: 1px solid #ffe3e3;
  box-shadow: 0 4rpx 12rpx rgba(255, 107, 107, 0.08); 
  position: relative;
  overflow: hidden;
}
.feed-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 8rpx;
  background: #ff6b6b;
}
.feed-content {
  flex: 1; 
  margin-right: 24rpx; 
  padding-left: 16rpx;
}
.feed-msg { 
  font-size: 28rpx; 
  color: #333; 
  line-height: 1.5;
  margin-bottom: 8rpx;
}
.feed-name { font-weight: bold; color: #333; }
.feed-time { font-size: 22rpx; color: #999; }
.feed-btn { 
  margin: 0;
  background: #ff6b6b; 
  color: #fff; 
  font-size: 24rpx; 
  padding: 0 28rpx; 
  height: 60rpx; 
  line-height: 60rpx; 
  border-radius: 30rpx; 
  box-shadow: 0 4rpx 10rpx rgba(255, 107, 107, 0.3);
}
.feed-btn:active { opacity: 0.9; transform: translateY(2rpx); }
</style>
