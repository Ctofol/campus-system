<template>
  <view class="run">
    <!-- Custom Navigation Bar -->
    <view class="custom-navbar" :style="{paddingTop: statusBarHeight + 'px'}">
      <view class="navbar-content">
        <view class="navbar-left" @click="goBack">
          <text class="back-icon">←</text>
        </view>
        <text class="navbar-title">璺戞</text>
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
      <text class="ai-btn-icon">馃</text>
      <text class="ai-btn-text">AI鍔╂墜</text>
    </view>

    <!-- 1. 鎼滅储鎵撳崱鐐癸紙浠呮牎鍥墦鍗＄敤锛?-->
    <view class="search-bar" v-if="currentMode === 'campus'">
      <view class="map-select-panel">
        <view class="map-select-btn" @click="handleMapSelect">
          <text class="map-icon">📍</text>
          <view class="map-select-copy">
            <text class="map-select-title">选择校园打卡点</text>
            <text class="map-select-desc">点这里从地图上选位置</text>
          </view>
          <view class="map-select-arrow link-arrow" />
        </view>
        <text class="map-select-hint">选点后会自动匹配最近的有效打卡点</text>
      </view>
    </view>

    <!-- 2. 鍦板浘灞曠ず -->
    <view class="overview-card">
      <text class="overview-title">浠婃棩璺戞姒傝</text>
      <view class="overview-meta">
        <text>娆℃暟锛歿{ todayRunCount }}</text>
        <text>閲岀▼锛歿{ todayRunDistance }} km</text>
      </view>
      <text v-if="teacherRunTask" class="task-tip">鏁欏笀浠诲姟锛歿{ teacherRunTask }}</text>
    </view>
    <map 
      v-if="isMapReady"
      class="map" 
      :latitude="lat" 
      :longitude="lng" 
      :markers="markers"
      :polyline="polyline"
      :enable-zoom="true"
      :enable-scroll="true"
      :show-compass="true"
      :min-scale="3"
      :max-scale="20"
      scale="16"
      :show-location="showNativeLocation"
    >
       <cover-view class="location-status-bar" :style="{ display: locationState === 'success' ? 'none' : 'flex' }">
         <cover-view class="status-text">{{ locationStatusText }}</cover-view>
       </cover-view>
       <cover-view v-if="showMapLegend" class="map-legend">
         <cover-view class="legend-row">
           <cover-view class="legend-pin legend-pin-me" />
           <cover-view class="legend-txt">我的位置</cover-view>
         </cover-view>
         <cover-view v-if="isRunning && trajectoryPointCount >= 2" class="legend-row">
           <cover-view class="legend-line-sample" />
           <cover-view class="legend-txt">跑步轨迹</cover-view>
         </cover-view>
         <cover-view v-if="runStartMarker" class="legend-row">
           <cover-view class="legend-pin legend-pin-start" />
           <cover-view class="legend-txt">起点</cover-view>
         </cover-view>
       </cover-view>
    </map>

    <!-- 2.5 鎺ㄨ崘璺嚎锛堟柊澧烇級 -->
    <view class="routes-card" v-if="currentMode === 'normal'">
      <view class="card-header" @click="toggleRoutes">
        <text class="card-title">馃弮 鎺ㄨ崘璺嚎</text>
        <text class="card-toggle">{{ showRoutes ? '鏀惰捣' : '灞曞紑' }}</text>
      </view>
      <view class="routes-list" v-if="showRoutes">
        <view class="route-item" v-for="(route, idx) in recommendRoutes" :key="idx" @click="useRoute(route)">
          <view class="route-info">
            <text class="route-name">{{ route.name }}</text>
            <text class="route-meta">{{ route.distance }}km · {{ route.difficulty }}</text>
          </view>
          <text class="route-action">去跑步</text>
        </view>
      </view>
    </view>

    <!-- 3. 鏍稿績璺戞妯″紡鍒囨崲锛堜换鍔¤窇閿佸畾涓恒€屼笓椤规祴璇曘€嶄腑闂撮〉锛?-->
    <view class="mode-switch" v-if="!taskRunLocked">
      <text class="mode-item" :class="{active: currentMode === 'normal'}" @click="switchMode('normal')">鏅€氳窇姝</text>
      <text class="mode-item" :class="{active: currentMode === 'police'}" @click="switchMode('police')">涓撻」娴嬭瘯</text>
      <text class="mode-item" :class="{active: currentMode === 'campus'}" @click="switchMode('campus')">鏍″洯鎵撳崱</text>
    </view>
    <view v-else class="task-mode-hint">
      <text class="task-mode-hint-text">馃搵 浠诲姟璺戞锛堜笓椤硅窇锛壜?宸查攣瀹氭ā寮</text>
    </view>

    <!-- 4. 涓撻」娴嬭瘯璁″垝 / 浠诲姟瑕佹眰 -->
    <view v-if="currentMode === 'police'" class="police-plan">
  <text class="plan-title">{{ taskRunLocked ? '鏈浠诲姟瑕佹眰' : '涓撻」浣撹兘璁粌' }}</text>
  <view class="plan-info">
    <view class="info-item">
      <text>鏈€浣庤窛绂伙細</text>
      <text class="highlight">{{ (policeTargetDistance / 1000).toFixed(1) }} 鍏噷</text>
    </view>
    <view class="info-item" v-if="taskMinDurationSec > 0">
      <text>鏈€浣庢椂闀匡細</text>
      <text class="highlight">{{ Math.floor(taskMinDurationSec / 60) }} 分 {{ taskMinDurationSec % 60 }} 秒</text>
    </view>
    <view class="info-item">
      <text>鍙傝€冮厤閫燂細</text>
      <text class="highlight">{{ policeTargetPace }} 鍒嗛挓/鍏噷</text>
      <text>锛堝睍绀虹敤锛岃揪鏍囦互浠诲姟璺濈/鏃堕暱涓哄噯锛</text>
    </view>
    <text class="info-item task-desc" v-if="taskRunLocked && taskDescription">{{ taskDescription }}</text>
  </view>
</view>

    <!-- 5. 鏅€氳窇姝?-->
    <view v-if="currentMode === 'normal'" class="run-mode-box">
      <view v-if="!isRunning" class="start-box">
        <text class="tip">鏃犲湴鐐?璺濈闄愬埗锛岃嚜鐢辫褰曡窇姝ヨ建杩</text>
        <button @click="startNormalRun" class="start-btn">寮€濮嬭窇姝</button>
      </view>
      <view v-else class="running-box">
        <text class="data">鏃堕暱锛歿{duration}}绉?| 宸茶窇锛歿{((distance || 0)/1000).toFixed(2)}}km | 閫熷害锛歿{currentSpeedKmh}}km/h</text>
        <text class="data">姝ユ暟锛歿{stepCount}} | 蹇冪巼锛歿{heartRate}}娆?鍒?| 骞冲潎閫熷害锛歿{avgSpeedKmh}}km/h</text>
        <view class="progress-wrap">
          <view class="progress-bar">
            <view class="progress-fill" :style="{width: normalProgress + '%'}"></view>
          </view>
          <text class="progress-text">宸茶窇 {{((distance || 0)/1000).toFixed(2)}} km</text>
        </view>
        <button @click="stopRun" class="stop-btn">缁撴潫璺戞</button>
      </view>
    </view>

    <!-- 6. 涓撻」璺戞锛堟寜2000绫崇洰鏍囪窇锛?-->
    <view v-if="currentMode === 'police'" class="run-mode-box">
      <view v-if="!isRunning" class="start-box">
        <text class="tip">鎸夎绋嬭姹傚畬鎴?000绫宠窇锛岃嚜鍔ㄦ牎楠岄厤閫熸槸鍚﹁揪鏍</text>
        <button @click="startPoliceRun" class="start-btn">寮€濮嬩笓椤硅缁</button>
      </view>
      <view v-else class="running-box">
        <text class="data">鏃堕暱锛歿{duration}}绉?| 宸茶窇锛歿{(distance/1000).toFixed(2)}}km / 鐩爣锛?km</text>
        <text class="data">鍓╀綑锛歿{(Math.max(0, policeTargetDistance - distance)/1000).toFixed(2)}}km | 閰嶉€燂細{{currentPace.toFixed(1)}}鍒嗛挓/鍏噷</text>
        <text class="data">蹇冪巼锛歿{heartRate}}娆?鍒?| 姝ユ暟锛歿{stepCount}}</text>
        <text class="pace-status" :style="{color: currentPace <= policeTargetPace ? 'green' : 'red'}">
          {{currentPace <= policeTargetPace ? '✅ 配速达标' : '❌ 配速未达标'}}
        </text>
        <!-- 杈惧埌鐩爣璺濈鑷姩鎻愮ず -->
        <text class="finish-tip" v-if="distance >= policeTargetDistance">馃帀 宸插畬鎴?000绫崇洰鏍囷紒</text>
        <view class="progress-wrap">
          <view class="progress-bar"><view class="progress-fill" :style="{width: policeProgress + '%'}"></view></view>
          <text class="progress-text">涓撻」鐩爣 2 km 路 瀹屾垚 {{(distance/1000).toFixed(2)}} km</text>
        </view>
        <button @click="stopRun" class="stop-btn">缁撴潫璁粌</button>
      </view>
    </view>

    <!-- 7. 鏍″洯鎵撳崱 -->
    <view v-if="currentMode === 'campus'" class="run-mode-box">
      <view v-if="!checkpoint.name" class="no-checkpoint">
        <text class="tip">璇峰厛鎼滅储鏍″洯鎵撳崱鐐</text>
      </view>
      <view v-else>
        <view v-if="!isRunning" class="start-box">
          <text class="checkpoint-info">鎵撳崱鐐癸細{{checkpoint.name}}锛堝埌杈剧害 {{ checkpoint.radius || 100 }} 绫冲唴鍙垽瀹氫负宸插埌杈撅級</text>
          <button @click="startCampusRun" class="start-btn">寮€濮嬫墦鍗</button>
        </view>
        <view v-else class="running-box">
          <text class="data">鏃堕暱锛歿{duration}}绉?| 璺濇墦鍗＄偣锛歿{distanceToCheckpoint}}绫?| 姝ユ暟锛歿{stepCount}} | 蹇冪巼锛歿{heartRate}}娆?鍒</text>
          <text class="reach-status" :style="{color: isReach ? 'green' : 'red'}">
            {{isReach ? '✅ 已到达打卡点' : '❌ 未到达打卡点'}}
          </text>
          <button @click="stopRun" class="stop-btn">缁撴潫鎵撳崱</button>
        </view>
      </view>
    </view>
    
    <view v-if="showFaceCamera" class="face-camera-mask">
      <!-- #ifdef MP-WEIXIN -->
      <camera
        id="faceCamera"
        class="face-camera-view"
        device-position="front"
        flash="off"
        @initdone="handleFaceCameraReady"
        @error="handleFaceCameraError"
      />
      <!-- #endif -->
      <view class="face-camera-panel">
        <text class="face-camera-title">{{ faceCapturePhase === 'end' ? '结束人脸验证' : '开始人脸验证' }}</text>
        <text class="face-camera-tip">璇锋瑙嗛暅澶存媿鎽勶紝鎷嶇収鍚庝細鐩存帴涓婁紶鐢ㄤ簬鏈璺戞楠岃瘉</text>
        <text v-if="faceCameraErrorText" class="face-camera-error">{{ faceCameraErrorText }}</text>
        <view class="face-camera-actions">
          <button class="face-camera-cancel" @click="cancelFaceCamera">鍙栨秷</button>
          <button class="face-camera-shoot" :disabled="faceCameraBusy" @click="captureFaceFromInlineCamera">
            {{ faceCameraBusy ? '上传中...' : '拍照上传' }}
          </button>
        </view>
      </view>
    </view>

  </view>
</template>

<script setup>
// 缁熶竴瀵煎叆瑙勮寖
import { ref, computed, onUnmounted, onMounted, nextTick } from 'vue';
import AiChatRobot from '@/components/ai-chat-robot/ai-chat-robot.vue';
import { submitActivity, getCheckpoints, checkIn, uploadFile, getStudentTaskDetail } from '@/utils/request.js';
import { getCurrentLocation } from '@/utils/location.js';

// Navbar Settings
const statusBarHeight = ref(20);

const isMapReady = ref(false);

// 杩斿洖鎸夐挳
const goBack = () => {
  uni.navigateBack({
    delta: 1
  });
};

// 缁勪欢鎸傝浇鏃惰幏鍙栫姸鎬佹爮楂樺害
onMounted(() => {
  const sys = uni.getSystemInfoSync();
  statusBarHeight.value = sys.statusBarHeight || 20;
  
  // 寤惰繜鍔犺浇鍦板浘锛岄槻姝㈠鍣ㄦ湭灏辩华瀵艰嚧鐨勬覆鏌撻敊璇?
  setTimeout(() => {
    isMapReady.value = true;
  }, 500);
  
  // 鍒濆鍖栦氦缁欑埗椤?onShow 璋冪敤 onPageShow锛堝甫 options锛夛紱姝ゅ涓嶅啀璋冪敤锛岄伩鍏嶄笌鐖堕〉 50ms 鍚庣殑璋冪敤褰㈡垚銆屽厛绌哄悗瀹炪€嶈闃叉姈璇悶
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

// 椤甸潰鏄剧ず閫昏緫 (鏇夸唬 onShow)
let isPageActive = false;
let lastShowTime = 0;

/** 鐖堕〉 onLoad 浼犲叆鐨勫惎鍔ㄥ弬鏁帮紙鏈?taskId 绛夋椂涓嶅彲琚€岀┖ onShow銆嶉槻鎶栨帀锛?*/
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
    // 浠呰烦杩囥€岀煭鏃堕棿鍐呴噸澶嶄笖鏃犺矾鐢卞弬鏁般€嶇殑鎶栧姩锛涘甫 taskId/mode 鐨勭浜屾璋冪敤蹇呴』鎵ц锛堝惁鍒欎换鍔¤窇銆佽矾鐢卞弬鏁颁涪澶憋級
    if (!forceTask && now - lastShowTime < 500 && !hasMeaningfulRunPageOptions(options)) {
        return;
    }
    lastShowTime = now;

    isPageActive = true;
    
    // 鏇存柊鐘舵€佹爮楂樺害
    const sys = uni.getSystemInfoSync();
    statusBarHeight.value = sys.statusBarHeight || 20;

    // 寮哄埗璁剧疆瀵艰埅鏍忔爣棰樺拰棰滆壊 (铏界劧鏄粍浠讹紝浣嗗鏋滈渶瑕佸姩鎬佷慨鏀圭埗瀹瑰櫒瀵艰埅鏍忥紝涔熷彲浠ヤ繚鐣?
    uni.setNavigationBarTitle({
      title: '璺戞'
    });
    uni.setNavigationBarColor({
      frontColor: '#ffffff',
      backgroundColor: '#20C997'
    });
    
    const role = uni.getStorageSync('userRole') || uni.getStorageSync('role');
    if (role === 'teacher') {
      uni.showToast({ title: '该功能仅对学生开放', icon: 'none' });
      // 娉ㄦ剰锛氳繖閲屽彲鑳介渶瑕佺埗缁勪欢閰嶅悎璺宠浆锛屾垨鑰呯洿鎺ヤ娇鐢?uni.switchTab
      setTimeout(() => {
        // 鍋囪 teacher home 涔熸槸 tab 椤?
        uni.switchTab({ url: '/pages/tab/home' }); // Correct path to home tab
      }, 800);
      return;
    }

    // 鏍规嵁鎬у埆鑷姩璁剧疆鏅€氳窇姝ョ洰鏍囬噷绋?
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

    // 澶勭悊鍙傛暟 (鍚堝苟 onLoad 閫昏緫)
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
      if (options.taskTitle) {
        teacherRunTask.value = decodeURIComponent(options.taskTitle);
      }
      taskDescription.value = options.taskDescription ? decodeURIComponent(options.taskDescription) : '';
      taskMinDurationSec.value = Number(options.taskMinDurationSec || options.minDuration || 0) || 0;
      const routeDistanceKm = Number(options.taskMinDistanceKm || options.minDistance || 0);
      if (routeDistanceKm > 0) {
        policeTargetDistance.value = Math.round(routeDistanceKm * 1000);
      }
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
      uni.showToast({ title: `寮€濮嬭绋嬶細${options.course}`, icon: 'none' });
    }

    const targetMode = uni.getStorageSync('runMode');
    if (targetMode && !taskRunLocked.value && !isRunning.value) {
      switchMode(targetMode);
      uni.removeStorageSync('runMode');
    }

    startLocationService();
    
    // Load Checkpoints for Campus Mode
    getCheckpoints().then(data => {
      availableCheckpoints.value = Array.isArray(data) ? data : [];
    }).catch(err => {
      console.error('Failed to load checkpoints', err);
      availableCheckpoints.value = [];
    });

    checkpoint.value = {};
    checkpointName.value = '';
    checkpointMarker.value = null;
    navPolyline.value = null;
    uni.removeStorageSync('checkpoint');
    refreshMarkers();
    updateMapPolyline();
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
const showFaceCamera = ref(false);
const faceCapturePhase = ref('start');
const faceCameraBusy = ref(false);
const faceCameraErrorText = ref('');
let faceCameraResolve = null;
let faceCameraContext = null;

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
    uni.showToast({ title: '鍔犺浇浠诲姟瑕佹眰澶辫触', icon: 'none' });
  }
};

// 鏆撮湶缁欑埗缁勪欢 (Merged below)
// defineExpose({
//   onPageShow
// });

const handleShareToTeacher = (card) => {
  // Save shared report to storage for teacher to see (mock)
  const report = {
    studentName: uni.getStorageSync('userInfo')?.name || '瀛﹀憳',
    time: new Date().toLocaleString(),
    card: card
  };
  // In a real app, this would be an API call. 
  // Here we mock it by saving to a global list that teacher page reads.
  let sharedReports = uni.getStorageSync('mockSharedReports') || [];
  sharedReports.unshift(report);
  uni.setStorageSync('mockSharedReports', sharedReports);
};

// 姒傝涓庝换鍔℃彁绀?
const todayRunCount = ref(0);
const todayRunDistance = ref(0);
const teacherRunTask = ref('');
const dailyTarget = ref(2);
const normalProgress = ref(0);
const policeProgress = ref(0);
const historyList = ref([]);

// 鏂板鏁版嵁
const showRoutes = ref(false);
const recommendRoutes = ref([
  { name: '环校外圈跑', distance: 5.2, difficulty: '中等' },
  { name: '湖畔林荫道', distance: 3.0, difficulty: '简单' },
  { name: '体育场冲刺', distance: 1.5, difficulty: '困难' }
]);
const toggleRoutes = () => showRoutes.value = !showRoutes.value;
const availableCheckpoints = ref([]);
const useRoute = (route) => {
  uni.showToast({ title: `宸插姞杞借矾绾匡細${route.name}`, icon: 'none' });
  dailyTarget.value = route.distance;
};

// 1. 鍦板浘/鎵撳崱鐐规暟鎹?
const locationState = ref('idle'); // idle, locating, success, fail
/** 鏈€杩戜竴娆°€屽彲寮€璺戙€嶇殑瀹氫綅鏄惁鏉ヨ嚜缂撳瓨鍏滃簳锛堢湡 GPS 鏈垚鍔燂級锛屼究浜庢彁绀虹敤鎴峰埛鏂颁互鍏嶉噷绋嬮暱鏈熶负 0 */
const lastLocationFixWasStale = ref(false);
let locationRetryTimer = null;
let locationPromise = null;
/** 寰俊灏忕▼搴忥細瀹氫綅鍏滃簳 setTimeout锛岄』鍦ㄥ仠姝㈣窇姝ヤ笌鍗歌浇鏃舵竻闄?*/
let wxLocationWatchdogTimer = null;
/** 寰俊灏忕▼搴忥細鏄惁宸叉垚鍔熷紑鍚悗鍙版寔缁畾浣嶏紙涓?startLocationUpdateBackground 鐘舵€佸悓姝ワ級 */
let mpBackgroundLocationActive = false;
/** 寰俊鐪熸満 map 椤?onLocationChange 甯镐笉鍥炶皟锛氫笌鎸佺画瀹氫綅骞惰 2s getLocation锛岄┍鍔ㄦ椂闀?閲岀▼ */
let wxRunAssistTimer = null;
/** 璺戞涓?GPS 鎸囨暟骞虫粦鐘舵€侊紝鍑忚交灏忕▼搴忕杞ㄨ抗閿娇涓庝弗閲嶅亸绉绘姈鍔?*/
let runLocationSmooth = null;
/** 宸茶閲岀▼閫昏緫鎺ョ撼鐨勬湁鏁堣建杩圭偣鏁帮紝鐢ㄤ簬鍒ゆ柇 GPS 閫熷害鏄剧ず鏄惁杩涘叆绋冲畾闃舵 */
let gpsAcceptedPointCount = 0;
/** 鏈€杩戜竴娆″師濮嬪畾浣嶉噰鏍凤細鐢ㄤ簬鍘婚噸鍜屾姂鍒跺苟琛屽洖璋冨鑷寸殑闈欐鎶栧姩 */
let lastRawLocationSample = null;
let lastStepDetectedAt = 0;
let lastStrongStepMotionAt = 0;
let lastGpsMotionAt = 0;
let stepBurstCount = 0;
let gpsMotionBurstCount = 0;

const resetRunMotionEvidence = () => {
  lastStepDetectedAt = 0;
  lastStrongStepMotionAt = 0;
  lastGpsMotionAt = 0;
  stepBurstCount = 0;
  gpsMotionBurstCount = 0;
};

const hasRecentStepMotion = () => lastStepDetectedAt > 0 && (Date.now() - lastStepDetectedAt) < 4500;
const hasStrongStepMotion = () => lastStrongStepMotionAt > 0 && (Date.now() - lastStrongStepMotionAt) < 6500;
const hasRecentGpsMotionEvidence = () => lastGpsMotionAt > 0 && (Date.now() - lastGpsMotionAt) < 7000;
const hasTrustedRunMotion = () => hasStrongStepMotion() || hasRecentGpsMotionEvidence();

const noteStepMotion = (now) => {
  const gap = lastStepDetectedAt > 0 ? now - lastStepDetectedAt : Infinity;
  if (gap >= 260 && gap <= 1600) {
    stepBurstCount += 1;
  } else {
    stepBurstCount = 1;
  }
  lastStepDetectedAt = now;
  if (stepBurstCount >= 2) {
    lastStrongStepMotionAt = now;
  }
};

const noteGpsMotion = (now, segmentDistanceM, speedMps, accuracyM) => {
  const goodAccuracy = !Number.isFinite(accuracyM) || accuracyM <= 35;
  const speedOk = speedMps >= 0.8 && speedMps <= 5.8;
  const distanceOk = segmentDistanceM >= 2.4;
  if (goodAccuracy && speedOk && distanceOk) {
    gpsMotionBurstCount += 1;
    if (gpsMotionBurstCount >= 2) {
      lastGpsMotionAt = now;
    }
    return;
  }
  if (Number.isFinite(accuracyM) && accuracyM > 60) {
    gpsMotionBurstCount = 0;
  } else {
    gpsMotionBurstCount = Math.max(0, gpsMotionBurstCount - 1);
  }
};

const classifyMotionTier = ({ speedMps, distanceM, timeDiffS, trustedMotion, recentStepMotion, accuracyM }) => {
  const reliableAccuracy = !Number.isFinite(accuracyM) || accuracyM <= 35;
  const stepBacked = trustedMotion || recentStepMotion;
  const segmentDistance = Number.isFinite(distanceM) ? distanceM : 0;
  const segmentSpeed = Number.isFinite(speedMps) ? speedMps : 0;
  const dt = Number.isFinite(timeDiffS) ? timeDiffS : 0;

  if (stepBacked && reliableAccuracy && segmentSpeed >= 2.75 && segmentDistance >= Math.max(6.5, dt * 1.7)) {
    return 'fast_run';
  }
  if (stepBacked && segmentSpeed >= 1.75 && segmentDistance >= Math.max(4.2, dt * 1.15)) {
    return 'jog';
  }
  if (stepBacked && segmentSpeed >= 0.7 && segmentDistance >= Math.max(2.2, dt * 0.45)) {
    return 'walk';
  }
  if (!stepBacked && reliableAccuracy && segmentSpeed >= 1.6 && segmentDistance >= Math.max(4.8, dt * 1.25)) {
    return 'jog';
  }
  if (!stepBacked && reliableAccuracy && segmentSpeed >= 0.85 && segmentDistance >= Math.max(3.2, dt * 0.65)) {
    return 'walk';
  }
  return 'unknown';
};

const getMotionTierConfig = (tier, { coldPhase, weakGpsSignal, earlyMotionStrict, tightenNoSteps }) => {
  const configs = {
    walk: {
      minDistance: weakGpsSignal ? 3.8 : 2.2,
      maxSpeed: 2.45,
      minSpeed: 0.65,
      maxStepDistance: weakGpsSignal ? 9.5 : 12,
      requiresTrustedMotion: weakGpsSignal && (earlyMotionStrict || tightenNoSteps)
    },
    jog: {
      minDistance: weakGpsSignal ? 4.8 : 3.8,
      maxSpeed: 4.9,
      minSpeed: 1.45,
      maxStepDistance: weakGpsSignal ? 14 : 18,
      requiresTrustedMotion: false
    },
    fast_run: {
      minDistance: weakGpsSignal ? 6.2 : 5.2,
      maxSpeed: 7.2,
      minSpeed: 2.6,
      maxStepDistance: weakGpsSignal ? 20 : 24,
      requiresTrustedMotion: false
    },
    unknown: {
      minDistance: weakGpsSignal ? 5.4 : 3.6,
      maxSpeed: tightenNoSteps ? 2.8 : 3.6,
      minSpeed: 0.8,
      maxStepDistance: weakGpsSignal ? 8.5 : 10.5,
      requiresTrustedMotion: weakGpsSignal || tightenNoSteps
    }
  };

  const base = configs[tier] || configs.unknown;
  const coldBump = coldPhase ? 1 : 0;
  return {
    ...base,
    minDistance: base.minDistance + coldBump,
    maxSpeed: coldPhase && tier === 'walk' ? Math.min(base.maxSpeed, 2.1) : base.maxSpeed,
    maxStepDistance: coldPhase ? Math.max(4.5, base.maxStepDistance - 1.5) : base.maxStepDistance
  };
};
const clearWxRunAssistTimer = () => {
  if (wxRunAssistTimer != null) {
    clearTimeout(wxRunAssistTimer);
    clearInterval(wxRunAssistTimer);
    wxRunAssistTimer = null;
  }
};

const checkpointName = ref('');
const DEFAULT_MAP_LAT = 39.909;
const DEFAULT_MAP_LNG = 116.397;
const lat = ref(DEFAULT_MAP_LAT);
const lng = ref(DEFAULT_MAP_LNG);
const markers = ref([]);
const checkpointMarker = ref(null);
const runStartMarker = ref(null);
const runEndMarker = ref(null);

const hasPlausibleCoords = () => {
  if (!Number.isFinite(lat.value) || !Number.isFinite(lng.value)) return false;
  return !(
    Math.abs(lat.value - DEFAULT_MAP_LAT) < 0.0002 &&
    Math.abs(lng.value - DEFAULT_MAP_LNG) < 0.0002
  );
};

/** 有真实坐标或已定位成功时显示系统蓝点 */
const showNativeLocation = computed(
  () => locationState.value === 'success' || (locationState.value === 'locating' && hasPlausibleCoords())
);

const showMapLegend = computed(() => locationState.value === 'success' && hasPlausibleCoords());

const createCurrentLocationMarker = (latitude, longitude) => {
  const locating = locationState.value !== 'success';
  return {
    id: 0,
    latitude,
    longitude,
    title: '当前位置',
    iconPath: '/static/location.png',
    width: locating ? 46 : 58,
    height: locating ? 46 : 58,
    zIndex: 100,
    anchor: { x: 0.5, y: 0.5 },
    callout: {
      content: locating ? '定位中…' : '我的位置',
      color: '#333333',
      fontSize: 12,
      borderRadius: 8,
      bgColor: '#ffffff',
      padding: 6,
      display: locating ? 'BYCLICK' : 'ALWAYS',
      borderWidth: 1,
      borderColor: '#20C997'
    }
  };
};

const createRunPointMarker = (id, latitude, longitude, labelText, bgColor) => ({
  id,
  latitude,
  longitude,
  iconPath: '/static/location.png',
  width: 24,
  height: 24,
  zIndex: 60 + id,
  anchor: { x: 0.5, y: 0.5 },
  alpha: 0.35,
  label: {
    content: labelText,
    color: '#ffffff',
    fontSize: 11,
    bgColor,
    borderRadius: 6,
    padding: 4,
    anchorX: -10,
    anchorY: -40
  }
});

const refreshMarkers = () => {
  const nextMarkers = [];
  if (runStartMarker.value) {
    nextMarkers.push({ ...runStartMarker.value });
  }
  if (runEndMarker.value) {
    nextMarkers.push({ ...runEndMarker.value });
  }
  if (checkpointMarker.value) {
    nextMarkers.push({ ...checkpointMarker.value });
  }
  if (hasPlausibleCoords()) {
    nextMarkers.push(createCurrentLocationMarker(lat.value, lng.value));
  }
  markers.value = nextMarkers;
};

// Separate line states for better management
const runPolyline = ref({
  points: [],
  color: '#1E88E5',
  width: 6,
  arrowLine: true,
  borderColor: '#FFFFFF',
  borderWidth: 2
});
const navPolyline = ref(null);

const polyline = ref([]); // Final array for map component
const checkpoint = ref({});
const trajectoryPoints = ref([]); // Store real GPS points
const checkinRecords = ref([]); // Store successful check-ins

const trajectoryPointCount = computed(() => trajectoryPoints.value.length);

// Helper to update map polyline with deep clone to force render
const updateMapPolyline = () => {
  const lines = [];
  // 1. Add running trajectory (Blue)
  // 寰俊灏忕▼搴忓湴灞傚浘灞傞潪甯镐弗鑻涳紝points蹇呴』瑕?=2涓偣鎵嶄細鐢熸垚璺嚎锛岀┖鏁扮粍鍙嶈€屼細鎶ラ敊宕╂簝
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

/**
 * 杞ㄨ抗鎶樼嚎鍑犱綍闀垮害锛堢背锛夛細鐩搁偦鐐?Haversine 涔嬪拰锛屽崟娈靛皝椤舵姂鍒跺崟鐐归鐐广€?
 * 鎻愪氦鍓嶄笌 `distance` 瀵归綈锛屽噺杞荤涓婃护娉㈣繃涓ュ鑷淬€岀晫闈?鍦板浘涓庡叾瀹冭蒋浠舵洿鎺ヨ繎 2km锛屼絾涓婃姤涓嶈冻 2km 鈫?闃冲厜璺戦噷绋嬩笉瓒炽€嶃€?
 */
const computeTrajectoryPathLengthM = (points) => {
  if (!points || points.length < 2) return 0;
  let s = 0;
  for (let i = 1; i < points.length; i++) {
    const a = points[i - 1];
    const b = points[i];
    if (a == null || b == null || a.latitude == null || b.latitude == null) continue;
    const seg = getDistance(a.latitude, a.longitude, b.latitude, b.longitude);
    s += Math.min(seg, 65);
  }
  return s;
};

/** 浠庡洖璋冨璞℃垨鏁板€间腑鍙栨按骞崇簿搴︼紙绫筹級锛岀敤浜庡喎鍚姩闃叉紓绉伙紱涓嶇敤浜庢暣娈典涪寮冪偣 */
const getHorizontalAccuracyM = (accuracyOrRes) => {
  if (accuracyOrRes == null) return NaN;
  if (typeof accuracyOrRes === 'number') {
    return Number.isFinite(accuracyOrRes) ? accuracyOrRes : NaN;
  }
  const a = accuracyOrRes.accuracy;
  const h = accuracyOrRes.horizontalAccuracy;
  const n = a != null ? Number(a) : h != null ? Number(h) : NaN;
  return Number.isFinite(n) ? n : NaN;
};

const hasReliableGpsMovement = () => {
  return gpsAcceptedPointCount >= 3 || distance.value >= 28 || currentSpeed.value >= 1.15;
};

const estimateStepsByDistance = (distanceM) => {
  if (!Number.isFinite(distanceM) || distanceM < 6) return 0;
  const strideLengthM = currentMode.value === 'police' ? 0.72 : 0.78;
  return Math.floor(distanceM / strideLengthM);
};

const maybeEstimateStepsFromDistance = () => {
  const estimatedSteps = estimateStepsByDistance(distance.value);
  if (estimatedSteps <= 0) return;
  const now = Date.now();
  const sensorLooksMissing =
    !lastStrongStepMotionAt ||
    (now - lastStrongStepMotionAt > 12000 && distance.value >= 30);
  if (stepCount.value === 0 || (sensorLooksMissing && estimatedSteps > stepCount.value + 8)) {
    stepCount.value = estimatedSteps;
  }
};

// Unified location update logic
const updateLocationLogic = (newLat, newLng, speed, accuracyOrRes) => {
  const nowTs = Date.now();
  if (
    isRunning.value &&
    lastRawLocationSample &&
    lastRawLocationSample.latitude != null &&
    lastRawLocationSample.longitude != null
  ) {
    const rawDt = (nowTs - lastRawLocationSample.timestamp) / 1000;
    const rawD = getDistance(
      lastRawLocationSample.latitude,
      lastRawLocationSample.longitude,
      newLat,
      newLng
    );
    if (rawDt < 0.9 && rawD < 0.7) {
      return;
    }
  }
  lastRawLocationSample = { latitude: newLat, longitude: newLng, timestamp: nowTs };

  let workLat = newLat;
  let workLng = newLng;
  if (isRunning.value) {
    const lastTrackPoint = trajectoryPoints.value[trajectoryPoints.value.length - 1];
    const rawDistanceToLast = lastTrackPoint
      ? getDistance(lastTrackPoint.latitude, lastTrackPoint.longitude, newLat, newLng)
      : 0;
    const smoothAlpha = rawDistanceToLast > 10 ? 0.82 : 0.68;
    const suspiciousLargeJump = rawDistanceToLast > (hasReliableGpsMovement() ? 35 : 12);
    if (!runLocationSmooth && trajectoryPoints.value.length > 0) {
      const p0 = trajectoryPoints.value[trajectoryPoints.value.length - 1];
      runLocationSmooth = { lat: p0.latitude, lng: p0.longitude };
    }
    if (!runLocationSmooth) {
      runLocationSmooth = { lat: newLat, lng: newLng };
    } else if (suspiciousLargeJump) {
      const deltaLat = newLat - runLocationSmooth.lat;
      const deltaLng = newLng - runLocationSmooth.lng;
      const deltaDist = Math.max(rawDistanceToLast, 0.0001);
      const cappedMoveM = hasReliableGpsMovement() ? 8 : 3.2;
      const ratio = Math.min(1, cappedMoveM / deltaDist);
      runLocationSmooth = {
        lat: runLocationSmooth.lat + deltaLat * ratio,
        lng: runLocationSmooth.lng + deltaLng * ratio
      };
    } else {
      runLocationSmooth = {
        lat: runLocationSmooth.lat + smoothAlpha * (newLat - runLocationSmooth.lat),
        lng: runLocationSmooth.lng + smoothAlpha * (newLng - runLocationSmooth.lng)
      };
    }
    workLat = runLocationSmooth.lat;
    workLng = runLocationSmooth.lng;
  } else {
    runLocationSmooth = null;
  }

  lat.value = isRunning.value ? workLat : newLat;
  lng.value = isRunning.value ? workLng : newLng;
  refreshMarkers();

  if (isRunning.value) {
    syncRunElapsedDisplay();
    // 涓嶅啀鎸?horizontalAccuracy 鏁存涓㈠純鍥炶皟锛氬急淇″彿涓嬪父 >100m锛屼涪寮冨悗閲岀▼姘歌繙涓嶆定锛涘紓甯镐綅绉诲凡鐢?d / calculatedSpeed 绾︽潫

    // 1. Initial point
    if (trajectoryPoints.value.length === 0) {
        const point = { latitude: workLat, longitude: workLng, timestamp: nowTs, speed: speed || currentSpeed.value };
        trajectoryPoints.value.push(point);
        runPolyline.value.points.push({ latitude: workLat, longitude: workLng });
        updateMapPolyline();
        
        // 淇锛氱涓€涓偣涔熼渶瑕佽绠楁墦鍗＄偣璺濈
        if (currentMode.value === 'campus' && checkpoint.value.lat) {
          distanceToCheckpoint.value = Math.floor(getDistance(workLat, workLng, checkpoint.value.lat, checkpoint.value.lng));
          if (distanceToCheckpoint.value <= (checkpoint.value.radius || 100)) { 
             isReach.value = true;
          }
        }
        return;
    }

    // 2. Subsequent points
    const lastPoint = trajectoryPoints.value[trajectoryPoints.value.length - 1];
    const d = getDistance(lastPoint.latitude, lastPoint.longitude, workLat, workLng);
    const timeDiff = (nowTs - lastPoint.timestamp) / 1000; // seconds

    // 鐬椂閫熷害锛坢/s锛夛細涓庢槸鍚﹁鍏ユ€婚噷绋嬭В鑰︼紝鐢ㄤ簬鐣岄潰閫熷害/閰嶉€燂紱寰俊 onLocationChange 鐨?speed 甯镐负 -1
    const spNum = typeof speed === 'number' && !Number.isNaN(speed) ? speed : -1;
    const calcSp = timeDiff > 0.001 ? d / timeDiff : 0;
    const runGpsSpeedWarmup = !hasReliableGpsMovement() && duration.value < 15 && distance.value < 28;
    if (!runGpsSpeedWarmup) {
      if (spNum >= 0 && spNum < 22) {
        currentSpeed.value = spNum;
      } else if (timeDiff >= 0.12 && calcSp > 0.06 && calcSp < 18) {
        currentSpeed.value = calcSp;
      }
    } else {
      currentSpeed.value = 0;
    }

    // Checkpoint logic - 淇锛氱Щ鍑洪噷绋嬭繃婊ら€昏緫锛岀‘淇濋潤姝㈡椂涔熻兘鍒锋柊璺濈
    if (currentMode.value === 'campus' && checkpoint.value.lat) {
      distanceToCheckpoint.value = Math.floor(getDistance(workLat, workLng, checkpoint.value.lat, checkpoint.value.lng));
      // Tolerance increased to 100m as requested for better user experience
      if (distanceToCheckpoint.value <= (checkpoint.value.radius || 100)) { 
        isReach.value = true;
        if (!uni.getStorageSync('checkpointReached')) {
           if (checkpoint.value.id) {
             checkIn({ lat: workLat, lng: workLng, checkpoint_id: checkpoint.value.id })
               .then(res => {
                 if (res.success) {
                   uni.showToast({ title: '打卡成功！', icon: 'success' });
                   checkinRecords.value.push({ checkpoint_id: checkpoint.value.id, time: new Date().toISOString(), lat: workLat, lng: workLng });
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

    // 鑻ユ椂闂撮棿闅旇繃鐭紝澶氫负閲嶅鍥炶皟锛岀暐鏀惧閬垮厤涓㈢偣
    if (timeDiff < 0.35) return;

    const calculatedSpeed = d / timeDiff;
    const accM = getHorizontalAccuracyM(accuracyOrRes);
    /** 寮€璺戝悗绾?50s 鍐?GPS 甯告姈鍔ㄥ嚭銆屾湭鍔ㄥ嵈鏈夐噷绋嬨€嶏紱鍗曞尯闂翠綅绉诲皝椤讹紝瓒呭嚭鍙籂鍋忔湯鐐广€佷笉璁￠噷绋?*/
    const coldPhase = duration.value < 50;
    /** 姝ユ暟闀挎湡涓?0 鏃朵粎闈?GPS 鏄撶疮璁″亣閲岀▼锛堟紓绉伙級锛涘湪鍑虹幇鐪熷疄姝ラ鍓嶆寔缁敹绱э紙鏈夋鏁板悗鑷姩瑙ｉ櫎锛?*/
    const recentStepMotion = hasRecentStepMotion();
    const trustedMotion = hasTrustedRunMotion();
    const tightenNoSteps = stepCount.value === 0 && !trustedMotion && duration.value >= 20 && duration.value < 90 && distance.value < 160;
    const driftTight = coldPhase || tightenNoSteps;
    const weakGpsSignal = Number.isFinite(accM) && accM > 45;
    const veryWeakGpsSignal = Number.isFinite(accM) && accM > 80;
    const earlyMotionStrict = !trustedMotion && duration.value >= 10 && duration.value < 45 && distance.value < 120;
    const motionTier = classifyMotionTier({
      speedMps: calculatedSpeed,
      distanceM: d,
      timeDiffS: timeDiff,
      trustedMotion,
      recentStepMotion,
      accuracyM: accM
    });
    const tierConfig = getMotionTierConfig(motionTier, {
      coldPhase,
      weakGpsSignal,
      earlyMotionStrict,
      tightenNoSteps
    });

    let minD = coldPhase ? 0.55 : 0.4;
    if (Number.isFinite(accM) && accM > 10) {
      minD = Math.max(minD, Math.min(accM * 0.18, coldPhase ? 8 : 5));
    } else if (coldPhase) {
      minD = Math.max(minD, 1.15);
    }
    minD = Math.max(minD, tierConfig.minDistance);

    const maxStepGate = Math.min(Math.max(1.2, timeDiff * 7.5), tierConfig.maxStepDistance);
    const maxSpeedCold = driftTight ? Math.min(5.2, tierConfig.maxSpeed) : tierConfig.maxSpeed;

    if (driftTight && (calculatedSpeed > maxSpeedCold || d > maxStepGate)) {
      return;
    }

    if (veryWeakGpsSignal && !recentStepMotion && !trustedMotion) {
      currentSpeed.value = 0;
      return;
    }

    if (
      stepCount.value === 0 &&
      !trustedMotion &&
      duration.value >= 15 &&
      timeDiff <= 2.6 &&
      d < Math.max(4.5, tierConfig.minDistance + 0.8) &&
      calculatedSpeed < Math.max(1.5, tierConfig.minSpeed + 0.15)
    ) {
      currentSpeed.value = 0;
      return;
    }

    if (
      earlyMotionStrict &&
      timeDiff <= 3.2 &&
      d < Math.max(5.5, tierConfig.minDistance + 1.4) &&
      calculatedSpeed < Math.max(1.8, tierConfig.minSpeed + 0.35)
    ) {
      currentSpeed.value = 0;
      return;
    }

    if (
      earlyMotionStrict &&
      weakGpsSignal &&
      d < Math.max(8, tierConfig.minDistance + 2.2) &&
      calculatedSpeed < Math.max(2.3, tierConfig.minSpeed + 0.7)
    ) {
      currentSpeed.value = 0;
      return;
    }

    const maxSpeedForDistance = driftTight ? Math.min(tierConfig.maxSpeed, motionTier === 'fast_run' ? 5.8 : tierConfig.maxSpeed) : Math.max(tierConfig.maxSpeed, 7.8);
    if (d >= minD && calculatedSpeed >= tierConfig.minSpeed && calculatedSpeed < maxSpeedForDistance) {
        const gpsLooksGood = (!Number.isFinite(accM) || accM <= 28) && calculatedSpeed >= 1.1 && d >= 4.5;
        const canTrustThisSegment = trustedMotion || recentStepMotion || gpsLooksGood || gpsAcceptedPointCount >= 4;
        const trustedByTier = !tierConfig.requiresTrustedMotion || trustedMotion || recentStepMotion;
        if (!trustedByTier && duration.value >= 8 && distance.value < 180) {
          currentSpeed.value = 0;
          return;
        }
        if (!canTrustThisSegment && duration.value >= 10 && distance.value < 180) {
          currentSpeed.value = 0;
          return;
        }
        distance.value += d;
        gpsAcceptedPointCount += 1;
        noteGpsMotion(nowTs, d, calculatedSpeed, accM);

        const point = { latitude: workLat, longitude: workLng, timestamp: nowTs, speed: speed || calculatedSpeed };
        trajectoryPoints.value.push(point);

        runPolyline.value.points.push({ latitude: workLat, longitude: workLng });

        updateMapPolyline();

        if (currentMode.value === 'normal') {
           normalProgress.value = Math.min(100, ((distance.value/1000) / dailyTarget.value) * 100);
        } else if (currentMode.value === 'police') {
           policeProgress.value = Math.min(100, (distance.value / policeTargetDistance.value) * 100);
        }
        maybeEstimateStepsFromDistance();
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
        const runGpsSpeedWarmup = !hasReliableGpsMovement() && duration.value < 15 && distance.value < 28;
        currentSpeed.value = runGpsSpeedWarmup ? 0 : speedVal;

        updateLocationLogic(newLat, newLng, speedVal, res);
        lastTs = Date.now();
    }).catch(err => {
        console.warn('H5 Polling failed', err);
    });
  }, 1000);
  // #endif
  // #ifdef MP-WEIXIN
  // 鎭睆/鍒囧悗鍙帮細椤诲厛 startLocationUpdate锛屽啀 startLocationUpdateBackground锛沵anifest requiredBackgroundModes + 鐢ㄦ埛鎺堟潈
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
  /** 椤诲湪 startLocationUpdate 鎴愬姛涔嬪悗鍐嶈皟 startLocationUpdateBackground锛涚姝㈠厛鍗°€屽悗鍙板畾浣嶆巿鏉冦€嶅啀寮€鍓嶅彴锛屽惁鍒欓儴鍒嗙湡鏈哄叏绋嬫棤 onLocationChange銆侀噷绋?璁℃椂涓?0 */
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
              uni.showToast({ title: '鍚庡彴瀹氫綅鏈紑鍚紝鍓嶅彴浠嶄細璁板綍杞ㄨ抗', icon: 'none', duration: 2200 });
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
  // 閮ㄥ垎鐪熸満 startLocationUpdate 鎴愬姛浣嗛暱鏃堕棿鏃?onLocationChange锛岀敤杞鍏滃簳
  wxLocationWatchdogTimer = setTimeout(() => {
    wxLocationWatchdogTimer = null;
    if (!isRunning.value || h5LocationTimer) return;
    // 鏃ф潯浠?trajectory<=2锛欸PS 鎶栧姩澶氱偣鍚庢案杩滀笉瑙﹀彂鍏滃簳锛屽鑷村叏绋?0
    if (distance.value < 8) {
      console.log('WX: watchdog starting location poll fallback');
      startPollFallback();
    }
  }, 4000);
  // 涓?onLocationChange 骞惰锛歮ap 椤?setInterval 甯歌鑺傛祦鍒板仠琛紝鐢?setTimeout 閫掑綊锛涙瘡鎷嶅厛鍚屾澧欓挓鏃堕暱锛岄伩鍏嶄粎闈犺窇姝ユ椂閽熸椂鐣岄潰涓€鐩?0
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
        // startPollFallback 宸插垏鍒?h5LocationTimer 杞鏃讹紝鍕垮啀鎸?wx 杈呭姪瀹氭椂鍣紝閬垮厤鍙岄€氶亾閲嶅
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
  // 鏈叧闂悗鍙版寔缁畾浣嶆椂锛岄儴鍒嗘満鍨嬬浜屾 startLocationUpdate 寮傚父銆佸叏绋嬫棤鐐癸紙鏃堕暱/閲岀▼涓€鐩?0锛?
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
  runLocationSmooth = null;
  lastRawLocationSample = null;
};

// 2. 璺戞鏍稿績閰嶇疆
const currentMode = ref('normal'); // normal-鏅€?police-璀﹀姟 campus-鏍″洯
const isRunning = ref(false);
const duration = ref(0);
/** 寰俊灏忕▼搴?map 椤靛父瑙?setInterval 琚妭娴?鍋滆〃锛岀敤澧欓挓 + 鍒嗘鍩哄噯淇濊瘉鏃堕暱涓庡績鐜囧彲鏇存柊 */
const runActiveBaseSec = ref(0);
const runSegmentStartMs = ref(0);
const distance = ref(0); // 宸茶窇璺濈锛堢背锛?
const distanceToCheckpoint = ref('---');
const isReach = ref(false);
const stepCount = ref(0);
const heartRate = ref(80);
const currentSpeed = ref(0); // 瀹炴椂閫熷害 m/s
const maxSpeed = ref(0); // 鏈€澶ч€熷害 m/s
// 璀﹀姟涓撻」锛坱ickPoliceFinishHint 渚濊禆锛岄』鏃╀簬璺戞鏃堕挓鍑芥暟锛?
const policeTargetDistance = ref(2000); // 鍥哄畾2000绫?
const policeTargetPace = ref(6.5); // 杈炬爣閰嶉€燂細6.5鍒嗛挓/鍏噷锛堢敺鐢熸爣鍑嗭級
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

/** 寰俊鐪熸満 map 鍦烘櫙涓嬩紭鍏堢敤 setTimeout 閫掑綊锛岄伩鍏?setInterval 瀹屽叏涓嶈Е鍙?*/
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

// 璁＄畻褰撳墠閰嶉€燂紙鍒嗛挓/鍏噷锛夛細閲岀▼灏氱煭鏃剁敤鐬椂閫熷害鎺ㄧ畻锛岄伩鍏嶄竴鐩存樉绀?0
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
// 瀹炴椂閫熷害 (km/h)锛氬紑璺戝悗鐭椂鍐呬笉灞曠ず GPS 鎺ㄧ畻鍊硷紱鏃犳鏁颁笖閲岀▼鍙枒鏃朵笉灞曠ず锛屾姂鍒堕潤姝㈡紓绉?
const currentSpeedKmh = computed(() => {
  if (!isRunning.value) return '0.0';
  if (duration.value < 12 && distance.value < 20) {
    return '0.0';
  }
  if (!hasReliableGpsMovement() && currentSpeed.value < 0.2) {
    return '0.0';
  }
  const v = currentSpeed.value * 3.6;
  if (v < 0.2) return '0.0';
  return v.toFixed(1);
});
// 骞冲潎閫熷害 (km/h)锛氶噷绋嬪皻鐭垨寮€璺戜笉涔呮椂缃?0锛涙棤姝ユ暟鏃舵殏涓嶅睍绀哄钩鍧囬€熷害锛岄伩鍏嶄笌婕傜Щ閲岀▼涓€璧疯瀵?
const avgSpeedKmh = computed(() => {
  if (!isRunning.value) return '0.0';
  if (duration.value < 12 || duration.value === 0) return '0.0';
  if (duration.value < 50 && distance.value < 40) return '0.0';
  if (!hasReliableGpsMovement() && distance.value < 40) return '0.0';
  return ((distance.value / 1000) / (duration.value / 3600)).toFixed(1);
});

// Listener for custom location selection
uni.$on('onLocationChosen', (res) => {
  processSelectedLocation(res);
});

// 4. 瀹氫綅浼樺寲锛堝惈鏉冮檺鐢宠+鏍″洯鍥存爮锛?
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
  /** 鍐峰惎鍔ㄦ椂绔嬪埢 getLocation 甯告棤鍥炶皟锛涙巿鏉?宸叉巿鏉冨悗 nextTick + 鐭欢杩熷啀鎷夊彇锛屼笌銆岄噸杩涘皬绋嬪簭灏卞ソ銆嶅悓绫婚棶棰?*/
  const scheduleWxInitialLocate = () => {
    nextTick(() => {
      setTimeout(() => {
        if (!isPageActive) return;
        doGetLocation();
      }, 340);
    });
  };
  uni.getSetting({
    success: (st) => {
      const granted = st.authSetting && st.authSetting['scope.userLocation'] === true;
      if (granted) {
        scheduleWxInitialLocate();
        return;
      }
      uni.authorize({
        scope: 'scope.userLocation',
        success: () => scheduleWxInitialLocate(),
        fail: () => {
          locationState.value = 'fail';
          uni.showModal({
            title: '权限申请',
            content: '需要定位权限才能使用打卡、跑步功能，请前往设置开启',
            confirmText: '去设置',
            success: (res) => {
              if (res.confirm) uni.openSetting();
            }
          });
        }
      });
    },
    fail: () => {
      uni.authorize({
        scope: 'scope.userLocation',
        success: () => scheduleWxInitialLocate(),
        fail: () => {
          locationState.value = 'fail';
          uni.showModal({
            title: '权限申请',
            content: '需要定位权限才能使用打卡、跑步功能，请前往设置开启',
            confirmText: '去设置',
            success: (res) => {
              if (res.confirm) uni.openSetting();
            }
          });
        }
      });
    }
  });
  // #endif

  // #ifndef MP-WEIXIN
  // App绔拰H5绔洿鎺ヨ皟鐢╣etLocation锛岀郴缁熶細鑷姩澶勭悊鏉冮檺璇锋眰
  doGetLocation();
  // #endif
};

const handleLocationSuccess = (res) => {
  lastLocationFixWasStale.value = false;
  lat.value = res.latitude;
  lng.value = res.longitude;
  
  // Cache location for faster load next time
  uni.setStorageSync('lastLocation', { lat: res.latitude, lng: res.longitude });

  refreshMarkers();
  // 鏍″洯鍥存爮锛堜粎鏍″洯鎵撳崱鐢級
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
  let msg = '瀹氫綅澶辫触';
  let showSettings = false;

  // getCurrentLocation 澶辫触鏃跺彲鑳芥槸鍖呰瀵硅薄锛岀湡瀹?errMsg 鍦?originalErr
  const raw = err?.originalErr || err;
  const errMsg = (raw && raw.errMsg) || err?.message || '';
  if (errMsg.includes('privacy') || errMsg.includes('闅愮')) {
    msg = '需先同意小程序隐私保护指引。请返回首页同意，或重新进入本页后再试。';
  } else if (errMsg.includes('auth') || errMsg.includes('denied') || errMsg.includes('permission')) {
    msg = '定位权限被拒绝，请去设置开启';
    showSettings = true;
  } else if (errMsg.includes('service') || errMsg.includes('unavailable')) {
    msg = '瀹氫綅鏈嶅姟涓嶅彲鐢紝璇锋鏌PS';
  }

  // #ifdef H5
  if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
    msg = 'H5瀹氫綅闇€HTTPS';
  }
  // #endif

  if (showSettings) {
     uni.showModal({
       title: '鏉冮檺鎻愮ず',
       content: msg,
       confirmText: '去设置',
       success: (res) => {
         if (res.confirm) uni.openSetting();
       }
     });
  } else {
     uni.showToast({ title: msg, icon: 'none', duration: 3000 });
  }
  
  // 鏇存柊鐘舵€佷负澶辫触
  locationState.value = 'fail';
};

const doGetLocation = async () => {
  if (locationPromise) return locationPromise;

  locationPromise = (async () => {
    const raceGetLocation = () => {
      const locateMs = 22000;
      return Promise.race([
        getCurrentLocation(),
        new Promise((_, reject) => {
          setTimeout(() => {
            reject({
              success: false,
              type: 'timeout',
              message: 'Location timeout',
              originalErr: { errMsg: 'getLocation:fail outer timeout' }
            });
          }, locateMs);
        })
      ]);
    };

    const lastLoc = uni.getStorageSync('lastLocation');
    if (lastLoc) {
      lat.value = lastLoc.lat;
      lng.value = lastLoc.lng;
      refreshMarkers();
    } else {
      uni.showLoading({ title: '定位中...' });
    }

    locationState.value = 'locating';

    try {
      let res;
      // #ifdef MP-WEIXIN
      try {
        res = await raceGetLocation();
      } catch (e1) {
        if (isPageActive) {
          await new Promise((r) => setTimeout(r, 520));
          res = await raceGetLocation();
        } else {
          throw e1;
        }
      }
      // #endif
      // #ifndef MP-WEIXIN
      res = await raceGetLocation();
      // #endif

      if (!isPageActive) {
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

      if (res && res.success) {
        locationState.value = 'success';
        handleLocationSuccess(res);
        refreshMarkers();
        uni.showToast({ title: '定位成功', icon: 'none' });
      } else {
        throw res || { originalErr: { errMsg: 'getLocation:fail unknown' } };
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
        uni.showToast({ title: '刷新定位失败，暂用上次位置，请到室外后重试', icon: 'none', duration: 2800 });
        locationState.value = 'success';
      }
    } finally {
      uni.hideLoading();
      locationPromise = null;
    }
  })();

  return locationPromise;
};

const handleRelocate = () => {
    uni.showLoading({ title: '閲嶆柊瀹氫綅...' });
    locationState.value = 'locating';
    // 寮哄埗娓呴櫎 loading
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
  switch (locationState.value) {
    case 'locating':
      return hasPlausibleCoords() ? '正在刷新位置…' : '正在定位…';
    case 'success':
      return lastLocationFixWasStale.value ? '已用上次位置，点击地图可重定位' : '';
    case 'fail':
      return '定位失败，请到室外开阔处或检查定位权限';
    default:
      return '等待定位';
  }
});

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

  uni.showToast({ title: `宸查攣瀹氾細${newCheckpoint.name}`, icon: 'success' });
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
          title: '鎻愮ず',
          content: '您选择的地点不在校园打卡点范围内，是否仍要设为目标？（无法进行有效打卡）',
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

// 6. 娣诲姞鎵撳崱鐐规爣璁?
const addCheckpointMarker = (lat, lng, name) => {
  checkpointMarker.value = {
    id: 1,
    latitude: lat,
    longitude: lng,
    title: name,
    iconPath: '/static/checkpoint.png',
    width: 40,
    height: 40,
    zIndex: 70,
    anchor: { x: 0.5, y: 1 },
    callout: {
      content: name || '打卡点',
      color: '#333333',
      fontSize: 12,
      borderRadius: 6,
      bgColor: '#fff7e6',
      padding: 6,
      display: 'BYCLICK',
      borderColor: '#ff9800',
      borderWidth: 1
    }
  };
  refreshMarkers();
};

// 7. 鍒囨崲璺戞妯″紡锛堟櫘閫?璀﹀姟/鏍″洯锛?
const switchMode = (mode) => {
  if (taskRunLocked.value) {
    uni.showToast({ title: '浠诲姟璺戞璇蜂娇鐢ㄤ笓椤硅窇椤甸潰', icon: 'none' });
    return;
  }
  const wasRunning = isRunning.value;
  const hadStepListener = !!accelerometerCallback;
  const hadLocTracking = !!(locationCallback || h5LocationTimer || wxRunAssistTimer);
  // 鍒囨崲妯″紡鏃堕噸缃窇姝ョ姸鎬侊紱鏈紑璺戞椂涓嶈鍙嶅 stop 鍔犻€熷害/鎸佺画瀹氫綅锛堝噺灏戞帶鍒跺彴鍣煶锛屼篃閬垮厤骞叉壈妯℃嫙鍣級
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
  runStartMarker.value = null;
  runEndMarker.value = null;
  runLocationSmooth = null;
  gpsAcceptedPointCount = 0;
  lastRawLocationSample = null;
  resetRunMotionEvidence();
  if (mode === 'campus' && checkpoint.value && checkpoint.value.lat && checkpoint.value.lng) {
    checkpointMarker.value = {
      id: 1,
      latitude: checkpoint.value.lat,
      longitude: checkpoint.value.lng,
      title: checkpoint.value.name,
      iconPath: '/static/checkpoint.png',
      width: 34,
      height: 34,
      anchor: {
        x: 0.5,
        y: 1
      }
    };
  } else {
    checkpointMarker.value = null;
  }
  refreshMarkers();
  updateMapPolyline();
  currentMode.value = mode;
};

// 8. 姝ユ暟缁熻锛堝姞閫熷害浼犳劅鍣級
// 璁℃锛氭尝宄?+ 闃叉姈銆傞儴鍒嗘満鍨?鐜涓嬭繑鍥炵殑鏄€屼笉鍚噸鍔涖€嶇殑绾挎€у姞閫熷害锛堥潤姝㈡帴杩?0锛夛紝鑻ュ啀寮鸿褰掍竴鍒?1g 浼氭案杩滆揪涓嶅埌闃堝€硷紱鏁呯敤銆屽惈閲嶅姏鏃?|妯￠暱鈭?g|銆嶄笌銆岀函绾挎€ф椂妯￠暱銆嶇粺涓€鐨?m/s虏 寮哄害淇″彿銆?
    let isStepActive = false;
    let lastStepTime = 0;
    let accelMagPrev = null;
    let accelBaseline = null;
    let linearMagPrev = 0;
    /** 涓婇槇鍊硷細涓€娆℃槑鏄惧啿鍑伙紙鍚檭鎵嬫満锛夊簲鑳借秴杩囷紱涓嬮槇鍊奸』浣庝簬涓婇槇鍊硷紝涓斾笉瀹滆繃浣庯紝鍚﹀垯鍣０涓嬫棤娉曞洖钀姐€佷細鍗℃鍙兘璁?1 姝?*/
    const STEP_SIGNAL_UP_MS2 = 0.24;
    const STEP_SIGNAL_DOWN_MS2 = 0.10;
    const MIN_STEP_INTERVAL = 220;
    const RESET_TIMEOUT = 900;

    // 鍚姩姝ユ暟缁熻 - 甯﹂噸璇曟満鍒?
    const startStepCount = (retryCount = 0) => {
      const MAX_RETRIES = 3;
      console.log('=== 寮€濮嬪惎鍔ㄦ鏁扮粺璁?(閲嶈瘯娆℃暟:', retryCount, ') ===');
      
      // 鍏堢‘淇濆仠姝箣鍓嶇殑鐩戝惉锛屼娇鐢ㄥ洖璋冪‘淇濆畬鎴愬悗鍐嶅惎鍔?
      const stopAndStart = () => {
        uni.stopAccelerometer({
          success: () => {
            console.log('鉁?浼犳劅鍣ㄥ凡鍋滄');
            // 寤惰繜200ms纭繚浼犳劅鍣ㄥ畬鍏ㄩ噴鏀?
            setTimeout(() => {
              startAccelerometerWithRetry(retryCount);
            }, 200);
          },
          fail: (err) => {
            console.warn('鍋滄浼犳劅鍣ㄥけ璐ワ紝缁х画灏濊瘯鍚姩:', err);
            // 鍗充娇鍋滄澶辫触涔熷皾璇曞惎鍔?
            setTimeout(() => {
              startAccelerometerWithRetry(retryCount);
            }, 200);
          }
        });
      };
      
      stopAndStart();
    };
    
    // 甯﹂噸璇曠殑鍚姩浼犳劅鍣細浠呭湪 start 鎴愬姛鍚庡啀娉ㄥ唽鐩戝惉锛岄伩鍏嶅け璐ラ噸璇曟椂閲嶅 on 瀵艰嚧鍐茬獊锛涢檷閲囨牱鎻愰珮閮ㄥ垎鏈哄瀷/寰俊鐜鍏煎鎬?
    const startAccelerometerWithRetry = (retryCount) => {
      const MAX_RETRIES = 3;
      const intervals = ['game', 'normal', 'ui'];
      const interval = intervals[Math.min(retryCount, intervals.length - 1)];

      const bindAccelerometerListener = () => {
        accelMagPrev = null;
        accelBaseline = null;
        linearMagPrev = 0;
        if (accelerometerCallback) {
          try {
            uni.offAccelerometerChange(accelerometerCallback);
          } catch (e) {
            console.warn('offAccelerometerChange:', e);
          }
        }
        accelerometerCallback = (res) => {
          const mag = Math.sqrt(res.x * res.x + res.y * res.y + res.z * res.z);
          if (!Number.isFinite(mag)) return;
          // 鍚噸鍔涳細|妯￠暱鈭?g|锛涘急妯￠暱锛氱敤绾挎€у己搴︺€傛憞鏅冩椂妯￠暱甯镐粛鎺ヨ繎 1g锛屽繀椤诲彔鍔犲抚闂村彉鍖栭噺鎵嶈兘绋冲畾瑙﹀彂
          accelBaseline = accelBaseline == null ? mag : (accelBaseline * 0.82 + mag * 0.18);
          const gravOrLin = mag >= 3.5 ? Math.abs(mag - accelBaseline) : mag;
          const jerk = accelMagPrev != null ? Math.abs(mag - accelMagPrev) : 0;
          accelMagPrev = mag;
          const linearMag = gravOrLin;
          const signal = Math.max(linearMag * 0.95, jerk * 0.75, Math.abs(linearMag - linearMagPrev) * 1.1);
          linearMagPrev = linearMag;

          const now = Date.now();

          if (isStepActive && now - lastStepTime > RESET_TIMEOUT) {
            isStepActive = false;
          }

          if (!isStepActive && signal > STEP_SIGNAL_UP_MS2) {
            if (now - lastStepTime > MIN_STEP_INTERVAL) {
              stepCount.value += 1;
              console.log('👣 步数+1', stepCount.value, 'signal≈', signal.toFixed(2), 'mag≈', mag.toFixed(2));
              noteStepMotion(now);
              lastStepTime = now;
              isStepActive = true;
            }
          } else if (isStepActive && signal < STEP_SIGNAL_DOWN_MS2) {
            isStepActive = false;
          }
        };
        uni.onAccelerometerChange(accelerometerCallback);
        console.log('=== 姝ユ暟缁熻鐩戝惉宸茶缃?(interval=' + interval + ') ===');
      };

      uni.startAccelerometer({
        interval,
        success: () => {
          console.log('✅ 加速度传感器启动成功');
          bindAccelerometerListener();
          isStepActive = false;
          accelMagPrev = null;
          accelBaseline = null;
          linearMagPrev = 0;
          resetRunMotionEvidence();
          lastStepTime = Date.now();
        },
        fail: (err) => {
          console.error('鉂?鍔犻€熷害浼犳劅鍣ㄥ惎鍔ㄥけ璐?', err);

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
            console.log('馃攧 浼犳劅鍣ㄥ惎鍔ㄥけ璐ワ紝鍑嗗閲嶈瘯:', errMsg);
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
              title: '姝ユ暟缁熻鍚姩澶辫触',
              content:
                '无法启动加速度传感器，步数将无法统计。请在系统设置与微信「小程序」权限中允许运动/传感器相关权限；若已开启，请结束小程序进程后重试。',
              showCancel: false
            });
          }
        }
      });
    };

const stopStepCount = () => {
  if (!accelerometerCallback) {
    resetRunMotionEvidence();
    return;
  }
  uni.stopAccelerometer();
  uni.offAccelerometerChange(accelerometerCallback);
  accelerometerCallback = null;
  accelMagPrev = null;
  accelBaseline = null;
  linearMagPrev = 0;
  resetRunMotionEvidence();
  isStepActive = false;
};

/**
 * 浜鸿劯鎷嶇収 / chooseMedia 鍒氱粨鏉熸椂锛岄儴鍒嗗井淇＄湡鏈洪渶杩囦竴灏忔鍐嶈皟 startLocationUpdate锛屽惁鍒?onLocationChange 涓嶅洖璋冿紙姝ユ暟銆佸閽熴€侀噷绋嬪潎涓嶆定锛夈€?
 * 娴嬭瘯鍙嶉銆岀涓€娆℃媿鐓у悗寮€濮嬭窇姝ョ粺璁′笉宸ヤ綔锛涚偣缁撴潫璺戞鍐嶅彇娑堝悗姝ｅ父銆嶅嵆鍏稿瀷鏃跺簭闂銆?
 */
const beginRunTrackingAfterFaceDefer = () => {
  const go = () => {
    if (!isRunning.value) return;
    startRealLocationTracking();
    startStepCount();
    scheduleRunClock();
  };
  nextTick(() => {
    setTimeout(go, 400);
  });
};

// 9. 蹇冪巼鏇存柊+棰勮
const updateHeartRate = () => {
  heartRate.value = 80 + Math.floor(duration.value / 10);
  if (heartRate.value > 180) {
    uni.showModal({
      title: '鍋ュ悍棰勮',
      content: `当前心率过高（${heartRate.value}次/分），建议降速休息`,
      showCancel: false
    });
  }
};

// 10. 寮€濮嬭窇姝ワ紙鍒嗕笁绉嶆ā寮忥級
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
  gpsAcceptedPointCount = 0;
  resetRunMotionEvidence();
  
  // Clear previous trajectory
  runPolyline.value.points = [];
  trajectoryPoints.value = [];
  runEndMarker.value = null;
  runLocationSmooth = null;
  lastRawLocationSample = null;

  // Add start point immediately to avoid delay in drawing line
  if (lat.value && lng.value) {
    const startPoint = { latitude: lat.value, longitude: lng.value, timestamp: Date.now(), speed: 0 };
    trajectoryPoints.value.push(startPoint);
    runPolyline.value.points.push({ latitude: lat.value, longitude: lng.value });
    runStartMarker.value = createRunPointMarker(2, lat.value, lng.value, '起', '#20C997');
    refreshMarkers();
    updateMapPolyline();
  }
  return true;
};

// 浜鸿劯楠岃瘉锛氶€夊浘/鎷嶇収锛堢浉鍐?鐩告満鍦ㄥ井淇″叕浼楀钩鍙般€岄殣绉佷繚鎶ゆ寚寮曘€嶄腑澹版槑鐢ㄩ€旓紱鍕垮啓鍏?app.json 鐨?requiredPrivateInfos锛岃瀛楁浠呭厑璁稿畾浣嶇被鐧藉悕鍗曪級
const handleFacePickFail = (resolve, err) => {
  const errMsg = (err && err.errMsg) ? String(err.errMsg) : '';
  if (errMsg.includes('cancel')) {
    resolve(false);
    return;
  }
  if (errMsg.includes('privacy') || errMsg.includes('闅愮')) {
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
    title: '鎷嶇収鎴栭€夊浘澶辫触',
    content: errMsg
      ? `${errMsg}\n\n可稍后重试或改用相册选图。未完成人脸验证无法开始或结束跑步。`
      : '请检查相机与相册权限、存储空间是否正常，或稍后重试。未完成人脸验证无法开始或结束跑步。',
    showCancel: false,
    confirmText: '知道了'
  });
  resolve(false);
};

const finishFaceCamera = (result) => {
  const resolver = faceCameraResolve;
  faceCameraResolve = null;
  showFaceCamera.value = false;
  faceCameraBusy.value = false;
  faceCameraErrorText.value = 'Camera unavailable, please retry';
  faceCameraContext = null;
  if (resolver) resolver(result);
};

const cancelFaceCamera = () => finishFaceCamera(false);

const handleFaceCameraReady = () => {
  // #ifdef MP-WEIXIN
  faceCameraContext = uni.createCameraContext('faceCamera');
  // #endif
  faceCameraErrorText.value = '';
};

const handleFaceCameraError = (err) => {
  console.error('Inline face camera error:', err);
  faceCameraErrorText.value = 'Camera unavailable, please retry';
};

const openInlineFaceCamera = (phase) => {
  faceCapturePhase.value = phase;
  faceCameraBusy.value = false;
  faceCameraErrorText.value = '';
  showFaceCamera.value = true;
  return new Promise((resolve) => {
    faceCameraResolve = resolve;
    nextTick(() => {
      // #ifdef MP-WEIXIN
      faceCameraContext = uni.createCameraContext('faceCamera');
      // #endif
    });
  });
};

const uploadFaceCapture = async (filePath, phase, resolve) => {
  if (!filePath) {
    uni.showModal({
      title: 'No photo captured',
      content: 'Face verification was not completed. Please retake the photo.',
      showCancel: false,
      confirmText: 'OK'
    });
    resolve(false);
    return;
  }
  try {
    uni.showLoading({ title: '涓婁紶楠岃瘉鐓х墖...' });
    const uploadRes = await uploadFile(filePath);
    uni.hideLoading();

    const url = uploadRes?.url || uploadRes?.path || uploadRes?.filePath || uploadRes;
    if (!url) {
      uni.showModal({
        title: 'Upload failed',
        content: 'Photo upload failed. Please check the server and network, then try again.',
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
    const msg = e?.message || e?.detail || 'Photo upload failed, please try again later';
    uni.showModal({
      title: 'Upload failed',
      content: msg,
      showCancel: false
    });
    resolve(false);
  }
};

const captureFaceFromInlineCamera = () => {
  // #ifndef MP-WEIXIN
  return;
  // #endif
  // #ifdef MP-WEIXIN
  if (faceCameraBusy.value) return;
  if (!faceCameraContext) {
    faceCameraErrorText.value = 'Camera unavailable, please retry';
    return;
  }
  faceCameraBusy.value = true;
  faceCameraErrorText.value = '';
  faceCameraContext.takePhoto({
    quality: 'medium',
    success: async (res) => {
      const done = (ok) => finishFaceCamera(ok);
      await uploadFaceCapture(res?.tempImagePath || '', faceCapturePhase.value, done);
    },
    fail: (err) => {
      faceCameraBusy.value = false;
      console.error('Inline face capture fail:', err);
      faceCameraErrorText.value = 'Capture failed, please retry';
    }
  });
  // #endif
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

        const uploadChosen = async (filePath) => uploadFaceCapture(filePath, phase, resolve);

        // #ifdef MP-WEIXIN
        openInlineFaceCamera(phase).then((ok) => {
          if (ok === false) {
            resolve(false);
            return;
          }
          resolve(ok);
        });
        // #endif
        // #ifndef MP-WEIXIN
        uni.chooseImage({
          count: 1,
          sizeType: ['compressed'],
          sourceType: ['camera'],
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

// 鏅€氳窇姝ワ紙鏃犲浐瀹氱洰鏍囷級
const startNormalRun = async () => {
  if (locationState.value !== 'success') {
    uni.showToast({ title: '瀹氫綅鏈垚鍔燂紝璇风◢鍊欐垨鐐瑰嚮鍦板浘鏃佸畾浣嶆寜閽埛鏂板悗鍐嶈瘯', icon: 'none' });
    doGetLocation();
    return;
  }
  if (lastLocationFixWasStale.value) {
    uni.showToast({
      title: '褰撳墠涓哄巻鍙插畾浣嶏紝寤鸿鍏堢偣鍦板浘鏃併€屽畾浣嶃€嶅埛鏂版垨鍒板澶栧啀璺戯紝浠ュ厤閲岀▼缁熻鍋忔櫄',
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

// 涓撻」璁粌锛堝浐瀹?000绫筹紝鎸夎揪鏍囬厤閫熻窇锛?
const startPoliceRun = async () => {
  if (locationState.value !== 'success') {
    uni.showToast({ title: '瀹氫綅鏈垚鍔燂紝璇风◢鍊欐垨鐐瑰嚮鍦板浘鏃佸畾浣嶆寜閽埛鏂板悗鍐嶈瘯', icon: 'none' });
    doGetLocation();
    return;
  }
  if (lastLocationFixWasStale.value) {
    uni.showToast({
      title: '褰撳墠涓哄巻鍙插畾浣嶏紝寤鸿鍏堢偣鍦板浘鏃併€屽畾浣嶃€嶅埛鏂版垨鍒板澶栧啀璺戯紝浠ュ厤閲岀▼缁熻鍋忔櫄',
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

// 鏍″洯鎵撳崱
const startCampusRun = async () => {
  if (locationState.value !== 'success') {
    uni.showToast({ title: '瀹氫綅鏈垚鍔燂紝璇风◢鍊欐垨鐐瑰嚮鍦板浘鏃佸畾浣嶆寜閽埛鏂板悗鍐嶈瘯', icon: 'none' });
    doGetLocation();
    return;
  }
  if (lastLocationFixWasStale.value) {
    uni.showToast({
      title: '褰撳墠涓哄巻鍙插畾浣嶏紝寤鸿鍏堢偣鍦板浘鏃併€屽畾浣嶃€嶅埛鏂版垨鍒板澶栧啀璺戯紝浠ュ厤閲岀▼缁熻鍋忔櫄',
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

// 缁撴潫璺戞鏃惰嫢鐢ㄦ埛鍙栨秷浜鸿劯楠岃瘉锛氭仮澶嶈鏃躲€佽姝ヤ笌瀹氫綅锛堥伩鍏嶅凡鍋滆〃鍗存棤娉曠户缁窇锛?
const resumeRunAfterEndFaceCancelled = () => {
  runEndMarker.value = null;
  refreshMarkers();
  runActiveBaseSec.value = duration.value;
  runSegmentStartMs.value = Date.now();
  isRunning.value = true;
  clearRunTickTimer();
  beginRunTrackingAfterFaceDefer();
};

// 鎻愪氦璺戞璁板綍骞惰烦杞粨绠楅〉
const redirectToRunResult = () => {
  uni.redirectTo({
    url: '/pages/result/result?useStorage=true',
    fail: (err) => {
      console.error('Navigate failed:', err);
      uni.showToast({ title: '椤甸潰璺宠浆澶辫触', icon: 'none' });
    }
  });
};

/** 璇诲彇鏈湴璺戞鏉★紙鍏煎瀛楃涓插瓨鍌級 */
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

/** 浠婃棩姒傝 / 鍘嗗彶鏉′緷璧栨湰鍦?runRecordsList锛涙鍓嶄粠鏈啓鍏ュ鑷翠竴鐩翠负 0 */
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
  uni.showLoading({ title: '姝ｅ湪鏍搁獙杩愬姩鏁版嵁...' });
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

// 11. 缁撴潫璺戞锛堢粺涓€閫昏緫锛?
const stopRun = async () => {
  if (!isRunning.value) return;
  syncRunElapsedDisplay();
  if (hasPlausibleCoords()) {
    runEndMarker.value = createRunPointMarker(3, lat.value, lng.value, '终', '#E53935');
    refreshMarkers();
  }
  isRunning.value = false;
  clearRunTickTimer();
  stopStepCount();
  stopRealLocationTracking();

  const token = uni.getStorageSync('token');
  if (!token) {
    uni.showToast({ title: '璇峰厛鐧诲綍', icon: 'none' });
    setTimeout(() => {
      uni.reLaunch({ url: '/pages/login/login' });
    }, 800);
    return;
  }

  // 缁撴潫鍓嶈繘琛屼竴娆′汉鑴搁獙璇佹媿鐓?
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

  const filtM = distance.value;
  /** 闈炰换鍔¤窇锛氫笂鎶ラ噷绋嬩笌杞ㄨ抗鍑犱綍闀垮榻愶紙闃叉护娉㈠亸浣庯級锛涗换鍔¤窇浠嶄互绔笂绱涓哄噯锛岄伩鍏嶄笌浠诲姟瑙勫垯鍐茬獊 */
  let reportM = filtM;
  if (!taskId.value && trajectoryPoints.value.length >= 2) {
    const trajM = computeTrajectoryPathLengthM(trajectoryPoints.value);
    const relaxedTraj = trajM * 0.94;
    reportM = Math.max(filtM, Math.min(relaxedTraj, filtM * 1.28));
  }
  const distKm = reportM / 1000;
  const durSec = Math.max(duration.value, 1);
  const paceFromDist = distKm > 1e-6 ? (durSec / 60) / distKm : Number(currentPace.value) || 0;
  const paceStr = Number.isFinite(paceFromDist) && paceFromDist > 0 ? paceFromDist.toFixed(1) : String(currentPace.value || '0');
  const reportedStepCount = stepCount.value;
  const durOk = !taskMinDurationSec.value || duration.value >= taskMinDurationSec.value;
  const distOk = !policeTargetDistance.value || reportM >= policeTargetDistance.value;
  const taskMetPreview = !taskId.value || (distOk && durOk);

  const runData = {
    type: 'run',
    source: taskId.value ? 'task' : 'free',
    started_at: new Date(Date.now() - duration.value * 1000).toISOString(),
    ended_at: new Date().toISOString(),
    metrics: {
      distance: distKm,
      duration: duration.value,
      pace: paceStr,
      step_count: reportedStepCount,
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

  // 娣诲姞璧疯窇涓庣粨鏉熶汉鑴哥収鐗囪瘉鎹紙濡傛湁锛?
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
    const msg = error?.message || error?.detail || String(error) || '缃戠粶鎴栨湇鍔″櫒閿欒锛岃閲嶈瘯';
    uni.showModal({
      title: '鎻愪氦澶辫触',
      content: msg,
      confirmText: '閲嶈瘯',
      cancelText: '寮哄埗缁撴潫',
      success: (modalRes) => {
        if (modalRes.confirm) {
          submitCurrentRunToServer(runData).catch((e2) => {
            uni.showToast({
              title: e2?.message || e2?.detail || '閲嶈瘯澶辫触锛岃绋嶅悗鍐嶈瘯',
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
  background-color: rgba(0, 0, 0, 0.65);
  padding: 10rpx 24rpx;
  border-radius: 30rpx;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  max-width: 90%;
}
.status-text {
  color: #ffffff;
  font-size: 24rpx;
  line-height: 1.4;
  text-align: center;
}
.map-legend {
  position: absolute;
  left: 16rpx;
  bottom: 16rpx;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 12rpx;
  padding: 12rpx 16rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.12);
}
.legend-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 8rpx;
}
.legend-row:last-child {
  margin-bottom: 0;
}
.legend-pin {
  width: 20rpx;
  height: 20rpx;
  border-radius: 50%;
  margin-right: 10rpx;
}
.legend-pin-me {
  background: #20c997;
  border: 3rpx solid #fff;
  box-shadow: 0 0 0 2rpx #20c997;
}
.legend-pin-start {
  background: #20c997;
}
.legend-line-sample {
  width: 28rpx;
  height: 6rpx;
  border-radius: 3rpx;
  background: #1e88e5;
  margin-right: 10rpx;
}
.legend-txt {
  font-size: 22rpx;
  color: #333;
  line-height: 1.2;
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

/* 鏂板椤堕儴鏍峰紡 */
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

/* 鎺ㄨ崘璺嚎鏍峰紡 */
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
/* 鎼滅储鏍忎粎鏍″洯妯″紡鏄剧ず */
.search-bar {
  margin-bottom: 20rpx;
}
.map-select-panel {
  width: 100%;
}
.map-select-btn {
  display: flex;
  align-items: center;
  gap: 18rpx;
  min-height: 108rpx;
  background: linear-gradient(135deg, #1fc48d, #22c55e);
  border-radius: 18rpx;
  padding: 0 24rpx;
  box-shadow: 0 10rpx 24rpx rgba(32, 201, 151, 0.2);
}
.map-icon {
  width: 62rpx;
  height: 62rpx;
  line-height: 62rpx;
  text-align: center;
  font-size: 34rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
}
.map-select-copy {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.map-select-title {
  font-size: 30rpx;
  line-height: 1.2;
  color: #fff;
  font-weight: 700;
}
.map-select-desc {
  margin-top: 8rpx;
  font-size: 24rpx;
  line-height: 1.35;
  color: rgba(255, 255, 255, 0.9);
}
.map-select-arrow {
  width: 18rpx;
  height: 18rpx;
  border-color: #fff;
}
.map-select-hint {
  display: block;
  margin-top: 12rpx;
  padding: 0 8rpx;
  font-size: 24rpx;
  line-height: 1.4;
  color: #5f6b7a;
}
/* 鍦板浘 */
.map {
  width: 100%;
  height: 460rpx;
  min-height: 360rpx;
  border-radius: 16rpx;
  margin-bottom: 24rpx;
  overflow: hidden;
}
/* 妯″紡鍒囨崲锛堜笁閫変竴锛?*/
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
/* 璀﹀姟涓撻」璁″垝妯″潡 */
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
  flex-direction: column;
  align-items: flex-start;
  gap: 12rpx;
}
.info-item {
  font-size: 26rpx;
  color: #666;
  margin: 0;
  line-height: 1.6;
}
.highlight {
  color: #d81e06;
  font-weight: bold;
}
/* 閫氱敤璺戞妯″潡鏍峰紡 */
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

.face-camera-mask {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0, 0, 0, 0.92);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.face-camera-view {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.face-camera-panel {
  position: relative;
  z-index: 2;
  padding: 32rpx 28rpx calc(36rpx + env(safe-area-inset-bottom));
  background: linear-gradient(to top, rgba(0, 0, 0, 0.88), rgba(0, 0, 0, 0.3));
}

.face-camera-title {
  display: block;
  color: #fff;
  font-size: 34rpx;
  font-weight: 700;
  text-align: center;
}

.face-camera-tip {
  display: block;
  margin-top: 14rpx;
  color: rgba(255, 255, 255, 0.88);
  font-size: 26rpx;
  line-height: 1.5;
  text-align: center;
}

.face-camera-error {
  display: block;
  margin-top: 14rpx;
  color: #ffd6d6;
  font-size: 24rpx;
  text-align: center;
}

.face-camera-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18rpx;
  margin-top: 28rpx;
}

.face-camera-cancel,
.face-camera-shoot {
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 44rpx;
  font-size: 30rpx;
  border: none;
}

.face-camera-cancel {
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
}

.face-camera-shoot {
  background: #20c997;
  color: #fff;
}

@keyframes pulse {
  0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(32, 201, 151, 0.4); }
  70% { transform: scale(1.05); box-shadow: 0 0 0 20rpx rgba(32, 201, 151, 0); }
  100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(32, 201, 151, 0); }
}
</style>

