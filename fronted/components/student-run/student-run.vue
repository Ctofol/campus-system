<template>
  <view class="run">
    <!-- Custom Navigation Bar -->
    <view class="custom-navbar" :style="{paddingTop: statusBarHeight + 'px'}">
      <view class="navbar-content">
        <view class="navbar-left" @click="goBack">
          <text class="back-icon">←</text>
        </view>
        <text class="navbar-title">跑步</text>
        <view class="navbar-right"></view>
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
      v-if="isMapReady"
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
       <cover-view class="location-status-bar" :style="{ display: locationState === 'success' ? 'none' : 'flex' }">
         {{ locationStatusText }}
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

    <!-- 3. 核心跑步模式切换（任务跑锁定为「专项测试」中间页） -->
    <view class="mode-switch" v-if="!taskRunLocked">
      <text class="mode-item" :class="{active: currentMode === 'normal'}" @click="switchMode('normal')">普通跑步</text>
      <text class="mode-item" :class="{active: currentMode === 'police'}" @click="switchMode('police')">专项测试</text>
      <text class="mode-item" :class="{active: currentMode === 'campus'}" @click="switchMode('campus')">校园打卡</text>
    </view>
    <view v-else class="task-mode-hint">
      <text class="task-mode-hint-text">📋 任务跑步（专项跑）· 已锁定模式</text>
    </view>

    <!-- 4. 专项测试计划 / 任务要求 -->
    <view v-if="currentMode === 'police'" class="police-plan">
      <text class="plan-title">{{ taskRunLocked ? '📋 本次任务要求' : '🎯 专项体能训练' }}</text>
      <view class="plan-info">
        <text class="info-item">目标距离：<span class="highlight">{{policeTargetDistance/1000}}公里</span></text>
        <text class="info-item" v-if="taskMinDurationSec > 0">最低时长：<span class="highlight">{{Math.floor(taskMinDurationSec/60)}}分{{taskMinDurationSec%60}}秒</span></text>
        <text class="info-item">参考配速：<span class="highlight">{{policeTargetPace}}分钟/公里</span>（展示用，达标以任务距离/时长为准）</text>
        <text class="info-item task-desc" v-if="taskRunLocked && taskDescription">{{ taskDescription }}</text>
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
          <view class="progress-bar">
            <view class="progress-fill" :style="{width: normalProgress + '%'}"></view>
          </view>
          <text class="progress-text">已跑 {{((distance || 0)/1000).toFixed(2)}} km</text>
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
        <text class="data">剩余：{{(Math.max(0, policeTargetDistance - distance)/1000).toFixed(2)}}km | 配速：{{currentPace.toFixed(1)}}分钟/公里</text>
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
          <text class="checkpoint-info">打卡点：{{checkpoint.name}}（到达约 {{ checkpoint.radius || 100 }} 米内可判定为已到达）</text>
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
    
  </view>
</template>

<script setup>
// 统一导入规范
import { ref, computed, onUnmounted, onMounted, nextTick } from 'vue';
import AiChatRobot from '@/components/ai-chat-robot/ai-chat-robot.vue';
import { submitActivity, getCheckpoints, checkIn, uploadFile, getStudentTaskDetail } from '@/utils/request.js';
import { getCurrentLocation } from '@/utils/location.js';

// Navbar Settings
const statusBarHeight = ref(20);

const isMapReady = ref(false);

// 返回按钮
const goBack = () => {
  uni.navigateBack({
    delta: 1
  });
};

// 组件挂载时获取状态栏高度
onMounted(() => {
  const sys = uni.getSystemInfoSync();
  statusBarHeight.value = sys.statusBarHeight || 20;
  
  // 延迟加载地图，防止容器未就绪导致的渲染错误
  setTimeout(() => {
    isMapReady.value = true;
  }, 500);
  
  // 初始化交给父页 onShow 调用 onPageShow（带 options）；此处不再调用，避免与父页 50ms 后的调用形成「先空后实」被防抖误吞
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

// 页面显示逻辑 (替代 onShow)
let isPageActive = false;
let lastShowTime = 0;

/** 父页 onLoad 传入的启动参数（有 taskId 等时不可被「空 onShow」防抖掉） */
const hasMeaningfulRunPageOptions = (opt) => {
  if (!opt || typeof opt !== 'object') return false;
  return !!(
    opt.mode ||
    opt.taskId ||
    opt.task_id ||
    opt.target != null ||
    opt.pace != null ||
    opt.taskTitle ||
    opt.course
  );
};

const onPageShow = (options = {}) => {
    const now = Date.now();
    const forceTask = options && (options.taskId || options.task_id);
    // 仅跳过「短时间内重复且无路由参数」的抖动；带 taskId/mode 的第二次调用必须执行（否则任务跑、路由参数丢失）
    if (!forceTask && now - lastShowTime < 500 && !hasMeaningfulRunPageOptions(options)) {
        return;
    }
    lastShowTime = now;

    isPageActive = true;
    
    // 更新状态栏高度
    const sys = uni.getSystemInfoSync();
    statusBarHeight.value = sys.statusBarHeight || 20;

    // 强制设置导航栏标题和颜色 (虽然是组件，但如果需要动态修改父容器导航栏，也可以保留)
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
      // 注意：这里可能需要父组件配合跳转，或者直接使用 uni.switchTab
      setTimeout(() => {
        // 假设 teacher home 也是 tab 页
        uni.switchTab({ url: '/pages/tab/home' }); // Correct path to home tab
      }, 800);
      return;
    }

    // 根据性别自动设置普通跑步目标里程
    const userInfo = uni.getStorageSync('userInfo');
    if (userInfo) {
      try {
        const userObj = typeof userInfo === 'string' ? JSON.parse(userInfo) : userInfo;
        const gender = userObj.gender;
        if (gender === 'male' || gender === '男') {
          dailyTarget.value = 3;
        } else {
          dailyTarget.value = 2;
        }
      } catch (e) {
        dailyTarget.value = 2;
      }
    }

    // 处理参数 (合并 onLoad 逻辑)
    if (options.mode) {
      currentMode.value = options.mode;
    }
    if (options.target) {
      policeTargetDistance.value = parseInt(options.target);
    }
    if (options.pace) {
      policeTargetPace.value = parseFloat(options.pace);
    }
    if (options.taskId || options.task_id) {
      taskId.value = String(options.taskId || options.task_id);
      if (options.taskType || options.task_type) {
        taskType.value = options.taskType || options.task_type;
      }
      taskRunLocked.value = true;
      currentMode.value = 'police';
      loadTaskRequirements(taskId.value);
    } else {
      taskRunLocked.value = false;
      taskId.value = null;
      taskType.value = null;
      taskDescription.value = '';
      taskMinDurationSec.value = 0;
    }
    if (options.taskTitle) {
      teacherRunTask.value = decodeURIComponent(options.taskTitle);
    }
    if (options.course) {
      uni.showToast({ title: `开始课程：${options.course}`, icon: 'none' });
    }

    const targetMode = uni.getStorageSync('runMode');
    if (targetMode && !taskRunLocked.value && !isRunning.value) {
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
    const records = getStoredRunRecordsList();
    const today = new Date();
    const dayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime();
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
};

const taskRunLocked = ref(false);
const taskDescription = ref('');
const taskMinDurationSec = ref(0);

const loadTaskRequirements = async (tid) => {
  if (!tid) return;
  try {
    const d = await getStudentTaskDetail(tid);
    teacherRunTask.value = d.title || teacherRunTask.value;
    taskType.value = d.type || 'run';
    taskDescription.value = d.description || '';
    taskMinDurationSec.value = Number(d.min_duration) || 0;
    const km = Number(d.min_distance);
    if (km > 0) {
      policeTargetDistance.value = Math.round(km * 1000);
    } else {
      policeTargetDistance.value = 2000;
    }
    if (d.min_duration && km > 0) {
      policeTargetPace.value = Number(d.min_duration) / 60 / km;
    }
    if (d.can_submit === false && d.submit_hint) {
      uni.showToast({ title: d.submit_hint, icon: 'none', duration: 2500 });
    }
  } catch (e) {
    console.error(e);
    uni.showToast({ title: '加载任务要求失败', icon: 'none' });
  }
};

// 暴露给父组件 (Merged below)
// defineExpose({
//   onPageShow
// });

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
const dailyTarget = ref(2);
const normalProgress = ref(0);
const policeProgress = ref(0);
const historyList = ref([]);

// 新增数据
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
/** 最近一次「可开跑」的定位是否来自缓存兜底（真 GPS 未成功），便于提示用户刷新以免里程长期为 0 */
const lastLocationFixWasStale = ref(false);
let locationRetryTimer = null;
/** 微信小程序：定位兜底 setTimeout，须在停止跑步与卸载时清除 */
let wxLocationWatchdogTimer = null;
/** 微信小程序：是否已成功开启后台持续定位（与 startLocationUpdateBackground 状态同步） */
let mpBackgroundLocationActive = false;
/** 微信真机 map 页 onLocationChange 常不回调：与持续定位并行 2s getLocation，驱动时长/里程 */
let wxRunAssistTimer = null;
const clearWxRunAssistTimer = () => {
  if (wxRunAssistTimer != null) {
    clearTimeout(wxRunAssistTimer);
    clearInterval(wxRunAssistTimer);
    wxRunAssistTimer = null;
  }
};

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
  // 微信小程序地层图层非常严苛，points必须要>=2个点才会生成路线，空数组反而会报错崩溃
  if (runPolyline.value.points && runPolyline.value.points.length >= 2) {
    // Using spread to update reference for better performance in long runs
    lines.push({ ...runPolyline.value, points: [...runPolyline.value.points] });
  }
  
  // 2. Add navigation line (Red) if exists
  if (navPolyline.value && navPolyline.value.points && navPolyline.value.points.length >= 2) {
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
const updateLocationLogic = (newLat, newLng, speed, accuracyOrRes) => {
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
    syncRunElapsedDisplay();
    // 不再按 horizontalAccuracy 整段丢弃回调：弱信号下常 >100m，丢弃后里程永远不涨；异常位移已由 d / calculatedSpeed 约束

    // 1. Initial point
    if (trajectoryPoints.value.length === 0) {
        const point = { latitude: newLat, longitude: newLng, timestamp: Date.now(), speed: speed || currentSpeed.value };
        trajectoryPoints.value.push(point);
        runPolyline.value.points.push({ latitude: newLat, longitude: newLng });
        updateMapPolyline();
        
        // 修复：第一个点也需要计算打卡点距离
        if (currentMode.value === 'campus' && checkpoint.value.lat) {
          distanceToCheckpoint.value = Math.floor(getDistance(newLat, newLng, checkpoint.value.lat, checkpoint.value.lng));
          if (distanceToCheckpoint.value <= (checkpoint.value.radius || 100)) { 
             isReach.value = true;
          }
        }
        return;
    }

    // 2. Subsequent points
    const lastPoint = trajectoryPoints.value[trajectoryPoints.value.length - 1];
    const d = getDistance(lastPoint.latitude, lastPoint.longitude, newLat, newLng);
    const timeDiff = (Date.now() - lastPoint.timestamp) / 1000; // seconds

    // 瞬时速度（m/s）：与是否计入总里程解耦，用于界面速度/配速；微信 onLocationChange 的 speed 常为 -1
    const spNum = typeof speed === 'number' && !Number.isNaN(speed) ? speed : -1;
    const calcSp = timeDiff > 0.001 ? d / timeDiff : 0;
    const runGpsSpeedWarmup = duration.value < 12 && distance.value < 25;
    if (!runGpsSpeedWarmup) {
      if (spNum >= 0 && spNum < 22) {
        currentSpeed.value = spNum;
      } else if (timeDiff >= 0.12 && calcSp > 0.06 && calcSp < 18) {
        currentSpeed.value = calcSp;
      }
    } else {
      currentSpeed.value = 0;
    }

    // Checkpoint logic - 修复：移出里程过滤逻辑，确保静止时也能刷新距离
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

    // 若时间间隔过短，多为重复回调，略放宽避免丢点
    if (timeDiff < 0.35) return;

    const calculatedSpeed = d / timeDiff;

    // 1. 略放宽最小位移，便于步行/弱 GPS 仍能累计
    // 2. 过滤异常「瞬移」
    if (d >= 0.35 && calculatedSpeed < 18) {
        distance.value += d;
        
        const point = { latitude: newLat, longitude: newLng, timestamp: Date.now(), speed: speed || calculatedSpeed };
        trajectoryPoints.value.push(point);
        
        // Update Blue Line Points
        runPolyline.value.points.push({ latitude: newLat, longitude: newLng });
        
        // Force Map Update
        updateMapPolyline();

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
        const runGpsSpeedWarmup = duration.value < 12 && distance.value < 25;
        currentSpeed.value = runGpsSpeedWarmup ? 0 : speedVal;

        updateLocationLogic(newLat, newLng, speedVal, res);
        lastTs = Date.now();
    }).catch(err => {
        console.warn('H5 Polling failed', err);
    });
  }, 1000);
  // #endif
  // #ifdef MP-WEIXIN
  // 息屏/切后台：须先 startLocationUpdate，再 startLocationUpdateBackground；manifest requiredBackgroundModes + 用户授权
  if (wxLocationWatchdogTimer) {
    clearTimeout(wxLocationWatchdogTimer);
    wxLocationWatchdogTimer = null;
  }
  mpBackgroundLocationActive = false;
  const registerLocationChange = () => {
    if (locationCallback) uni.offLocationChange(locationCallback);
    locationCallback = (res) => {
      const sp = res.speed;
      updateLocationLogic(res.latitude, res.longitude, sp, res);
    };
    uni.onLocationChange(locationCallback);
  };
  const startPollFallback = () => {
    clearWxRunAssistTimer();
    console.log('startLocationUpdate failed, use polling');
    try {
      uni.stopLocationUpdate();
    } catch (e) {}
    if (locationCallback) {
      try {
        uni.offLocationChange(locationCallback);
      } catch (e) {}
      locationCallback = null;
    }
    uni.showToast({ title: '定位服务兼容模式已启动', icon: 'none' });
    if (h5LocationTimer) {
      clearTimeout(h5LocationTimer);
      clearInterval(h5LocationTimer);
      h5LocationTimer = null;
    }
    let preferredType = 'gcj02';
    const pollTick = () => {
      if (!isRunning.value) return;
      syncRunElapsedDisplay();
      updateHeartRate();
      tickPoliceFinishHint();
      getCurrentLocation({ type: preferredType })
        .then((res) => {
          updateLocationLogic(res.latitude, res.longitude, res.speed || 0, res);
        })
        .catch((err) => {
          console.error(`Polling fallback failed for ${preferredType}`, err);
          if (preferredType === 'gcj02') {
            preferredType = 'wgs84';
          }
        })
        .finally(() => {
          if (!isRunning.value) return;
          h5LocationTimer = setTimeout(pollTick, 2000);
        });
    };
    h5LocationTimer = setTimeout(pollTick, 0);
  };
  /** 须在 startLocationUpdate 成功之后再调 startLocationUpdateBackground；禁止先卡「后台定位授权」再开前台，否则部分真机全程无 onLocationChange、里程/计时为 0 */
  const tryStartWxBackgroundAfterForeground = () => {
    try {
      uni.authorize({
        scope: 'scope.userLocationBackground',
        success: () => {
          uni.startLocationUpdateBackground({
            type: 'gcj02',
            success: () => {
              mpBackgroundLocationActive = true;
              uni.showToast({ title: '已开启后台定位，息屏可继续记录', icon: 'none', duration: 2000 });
            },
            fail: () => {
              mpBackgroundLocationActive = false;
              uni.showToast({ title: '后台定位未开启，前台仍会记录轨迹', icon: 'none', duration: 2200 });
            }
          });
        },
        fail: () => {
          mpBackgroundLocationActive = false;
          uni.showToast({ title: '未开后台定位时息屏可能暂停，可在设置中开启', icon: 'none', duration: 2600 });
        }
      });
    } catch (e) {
      mpBackgroundLocationActive = false;
      console.warn('tryStartWxBackgroundAfterForeground', e);
    }
  };
  uni.startLocationUpdate({
    success: () => {
      registerLocationChange();
      tryStartWxBackgroundAfterForeground();
    },
    fail: () => startPollFallback()
  });
  // 部分真机 startLocationUpdate 成功但长时间无 onLocationChange，用轮询兜底
  wxLocationWatchdogTimer = setTimeout(() => {
    wxLocationWatchdogTimer = null;
    if (!isRunning.value || h5LocationTimer) return;
    // 旧条件 trajectory<=2：GPS 抖动多点后永远不触发兜底，导致全程 0
    if (distance.value < 8) {
      console.log('WX: watchdog starting location poll fallback');
      startPollFallback();
    }
  }, 4000);
  // 与 onLocationChange 并行：map 页 setInterval 常被节流到停表，用 setTimeout 递归；每拍先同步墙钟时长，避免仅靠跑步时钟时界面一直 0
  clearWxRunAssistTimer();
  const wxAssistTick = () => {
    if (!isRunning.value) return;
    syncRunElapsedDisplay();
    updateHeartRate();
    tickPoliceFinishHint();
    getCurrentLocation({ type: 'gcj02' })
      .then((res) => {
        updateLocationLogic(res.latitude, res.longitude, res.speed || 0, res);
      })
      .catch(() => {})
      .finally(() => {
        if (!isRunning.value) return;
        // startPollFallback 已切到 h5LocationTimer 轮询时，勿再挂 wx 辅助定时器，避免双通道重复
        if (h5LocationTimer) return;
        wxRunAssistTimer = setTimeout(wxAssistTick, 2000);
      });
  };
  wxAssistTick();
  // #endif
  // #if !defined(H5) && !defined(MP-WEIXIN)
  uni.startLocationUpdate({
    success: () => {
      locationCallback = (res) => {
        updateLocationLogic(res.latitude, res.longitude, res.speed, res);
      };
      uni.onLocationChange(locationCallback);
    },
    fail: (err) => {
      console.log('startLocationUpdate failed:', err);
      uni.showToast({ title: '定位服务兼容模式已启动', icon: 'none' });
      if (h5LocationTimer) clearInterval(h5LocationTimer);
      let preferredType = 'gcj02';
      const doPoll = () => {
        getCurrentLocation({ type: preferredType }).then((res) => {
          updateLocationLogic(res.latitude, res.longitude, res.speed, res);
        }).catch((err2) => {
          console.error(`Polling fallback failed for ${preferredType}`, err2);
          if (preferredType === 'gcj02') {
            preferredType = 'wgs84';
            doPoll();
          }
        });
      };
      h5LocationTimer = setInterval(doPoll, 2000);
      doPoll();
    }
  });
  // #endif
};

const stopRealLocationTracking = () => {
  if (wxLocationWatchdogTimer) {
    clearTimeout(wxLocationWatchdogTimer);
    wxLocationWatchdogTimer = null;
  }
  clearWxRunAssistTimer();
  if (h5LocationTimer) {
    clearTimeout(h5LocationTimer);
    clearInterval(h5LocationTimer);
    h5LocationTimer = null;
  }
  // #ifndef H5
  // #ifdef MP-WEIXIN
  // 未关闭后台持续定位时，部分机型第二次 startLocationUpdate 异常、全程无点（时长/里程一直 0）
  if (mpBackgroundLocationActive) {
    try {
      uni.stopLocationUpdateBackground({ complete: () => {} });
    } catch (e) {
      console.warn('stopLocationUpdateBackground', e);
    }
    mpBackgroundLocationActive = false;
  }
  // #endif
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
/** 微信小程序 map 页常见 setInterval 被节流/停表，用墙钟 + 分段基准保证时长与心率可更新 */
const runActiveBaseSec = ref(0);
const runSegmentStartMs = ref(0);
const distance = ref(0); // 已跑距离（米）
const distanceToCheckpoint = ref('---');
const isReach = ref(false);
const stepCount = ref(0);
const heartRate = ref(80);
const currentSpeed = ref(0); // 实时速度 m/s
const maxSpeed = ref(0); // 最大速度 m/s
// 警务专项（tickPoliceFinishHint 依赖，须早于跑步时钟函数）
const policeTargetDistance = ref(2000); // 固定2000米
const policeTargetPace = ref(6.5); // 达标配速：6.5分钟/公里（男生标准）
let timer = null;

const syncRunElapsedDisplay = () => {
  if (!isRunning.value || !runSegmentStartMs.value) return;
  duration.value = runActiveBaseSec.value + Math.floor((Date.now() - runSegmentStartMs.value) / 1000);
};

const clearRunTickTimer = () => {
  if (timer != null) {
    clearTimeout(timer);
    clearInterval(timer);
    timer = null;
  }
};

const tickPoliceFinishHint = () => {
  if (currentMode.value !== 'police') return;
  if (distance.value >= policeTargetDistance.value && !uni.getStorageSync('policeFinishTip')) {
    uni.showToast({ title: `已完成 ${(policeTargetDistance.value / 1000).toFixed(2)} 公里目标！`, icon: 'success' });
    uni.setStorageSync('policeFinishTip', '1');
  }
};

/** 微信真机 map 场景下优先用 setTimeout 递归，避免 setInterval 完全不触发 */
const scheduleRunClock = () => {
  clearRunTickTimer();
  if (!isRunning.value) return;
  const loop = () => {
    if (!isRunning.value) {
      timer = null;
      return;
    }
    syncRunElapsedDisplay();
    updateHeartRate();
    tickPoliceFinishHint();
    timer = setTimeout(loop, 1000);
  };
  syncRunElapsedDisplay();
  updateHeartRate();
  tickPoliceFinishHint();
  timer = setTimeout(loop, 1000);
};

let accelerometerCallback = null;
let locationCallback = null;
let h5LocationTimer = null;
const startFaceUrl = ref(null);
const endFaceUrl = ref(null);

const taskId = ref(null);
const taskType = ref(null);

// 计算当前配速（分钟/公里）：里程尚短时用瞬时速度推算，避免一直显示 0
const currentPace = computed(() => {
  const km = distance.value / 1000;
  const min = duration.value / 60;
  const vMs = currentSpeed.value;
  const overall = km > 0.0005 ? min / km : 0;

  if (km >= 0.08 && overall > 0 && overall < 999) {
    return overall;
  }
  if (vMs > 0.12) {
    const vKmh = Math.max(vMs * 3.6, 0.05);
    const inst = 60 / vKmh;
    return inst > 999 ? 999 : inst;
  }
  if (overall > 0 && overall < 999) return overall;
  return 0;
});
// 实时速度 (km/h)：开跑后短时内不展示 GPS 推算值，避免刚启动就显示 2～3km/h 的抖动
const currentSpeedKmh = computed(() => {
  if (!isRunning.value) return '0.0';
  if (duration.value < 12 && distance.value < 20) {
    return '0.0';
  }
  const v = currentSpeed.value * 3.6;
  if (v < 0.2) return '0.0';
  return v.toFixed(1);
});
// 平均速度 (km/h)：短时内同样置 0，与瞬时速度展示策略一致
const avgSpeedKmh = computed(() => {
  if (!isRunning.value) return '0.0';
  if (duration.value < 10 || duration.value === 0) return '0.0';
  if (distance.value < 3) return '0.0';
  return ((distance.value / 1000) / (duration.value / 3600)).toFixed(1);
});

// Listener for custom location selection
uni.$on('onLocationChosen', (res) => {
  processSelectedLocation(res);
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

// onHide logic simulated for component
const onPageHide = () => {
    isPageActive = false;
    stopLocationPolling();
};
defineExpose({ onPageShow, onPageHide });

onUnmounted(() => {
  uni.$off('onLocationChosen');
  stopLocationPolling();
  clearRunTickTimer();
  stopStepCount();
  stopRealLocationTracking();
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
  lastLocationFixWasStale.value = false;
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

  // getCurrentLocation 失败时可能是包装对象，真实 errMsg 在 originalErr
  const raw = err?.originalErr || err;
  const errMsg = (raw && raw.errMsg) || err?.message || '';
  if (errMsg.includes('privacy') || errMsg.includes('隐私')) {
    msg = '需先同意小程序隐私保护指引。请返回首页同意，或重新进入本页后再试。';
  } else if (errMsg.includes('auth') || errMsg.includes('denied') || errMsg.includes('permission')) {
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

  // 2. 调用封装的定位方法（外层超时：极少数机型 uni.getLocation 长期不回调，避免永远「定位中」）
  const locateMs = 26000;
  try {
    const res = await Promise.race([
      getCurrentLocation(),
      new Promise((_, reject) => {
        setTimeout(() => {
          reject({
            success: false,
            type: 'timeout',
            message: '定位超时',
            originalErr: { errMsg: 'getLocation:fail outer timeout' }
          });
        }, locateMs);
      })
    ]);
    if (!isPageActive) {
      // 例：校园模式跳转选点页触发 onHide，若仍 return 且不更新状态，会永远卡在 locating
      if (res && res.success) {
        handleLocationSuccess(res);
        locationState.value = 'success';
      } else if (lastLoc) {
        lastLocationFixWasStale.value = true;
        locationState.value = 'success';
      } else {
        locationState.value = 'idle';
      }
      return;
    }
    if (res.success) {
      handleLocationSuccess(res);
      uni.showToast({ title: '定位成功', icon: 'none' });
      locationState.value = 'success';
    }
  } catch (err) {
    if (!isPageActive) {
      if (lastLoc) {
        lastLocationFixWasStale.value = true;
        locationState.value = 'success';
      } else {
        locationState.value = 'fail';
      }
      return;
    }
    if (!lastLoc) {
      handleLocationError(err?.originalErr || err);
    } else {
      lastLocationFixWasStale.value = true;
      uni.showToast({ title: '刷新定位失败，暂用历史位置，请到室外或点击定位按钮重试', icon: 'none', duration: 2800 });
      locationState.value = 'success';
    }
  } finally {
    uni.hideLoading();
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
        handleLocationError(err?.originalErr || err);
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
      
      if (availableCheckpoints.value && Array.isArray(availableCheckpoints.value)) {
        availableCheckpoints.value.forEach(cp => {
          const d = getDistance(selLat, selLng, cp.latitude, cp.longitude);
          if (d < minDist) {
            minDist = d;
            nearest = cp;
          }
        });
      }
      
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
  if (taskRunLocked.value) {
    uni.showToast({ title: '任务跑步请使用专项跑页面', icon: 'none' });
    return;
  }
  const wasRunning = isRunning.value;
  const hadStepListener = !!accelerometerCallback;
  const hadLocTracking = !!(locationCallback || h5LocationTimer || wxRunAssistTimer);
  // 切换模式时重置跑步状态；未开跑时不要反复 stop 加速度/持续定位（减少控制台噪音，也避免干扰模拟器）
  isRunning.value = false;
  clearRunTickTimer();
  runActiveBaseSec.value = 0;
  runSegmentStartMs.value = 0;
  if (wasRunning || hadStepListener) stopStepCount();
  if (wasRunning || hadLocTracking) stopRealLocationTracking();
  duration.value = 0;
  distance.value = 0;
  stepCount.value = 0;
  heartRate.value = 80;
  runPolyline.value.points = [];
  trajectoryPoints.value = [];
  updateMapPolyline();
  currentMode.value = mode;
};

// 8. 步数统计（加速度传感器）
// 计步逻辑：简单的波峰波谷或者阈值判定+防抖
    let isStepActive = false;
    let lastStepTime = 0;
    const STEP_THRESHOLD_UP = 1.12; // 合加速度峰值（约当量 g），原 1.25 过高导致归一化后峰值达不到、步数长期为 0
    const STEP_THRESHOLD_DOWN = 0.93;
    const MIN_STEP_INTERVAL = 300; // 最小间隔 ms
    const RESET_TIMEOUT = 1500; // 强制复位超时 (ms)

    // 启动步数统计 - 带重试机制
    const startStepCount = (retryCount = 0) => {
      const MAX_RETRIES = 3;
      console.log('=== 开始启动步数统计 (重试次数:', retryCount, ') ===');
      
      // 先确保停止之前的监听，使用回调确保完成后再启动
      const stopAndStart = () => {
        uni.stopAccelerometer({
          success: () => {
            console.log('✅ 传感器已停止');
            // 延迟200ms确保传感器完全释放
            setTimeout(() => {
              startAccelerometerWithRetry(retryCount);
            }, 200);
          },
          fail: (err) => {
            console.warn('停止传感器失败，继续尝试启动:', err);
            // 即使停止失败也尝试启动
            setTimeout(() => {
              startAccelerometerWithRetry(retryCount);
            }, 200);
          }
        });
      };
      
      stopAndStart();
    };
    
    // 带重试的启动传感器：仅在 start 成功后再注册监听，避免失败重试时重复 on 导致冲突；降采样提高部分机型/微信环境兼容性
    const startAccelerometerWithRetry = (retryCount) => {
      const MAX_RETRIES = 3;
      const intervals = ['ui', 'normal', 'game'];
      const interval = intervals[Math.min(retryCount, intervals.length - 1)];

      const bindAccelerometerListener = () => {
        if (accelerometerCallback) {
          try {
            uni.offAccelerometerChange(accelerometerCallback);
          } catch (e) {
            console.warn('offAccelerometerChange:', e);
          }
        }
        accelerometerCallback = (res) => {
          // 合加速度模长统一换算为「约当量 g」，避免原先「>5 才除 9.8」时静止模长≈9.8 被除后约 1.0、峰值难超 1.25 导致不计步
          const mag = Math.sqrt(res.x * res.x + res.y * res.y + res.z * res.z);
          let g = mag / 9.80665;
          if (!Number.isFinite(g) || g < 0.2) g = 1;

          const now = Date.now();

          if (isStepActive && now - lastStepTime > RESET_TIMEOUT) {
            isStepActive = false;
          }

          if (!isStepActive && g > STEP_THRESHOLD_UP) {
            if (now - lastStepTime > MIN_STEP_INTERVAL) {
              stepCount.value += 1;
              console.log('👣 步数+1，当前步数:', stepCount.value, 'g≈', g.toFixed(2));
              lastStepTime = now;
              isStepActive = true;
            }
          } else if (isStepActive && g < STEP_THRESHOLD_DOWN) {
            isStepActive = false;
          }
        };
        uni.onAccelerometerChange(accelerometerCallback);
        console.log('=== 步数统计监听已设置 (interval=' + interval + ') ===');
      };

      uni.startAccelerometer({
        interval,
        success: () => {
          console.log('✅ 加速度传感器启动成功');
          bindAccelerometerListener();
          uni.showToast({
            title: '步数统计已启动',
            icon: 'none',
            duration: 1500
          });
          isStepActive = false;
          lastStepTime = Date.now();
        },
        fail: (err) => {
          console.error('❌ 加速度传感器启动失败:', err);

          const errMsg = err && err.errMsg ? String(err.errMsg) : '';
          const retriable =
            retryCount < MAX_RETRIES &&
            (errMsg.includes('enable') ||
              errMsg.includes('busy') ||
              errMsg.includes('system') ||
              errMsg.includes('auth') ||
              errMsg.includes('permission') ||
              errMsg.includes('fail'));

          if (retriable) {
            console.log('🔄 传感器启动失败，准备重试:', errMsg);
            uni.showToast({
              title: '传感器启动中，请稍候…',
              icon: 'none',
              duration: 1000
            });
            setTimeout(() => {
              startStepCount(retryCount + 1);
            }, 800);
          } else {
            uni.showModal({
              title: '步数统计启动失败',
              content:
                '无法启动加速度传感器，步数将无法统计。请在系统设置与微信「小程序」权限中允许运动/传感器相关权限；若已开启，请结束小程序进程后重试。',
              showCancel: false
            });
          }
        }
      });
    };

const stopStepCount = () => {
  if (!accelerometerCallback) return;
  uni.stopAccelerometer();
  uni.offAccelerometerChange(accelerometerCallback);
  accelerometerCallback = null;
};

/**
 * 人脸拍照 / chooseMedia 刚结束时，部分微信真机需过一小段再调 startLocationUpdate，否则 onLocationChange 不回调（步数、墙钟、里程均不涨）。
 * 测试反馈「第一次拍照后开始跑步统计不工作；点结束跑步再取消后正常」即典型时序问题。
 */
const beginRunTrackingAfterFaceDefer = () => {
  const go = () => {
    if (!isRunning.value) return;
    startRealLocationTracking();
    startStepCount();
    scheduleRunClock();
  };
  nextTick(() => {
    setTimeout(go, 280);
  });
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
  runActiveBaseSec.value = 0;
  runSegmentStartMs.value = Date.now();
  distance.value = 0;
  stepCount.value = 0;
  heartRate.value = 80;
  currentSpeed.value = 0;
  endFaceUrl.value = null;
  
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

// 人脸验证：选图/拍照（相册/相机在微信公众平台「隐私保护指引」中声明用途；勿写入 app.json 的 requiredPrivateInfos，该字段仅允许定位类白名单）
const handleFacePickFail = (resolve, err) => {
  const errMsg = (err && err.errMsg) ? String(err.errMsg) : '';
  if (errMsg.includes('cancel')) {
    resolve(false);
    return;
  }
  if (errMsg.includes('privacy') || errMsg.includes('隐私')) {
    uni.showModal({
      title: '隐私授权未完成',
      content: '请先同意《用户隐私保护指引》（可返回首页弹出框点「同意并继续」），再重试拍照。',
      showCancel: false,
      confirmText: '知道了'
    });
    resolve(false);
    return;
  }
  if (errMsg.includes('auth') || errMsg.includes('deny') || errMsg.includes('denied')) {
    uni.showModal({
      title: '需要相机/相册权限',
      content: '无法打开相机或相册。请在手机系统设置与微信「小程序」权限中允许本小程序使用相机、相册后重试。',
      confirmText: '去设置',
      success: (r) => {
        if (r.confirm) uni.openSetting();
      }
    });
    resolve(false);
    return;
  }
  uni.showModal({
    title: '拍照或选图失败',
    content: errMsg
      ? `${errMsg}\n\n可稍后重试或改用相册选图。未完成人脸验证无法开始或结束跑步。`
      : '请检查相机与相册权限、存储空间是否正常，或稍后重试。未完成人脸验证无法开始或结束跑步。',
    showCancel: false,
    confirmText: '知道了'
  });
  resolve(false);
};

const faceVerify = (phase) => {
  return new Promise((resolve) => {
    uni.showModal({
      title: '人脸验证',
      content: phase === 'start'
        ? '请拍摄起跑照片，用于本次阳光跑验证。'
        : '请拍摄结束照片，用于本次阳光跑验证。',
      showCancel: true,
      success: (modalRes) => {
        if (!modalRes.confirm) {
          resolve(false);
          return;
        }

        const uploadChosen = async (filePath) => {
          if (!filePath) {
            uni.showModal({
              title: '未获取到照片',
              content: '未完成人脸验证，无法开始或结束本次跑步。请重新拍照。',
              showCancel: false,
              confirmText: '知道了'
            });
            resolve(false);
            return;
          }
          try {
            uni.showLoading({ title: '上传验证照片...' });
            const uploadRes = await uploadFile(filePath);
            uni.hideLoading();

            const url = uploadRes?.url || uploadRes?.path || uploadRes?.filePath || uploadRes;
            if (!url) {
              uni.showModal({
                title: '验证失败',
                content: '照片上传失败，请检查后端是否启动、网络是否正常，然后重试。',
                showCancel: false
              });
              resolve(false);
              return;
            }

            if (phase === 'start') startFaceUrl.value = url;
            else endFaceUrl.value = url;
            resolve(true);
          } catch (e) {
            uni.hideLoading();
            console.error('Face upload fail:', e);
            const msg = e?.message || e?.detail || '照片上传失败，请稍后重试';
            uni.showModal({
              title: '验证失败',
              content: msg,
              showCancel: false
            });
            resolve(false);
          }
        };

        // #ifdef MP-WEIXIN
        uni.chooseMedia({
          count: 1,
          mediaType: ['image'],
          sourceType: ['camera', 'album'],
          sizeType: ['compressed'],
          success: (res) => {
            const f = res.tempFiles && res.tempFiles[0];
            const path = f && f.tempFilePath ? f.tempFilePath : '';
            uploadChosen(path);
          },
          fail: (err) => {
            uni.chooseImage({
              count: 1,
              sizeType: ['compressed'],
              sourceType: ['camera', 'album'],
              success: (res2) => {
                const path = res2.tempFilePaths && res2.tempFilePaths[0] ? res2.tempFilePaths[0] : '';
                uploadChosen(path);
              },
              fail: (err2) => handleFacePickFail(resolve, err2 || err)
            });
          }
        });
        // #endif
        // #ifndef MP-WEIXIN
        uni.chooseImage({
          count: 1,
          sizeType: ['compressed'],
          sourceType: ['camera', 'album'],
          success: (res) => {
            const path = res.tempFilePaths && res.tempFilePaths[0] ? res.tempFilePaths[0] : '';
            uploadChosen(path);
          },
          fail: (err) => handleFacePickFail(resolve, err)
        });
        // #endif
      }
    });
  });
};

// 普通跑步（无固定目标）
const startNormalRun = async () => {
  if (locationState.value !== 'success') {
    uni.showToast({ title: '定位未成功，请稍候或点击地图旁定位按钮刷新后再试', icon: 'none' });
    doGetLocation();
    return;
  }
  if (lastLocationFixWasStale.value) {
    uni.showToast({
      title: '当前为历史定位，建议先点地图旁「定位」刷新或到室外再跑，以免里程统计偏晚',
      icon: 'none',
      duration: 3200
    });
  }
  const ok = await faceVerify('start');
  if (!ok) {
    return;
  }

  // Clear navigation line in normal mode to ensure clean map
  navPolyline.value = null;
  if (!initializeRunState()) {
    startFaceUrl.value = null;
    return;
  }

  uni.removeStorageSync('checkpointReached');
  beginRunTrackingAfterFaceDefer();
};

// 专项训练（固定2000米，按达标配速跑）
const startPoliceRun = async () => {
  if (locationState.value !== 'success') {
    uni.showToast({ title: '定位未成功，请稍候或点击地图旁定位按钮刷新后再试', icon: 'none' });
    doGetLocation();
    return;
  }
  if (lastLocationFixWasStale.value) {
    uni.showToast({
      title: '当前为历史定位，建议先点地图旁「定位」刷新或到室外再跑，以免里程统计偏晚',
      icon: 'none',
      duration: 3200
    });
  }
  const ok = await faceVerify('start');
  if (!ok) {
    return;
  }

  if (!initializeRunState()) {
    startFaceUrl.value = null;
    return;
  }

  uni.removeStorageSync('policeFinishTip');
  beginRunTrackingAfterFaceDefer();
};

// 校园打卡
const startCampusRun = async () => {
  if (locationState.value !== 'success') {
    uni.showToast({ title: '定位未成功，请稍候或点击地图旁定位按钮刷新后再试', icon: 'none' });
    doGetLocation();
    return;
  }
  if (lastLocationFixWasStale.value) {
    uni.showToast({
      title: '当前为历史定位，建议先点地图旁「定位」刷新或到室外再跑，以免里程统计偏晚',
      icon: 'none',
      duration: 3200
    });
  }
  const ok = await faceVerify('start');
  if (!ok) {
    return;
  }

  if (!initializeRunState()) {
    startFaceUrl.value = null;
    return;
  }

  isReach.value = false;
  uni.removeStorageSync('checkpointReached');
  beginRunTrackingAfterFaceDefer();
};

// 结束跑步时若用户取消人脸验证：恢复计时、计步与定位（避免已停表却无法继续跑）
const resumeRunAfterEndFaceCancelled = () => {
  runActiveBaseSec.value = duration.value;
  runSegmentStartMs.value = Date.now();
  isRunning.value = true;
  clearRunTickTimer();
  beginRunTrackingAfterFaceDefer();
};

// 提交跑步记录并跳转结算页
const redirectToRunResult = () => {
  uni.redirectTo({
    url: '/pages/result/result?useStorage=true',
    fail: (err) => {
      console.error('Navigate failed:', err);
      uni.showToast({ title: '页面跳转失败', icon: 'none' });
    }
  });
};

/** 读取本地跑步条（兼容字符串存储） */
const getStoredRunRecordsList = () => {
  let raw = uni.getStorageSync('runRecordsList');
  if (raw == null || raw === '') return [];
  if (typeof raw === 'string') {
    try {
      raw = JSON.parse(raw);
    } catch {
      return [];
    }
  }
  return Array.isArray(raw) ? raw : [];
};

/** 今日概览 / 历史条依赖本地 runRecordsList；此前从未写入导致一直为 0 */
const appendLocalRunRecord = (runData) => {
  try {
    const distanceKm = Number(runData?.metrics?.distance) || 0;
    const endedAt = runData?.ended_at || new Date().toISOString();
    const list = [...getStoredRunRecordsList()];
    list.unshift({
      createTime: endedAt,
      distance: distanceKm,
      type: 'run',
      source: runData?.source || 'free',
      duration: runData?.metrics?.duration || 0
    });
    uni.setStorageSync('runRecordsList', list.slice(0, 200));
  } catch (e) {
    console.warn('appendLocalRunRecord failed', e);
  }
};

const submitCurrentRunToServer = async (runData) => {
  uni.showLoading({ title: '正在核验运动数据...' });
  try {
    const res = await submitActivity(runData);
    uni.hideLoading();
    console.log('Submit success:', res);
    uni.setStorageSync('tempRunResult', res);
    appendLocalRunRecord(runData);
    redirectToRunResult();
    return res;
  } catch (e) {
    uni.hideLoading();
    throw e;
  }
};

// 11. 结束跑步（统一逻辑）
const stopRun = async () => {
  if (!isRunning.value) return;
  syncRunElapsedDisplay();
  isRunning.value = false;
  clearRunTickTimer();
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

  // 结束前进行一次人脸验证拍照
  const faceOk = await faceVerify('end');
  if (!faceOk) {
    resumeRunAfterEndFaceCancelled();
    return;
  }

  if (!endFaceUrl.value) {
    uni.showModal({
      title: '验证异常',
      content: '未获取到终点人脸照片，请再次点击结束并完成拍照。',
      showCancel: false
    });
    resumeRunAfterEndFaceCancelled();
    return;
  }

  const distKm = distance.value / 1000;
  const durOk = !taskMinDurationSec.value || duration.value >= taskMinDurationSec.value;
  const distOk = !policeTargetDistance.value || distance.value >= policeTargetDistance.value;
  const taskMetPreview = !taskId.value || (distOk && durOk);

  const runData = {
    type: 'run',
    source: taskId.value ? 'task' : 'free',
    started_at: new Date(Date.now() - duration.value * 1000).toISOString(),
    ended_at: new Date().toISOString(),
    metrics: {
      distance: distKm,
      duration: duration.value,
      pace: currentPace.value.toFixed(1),
      step_count: stepCount.value,
      count: currentMode.value === 'police' ? 1 : null,
      qualified: taskId.value ? taskMetPreview : (currentMode.value === 'police' ? currentPace.value <= policeTargetPace.value : false),
      trajectory: JSON.stringify(trajectoryPoints.value),
      checkpoints: JSON.stringify(checkinRecords.value)
    },
    evidence: []
  };
  if (taskId.value) {
    runData.task_id = Number(taskId.value);
  }

  // 添加起跑与结束人脸照片证据（如有）
  if (startFaceUrl.value) {
    runData.evidence.push({
      evidence_type: 'start_face',
      data_ref: startFaceUrl.value
    });
  }
  if (endFaceUrl.value) {
    runData.evidence.push({
      evidence_type: 'end_face',
      data_ref: endFaceUrl.value
    });
  }

  try {
    await submitCurrentRunToServer(runData);
  } catch (error) {
    console.error('Submit failed:', error);
    const msg = error?.message || error?.detail || String(error) || '网络或服务器错误，请重试';
    uni.showModal({
      title: '提交失败',
      content: msg,
      confirmText: '重试',
      cancelText: '强制结束',
      success: (modalRes) => {
        if (modalRes.confirm) {
          submitCurrentRunToServer(runData).catch((e2) => {
            uni.showToast({
              title: e2?.message || e2?.detail || '重试失败，请稍后再试',
              icon: 'none',
              duration: 2500
            });
          });
        } else if (modalRes.cancel) {
          uni.showToast({ title: '已强制结束', icon: 'none' });
          setTimeout(() => {
            uni.reLaunch({ url: '/pages/tab/home' });
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

.task-mode-hint {
  background: #e6fff6;
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 16rpx;
}
.task-mode-hint-text {
  font-size: 28rpx;
  color: #0d8f6e;
  font-weight: 600;
}
.task-desc {
  display: block;
  margin-top: 12rpx;
  color: #666;
  font-size: 26rpx;
  line-height: 1.5;
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
  justify-content: space-between;
  position: relative;
  padding: 0 15px;
}

.navbar-left {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  color: #ffffff;
  font-size: 40rpx;
  font-weight: bold;
}

.navbar-title {
  color: #ffffff;
  font-size: 16px;
  font-weight: bold;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.navbar-right {
  width: 60rpx;
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
