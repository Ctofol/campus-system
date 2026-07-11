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
                <image class="entry-icon-text" src="/static/主页户外跑图标.png" mode="aspectFit" />
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
                <image class="entry-icon-text" src="/static/主页体能测试图标.png" mode="aspectFit" />
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
                <image class="today-ind-emoji-img" src="/static/勾号图标.png" mode="aspectFit" />
                <view class="today-ind-body">
                  <text class="today-ind-label">今日状态</text>
                  <text class="today-ind-val today-ind-val--ok" v-if="sunshine.today_status === 'success'">审核通过</text>
                  <text class="today-ind-val today-ind-val--pending" v-else>未开始</text>
                </view>
              </view>
              <view class="today-indicator" v-if="sunshine.today_status === 'failed'">
                <image class="today-ind-emoji-img" src="/static/叉号图标.png" mode="aspectFit" />
                <view class="today-ind-body">
                  <text class="today-ind-label">未通过原因</text>
                  <text class="today-ind-val today-ind-val--fail">{{ sunshine.today_fail_reason || '里程不足' }}</text>
                </view>
              </view>
              <view class="today-indicator" v-else>
              <view class="today-ind-icon today-ind-icon--count">
                <image class="today-ind-emoji-img" src="/static/有效次数图标.png" mode="aspectFit" />
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
              <image class="overview-icon" src="/static/总里程2.png" mode="aspectFit" />
              <text class="overview-val">{{ totalStats.distance }}</text>
              <text class="overview-unit">总里程(km)</text>
            </view>
            <view class="overview-item">
              <image class="overview-icon" src="/static/总时长2.png" mode="aspectFit" />
              <text class="overview-val">{{ totalStats.duration }}</text>
              <text class="overview-unit">总时长(min)</text>
            </view>
            <view class="overview-item">
              <image class="overview-icon" src="/static/总消耗.png" mode="aspectFit" />
              <text class="overview-val">{{ totalStats.calories }}</text>
              <text class="overview-unit">总消耗(kcal)</text>
            </view>
            <view class="overview-item">
              <image class="overview-icon" src="/static/运动次数.png" mode="aspectFit" />
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
                <image class="plan-icon-img" src="/static/训练图标.png" mode="aspectFit" />
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

const role = ref('student');
const teacherManageRef = ref(null);

const totalStats = ref({
  distance: 0, duration: 0, calories: 0, count: 0
});

const sunshine = ref({
  total_valid_count: 0,
  current_score: 0,
  score: 0,
  today_status: 'not_started',
  today_fail_reason: ''
});

const circleStyle = computed(() => {
  const total = Math.max(Number(sunshine.value.total_valid_count) || 0, 0);
  const pass = Math.min(total, 20);
  const extra = Math.max(Math.min(total - 20, 20), 0);
  const remain = Math.max(20 - pass, 0);
  const passDeg = (pass / 40) * 360;
  const extraDeg = (extra / 40) * 360;
  const remainDeg = (remain / 40) * 360;
  return {
    background: `conic-gradient(#20C997 0deg ${passDeg}deg, #ffb020 ${passDeg}deg ${passDeg + extraDeg}deg, #dcefe9 ${passDeg + extraDeg}deg ${passDeg + extraDeg + remainDeg}deg, #8b5cf6 ${passDeg + extraDeg + remainDeg}deg 360deg)`
  };
});

const todayStatusText = computed(() => {
  if (sunshine.value.today_status === 'success') return '今日目标已达成 ✅';
  if (sunshine.value.today_status === 'failed') return '审核未通过 ❌';
  return '今日尚未开始';
});

const goToRun = () => {
  uni.navigateTo({ url: '/pages/run/run' });
};

const goToPhysicalTest = () => {
  uni.navigateTo({ url: '/pages/test/test' });
};

const goToSunshineDetail = () => {
  if (role.value !== 'student') return;
  uni.navigateTo({ url: '/pages/sunshine/detail' });
};

const fetchTotalStats = async () => {
  try {
    const res = await request({
      url: '/student/total-stats',
      method: 'GET'
    });
    
    totalStats.value = {
      distance: res.total_distance ? res.total_distance.toFixed(1) : 0,
      duration: res.total_duration || 0,
      calories: res.total_calories || 0,
      count: res.total_count || 0
    };
  } catch (e) {
    console.error('Failed to fetch total stats:', e);
    // 优雅降级：使用占位数据
    totalStats.value = {
      distance: 0,
      duration: 0,
      calories: 0,
      count: 0
    };
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
  } catch (e) {
    console.error('Failed to fetch sunshine stats:', e);
  }
};

onShow(() => {
  role.value = uni.getStorageSync('userRole') || 'student';
  
  if (role.value === 'student') {
    fetchTotalStats();
    fetchSunshineStats();
  } else if (teacherManageRef.value && teacherManageRef.value.onPageShow) {
    teacherManageRef.value.onPageShow();
  }
});

onHide(() => {
  if (role.value === 'teacher' && teacherManageRef.value && teacherManageRef.value.onPageHide) {
    teacherManageRef.value.onPageHide();
  }
});

onMounted(() => {
  role.value = uni.getStorageSync('userRole') || 'student';
});
</script>

<style scoped>
.sport-container {
  min-height: 100vh;
  background: #f5f7fa;
}

/* 自定义导航栏 */
.custom-nav-bar {
  background: #20C997;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.nav-status-bar {
  height: var(--status-bar-height);
}

.nav-content {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-title {
  color: #fff;
  font-size: 32rpx;
  font-weight: bold;
}

/* 内容区域 */
.student-sport {
  min-height: 100vh;
}

.content-wrapper {
  padding-top: calc(var(--status-bar-height) + 44px + 30rpx);
  padding-bottom: 30rpx;
}

/* 运动卡片 */
.sport-card {
  background: #fff;
  margin: 0 30rpx 30rpx;
  padding: 40rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  transition: transform 0.2s ease;
}

.sport-card:active {
  transform: scale(0.98);
}

.card-icon {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 30rpx;
}

.run-icon {
  background: linear-gradient(135deg, #20C997 0%, #17a589 100%);
}

.test-icon {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
}

.icon-text {
  font-size: 60rpx;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 34rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 12rpx;
}

.card-desc {
  font-size: 26rpx;
  color: #999;
}

.card-arrow {
  font-size: 60rpx;
  color: #ddd;
  font-weight: 300;
}

/* 统计区域 */
.stats-section {
  background: #fff;
  margin: 0 30rpx;
  padding: 40rpx;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.sunshine-section {
  background: #fff;
  margin: 0 30rpx 30rpx;
  margin-top: 0;
  padding: 40rpx;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.sunshine-content {
  margin-top: 20rpx;
  display: flex;
  flex-direction: row;
  align-items: center;
}

.sunshine-circle {
  width: 200rpx;
  height: 200rpx;
  margin-right: 40rpx;
}

.circle-outer {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: #e5f7f3;
  display: flex;
  align-items: center;
  justify-content: center;
}

.circle-progress {
  position: absolute;
  width: 200rpx;
  height: 200rpx;
  border-radius: 50%;
}

.circle-inner {
  width: 140rpx;
  height: 140rpx;
  border-radius: 50%;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.circle-count {
  font-size: 36rpx;
  font-weight: bold;
  color: #20C997;
}

.circle-label {
  font-size: 22rpx;
  color: #999;
  margin-top: 4rpx;
}

.sunshine-info {
  flex: 1;
}

.score-row, .status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.score-label, .status-label {
  font-size: 26rpx;
  color: #666;
}

.score-value {
  font-size: 40rpx;
  font-weight: bold;
  color: #ff9800;
}

.status-text {
  font-size: 26rpx;
}

.status-text.success {
  color: #4caf50;
}

.status-text.failed {
  color: #f44336;
}

.status-text.not_started {
  color: #999;
}

.status-reason {
  font-size: 24rpx;
  color: #f44336;
  margin-top: 6rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 30rpx;
  padding-left: 20rpx;
  border-left: 8rpx solid #20C997;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30rpx;
  background: #f8f9fa;
  border-radius: 16rpx;
}

.stat-value {
  font-size: 48rpx;
  font-weight: bold;
  color: #20C997;
  margin-bottom: 12rpx;
  font-family: DINAlternate-Bold, sans-serif;
}

.stat-label {
  font-size: 24rpx;
  color: #666;
}
</style>
