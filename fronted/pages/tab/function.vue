<template>
  <view class="sport-container">
    <view v-if="role === 'student'" class="student-sport">
      <page-tab-header title="运动" theme="brand" />

      <view class="content-wrapper page-tab-body">
        <!-- 运动入口卡片（2列） -->
        <view class="entry-grid">
          <view class="entry-card" @click="goToRun">
            <view class="entry-icon-wrap">
              <view class="entry-icon entry-icon--run">
                <text class="entry-icon-text">🏃</text>
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
                <text class="entry-icon-text">💪</text>
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
                <view class="today-ind-icon today-ind-icon--check">
                  <text class="today-ind-emoji">✅</text>
                </view>
                <view class="today-ind-body">
                  <text class="today-ind-label">今日状态</text>
                  <text class="today-ind-val today-ind-val--ok" v-if="sunshine.today_status === 'success'">审核通过</text>
                  <text class="today-ind-val today-ind-val--pending" v-else>未开始</text>
                </view>
              </view>
              <view class="today-indicator" v-if="sunshine.today_status === 'failed'">
                <view class="today-ind-icon today-ind-icon--fail">
                  <text class="today-ind-emoji">❌</text>
                </view>
                <view class="today-ind-body">
                  <text class="today-ind-label">未通过原因</text>
                  <text class="today-ind-val today-ind-val--fail">{{ sunshine.today_fail_reason || '里程不足' }}</text>
                </view>
              </view>
              <view class="today-indicator" v-else>
                <view class="today-ind-icon today-ind-icon--count">
                  <text class="today-ind-emoji">🏃</text>
                </view>
                <view class="today-ind-body">
                  <text class="today-ind-label">有效次数</text>
                  <text class="today-ind-val today-ind-val--count">{{ sunshine.total_valid_count }} / 20</text>
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
              <text class="overview-icon">📍</text>
              <text class="overview-val">{{ totalStats.distance }}</text>
              <text class="overview-unit">总里程(km)</text>
            </view>
            <view class="overview-item">
              <text class="overview-icon">⏱</text>
              <text class="overview-val">{{ totalStats.duration }}</text>
              <text class="overview-unit">总时长(min)</text>
            </view>
            <view class="overview-item">
              <text class="overview-icon">🔥</text>
              <text class="overview-val">{{ totalStats.calories }}</text>
              <text class="overview-unit">总消耗(kcal)</text>
            </view>
            <view class="overview-item">
              <text class="overview-icon">📊</text>
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
                <text class="plan-icon-emoji">🎯</text>
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
          <view class="history-list" v-if="recentRecords.length > 0">
            <view class="history-item" v-for="(item, idx) in recentRecords" :key="idx" @click="goToHistory">
              <view class="history-thumb">
                <image v-if="item.thumb" :src="item.thumb" class="history-thumb-img" mode="aspectFill" />
                <view v-else class="history-thumb-placeholder">
                  <text class="history-thumb-icon">🏃</text>
                </view>
              </view>
              <view class="history-info">
                <view class="history-title-row">
                  <text class="history-title">{{ item.typeLabel }}</text>
                  <text class="history-dist">{{ item.distance }} 公里</text>
                </view>
                <text class="history-date">{{ item.dateLabel }}</text>
                <view class="history-meta">
                  <text class="history-meta-item">{{ item.duration }}</text>
                  <text class="history-meta-item">{{ item.pace }}</text>
                  <text class="history-meta-item">{{ item.calories }} 千卡</text>
                </view>
              </view>
              <text class="history-arrow">›</text>
            </view>
          </view>
          <view class="history-empty" v-else>
            <text class="history-empty-txt">暂无运动记录</text>
          </view>
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
import { request, getSunshineStats, getStudentTasks } from '@/utils/request.js';

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
  try {
    const res = await request({ url: '/student/home/dashboard', method: 'GET' });
    const runs = res?.recent_runs || [];
    recentRecords.value = runs.slice(0, 3).map(r => ({
      typeLabel: r.title || '户外跑步',
      distance: r.distance_km || 0,
      dateLabel: r.time_label || '',
      duration: r.duration || '',
      pace: r.pace_label || '',
      calories: r.calories || 0,
      thumb: r.thumb || ''
    }));
  } catch (e) {
    recentRecords.value = [];
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
.entry-icon--run { background: #E8F8F2; }
.entry-icon--test { background: #FFF3E0; }
.entry-icon-text { font-size: 32rpx; }
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
.today-ind-icon { width: 56rpx; height: 56rpx; border-radius: 12rpx; display: flex; align-items: center; justify-content: center; margin-right: 14rpx; }
.today-ind-icon--check { background: #E8F8F2; }
.today-ind-icon--fail { background: #FFF0F0; }
.today-ind-icon--count { background: #E8F4FC; }
.today-ind-emoji { font-size: 26rpx; }
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
.overview-icon { font-size: 28rpx; margin-bottom: 8rpx; }
.overview-val { font-size: 32rpx; font-weight: 900; color: #191C1E; }
.overview-unit { font-size: 20rpx; color: #8E8E93; font-weight: 600; margin-top: 4rpx; }

/* 训练计划 */
.plan-body { display: flex; }
.plan-body-left { display: flex; align-items: center; width: 100%; }
.plan-icon { width: 96rpx; height: 96rpx; border-radius: 16rpx; background: #E8F8F2; display: flex; align-items: center; justify-content: center; margin-right: 20rpx; flex-shrink: 0; }
.plan-icon-emoji { font-size: 42rpx; }
.plan-info { flex: 1; min-width: 0; }
.plan-name { font-size: 28rpx; font-weight: 700; color: #191C1E; display: block; }
.plan-meta { display: flex; gap: 16rpx; margin-top: 6rpx; }
.plan-meta-item { font-size: 20rpx; color: #8E8E93; }
.plan-bar { flex: 1; height: 10rpx; background: #F0F3F6; border-radius: 5rpx; overflow: hidden; margin-top: 14rpx; }
.plan-bar-fill { height: 100%; background: #33C9AB; border-radius: 5rpx; transition: width 0.3s; }
.plan-bar-label { font-size: 20rpx; font-weight: 700; color: #33C9AB; margin-top: 6rpx; display: block; }

/* 最近记录 */
.history-list { display: flex; flex-direction: column; gap: 20rpx; }
.history-item { display: flex; align-items: center; }
.history-item:active { opacity: 0.7; }
.history-thumb { width: 120rpx; height: 90rpx; border-radius: 14rpx; overflow: hidden; flex-shrink: 0; margin-right: 18rpx; }
.history-thumb-img { width: 100%; height: 100%; }
.history-thumb-placeholder { width: 100%; height: 100%; background: #F0F3F6; display: flex; align-items: center; justify-content: center; }
.history-thumb-icon { font-size: 36rpx; opacity: 0.4; }
.history-info { flex: 1; min-width: 0; }
.history-title-row { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 4rpx; }
.history-title { font-size: 26rpx; font-weight: 700; color: #191C1E; }
.history-dist { font-size: 32rpx; font-weight: 900; color: #191C1E; }
.history-date { font-size: 20rpx; color: #8E8E93; display: block; margin-bottom: 8rpx; }
.history-meta { display: flex; gap: 16rpx; }
.history-meta-item { font-size: 20rpx; color: #8E8E93; }
.history-arrow { font-size: 30rpx; color: #C5CED6; flex-shrink: 0; margin-left: 8rpx; }
.history-empty { text-align: center; padding: 24rpx 0; }
.history-empty-txt { font-size: 26rpx; color: #8E8E93; }
</style>