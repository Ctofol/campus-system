<template>
  <view class="run">
    <!-- Custom Navigation Bar -->
    <view class="custom-navbar" :style="{paddingTop: statusBarHeight + 'px'}">
      <view class="navbar-content">
        <text class="navbar-title">跑步</text>
      </view>
    </view>
    <view class="content-spacer" :style="{height: (statusBarHeight + 44) + 'px'}"></view>

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
      <!-- Map Select Button -->
      <view class="map-select-btn" @click="handleMapSelect">
        <text class="map-icon">🗺️</text>
      </view>
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
      :enable-zoom="true"
      :min-scale="3"
      :max-scale="20"
      scale="16"
      :show-location="true"
    >
       <!-- Use style display instead of v-if to avoid DOM node removal errors on native map -->
       <cover-view class="location-status-bar" :style="{ display: locationState === 'success' ? 'none' : 'flex' }">
         <text class="status-text">{{ locationStatusText }}</text>
       </cover-view>

       <cover-view class="map-controls">
         <cover-view class="control-btn" @click="handleRelocate">
           <cover-image src="/static/location.png" class="control-icon" />
         </cover-view>
       </cover-view>
    </map>

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
        <text class="data">时长：{{duration}}秒 | 已跑：{{((distance || 0)/1000).toFixed(2)}}km | 速度：{{currentSpeedKmh}}km/h</text>
        <text class="data">步数：{{stepCount}} | 心率：{{heartRate}}次/分 | 平均速度：{{avgSpeedKmh}}km/h</text>
        <view class="progress-wrap">
          <view class="progress-bar"><view class="progress-fill" :style="{width: normalProgress + '%'}"></view></view>
          <text class="progress-text">今日目标 {{dailyTarget}} km · 完成 {{((distance || 0)/1000).toFixed(2)}} km</text>
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
import { onShow, onLoad, onHide } from '@dcloudio/uni-app';
import AiChatRobot from '@/components/ai-chat-robot/ai-chat-robot.vue';
import CustomTabBar from '@/components/CustomTabBar/CustomTabBar.vue';
import { submitActivity, getCheckpoints, checkIn } from '@/utils/request.js';
import { getCurrentLocation } from '@/utils/location.js';

// Navbar Settings
const statusBarHeight = ref(20);
onLoad(() => {
  const sys = uni.getSystemInfoSync();
  statusBarHeight.value = sys.statusBarHeight || 20;
});

// 组件卸载时清理定时器
// Moved to later section


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

// 确保导航栏标题显示
  onShow(() => {
    isPageActive = true;
    console.log('run.vue onShow triggered');
    // 强制设置导航栏标题和颜色
    uni.setNavigationBarTitle({
      title: '跑步'
    });
    uni.setNavigationBarColor({
      frontColor: '#ffffff',
      backgroundColor: '#20C997'
    });
    
    const role = uni.getStorageSync('userRole') || uni.getStorageSync('role');
    if (role === 'teacher') {
      uni.showToast({ title: '该功能仅对学生开放', icon: 'none' });
      setTimeout(() => {
        uni.redirectTo({ url: '/pages/teacher/home/home' });
      }, 800);
      return;
    }

    // 1. 处理从首页跳转过来的模式参数
    const targetMode = uni.getStorageSync('runMode');
    if (targetMode) {
      switchMode(targetMode); 
      uni.removeStorageSync('runMode');
    }

    startLocationService();
    
    // Load Checkpoints for Campus Mode
    getCheckpoints().then(data => {
      availableCheckpoints.value = data;
    }).catch(err => {
      console.error('Failed to load checkpoints', err);
    });

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
    
    // Only load from storage if not already set by URL params (taskId)
    if (!taskId.value) {
      const taskStr = uni.getStorageSync('teacherTask');
      if (taskStr) {
        try {
          const obj = typeof taskStr === 'string' ? JSON.parse(taskStr) : taskStr;
          teacherRunTask.value = obj.title || '';
        } catch (e) {
          teacherRunTask.value = '';
        }
      }
    }
  });

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
const availableCheckpoints = ref([]);
const useRoute = (route) => {
  uni.showToast({ title: `已加载路线：${route.name}`, icon: 'none' });
  dailyTarget.value = route.distance;
};

// 1. 地图/打卡点数据
const locationState = ref('idle'); // idle, locating, success, fail
let locationRetryTimer = null;

const checkpointName = ref('');
const lat = ref(39.909);
const lng = ref(116.397);
const markers = ref([]);

// Separate line states for better management
const runPolyline = ref({
  points: [],
  color: '#007AFF',
  width: 4,
  arrowLine: true // Show arrows on the path
});
const navPolyline = ref(null);

const polyline = ref([]); // Final array for map component
const checkpoint = ref({});
const trajectoryPoints = ref([]); // Store real GPS points
const checkinRecords = ref([]); // Store successful check-ins

// Helper to update map polyline with deep clone to force render
const updateMapPolyline = () => {
  const lines = [];
  // 1. Add running trajectory (Blue)
  if (runPolyline.value.points.length > 0) {
    // Deep clone to ensure Vue detects change
    lines.push(JSON.parse(JSON.stringify(runPolyline.value)));
  } else {
    // Keep an empty line placeholder if needed, or just omit
    lines.push({ ...runPolyline.value, points: [] });
  }
  
  // 2. Add navigation line (Red) if exists
  if (navPolyline.value) {
    lines.push(JSON.parse(JSON.stringify(navPolyline.value)));
  }
  
  polyline.value = lines;
};

// Distance Calculation (Haversine Formula)
const getDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371e3; // Earth radius in meters
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLng/2) * Math.sin(dLng/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c; // Distance in meters
};

// Unified location update logic
const updateLocationLogic = (newLat, newLng, speed) => {
  lat.value = newLat;
  lng.value = newLng;
  markers.value[0] = {
    id: 0,
    latitude: newLat,
    longitude: newLng,
    title: '我的位置',
    iconPath: '/static/location.png',
    width: 30,
    height: 30
  };

  if (isRunning.value) {
    // 1. Initial point
    if (trajectoryPoints.value.length === 0) {
        const point = { latitude: newLat, longitude: newLng, timestamp: Date.now(), speed: speed || currentSpeed.value };
        trajectoryPoints.value.push(point);
        runPolyline.value.points.push({ latitude: newLat, longitude: newLng });
        updateMapPolyline();
        return;
    }

    // 2. Subsequent points
    const lastPoint = trajectoryPoints.value[trajectoryPoints.value.length - 1];
    const d = getDistance(lastPoint.latitude, lastPoint.longitude, newLat, newLng);
    const timeDiff = (Date.now() - lastPoint.timestamp) / 1000; // seconds
    
    // Speed check: Max 20m/s (72km/h) - Humanly impossible for running, likely GPS drift
    // If timeDiff is very small (e.g. duplicate updates), skip
    if (timeDiff < 0.5) return; 
    
    const calculatedSpeed = d / timeDiff;

    // Filter Logic:
    // 1. Ignore tiny jitters (d < 2m) to keep path smooth
    // 2. Ignore teleportation (Speed > 20m/s)
    if (d >= 2 && calculatedSpeed < 20) {
        distance.value += d;
        
        const point = { latitude: newLat, longitude: newLng, timestamp: Date.now(), speed: speed || calculatedSpeed };
        trajectoryPoints.value.push(point);
        
        // Update Blue Line Points
        runPolyline.value.points.push({ latitude: newLat, longitude: newLng });
        
        // Force Map Update
        updateMapPolyline();

        // Checkpoint logic
        if (currentMode.value === 'campus' && checkpoint.value.lat) {
          distanceToCheckpoint.value = Math.floor(getDistance(newLat, newLng, checkpoint.value.lat, checkpoint.value.lng));
          // Tolerance increased to 100m as requested for better user experience
          if (distanceToCheckpoint.value <= (checkpoint.value.radius || 100)) { 
            isReach.value = true;
            if (!uni.getStorageSync('checkpointReached')) {
               if (checkpoint.value.id) {
                 checkIn({ lat: newLat, lng: newLng, checkpoint_id: checkpoint.value.id })
                   .then(res => {
                     if (res.success) {
                       uni.showToast({ title: '打卡成功！', icon: 'success' });
                       checkinRecords.value.push({ checkpoint_id: checkpoint.value.id, time: new Date().toISOString(), lat: newLat, lng: newLng });
                     }
                   }).catch(() => {});
               } else {
                  uni.showToast({ title: '已到达打卡点范围！', icon: 'success' });
               }
               uni.setStorageSync('checkpointReached', '1');
            }
          } else {
            isReach.value = false;
          }
        }

        // Update progress
        if (currentMode.value === 'normal') {
           normalProgress.value = Math.min(100, ((distance.value/1000) / dailyTarget.value) * 100);
        } else if (currentMode.value === 'police') {
           policeProgress.value = Math.min(100, (distance.value / policeTargetDistance.value) * 100);
        }
    }
  }
};

// Real-time Location Tracking
const startRealLocationTracking = () => {
  // #ifdef H5
  if (h5LocationTimer) clearInterval(h5LocationTimer);
  let lastTs = Date.now();
  h5LocationTimer = setInterval(() => {
    getCurrentLocation({ type: 'gcj02' }).then(res => {
        const newLat = res.latitude;
        const newLng = res.longitude;
        
        let speedVal = 0;
        // Simple speed calc for H5
        if (isRunning.value && trajectoryPoints.value.length > 0) {
           const lastPoint = trajectoryPoints.value[trajectoryPoints.value.length - 1];
           const d = getDistance(lastPoint.latitude, lastPoint.longitude, newLat, newLng);
           const dt = (Date.now() - lastTs) / 1000;
           if (dt > 0) speedVal = d / dt;
        }
        currentSpeed.value = speedVal;
        
        updateLocationLogic(newLat, newLng, speedVal);
        lastTs = Date.now();
    }).catch(err => {
        console.warn('H5 Polling failed', err);
    });
  }, 1000);
  // #endif
  // #ifndef H5
  uni.startLocationUpdate({
    success: () => {
      locationCallback = (res) => {
        if (res.speed && res.speed >= 0) {
          currentSpeed.value = res.speed;
        }
        updateLocationLogic(res.latitude, res.longitude, currentSpeed.value);
      };
      uni.onLocationChange(locationCallback);
    },
    fail: (err) => {
      console.log('startLocationUpdate failed:', err);
      // Fallback: Use polling if real-time tracking fails
      uni.showToast({ title: '定位服务兼容模式已启动', icon: 'none' });
      
      if (h5LocationTimer) clearInterval(h5LocationTimer);
      
      // Default to gcj02 first to match map view, then fallback to wgs84
      let preferredType = 'gcj02'; 
      
      const doPoll = () => {
          getCurrentLocation({ type: preferredType }).then(res => {
              updateLocationLogic(res.latitude, res.longitude, res.speed || 0);
          }).catch(err => {
              console.error(`Polling fallback failed for ${preferredType}`, err);
              // If gcj02 failed, try wgs84 immediately
              if (preferredType === 'gcj02') {
                  preferredType = 'wgs84';
                  doPoll(); // Retry immediately
              }
          });
      };
      
      h5LocationTimer = setInterval(doPoll, 2000); // Poll every 2 seconds
      doPoll(); // Run immediately
    }
  });
  // #endif
};

const stopRealLocationTracking = () => {
  // #ifdef H5
  if (h5LocationTimer) {
    clearInterval(h5LocationTimer);
    h5LocationTimer = null;
  }
  // #endif
  // #ifndef H5
  uni.stopLocationUpdate();
  if (locationCallback) {
    uni.offLocationChange(locationCallback);
    locationCallback = null;
  }
  // #endif
};

// 2. 跑步核心配置
const currentMode = ref('normal'); // normal-普通 police-警务 campus-校园
const isRunning = ref(false);
const duration = ref(0);
const distance = ref(0); // 已跑距离（米）
const distanceToCheckpoint = ref(0);
const isReach = ref(false);
const stepCount = ref(0);
const heartRate = ref(80);
const currentSpeed = ref(0); // 实时速度 m/s
const maxSpeed = ref(0); // 最大速度 m/s
let timer = null;
let accelerometerCallback = null;
let locationCallback = null;
let h5LocationTimer = null;
let isPageActive = true; // Flag to track page visibility for safe rendering

// 3. 警务专项固定配置（按公安考核标准）
const policeTargetDistance = ref(2000); // 固定2000米
const policeTargetPace = ref(6.5); // 达标配速：6.5分钟/公里（男生标准）
const taskId = ref(null);
const taskType = ref(null);

// 计算当前配速（分钟/公里）
const currentPace = computed(() => {
  const km = distance.value / 1000;
  const min = duration.value / 60;
  if (km === 0) return 0;
  const p = min / km;
  return p > 999 ? 999 : p;
});
// 实时速度展示 (km/h)
const currentSpeedKmh = computed(() => (currentSpeed.value * 3.6).toFixed(1));
// 平均速度 (km/h)
const avgSpeedKmh = computed(() => {
  if (duration.value === 0) return 0;
  return ((distance.value / 1000) / (duration.value / 3600)).toFixed(1);
});

// 接收页面参数
onLoad((options) => {
  if (options.mode) {
    currentMode.value = options.mode;
  }
  if (options.target) {
    policeTargetDistance.value = parseInt(options.target);
  }
  if (options.pace) {
    policeTargetPace.value = parseFloat(options.pace);
  }
  if (options.taskId) {
    taskId.value = options.taskId;
    // Set task type if provided, or infer from mode
    if (options.taskType) {
      taskType.value = options.taskType;
    }
  }
  if (options.taskTitle) {
    teacherRunTask.value = decodeURIComponent(options.taskTitle);
  }
  if (options.course) {
    uni.showToast({ title: `开始课程：${options.course}`, icon: 'none' });
  }
});

// Listener for custom location selection
uni.$on('onLocationChosen', (res) => {
  processSelectedLocation(res);
});

onUnmounted(() => {
  uni.$off('onLocationChosen');
  stopLocationPolling();
  if (timer) clearInterval(timer);
});

// 4. 定位优化（含权限申请+校园围栏）
const startLocationService = () => {
  getLocation(); // First try
  
  // Android Polling Optimization
  // #ifdef APP-PLUS
  if (uni.getSystemInfoSync().platform === 'android') {
      if (locationRetryTimer) clearInterval(locationRetryTimer);
      console.log('Starting Android location polling...');
      locationRetryTimer = setInterval(() => {
          if (!isPageActive) return; // Skip if page is not active
          if (locationState.value !== 'success') {
              console.log('Retry locating (Android)...');
              doGetLocation();
          } else {
              console.log('Location success, stop polling.');
              clearInterval(locationRetryTimer);
              locationRetryTimer = null;
          }
      }, 3000);
  }
  // #endif
};

const stopLocationPolling = () => {
  if (locationRetryTimer) {
    clearInterval(locationRetryTimer);
    locationRetryTimer = null;
  }
};

onHide(() => {
    isPageActive = false;
    stopLocationPolling();
  });

onUnmounted(() => {
  stopLocationPolling();
  if (timer) clearInterval(timer);
  stopStepCount();
});

const getLocation = () => {
  // #ifdef MP-WEIXIN
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

  // #ifndef MP-WEIXIN
  // App端和H5端直接调用getLocation，系统会自动处理权限请求
  doGetLocation();
  // #endif
};

const handleLocationSuccess = (res) => {
  lat.value = res.latitude;
  lng.value = res.longitude;
  
  // Cache location for faster load next time
  uni.setStorageSync('lastLocation', { lat: res.latitude, lng: res.longitude });

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
};

const handleLocationError = (err) => {
  console.error('Location failed:', err);
  let msg = '定位失败';
  let showSettings = false;

  // Analyze error message
  const errMsg = err.errMsg || '';
  if (errMsg.includes('auth') || errMsg.includes('denied') || errMsg.includes('permission')) {
    msg = '定位权限被拒绝，请去设置开启';
    showSettings = true;
  } else if (errMsg.includes('service') || errMsg.includes('unavailable')) {
    msg = '定位服务不可用，请检查GPS';
  }

  // #ifdef H5
  if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
    msg = 'H5定位需HTTPS';
  }
  // #endif

  if (showSettings) {
     uni.showModal({
       title: '权限提示',
       content: msg,
       confirmText: '去设置',
       success: (res) => {
         if (res.confirm) uni.openSetting();
       }
     });
  } else {
     uni.showToast({ title: msg, icon: 'none', duration: 3000 });
  }
  
  // 更新状态为失败
  locationState.value = 'fail';
};

const doGetLocation = async () => {
  // 1. 优先使用缓存 (提升首屏速度)
  const lastLoc = uni.getStorageSync('lastLocation');
  if (lastLoc) {
    lat.value = lastLoc.lat;
    lng.value = lastLoc.lng;
    markers.value = [{
      id: 0,
      latitude: lastLoc.lat,
      longitude: lastLoc.lng,
      title: '我的位置',
      iconPath: '/static/location.png',
      width: 30,
      height: 30
    }];
    // 有缓存不算完全成功，仍需获取最新定位，但状态暂不置为 fail
  } else {
    uni.showLoading({ title: '定位中...' });
  }

  locationState.value = 'locating';

  // 2. 调用封装的定位方法
  try {
    const res = await getCurrentLocation();
    if (!isPageActive) return; // Prevent updating state if page inactive

    uni.hideLoading();
    if (res.success) {
      handleLocationSuccess(res);
      uni.showToast({ title: '定位成功', icon: 'none' });
      locationState.value = 'success';
    }
  } catch (err) {
    if (!isPageActive) return; // Prevent updating state if page inactive

    uni.hideLoading();
    // 如果没有缓存，且定位失败，则显示错误
    if (!lastLoc) {
       handleLocationError(err);
    } else {
       // 有缓存但最新定位失败，提示一下
       uni.showToast({ title: '刷新定位失败，使用历史位置', icon: 'none' });
       // 这种情况暂时认为是 fail，因为需要最新位置才能打卡
       locationState.value = 'fail';
    }
  }
};

const handleRelocate = () => {
    uni.showLoading({ title: '重新定位...' });
    locationState.value = 'locating';
    // 强制清除 loading
    setTimeout(() => uni.hideLoading(), 5000);
    
    getCurrentLocation().then(res => {
        if (!isPageActive) return;
        uni.hideLoading();
        handleLocationSuccess(res);
        uni.showToast({ title: '已更新位置', icon: 'none' });
        locationState.value = 'success';
    }).catch(err => {
        if (!isPageActive) return;
        uni.hideLoading();
        handleLocationError(err);
    });
};

const locationStatusText = computed(() => {
  switch(locationState.value) {
    case 'locating': return '正在定位...';
    case 'success': return '定位成功';
    case 'fail': return '定位失败，请移至室外开阔地';
    default: return '等待定位';
  }
});

// 5. 搜索打卡点（仅校园模式）
const searchCheckpoint = () => {
  // If input is empty, show list of all available checkpoints
  if (!checkpointName.value) {
    if (availableCheckpoints.value.length === 0) {
      uni.showToast({ title: '未加载到打卡点数据', icon: 'none' });
      // Retry loading
      getCheckpoints().then(data => {
         availableCheckpoints.value = data;
         uni.showToast({ title: '数据已重新加载，请重试', icon: 'none' });
      });
      return;
    }

    const itemList = availableCheckpoints.value.map(cp => cp.name);
    uni.showActionSheet({
      itemList: itemList,
      success: (res) => {
        const target = availableCheckpoints.value[res.tapIndex];
        selectCheckpoint(target);
      },
      fail: (res) => {
        console.log(res.errMsg);
      }
    });
    return;
  }
  
  // Fuzzy search in available checkpoints
  const target = availableCheckpoints.value.find(cp => cp.name.includes(checkpointName.value));
  
  if (!target) {
     uni.showToast({ title: '未找到该打卡点', icon: 'none' });
     return;
  }

  selectCheckpoint(target);
};

const selectCheckpoint = (target) => {
  const newCheckpoint = {
    name: target.name,
    lat: target.latitude,
    lng: target.longitude,
    radius: target.radius,
    id: target.id
  };
  uni.setStorageSync('checkpoint', newCheckpoint);
  checkpoint.value = newCheckpoint;
  addCheckpointMarker(newCheckpoint.lat, newCheckpoint.lng, newCheckpoint.name);
  
  // Update Navigation Line (Red Dotted)
  navPolyline.value = {
    points: [
      { latitude: lat.value, longitude: lng.value },
      { latitude: newCheckpoint.lat, longitude: newCheckpoint.lng }
    ],
    color: '#FF0000',
    width: 2,
    dottedLine: true
  };

  // Force Map Update
  updateMapPolyline();

  uni.showToast({ title: `已锁定：${newCheckpoint.name}`, icon: 'success' });
};

const processSelectedLocation = (res) => {
      console.log('Selected location:', res);
      const selLat = res.latitude;
      const selLng = res.longitude;
      
      // Find nearest checkpoint
      let nearest = null;
      let minDist = Infinity;
      
      availableCheckpoints.value.forEach(cp => {
        const d = getDistance(selLat, selLng, cp.latitude, cp.longitude);
        if (d < minDist) {
          minDist = d;
          nearest = cp;
        }
      });
      
      // Tolerance 200m
      if (nearest && minDist <= 200) {
        checkpointName.value = nearest.name;
        
        const newCheckpoint = {
          name: nearest.name,
          lat: nearest.latitude,
          lng: nearest.longitude,
          radius: nearest.radius,
          id: nearest.id // Ensure ID is passed
        };
        uni.setStorageSync('checkpoint', newCheckpoint);
        checkpoint.value = newCheckpoint;
        addCheckpointMarker(newCheckpoint.lat, newCheckpoint.lng, newCheckpoint.name);
        
        navPolyline.value = {
          points: [
            { latitude: lat.value, longitude: lng.value },
            { latitude: newCheckpoint.lat, longitude: newCheckpoint.lng }
          ],
          color: '#FF0000',
          width: 2,
          dottedLine: true
        };
        updateMapPolyline();
        
        uni.showToast({ title: `已定位到：${nearest.name}`, icon: 'success' });
      } else {
        uni.showModal({
          title: '提示',
          content: '您选择的地点不在校园打卡点范围内，是否仍要设为目标？(无法进行有效打卡)',
          success: (mRes) => {
            if (mRes.confirm) {
               checkpointName.value = res.name || '自定义位置';
               const customCheckpoint = {
                 name: res.name || '自定义位置',
                 lat: selLat,
                 lng: selLng,
                 radius: 50,
                 id: null 
               };
               uni.setStorageSync('checkpoint', customCheckpoint);
               checkpoint.value = customCheckpoint;
               addCheckpointMarker(selLat, selLng, customCheckpoint.name);
               
               navPolyline.value = {
                points: [
                  { latitude: lat.value, longitude: lng.value },
                  { latitude: selLat, longitude: selLng }
                ],
                color: '#FF0000',
                width: 2,
                dottedLine: true
               };
               updateMapPolyline();
            }
          }
        });
      }
};

// 5.5 Map Selection Handler
const handleMapSelect = () => {
  // #ifdef H5
  uni.chooseLocation({
    success: (res) => {
      processSelectedLocation(res);
    },
    fail: (err) => {
      console.error('Choose location failed', err);
    }
  });
  // #endif

  // #ifndef H5
  uni.navigateTo({
    url: '/pages/common/choose-location/choose-location'
  });
  // #endif
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
// 计步逻辑：简单的波峰波谷或者阈值判定+防抖
    let isStepActive = false;
    let lastStepTime = 0;
    const STEP_THRESHOLD_UP = 1.25; // 上升阈值 (g) - 调高以减少误触
    const STEP_THRESHOLD_DOWN = 1.05; // 下降/重置阈值 (g) - 确保能复位
    const MIN_STEP_INTERVAL = 300; // 最小间隔 ms
    const RESET_TIMEOUT = 1500; // 强制复位超时 (ms)

    const startStepCount = () => {
      // 先停止之前的监听，防止重复
      uni.stopAccelerometer();
      
      uni.startAccelerometer({
        interval: 'game', // 使用 game (20ms) 频率，采样更密集，捕捉波峰更准
        success: () => {
          console.log('Accelerometer started');
          isStepActive = false;
          lastStepTime = Date.now();
        },
        fail: (err) => {
          console.error('Start Accelerometer failed:', err);
        }
      });
      
      accelerometerCallback = (res) => {
        let acceleration = Math.sqrt(res.x*res.x + res.y*res.y + res.z*res.z);
        
        // 归一化处理：如果加速度 > 5，说明单位是 m/s^2，转换为 g (除以 9.8)
        if (acceleration > 5) {
          acceleration = acceleration / 9.8;
        }

        const now = Date.now();
        
        // 强制复位检查：如果处于激活状态太久（超过1.5秒），说明卡住了，强制复位
        if (isStepActive && (now - lastStepTime > RESET_TIMEOUT)) {
            isStepActive = false;
        }

        if (!isStepActive && acceleration > STEP_THRESHOLD_UP) {
           if (now - lastStepTime > MIN_STEP_INTERVAL) {
             stepCount.value += 1;
             lastStepTime = now;
             isStepActive = true; 
           }
        } else if (isStepActive && acceleration < STEP_THRESHOLD_DOWN) {
           isStepActive = false;
        }
      };
      uni.onAccelerometerChange(accelerometerCallback);
    };
const stopStepCount = () => {
  if (accelerometerCallback) {
    uni.stopAccelerometer(); // 停止监听
    uni.offAccelerometerChange(accelerometerCallback);
    accelerometerCallback = null;
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
// Common start logic
const initializeRunState = () => {
  if (locationState.value !== 'success') {
    uni.showToast({ title: '定位未成功，无法开始', icon: 'none' });
    doGetLocation(); // Try to refresh
    return false;
  }

  isRunning.value = true;
  duration.value = 0;
  distance.value = 0;
  stepCount.value = 0;
  heartRate.value = 80;
  
  // Clear previous trajectory
  runPolyline.value.points = [];
  trajectoryPoints.value = [];
  
  // Add start point immediately to avoid delay in drawing line
  if (lat.value && lng.value) {
     const startPoint = { latitude: lat.value, longitude: lng.value, timestamp: Date.now(), speed: 0 };
     trajectoryPoints.value.push(startPoint);
     runPolyline.value.points.push({ latitude: lat.value, longitude: lng.value });
     
     // Force Map Update
     updateMapPolyline();
  }
  return true;
};

// 普通跑步（无固定目标）
const startNormalRun = () => {
  // Clear navigation line in normal mode to ensure clean map
  navPolyline.value = null;
  if (!initializeRunState()) return;

  uni.removeStorageSync('checkpointReached');
  startRealLocationTracking();
  startStepCount();
  timer = setInterval(() => {
    duration.value += 1;
    updateHeartRate();
  }, 1000);
};

// 专项训练（固定2000米，按达标配速跑）
const startPoliceRun = () => {
  if (!initializeRunState()) return;

  uni.removeStorageSync('policeFinishTip');
  startRealLocationTracking();
  startStepCount();
  timer = setInterval(() => {
    duration.value += 1;
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
  if (!initializeRunState()) return;

  isReach.value = false;
  uni.removeStorageSync('checkpointReached');
  startRealLocationTracking();
  startStepCount();
  timer = setInterval(() => {
    duration.value += 1;
    updateHeartRate();
  }, 1000);
};

// 11. 结束跑步（统一逻辑）
const stopRun = async () => {
  if (!isRunning.value) return;
  isRunning.value = false;
  clearInterval(timer);
  stopStepCount();
  stopRealLocationTracking();

  const token = uni.getStorageSync('token');
  if (!token) {
    uni.showToast({ title: '请先登录', icon: 'none' });
    setTimeout(() => {
      uni.reLaunch({ url: '/pages/login/login' });
    }, 800);
    return;
  }

  const runData = {
    type: taskType.value ? taskType.value : (currentMode.value === 'police' ? 'test' : 'run'),
    source: taskId.value ? 'task' : 'free',
    started_at: new Date(Date.now() - duration.value * 1000).toISOString(),
    ended_at: new Date().toISOString(),
    metrics: {
      distance: distance.value / 1000, // Convert meters to km
      duration: duration.value,
      pace: currentPace.value.toFixed(1),
      count: currentMode.value === 'police' ? 1 : null,
      qualified: currentMode.value === 'police' ? currentPace.value <= policeTargetPace.value : false,
      trajectory: JSON.stringify(trajectoryPoints.value),
      checkpoints: JSON.stringify(checkinRecords.value)
    },
    evidence: []
  };

  try {
    uni.showLoading({ title: '提交中...' });
    const res = await submitActivity(runData);
    uni.hideLoading();
    console.log('Submit success:', res);
    
    // Jump to result page with data
    // Use storage to pass data to avoid URL length limit
    uni.setStorageSync('tempRunResult', runData);
    
    // 使用 reLaunch 确保清理页面栈，或者 redirectTo
    uni.redirectTo({
      url: '/pages/result/result?useStorage=true',
      fail: (err) => {
        console.error('Navigate failed:', err);
        uni.showToast({ title: '页面跳转失败', icon: 'none' });
      }
    });
  } catch (error) {
    uni.hideLoading();
    console.error('Submit failed:', error);
    uni.showModal({
      title: '提交失败',
      content: (error && error.detail) ? error.detail : '网络或服务器错误，请重试',
      confirmText: '重试',
      cancelText: '强制结束',
      success: (modalRes) => {
         if (modalRes.confirm) {
            // User wants to retry - do nothing, they can click stop again
         } else if (modalRes.cancel) {
            // Force stop - jump to home or result without saving?
            // Let's jump to result but maybe with local data only?
            // Or just back to home
            uni.showToast({ title: '已强制结束', icon: 'none' });
            setTimeout(() => {
               uni.reLaunch({ url: '/pages/home/home' });
            }, 800);
         }
      }
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

.location-status-bar {
  position: absolute;
  top: 20rpx;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(0,0,0,0.6);
  padding: 10rpx 24rpx;
  border-radius: 30rpx;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}
.status-text {
  color: #ffffff;
  font-size: 24rpx;
}

.custom-navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: #20C997;
  z-index: 999;
}

.navbar-content {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.navbar-title {
  color: #ffffff;
  font-size: 16px;
  font-weight: bold;
}

.content-spacer {
  width: 100%;
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
.map-select-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  border-radius: 8rpx;
  padding: 0 20rpx;
  margin-right: 10rpx;
}
.map-icon {
  font-size: 32rpx;
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

/* Map Controls */
.map {
  position: relative;
}
.map-controls {
  position: absolute;
  bottom: 20rpx;
  right: 20rpx;
  z-index: 999;
}
.control-btn {
  width: 80rpx;
  height: 80rpx;
  background-color: #ffffff;
  border-radius: 50%;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.2);
  display: flex;
  justify-content: center;
  align-items: center;
}
.control-icon {
  width: 40rpx;
  height: 40rpx;
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
