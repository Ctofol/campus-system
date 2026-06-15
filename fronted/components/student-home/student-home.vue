<template>
  <view class="home-page">
    <page-tab-header title="首页" theme="brand" />
    <scroll-view
      scroll-y
      class="home-scroll"
      :style="{ paddingBottom: safeBottom + 'px' }"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onPullRefresh"
    >
      <view class="home-hero">
        <!-- 顶栏：居中标题胶囊 + 日历通知 -->
        <view class="home-hero__topbar">
          <view class="home-hero__title-capsule">
            <text class="home-hero__title">首页</text>
          </view>
          <view class="home-hero__actions">
            <view class="home-hero__action" @tap="goSunshineDetail">
              <image class="home-hero__action-icon-img" src="/static/日历.png" mode="aspectFit" />
              <text class="home-hero__action-label">日历</text>
            </view>
            <view class="home-hero__action home-hero__action--notif" @tap="goNotifications">
              <image class="home-hero__action-icon-img" src="/static/通知图标2.png" mode="aspectFit" />
              <text
                v-if="unreadNotifyCount > 0"
                class="home-hero__badge"
              >{{ unreadNotifyCount > 99 ? '99+' : unreadNotifyCount }}</text>
              <text class="home-hero__action-label">通知</text>
            </view>
          </view>
        </view>

        <!-- 居中问候 -->
        <view class="home-hero__greet">
          <text class="home-hero__greet-title">{{ greetingText }}{{ greetingIcon }}</text>
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
          <HomeFeatureGrid :items="featureItems" @tap="onFeatureTap" />
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
          <HomeSectionHeader title="最近活动" more-text="全部任务" @more="handleTaskClick" />
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
    </scroll-view>

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
        <image class="notif-close-img" src="/static/叉号图标.png" mode="aspectFit" @tap="closeTaskModal" />

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
          <image class="notif-tip-icon-img" src="/static/通知图标（收到通知红点版）.png" mode="aspectFit" />
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

const {
  loading,
  greetingText,
  greetingIcon,
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
  { id: 'outdoor', icon: '/static/主页户外跑图标.png', label: '户外跑', desc: '记录户外路线' },
  { id: 'test', icon: '/static/主页体能测试图标.png', label: '体能测试', desc: '评估身体状态' },
  { id: 'learn', icon: '/static/主页课程图标.png', label: '课程', desc: '科学训练指导' },
  { id: 'rungroup', icon: '/static/主页跑团图标.png', label: '跑团', desc: '一起跑步' }
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
  else if (id === 'learn') uni.switchTab({ url: '/pages/tab/learn' });
  else if (id === 'rungroup') uni.navigateTo({ url: '/pages/run-group/discover' });
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
    uni.navigateTo({ url: `/pages/student/tasks/list?taskId=${task.id}` });
  } else {
    uni.navigateTo({ url: '/pages/student/tasks/list' });
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
  uni.navigateTo({ url: '/pages/history/history' });
};

const goSunshineDetail = () => {
  uni.navigateTo({ url: '/pages/sunshine/detail' });
};

const goNotifications = () => {
  uni.navigateTo({ url: '/pages/student/notifications/list' });
};

const goRunDetail = (run) => {
  const payload = run?.activity || run?.raw;
  if (!payload) {
    viewHistory();
    return;
  }
  try {
    const dataStr = encodeURIComponent(JSON.stringify(payload));
    uni.navigateTo({ url: `/pages/history/detail?data=${dataStr}` });
  } catch (e) {
    console.error('Go detail failed', e);
  }
};

const goActivityList = () => {
  uni.navigateTo({ url: '/pages/activity/list' });
};

const goActivityDetail = (activity) => {
  if (activity?.id) {
    uni.navigateTo({ url: `/pages/run-group/activity-detail?activityId=${activity.id}` });
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
    return '/static/主页课程图标.png';
  }
  return '/static/主页户外跑图标.png';
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
  if (theme === 'orange') return '/static/数据图标.png';
  if (theme === 'purple') return '/static/主页户外跑图标.png';
  return '/static/数据图标.png';
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

const reloadAll = async () => {
  await Promise.all([loadDashboard(checkNewTasks), loadHomeWeather()]);
  warmUpLocationCache();
};

const onPullRefresh = async () => {
  refreshing.value = true;
  await reloadAll();
  refreshing.value = false;
};

const onPageShow = async () => {
  const sys = uni.getSystemInfoSync();
  safeBottom.value = sys.safeAreaInsets?.bottom || 0;

  if (!getStoredToken()) {
    uni.reLaunch({ url: '/pages/login/login' });
    return;
  }

  await reloadAll();
};

onMounted(() => {
  onPageShow();
});

defineExpose({
  onPageShow
});
</script>

<style scoped lang="scss">
@import './home-dashboard.scss';
</style>
