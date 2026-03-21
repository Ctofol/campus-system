<template>
  <view class="teacher-test-page">
    <!-- Custom Navigation Bar -->
    <view class="custom-nav-bar">
      <view class="nav-status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
      <view class="nav-content">
        <view class="nav-back" @click="handleBack">
          <text class="nav-back-icon"><</text>
          <text class="nav-back-text">返回</text>
        </view>
        <text class="nav-title">测试监控</text>
      </view>
    </view>

    <!-- Tab Switcher - 模块删除：删除实时监控和异常处理 -->
    <view class="header-tabs">
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 'analysis' }"
        @click="currentTab = 'analysis'"
      >
        <text class="tab-title">数据分析</text>
        <view class="tab-indicator" v-if="currentTab === 'analysis'"></view>
      </view>
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 'history' }"
        @click="currentTab = 'history'"
      >
        <text class="tab-title">历史回顾</text>
        <view class="tab-indicator" v-if="currentTab === 'history'"></view>
      </view>
    </view>

    <!-- 阳光跑实时看板：监控今日运动人次与异常情况 -->
    <scroll-view scroll-y class="content-area" v-if="currentTab === 'analysis'">
      <view class="chart-card sunshine-monitor">
        <view class="card-title">
          <text class="card-title-text">阳光跑实时看板</text>
        </view>
        <view class="sunshine-stats-row">
          <view class="sunshine-stat-item">
            <text class="sunshine-label">今日运动人次</text>
            <text class="sunshine-value">{{ sunshineMonitor.todayTotal }}</text>
          </view>
          <view class="sunshine-stat-item">
            <text class="sunshine-label">今日异常记录</text>
            <text class="sunshine-value danger">{{ sunshineMonitor.todayExceptions }}</text>
          </view>
        </view>
      </view>

      <!-- Content: Data Analysis - 数据分析逻辑限定：仅统计任务完成、平时分、打分趋势 -->
      <!-- 学生任务完成情况 -->
      <view class="chart-card">
        <view class="card-title">
          <text class="card-title-text">学生任务完成情况</text>
        </view>
        <view v-if="taskCompletionData.length > 0" class="task-completion-list">
          <view class="task-item" v-for="(task, idx) in taskCompletionData" :key="idx">
            <view class="task-header">
              <text class="task-name">{{ task.task_title }}</text>
              <text class="completion-rate" :class="{ high: task.completion_rate >= 80 }">
                {{ task.completion_rate }}%
              </text>
            </view>
            <view class="task-progress">
              <view class="progress-bar">
                <view class="progress-fill" :style="{ width: task.completion_rate + '%' }"></view>
              </view>
              <text class="progress-text">{{ task.completed_count }}/{{ task.total_students }}人</text>
            </view>
          </view>
        </view>
        <view v-else class="empty-placeholder">
          <text class="placeholder-icon">📊</text>
          <text class="placeholder-text">暂无统计数据</text>
        </view>
      </view>

      <!-- 平时分变化趋势 -->
      <view class="chart-card">
        <view class="card-title">
          <text class="card-title-text">平时分变化趋势</text>
        </view>
        <view v-if="scoreTrendData.length > 0" class="trend-chart">
          <view class="trend-line">
            <view 
              class="trend-point" 
              v-for="(point, idx) in scoreTrendData.slice(-7)" 
              :key="idx"
              :style="{ left: (idx * 14.28) + '%', bottom: (point.avg_score) + '%' }"
            >
              <view class="point-dot"></view>
              <text class="point-label">{{ point.avg_score }}</text>
            </view>
          </view>
          <view class="trend-labels">
            <text 
              class="label-item" 
              v-for="(point, idx) in scoreTrendData.slice(-7)" 
              :key="idx"
            >
              {{ point.date.slice(5) }}
            </text>
          </view>
        </view>
        <view v-else class="empty-placeholder">
          <text class="placeholder-icon">📈</text>
          <text class="placeholder-text">暂无统计数据</text>
        </view>
      </view>

      <!-- 教师打分趋势 -->
      <view class="chart-card">
        <view class="card-title">
          <text class="card-title-text">教师打分趋势</text>
        </view>
        <view v-if="scoringTrendData.total_scored > 0" class="scoring-stats">
          <view class="stat-row">
            <view class="stat-item">
              <text class="stat-label">已打分</text>
              <text class="stat-value">{{ scoringTrendData.total_scored }}</text>
            </view>
            <view class="stat-item">
              <text class="stat-label">平均分</text>
              <text class="stat-value highlight">{{ scoringTrendData.avg_score }}</text>
            </view>
          </view>
          <view class="distribution-chart">
            <view 
              class="dist-bar" 
              v-for="(value, key) in scoringTrendData.distribution" 
              :key="key"
            >
              <view class="bar-fill" :style="{ height: (value / scoringTrendData.total_scored * 100) + '%' }">
                <text class="bar-value">{{ value }}</text>
              </view>
              <text class="bar-label">{{ key }}</text>
            </view>
          </view>
        </view>
        <view v-else class="empty-placeholder">
          <text class="placeholder-icon">📝</text>
          <text class="placeholder-text">暂无统计数据</text>
        </view>
      </view>
    </scroll-view>

    <!-- Content: History -->
    <scroll-view scroll-y class="content-area" v-if="currentTab === 'history'">
      <view class="history-list">
        <view class="history-item" v-for="(h, idx) in historyList" :key="idx">
          <view class="h-left">
            <text class="h-date">{{ h.date }}</text>
            <text class="h-name">{{ h.testName }}</text>
          </view>
          <view class="h-right">
            <text class="h-stat">参与: {{ h.count }}人</text>
            <text class="h-stat" :class="{ 'high-pass': h.passRate >= 90 }">合格: {{ h.passRate }}%</text>
            <text class="arrow">></text>
          </view>
        </view>
        <view v-if="historyList.length === 0" class="empty-state">
          <text class="empty-icon">📋</text>
          <text class="empty-text">暂无历史数据</text>
        </view>
      </view>
    </scroll-view>

  </view>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { request } from '@/utils/request.js';

const currentTab = ref('analysis');
const statusBarHeight = ref(20);

// 数据分析相关数据
const taskCompletionData = ref([]);
const scoreTrendData = ref([]);
const scoringTrendData = ref({
  total_scored: 0,
  avg_score: 0,
  distribution: {}
});

// 阳光跑监控数据
const sunshineMonitor = ref({
  todayTotal: 0,
  todayExceptions: 0
});

onMounted(() => {
  const info = uni.getSystemInfoSync();
  statusBarHeight.value = info.statusBarHeight || 20;
  
  fetchTestHistory();
  fetchAnalysisData();
});

// 顶部返回键
const handleBack = () => {
  try {
    uni.navigateBack({
      delta: 1,
      fail() {
        uni.reLaunch({
          url: '/pages/teacher/dashboard/index'
        });
      }
    });
  } catch (e) {
    uni.reLaunch({
      url: '/pages/teacher/dashboard/index'
    });
  }
};

// 获取数据分析数据
const fetchAnalysisData = async () => {
  try {
    // 获取任务完成情况
    const taskRes = await request({
      url: '/teacher/stats/task-completion',
      method: 'GET'
    });
    taskCompletionData.value = taskRes.tasks || [];
    
    // 获取平时分趋势
    const trendRes = await request({
      url: '/teacher/stats/score-trend',
      method: 'GET',
      data: { days: 30 }
    });
    scoreTrendData.value = trendRes.trend || [];
    
    // 获取打分趋势
    const scoringRes = await request({
      url: '/teacher/stats/scoring-trend',
      method: 'GET'
    });
    scoringTrendData.value = scoringRes;

    // 获取阳光跑实时数据
    await fetchSunshineMonitor();
    
  } catch (e) {
    console.error('Failed to fetch analysis data:', e);
  }
};

// 历史数据
const historyList = ref([]);

const fetchTestHistory = async () => {
  try {
    const res = await request({
      url: '/teacher/tests/history',
      method: 'GET'
    });
    
    historyList.value = res.items.map(item => ({
      date: item.date,
      testName: item.test_name,
      count: item.count,
      passRate: item.pass_rate
    }));
  } catch (e) {
    console.error('Failed to fetch test history:', e);
    historyList.value = [];
  }
};

// 阳光跑实时监控（今日总人次 & 今日异常数）
const fetchSunshineMonitor = async () => {
  try {
    // 今日运动总人次：复用教师统计接口
    const stats = await request({
      url: '/teacher/stats',
      method: 'GET'
    });
    sunshineMonitor.value.todayTotal = stats.today_checkin || 0;

    // 今日异常记录：从异常活动接口中过滤今天
    const invalidList = await request({
      url: '/teacher/activities/invalid',
      method: 'GET'
    });

    const todayStr = new Date().toDateString();
    sunshineMonitor.value.todayExceptions = (invalidList || []).filter(item => {
      if (!item.started_at) return false;
      const d = new Date(item.started_at);
      return d.toDateString() === todayStr;
    }).length;
  } catch (e) {
    console.error('Failed to fetch sunshine monitor data:', e);
  }
};

const refreshData = () => {
  if (currentTab.value === 'history') {
    fetchTestHistory();
  } else if (currentTab.value === 'analysis') {
    fetchAnalysisData();
  }
};

const onPageShow = () => {
  refreshData();
};

const onPageHide = () => {
  // No cleanup needed
};

onUnmounted(() => {
  // No cleanup needed
});

defineExpose({
  onPageShow,
  onPageHide
});
</script>

<style scoped>
/* CSS样式修复：确保所有样式统一、无错位、无横向滚动 */
.teacher-test-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
  width: 100%;
  overflow-x: hidden;
}

/* Custom Navigation Bar */
.custom-nav-bar {
  background: #fff;
  width: 100%;
  border-bottom: 1px solid #eee;
}
.nav-status-bar {
  height: 20px;
  width: 100%;
}
.nav-content {
  height: 44px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.nav-back {
  position: absolute;
  left: 16rpx;
  top: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  padding: 0 12rpx;
}
.nav-back-icon {
  font-size: 32rpx;
  color: #333;
  margin-right: 4rpx;
}
.nav-back-text {
  font-size: 26rpx;
  color: #666;
}
.nav-title {
  color: #333;
  font-size: 32rpx;
  font-weight: bold;
}
  
.header-tabs {
  background: #fff;
  display: flex;
  padding: 0 20rpx;
  border-bottom: 1px solid #eee;
  z-index: 99;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 30rpx 0;
  position: relative;
  font-size: 30rpx;
  color: #666;
}

.tab-item.active {
  color: #20C997;
  font-weight: bold;
}

.tab-title {
  font-size: 30rpx;
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40rpx;
  height: 6rpx;
  background: #20C997;
  border-radius: 4rpx;
}

.content-area {
  flex: 1;
  padding: 30rpx;
  width: 100%;
  box-sizing: border-box;
}

/* Analysis Chart Styles */
.chart-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 36rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.03);
  width: 100%;
  box-sizing: border-box;
}

.card-title {
  margin-bottom: 30rpx;
  border-left: 8rpx solid #20C997;
  padding-left: 20rpx;
}
.card-title-text { 
  font-size: 32rpx; 
  font-weight: bold; 
  color: #333; 
}

/* 任务完成情况 */
.task-completion-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.task-item {
  padding: 24rpx;
  background: #f9f9f9;
  border-radius: 16rpx;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.task-name {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.completion-rate {
  font-size: 32rpx;
  font-weight: bold;
  color: #ff9f43;
  margin-left: 20rpx;
  flex-shrink: 0;
}

.completion-rate.high {
  color: #20C997;
}

.task-progress {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.progress-bar {
  flex: 1;
  height: 12rpx;
  background: #e0e0e0;
  border-radius: 6rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #20C997, #4cd9b0);
  border-radius: 6rpx;
  transition: width 0.3s;
}

.progress-text {
  font-size: 24rpx;
  color: #666;
  min-width: 120rpx;
  text-align: right;
  flex-shrink: 0;
}

/* 趋势图 */
.trend-chart {
  padding: 20rpx 0;
}

.trend-line {
  position: relative;
  height: 200rpx;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 20rpx;
}

.trend-point {
  position: absolute;
}

.point-dot {
  width: 12rpx;
  height: 12rpx;
  background: #20C997;
  border-radius: 50%;
  border: 2rpx solid #fff;
  box-shadow: 0 2rpx 4rpx rgba(0,0,0,0.1);
}

.point-label {
  position: absolute;
  top: -30rpx;
  left: 50%;
  transform: translateX(-50%);
  font-size: 22rpx;
  color: #666;
  white-space: nowrap;
}

.trend-labels {
  display: flex;
  justify-content: space-between;
  padding: 0 10rpx;
}

.label-item {
  font-size: 22rpx;
  color: #999;
}

/* 打分统计 */
.scoring-stats {
  padding: 20rpx 0;
}

.stat-row {
  display: flex;
  justify-content: space-around;
  margin-bottom: 40rpx;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 26rpx;
  color: #666;
  display: block;
  margin-bottom: 12rpx;
}

.stat-value {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  display: block;
}

.stat-value.highlight {
  color: #20C997;
}

.distribution-chart {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 200rpx;
  padding: 0 20rpx;
}

.dist-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
}

.bar-fill {
  width: 60rpx;
  background: linear-gradient(180deg, #20C997, #4cd9b0);
  border-radius: 8rpx 8rpx 0 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 8rpx;
  min-height: 40rpx;
  transition: height 0.3s;
}

.bar-value {
  font-size: 22rpx;
  color: #fff;
  font-weight: bold;
}

.bar-label {
  font-size: 22rpx;
  color: #666;
  margin-top: 12rpx;
}

/* 空状态 */
.empty-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 40rpx;
  text-align: center;
}

.placeholder-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
  opacity: 0.5;
}

.placeholder-text {
  font-size: 28rpx;
  color: #999;
}

/* History Styles */
.history-list {
  background: #fff;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.03);
  overflow: hidden;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 36rpx;
  border-bottom: 1px solid #f5f5f5;
}

.history-item:last-child {
  border-bottom: none;
}

.h-left { 
  display: flex; 
  flex-direction: column; 
  flex: 1;
}
.h-date { 
  font-size: 24rpx; 
  color: #999; 
  margin-bottom: 12rpx; 
}
.h-name { 
  font-size: 30rpx; 
  font-weight: bold; 
  color: #333; 
}

.h-right { 
  display: flex; 
  align-items: center; 
  gap: 20rpx;
  flex-shrink: 0;
}
.h-stat { 
  font-size: 26rpx; 
  color: #666; 
}
.h-stat.high-pass { 
  color: #20C997; 
  font-weight: bold; 
}
.arrow { 
  color: #ccc; 
  font-size: 28rpx; 
  margin-left: 10rpx;
}

.empty-state { 
  padding: 120rpx 40rpx; 
  text-align: center; 
  display: flex;
  flex-direction: column;
  align-items: center;
}
.empty-icon {
  font-size: 100rpx;
  margin-bottom: 30rpx;
  opacity: 0.5;
}
.empty-text { 
  font-size: 28rpx; 
  color: #999; 
}
</style>
