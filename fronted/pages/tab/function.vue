<template>
  <view class="sport-container">
    <view v-if="role === 'student'" class="student-sport">
      <page-tab-header title="运动" theme="brand" />

      <view class="content-wrapper page-tab-body page-tab-body--compact-top">
        <!-- 运动入口卡片（2列） -->
        <view class="entry-grid">
          <view class="entry-card" @click="goToRun">
            <view class="entry-icon-wrap">
              <view class="entry-icon entry-icon--run">
                <image class="entry-icon-text" src="/static/home-outdoor-run.png" mode="aspectFit" />
              </view>
            </view>
            <view class="entry-info">
              <text class="entry-title">户外跑步</text>
              <text class="entry-desc">GPS定位，实时记录轨迹</text>
            </view>
            <text class="entry-arrow">›</text>
          </view>
          <view class="entry-card" @click="goToPhysicalTest">
            <view class="entry-icon-wrap">
              <view class="entry-icon entry-icon--test">
                <image class="entry-icon-text" src="/static/home-fitness-test.png" mode="aspectFit" />
              </view>
            </view>
            <view class="entry-info">
              <text class="entry-title">体能测试</text>
              <text class="entry-desc">标准体测项目</text>
            </view>
            <text class="entry-arrow">›</text>
          </view>
        </view>

        <!-- 阳光跑看板 / 今日状态 -->
        <view class="today-card page-card" @click="goToSunshineDetail">
          <view class="card-header">
            <text class="card-title">今日状态</text>
          </view>
          <view class="today-body">
            <view class="today-ring-wrap">
              <view class="today-ring" :style="ringStyle">
                <view class="today-ring-inner">
                  <text class="today-ring-label">当前积分</text>
                  <view class="today-ring-row">
                    <text class="today-ring-num">{{ sunshine.current_score || sunshine.score }}</text>
                    <text class="today-ring-unit">分</text>
                  </view>
                </view>
              </view>
            </view>
              <view class="today-indicators">
              <view class="today-indicator">
                <image class="today-ind-emoji-img" src="/static/sport-today-status.png" mode="aspectFit" />
                <view class="today-ind-body">
                  <text class="today-ind-label">今日状态</text>
                  <text class="today-ind-val today-ind-val--ok" v-if="sunshine.today_status === 'success'">审核通过</text>
                  <text class="today-ind-val today-ind-val--pending" v-else>未开始</text>
                </view>
              </view>
              <view class="today-indicator">
                <image class="today-ind-emoji-img" src="/static/sport-checkin-status.png" mode="aspectFit" />
                <view class="today-ind-body">
                  <text class="today-ind-label">打卡状态</text>
                  <text class="today-ind-val today-ind-val--fail" v-if="sunshine.today_status === 'failed'">审核未通过：{{ sunshine.today_fail_reason || '里程不足' }}</text>
                  <text class="today-ind-val today-ind-val--ok" v-else-if="sunshine.today_status === 'success'">已完成打卡</text>
                  <text class="today-ind-val today-ind-val--pending" v-else>待打卡</text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 运动数据概览 -->
        <view class="overview-card page-card">
          <view class="card-header">
            <text class="card-title">运动数据概览</text>
          </view>
          <view class="overview-grid">
            <view class="overview-item">
              <image class="overview-icon" src="/static/stats-distance-2.png" mode="aspectFit" />
              <text class="overview-val">{{ totalStats.distance }}</text>
              <text class="overview-unit">总里程(km)</text>
            </view>
            <view class="overview-item">
              <image class="overview-icon" src="/static/stats-duration-2.png" mode="aspectFit" />
              <text class="overview-val">{{ totalStats.duration }}</text>
              <text class="overview-unit">总时长(min)</text>
            </view>
            <view class="overview-item">
              <image class="overview-icon" src="/static/stats-calories.png" mode="aspectFit" />
              <text class="overview-val">{{ totalStats.calories }}</text>
              <text class="overview-unit">总消耗(kcal)</text>
            </view>
            <view class="overview-item">
              <image class="overview-icon" src="/static/icon-sport-count.png" mode="aspectFit" />
              <text class="overview-val">{{ totalStats.count }}</text>
              <text class="overview-unit">运动次数</text>
            </view>
          </view>
        </view>

        <!-- 训练计划（教师任务） -->
        <view class="plan-card page-card" v-if="activeTask" @click="goToTask(activeTask)">
          <view class="card-header">
            <text class="card-title">训练计划</text>
            <view class="card-more" @click.stop="goToTaskList">
              <text>全部计划</text>
              <text class="card-more-arrow">›</text>
            </view>
          </view>
          <view class="plan-body">
            <view class="plan-body-left">
              <view class="plan-icon">
                <image class="plan-icon-img" src="/static/icons/icon-training.svg" mode="aspectFit" />
              </view>
              <view class="plan-info">
                <text class="plan-name">{{ activeTask.title }}</text>
                <view class="plan-meta">
                  <text class="plan-meta-item" v-if="activeTask.weekLabel">{{ activeTask.weekLabel }}</text>
                  <text class="plan-meta-item" v-if="activeTask.progress">{{ activeTask.progress }}</text>
                </view>
                <view class="plan-bar">
                  <view class="plan-bar-fill" :style="{ width: activeTask.progressPercent + '%' }"></view>
                </view>
                <text class="plan-bar-label">{{ activeTask.progressPercent }}%</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 最近运动记录 -->
        <view class="history-card page-card">
          <view class="card-header">
            <text class="card-title">最近运动记录</text>
            <view class="card-more" @click="goToHistory">
              <text>全部记录</text>
              <text class="card-more-arrow">›</text>
            </view>
          </view>
          <HomeRecentList
            :items="recentRecords"
            :loading="loading"
            @detail="goToHistory"
            @start-run="goToHistory"
          />
        </view>

        <view style="height: 32rpx;"></view>
      </view>
    </view>

    <teacher-manage v-else ref="teacherManageRef" />
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { onShow, onHide } from '@dcloudio/uni-app';
import TeacherManage from '@/components/teacher-manage/teacher-manage.vue';
import HomeRecentList from '@/components/student-home/HomeRecentList.vue';
import { request, getSunshineStats, getStudentTasks } from '@/utils/request.js';
import { applyRoleTabBar } from '@/utils/role-tabbar.js';

const role = ref('student');
const teacherManageRef = ref(null);

const totalStats = ref({
  distance: 0, duration: 0, calories: 0, count: 0
});

const sunshine = ref({
  total_valid_count: 0, current_score: 0, score: 0,
  today_status: 'not_started', today_fail_reason: ''
});

const recentRecords = ref([]);
const loading = ref(false);
const activeTask = ref(null);

const ringStyle = computed(() => {
  const max = 40;
  const n = Math.min(Number(sunshine.value.total_valid_count) || 0, max);
  const deg = (n / max) * 360;
  return { background: `conic-gradient(#33C9AB 0deg ${deg}deg, #e5e7eb ${deg}deg 360deg)` };
});

const goToRun = () => uni.navigateTo({ url: '/pages/run/run' });
const goToPhysicalTest = () => uni.navigateTo({ url: '/pages/test/test' });
const goToSunshineDetail = () => {
  if (role.value !== 'student') return;
  uni.navigateTo({ url: '/pages/sunshine/detail' });
};
const goToHistory = () => uni.navigateTo({ url: '/pages/history/history' });
const goToTaskList = () => uni.navigateTo({ url: '/pages/student/tasks/list' });
const goToTask = (task) => {
  if (task?.taskId) {
    uni.navigateTo({ url: `/pages/student/tasks/list?taskId=${task.taskId}` });
  }
};

const fetchTotalStats = async () => {
  try {
    const res = await request({ url: '/student/total-stats', method: 'GET' });
    totalStats.value = {
      distance: res.total_distance ? res.total_distance.toFixed(1) : 0,
      duration: res.total_duration || 0,
      calories: res.total_calories || 0,
      count: res.total_count || 0
    };
  } catch (e) {
    totalStats.value = { distance: 0, duration: 0, calories: 0, count: 0 };
  }
};

const fetchSunshineStats = async () => {
  try {
    const res = await getSunshineStats();
    sunshine.value = {
      total_valid_count: res.total_valid_count || 0,
      current_score: res.current_score || res.score || 0,
      score: res.score || 0,
      today_status: res.today_status || 'not_started',
      today_fail_reason: res.today_fail_reason || ''
    };
  } catch (e) { /* ignore */ }
};

const fetchRecentRecords = async () => {
  loading.value = true;
  try {
    const res = await request({ url: '/student/home/dashboard', method: 'GET' });
    const runs = res?.recent_runs || [];
    recentRecords.value = runs.slice(0, 3).map(r => ({
      id: r.id,
      title: r.title || '户外跑步',
      distanceKm: r.distance_km || '0.00',
      timeLabel: r.time_label || '',
      paceLabel: r.pace_label || '',
      hasTrack: !!r.has_track,
      isValid: !!r.is_valid,
      trajectoryPreview: (r.trajectory_preview || []).map(p => ({ lat: p.lat, lng: p.lng }))
    }));
  } catch (e) {
    recentRecords.value = [];
  } finally {
    loading.value = false;
  }
};

const fetchActiveTask = async () => {
  try {
    const res = await getStudentTasks({ page: 1, size: 5 });
    const tasks = (res?.items || []).filter(t => t.status === 'pending' || t.status === 'in_progress');
    if (tasks.length > 0) {
      const t = tasks[0];
      const now = new Date();
      const weeks = ['日', '一', '二', '三', '四', '五', '六'];
      const deadline = t.end_time ? new Date(t.end_time) : null;
      const completePct = t.total_targets > 0 ? Math.round((t.completed_count || 0) / t.total_targets * 100) : 0;
      activeTask.value = {
        taskId: t.id,
        title: t.title,
        weekLabel: `第${Math.ceil((now.getDate()) / 7)}周`,
        progress: `${t.completed_count || 0}/${t.total_targets || '?'} 次`,
        progressPercent: Math.min(100, completePct),
        deadlineLabel: deadline ? `${deadline.getMonth()+1}/${deadline.getDate()}` : ''
      };
    } else {
      activeTask.value = null;
    }
  } catch (e) {
    activeTask.value = null;
  }
};

onShow(() => {
  role.value = uni.getStorageSync('userRole') || 'student';
  applyRoleTabBar(role.value);
  if (role.value === 'student') {
    fetchTotalStats();
    fetchSunshineStats();
    fetchRecentRecords();
    fetchActiveTask();
  } else if (teacherManageRef.value?.onPageShow) {
    teacherManageRef.value.onPageShow();
  }
});

onHide(() => {
  if (role.value === 'teacher' && teacherManageRef.value?.onPageHide) {
    teacherManageRef.value.onPageHide();
  }
});

onMounted(() => {
  role.value = uni.getStorageSync('userRole') || 'student';
});
</script>

<style scoped>
.sport-container { min-height: 100vh; background: #F7F8FA; }
.student-sport { min-height: 100vh; }

/* 入口卡片 2列 */
.entry-grid {
  display: flex; gap: 20rpx;
  padding: 0 30rpx; margin-bottom: 24rpx;
}
.entry-card {
  flex: 1; background: #fff; border-radius: 20rpx;
  padding: 28rpx 20rpx; display: flex; align-items: center;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04); transition: transform 0.15s;
}
.entry-card:active { transform: scale(0.97); }
.entry-icon-wrap { margin-right: 16rpx; flex-shrink: 0; }
.entry-icon { width: 72rpx; height: 72rpx; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.entry-icon--run { background: transparent; }
.entry-icon--test { background: transparent; }
.entry-icon-text { width: 56rpx; height: 56rpx; }
.entry-info { flex: 1; min-width: 0; }
.entry-title { font-size: 28rpx; font-weight: 700; color: #191C1E; display: block; }
.entry-desc { font-size: 20rpx; color: #8E8E93; margin-top: 4rpx; display: block; }
.entry-arrow { font-size: 36rpx; color: #C5CED6; flex-shrink: 0; margin-left: 8rpx; }

/* 今日状态卡片 */
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx; }
.card-title { font-size: 30rpx; font-weight: 800; color: #191C1E; }
.card-more { display: flex; align-items: center; font-size: 24rpx; color: #8E8E93; font-weight: 600; }
.card-more-arrow { margin-left: 4rpx; font-size: 28rpx; }

.today-body { display: flex; align-items: center; gap: 24rpx; }
.today-ring-wrap { flex-shrink: 0; }
.today-ring {
  width: 180rpx; height: 180rpx; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}
.today-ring-inner {
  width: 150rpx; height: 150rpx; border-radius: 50%;
  background: #fff; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.today-ring-label { font-size: 20rpx; color: #8E8E93; }
.today-ring-row { display: flex; align-items: baseline; margin-top: 4rpx; }
.today-ring-num { font-size: 48rpx; font-weight: 900; color: #191C1E; }
.today-ring-unit { font-size: 22rpx; color: #191C1E; font-weight: 700; margin-left: 4rpx; }

.today-indicators { flex: 1; display: flex; flex-direction: column; gap: 16rpx; }
.today-indicator { display: flex; align-items: center; background: #F7F8FA; border-radius: 16rpx; padding: 18rpx 20rpx; }
.today-ind-icon { width: 56rpx; height: 56rpx; display: flex; align-items: center; justify-content: center; margin-right: 14rpx; }
.today-ind-emoji { font-size: 26rpx; }
.today-ind-emoji-img { width: 56rpx; height: 56rpx; }
.today-ind-body { flex: 1; }
.today-ind-label { font-size: 22rpx; color: #8E8E93; display: block; }
.today-ind-val { font-size: 24rpx; font-weight: 700; display: block; margin-top: 4rpx; }
.today-ind-val--ok { color: #33C9AB; }
.today-ind-val--fail { color: #F87171; }
.today-ind-val--count { color: #2196F3; }
.today-ind-val--pending { color: #8E8E93; }

/* 数据概览 */
.overview-grid { display: flex; }
.overview-item {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  padding: 8rpx 4rpx; position: relative;
}
.overview-item + .overview-item::before {
  content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%);
  width: 1rpx; height: 60rpx; background: #F0F3F6;
}
.overview-icon { width: 52rpx; height: 52rpx; margin-bottom: 8rpx; }
.overview-val { font-size: 32rpx; font-weight: 900; color: #191C1E; }
.overview-unit { font-size: 20rpx; color: #8E8E93; font-weight: 600; margin-top: 4rpx; }

/* 训练计划 */
.plan-body { display: flex; }
.plan-body-left { display: flex; align-items: center; width: 100%; }
.plan-icon { width: 96rpx; height: 96rpx; border-radius: 16rpx; background: #E8F8F2; display: flex; align-items: center; justify-content: center; margin-right: 20rpx; flex-shrink: 0; }
.plan-icon-emoji { font-size: 42rpx; }
.plan-icon-img { width: 70rpx; height: 70rpx; }
.plan-info { flex: 1; min-width: 0; }
.plan-name { font-size: 28rpx; font-weight: 700; color: #191C1E; display: block; }
.plan-meta { display: flex; gap: 16rpx; margin-top: 6rpx; }
.plan-meta-item { font-size: 20rpx; color: #8E8E93; }
.plan-bar { flex: 1; height: 10rpx; background: #F0F3F6; border-radius: 5rpx; overflow: hidden; margin-top: 14rpx; }
.plan-bar-fill { height: 100%; background: #33C9AB; border-radius: 5rpx; transition: width 0.3s; }
.plan-bar-label { font-size: 20rpx; font-weight: 700; color: #33C9AB; margin-top: 6rpx; display: block; }

/* 最近记录 */

</style>
