<template>
  <view class="teacher-test-page">
    <!-- Custom Navigation Bar -->
    <view class="custom-nav-bar">
      <view class="nav-status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
      <view class="nav-content">
        <text class="nav-title">测试监控</text>
      </view>
    </view>

    <!-- Header / Tab Switcher -->
    <view class="header-tabs">
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 'live' }"
        @click="currentTab = 'live'"
      >
        <text class="tab-title">实时监控</text>
        <view class="tab-indicator" v-if="currentTab === 'live'"></view>
      </view>
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
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 'exception' }"
        @click="currentTab = 'exception'"
      >
        <text class="tab-title">异常处理</text>
        <view class="tab-indicator" v-if="currentTab === 'exception'"></view>
      </view>
    </view>

    <!-- Content: Live Monitoring -->
    <scroll-view scroll-y class="content-area" v-if="currentTab === 'live'">
      <view class="live-card">
        <view class="live-header">
          <text class="live-title">当前正在进行的测试</text>
          <view class="live-badge"><text class="live-badge-text">AI 评分接入中</text></view>
        </view>
        
        <view class="student-live-grid">
          <view class="student-monitor-card" v-for="(stu, idx) in liveStudents" :key="idx">
            <view class="monitor-video-placeholder">
              <video 
                v-if="stu.videoUrl" 
                :src="stu.videoUrl" 
                class="monitor-video"
                controls
                :show-center-play-btn="true"
              ></video>
              <view v-else class="no-video">
                <text class="no-video-text">暂无视频</text>
              </view>
              <text class="ai-overlay">AI 评分: {{ stu.confidence }}%</text>
              <text class="live-score">{{ stu.currentScore }}</text>
            </view>
            <view class="monitor-info">
              <text class="s-name">{{ stu.name }}</text>
              <text class="s-action">{{ stu.action }}</text>
              <text class="s-status warning" v-if="stu.isAbnormal">动作不标准</text>
              <text class="s-status good" v-else>动作标准</text>
            </view>
          </view>
          <view v-if="liveStudents.length === 0" class="empty-state">
            <text class="empty-text">暂无正在进行的测试</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- Content: Data Analysis -->
    <scroll-view scroll-y class="content-area" v-if="currentTab === 'analysis'">
      <!-- New Radar-like Skills Matrix -->
      <view class="chart-card">
        <view class="card-title"><text class="card-title-text">班级体能综合模型</text></view>
        <view class="skills-matrix">
           <view class="skill-row" v-for="(skill, idx) in classSkills" :key="idx">
             <text class="skill-name">{{ skill.name }}</text>
             <view class="skill-track">
               <view class="skill-bar" :style="{ width: skill.val + '%', background: skill.color }"></view>
             </view>
             <text class="skill-val">{{ skill.val }}</text>
           </view>
        </view>
        <view class="analysis-summary">
           <text class="summary-text">💡 建议加强 <text class="highlight">上肢力量</text> 专项训练</text>
        </view>
      </view>

      <view class="chart-card">
        <view class="card-title"><text class="card-title-text">班级成绩分布对比</text></view>
        <view class="bar-chart">
          <view class="bar-group" v-for="(item, idx) in classComparison" :key="idx">
            <view class="bar-col">
              <view class="bar-fill" :style="{ height: item.percent + '%', background: item.color }">
                <text class="bar-val">{{ item.value }}人</text>
              </view>
            </view>
            <text class="bar-label">{{ item.label }}</text>
          </view>
        </view>
      </view>

      <view class="chart-card">
        <view class="card-title"><text class="card-title-text">各项体能合格率</text></view>
        <view class="progress-list">
          <view class="prog-item" v-for="(p, idx) in passRates" :key="idx">
            <view class="prog-header">
              <text class="prog-name">{{ p.name }}</text>
              <text class="prog-val" :style="{ color: p.rate >= 80 ? '#20C997' : '#ff9f43' }">{{ p.rate }}%</text>
            </view>
            <view class="prog-track">
              <view class="prog-bar" :style="{ width: p.rate + '%', background: p.rate >= 80 ? '#20C997' : '#ff9f43' }"></view>
            </view>
          </view>
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
      </view>
    </scroll-view>

    <!-- Content: Exception Handling -->
    <scroll-view scroll-y class="content-area" v-if="currentTab === 'exception'">
      <view class="exception-header">
        <view class="ex-stats-row">
            <view class="ex-stat-item">
                <text class="ex-stat-num">{{ pendingCount }}</text>
                <text class="ex-stat-desc">待处理</text>
            </view>
            <view class="ex-stat-item">
                <text class="ex-stat-num">{{ todayCount }}</text>
                <text class="ex-stat-desc">今日新增</text>
            </view>
        </view>
      </view>

      <view class="filter-bar">
        <text class="filter-item" :class="{ active: currentFilter === 'all' }" @click="currentFilter = 'all'">全部</text>
        <text class="filter-item" :class="{ active: currentFilter === 'urgent' }" @click="currentFilter = 'urgent'">紧急</text>
        <text class="filter-item" :class="{ active: currentFilter === 'normal' }" @click="currentFilter = 'normal'">一般</text>
      </view>

      <view class="alert-list">
        <view class="alert-card" v-for="(alert, index) in filteredAlerts" :key="alert.id">
            <view class="alert-header">
                <view class="alert-header-left">
                    <text class="type-tag" :class="alert.typeClass">{{ alert.typeText }}</text>
                    <text class="student-name">{{ alert.studentName }}</text>
                    <text class="student-id">{{ alert.studentId }}</text>
                </view>
                <text class="time">{{ alert.time }}</text>
            </view>
            <view class="alert-body">
                <view class="data-row">
                    <text class="label">异常数据：</text>
                    <text class="value highlight">{{ alert.value }}</text>
                    <text class="standard">（标准: {{ alert.standard }}）</text>
                </view>
                <view class="desc-box">
                    <text class="desc-title">说明：</text>
                    <text class="desc-content">{{ alert.description }}</text>
                </view>
            </view>
            <view class="alert-footer">
                <button class="action-btn ignore" size="mini" @click="ignoreAlert(alert.id)">忽略</button>
                <button class="action-btn notify" size="mini" @click="notifyStudent(alert)">通知</button>
                <button class="action-btn handle" size="mini" @click="handleAlert(alert)">处理</button>
            </view>
        </view>
        <view v-if="filteredAlerts.length === 0" class="empty-state">
            <text class="empty-text">暂无异常数据</text>
        </view>
      </view>
    </scroll-view>

  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { request, BASE_URL } from '@/utils/request.js';

const currentTab = ref('live'); // 'live' | 'analysis' | 'history' | 'exception'
const timer = ref(null);
const statusBarHeight = ref(20);

onMounted(() => {
  const info = uni.getSystemInfoSync();
  statusBarHeight.value = info.statusBarHeight || 20;
  
  // Load initial data
  fetchLiveTests();
  fetchTestStats();
  fetchTestHistory();
});

// --- Live Data ---
const liveStudents = ref([]);

const fetchLiveTests = async () => {
  try {
    const res = await request({
      url: '/teacher/tests/live',
      method: 'GET'
    });
    
    console.log('Live tests response:', res);
    
    liveStudents.value = res.items.map(item => ({
      id: item.id,
      name: item.student_name,
      action: item.action,
      currentScore: item.score,
      isAbnormal: item.is_abnormal,
      confidence: item.confidence,
      videoUrl: item.video_url ? `${BASE_URL}${item.video_url}` : null,
      startedAt: item.started_at
    }));
    
    console.log('Mapped live students:', liveStudents.value);
  } catch (e) {
    console.error('Failed to fetch live tests:', e);
    liveStudents.value = [];
  }
};

// --- Analysis Data ---
const classSkills = ref([]);
const classComparison = ref([]);
const passRates = ref([]);

const fetchTestStats = async () => {
  try {
    const res = await request({
      url: '/teacher/tests/stats',
      method: 'GET'
    });
    
    classSkills.value = res.class_skills || [];
    classComparison.value = res.class_comparison || [];
    passRates.value = res.pass_rates || [];
  } catch (e) {
    console.error('Failed to fetch test stats:', e);
  }
};

// --- History Data ---
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

// --- Exception Data ---
const currentFilter = ref('all');
const todayCount = ref(5);
const alerts = ref([
  {
    id: 1, type: 'heart_rate', typeText: '心率过高', typeClass: 'tag-red',
    studentName: '张三', studentId: '2023001', time: '10:30',
    value: '195 bpm', standard: '60-180 bpm',
    description: '跑步过程中持续3分钟心率超过安全阈值。', level: 'urgent'
  },
  {
    id: 2, type: 'pace', typeText: '配速异常', typeClass: 'tag-orange',
    studentName: '李四', studentId: '2023002', time: '10:45',
    value: '2\'30"/km', standard: '4\'00"-8\'00"/km',
    description: '短时间内配速极快，疑似骑车或数据漂移。', level: 'normal'
  },
  {
    id: 3, type: 'location', typeText: '轨迹异常', typeClass: 'tag-blue',
    studentName: '王五', studentId: '2023003', time: '09:15',
    value: '直线穿越', standard: '连续轨迹',
    description: '轨迹点之间距离过大，且无中间路径。', level: 'normal'
  }
]);

const pendingCount = computed(() => alerts.value.length);
const filteredAlerts = computed(() => {
  if (currentFilter.value === 'all') return alerts.value;
  return alerts.value.filter(a => a.level === currentFilter.value);
});

// --- Exception Handlers ---
const ignoreAlert = (id) => {
  uni.showModal({
    title: '确认忽略',
    content: '忽略后该异常将不再提醒，确认操作？',
    success: (res) => {
      if (res.confirm) {
        alerts.value = alerts.value.filter(a => a.id !== id);
        uni.showToast({ title: '已忽略', icon: 'none' });
      }
    }
  });
};

const notifyStudent = (alert) => {
  uni.showToast({ title: `已发送通知给 ${alert.studentName}`, icon: 'success' });
};

const handleAlert = (alert) => {
  uni.showActionSheet({
    itemList: ['标记为无效成绩', '标记为设备故障', '要求重测'],
    success: (res) => {
      const actions = ['无效成绩', '设备故障', '重测'];
      uni.showToast({ title: `已标记为：${actions[res.tapIndex]}`, icon: 'success' });
      alerts.value = alerts.value.filter(a => a.id !== alert.id);
    }
  });
};

// --- Live Simulation (removed, using real data) ---
const refreshData = () => {
  if (currentTab.value === 'live') {
    fetchLiveTests();
  } else if (currentTab.value === 'analysis') {
    fetchTestStats();
  } else if (currentTab.value === 'history') {
    fetchTestHistory();
  }
};

const startLiveUpdate = () => {
  if (timer.value) clearInterval(timer.value);
  // Refresh every 30 seconds
  timer.value = setInterval(() => {
    fetchLiveTests();
  }, 30000);
};

const stopLiveUpdate = () => {
  if (timer.value) {
    clearInterval(timer.value);
    timer.value = null;
  }
};

const onPageShow = () => {
  refreshData();
  if (currentTab.value === 'live') {
    startLiveUpdate();
  }
};

const onPageHide = () => {
  stopLiveUpdate();
};

onUnmounted(() => {
  stopLiveUpdate();
});

defineExpose({
  onPageShow,
  onPageHide
});
</script>

<style scoped>
.teacher-test-page {
  flex: 1;
  background-color: #f8f9fa;
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Custom Navigation Bar */
  .custom-nav-bar {
    background: #fff;
    width: 750rpx; /* Ensure full width in NVUE */
    /* position: sticky; */
    /* top: 0; */
    /* z-index: 100; */
    border-bottom: 1px solid #eee;
  }
  .nav-status-bar {
    height: 20px; /* Default fallback */
    width: 750rpx;
  }
  .nav-content {
    height: 44px; /* Standard navbar height */
    width: 750rpx; /* Ensure full width for centering */
    display: flex;
    flex-direction: row; /* Fixed */
    align-items: center;
    justify-content: center;
    position: relative;
  }
  .nav-title {
    color: #333;
    font-size: 32rpx;
    font-weight: bold;
  }
  
  .header-tabs {
    background: #fff;
    display: flex;
    flex-direction: row; /* Fixed for NVUE/Flex */
    padding: 0 20rpx;
    border-bottom: 1px solid #eee;
    /* position: sticky; */ /* Removed sticky to fix visibility issue */
    /* top: 0; */
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
  padding: 20rpx;
}

/* Live Monitor Styles */
.live-header {
  display: flex;
  flex-direction: row; /* Fixed */
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.live-title { font-size: 32rpx; font-weight: bold; color: #333; }
.live-badge { 
  background: rgba(32, 201, 151, 0.1); 
  padding: 4rpx 12rpx; 
  border-radius: 8rpx; 
}
.live-badge-text { color: #20C997; font-size: 24rpx; }

.student-live-grid {
  display: flex;
  flex-direction: row; /* Fixed */
  flex-wrap: wrap;
  justify-content: space-between;
}

.student-monitor-card {
    width: 340rpx; /* Better responsive width for 2 columns */
    background: #fff;
    border-radius: 12rpx;
    overflow: hidden;
    box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
    margin-bottom: 20rpx;
  }

.monitor-video-placeholder {
  height: 200rpx;
  background: #1a1a1a;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.monitor-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-video {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2a2a2a;
}

.no-video-text {
  color: #666;
  font-size: 24rpx;
}

.ai-overlay {
  position: absolute;
  top: 10rpx;
  left: 10rpx;
  color: #fff;
  font-size: 20rpx;
  background: rgba(0,0,0,0.7);
  padding: 4rpx 8rpx;
  border-radius: 4rpx;
  z-index: 10;
}

.live-score {
  position: absolute;
  bottom: 10rpx;
  right: 10rpx;
  color: #fff;
  font-weight: bold;
  font-size: 36rpx;
  background: rgba(0,0,0,0.5);
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  z-index: 10;
}


.monitor-info { padding: 16rpx; }
.s-name { font-size: 28rpx; font-weight: bold; color: #333; }
.s-action { font-size: 24rpx; color: #666; margin: 4rpx 0; }
.s-status { font-size: 22rpx; padding: 4rpx 10rpx; border-radius: 6rpx; margin-top: 8rpx; text-align: center; }
.s-status.good { background: #e6fffa; color: #20C997; }
.s-status.warning { background: #fff5f5; color: #ff6b6b; }

/* Analysis Chart Styles */
.chart-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.03);
}

.card-title {
  margin-bottom: 30rpx;
  border-left: 8rpx solid #20C997;
  padding-left: 20rpx;
}
.card-title-text { font-size: 32rpx; font-weight: bold; color: #333; }

.skills-matrix {
  display: flex;
  flex-direction: column;
}
.skill-row {
  display: flex;
  flex-direction: row; /* Fixed */
  align-items: center;
  margin-bottom: 20rpx;
}
.skill-name { font-size: 26rpx; color: #555; width: 120rpx; margin-right: 20rpx; }
.skill-track { flex: 1; height: 20rpx; background: #f0f0f0; border-radius: 10rpx; overflow: hidden; }
.skill-bar { height: 100%; border-radius: 10rpx; transition-property: width; transition-duration: 1s; }
.skill-val { font-size: 26rpx; font-weight: bold; color: #333; width: 60rpx; text-align: right; }

.analysis-summary {
  margin-top: 20rpx; padding: 20rpx;
  background: #e6fffa; border-radius: 12rpx; border: 1px solid #b2f5ea;
}
.summary-text { font-size: 28rpx; color: #234e52; }
.highlight { color: #d53f8c; font-weight: bold; }

.bar-chart {
  display: flex;
  flex-direction: row; /* Fixed */
  justify-content: space-around;
  align-items: flex-end;
  height: 320rpx;
  padding-bottom: 20rpx;
  border-bottom: 1px solid #eee;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
  flex: 1;
  position: relative;
}

.bar-col {
  width: 60rpx;
  height: 85%;
  background: #f5f5f5;
  border-radius: 20rpx;
  position: relative;
  display: flex;
  align-items: flex-end;
}

.bar-fill {
  width: 100%;
  border-radius: 20rpx;
  position: absolute;
  bottom: 0; left: 0;
  transition-property: height; transition-duration: 1s;
}

.bar-val {
  position: absolute;
  top: -40rpx; left: 50%; transform: translateX(-50%);
  font-size: 22rpx; color: #666; font-weight: bold;
  lines: 1; text-overflow: clip; z-index: 10;
}

.bar-label {
  margin-top: 16rpx;
  font-size: 26rpx; color: #666;
}

.progress-list { display: flex; flex-direction: column; }
.prog-item { width: 100%; margin-bottom: 30rpx; }
.prog-header { display: flex; flex-direction: row; /* Fixed */ justify-content: space-between; margin-bottom: 12rpx; }
.prog-name { font-size: 28rpx; color: #444; }
.prog-val { font-size: 28rpx; font-weight: bold; }
.prog-track { height: 16rpx; background: #f0f0f0; border-radius: 8rpx; overflow: hidden; }
.prog-bar { height: 100%; border-radius: 8rpx; transition-property: width; transition-duration: 1s; }

/* History Styles */
.history-list {
  background: #fff;
  border-radius: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.03);
}

.history-item {
  display: flex;
  flex-direction: row; /* Fixed */
  justify-content: space-between;
  align-items: center;
  padding: 32rpx;
  border-bottom: 1px solid #f5f5f5;
}

.h-left { display: flex; flex-direction: column; }
.h-date { font-size: 24rpx; color: #999; margin-bottom: 8rpx; }
.h-name { font-size: 32rpx; font-weight: bold; color: #333; }

.h-right { display: flex; flex-direction: row; /* Fixed */ align-items: center; }
.h-stat { font-size: 26rpx; color: #666; margin-right: 20rpx; }
.h-stat.high-pass { color: #20C997; font-weight: bold; }
.arrow { color: #ccc; font-size: 24rpx; }

/* Exception Styles */
.exception-header {
  background: #fff;
  padding: 30rpx;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}
.ex-stats-row { display: flex; flex-direction: row; justify-content: space-around; }
.ex-stat-item { display: flex; flex-direction: column; align-items: center; }
.ex-stat-num { font-size: 36rpx; font-weight: bold; color: #ff6b6b; }
.ex-stat-desc { font-size: 24rpx; color: #999; }

.filter-bar {
  display: flex;
  flex-direction: row;
  margin-bottom: 20rpx;
  background: #fff;
  padding: 10rpx;
  border-radius: 12rpx;
}
.filter-item {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  font-size: 28rpx;
  color: #666;
  border-radius: 8rpx;
}
.filter-item.active { background: #e6f7ff; color: #1890ff; font-weight: 500; }

.alert-list { padding-bottom: 40rpx; }
.alert-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}
.alert-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
  padding-bottom: 20rpx;
  border-bottom: 1px solid #f0f0f0;
}
.alert-header-left { display: flex; flex-direction: row; align-items: center; }
.type-tag { font-size: 22rpx; padding: 4rpx 12rpx; border-radius: 6rpx; color: #fff; margin-right: 16rpx; }
.tag-red { background: #ff4d4f; }
.tag-orange { background: #faad14; }
.tag-blue { background: #1890ff; }
.student-name { font-size: 30rpx; font-weight: 500; color: #333; margin-right: 16rpx; }
.student-id { font-size: 24rpx; color: #999; }
.time { font-size: 24rpx; color: #999; }

.alert-body { margin-bottom: 24rpx; }
.data-row { display: flex; flex-direction: row; margin-bottom: 16rpx; font-size: 28rpx; align-items: center; }
.label { color: #666; }
.value { color: #333; font-weight: 500; margin-right: 10rpx; }
.value.highlight { color: #ff4d4f; }
.standard { color: #999; font-size: 24rpx; }

.desc-box { background: #f9f9f9; padding: 16rpx; border-radius: 8rpx; }
.desc-title { font-size: 26rpx; color: #333; font-weight: 500; margin-bottom: 8rpx; }
.desc-content { font-size: 26rpx; color: #666; }

.alert-footer { display: flex; flex-direction: row; justify-content: flex-end; }
.action-btn { margin-left: 20rpx; margin-right: 0; font-size: 24rpx; }
.action-btn.ignore { color: #999; background: #fff; border: 1px solid #ddd; }
.action-btn.notify { color: #1890ff; background: #fff; border: 1px solid #1890ff; }
.action-btn.handle { background: #20C997; color: #fff; }

.empty-state { padding: 60rpx; text-align: center; color: #999; font-size: 28rpx; }
</style>