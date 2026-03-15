<template>
  <view class="sport-container">
    <!-- 学生端：运动选择页面 -->
    <view v-if="role === 'student'" class="student-sport">
      <!-- 自定义导航栏 -->
      <view class="custom-nav-bar">
        <view class="nav-status-bar"></view>
        <view class="nav-content">
          <text class="nav-title">运动</text>
        </view>
      </view>

      <view class="content-wrapper">
        <!-- 运动选项卡片 -->
        <view class="sport-card" @click="goToRun">
          <view class="card-icon run-icon">
            <text class="icon-text">🏃</text>
          </view>
          <view class="card-content">
            <text class="card-title">户外跑步</text>
            <text class="card-desc">GPS定位，实时记录跑步轨迹</text>
          </view>
          <view class="card-arrow">›</view>
        </view>

        <view class="sport-card" @click="goToPhysicalTest">
          <view class="card-icon test-icon">
            <text class="icon-text">💪</text>
          </view>
          <view class="card-content">
            <text class="card-title">体能测试</text>
            <text class="card-desc">标准体测项目，记录测试成绩</text>
          </view>
          <view class="card-arrow">›</view>
        </view>

        <!-- 阳光跑看板 -->
        <view class="sunshine-section" @click="goToSunshineDetail">
          <view class="section-title">阳光跑看板</view>
          <view class="sunshine-content">
            <view class="sunshine-circle">
              <view class="circle-outer">
                <view class="circle-progress" :style="circleStyle"></view>
                <view class="circle-inner">
                  <text class="circle-count">{{ sunshine.total_valid_count }}</text>
                  <text class="circle-label">有效次数 / 20</text>
                </view>
              </view>
            </view>
            <view class="sunshine-info">
              <view class="score-row">
                <text class="score-label">当前积分</text>
                <text class="score-value">{{ sunshine.score }} 分</text>
              </view>
              <view class="status-row">
                <text class="status-label">今日状态</text>
                <text class="status-text" :class="sunshine.today_status">
                  {{ todayStatusText }}
                </text>
              </view>
              <text class="status-reason" v-if="sunshine.today_status === 'failed' && sunshine.today_fail_reason">
                审核未通过：{{ sunshine.today_fail_reason }} ❌
              </text>
            </view>
          </view>
        </view>

        <!-- 运动记录统计 -->
        <view class="stats-section">
          <view class="section-title">运动数据统计</view>
          <view class="stats-grid">
            <view class="stat-item">
              <text class="stat-value">{{ totalStats.distance }}</text>
              <text class="stat-label">总里程(km)</text>
            </view>
            <view class="stat-item">
              <text class="stat-value">{{ totalStats.duration }}</text>
              <text class="stat-label">总时长(min)</text>
            </view>
            <view class="stat-item">
              <text class="stat-value">{{ totalStats.calories }}</text>
              <text class="stat-label">总消耗(kcal)</text>
            </view>
            <view class="stat-item">
              <text class="stat-value">{{ totalStats.count }}</text>
              <text class="stat-label">运动次数</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 教师端：综合管理 -->
    <teacher-manage v-else ref="teacherManageRef" />
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { onShow, onHide } from '@dcloudio/uni-app';
import TeacherManage from '@/components/teacher-manage/teacher-manage.vue';
import { request, getSunshineStats } from '@/utils/request.js';

const role = ref('student');
const teacherManageRef = ref(null);

const totalStats = ref({
  distance: 0,
  duration: 0,
  calories: 0,
  count: 0
});

const sunshine = ref({
  total_valid_count: 0,
  score: 0,
  today_status: 'not_started',
  today_fail_reason: ''
});

const circleStyle = computed(() => {
  const max = 20;
  const percent = Math.min(1, (sunshine.value.total_valid_count || 0) / max);
  const deg = 360 * percent;
  return {
    backgroundImage: `conic-gradient(#20C997 ${deg}deg, #e5f7f3 ${deg}deg 360deg)`
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