<template>
  <view class="home-container">
    <view class="teacher-dashboard">
      <!-- 自定义导航栏 -->
      <view class="custom-nav-bar">
        <view class="nav-status-bar"></view>
        <view class="nav-content">
          <text class="nav-title">教师工作�?/text>
        </view>
      </view>
      
      <!-- 1. 教师头部信息 -->
      <view class="teacher-header">
        <view class="teacher-info">
          <text class="teacher-name">{{ userInfo.name || '老师' }}</text>
          <text class="teacher-title">体育教研�?/text>
        </view>
        <view class="teacher-avatar">
                <image class="avatar-img" src="/static/avatar.png" mode="aspectFill"></image>
              </view>
            </view>
            <!-- 2. 核心数据概览 - 功能打通：重命�?+ 跳转 -->
      <view class="dashboard-stats">
        <view class="stat-card">
          <text class="stat-num">{{ teacherStats.todayCheckin }}</text>
          <text class="stat-label">今日打卡</text>
        </view>
        <view class="stat-card" @click="goToLeaveApproval">
          <view class="badge-wrapper">
            <text class="stat-num">{{ teacherStats.pendingHealth }}</text>
            <view class="badge" v-if="teacherStats.pendingHealth > 0">{{ teacherStats.pendingHealth }}</view>
          </view>
          <text class="stat-label">请假待处�?/text>
        </view>
        <view class="stat-card" @click="goToActivityApproval">
          <text class="stat-num">{{ teacherStats.pendingActivities }}</text>
          <text class="stat-label">运动待审�?/text>
        </view>
      </view>

      <!-- 3. 待办事项 - 功能打通：全部按钮跳转 -->
      <view class="section-card todo-section">
        <view class="section-header">
          <text class="section-title">今日待办</text>
          <text class="section-more" @tap="goToTodos">全部 ></text>
        </view>
        <view class="todo-list">
          <view 
            class="todo-item" 
            v-for="(todo, idx) in todoList" 
            :key="idx" 
            @tap="handleTodoClick(todo)"
          >
            <view class="todo-check"></view>
            <view class="todo-content">
              <text class="todo-text">{{ todo.title }}: {{ todo.desc }}</text>
              <text class="todo-time">{{ todo.time }}</text>
            </view>
          </view>
          <view class="todo-empty" v-if="todoList.length === 0">
             <text>🎉 暂无待办事项</text>
          </view>
        </view>
      </view>

      <!-- 3. 学员整体数据概览 (新增图表) -->
      <view class="section-card chart-section">
        <view class="section-header">
          <text class="section-title">学员体能概览</text>
          <text class="section-more" @tap="goToStudentStats">更多 ></text>
        </view>
        <view class="overview-chart">
          <view class="chart-col">
            <view class="chart-ring ring-green">
              <text class="ring-val">{{ studentOverview.qualifiedRate }}%</text>
              <text class="ring-label">达标�?/text>
            </view>
            <text class="chart-name">体能达标</text>
          </view>
          <view class="chart-col">
            <view class="chart-ring ring-blue">
              <text class="ring-val">{{ studentOverview.completionRate }}%</text>
              <text class="ring-label">完成�?/text>
            </view>
            <text class="chart-name">本周任务</text>
          </view>
          <view class="chart-col">
            <view class="chart-ring ring-red">
              <text class="ring-val">{{ studentOverview.avgPace }}</text>
              <text class="ring-label">平均配�?/text>
            </view>
            <text class="chart-name">跑步状�?/text>
          </view>
        </view>
        
        <!-- 新增：本周运动趋�?-->
        <view class="trend-chart">
          <text class="trend-title">本周运动趋势</text>
          <view class="trend-bars">
            <view class="t-bar-group" v-for="(d, i) in weeklyTrend" :key="i">
              <view class="t-bar" :style="{height: d.val + '%', background: d.color}"></view>
              <text class="t-day">{{ d.day }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 5. 实时异常警报 (优化样式) -->
      <view class="section-card alert-widget" v-if="abnormalAlerts.length > 0">
        <view class="section-header">
          <text class="section-title red-dot">⚠️ 实时警报</text>
        </view>
        <view class="alert-feed">
          <view class="feed-item" v-for="(alert, idx) in abnormalAlerts" :key="idx">
            <view class="feed-content">
              <text class="feed-msg"><text class="feed-name">{{ alert.student }}</text> {{ alert.type }} ({{ alert.value }})</text>
              <text class="feed-time">{{ alert.time }}</text>
            </view>
            <button class="feed-btn" size="mini" @click="handleResolveAlert(idx)">干预</button>
          </view>
        </view>
      </view>
      
      <view style="height: 20rpx;"></view> <!-- Spacer for TabBar -->
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { request, getTeacherDashboardStats } from '@/utils/request.js';

const userInfo = ref({});

// 功能打通：跳转到请假审批列�?const goToLeaveApproval = () => {
  uni.navigateTo({ url: '/pages/teacher/approval/index?type=leave' });
};

// 功能打通：跳转到运动审批列表（任务上传/打分审批�?const goToActivityApproval = () => {
  uni.navigateTo({ url: '/pages/teacher/approve/approve' });
};

// 功能打通：跳转到待办事项列�?const goToTodos = () => {
  uni.navigateTo({ url: '/pages/teacher/todos/index' });
};

// 跳转到学员统计页�?const goToStudentStats = () => {
  uni.navigateTo({ url: '/pages/teacher/students/students' });
};

const todoList = ref([]);

// 学员体能概览数据
const studentOverview = ref({
  qualifiedRate: 0,
  completionRate: 0,
  avgPace: '--'
});

const fetchTeacherStats = async () => {
  try {
    const res = await getTeacherDashboardStats();
    // Map backend response to frontend state
    teacherStats.value = {
      studentCount: res.stats.student_count,
      todayCheckin: res.stats.today_checkin,
      abnormalCount: res.stats.abnormal_count,
      pendingHealth: res.stats.pending_health ?? 0,
      pendingActivities: res.stats.pending_activities ?? 0,
      pendingApprovals: res.stats.pending_approvals,
      avgPace: res.stats.avg_pace,
      taskCount: res.stats.task_count,
      complianceRate: res.stats.compliance_rate
    };
    
    // 更新学员体能概览数据
    studentOverview.value = {
      qualifiedRate: res.stats.qualified_rate || 0,
      completionRate: res.stats.completion_rate || 0,
      avgPace: res.stats.avg_pace || '--'
    };
    
    todoList.value = res.todos || [];
  } catch (e) {
    if (!uni.getStorageSync('token')) return;
    console.error('Failed to fetch teacher stats:', e);
  }
};

const onPageShow = () => {
  // uni.hideHomeButton && uni.hideHomeButton(); // Removed for tab bar page

  const storedUser = uni.getStorageSync('userInfo');
  if (storedUser) {
    try {
        userInfo.value = typeof storedUser === 'string' ? JSON.parse(storedUser) : storedUser;
    } catch (e) {
        console.error('JSON parse error', e);
        userInfo.value = {};
    }
  }
  
  // Check token before fetching
  if (!uni.getStorageSync('token')) {
      uni.reLaunch({ url: '/pages/login/login' });
      return;
  }
  
  // Fetch real stats
  fetchTeacherStats();
  fetchAbnormalAlerts();
};

onMounted(() => {
  onPageShow();
});

defineExpose({
  onPageShow
});

  // --- 教师端数�?---
  const teacherStats = ref({
    studentCount: 0,
    todayCheckin: 0,
    abnormalCount: 0,
    pendingHealth: 0,
    pendingActivities: 0,
    pendingApprovals: 0,
    avgPace: "--",
    taskCount: 0,
    complianceRate: 0
  });

  const weeklyTrend = ref([
    { day: '周一', val: 0, color: 'linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)' },
    { day: '周二', val: 0, color: 'linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)' },
    { day: '周三', val: 0, color: 'linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)' },
    { day: '周四', val: 0, color: 'linear-gradient(180deg, #20C997 0%, #63e6be 100%)' },
    { day: '周五', val: 0, color: 'linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)' },
    { day: '周六', val: 0, color: 'linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)' },
    { day: '周日', val: 0, color: 'linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)' }
  ]);

  const abnormalAlerts = ref([]);

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
          value: s.abnormal_reason || '未说�?,
          time: s.updated_at ? new Date(s.updated_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) : '--:--'
        })).slice(0, 5); // 只显示前5�?      }
    } catch (e) {
      if (!uni.getStorageSync('token')) return;
      console.error('Failed to fetch abnormal alerts:', e);
    }
  };

const handleTeacherAction = (action) => {
  if (action === '学员管理') {
    uni.navigateTo({ url: '/pages/teacher/students/students' });
  } else if (action === '任务管理') {
    uni.navigateTo({ url: '/pages/teacher/tasks/tasks' });
  } else if (action === '发布任务') {
    uni.navigateTo({ url: '/pages/teacher/tasks/create' });
  } else if (action === '异常处理') {
    uni.navigateTo({ url: '/pages/teacher/exceptions/exceptions' });
  } else if (action === '测试监控') {
    uni.navigateTo({ url: '/pages/teacher/tests/tests' });
  } else {
    uni.showToast({ title: `${action}功能即将上线`, icon: 'none' });
  }
};

const handleTodoClick = (todo) => {
  console.log('Todo clicked:', todo);
  if (todo.path) {
    uni.navigateTo({ 
      url: todo.path,
      fail: (err) => {
        console.error('Navigation failed:', err);
        uni.showToast({ 
          title: '页面跳转失败', 
          icon: 'none' 
        });
      }
    });
  } else {
    uni.showToast({ 
      title: '暂无详情页面', 
      icon: 'none' 
    });
  }
};

const handleResolveAlert = (index) => {
  uni.showActionSheet({
    itemList: ['联系学生', '标记已处�?, '查看详情'],
    success: (res) => {
      if (res.tapIndex === 1) {
        abnormalAlerts.value.splice(index, 1);
        teacherStats.value.abnormalCount = Math.max(0, teacherStats.value.abnormalCount - 1);
        uni.showToast({ title: '已处�?, icon: 'success' });
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
  height: 44px; /* 标准导航栏高�?*/
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

/* 教师端样�?*/
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

/* Dashboard Stats */
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
.badge {
  position: absolute;
  top: -10rpx;
  right: -20rpx;
  background: #ff4d4f;
  color: #fff;
  font-size: 20rpx;
  padding: 4rpx 10rpx;
  border-radius: 20rpx;
  min-width: 32rpx;
  text-align: center;
  font-weight: bold;
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
  align-items: flex-start;
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
  margin-top: 6rpx;
  box-sizing: border-box;
  flex-shrink: 0;
  position: relative;
}
/* Optional: Add a checkmark if needed in future */
/* .todo-check::after {
  content: '';
  position: absolute;
  top: 6rpx;
  left: 6rpx;
  width: 18rpx;
  height: 18rpx;
  background: #20C997;
  border-radius: 50%;
} */

.todo-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}
.todo-text {
  font-size: 30rpx;
  color: #333;
  margin-bottom: 8rpx;
  font-weight: 500;
  line-height: 1.5;
  white-space: normal;
  word-break: break-word;
}
.todo-time {
  font-size: 24rpx;
  color: #999;
}

.todo-empty {
  padding: 30rpx;
  text-align: center;
  color: #999;
  font-size: 26rpx;
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
.section-more, .section-action { font-size: 26rpx; color: #20C997; padding: 10rpx 0; }
.red-dot { color: #ff6b6b; }

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
