<template>
  <view class="teacher-test-page">
    <page-tab-header title="测试监控" show-back theme="white" />

    <view class="header-tabs page-tab-body">
      <view class="tab-item" :class="{ active: currentTab === 'analysis' }" @click="currentTab = 'analysis'">
        <text class="tab-title">数据总览</text>
        <view class="tab-indicator" v-if="currentTab === 'analysis'"></view>
      </view>
      <view class="tab-item" :class="{ active: currentTab === 'history' }" @click="currentTab = 'history'">
        <text class="tab-title">任务回顾</text>
        <view class="tab-indicator" v-if="currentTab === 'history'"></view>
      </view>
    </view>

    <scroll-view scroll-y class="content-area" v-if="currentTab === 'analysis'">
      <view class="summary-grid">
        <view class="summary-card">
          <text class="summary-label">今日运动人次</text>
          <text class="summary-value">{{ sunshineMonitor.todayTotal }}</text>
        </view>
        <view class="summary-card">
          <text class="summary-label">今日异常记录</text>
          <text class="summary-value danger">{{ sunshineMonitor.todayExceptions }}</text>
        </view>
        <view class="summary-card">
          <text class="summary-label">任务总数</text>
          <text class="summary-value">{{ taskCompletionSummary.totalTasks }}</text>
        </view>
        <view class="summary-card">
          <text class="summary-label">平均完成率</text>
          <text class="summary-value">{{ taskCompletionSummary.avgCompletion }}%</text>
        </view>
      </view>

      <view class="chart-card">
        <view class="card-title">
          <text class="card-title-text">任务完成情况</text>
          <text class="card-subtitle">只保留重点任务，避免信息堆太满</text>
        </view>
        <view v-if="taskCompletionData.length" class="task-completion-list">
          <view class="task-item" v-for="task in taskCompletionData" :key="task.task_id">
            <view class="task-header">
              <text class="task-name">{{ task.task_title }}</text>
              <text class="completion-rate">{{ task.completion_rate }}%</text>
            </view>
            <view class="task-progress">
              <view class="progress-bar">
                <view class="progress-fill" :style="{ width: task.completion_rate + '%' }"></view>
              </view>
              <text class="progress-text">{{ task.completed_count }}/{{ task.total_students }}</text>
            </view>
          </view>
        </view>
        <view v-else class="empty-placeholder">
          <text class="placeholder-text">暂无任务统计</text>
        </view>
      </view>

      <view class="chart-card">
        <view class="card-title">
          <text class="card-title-text">教师评分分布</text>
          <text class="card-subtitle">修复空白饼图，直接显示分数段占比</text>
        </view>
        <view v-if="scoreSummary.totalScored > 0" class="score-panel">
          <view class="score-ring" :style="scoreRingStyle">
            <view class="score-ring-inner">
              <text class="ring-main">{{ scoreSummary.avgScore }}</text>
              <text class="ring-sub">平均分</text>
            </view>
          </view>
          <view class="score-legend">
            <view class="legend-row" v-for="item in scoreSummary.legend" :key="item.label">
              <view class="legend-left">
                <view class="legend-dot" :style="{ background: item.color }"></view>
                <text class="legend-label">{{ item.label }}</text>
              </view>
              <text class="legend-value">{{ item.count }} 人</text>
            </view>
          </view>
        </view>
        <view v-else class="empty-placeholder">
          <text class="placeholder-text">暂无评分数据</text>
        </view>
      </view>
    </scroll-view>

    <scroll-view scroll-y class="content-area" v-if="currentTab === 'history'">
      <view class="history-list">
        <view class="history-item" v-for="h in historyList" :key="`${h.date}-${h.testName}`">
          <view class="h-left">
            <text class="h-date">{{ h.date }}</text>
            <text class="h-name">{{ h.testName }}</text>
          </view>
          <view class="h-right">
            <text class="h-stat">参与 {{ h.count }}</text>
            <text class="h-stat">{{ h.passRate }}%</text>
          </view>
        </view>
        <view v-if="!historyList.length" class="empty-placeholder">
          <text class="placeholder-text">暂无历史数据</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { request } from '@/utils/request.js';

const currentTab = ref('analysis');
const taskCompletionData = ref([]);
const historyList = ref([]);
const sunshineMonitor = ref({
  todayTotal: 0,
  todayExceptions: 0
});
const scoreSummary = ref({
  totalScored: 0,
  avgScore: 0,
  legend: []
});

const taskCompletionSummary = computed(() => {
  const list = taskCompletionData.value || [];
  if (!list.length) {
    return { totalTasks: 0, avgCompletion: 0 };
  }
  const avg = Math.round(list.reduce((sum, item) => sum + (Number(item.completion_rate) || 0), 0) / list.length);
  return {
    totalTasks: list.length,
    avgCompletion: avg
  };
});

const scoreRingStyle = computed(() => {
  const items = scoreSummary.value.legend || [];
  const total = items.reduce((sum, item) => sum + item.count, 0);
  if (!total) {
    return { background: '#e9ecef' };
  }
  let start = 0;
  const parts = items.map((item) => {
    const deg = (item.count / total) * 360;
    const end = start + deg;
    const part = `${item.color} ${start}deg ${end}deg`;
    start = end;
    return part;
  });
  return {
    background: `conic-gradient(${parts.join(', ')})`
  };
});

const handleBack = () => {
  uni.navigateBack({
    delta: 1,
    fail() {
      uni.switchTab({ url: '/pages/tab/tab' });
    }
  });
};

const fetchTaskCompletion = async () => {
  const res = await request({
    url: '/teacher/stats/task-completion',
    method: 'GET'
  });
  const list = Array.isArray(res?.tasks) ? res.tasks : [];
  taskCompletionData.value = list
    .sort((a, b) => (Number(b.completion_rate) || 0) - (Number(a.completion_rate) || 0))
    .slice(0, 5)
    .map((item) => ({
      ...item,
      completion_rate: Number(item.completion_rate) || 0,
      total_students: Number(item.total_students) || 0,
      completed_count: Number(item.completed_count) || 0
    }));
};

const fetchScoreSummary = async () => {
  const res = await request({
    url: '/teacher/export/scores',
    method: 'GET'
  });
  const rows = Array.isArray(res?.data) ? res.data : [];
  const buckets = [
    { label: '90-100', color: '#20c997', count: 0, hit: (v) => v >= 90 },
    { label: '80-89', color: '#4dabf7', count: 0, hit: (v) => v >= 80 && v < 90 },
    { label: '70-79', color: '#ffd166', count: 0, hit: (v) => v >= 70 && v < 80 },
    { label: '0-69', color: '#ff6b6b', count: 0, hit: (v) => v < 70 }
  ];
  let total = 0;
  let sum = 0;
  rows.forEach((row) => {
    const val = Number(row.avg_score);
    if (!Number.isFinite(val)) return;
    total += 1;
    sum += val;
    const bucket = buckets.find((item) => item.hit(val));
    if (bucket) bucket.count += 1;
  });
  scoreSummary.value = {
    totalScored: total,
    avgScore: total ? Math.round((sum / total) * 10) / 10 : 0,
    legend: buckets
  };
};

const fetchHistory = async () => {
  const res = await request({
    url: '/teacher/tasks',
    method: 'GET',
    data: { status: 'ended', page: 1, size: 20 }
  });
  const rows = Array.isArray(res?.items) ? res.items : [];
  historyList.value = rows.slice(0, 12).map((item) => ({
    date: item.deadline ? String(item.deadline).slice(0, 10) : '长期',
    testName: item.title,
    count: Number(item.completed_count) || 0,
    passRate: item.total_students ? Math.round(((Number(item.completed_count) || 0) / Number(item.total_students)) * 100) : 0
  }));
};

const fetchSunshineMonitor = async () => {
  const stats = await request({
    url: '/teacher/stats',
    method: 'GET'
  });
  sunshineMonitor.value.todayTotal = Number(stats?.today_checkin) || 0;

  const invalidList = await request({
    url: '/teacher/activities/invalid',
    method: 'GET'
  });
  const todayStr = new Date().toDateString();
  sunshineMonitor.value.todayExceptions = (Array.isArray(invalidList) ? invalidList : []).filter((item) => {
    if (!item?.started_at) return false;
    return new Date(item.started_at).toDateString() === todayStr;
  }).length;
};

const fetchAnalysisData = async () => {
  try {
    await Promise.all([fetchTaskCompletion(), fetchScoreSummary(), fetchSunshineMonitor()]);
  } catch (e) {
    console.error('Failed to fetch analysis data:', e);
  }
};

const refreshData = () => {
  if (currentTab.value === 'history') {
    fetchHistory();
  } else {
    fetchAnalysisData();
  }
};

const onPageShow = () => {
  refreshData();
};

const onPageHide = () => {};

onMounted(() => {
  const info = uni.getSystemInfoSync();
  fetchAnalysisData();
  fetchHistory();
});

onUnmounted(() => {});

defineExpose({
  onPageShow,
  onPageHide
});
</script>

<style scoped>
.teacher-test-page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.header-tabs {
  background: #fff;
  display: flex;
  padding: 0 20rpx;
  border-bottom: 1px solid #eee;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 28rpx 0;
  position: relative;
}

.tab-item.active {
  color: #20C997;
  font-weight: 700;
}

.tab-title {
  font-size: 30rpx;
}

.tab-indicator {
  position: absolute;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  width: 40rpx;
  height: 6rpx;
  border-radius: 6rpx;
  background: #20C997;
}

.content-area {
  flex: 1;
  padding: 24rpx;
  box-sizing: border-box;
}

.summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.summary-card,
.chart-card,
.history-list {
  background: #fff;
  border-radius: 18rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
}

.summary-card {
  padding: 24rpx;
}

.summary-label {
  font-size: 24rpx;
  color: #7a7a7a;
  display: block;
  margin-bottom: 12rpx;
}

.summary-value {
  font-size: 40rpx;
  font-weight: 700;
  color: #222;
}

.summary-value.danger {
  color: #e03131;
}

.chart-card {
  padding: 28rpx;
  margin-bottom: 20rpx;
}

.card-title {
  margin-bottom: 20rpx;
}

.card-title-text {
  font-size: 30rpx;
  font-weight: 700;
  color: #333;
  display: block;
}

.card-subtitle {
  font-size: 22rpx;
  color: #8a8a8a;
  margin-top: 8rpx;
  display: block;
}

.task-completion-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.task-item {
  padding: 20rpx;
  border-radius: 14rpx;
  background: #f8fbfa;
}

.task-header,
.task-progress,
.legend-row,
.legend-left,
.history-item,
.h-right {
  display: flex;
  align-items: center;
}

.task-header,
.history-item {
  justify-content: space-between;
}

.task-header {
  gap: 12rpx;
  margin-bottom: 12rpx;
}

.task-name {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.completion-rate {
  font-size: 28rpx;
  font-weight: 700;
  color: #20C997;
}

.task-progress {
  gap: 12rpx;
}

.progress-bar {
  flex: 1;
  height: 12rpx;
  border-radius: 12rpx;
  background: #dfe9e7;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #20C997, #4dd4ac);
}

.progress-text {
  width: 120rpx;
  text-align: right;
  font-size: 22rpx;
  color: #666;
}

.score-panel {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.score-ring {
  width: 220rpx;
  height: 220rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.score-ring-inner {
  width: 148rpx;
  height: 148rpx;
  border-radius: 50%;
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.ring-main {
  font-size: 38rpx;
  font-weight: 700;
  color: #222;
}

.ring-sub {
  font-size: 22rpx;
  color: #8a8a8a;
  margin-top: 6rpx;
}

.score-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.legend-row {
  justify-content: space-between;
  gap: 10rpx;
}

.legend-left {
  gap: 10rpx;
}

.legend-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
}

.legend-label,
.legend-value,
.h-date,
.h-stat {
  font-size: 24rpx;
  color: #666;
}

.history-list {
  overflow: hidden;
}

.history-item {
  padding: 24rpx 28rpx;
  border-bottom: 1px solid #f2f2f2;
}

.history-item:last-child {
  border-bottom: none;
}

.h-left {
  flex: 1;
  min-width: 0;
}

.h-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
  margin-top: 8rpx;
  display: block;
}

.h-right {
  gap: 16rpx;
}

.empty-placeholder {
  padding: 70rpx 20rpx;
  text-align: center;
}

.placeholder-text {
  font-size: 26rpx;
  color: #999;
}
</style>
