<template>
  <view class="teacher-test-page">
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
    </view>

    <!-- Content: Live Monitoring -->
    <scroll-view scroll-y class="content-area" v-if="currentTab === 'live'">
      <view class="live-card">
        <view class="live-header">
          <text class="live-title">当前正在进行的测试</text>
          <view class="live-badge">AI 评分接入中</view>
        </view>
        
        <view class="student-live-grid">
          <view class="student-monitor-card" v-for="(stu, idx) in liveStudents" :key="idx">
            <view class="monitor-video-placeholder">
              <text class="ai-overlay">AI Analyzing...</text>
              <!-- Simulated AI Bounding Box -->
              <view class="ai-bbox" :style="{borderColor: stu.isAbnormal ? '#ff6b6b' : '#0f0'}">
                 <text class="bbox-label">{{ stu.confidence }}%</text>
              </view>
              <view class="pose-skeleton">
                 <view class="bone head"></view>
                 <view class="bone body"></view>
                 <view class="bone arm-l"></view>
                 <view class="bone arm-r"></view>
                 <view class="bone leg-l"></view>
                 <view class="bone leg-r"></view>
              </view>
              <text class="live-score">{{ stu.currentScore }}</text>
            </view>
            <view class="monitor-info">
              <text class="s-name">{{ stu.name }}</text>
              <text class="s-action">{{ stu.action }}</text>
              <text class="s-status warning" v-if="stu.isAbnormal">动作不标准</text>
              <text class="s-status good" v-else>动作标准</text>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- Content: Data Analysis -->
    <scroll-view scroll-y class="content-area" v-if="currentTab === 'analysis'">
      <!-- New Radar-like Skills Matrix -->
      <view class="chart-card">
        <view class="card-title">班级体能综合模型</view>
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
        <view class="card-title">班级成绩分布对比</view>
        <view class="bar-chart">
          <view class="bar-group" v-for="(item, idx) in classComparison" :key="idx">
            <view class="bar-col">
              <view class="bar-fill" :style="{ height: item.percent + '%', background: item.color }"></view>
              <text class="bar-val">{{ item.value }}</text>
            </view>
            <text class="bar-label">{{ item.label }}</text>
          </view>
        </view>
      </view>

      <view class="chart-card">
        <view class="card-title">各项体能合格率</view>
        <view class="progress-list">
          <view class="prog-item" v-for="(p, idx) in passRates" :key="idx">
            <view class="prog-header">
              <text class="prog-name">{{ p.name }}</text>
              <text class="prog-val">{{ p.rate }}%</text>
            </view>
            <view class="prog-track">
              <view class="prog-bar" :style="{ width: p.rate + '%' }"></view>
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
            <text class="h-stat">合格: {{ h.passRate }}%</text>
            <text class="arrow">></text>
          </view>
        </view>
      </view>
    </scroll-view>

  </view>
</template>

<script setup>
import { ref } from 'vue';

const currentTab = ref('live');

// Mock Data
const liveStudents = ref([
  { name: '张伟', action: '引体向上', currentScore: 8, isAbnormal: false, confidence: 98 },
  { name: '李强', action: '仰卧起坐', currentScore: 24, isAbnormal: true, confidence: 85 },
  { name: '王芳', action: '深蹲', currentScore: 15, isAbnormal: false, confidence: 96 },
  { name: '赵杰', action: '俯卧撑', currentScore: 12, isAbnormal: false, confidence: 99 }
]);

const classSkills = ref([
  { name: '爆发力', val: 85, color: '#ff6b6b' },
  { name: '耐力', val: 72, color: '#4dabf7' },
  { name: '柔韧性', val: 68, color: '#ffd43b' },
  { name: '协调性', val: 90, color: '#20C997' },
  { name: '核心力量', val: 78, color: '#a55eea' }
]);

const classComparison = ref([
  { label: '优秀', value: 15, percent: 30, color: '#20C997' },
  { label: '良好', value: 45, percent: 60, color: '#4dabf7' },
  { label: '及格', value: 30, percent: 45, color: '#ffd43b' },
  { label: '不及格', value: 10, percent: 20, color: '#ff6b6b' }
]);

const passRates = ref([
  { name: '1000米跑', rate: 85 },
  { name: '引体向上', rate: 62 },
  { name: '立定跳远', rate: 94 },
  { name: '坐位体前屈', rate: 78 }
]);

const historyList = ref([
  { date: '2026-05-18', testName: '全员体能摸底测试', count: 128, passRate: 92 },
  { date: '2026-05-10', testName: '力量专项考核', count: 45, passRate: 88 },
  { date: '2026-04-28', testName: '耐力跑测试', count: 128, passRate: 76 }
]);
</script>

<style scoped>
.teacher-test-page {
  min-height: 100vh;
  background: #f8f9fa;
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
  box-sizing: border-box;
}

/* Live Monitor Styles */
.live-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.live-title { font-size: 32rpx; font-weight: bold; color: #333; }
.live-badge { 
  background: rgba(32, 201, 151, 0.1); 
  color: #20C997; 
  font-size: 24rpx; 
  padding: 4rpx 12rpx; 
  border-radius: 8rpx; 
}

.student-live-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}

.student-monitor-card {
  background: #fff;
  border-radius: 12rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}

.monitor-video-placeholder {
  height: 200rpx;
  background: #000;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-overlay {
  position: absolute;
  top: 10rpx;
  left: 10rpx;
  color: #0f0;
  font-size: 20rpx;
  font-family: monospace;
}

.live-score {
  position: absolute;
  bottom: 10rpx;
  right: 10rpx;
  color: #fff;
  font-weight: bold;
  font-size: 36rpx;
  text-shadow: 0 2rpx 4rpx rgba(0,0,0,0.5);
}

.pose-skeleton {
  width: 60rpx;
  height: 100rpx;
  position: relative;
}
.bone { background: #0f0; position: absolute; }
.bone.head { width: 16rpx; height: 16rpx; border-radius: 50%; top: 0; left: 22rpx; }
.bone.body { width: 4rpx; height: 40rpx; top: 16rpx; left: 28rpx; }
.bone.arm-l { width: 20rpx; height: 4rpx; top: 24rpx; left: 8rpx; transform: rotate(20deg); }
.bone.arm-r { width: 20rpx; height: 4rpx; top: 24rpx; right: 8rpx; transform: rotate(-20deg); }
.bone.leg-l { width: 4rpx; height: 30rpx; top: 56rpx; left: 24rpx; transform: rotate(10deg); }
.bone.leg-r { width: 4rpx; height: 30rpx; top: 56rpx; left: 34rpx; transform: rotate(-10deg); }

.ai-bbox {
  position: absolute;
  top: 20rpx;
  left: 20%;
  width: 60%;
  height: 80%;
  border: 2rpx dashed #0f0;
  border-radius: 8rpx;
}
.bbox-label {
  position: absolute;
  top: -24rpx;
  left: 0;
  background: #0f0;
  color: #000;
  font-size: 18rpx;
  padding: 0 4rpx;
}

.monitor-info {
  padding: 16rpx;
}

/* Skills Matrix */
.skills-matrix {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.skill-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
}
.skill-name { font-size: 24rpx; color: #666; width: 100rpx; }
.skill-track { flex: 1; height: 16rpx; background: #f0f0f0; border-radius: 8rpx; overflow: hidden; }
.skill-bar { height: 100%; border-radius: 8rpx; }
.skill-val { font-size: 24rpx; font-weight: bold; color: #333; width: 50rpx; text-align: right; }
.analysis-summary {
  margin-top: 20rpx;
  padding: 16rpx;
  background: #f8f9fa;
  border-radius: 8rpx;
}
.summary-text { font-size: 26rpx; color: #666; }
.highlight { color: #ff6b6b; font-weight: bold; }

.s-name { font-size: 28rpx; font-weight: bold; display: block; }
.s-action { font-size: 24rpx; color: #666; display: block; margin: 4rpx 0; }
.s-status { font-size: 22rpx; padding: 2rpx 8rpx; border-radius: 4rpx; }
.s-status.good { background: #e6fffa; color: #20C997; }
.s-status.warning { background: #fff5f5; color: #ff6b6b; }

/* Analysis Chart Styles */
.chart-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.card-title {
  font-size: 30rpx;
  font-weight: bold;
  margin-bottom: 30rpx;
  border-left: 8rpx solid #20C997;
  padding-left: 16rpx;
}

.bar-chart {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 300rpx;
  padding-bottom: 20rpx;
  border-bottom: 1px solid #eee;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
}

.bar-col {
  width: 40rpx;
  height: 80%;
  background: #f0f0f0;
  border-radius: 20rpx;
  position: relative;
  display: flex;
  align-items: flex-end;
}

.bar-fill {
  width: 100%;
  border-radius: 20rpx;
  transition: height 1s;
}

.bar-val {
  position: absolute;
  top: -30rpx;
  left: 50%;
  transform: translateX(-50%);
  font-size: 22rpx;
  color: #666;
}

.bar-label {
  margin-top: 10rpx;
  font-size: 24rpx;
  color: #666;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.prog-item { width: 100%; }
.prog-header { display: flex; justify-content: space-between; margin-bottom: 8rpx; }
.prog-name { font-size: 26rpx; color: #333; }
.prog-val { font-size: 26rpx; font-weight: bold; color: #20C997; }
.prog-track { height: 12rpx; background: #f0f0f0; border-radius: 6rpx; overflow: hidden; }
.prog-bar { height: 100%; background: #20C997; border-radius: 6rpx; }

/* History Styles */
.history-list {
  background: #fff;
  border-radius: 16rpx;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1px solid #f5f5f5;
}

.history-item:last-child { border-bottom: none; }

.h-left { display: flex; flex-direction: column; gap: 8rpx; }
.h-date { font-size: 24rpx; color: #999; }
.h-name { font-size: 30rpx; font-weight: bold; color: #333; }

.h-right { display: flex; align-items: center; gap: 20rpx; }
.h-stat { font-size: 24rpx; color: #666; }
.arrow { color: #ccc; font-size: 24rpx; }
</style>