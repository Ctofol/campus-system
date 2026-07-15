<template>
  <view class="teacher-home">
    <page-tab-header title="教师首页" theme="brand">
      <template #right>
        <view class="header-action" @click="goToNotifications">
          <image class="header-action__icon" :src="notificationIcon" mode="aspectFit" />
          <text v-if="notificationCount" class="header-action__badge">{{ notificationCount }}</text>
        </view>
      </template>
    </page-tab-header>

    <scroll-view scroll-y class="teacher-home__body page-tab-body">
      <view class="welcome-card">
        <view class="teacher-avatar" @click="goToProfileEdit">
          <image class="avatar-img" :src="avatarDisplay" mode="aspectFill" />
        </view>
        <view class="welcome-copy">
          <text class="welcome-title">{{ displayName }}，{{ greeting }}！</text>
          <text class="welcome-subtitle">今天也把班级训练节奏稳稳推进。</text>
        </view>
        <view class="date-block">
          <text class="date-text">{{ currentDate }}</text>
          <text class="weekday-text">{{ currentWeekday }}</text>
        </view>
      </view>

      <view class="overview-panel">
        <view class="overview-head">
          <view>
            <text class="panel-title panel-title--light">今日概览</text>
            <text class="overview-subtitle">关键教学数据</text>
          </view>
          <text class="overview-date">{{ currentWeekday }}</text>
        </view>
        <view class="overview-grid">
          <view class="overview-item" v-for="item in overviewItems" :key="item.label">
            <image class="overview-icon" :src="item.icon" mode="aspectFit" />
            <view class="overview-copy">
              <text class="overview-value">{{ item.value }}</text>
              <text class="overview-label">{{ item.label }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="section-block">
        <view class="section-title">快捷操作</view>
        <view class="quick-grid">
          <view class="quick-item" v-for="item in quickActions" :key="item.label" @click="navTo(item.path)">
            <view class="quick-icon-wrap" :class="item.tone">
              <image class="quick-icon" :class="{ 'is-svg-icon': item.svg }" :src="item.icon" mode="aspectFit" />
            </view>
            <text class="quick-label">{{ item.label }}</text>
          </view>
        </view>
      </view>

      <view class="section-block">
        <view class="section-head">
          <text class="section-title">进行中的任务</text>
          <view class="section-more" @click="navTo('/pages/teacher/tasks/tasks')">
            <text>查看全部</text>
            <view class="more-arrow" />
          </view>
        </view>
        <view v-if="activeTasks.length" class="task-list">
          <view class="task-row" v-for="task in activeTasks" :key="task.id" @click="goToTaskDetail(task)">
            <view class="task-mark" :class="task.tone">
              <image class="task-mark__icon" :class="{ 'is-svg-icon': task.svg }" :src="task.icon" mode="aspectFit" />
            </view>
            <view class="task-info">
              <view class="task-title-row">
                <text class="task-title">{{ task.title }}</text>
                <text class="task-status">进行中</text>
              </view>
              <text class="task-desc">{{ task.desc }}</text>
              <text class="task-meta">截止：{{ task.deadline }} · {{ task.completed }}/{{ task.total }}人</text>
            </view>
            <view class="progress-ring" :style="{ '--percent': task.percent }">
              <text class="progress-value">{{ task.percent }}%</text>
              <text class="progress-label">完成率</text>
            </view>
          </view>
        </view>
        <view v-else class="empty-state">
          <text>暂无进行中的任务</text>
        </view>
      </view>

      <view class="section-block">
        <view class="section-head">
          <text class="section-title">待处理事项</text>
          <view class="section-more" @click="goToTodos">
            <text>查看全部</text>
            <view class="more-arrow" />
          </view>
        </view>
        <view class="pending-grid">
          <view class="pending-item" v-for="item in pendingItems" :key="item.label" @click="navTo(item.path)">
            <view class="pending-icon-wrap" :class="item.tone">
              <image class="pending-icon" :class="{ 'is-svg-icon': item.svg }" :src="item.icon" mode="aspectFit" />
              <text v-if="item.count > 0" class="pending-badge">{{ item.count }}</text>
            </view>
            <view class="pending-copy">
              <text class="pending-count">{{ item.count }}</text>
              <text class="pending-label">{{ item.label }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="section-block chart-section">
        <view class="section-head">
          <text class="section-title">学员体能概览</text>
          <view class="section-more" @click="goToSunshineBoard">
            <text>阳光跑</text>
            <view class="more-arrow" />
          </view>
        </view>
        <view class="fitness-grid">
          <view class="fitness-item">
            <text class="fitness-value">{{ teacherStats.qualifiedRate }}%</text>
            <text class="fitness-label">体能达标</text>
          </view>
          <view class="fitness-item">
            <text class="fitness-value">{{ teacherStats.completionRate }}%</text>
            <text class="fitness-label">本周任务</text>
          </view>
          <view class="fitness-item">
            <text class="fitness-value">{{ teacherStats.avgPace }}</text>
            <text class="fitness-label">平均配速</text>
          </view>
        </view>
        <view class="trend-bars" @click="goToSunshineBoard">
          <view class="t-bar-group" v-for="(d, i) in weeklyTrend" :key="i">
            <view class="t-bar" :style="{ height: d.val + '%', background: d.color }"></view>
            <text class="t-day">{{ d.day }}</text>
          </view>
        </view>
      </view>

      <view class="bottom-spacer"></view>
    </scroll-view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import {
  request,
  getTeacherTasks,
  getStoredUserInfo,
  patchStoredUserInfo,
  avatarImageSrc
} from '@/utils/request.js';

const userInfo = ref({});
const avatarDisplay = ref('/static/default-avatar.svg');
const todos = ref([]);
const activeTasks = ref([]);
const weeklyTrend = ref(defaultWeeklyTrend());
const abnormalAlerts = ref([]);

const teacherStats = ref({
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
});

const notificationIcon = computed(() => (
  notificationCount.value > 0
    ? '/static/icons/home-notification-unread.svg'
    : '/static/icons/home-notification.svg'
));

const displayName = computed(() => userInfo.value.name || '老师');
const notificationCount = computed(() => Math.min(99, teacherStats.value.abnormalCount || todos.value.length || 0));

const greeting = computed(() => {
  const hour = new Date().getHours();
  if (hour < 6) return '夜深了';
  if (hour < 12) return '上午好';
  if (hour < 18) return '下午好';
  return '晚上好';
});

const currentDate = computed(() => {
  const now = new Date();
  return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`;
});

const currentWeekday = computed(() => {
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
  return weekdays[new Date().getDay()];
});

const overviewItems = computed(() => ([
  {
    label: '进行中任务',
    value: activeTasks.value.length || teacherStats.value.taskCount,
    icon: '/static/icons/teacher-home-task.svg',
    path: '/pages/teacher/tasks/tasks'
  },
  {
    label: '学员总数',
    value: teacherStats.value.studentCount,
    icon: '/static/icons/teacher-students-total.svg',
    path: '/pages/teacher/students/students'
  },
  {
    label: '任务完成率',
    value: `${teacherStats.value.completionRate}%`,
    icon: '/static/icons/teacher-completion-rate.svg',
    path: '/pages/teacher/tasks/tasks'
  },
  {
    label: '待审批记录',
    value: teacherStats.value.pendingApprovals || teacherStats.value.pendingActivities,
    icon: '/static/icons/teacher-pending-record.svg',
    path: '/pages/teacher/exceptions/exceptions'
  }
]));

const quickActions = [
  { label: '发布任务', icon: '/static/icons/teacher-publish-task.svg', svg: true, tone: 'tone-green', path: '/pages/teacher/tasks/create' },
  { label: '学员管理', icon: '/static/icons/teacher-student-manage.svg', svg: true, tone: 'tone-blue', path: '/pages/teacher/students/students' },
  { label: '成绩审批', icon: '/static/icons/teacher-score-approval.svg', svg: true, tone: 'tone-orange', path: '/pages/teacher/students/students?showHealth=true' },
  { label: '数据统计', icon: '/static/icons/teacher-data-stats.svg', svg: true, tone: 'tone-purple', path: '/pages/teacher/sunshine/manage' }
];

const pendingItems = computed(() => ([
  {
    label: '请假申请',
    count: teacherStats.value.pendingHealth,
    icon: '/static/icons/teacher-pending-leave.svg',
    svg: true,
    tone: 'tone-green',
    path: '/pages/teacher/students/students?showHealth=true'
  },
  {
    label: '运动审批',
    count: teacherStats.value.pendingActivities,
    icon: '/static/icons/teacher-score-approval.svg',
    svg: true,
    tone: 'tone-orange',
    path: '/pages/teacher/exceptions/exceptions'
  },
  {
    label: '异常记录',
    count: teacherStats.value.abnormalCount,
    icon: '/static/icons/teacher-pending-alert.svg',
    svg: true,
    tone: 'tone-blue',
    path: '/pages/teacher/exceptions/exceptions'
  },
  {
    label: '系统消息',
    count: todos.value.length,
    icon: '/static/icons/teacher-pending-notification.svg',
    svg: true,
    tone: 'tone-purple',
    path: '/pages/teacher/notifications/list'
  }
]));

function defaultWeeklyTrend() {
  return [
    { day: '周一', val: 0, raw: 0, color: 'linear-gradient(180deg, #d8dde4 0%, #edf0f4 100%)' },
    { day: '周二', val: 0, raw: 0, color: 'linear-gradient(180deg, #d8dde4 0%, #edf0f4 100%)' },
    { day: '周三', val: 0, raw: 0, color: 'linear-gradient(180deg, #d8dde4 0%, #edf0f4 100%)' },
    { day: '周四', val: 0, raw: 0, color: 'linear-gradient(180deg, #20C997 0%, #76e3c6 100%)' },
    { day: '周五', val: 0, raw: 0, color: 'linear-gradient(180deg, #d8dde4 0%, #edf0f4 100%)' },
    { day: '周六', val: 0, raw: 0, color: 'linear-gradient(180deg, #d8dde4 0%, #edf0f4 100%)' },
    { day: '周日', val: 0, raw: 0, color: 'linear-gradient(180deg, #d8dde4 0%, #edf0f4 100%)' }
  ];
}

const syncAvatar = () => {
  avatarDisplay.value = avatarImageSrc(userInfo.value.avatar_url);
};

const fetchProfile = async () => {
  try {
    const res = await request({ url: '/users/profile', method: 'GET' });
    if (!res) return;
    userInfo.value = { ...getStoredUserInfo(), ...res };
    syncAvatar();
    patchStoredUserInfo(res);
  } catch (e) {
    console.error('fetch teacher profile failed', e);
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

    todos.value = Array.isArray(res.todos) ? res.todos : [];
  } catch (e) {
    if (!uni.getStorageSync('token')) return;
    console.error('Failed to fetch teacher stats:', e);
    todos.value = [];
  }
};

const fetchActiveTasks = async () => {
  try {
    const res = await getTeacherTasks({ page: 1, size: 2, status: 'active' });
    const items = Array.isArray(res.items) ? res.items : [];
    activeTasks.value = items.map((item, index) => {
      const completed = item.completed_count || 0;
      const total = item.total_students || 0;
      const percent = total > 0 ? Math.round((completed / total) * 100) : 0;
      return {
        id: item.id,
        title: item.title || '未命名任务',
        desc: item.description || (item.min_distance ? `目标：${item.min_distance}km` : '暂无任务说明'),
        deadline: item.deadline ? item.deadline.split('T')[0] : '未设置',
        completed,
        total,
        percent,
        icon: item.type === 'test' ? '/static/home-fitness-test.png' : '/static/home-outdoor-run.png',
        tone: index % 2 === 0 ? 'tone-green' : 'tone-purple'
      };
    });
  } catch (e) {
    if (!uni.getStorageSync('token')) return;
    console.error('Failed to fetch active tasks:', e);
    activeTasks.value = [];
  }
};

const fetchWeeklyTrend = async () => {
  try {
    const res = await request({
      url: '/teacher/weekly-sunshine-trend',
      method: 'GET'
    });
    if (Array.isArray(res) && res.length) {
      const maxVal = Math.max(...res.map(d => d.value || 0), 1);
      weeklyTrend.value = res.map(d => ({
        day: d.day,
        raw: d.value || 0,
        val: d.value > 0 ? Math.max(8, Math.round((d.value / maxVal) * 100)) : 0,
        color: d.value > 0
          ? 'linear-gradient(180deg, #20C997 0%, #76e3c6 100%)'
          : 'linear-gradient(180deg, #d8dde4 0%, #edf0f4 100%)'
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

const fetchAbnormalAlerts = async () => {
  try {
    const res = await request({
      url: '/teacher/students/abnormal',
      method: 'GET'
    });
    if (Array.isArray(res)) {
      abnormalAlerts.value = res.slice(0, 5);
    }
  } catch (e) {
    if (!uni.getStorageSync('token')) return;
    console.error('Failed to fetch abnormal alerts:', e);
  }
};

const navTo = (path) => {
  if (!path) return;
  uni.navigateTo({ url: path });
};

const goToTaskDetail = (task) => {
  uni.navigateTo({ url: `/pages/teacher/tasks/detail?id=${task.id}` });
};

const goToTodos = () => {
  uni.navigateTo({ url: '/pages/teacher/todos/index' });
};

const goToNotifications = () => {
  uni.navigateTo({ url: '/pages/teacher/notifications/list' });
};

const goToSunshineBoard = () => {
  uni.navigateTo({ url: '/pages/teacher/sunshine/manage' });
};

const goToProfileEdit = () => {
  uni.navigateTo({ url: '/pages/teacher/profile/edit' });
};

const onPageShow = () => {
  uni.hideHomeButton && uni.hideHomeButton();

  userInfo.value = getStoredUserInfo();
  syncAvatar();

  if (!uni.getStorageSync('token')) {
    uni.reLaunch({ url: '/pages/login/login' });
    return;
  }

  fetchProfile();
  fetchTeacherStats();
  fetchActiveTasks();
  fetchWeeklyTrend();
  fetchAbnormalAlerts();
};

onShow(() => {
  onPageShow();
});

defineExpose({
  onPageShow
});
</script>

<style scoped>
.teacher-home {
  min-height: 100vh;
  background: #f5f8fa;
  display: flex;
  flex-direction: column;
  max-width: 750rpx;
  margin: 0 auto;
}

.teacher-home__body {
  flex: 1;
  box-sizing: border-box;
  padding: 22rpx 24rpx 0;
  background: #f5f8fa;
}

.header-action {
  position: relative;
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-action__icon {
  width: 42rpx;
  height: 42rpx;
}

.header-action__badge,
.pending-badge {
  position: absolute;
  min-width: 32rpx;
  height: 32rpx;
  padding: 0 8rpx;
  box-sizing: border-box;
  border-radius: 18rpx;
  background: #ff4d5f;
  color: #fff;
  font-size: 20rpx;
  line-height: 32rpx;
  text-align: center;
}

.header-action__badge {
  top: 4rpx;
  right: 0;
}

.welcome-card,
.section-block {
  background: #fff;
  border-radius: 22rpx;
  border: 1rpx solid rgba(24, 35, 46, 0.06);
  box-shadow: 0 8rpx 22rpx rgba(24, 35, 46, 0.045);
}

.welcome-card {
  min-height: 156rpx;
  padding: 28rpx;
  display: flex;
  align-items: center;
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
}

.welcome-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 8rpx;
  background: #24bfa2;
}

.teacher-avatar {
  width: 92rpx;
  height: 92rpx;
  border-radius: 46rpx;
  background: #edf8f5;
  padding: 6rpx;
  box-sizing: border-box;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.welcome-copy {
  flex: 1;
  min-width: 0;
  padding: 0 14rpx 0 20rpx;
  display: flex;
  flex-direction: column;
}

.welcome-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #18232e;
  line-height: 1.25;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.welcome-subtitle {
  margin-top: 8rpx;
  font-size: 23rpx;
  color: #718094;
  line-height: 1.35;
}

.date-block {
  width: 124rpx;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  padding: 12rpx 0;
}

.date-text,
.weekday-text {
  font-size: 21rpx;
  color: #718094;
  line-height: 1.6;
  white-space: nowrap;
}

.weekday-text {
  color: #24bfa2;
  font-weight: 700;
}

.overview-panel {
  margin-top: 22rpx;
  padding: 28rpx;
  border-radius: 22rpx;
  background: #fff;
  color: #18232e;
  border: 1rpx solid rgba(24, 35, 46, 0.06);
  box-shadow: 0 10rpx 28rpx rgba(24, 35, 46, 0.045);
}

.overview-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.overview-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 23rpx;
  color: #718094;
}

.overview-date {
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: #eef9f6;
  color: #24bfa2;
  font-size: 23rpx;
  font-weight: 700;
  box-shadow: inset 0 0 0 1rpx rgba(36, 191, 162, 0.12);
}

.panel-title {
  font-size: 32rpx;
  font-weight: 700;
}

.panel-title--light {
  color: #18232e;
}

.overview-grid {
  margin-top: 24rpx;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14rpx;
}

.overview-item {
  min-width: 0;
  min-height: 124rpx;
  border-radius: 16rpx;
  background: #f8fafb;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0 20rpx;
  box-sizing: border-box;
  border: 1rpx solid rgba(24, 35, 46, 0.055);
}

.overview-item:last-child {
  border-right: 1rpx solid #eef2f5;
}

.overview-icon {
  width: 46rpx;
  height: 46rpx;
  flex-shrink: 0;
}

.overview-copy {
  min-width: 0;
  margin-left: 18rpx;
  display: flex;
  flex-direction: column;
}

.overview-value {
  font-size: 36rpx;
  font-weight: 800;
  line-height: 1.1;
  color: #18232e;
}

.overview-label {
  margin-top: 8rpx;
  font-size: 23rpx;
  color: #718094;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.section-block {
  margin-top: 22rpx;
  padding: 26rpx;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22rpx;
}

.section-title {
  font-size: 31rpx;
  font-weight: 700;
  color: #18232e;
}

.section-more {
  display: flex;
  align-items: center;
  color: #718094;
  font-size: 25rpx;
  line-height: 1;
}

.more-arrow {
  width: 14rpx;
  height: 14rpx;
  margin-left: 10rpx;
  border-top: 3rpx solid currentColor;
  border-right: 3rpx solid currentColor;
  transform: rotate(45deg);
}

.quick-grid,
.pending-grid {
  display: grid;
}

.quick-grid {
  grid-template-columns: repeat(4, 1fr);
  gap: 8rpx;
}

.pending-grid {
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
}

.quick-item {
  position: relative;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pending-item {
  position: relative;
  min-width: 0;
  min-height: 118rpx;
  border-radius: 18rpx;
  background: #f8fafb;
  border: 1rpx solid rgba(24, 35, 46, 0.055);
  display: flex;
  align-items: center;
  padding: 0 20rpx;
  box-sizing: border-box;
}

.quick-icon-wrap,
.pending-icon-wrap {
  position: relative;
  width: 80rpx;
  height: 80rpx;
  border-radius: 18rpx;
  background: #f2f8f7;
  border: 1rpx solid rgba(36, 191, 162, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.quick-icon,
.pending-icon,
.task-mark__icon {
  width: 42rpx;
  height: 42rpx;
}

.quick-icon.is-svg-icon,
.pending-icon.is-svg-icon,
.task-mark__icon.is-svg-icon {
  filter: none;
}

.quick-icon:not(.is-svg-icon),
.pending-icon:not(.is-svg-icon),
.task-mark__icon:not(.is-svg-icon) {
  width: 58rpx;
  height: 58rpx;
}

.quick-label {
  margin-top: 16rpx;
  font-size: 26rpx;
  color: #18232e;
  font-weight: 600;
}

.tone-green {
  background: #f2f8f7;
}

.tone-blue {
  background: #f2f8f7;
}

.tone-orange {
  background: #f2f8f7;
}

.tone-purple {
  background: #f2f8f7;
}

.task-list {
  display: flex;
  flex-direction: column;
}

.task-row {
  display: flex;
  align-items: center;
  min-height: 148rpx;
  padding: 24rpx 0;
  border-bottom: 1rpx solid rgba(24, 35, 46, 0.06);
}

.task-row:last-child {
  border-bottom: none;
}

.task-mark {
  width: 80rpx;
  height: 80rpx;
  border-radius: 18rpx;
  border: 1rpx solid rgba(36, 191, 162, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.task-info {
  flex: 1;
  min-width: 0;
  padding: 0 22rpx;
  display: flex;
  flex-direction: column;
}

.task-title-row {
  display: flex;
  align-items: center;
  min-width: 0;
}

.task-title {
  max-width: 330rpx;
  font-size: 30rpx;
  font-weight: 700;
  color: #18232e;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-status {
  margin-left: 14rpx;
  padding: 4rpx 12rpx;
  border-radius: 999rpx;
  background: #eef9f6;
  color: #24bfa2;
  font-size: 22rpx;
  flex-shrink: 0;
}

.task-desc,
.task-meta {
  margin-top: 10rpx;
  font-size: 25rpx;
  color: #718094;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.progress-ring {
  --percent: 0;
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: conic-gradient(#24bfa2 calc(var(--percent) * 1%), #e7edf0 0);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
}

.progress-ring::after {
  content: '';
  position: absolute;
  inset: 9rpx;
  border-radius: 50%;
  background: #fff;
}

.progress-value,
.progress-label {
  position: relative;
  z-index: 1;
}

.progress-value {
  font-size: 27rpx;
  color: #18232e;
  font-weight: 800;
  line-height: 1;
}

.progress-label {
  margin-top: 6rpx;
  color: #24bfa2;
  font-size: 18rpx;
}

.pending-icon-wrap {
  width: 70rpx;
  height: 70rpx;
}

.pending-badge {
  top: -12rpx;
  right: -14rpx;
}

.pending-copy {
  min-width: 0;
  margin-left: 18rpx;
  display: flex;
  flex-direction: column;
}

.pending-count {
  font-size: 34rpx;
  color: #18232e;
  font-weight: 800;
  line-height: 1.2;
}

.pending-label {
  margin-top: 6rpx;
  color: #718094;
  font-size: 25rpx;
}

.fitness-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14rpx;
}

.fitness-item {
  min-height: 108rpx;
  border-radius: 16rpx;
  background: #f8fafb;
  border: 1rpx solid rgba(24, 35, 46, 0.055);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.fitness-value {
  font-size: 34rpx;
  color: #18232e;
  font-weight: 800;
}

.fitness-label {
  margin-top: 8rpx;
  color: #718094;
  font-size: 24rpx;
}

.trend-bars {
  height: 150rpx;
  margin-top: 26rpx;
  padding: 0 8rpx;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-top: 1rpx solid rgba(24, 35, 46, 0.06);
}

.t-bar-group {
  height: 124rpx;
  width: 60rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
}

.t-bar {
  width: 18rpx;
  min-height: 8rpx;
  border-radius: 12rpx;
}

.t-day {
  margin-top: 12rpx;
  color: #718094;
  font-size: 22rpx;
}

.empty-state {
  min-height: 112rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8a9390;
  font-size: 26rpx;
}

.bottom-spacer {
  height: 44rpx;
}
</style>
