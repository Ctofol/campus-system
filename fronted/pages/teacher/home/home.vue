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
          <text class="teacher-name">{{ userInfo.name || '老师' }}</text>
          <text class="teacher-title">公共体育教研部</text>
        </view>
        <view class="teacher-avatar">
          <image class="avatar-img" src="/static/avatar.png" mode="aspectFill"></image>
        </view>
      </view>
      
      <!-- 2. 核心数据概览 -->
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
          <text class="stat-label">请假待处理</text>
        </view>
        <view class="stat-card" @click="goToActivityApproval">
          <text class="stat-num">{{ teacherStats.pendingActivities }}</text>
          <text class="stat-label">运动待审批</text>
        </view>
      </view>

      <!-- 3. 待办事项 -->
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
          <text class="section-more" @click="goToStudentStats">更多 ></text>
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
        
        <!-- 本周运动趋势 -->
        <view class="trend-chart">
          <text class="trend-title">本周运动趋势</text>
          <view class="trend-bars">
            <view class="t-bar-group" v-for="(d, i) in weeklyTrend" :key="i">
              <view class="t-bar" :style="{height: (d.val || 0) + '%', background: d.color}"></view>
              <text class="t-day">{{ d.day }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 5. 实时异常警报 -->
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

const goToLeaveApproval = () => {
  uni.navigateTo({ url: '/pages/teacher/approval/index?type=leave' });
};

const goToActivityApproval = () => {
  uni.navigateTo({ url: '/pages/teacher/approve/approve' });
};

const goToTodos = () => {
  uni.navigateTo({ url: '/pages/teacher/todos/index' });
};

// 跳转到班级阳光跑排行页
const goToStudentStats = () => {
  uni.navigateTo({ url: '/pages/teacher/class-rank/class-rank' });
};

const handleTodoClick = (todo) => {
  if (todo.path) {
    uni.navigateTo({ url: todo.path });
  }
};

const fetchTeacherStats = async () => {
  try {
    const res = await request({ url: '/teacher/dashboard/stats', method: 'GET' });
    teacherStats.value = {
      studentCount: res.stats?.student_count || 0,
      todayCheckin: res.stats?.today_checkin || 0,
      abnormalCount: res.stats?.abnormal_count || 0,
      pendingHealth: res.stats?.pending_health ?? 0,
      pendingActivities: res.stats?.pending_activities ?? 0,
      pendingApprovals: res.stats?.pending_approvals || 0,
      avgPace: res.stats?.avg_pace || '--',
      taskCount: res.stats?.task_count || 0,
      complianceRate: res.stats?.compliance_rate || 0,
      qualifiedRate: res.stats?.qualified_rate ?? 0,
      completionRate: res.stats?.completion_rate ?? 0
    };
    if (res.todos && Array.isArray(res.todos)) {
      todos.value = res.todos;
    }
  } catch (e) {
    if (!uni.getStorageSync('token')) return;
    console.error('Failed to fetch teacher stats:', e);
  }
};

// 使用新的阳光跑趋势接口
const fetchWeeklyTrend = async () => {
  try {
    const res = await request({ url: '/teacher/weekly-sunshine-trend', method: 'GET' });
    if (Array.isArray(res)) {
      // 归一化：找最大值作为100%高度基准，最小显示5%
      const maxVal = Math.max(...res.map(d => d.value), 1);
      weeklyTrend.value = res.map(d => ({
        day: d.day,
        val: d.value > 0 ? Math.max(5, Math.round((d.value / maxVal) * 100)) : 0,
        color: d.value > 0
          ? 'linear-gradient(180deg, #20C997 0%, #63e6be 100%)'
          : 'linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)'
      }));
    }
  } catch (e) {
    if (!uni.getStorageSync('token')) return;
    console.error('Failed to fetch weekly sunshine trend:', e);
  }
};

const fetchAbnormalAlerts = async () => {
  try {
    const res = await request({ url: '/teacher/students/abnormal', method: 'GET' });
    if (Array.isArray(res)) {
      abnormalAlerts.value = res.map((s, index) => ({
        id: s.id || index,
        student: s.name,
        type: s.health_status === 'injured' ? '受伤' : (s.health_status === 'leave' ? '请假' : '异常'),
        value: s.abnormal_reason || '未说明',
        time: s.updated_at
          ? new Date(s.updated_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
          : '--:--'
      })).slice(0, 5);
    }
  } catch (e) {
    if (!uni.getStorageSync('token')) return;
    console.error('Failed to fetch abnormal alerts:', e);
  }
};

onShow(() => {
  const storedUser = uni.getStorageSync('userInfo');
  if (storedUser) {
    try {
      userInfo.value = typeof storedUser === 'string' ? JSON.parse(storedUser) : storedUser;
    } catch (e) {
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
  studentCount: 0, todayCheckin: 0, abnormalCount: 0,
  pendingHealth: 0, pendingActivities: 0, pendingApprovals: 0,
  avgPace: '--', taskCount: 0, complianceRate: 0,
  qualifiedRate: 0, completionRate: 0
});

const weeklyTrend = ref(
  ['周一','周二','周三','周四','周五','周六','周日'].map(day => ({
    day, val: 0, color: 'linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)'
  }))
);

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
