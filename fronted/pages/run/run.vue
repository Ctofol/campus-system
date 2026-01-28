<template>
  <view class="run">
    <!-- AI Robot Component -->
    <ai-chat-robot 
      v-model:visible="showAiRobot" 
      :run-data="currentRunData"
      @share="handleShareToTeacher"
    />
    
    <!-- AI Robot Float Button -->
    <view class="ai-float-btn" @click="openAiRobot" v-if="isRunning || distance > 0">
      <text class="ai-btn-icon">🤖</text>
      <text class="ai-btn-text">AI助手</text>
    </view>

    <!-- 0. 顶部天气与成就（新增） -->
    <view class="top-widgets">
      <view class="weather-widget">
        <view class="weather-left">
          <text class="weather-temp">24°C</text>
          <text class="weather-status">☀️ 晴朗</text>
        </view>
        <view class="weather-right">
          <text class="weather-tips">空气优 · 适宜跑步</text>
        </view>
      </view>
      <scroll-view scroll-x class="achievements-scroll" :show-scrollbar="false">
        <view class="badge-item" v-for="(badge, idx) in achievements" :key="idx">
          <text class="badge-icon">{{ badge.icon }}</text>
          <text class="badge-name">{{ badge.name }}</text>
        </view>
      </scroll-view>
    </view>

    <!-- 1. 搜索打卡点（仅校园打卡用） -->
    <view class="search-bar" v-if="currentMode === 'campus'">
      <input 
        v-model="checkpointName" 
        placeholder="输入校园打卡点（如：操场/跑道）"
        class="search-input"
      />
      <button @click="searchCheckpoint" class="search-btn">搜索</button>
    </view>

    <!-- 2. 地图展示 -->
    <view class="overview-card">
      <text class="overview-title">今日跑步概览</text>
      <view class="overview-meta">
        <text>次数：{{ todayRunCount }}</text>
        <text>里程：{{ todayRunDistance }} km</text>
      </view>
      <text v-if="teacherRunTask" class="task-tip">教师任务：{{ teacherRunTask }}</text>
    </view>
    <map 
      class="map" 
      :latitude="lat" 
      :longitude="lng" 
      :markers="markers"
      :polyline="polyline"
    ></map>

    <!-- 2.5 推荐路线（新增） -->
    <view class="routes-card" v-if="currentMode === 'normal'">
      <view class="card-header" @click="toggleRoutes">
        <text class="card-title">🏃 推荐路线</text>
        <text class="card-toggle">{{ showRoutes ? '收起' : '展开' }}</text>
      </view>
      <view class="routes-list" v-if="showRoutes">
        <view class="route-item" v-for="(route, idx) in recommendRoutes" :key="idx" @click="useRoute(route)">
          <view class="route-info">
            <text class="route-name">{{ route.name }}</text>
            <text class="route-meta">{{ route.distance }}km · {{ route.difficulty }}</text>
          </view>
          <text class="route-action">去跑步 ></text>
        </view>
      </view>
    </view>

    <!-- 3. 核心跑步模式切换（普通/专项/校园，三选一） -->
    <view class="mode-switch">
      <text class="mode-item" :class="{active: currentMode === 'normal'}" @click="switchMode('normal')">普通跑步</text>
      <text class="mode-item" :class="{active: currentMode === 'police'}" @click="switchMode('police')">专项测试</text>
      <text class="mode-item" :class="{active: currentMode === 'campus'}" @click="switchMode('campus')">校园打卡</text>
    </view>

    <!-- 4. 专项测试计划（独立模块，仅专项模式显示） -->
    <view v-if="currentMode === 'police'" class="police-plan">
      <text class="plan-title">🎯 2000米体能专项训练</text>
      <view class="plan-info">
        <text class="info-item">目标距离：<span class="highlight">{{policeTargetDistance/1000}}公里</span></text>
        <text class="info-item">达标配速：<span class="highlight">{{policeTargetPace}}分钟/公里</span></text>
        <text class="info-item">建议标准：<span class="highlight">可按学校或课程要求配置</span></text>
      </view>
    </view>

    <!-- 5. 普通跑步 -->
    <view v-if="currentMode === 'normal'" class="run-mode-box">
      <view v-if="!isRunning" class="start-box">
        <text class="tip">无地点/距离限制，自由记录跑步轨迹</text>
        <button @click="startNormalRun" class="start-btn">开始跑步</button>
      </view>
      <view v-else class="running-box">
        <text class="data">时长：{{duration}}秒 | 已跑：{{(distance/1000).toFixed(2)}}km | 步数：{{stepCount}} | 心率：{{heartRate}}次/分</text>
        <view class="progress-wrap">
          <view class="progress-bar"><view class="progress-fill" :style="{width: normalProgress + '%'}"></view></view>
          <text class="progress-text">今日目标 {{dailyTarget}} km · 完成 {{(distance/1000).toFixed(2)}} km</text>
        </view>
        <button @click="stopRun" class="stop-btn">结束跑步</button>
      </view>
    </view>

    <!-- 6. 专项跑步（按2000米目标跑） -->
    <view v-if="currentMode === 'police'" class="run-mode-box">
      <view v-if="!isRunning" class="start-box">
        <text class="tip">按课程要求完成2000米跑，自动校验配速是否达标</text>
        <button @click="startPoliceRun" class="start-btn">开始专项训练</button>
      </view>
      <view v-else class="running-box">
        <text class="data">时长：{{duration}}秒 | 已跑：{{(distance/1000).toFixed(2)}}km / 目标：2km</text>
        <text class="data">剩余：{{((policeTargetDistance - distance)/1000).toFixed(2)}}km | 配速：{{currentPace.toFixed(1)}}分钟/公里</text>
        <text class="data">心率：{{heartRate}}次/分 | 步数：{{stepCount}}</text>
        <text class="pace-status" :style="{color: currentPace <= policeTargetPace ? 'green' : 'red'}">
          {{currentPace <= policeTargetPace ? '✅ 配速达标' : '❌ 配速未达标'}}
        </text>
        <!-- 达到目标距离自动提示 -->
        <text class="finish-tip" v-if="distance >= policeTargetDistance">🎉 已完成2000米目标！</text>
        <view class="progress-wrap">
          <view class="progress-bar"><view class="progress-fill" :style="{width: policeProgress + '%'}"></view></view>
          <text class="progress-text">专项目标 2 km · 完成 {{(distance/1000).toFixed(2)}} km</text>
        </view>
        <button @click="stopRun" class="stop-btn">结束训练</button>
      </view>
    </view>

    <!-- 7. 校园打卡 -->
    <view v-if="currentMode === 'campus'" class="run-mode-box">
      <view v-if="!checkpoint.name" class="no-checkpoint">
        <text class="tip">请先搜索校园打卡点</text>
      </view>
      <view v-else>
        <view v-if="!isRunning" class="start-box">
          <text class="checkpoint-info">打卡点：{{checkpoint.name}}（需到达10米内）</text>
          <button @click="startCampusRun" class="start-btn">开始打卡</button>
        </view>
        <view v-else class="running-box">
          <text class="data">时长：{{duration}}秒 | 距打卡点：{{distanceToCheckpoint}}米 | 步数：{{stepCount}} | 心率：{{heartRate}}次/分</text>
          <text class="reach-status" :style="{color: isReach ? 'green' : 'red'}">
            {{isReach ? '✅ 已到达打卡点' : '❌ 未到达打卡点'}}
          </text>
          <button @click="stopRun" class="stop-btn">结束打卡</button>
        </view>
      </view>
    </view>
    
    <!-- 底部导航栏 -->
    <CustomTabBar current="/pages/run/run" />
  </view>
</template>

<script setup>
// 统一导入规范
import { ref, computed, onUnmounted } from 'vue';
import { onShow, onLoad } from '@dcloudio/uni-app';
import AiChatRobot from '@/components/ai-chat-robot/ai-chat-robot.vue';
import CustomTabBar from '@/components/CustomTabBar/CustomTabBar.vue';
import { submitActivity } from '@/utils/request.js';

// 组件卸载时清理定时器
onUnmounted(() => {
  if (timer) clearInterval(timer);
  stopStepCount();
});

// AI Robot Logic
const showAiRobot = ref(false);
const currentRunData = computed(() => ({
  distance: distance.value,
  pace: currentPace.value || (distance.value > 0 ? (duration.value/60)/(distance.value/1000) : 0),
  heartRate: heartRate.value,
  stepCount: stepCount.value
}));

const openAiRobot = () => {
  showAiRobot.value = true;
};

const handleShareToTeacher = (card) => {
  // Save shared report to storage for teacher to see (mock)
  const report = {
    studentName: uni.getStorageSync('userInfo')?.name || '学员',
    time: new Date().toLocaleString(),
    card: card
  };
  // In a real app, this would be an API call. 
  // Here we mock it by saving to a global list that teacher page reads.
  let sharedReports = uni.getStorageSync('mockSharedReports') || [];
  sharedReports.unshift(report);
  uni.setStorageSync('mockSharedReports', sharedReports);
};

// 概览与任务提示
const todayRunCount = ref(0);
const todayRunDistance = ref(0);
const teacherRunTask = ref('');
const dailyTarget = ref(5);
const normalProgress = ref(0);
const policeProgress = ref(0);
const historyList = ref([]);

// 新增数据
const achievements = ref([
  { name: '初次开跑', icon: '🏅' },
  { name: '五公里达人', icon: '🏃‍♂️' },
  { name: '全勤周', icon: '🔥' },
  { name: '早起鸟', icon: '🐦' }
]);
const showRoutes = ref(false);
const recommendRoutes = ref([
  { name: '环校外圈跑', distance: 5.2, difficulty: '中等' },
  { name: '湖畔林荫道', distance: 3.0, difficulty: '简单' },
  { name: '体育场冲刺', distance: 1.5, difficulty: '困难' }
]);
const toggleRoutes = () => showRoutes.value = !showRoutes.value;
const useRoute = (route) => {
  uni.showToast({ title: `已加载路线：${route.name}`, icon: 'none' });
  dailyTarget.value = route.distance;
};

// 1. 地图/打卡点数据
const checkpointName = ref('');
const lat = ref(0);
const lng = ref(0);
const markers = ref([]);
const polyline = ref([]);
const checkpoint = ref({});

// 2. 跑步核心配置
const currentMode = ref('normal'); // normal-普通 police-警务 campus-校园
const isRunning = ref(false);
const duration = ref(0);
const distance = ref(0); // 已跑距离（米）
const distanceToCheckpoint = ref(0);
const isReach = ref(false);
const stepCount = ref(0);
const heartRate = ref(80);
let timer = null;
let accelerometerListener = null;

// 3. 警务专项固定配置（按公安考核标准）
const policeTargetDistance = ref(2000); // 固定2000米
const policeTargetPace = ref(6.5); // 达标配速：6.5分钟/公里（男生标准）
// 计算当前配速（分钟/公里）
const currentPace = computed(() => {
  const km = distance.value / 1000;
  const min = duration.value / 60;
  return km === 0 ? 0 : min / km;
});

// 接收页面参数
onLoad((options) => {
  if (options.mode) {
    currentMode.value = options.mode;
  }
  if (options.target) {
    policeTargetDistance.value = parseInt(options.target);
  }
  if (options.course) {
    uni.showToast({ title: `开始课程：${options.course}`, icon: 'none' });
  }
});

// 页面显示时初始化
onShow(() => {
    const role = uni.getStorageSync('userRole') || uni.getStorageSync('role');
    if (role === 'teacher') {
      uni.showToast({ title: '该功能仅对学生开放', icon: 'none' });
      setTimeout(() => {
        uni.redirectTo({ url: '/pages/teacher/home/home' });
      }, 800);
      return;
    }
  // 1. 处理从首页跳转过来的模式参数 (因 switchTab 不支持 URL 传参)
  const targetMode = uni.getStorageSync('runMode');
  if (targetMode) {
    switchMode(targetMode); // 使用 switchMode 方法以确保状态重置
    uni.removeStorageSync('runMode'); // 消费后清除
  }

  getLocation();
  checkpoint.value = uni.getStorageSync('checkpoint') || {};
  if (checkpoint.value.name) {
    addCheckpointMarker(checkpoint.value.lat, checkpoint.value.lng, checkpoint.value.name);
  }
  const records = uni.getStorageSync('runRecordsList') || [];
  const now = new Date();
  const dayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const dayEnd = dayStart + 24 * 60 * 60 * 1000;
  let c = 0;
  let d = 0;
  records.forEach(r => {
    const t = new Date(r.createTime).getTime();
    const isRunType = r.type ? r.type === 'run' : true;
    if (isRunType && t >= dayStart && t < dayEnd) {
      c += 1;
      d += Number(r.distance) || 0;
    }
  });
  todayRunCount.value = c;
  todayRunDistance.value = Number(d.toFixed(2));
  historyList.value = buildHistory(records);
  const taskStr = uni.getStorageSync('teacherTask');
  if (taskStr) {
    try {
      const obj = typeof taskStr === 'string' ? JSON.parse(taskStr) : taskStr;
      teacherRunTask.value = obj.title || '';
    } catch (e) {
      teacherRunTask.value = '';
    }
  }
});

// 4. 定位优化（含权限申请+校园围栏）
const getLocation = () => {
  // #ifdef H5
  doGetLocation();
  // #endif

  // #ifndef H5
  uni.authorize({
    scope: 'scope.userLocation',
    success: () => {
      doGetLocation();
    },
    fail: () => {
      uni.showModal({
        title: '权限申请',
        content: '需要定位权限才能使用打卡/跑步功能，请前往设置开启',
        confirmText: '去设置',
        success: (res) => {
          if (res.confirm) uni.openSetting();
        }
      });
    }
  });
  // #endif
};

const doGetLocation = () => {
  uni.getLocation({
    type: 'gcj02',
    accuracy: 'high',
    success: (res) => {
      lat.value = res.latitude;
      lng.value = res.longitude;
      markers.value = [{
        id: 0,
        latitude: res.latitude,
        longitude: res.longitude,
        title: '我的位置',
        iconPath: '/static/location.png',
        width: 30,
        height: 30
      }];
      // 校园围栏（仅校园打卡用）
      const campusLatMin = 39.90;
      const campusLatMax = 39.92;
      const campusLngMin = 116.39;
      const campusLngMax = 116.41;
      const isInCampus = res.latitude >= campusLatMin && res.latitude <= campusLatMax 
                      && res.longitude >= campusLngMin && res.longitude <= campusLngMax;
      if (!isInCampus && currentMode.value === 'campus') {
        uni.showToast({ title: '仅校园内可进行打卡', icon: 'none' });
      }
    },
    fail: (err) => {
      console.error('Location failed:', err);
      let msg = '定位失败，已使用模拟位置';
      
      // #ifdef H5
      // Chrome等浏览器限制非HTTPS环境无法使用定位（localhost除外）
      if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
        msg = 'H5定位需HTTPS，已切模拟位置';
      } else if (err.errMsg && err.errMsg.indexOf('auth') !== -1) {
        msg = '定位权限被拒，已切模拟位置';
      }
      // #endif

      uni.showToast({ title: msg, icon: 'none', duration: 3000 });
      
      // 降级使用模拟位置（北京天安门附近）
      lat.value = 39.908823;
      lng.value = 116.397470;
      markers.value = [{ 
        id: 0, 
        latitude: 39.908823, 
        longitude: 116.397470, 
        title: '我的位置 (模拟)', 
        iconPath: '/static/location.png', 
        width: 30, 
        height: 30 
      }];
    }
  });
};

// 5. 搜索打卡点（仅校园模式）
const searchCheckpoint = () => {
  if (!checkpointName.value) {
    uni.showToast({ title: '请输入打卡点名称', icon: 'none' });
    return;
  }
  const newCheckpoint = {
    name: checkpointName.value,
    lat: lat.value + 0.001,
    lng: lng.value + 0.001
  };
  uni.setStorageSync('checkpoint', newCheckpoint);
  checkpoint.value = newCheckpoint;
  addCheckpointMarker(newCheckpoint.lat, newCheckpoint.lng, newCheckpoint.name);
  polyline.value = [{
    points: [
      { latitude: lat.value, longitude: lng.value },
      { latitude: newCheckpoint.lat, longitude: newCheckpoint.lng }
    ],
    color: '#FF0000',
    width: 5
  }];
  uni.showToast({ title: `找到${newCheckpoint.name}`, icon: 'success' });
};

// 6. 添加打卡点标记
const addCheckpointMarker = (lat, lng, name) => {
  markers.value.push({
    id: 1,
    latitude: lat,
    longitude: lng,
    title: name,
    iconPath: '/static/checkpoint.png',
    width: 40,
    height: 40
  });
};

// 7. 切换跑步模式（普通/警务/校园）
const switchMode = (mode) => {
  // 切换模式时重置所有跑步状态
  isRunning.value = false;
  clearInterval(timer);
  stopStepCount();
  duration.value = 0;
  distance.value = 0;
  stepCount.value = 0;
  heartRate.value = 80;
  currentMode.value = mode;
};

// 8. 步数统计（加速度传感器）
const startStepCount = () => {
  accelerometerListener = uni.onAccelerometerChange((res) => {
    const acceleration = Math.sqrt(res.x*res.x + res.y*res.y + res.z*res.z);
    if (acceleration > 15) stepCount.value += 1;
  });
};
const stopStepCount = () => {
  if (accelerometerListener) {
    uni.offAccelerometerChange(accelerometerListener);
    accelerometerListener = null;
  }
};

// 9. 心率更新+预警
const updateHeartRate = () => {
  heartRate.value = 80 + Math.floor(duration.value / 10);
  if (heartRate.value > 180) {
    uni.showModal({
      title: '健康预警',
      content: `当前心率过高（${heartRate.value}次/分），建议降速休息`,
      showCancel: false
    });
  }
};

// 10. 开始跑步（分三种模式）
// 普通跑步（无固定目标）
const startNormalRun = () => {
  isRunning.value = true;
  duration.value = 0;
  distance.value = 0;
  stepCount.value = 0;
  heartRate.value = 80;
  startStepCount();
  timer = setInterval(() => {
    duration.value += 1;
    distance.value += Math.random() * 5; // 模拟每秒跑5米左右
    normalProgress.value = Math.min(100, ((distance.value/1000) / dailyTarget.value) * 100);
    updateHeartRate();
  }, 1000);
};

// 专项训练（固定2000米，按达标配速跑）
const startPoliceRun = () => {
  isRunning.value = true;
  duration.value = 0;
  distance.value = 0;
  stepCount.value = 0;
  heartRate.value = 80;
  startStepCount();
  // 按达标配速6.5分钟/公里推进（约2.56米/秒）
  timer = setInterval(() => {
    duration.value += 1;
    distance.value += 2.56; // 精准匹配6.5分钟/公里的配速
    policeProgress.value = Math.min(100, (distance.value / policeTargetDistance.value) * 100);
    updateHeartRate();
    // 达到目标距离弹窗提示
    if (distance.value >= policeTargetDistance.value && !uni.getStorageSync('policeFinishTip')) {
      uni.showToast({ title: '已完成2000米目标！', icon: 'success' });
      uni.setStorageSync('policeFinishTip', '1');
    }
  }, 1000);
};

// 校园打卡
const startCampusRun = () => {
  isRunning.value = true;
  duration.value = 0;
  distanceToCheckpoint.value = 50;
  isReach.value = false;
  stepCount.value = 0;
  heartRate.value = 80;
  startStepCount();
  timer = setInterval(() => {
    duration.value += 1;
    distanceToCheckpoint.value = Math.max(0, distanceToCheckpoint.value - 0.5);
    isReach.value = distanceToCheckpoint.value <= 10;
    updateHeartRate();
  }, 1000);
};

// 11. 结束跑步（统一逻辑）
const stopRun = async () => {
  isRunning.value = false;
  clearInterval(timer);
  stopStepCount();

  const runData = {
    type: currentMode.value === 'police' ? 'test' : 'run',
    source: 'free',
    started_at: new Date(Date.now() - duration.value * 1000).toISOString(),
    ended_at: new Date().toISOString(),
    metrics: {
      distance: distance.value / 1000, // Convert meters to km
      duration: duration.value,
      pace: currentPace.value.toFixed(1),
      count: currentMode.value === 'police' ? 1 : null,
      qualified: currentMode.value === 'police' ? currentPace.value <= policeTargetPace.value : false
    },
    evidence: []
  };

  try {
    uni.showLoading({ title: '提交中...' });
    const res = await submitActivity(runData);
    uni.hideLoading();
    
    // Jump to result page with data
    uni.navigateTo({
      url: `/pages/result/result?data=${encodeURIComponent(JSON.stringify(runData))}`
    });
  } catch (error) {
    uni.hideLoading();
    console.error('Submit failed:', error);
    uni.showToast({
      title: (error && error.detail) ? `提交失败：${error.detail}` : '提交失败，请重试',
      icon: 'none',
      duration: 2000
    });
  }
};

const buildHistory = (records) => {
  const days = 7;
  const now = new Date();
  const arr = [];
  for (let i=0;i<days;i++) {
    const day = new Date(now.getFullYear(), now.getMonth(), now.getDate()-i);
    const start = new Date(day.getFullYear(), day.getMonth(), day.getDate()).getTime();
    const end = start + 24*60*60*1000;
    const runRecs = records.filter(r => {
      const t = new Date(r.createTime).getTime();
      const isRunType = r.type ? r.type === 'run' : true;
      return isRunType && t>=start && t<end;
    });
    const count = runRecs.length;
    const distanceSum = runRecs.reduce((s,x)=>s+Number(x.distance||0),0);
    arr.push({ date: `${day.getMonth()+1}/${day.getDate()}`, count, distance: Number(distanceSum.toFixed(2)) });
  }
  return arr.reverse();
};
</script>

<style scoped>
.run {
  padding: 20rpx;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
}
/* 新增顶部样式 */
.top-widgets {
  margin-bottom: 20rpx;
}
.weather-widget {
  background: linear-gradient(135deg, #74ebd5 0%, #ACB6E5 100%);
  border-radius: 12rpx;
  padding: 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15rpx;
  color: #fff;
  box-shadow: 0 4rpx 10rpx rgba(0,0,0,0.1);
}
.weather-left { display: flex; flex-direction: column; }
.weather-temp { font-size: 40rpx; font-weight: bold; }
.weather-status { font-size: 26rpx; opacity: 0.9; }
.weather-tips { font-size: 24rpx; background: rgba(255,255,255,0.2); padding: 4rpx 12rpx; border-radius: 20rpx; }

.achievements-scroll {
  white-space: nowrap;
  width: 100%;
}
.badge-item {
  display: inline-block;
  background: #fff;
  padding: 10rpx 20rpx;
  border-radius: 30rpx;
  margin-right: 15rpx;
  box-shadow: 0 2rpx 5rpx rgba(0,0,0,0.05);
}
.badge-icon { margin-right: 8rpx; }
.badge-name { font-size: 24rpx; color: #333; }

/* 推荐路线样式 */
.routes-card {
  background: #fff;
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-size: 30rpx; font-weight: bold; color: #333; }
.card-toggle { font-size: 24rpx; color: #999; }
.routes-list { margin-top: 15rpx; border-top: 1px solid #f5f5f5; padding-top: 10rpx; }
.route-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15rpx 0;
  border-bottom: 1px dashed #eee;
}
.route-item:last-child { border-bottom: none; }
.route-info { display: flex; flex-direction: column; }
.route-name { font-size: 28rpx; color: #333; }
.route-meta { font-size: 24rpx; color: #999; margin-top: 4rpx; }
.route-action { font-size: 24rpx; color: #20C997; }

.overview-card {
  background: #ffffff;
  border: 1px solid #eee;
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
}
.overview-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 10rpx;
}
.overview-meta {
  font-size: 28rpx;
  color: #666;
  display: flex;
  justify-content: space-between;
}
.task-tip {
  margin-top: 10rpx;
  font-size: 26rpx;
  color: #d81e06;
}
.progress-wrap { padding: 10rpx 20rpx; }
.progress-bar { width: 100%; height: 16rpx; background: #eee; border-radius: 10rpx; overflow: hidden; }
.progress-fill { height: 100%; background: #20C997; width: 0; }
.progress-text { font-size: 26rpx; color: #666; text-align: center; margin-top: 6rpx; display: block; }
/* 搜索栏仅校园模式显示 */
.search-bar {
  display: flex;
  margin-bottom: 20rpx;
}
.search-input {
  flex: 1;
  border: 1px solid #eee;
  padding: 15rpx;
  border-radius: 8rpx;
  margin-right: 10rpx;
}
.search-btn {
  background-color: #20C997;
  color: #fff;
  border: none;
  border-radius: 8rpx;
  padding: 0 20rpx;
}
/* 地图 */
.map {
  width: 100%;
  height: 300rpx;
  border-radius: 10rpx;
  margin-bottom: 20rpx;
}
/* 模式切换（三选一） */
.mode-switch {
  display: flex;
  justify-content: center;
  margin-bottom: 20rpx;
  flex-wrap: wrap;
}
.mode-item {
  padding: 15rpx 30rpx;
  margin: 0 8rpx 10rpx;
  font-size: 30rpx;
  border-bottom: 2rpx solid transparent;
}
.mode-item.active {
  border-bottom-color: #d81e06;
  color: #d81e06;
  font-weight: bold;
}
/* 警务专项计划模块 */
.police-plan {
  background-color: #fdf2f0;
  border: 1px solid #fef0f0;
  border-radius: 10rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
}
.plan-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #d81e06;
  display: block;
  text-align: center;
  margin-bottom: 15rpx;
}
.plan-info {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
}
.info-item {
  font-size: 26rpx;
  color: #666;
  margin: 5rpx 10rpx;
}
.highlight {
  color: #d81e06;
  font-weight: bold;
}
/* 通用跑步模块样式 */
.run-mode-box {
  margin-bottom: 20rpx;
}
.tip {
  font-size: 28rpx;
  color: #666;
  text-align: center;
  margin-bottom: 20rpx;
  padding: 0 20rpx;
}
.no-checkpoint {
  text-align: center;
  padding: 20rpx 0;
}
.checkpoint-info {
  font-size: 30rpx;
  color: #333;
  text-align: center;
  margin-bottom: 20rpx;
  display: block;
}
.start-box {
  text-align: center;
}
.start-btn {
  width: 600rpx;
  height: 80rpx;
  line-height: 80rpx;
  background-color: #20C997;
  color: #fff;
  border: none;
  border-radius: 10rpx;
  font-size: 32rpx;
}
.running-box {
  text-align: center;
  padding: 10rpx 0;
}
.data {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 10rpx;
  display: block;
}
.pace-status {
  font-size: 28rpx;
  margin-bottom: 15rpx;
  display: block;
}
.finish-tip {
  font-size: 28rpx;
  color: #20C997;
  font-weight: bold;
  margin-bottom: 15rpx;
  display: block;
}
.reach-status {
  font-size: 28rpx;
  margin-bottom: 15rpx;
  display: block;
}
.stop-btn {
  width: 600rpx;
  height: 80rpx;
  line-height: 80rpx;
  background-color: #d81e06;
  color: #fff;
  border: none;
  border-radius: 10rpx;
  font-size: 32rpx;
}

/* AI Float Button */
.ai-float-btn {
  position: fixed;
  right: 30rpx;
  bottom: 200rpx;
  background: #fff;
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: pulse 2s infinite;
}

.ai-btn-icon {
  font-size: 40rpx;
  margin-bottom: 4rpx;
}

.ai-btn-text {
  font-size: 18rpx;
  color: #333;
  font-weight: bold;
}

@keyframes pulse {
  0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(32, 201, 151, 0.4); }
  70% { transform: scale(1.05); box-shadow: 0 0 0 20rpx rgba(32, 201, 151, 0); }
  100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(32, 201, 151, 0); }
}
</style>
