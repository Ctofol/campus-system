<template>
  <view class="home-page">
    <page-tab-header title="首页" theme="brand" />
    <view class="home-scroll" :style="{ paddingBottom: safeBottom + 'px' }">
      <view class="home-hero">
        <!-- 顶栏：日历通知 -->
        <view class="home-hero__actions">
          <view class="home-hero__action" @tap="goSunshineDetail">
            <image class="home-hero__action-icon-img" src="/static/icons/home-calendar.svg" mode="aspectFit" />
            <text class="home-hero__action-label">日历</text>
          </view>
          <view class="home-hero__action home-hero__action--notif" @tap="goNotifications">
            <image
              class="home-hero__action-icon-img"
              :src="unreadNotifyCount > 0 ? '/static/icons/home-notification-unread.svg' : '/static/icons/home-notification.svg'"
              mode="aspectFit"
            />
            <text
              v-if="unreadNotifyCount > 0"
              class="home-hero__badge"
            >{{ unreadNotifyCount > 99 ? '99+' : unreadNotifyCount }}</text>
            <text class="home-hero__action-label">通知</text>
          </view>
        </view>

        <!-- 居中问候 -->
        <view class="home-hero__greet">
          <text class="home-hero__greet-title">{{ greetingText }}</text>
          <text class="home-hero__greet-sub">{{ greetingSub }}</text>
        </view>

        <!-- 天气信息 -->
        <view class="home-hero__bottom">
          <HomeWeatherCard :weather="homeWeather" :placeholder="!homeWeatherReady" />
        </view>
      </view>

      <HomeQuickStartCard
        :distance-km="totalDistanceKm"
        :goal-km="runGoalKm"
        :goal-progress="weekGoalProgress"
        :goal-hint="goalHintText"
        @go="showExerciseActionSheet"
        @settings="onRunSettings"
        @set-goal="openGoalModal"
      />

      <view class="home-body">
        <view class="home-card home-card--grid">
          <HomeFeatureGrid :items="featureItems" @feature-tap="onFeatureTap" />
        </view>

        <view class="home-activity-section">
          <HomeSectionHeader title="最新活动" more-text="查看全部" @more="goActivityList" />
          <HomeActivityCard :activity="latestActivity" :loading="loading" @tap="goActivityDetail" />
        </view>

        <view class="home-card">
          <HomeSectionHeader title="本周数据" more-text="查看全部" @more="viewHistory" />
          <text class="home-card__sub">{{ weeklySubTitle }}</text>
          <HomeWeekStats
            :stats="weeklyStats"
            :loading="loading"
            @start-run="startOutdoorRun"
          />
        </view>

        <view class="home-card">
          <HomeSectionHeader title="最近任务" more-text="全部任务" @more="handleTaskClick" />
          <view v-if="loading" class="home-recent__skeleton">
            <view v-for="i in 3" :key="i" class="home-recent__sk-row" />
          </view>
          <view v-else-if="!teacherTasks.length" class="home-task-empty">
            <text class="home-task-empty-txt">暂无教师发布的任务</text>
          </view>
          <view v-else class="home-task-list">
            <view
              v-for="task in teacherTasks"
              :key="task.id"
              class="home-task-item"
              @click="handleTaskClick(task)"
            >
              <view class="home-task-left">
                <view class="home-task-status-dot" :class="'home-task-status-dot--' + task.status" />
                <view class="home-task-info">
                  <view class="home-task-title-row">
                    <text class="home-task-title">{{ task.title }}</text>
                    <text class="home-task-badge" :class="'home-task-badge--' + task.status">{{ taskStatusLabel(task.status) }}</text>
                  </view>
                  <text class="home-task-desc">{{ task.desc }}</text>
                </view>
              </view>
              <text class="home-task-arrow">›</text>
            </view>
          </view>
        </view>
      </view>

      <view style="height: 32rpx;" />
    </view>

    <!-- 本周跑步目标 -->
    <view v-if="showGoalModal" class="home-overlay" @tap="closeGoalModal">
      <view class="home-goal-panel" @tap.stop>
        <text class="home-goal-panel__title">设置本周跑步目标</text>
        <text class="home-goal-panel__hint">按自然周（周一至周日）统计里程</text>
        <view class="home-goal-panel__input-row">
          <input
            v-model="goalInput"
            class="home-goal-panel__input"
            type="digit"
            placeholder="例如 15"
          />
          <text class="home-goal-panel__unit">公里 / 周</text>
        </view>
        <view class="home-goal-panel__btns">
          <view class="home-goal-panel__btn home-goal-panel__btn--ghost" @tap="clearGoal">清除目标</view>
          <view class="home-goal-panel__btn home-goal-panel__btn--primary" @tap="saveGoal">保存</view>
        </view>
      </view>
    </view>

    <!-- 新任务通知弹窗（设计稿风格，逐条展示） -->
    <view v-if="showTaskModal" class="notif-overlay" @tap="closeTaskModal">
      <view
        class="notif-card"
        :class="'notif-card--' + currentNotifTheme"
        @tap.stop
      >
        <!-- 关闭按钮 -->
        <image class="notif-close-img" src="/static/icons/icon-cross.svg" mode="aspectFit" @tap="closeTaskModal" />

        <!-- 顶部图标 -->
        <view class="notif-icon-wrap" :class="'notif-icon-wrap--' + currentNotifTheme">
          <image class="notif-icon-img" :src="currentNotifIcon" mode="aspectFit" />
        </view>

        <!-- 类型标签 -->
        <text class="notif-type" :class="'notif-type--' + currentNotifTheme">{{ currentNotifTypeLabel }}</text>

        <!-- 标题 -->
        <text class="notif-title">{{ currentTask.title }}</text>

        <!-- 详情列表 -->
        <view class="notif-rows">
          <view v-if="currentTask.starts_at" class="notif-row">
            <text class="notif-row-label">开始时间：</text>
            <text class="notif-row-val">{{ currentTask.starts_at }}</text>
          </view>
          <view v-if="currentTask.deadline" class="notif-row">
            <text class="notif-row-label">截止时间：</text>
            <text class="notif-row-val">{{ currentTask.deadline }}</text>
          </view>
          <view v-if="currentTask.min_distance" class="notif-row">
            <text class="notif-row-label">单次要求：</text>
            <text class="notif-row-val">距离不少于 {{ currentTask.min_distance }} 公里</text>
          </view>
        </view>

        <!-- 提示框 -->
        <view v-if="currentTask.desc" class="notif-tip" :class="'notif-tip--' + currentNotifTheme">
          <image class="notif-tip-icon-img" src="/static/icons/home-notification-unread.svg" mode="aspectFit" />
          <text class="notif-tip-text">{{ currentTask.desc }}</text>
        </view>

        <!-- 发布人 -->
        <view class="notif-footer">
          <text class="notif-publisher">发布人：{{ currentTask.publisher || '体育部老师' }}</text>
          <text class="notif-time">{{ currentTask.publishTime || '今天' }}</text>
        </view>

        <!-- 多任务分页点 -->
        <view v-if="teacherTasks.length > 1" class="notif-dots">
          <view
            v-for="(_, i) in teacherTasks"
            :key="i"
            class="notif-dot"
            :class="{ 'notif-dot--active': i === notifIndex }"
            @tap="notifIndex = i"
          />
        </view>

        <!-- 操作按钮 -->
        <view class="notif-btns">
          <view
            class="notif-btn notif-btn--primary"
            :class="'notif-btn--' + currentNotifTheme"
            @tap="handleNotifConfirm"
          >
            <text>{{ notifIndex < teacherTasks.length - 1 ? '下一条' : '我知道了' }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { getStoredToken } from '@/utils/request.js';
import { warmUpLocationCache } from '@/utils/location.js';
import { fetchWeather } from '@/utils/weather.js';
import { saveRunGoalKm } from '@/utils/run-goal.js';
import { useStudentHomeDashboard } from '@/composables/useStudentHomeDashboard.js';
import HomeWeatherCard from './HomeWeatherCard.vue';
import HomeQuickStartCard from './HomeQuickStartCard.vue';
import HomeFeatureGrid from './HomeFeatureGrid.vue';
import HomeSectionHeader from './HomeSectionHeader.vue';
import HomeWeekStats from './HomeWeekStats.vue';
import HomeActivityCard from './HomeActivityCard.vue';
import PageTabHeader from '@/components/page-tab-header/page-tab-header.vue';

const safeBottom = ref(0);
const refreshing = ref(false);
const showTaskModal = ref(false);
const showGoalModal = ref(false);
const notifIndex = ref(0);
const goalInput = ref('');
const homeWeather = ref(null);
const homeWeatherReady = ref(false);
const HOME_RELOAD_DEDUPE_MS = 30000;
let lastReloadAt = 0;
let reloadPromise = null;
let mountedByPageShow = false;

const {
  loading,
  greetingText,
  greetingSub,
  weeklySubTitle,
  totalDistanceKm,
  weeklyStats,
  recentRuns,
  teacherTasks,
  unreadNotifyCount,
  runGoalKm,
  weekGoalProgress,
  goalHintText,
  latestActivity,
  loadDashboard,
  applyRunGoal
} = useStudentHomeDashboard();

const featureItems = [
  { id: 'outdoor', icon: '/static/home-outdoor-run.png', iconScale: 1.08, label: '户外跑', desc: '记录户外路线' },
  { id: 'test', icon: '/static/home-fitness-test.png', iconScale: 0.9, label: '体能测试', desc: '评估身体状态' },
  { id: 'learn', icon: '/static/home-course.png', iconScale: 0.92, label: '课程', desc: '科学训练指导' },
  { id: 'rungroup', icon: '/static/home-run-group.png', iconScale: 1.02, label: '跑团', desc: '一起跑步' },
  { id: 'ai', icon: '/static/icons/icon-ai.svg', iconScale: 0.92, label: 'AI助手', desc: '训练建议问答' }
];

const checkNewTasks = (tasks) => {
  if (!tasks?.length) return;
  const viewedIds = uni.getStorageSync('viewed_task_ids') || [];
  const hasNew = tasks.some((t) => !viewedIds.includes(t.id));
  if (hasNew) {
    notifIndex.value = 0;
    showTaskModal.value = true;
  }
};

const showNavFailToast = (title) => {
  uni.showToast({ title, icon: 'none' });
};

const navigateToPage = (url, failTitle = '页面打开失败') => {
  uni.navigateTo({
    url,
    fail: (e) => {
      console.error('navigateTo fail', url, e);
      showNavFailToast(failTitle);
    }
  });
};

const switchToTab = (url, failTitle = '页面打开失败') => {
  uni.switchTab({
    url,
    fail: (e) => {
      console.error('switchTab fail', url, e);
      showNavFailToast(failTitle);
    }
  });
};

const startOutdoorRun = () => {
  navigateToPage('/pages/run/run', '跑步页面打开失败');
};

const startPhysicalTest = () => {
  navigateToPage('/pages/test/test', '体测页面打开失败');
};

const startAiTest = () => {
  navigateToPage('/pages/test/test', '体测页面打开失败');
};

const startFreeExercise = () => {
  navigateToPage('/pages/sport/free-practice', '自由练习打开失败');
};

const showExerciseActionSheet = () => {
  uni.showActionSheet({
    itemList: ['户外跑步', '体测'],
    success: (res) => {
      if (res.tapIndex === 0) startOutdoorRun();
      else if (res.tapIndex === 1) startAiTest();
      else if (res.tapIndex === 2) startFreeExercise();
    }
  });
};

const onFeatureTap = (id) => {
  if (id === 'outdoor') startOutdoorRun();
  else if (id === 'test') startPhysicalTest();
  else if (id === 'learn') switchToTab('/pages/tab/learn', '课程页面打开失败');
  else if (id === 'rungroup') navigateToPage('/pages/run-group/discover', '跑团页面打开失败');
  else if (id === 'ai') navigateToPage('/pages/ai-assistant/index', 'AI助手打开失败');
};

const onRunSettings = () => {
  uni.showActionSheet({
    itemList: ['运动记录', '阳光跑规则'],
    success: (res) => {
      if (res.tapIndex === 0) viewHistory();
      else if (res.tapIndex === 1) goSunshineDetail();
    }
  });
};

const openGoalModal = () => {
  goalInput.value = runGoalKm.value > 0 ? String(runGoalKm.value) : '';
  showGoalModal.value = true;
};

const closeGoalModal = () => {
  showGoalModal.value = false;
};

const saveGoal = async () => {
  const n = Number(goalInput.value);
  if (!Number.isFinite(n) || n <= 0) {
    uni.showToast({ title: '请输入有效公里数', icon: 'none' });
    return;
  }
  try {
    const km = await saveRunGoalKm(n);
    applyRunGoal(km);
    closeGoalModal();
    uni.showToast({ title: '目标已保存', icon: 'success' });
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' });
  }
};

const clearGoal = async () => {
  try {
    await saveRunGoalKm(0);
    applyRunGoal(0);
    closeGoalModal();
    uni.showToast({ title: '已清除目标', icon: 'none' });
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' });
  }
};

const handleTaskClick = (task) => {
  if (task?.id) {
    navigateToPage(`/pages/student/tasks/list?taskId=${task.id}`, '任务页面打开失败');
  } else {
    navigateToPage('/pages/student/tasks/list', '任务页面打开失败');
  }
};

const taskStatusLabel = (status) => {
  const map = { pending: '待开始', in_progress: '进行中', uncompleted: '未完成', not_started: '未开始', failed: '未通过' };
  return map[status] || '待开始';
};

const closeTaskModal = () => {
  showTaskModal.value = false;
  notifIndex.value = 0;
  const viewedIds = uni.getStorageSync('viewed_task_ids') || [];
  const newIds = teacherTasks.value.map((t) => t.id);
  uni.setStorageSync('viewed_task_ids', [...new Set([...viewedIds, ...newIds])]);
};

const handleNotifConfirm = () => {
  if (notifIndex.value < teacherTasks.value.length - 1) {
    notifIndex.value++;
  } else {
    closeTaskModal();
  }
};

const viewHistory = () => {
  navigateToPage('/pages/history/history', '历史记录打开失败');
};

const goSunshineDetail = () => {
  navigateToPage('/pages/sunshine/detail', '阳光跑详情打开失败');
};

const goNotifications = () => {
  navigateToPage('/pages/student/notifications/list', '通知页面打开失败');
};

const goRunDetail = (run) => {
  const payload = run?.activity || run?.raw;
  if (!payload) {
    viewHistory();
    return;
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

const goActivityList = () => {
  navigateToPage('/pages/activity/list', '活动列表打开失败');
};

const goActivityDetail = (activity) => {
  if (activity?.id) {
    navigateToPage(`/pages/run-group/activity-detail?activityId=${activity.id}`, '活动详情打开失败');
  } else {
    goActivityList();
  }
};

const getTaskTypeIcon = (task) => {
  if (
    task.type === 'learn' ||
    task.type === 'learning' ||
    task.title?.includes('课程') ||
    task.title?.includes('学习')
  ) {
    return '/static/icons/icon-course.svg';
  }
  return '/static/icons/icon-route.svg';
};

// 通知弹窗 computed
const currentTask = computed(() => teacherTasks.value[notifIndex.value] || {});

const currentNotifTheme = computed(() => {
  const t = currentTask.value;
  if (t.type === 'leave' || t.title?.includes('请假') || t.title?.includes('审批')) return 'orange';
  if (t.type === 'run' || t.title?.includes('跑') || t.title?.includes('打卡')) return 'purple';
  return 'green';
});

const currentNotifIcon = computed(() => {
  const theme = currentNotifTheme.value;
  if (theme === 'orange') return '/static/icons/icon-data.svg';
  if (theme === 'purple') return '/static/icons/icon-route.svg';
  return '/static/icons/icon-data.svg';
});

const currentNotifTypeLabel = computed(() => {
  const t = currentTask.value;
  if (t.title?.includes('请假') || t.title?.includes('审批')) return '请假审批通知';
  if (t.title?.includes('跑') || t.title?.includes('打卡')) return '晨跑打卡通知';
  return '考核通知';
});

const loadHomeWeather = async () => {
  const res = await fetchWeather();
  if (res.ok && res.weather) {
    homeWeather.value = res.weather;
    homeWeatherReady.value = true;
  } else {
    homeWeatherReady.value = false;
  }
};

const reloadAll = async ({ force = false } = {}) => {
  const now = Date.now();
  if (!force && lastReloadAt && now - lastReloadAt < HOME_RELOAD_DEDUPE_MS) {
    warmUpLocationCache();
    return;
  }
  if (reloadPromise) return reloadPromise;

  reloadPromise = Promise.all([loadDashboard(checkNewTasks), loadHomeWeather()])
    .then(() => {
      lastReloadAt = Date.now();
      warmUpLocationCache();
    })
    .finally(() => {
      reloadPromise = null;
    });

  return reloadPromise;
};

const onPullRefresh = async () => {
  refreshing.value = true;
  await reloadAll({ force: true });
  refreshing.value = false;
};

const onPageShow = async () => {
  mountedByPageShow = true;
  const sys = uni.getSystemInfoSync();
  safeBottom.value = sys.safeAreaInsets?.bottom || 0;

  if (!getStoredToken()) {
    uni.reLaunch({ url: '/pages/login/login' });
    return;
  }

  // Proactively request location permission on new devices
  // #ifdef MP-WEIXIN
  uni.getSetting({
    success: (res) => {
      if (!res.authSetting['scope.userLocation']) {
        uni.authorize({
          scope: 'scope.userLocation',
          fail: () => {
            // silent fail - user will be prompted on run page
          }
        });
      }
    }
  });
  // #endif

  await reloadAll();
};

onMounted(() => {
  setTimeout(() => {
    if (!mountedByPageShow) onPageShow();
  }, 0);
});

defineExpose({
  onPageShow
});
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

.section-more .link-arrow {
  border-color: #999;
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
