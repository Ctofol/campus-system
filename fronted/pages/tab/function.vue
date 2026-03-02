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

        <!-- 运动记录统计 -->
        <view class="stats-section">
          <view class="section-title">本周运动统计</view>
          <view class="stats-grid">
            <view class="stat-item">
              <text class="stat-value">{{ weekStats.distance }}</text>
              <text class="stat-label">总里程(km)</text>
            </view>
            <view class="stat-item">
              <text class="stat-value">{{ weekStats.duration }}</text>
              <text class="stat-label">总时长(min)</text>
            </view>
            <view class="stat-item">
              <text class="stat-value">{{ weekStats.calories }}</text>
              <text class="stat-label">总消耗(kcal)</text>
            </view>
            <view class="stat-item">
              <text class="stat-value">{{ weekStats.count }}</text>
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
import { ref, onMounted } from 'vue';
import { onShow, onHide } from '@dcloudio/uni-app';
import TeacherManage from '@/components/teacher-manage/teacher-manage.vue';
import { request } from '@/utils/request.js';

const role = ref('student');
const teacherManageRef = ref(null);

const weekStats = ref({
  distance: 0,
  duration: 0,
  calories: 0,
  count: 0
});

const goToRun = () => {
  uni.navigateTo({ url: '/pages/run/run' });
};

const goToPhysicalTest = () => {
  uni.navigateTo({ url: '/pages/test/test' });
};

const fetchWeekStats = async () => {
  try {
    // TODO: 对接真实API获取本周统计
    // const res = await request({
    //   url: '/student/week-stats',
    //   method: 'GET'
    // });
    // weekStats.value = res;
    
    // 暂时使用占位数据
    weekStats.value = {
      distance: 0,
      duration: 0,
      calories: 0,
      count: 0
    };
  } catch (e) {
    console.error('Failed to fetch week stats:', e);
  }
};

onShow(() => {
  role.value = uni.getStorageSync('userRole') || 'student';
  
  if (role.value === 'student') {
    fetchWeekStats();
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