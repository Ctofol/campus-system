<template>
  <view class="run run-sport">
    <page-tab-header title="跑步" show-back theme="white" />

    <view class="run-map-section">
      <map
        v-if="isMapReady"
        id="runMap"
        class="map map-full"
        :latitude="lat"
        :longitude="lng"
        :markers="markers"
        :polyline="polyline"
        :enable-zoom="true"
        :enable-scroll="true"
        :show-compass="false"
        :min-scale="3"
        :max-scale="20"
        scale="16"
        :show-location="showMapNativeLocation"
      >
        <cover-view
          v-if="showMapTopHintBar"
          class="location-status-bar"
          :class="{ 'location-status-tappable': showMapTopHintTappable }"
          @tap="onLocationStatusBarTap"
        >
          <cover-view class="status-text">{{ mapTopHintText }}</cover-view>
        </cover-view>

        <cover-view
          v-if="!hideMapCoverLayer && !isRunning"
          class="sport-dash cover-panel"
        >
          <cover-view class="sport-dash-main">
            <cover-view class="sport-dash-label">今日里程</cover-view>
            <cover-view class="sport-dash-km-row">
              <cover-view class="sport-dash-km">{{ todayRunDistance }}</cover-view>
              <cover-view class="sport-dash-unit">公里</cover-view>
            </cover-view>
            <cover-view class="sport-dash-sub">今日 {{ todayRunCount }} 次</cover-view>
          </cover-view>
          <cover-view class="sport-dash-link" @tap="goRunHistory">
            <cover-view class="sport-dash-link-t">历史记录 ›</cover-view>
          </cover-view>
        </cover-view>

        <cover-view
          v-if="!hideMapCoverLayer && taskRunLocked && !isRunning"
          class="sport-task-hint cover-panel"
        >
          <cover-view class="sport-task-hint-t">任务跑步 · 专项模式已锁定</cover-view>
        </cover-view>

        <cover-view v-if="showMapLegend" class="map-legend cover-panel">
          <cover-view class="legend-row">
            <cover-view class="legend-pin legend-pin-me" />
            <cover-view class="legend-txt">我的位置</cover-view>
          </cover-view>
          <cover-view v-if="isRunning && trajectoryPointCount >= 2" class="legend-row">
            <cover-view class="legend-line-pace" />
            <cover-view class="legend-txt">轨迹按配速上色</cover-view>
          </cover-view>
        </cover-view>
      </map>

      <view
        v-if="!hideMapCoverLayer"
        class="sport-recenter-float"
        :style="recenterFloatStyle"
        @tap="recenterMap"
      >
        <text class="sport-recenter-icon">◎</text>
      </view>

      <view
        v-if="!hideMapCoverLayer && isRunning"
        class="run-bottom-sheet"
        :class="{
          'run-bottom-sheet--expanded': runSheetExpandProgress >= 0.55,
          'run-bottom-sheet--dragging': runSheetDragging
        }"
        :style="runSheetStyle"
      >
        <view
          class="run-sheet-handle-wrap"
          @tap.stop="toggleRunSheetExpand"
          @touchstart.stop="onRunSheetTouchStart"
          @touchmove.stop.prevent="onRunSheetTouchMove"
          @touchend.stop="onRunSheetTouchEnd"
          @touchcancel.stop="onRunSheetTouchEnd"
        >
          <view class="run-sheet-handle" />
        </view>

        <view v-if="isRunPaused" class="run-sheet-paused-chip">已暂停</view>

        <view
          class="run-sheet-body"
          @touchstart.stop="onRunSheetTouchStart"
          @touchmove.stop.prevent="onRunSheetTouchMove"
          @touchend.stop="onRunSheetTouchEnd"
          @touchcancel.stop="onRunSheetTouchEnd"
        >
          <view class="run-sheet-layer run-sheet-layer--compact" :style="runSheetCompactStyle">
            <view class="run-sheet-metric">
              <text class="run-sheet-metric-val">{{ hudDistanceKm }}</text>
              <text class="run-sheet-metric-lbl">公里</text>
            </view>
            <view class="run-sheet-metric">
              <text class="run-sheet-metric-val run-sheet-metric-val--dim">{{ formatHudDuration(duration) }}</text>
              <text class="run-sheet-metric-lbl">用时</text>
            </view>
            <view class="run-sheet-metric">
              <text class="run-sheet-metric-val run-sheet-metric-val--dim">{{ hudAvgPace }}</text>
              <text class="run-sheet-metric-lbl">配速</text>
            </view>
          </view>

          <view
            v-show="runSheetExpandProgress > 0.04"
            class="run-sheet-layer run-sheet-layer--expanded"
            :style="runSheetExpandedLayerStyle"
          >
            <text class="run-sheet-hero-val">{{ hudDistanceKm }}</text>
            <text class="run-sheet-hero-lbl">总距离（公里）</text>
            <view class="run-sheet-grid">
              <view class="run-sheet-grid-item">
                <text class="run-sheet-grid-val">{{ formatHudDuration(duration) }}</text>
                <text class="run-sheet-grid-lbl">总时长</text>
              </view>
              <view class="run-sheet-grid-item">
                <text class="run-sheet-grid-val">{{ hudAvgPace }}</text>
                <text class="run-sheet-grid-lbl">平均配速</text>
              </view>
              <view class="run-sheet-grid-item">
                <text class="run-sheet-grid-val">{{ stepCount }}</text>
                <text class="run-sheet-grid-lbl">步数</text>
              </view>
              <view class="run-sheet-grid-item">
                <text class="run-sheet-grid-val">{{ runHudCalories }}</text>
                <text class="run-sheet-grid-lbl">消耗(千卡)</text>
              </view>
            </view>
          </view>
        </view>

        <view v-if="currentMode === 'police'" class="run-sheet-extra">
          目标 {{ policeTargetKmLabel }} · 剩余 {{ (Math.max(0, policeTargetDistance - displayRunDistanceM) / 1000).toFixed(2) }}km
        </view>
        <view v-if="currentMode === 'campus'" class="run-sheet-extra">
          距打卡点 {{ distanceToCheckpoint }}m · {{ isReach ? '已到达' : '未到达' }}
        </view>
        <view v-if="runHudProgressPct > 0" class="run-sheet-progress">
          <view class="run-sheet-progress-fill" :style="{ width: runHudProgressPct + '%' }" />
        </view>

        <view class="run-sheet-controls" :style="runSheetControlsStyle">
          <view
            class="run-ctrl-side"
            hover-class="run-ctrl-hover"
            :class="{ 'run-ctrl-side--on': runControlsLocked }"
            @tap="toggleRunLock"
          >
            <text class="run-ctrl-side-icon">{{ runControlsLocked ? '🔒' : '🔓' }}</text>
            <text class="run-ctrl-side-lbl">{{ runControlsLocked ? '已锁' : '锁定' }}</text>
          </view>
          <view
            class="run-ctrl-main"
            hover-class="run-ctrl-hover"
            :class="{ 'run-ctrl-main--resume': isRunPaused }"
            @tap="toggleRunPause"
          >
            <text class="run-ctrl-main-icon">{{ isRunPaused ? '▶' : '❚❚' }}</text>
            <text class="run-ctrl-main-lbl">{{ isRunPaused ? '继续' : '暂停' }}</text>
          </view>
          <view class="run-ctrl-end" hover-class="run-ctrl-end--hover" @tap="onCompactStopTap">
            <text class="run-ctrl-end-txt">{{ stopRunLabel }}</text>
          </view>
        </view>
      </view>

      <view
        v-if="!hideMapCoverLayer && showRunPrepSheet"
        class="run-prep-sheet"
        :style="runPrepSheetStyle"
      >
        <view class="run-sheet-handle-wrap">
          <view class="run-sheet-handle" />
        </view>

        <view v-if="!taskRunLocked" class="run-prep-mode-pill">
          <view
            class="run-prep-pill-item"
            :class="{ active: currentMode === 'normal' }"
            hover-class="run-prep-pill-item--hover"
            @tap="switchMode('normal')"
          >普通跑步</view>
          <view
            v-if="hasRunTaskAvailable"
            class="run-prep-pill-item"
            :class="{ active: currentMode === 'police' }"
            hover-class="run-prep-pill-item--hover"
            @tap="switchMode('police')"
          >专项测试</view>
          <view
            class="run-prep-pill-item"
            :class="{ active: currentMode === 'campus' }"
            hover-class="run-prep-pill-item--hover"
            @tap="switchMode('campus')"
          >校园打卡</view>
        </view>
        <text v-else class="run-prep-title">{{ runPrepSheetTitle }}</text>
        <text v-if="!taskRunLocked" class="run-prep-title">{{ runPrepSheetTitle }}</text>

        <view v-if="currentMode === 'normal'" class="run-prep-body">
          <view class="run-prep-card">
            <text class="run-prep-card-head">户外跑步</text>
            <text class="run-prep-desc run-prep-desc--center">自动记录里程、轨迹与配速，结束后可提交成绩</text>
          </view>
        </view>

        <view v-else-if="currentMode === 'police'" class="run-prep-body">
          <view
            v-if="!taskRunLocked && activeRunTasks.length > 1"
            class="run-prep-task-pick"
          >
            <text class="run-prep-task-pick-hint">请选择要完成的跑步任务</text>
            <view
              v-for="t in activeRunTasks"
              :key="t.id"
              class="run-prep-task-pick-item"
              :class="{ 'run-prep-task-pick-item--active': String(taskId) === String(t.id) }"
              hover-class="run-prep-task-pick-item--hover"
              @tap="selectRunTask(t)"
            >
              <text class="run-prep-task-pick-title">{{ t.title }}</text>
              <text class="run-prep-task-pick-meta">{{ formatRunTaskMeta(t) }}</text>
            </view>
          </view>
          <view v-if="taskId" class="run-prep-card">
            <text class="run-prep-card-head">{{ teacherRunTask || '本次任务' }}</text>
            <view v-if="policeTargetDistance > 0" class="run-prep-row">
              <text class="run-prep-row-lbl">最低距离</text>
              <text class="run-prep-row-val">{{ (policeTargetDistance / 1000).toFixed(2) }} 公里</text>
            </view>
            <view v-if="taskMinDurationSec > 0" class="run-prep-row">
              <text class="run-prep-row-lbl">最低时长</text>
              <text class="run-prep-row-val">{{ formatTaskDurationLabel(taskMinDurationSec) }}</text>
            </view>
            <view v-if="policeReferencePaceLabel" class="run-prep-row">
              <text class="run-prep-row-lbl">参考配速</text>
              <text class="run-prep-row-val">{{ policeReferencePaceLabel }}</text>
            </view>
            <text v-if="taskDescription" class="run-prep-desc">{{ taskDescription }}</text>
            <text v-if="taskSubmitHint" class="run-prep-desc run-prep-desc--warn">{{ taskSubmitHint }}</text>
          </view>
          <view v-else-if="!runTasksLoading" class="run-prep-card">
            <text class="run-prep-desc run-prep-desc--center">暂无进行中的跑步任务，请先在「我的任务」查看</text>
          </view>
        </view>

        <view v-else-if="currentMode === 'campus'" class="run-prep-body">
          <view class="run-prep-select" hover-class="run-prep-select--hover" @tap="handleMapSelect">
            <text class="run-prep-select-icon">📍</text>
            <view class="run-prep-select-copy">
              <text class="run-prep-select-title">{{ checkpoint.name || '选择校园打卡点' }}</text>
              <text class="run-prep-select-desc">
                {{ checkpoint.name ? `半径约 ${checkpoint.radius || 100} 米 · 点按可更换` : '点选地图上的打卡位置' }}
              </text>
            </view>
            <text class="run-prep-select-arrow">›</text>
          </view>
        </view>

        <view
          class="run-prep-start"
          hover-class="run-prep-start--hover"
          :class="{ 'run-prep-start--disabled': !canStartFromPrepSheet }"
          @tap="onMainStartTap"
        >
          <text class="run-prep-start-txt">{{ mainStartLabel }}</text>
        </view>
      </view>
    </view>

    <view v-if="!isRunning && teacherRunTask" class="sport-teacher-task">
      <text>教师任务：{{ teacherRunTask }}</text>
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
        <text class="face-camera-tip">请正对光线、面部无遮挡；拍照后用于本次跑步起止人脸核验</text>
        <text v-if="faceCameraErrorText" class="face-camera-error">{{ faceCameraErrorText }}</text>
        <view class="face-camera-actions">
          <button class="face-camera-cancel" @click="cancelFaceCamera">取消</button>
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
import { ref, computed, watch, onUnmounted, onMounted, nextTick } from 'vue';
import {
  submitActivity,
  getCheckpoints,
  checkIn,
  uploadFile,
  getStudentTaskDetail,
  getStudentTasks
} from '@/utils/request.js';
import { getCurrentLocation } from '@/utils/location.js';
import { smoothTrajectoryForMap } from '@/utils/trajectory-smooth.js';
import { buildPaceColoredPolylines } from '@/utils/trajectory-pace-polyline.js';
import { createRunEndpointMarker } from '@/utils/run-map-markers.js';
import { createStepCounter } from '@/utils/step-counter.js';
import { createTrajectoryFilter } from '@/utils/trajectory-filter.js';
import {
  pushRunGpsRawSample,
  resetRunGpsRawWindow,
  shouldRejectMileageSegment,
  computeDynamicMinDistanceM,
  isGpsClusterStationary
} from '@/utils/run-gps-mileage.js';

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
  initRunSheetSnap();
  initRunPrepSheetHeight();

  // 寤惰繜鍔犺浇鍦板浘锛岄槻姝㈠鍣ㄦ湭灏辩华瀵艰嚧鐨勬覆鏌撻敊璇?
  setTimeout(() => {
    isMapReady.value = true;
    startCompassWatch();
  }, 500);
  
  // 鍒濆鍖栦氦缁欑埗椤?onShow 璋冪敤 onPageShow锛堝甫 options锛夛紱姝ゅ涓嶅啀璋冪敤锛岄伩鍏嶄笌鐖堕〉 50ms 鍚庣殑璋冪敤褰㈡垚銆屽厛绌哄悗瀹炪€嶈闃叉姈璇悶
});

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
    const restoredSession = tryRestoreRunSession();
    // 短间隔重复 onShow（onLoad+onShow）时仍须能恢复会话
    if (!forceTask && now - lastShowTime < 500 && !hasMeaningfulRunPageOptions(options)) {
        if (restoredSession) {
          startLocationService();
          beginRunTrackingAfterFaceDefer();
        }
        return;
    }
    lastShowTime = now;

    isPageActive = true;
    
    // 鏇存柊鐘舵€佹爮楂樺害
    const sys = uni.getSystemInfoSync();
    statusBarHeight.value = sys.statusBarHeight || 20;

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
      uni.showToast({ title: `开始课程：${options.course}`, icon: 'none' });
    }

    const targetMode = uni.getStorageSync('runMode');
    if (targetMode && !taskRunLocked.value && !isRunning.value) {
      switchMode(targetMode);
      uni.removeStorageSync('runMode');
    }

    startLocationService();

    if (!restoredSession) {
      tryRestoreRunSession();
    }
    
    // Load Checkpoints for Campus Mode
    getCheckpoints().then(data => {
      availableCheckpoints.value = Array.isArray(data) ? data : [];
    }).catch(err => {
      console.error('Failed to load checkpoints', err);
      availableCheckpoints.value = [];
    });

    if (!isRunning.value) {
      checkpoint.value = {};
      checkpointName.value = '';
      checkpointMarker.value = null;
      navPolyline.value = null;
      uni.removeStorageSync('checkpoint');
      refreshMarkers();
      updateMapPolyline();
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
      refreshActiveRunTasks();
    } else {
      reconcilePoliceMode();
    }
};

const taskRunLocked = ref(false);
const taskDescription = ref('');
const taskMinDurationSec = ref(0);
const taskSubmitHint = ref('');
const activeRunTasks = ref([]);
const runTasksLoading = ref(false);

const isActionableRunTask = (t) =>
  t && t.type === 'run' && (t.status === 'pending' || t.status === 'failed');

const hasRunTaskAvailable = computed(
  () => !!taskId.value || activeRunTasks.value.some(isActionableRunTask)
);

const formatTaskDurationLabel = (sec) => {
  const s = Math.max(0, Math.floor(Number(sec) || 0));
  const m = Math.floor(s / 60);
  const ss = s % 60;
  return `${m} 分 ${ss} 秒`;
};

const formatRunTaskMeta = (t) => {
  const parts = [];
  const km = Number(t.min_distance);
  if (km > 0) parts.push(`≥${km.toFixed(2)}km`);
  if (t.min_duration) parts.push(`≥${formatTaskDurationLabel(t.min_duration)}`);
  return parts.length ? parts.join(' · ') : '查看任务说明';
};

const policeReferencePaceLabel = computed(() => {
  const km = policeTargetDistance.value / 1000;
  if (!(taskMinDurationSec.value > 0 && km > 0)) return '';
  const pace = taskMinDurationSec.value / 60 / km;
  if (!Number.isFinite(pace) || pace <= 0) return '';
  return `${pace.toFixed(1)} 分钟/公里`;
});

const applyRunTaskSnapshot = (task) => {
  if (!task?.id) return;
  taskId.value = String(task.id);
  taskType.value = 'run';
  teacherRunTask.value = task.title || '';
  taskDescription.value = task.description || '';
  taskMinDurationSec.value = Number(task.min_duration) || 0;
  taskSubmitHint.value = '';
  const km = Number(task.min_distance) || 0;
  if (km > 0) {
    policeTargetDistance.value = Math.round(km * 1000);
    if (taskMinDurationSec.value > 0) {
      policeTargetPace.value = taskMinDurationSec.value / 60 / km;
    }
  } else {
    policeTargetDistance.value = 0;
  }
};

const selectRunTask = (task) => {
  if (!task?.id) return;
  applyRunTaskSnapshot(task);
  loadTaskRequirements(task.id);
  initRunPrepSheetHeight();
};

const reconcilePoliceMode = () => {
  if (taskRunLocked.value) return;
  if (!hasRunTaskAvailable.value) {
    if (currentMode.value === 'police') {
      currentMode.value = 'normal';
      taskId.value = null;
      taskType.value = null;
      initRunPrepSheetHeight();
    }
    return;
  }
  if (currentMode.value === 'police' && !taskId.value && activeRunTasks.value.length === 1) {
    selectRunTask(activeRunTasks.value[0]);
  }
};

const refreshActiveRunTasks = async () => {
  if (taskRunLocked.value && taskId.value) return;
  runTasksLoading.value = true;
  try {
    const res = await getStudentTasks({ page: 1, size: 50 });
    activeRunTasks.value = (res.items || []).filter(isActionableRunTask);
  } catch (e) {
    console.error(e);
    activeRunTasks.value = [];
  } finally {
    runTasksLoading.value = false;
    reconcilePoliceMode();
  }
};
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
    applyRunTaskSnapshot({
      id: d.id,
      title: d.title,
      type: d.type || 'run',
      description: d.description,
      min_distance: d.min_distance,
      min_duration: d.min_duration
    });
    if (d.can_submit === false && d.submit_hint) {
      taskSubmitHint.value = d.submit_hint;
      uni.showToast({ title: d.submit_hint, icon: 'none', duration: 2500 });
    } else {
      taskSubmitHint.value = '';
    }
  } catch (e) {
    console.error(e);
    uni.showToast({ title: '加载任务要求失败', icon: 'none' });
  }
};

// 鏆撮湶缁欑埗缁勪欢 (Merged below)
// defineExpose({
//   onPageShow
// });

// 姒傝涓庝换鍔℃彁绀?
const todayRunCount = ref(0);
const todayRunDistance = ref(0);
const teacherRunTask = ref('');
const dailyTarget = ref(2);
const normalProgress = ref(0);
const policeProgress = ref(0);
const historyList = ref([]);

const availableCheckpoints = ref([]);

// 1. 鍦板浘/鎵撳崱鐐规暟鎹?
const locationState = ref('idle'); // idle, locating, success, fail
/** 鏈€杩戜竴娆°€屽彲寮€璺戙€嶇殑瀹氫綅鏄惁鏉ヨ嚜缂撳瓨鍏滃簳锛堢湡 GPS 鏈垚鍔燂級锛屼究浜庢彁绀虹敤鎴峰埛鏂颁互鍏嶉噷绋嬮暱鏈熶负 0 */
const lastLocationFixWasStale = ref(false);
let locationRetryTimer = null;
let locationPromise = null;
/** 微信小程序：新用户首次定位自动重试（无 lastLocation 时） */
let wxInitialLocateTimer = null;
let wxInitialLocateAttempts = 0;
const WX_INITIAL_LOCATE_MAX = 8;
const WX_INITIAL_LOCATE_INTERVAL_MS = 4000;
/** 寰俊灏忕▼搴忥細瀹氫綅鍏滃簳 setTimeout锛岄』鍦ㄥ仠姝㈣窇姝ヤ笌鍗歌浇鏃舵竻闄?*/
let wxLocationWatchdogTimer = null;
/** 寰俊灏忕▼搴忥細鏄惁宸叉垚鍔熷紑鍚悗鍙版寔缁畾浣嶏紙涓?startLocationUpdateBackground 鐘舵€佸悓姝ワ級 */
let mpBackgroundLocationActive = false;
/** 寰俊鐪熸満 map 椤?onLocationChange 甯镐笉鍥炶皟锛氫笌鎸佺画瀹氫綅骞惰 2s getLocation锛岄┍鍔ㄦ椂闀?閲岀▼ */
let wxRunAssistTimer = null;
let wxContinuousLocationOk = false;
let lastWxLocationChangeAt = 0;
const WX_LOCATION_CHANGE_STALE_MS = 6500;
const GPS_RUN_READY_ACCURACY_M = 25;
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
/** 最近一次定位水平精度（米），用于跑步中提示 */
const lastGpsAccuracyM = ref(NaN);
const gpsRunReady = computed(
  () =>
    locationState.value === 'success' &&
    Number.isFinite(lastGpsAccuracyM.value) &&
    lastGpsAccuracyM.value > 0 &&
    lastGpsAccuracyM.value <= GPS_RUN_READY_ACCURACY_M
);

let runStepCounter = null;
let runTrajectoryFilter = null;
let stepFusionSkewSince = 0;
let stepFusionLastAdjustAt = 0;

const resetRunMotionEvidence = () => {
  lastStepDetectedAt = 0;
  lastStrongStepMotionAt = 0;
  lastGpsMotionAt = 0;
  stepBurstCount = 0;
  gpsMotionBurstCount = 0;
  resetRunGpsRawWindow();
};

const hasRecentStepMotion = () => lastStepDetectedAt > 0 && (Date.now() - lastStepDetectedAt) < 4500;
const hasStrongStepMotion = () => lastStrongStepMotionAt > 0 && (Date.now() - lastStrongStepMotionAt) < 6500;
const hasRecentGpsMotionEvidence = () => lastGpsMotionAt > 0 && (Date.now() - lastGpsMotionAt) < 7000;
const hasTrustedRunMotion = () => hasStrongStepMotion() || hasRecentGpsMotionEvidence();

const getLastTrackAnchor = () => {
  const pts = trajectoryPoints.value;
  return pts.length > 0 ? pts[pts.length - 1] : null;
};

/**
 * “跑步模式”解锁：放宽计里程/画线。
 * 起跑就在跑时，通常 1～2 个定位点（约 5～15m）即可解锁，不会等很久。
 */
const isRunGpsUnlocked = () =>
  gpsAcceptedPointCount >= 2 ||
  distance.value >= 12 ||
  displayTrackPoints.value.length >= 4 ||
  (gpsAcceptedPointCount >= 1 && hasRecentGpsMotionEvidence()) ||
  (hasStrongStepMotion() && distance.value >= 6) ||
  (hasRecentGpsMotionEvidence() && distance.value >= 5) ||
  (hasRecentStepMotion() && stepCount.value >= 12 && duration.value >= 8);

const getMergePolylineGapM = () => (isRunGpsUnlocked() ? MERGE_POLYLINE_GAP_RUN_M : MERGE_POLYLINE_GAP_IDLE_M);

/** 仅“站着抖手机、GPS 几乎不动”时冻结；起跑就开跑（有位移/步频）不冻结 */
const shouldFreezeRunPosition = (rawLat, rawLng) => {
  if (!isRunning.value || isRunGpsUnlocked()) return false;
  if (hasRecentStepMotion() && stepCount.value >= 8) return false;
  const anchor = getLastTrackAnchor();
  if (!anchor) return false;
  const rawM = getDistance(anchor.latitude, anchor.longitude, rawLat, rawLng);
  if (rawM >= STATIONARY_RAW_IDLE_M) return false;
  if (hasStrongStepMotion() && rawM >= 1.8) return false;
  if (hasRecentStepMotion() && stepCount.value >= 12 && rawM >= 1.0) return false;
  if (
    !hasRecentStepMotion() &&
    !hasStrongStepMotion() &&
    isGpsClusterStationary({
      hasRecentStepMotion: false,
      hasStrongStepMotion: false
    })
  ) {
    return true;
  }
  const shakeOnly =
    stepCount.value >= 18 &&
    !hasRecentGpsMotionEvidence() &&
    !hasStrongStepMotion() &&
    !hasRecentStepMotion();
  return shakeOnly || rawM < 2.2;
};

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
  const goodAccuracy = !Number.isFinite(accuracyM) || accuracyM <= 40;
  const softAccuracy = !Number.isFinite(accuracyM) || accuracyM <= 55;
  const speedOk = speedMps >= 0.55 && speedMps <= 6.5;
  const softSpeedOk = speedMps >= 0.4 && speedMps <= 6.5;
  const distanceOk = segmentDistanceM >= 1.8;
  const softDistanceOk = segmentDistanceM >= 1.1;
  if (hasRecentStepMotion() && softAccuracy && softSpeedOk && softDistanceOk) {
    lastGpsMotionAt = now;
    gpsMotionBurstCount = Math.max(gpsMotionBurstCount, 1);
    return;
  }
  if (goodAccuracy && speedOk && distanceOk) {
    gpsMotionBurstCount += 1;
    if (segmentDistanceM >= 2.6 || gpsMotionBurstCount >= 2) {
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
  if (stepBacked && hasRecentGpsMotionEvidence() && segmentSpeed >= 0.85 && segmentDistance >= Math.max(3.5, dt * 0.55)) {
    return 'walk';
  }
  if (stepBacked && segmentSpeed >= 1.05 && segmentDistance >= Math.max(5.5, dt * 0.75)) {
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
const compareVersion = (v1, v2) => {
  const a = String(v1 || '0').split('.').map((n) => parseInt(n, 10) || 0);
  const b = String(v2 || '0').split('.').map((n) => parseInt(n, 10) || 0);
  const len = Math.max(a.length, b.length);
  for (let i = 0; i < len; i++) {
    const d = (a[i] || 0) - (b[i] || 0);
    if (d !== 0) return d;
  }
  return 0;
};

const buildWxLocationUpdateOptions = () => {
  const opts = { type: 'gcj02' };
  try {
    const sdk = uni.getSystemInfoSync().SDKVersion;
    if (compareVersion(sdk, '2.21.0') >= 0) {
      opts.needFullAccuracy = true;
    }
  } catch (e) {}
  return opts;
};

/** 仅当连续 onLocationChange 不可用或长时间无回调时，2s 辅助拉定位（与兼容轮询互斥） */
const scheduleWxRunLocationAssist = () => {
  // #ifdef MP-WEIXIN
  if (h5LocationTimer) return;
  clearWxRunAssistTimer();
  const wxAssistTick = () => {
    if (!isRunning.value) return;
    if (
      wxContinuousLocationOk &&
      Date.now() - lastWxLocationChangeAt < WX_LOCATION_CHANGE_STALE_MS
    ) {
      clearWxRunAssistTimer();
      return;
    }
    syncRunElapsedDisplay();
    tickPoliceFinishHint();
    getCurrentLocation({ type: 'gcj02', fastFix: true })
      .then((res) => {
        updateLocationLogic(res.latitude, res.longitude, res.speed || 0, res);
      })
      .catch(() => {})
      .finally(() => {
        if (!isRunning.value) return;
        if (h5LocationTimer) return;
        if (
          wxContinuousLocationOk &&
          Date.now() - lastWxLocationChangeAt < WX_LOCATION_CHANGE_STALE_MS
        ) {
          clearWxRunAssistTimer();
          return;
        }
        wxRunAssistTimer = setTimeout(wxAssistTick, 2000);
      });
  };
  wxAssistTick();
  // #endif
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

/** 未开跑：微信原生半透明蓝点；开跑：仅自定义方向箭头，二者不同时开避免叠影 */
const showMapNativeLocation = computed(
  () =>
    !isRunning.value &&
    hasPlausibleCoords() &&
    (locationState.value === 'success' || locationState.value === 'locating')
);

const MAP_ID = 'runMap';
const mapHeading = ref(0);
/** 指南针更新步长，减小 marker 旋转刷新频率，避免蓝箭头闪烁 */
const COMPASS_ROTATE_STEP = 12;
let compassHandler = null;

const snapCompassHeading = (deg) => {
  const n = Number(deg);
  if (!Number.isFinite(n)) return 0;
  const step = COMPASS_ROTATE_STEP;
  return Math.round(n / step) * step % 360;
};

const applyMapHeading = (deg) => {
  const snapped = snapCompassHeading(deg);
  if (snapped === mapHeading.value) return;
  mapHeading.value = snapped;
  if (locationState.value !== 'success' || !hasPlausibleCoords() || !isRunning.value) return;
  const idx = markers.value.findIndex((m) => m.id === 0);
  if (idx < 0) {
    refreshMarkers();
    return;
  }
  const cur = markers.value[idx];
  if (cur.rotate === snapped) return;
  const next = [...markers.value];
  next[idx] = { ...cur, rotate: snapped };
  markers.value = next;
};

/** 仅更新 id=0 的当前位置 marker，避免整表重建导致微信地图箭头叠影 */
const patchCurrentLocationMarker = () => {
  if (!hasPlausibleCoords() || !isRunning.value) return;
  const fresh = createCurrentLocationMarker(lat.value, lng.value);
  const idx = markers.value.findIndex((m) => m.id === 0);
  if (idx < 0) {
    refreshMarkers();
    return;
  }
  const cur = markers.value[idx];
  if (
    cur.latitude === fresh.latitude &&
    cur.longitude === fresh.longitude &&
    cur.rotate === fresh.rotate &&
    cur.iconPath === fresh.iconPath
  ) {
    return;
  }
  const next = [...markers.value];
  next[idx] = fresh;
  markers.value = next;
};

const startCompassWatch = () => {
  // #ifdef MP-WEIXIN || APP-PLUS
  if (compassHandler) return;
  compassHandler = (res) => {
    applyMapHeading(res.direction);
  };
  uni.onCompassChange(compassHandler);
  uni.startCompass({
    success: () => {},
    fail: () => {}
  });
  // #endif
};

const stopCompassWatch = () => {
  // #ifdef MP-WEIXIN || APP-PLUS
  if (compassHandler) {
    uni.offCompassChange(compassHandler);
    compassHandler = null;
  }
  try {
    uni.stopCompass();
  } catch (e) {}
  // #endif
};

/** 人脸验证打开时隐藏地图 cover-view（原生层会压在普通 view 之上） */
const hideMapCoverLayer = computed(() => showFaceCamera.value);

const showMapLegend = computed(
  () =>
    !hideMapCoverLayer.value &&
    isRunning.value &&
    locationState.value === 'success' &&
    hasPlausibleCoords()
);

const showLocationStatusBar = computed(
  () =>
    locationState.value !== 'success' ||
    lastLocationFixWasStale.value ||
    (locationState.value === 'success' && !gpsRunReady.value && !isRunning.value)
);

const createCurrentLocationMarker = (latitude, longitude) => {
  const size = 28;
  return {
    id: 0,
    latitude,
    longitude,
    title: '当前位置',
    iconPath: '/static/nav-arrow-soft.png',
    width: size,
    height: size,
    rotate: mapHeading.value,
    zIndex: 100,
    anchor: { x: 0.5, y: 0.5 },
    callout: {
      content: '我的位置',
      color: '#333333',
      fontSize: 12,
      borderRadius: 8,
      bgColor: '#ffffff',
      padding: 6,
      display: 'BYCLICK',
      borderWidth: 1,
      borderColor: '#1976D2'
    }
  };
};

const createRunPointMarker = (id, latitude, longitude, labelText) => {
  const type = labelText === '终' ? 'end' : 'start';
  return createRunEndpointMarker({ id, latitude, longitude, type });
};

/** 开跑初期隐藏起点 pin，避免与蓝箭头叠在一起难辨认 */
const showRunStartOnMap = computed(() => {
  if (!runStartMarker.value) return false;
  if (!isRunning.value) return true;
  if (distance.value >= 28) return true;
  if (duration.value >= 18 && trajectoryPointCount.value >= 3) return true;
  return false;
});

watch(showRunStartOnMap, () => {
  if (isRunning.value || runStartMarker.value) {
    refreshMarkers();
  }
});

watch(locationState, () => {
  if (hasPlausibleCoords()) {
    refreshMarkers();
  }
});

const refreshMarkers = () => {
  const nextMarkers = [];
  if (runStartMarker.value && showRunStartOnMap.value) {
    nextMarkers.push({ ...runStartMarker.value });
  }
  if (runEndMarker.value) {
    nextMarkers.push({ ...runEndMarker.value });
  }
  if (checkpointMarker.value) {
    nextMarkers.push({ ...checkpointMarker.value });
  }
  if (hasPlausibleCoords() && isRunning.value) {
    nextMarkers.push(createCurrentLocationMarker(lat.value, lng.value));
  }
  markers.value = nextMarkers;
};

// Separate line states for better management
/** 轨迹线不加 arrowLine，否则 GPS 抖动时每一段都会画箭头，内测反馈会叠成一片 */
const runPolyline = ref({
  points: [],
  color: '#1E88E5',
  width: 6,
  arrowLine: false,
  borderColor: '#FFFFFF',
  borderWidth: 2
});

/** 未确认真实跑动前：计里程轨迹点合并间距 */
const MERGE_POLYLINE_GAP_IDLE_M = 2.5;
/** 已确认在跑后：合并间距（慢走也能连续记里程） */
const MERGE_POLYLINE_GAP_RUN_M = 1.8;
/** 地图展示轨迹间距（与计里程解耦，保证折线连续可见） */
const DISPLAY_TRACK_GAP_M = 1.2;
/** 未解锁前：相对末点 GPS 位移过小视为静止抖动 */
const STATIONARY_RAW_IDLE_M = 3.2;
const navPolyline = ref(null);

const polyline = ref([]); // Final array for map component
const checkpoint = ref({});
const trajectoryPoints = ref([]); // Store real GPS points
/** 地图折线专用点列（GPS 位移即记录，不受计里程阈值影响） */
const displayTrackPoints = ref([]);
const checkinRecords = ref([]); // Store successful check-ins

const trajectoryPointCount = computed(() => {
  const d = displayTrackPoints.value.length;
  return d >= 2 ? d : trajectoryPoints.value.length;
});

const getPolylineSourcePoints = () => {
  if (displayTrackPoints.value.length >= 2) return displayTrackPoints.value;
  return trajectoryPoints.value;
};

// Helper to update map polyline with deep clone to force render
const updateMapPolyline = () => {
  const lines = [];
  const raw = getPolylineSourcePoints();
  if (raw.length >= 2) {
    const paceLines = buildPaceColoredPolylines(raw);
    if (paceLines.length > 0) {
      paceLines.forEach((ln) => lines.push({ ...ln, points: [...ln.points] }));
    } else if (runPolyline.value.points && runPolyline.value.points.length >= 2) {
      lines.push({ ...runPolyline.value, points: [...runPolyline.value.points] });
    }
  } else if (runPolyline.value.points && runPolyline.value.points.length >= 2) {
    lines.push({ ...runPolyline.value, points: [...runPolyline.value.points] });
  }
  if (navPolyline.value && navPolyline.value.points && navPolyline.value.points.length >= 2) {
    lines.push(JSON.parse(JSON.stringify(navPolyline.value)));
  }
  polyline.value = lines;
};

let displayPolylineRebuildTimer = null;
let lastDisplayPolylineAt = 0;
const DISPLAY_POLYLINE_MIN_INTERVAL_MS = 500;

/** 由原始 GPS 点生成配速分段上色折线（仅 map 展示，不影响里程） */
const rebuildDisplayPolyline = () => {
  const raw = getPolylineSourcePoints();
  if (raw.length < 2) {
    runPolyline.value.points =
      raw.length === 1
        ? [{ latitude: raw[0].latitude, longitude: raw[0].longitude }]
        : [];
  } else {
    const flat = raw.map((p) => ({ latitude: p.latitude, longitude: p.longitude }));
    runPolyline.value.points = smoothTrajectoryForMap(flat);
  }
  updateMapPolyline();
};

const scheduleRebuildDisplayPolyline = (force = false) => {
  const now = Date.now();
  if (force || now - lastDisplayPolylineAt >= DISPLAY_POLYLINE_MIN_INTERVAL_MS) {
    lastDisplayPolylineAt = now;
    if (displayPolylineRebuildTimer != null) {
      clearTimeout(displayPolylineRebuildTimer);
      displayPolylineRebuildTimer = null;
    }
    rebuildDisplayPolyline();
    return;
  }
  if (displayPolylineRebuildTimer != null) return;
  const delay = Math.max(50, DISPLAY_POLYLINE_MIN_INTERVAL_MS - (now - lastDisplayPolylineAt));
  displayPolylineRebuildTimer = setTimeout(() => {
    displayPolylineRebuildTimer = null;
    lastDisplayPolylineAt = Date.now();
    rebuildDisplayPolyline();
  }, delay);
};

/** 地图展示轨迹：有位移即记点，与计里程阈值解耦 */
const appendDisplayTrackPoint = (latIn, lngIn, extra = {}) => {
  if (!isRunning.value || isRunPaused.value) return false;
  const last = displayTrackPoints.value[displayTrackPoints.value.length - 1];
  if (last) {
    const gap = getDistance(last.latitude, last.longitude, latIn, lngIn);
    if (gap < DISPLAY_TRACK_GAP_M) return false;
  }
  displayTrackPoints.value.push({
    latitude: latIn,
    longitude: lngIn,
    timestamp: extra.timestamp ?? Date.now(),
    speed: extra.speed
  });
  scheduleRebuildDisplayPolyline();
  syncStepsFromDistanceFallback();
  return true;
};

/** 追加原始轨迹点；间距不足时不记点。展示折线由 rebuildDisplayPolyline 平滑生成 */
const appendRunTrackPoint = (workLat, workLng, point) => {
  const last = trajectoryPoints.value[trajectoryPoints.value.length - 1];
  if (last) {
    const gap = getDistance(last.latitude, last.longitude, workLat, workLng);
    if (gap < getMergePolylineGapM()) {
      return;
    }
  }
  trajectoryPoints.value.push(point);
  appendDisplayTrackPoint(workLat, workLng, {
    timestamp: point.timestamp,
    speed: point.speed
  });
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
  return (
    gpsAcceptedPointCount >= 2 ||
    distance.value >= 20 ||
    currentSpeed.value >= 1.0 ||
    (hasRecentStepMotion() && stepCount.value >= 16 && duration.value >= 10)
  );
};

const getStrideLengthM = () => {
  const distM = distance.value;
  const durS = duration.value;
  if (distM > 40 && durS > 0) {
    const paceMinPerKm = durS / 60 / (distM / 1000);
    if (paceMinPerKm >= 8) return 0.65;
    if (paceMinPerKm <= 5) return 0.75;
  }
  return currentMode.value === 'police' ? 0.72 : 0.78;
};

const estimateStepsByDistance = (distanceM) => {
  if (!Number.isFinite(distanceM) || distanceM < 4) return 0;
  return Math.floor(distanceM / getStrideLengthM());
};

/** 加速度计无步数时，用 GPS 里程估算步数（兜底） */
const syncStepsFromDistanceFallback = () => {
  if (!isRunning.value || isRunPaused.value) return;
  if (hasRecentStepMotion() && stepCount.value >= 4) return;
  const est = estimateStepsByDistance(distance.value);
  if (est <= 0) return;
  const hasMotion =
    gpsAcceptedPointCount >= 1 ||
    displayTrackPoints.value.length >= 2 ||
    hasRecentGpsMotionEvidence();
  if (!hasMotion || distance.value < 5) return;
  if (est > stepCount.value) {
    stepCount.value = est;
    if (runStepCounter) runStepCounter.setStepCount(est);
  }
};

/** GPS 距离与传感器步数融合：仅持续偏差 >25% 且满 30s 时缓慢校正，不粗暴取 max */
const maybeEstimateStepsFromDistance = () => {
  if (!hasRecentGpsMotionEvidence() && displayTrackPoints.value.length < 2) return;
  if (distance.value < 8) return;
  const estimatedSteps = estimateStepsByDistance(distance.value);
  if (estimatedSteps <= 0) return;
  const sensor = stepCount.value;
  const diff = Math.abs(sensor - estimatedSteps);
  const ratio = estimatedSteps > 0 ? diff / estimatedSteps : 0;
  const now = Date.now();
  if (ratio > 0.25) {
    if (!stepFusionSkewSince) stepFusionSkewSince = now;
    if (now - stepFusionSkewSince >= 30000 && now - stepFusionLastAdjustAt >= 5000) {
      const target = Math.round(sensor * 0.85 + estimatedSteps * 0.15);
      if (target !== sensor && target > 0) {
        stepCount.value = target;
        if (runStepCounter) runStepCounter.setStepCount(target);
        stepFusionLastAdjustAt = now;
      }
    }
  } else {
    stepFusionSkewSince = 0;
  }
};

const filterTrackCoordsForMileage = (latIn, lngIn, accuracyM) => {
  if (!runTrajectoryFilter) {
    runTrajectoryFilter = createTrajectoryFilter();
  }
  const out = runTrajectoryFilter.filter(latIn, lngIn, accuracyM);
  return { lat: out.latitude, lng: out.longitude };
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
  if (isRunning.value) {
    pushRunGpsRawSample(newLat, newLng, nowTs);
  }

  if (isRunning.value && shouldFreezeRunPosition(newLat, newLng)) {
    const anchor = getLastTrackAnchor();
    const followGpsOnMap = hasRecentStepMotion() && stepCount.value >= 8;
    if (followGpsOnMap) {
      lat.value = newLat;
      lng.value = newLng;
      runLocationSmooth = { lat: newLat, lng: newLng };
      patchCurrentLocationMarker();
      appendDisplayTrackPoint(newLat, newLng, { timestamp: nowTs, speed: 0 });
    } else if (anchor) {
      lat.value = anchor.latitude;
      lng.value = anchor.longitude;
      runLocationSmooth = { lat: anchor.latitude, lng: anchor.longitude };
      patchCurrentLocationMarker();
    }
    currentSpeed.value = 0;
    syncRunElapsedDisplay();
    if (currentMode.value === 'campus' && checkpoint.value.lat) {
      const refLat = followGpsOnMap ? newLat : anchor?.latitude;
      const refLng = followGpsOnMap ? newLng : anchor?.longitude;
      if (refLat != null && refLng != null) {
        distanceToCheckpoint.value = Math.floor(
          getDistance(refLat, refLng, checkpoint.value.lat, checkpoint.value.lng)
        );
      }
    }
    return;
  }

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
  patchCurrentLocationMarker();

  if (isRunning.value && !isRunPaused.value) {
    appendDisplayTrackPoint(workLat, workLng, {
      timestamp: nowTs,
      speed: typeof speed === 'number' && speed >= 0 ? speed : currentSpeed.value
    });
  }

  if (isRunning.value) {
    if (!isRunPaused.value) {
      syncRunElapsedDisplay();
    }
    if (isRunPaused.value) {
      currentSpeed.value = 0;
      return;
    }
    // 不再按 horizontalAccuracy 整段丢弃回调：弱信号下常 >100m，丢弃后里程永远不涨；异常位移已由 d / calculatedSpeed 约束

    // 1. Initial point
    if (trajectoryPoints.value.length === 0) {
        const acc0 = getHorizontalAccuracyM(accuracyOrRes);
        const ft0 = filterTrackCoordsForMileage(workLat, workLng, acc0);
        const point = { latitude: ft0.lat, longitude: ft0.lng, timestamp: nowTs, speed: speed || currentSpeed.value };
        appendRunTrackPoint(ft0.lat, ft0.lng, point);
        
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
    const runGpsSpeedWarmup = !hasReliableGpsMovement() && duration.value < 10 && distance.value < 18;
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
    if (Number.isFinite(accM)) {
      lastGpsAccuracyM.value = accM;
    }
    /** 开跑后 GPS 防抖；有步频时放宽，避免「有步数无里程」 */
    const runUnlocked = isRunGpsUnlocked();
    const stableCadence = runStepCounter?.hasStableCadence?.() ?? false;
    const coldPhase = !runUnlocked && duration.value < (stableCadence ? 35 : 50);
    const recentStepMotion = hasRecentStepMotion();
    const trustedMotion = hasTrustedRunMotion();
    const stepBoosted = recentStepMotion && stepCount.value >= 8;
    const tightenNoSteps =
      stepCount.value < 8 &&
      !trustedMotion &&
      !stableCadence &&
      duration.value >= 30 &&
      duration.value < 90 &&
      distance.value < 80;
    const driftTight = !runUnlocked && (coldPhase || tightenNoSteps) && !stepBoosted && !stableCadence;
    const weakGpsSignal = Number.isFinite(accM) && accM > 45;
    const veryWeakGpsSignal = Number.isFinite(accM) && accM > 80;
    const earlyMotionStrict =
      !runUnlocked &&
      !trustedMotion &&
      !stepBoosted &&
      duration.value >= 10 &&
      duration.value < 25 &&
      distance.value < 80;
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

    let minD = computeDynamicMinDistanceM({
      accuracyM: accM,
      runUnlocked,
      coldPhase,
      tierMinDistance: tierConfig.minDistance,
      recentStepMotion,
      hasStrongStepMotion: hasStrongStepMotion(),
      stableCadence,
      hasRecentGpsMotionEvidence: hasRecentGpsMotionEvidence()
    });
    if (!runUnlocked && (recentStepMotion || hasStrongStepMotion()) && !hasRecentGpsMotionEvidence()) {
      minD = hasStrongStepMotion() ? Math.max(minD, 2.4) : Math.max(minD, 4);
    }
    if (runUnlocked) {
      minD = Math.min(minD, stableCadence ? 2.5 : 3);
    }

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
      stepCount.value < 8 &&
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
      !stepBoosted &&
      d < Math.max(8, tierConfig.minDistance + 2.2) &&
      calculatedSpeed < Math.max(2.3, tierConfig.minSpeed + 0.7)
    ) {
      currentSpeed.value = 0;
      return;
    }

    const maxSpeedForDistance = driftTight ? Math.min(tierConfig.maxSpeed, motionTier === 'fast_run' ? 5.8 : tierConfig.maxSpeed) : Math.max(tierConfig.maxSpeed, 7.8);

    if (
      shouldRejectMileageSegment({
        segmentM: d,
        timeDiffS: timeDiff,
        speedMps: calculatedSpeed,
        accuracyM: accM,
        hasRecentStepMotion: recentStepMotion,
        hasStrongStepMotion: hasStrongStepMotion(),
        hasRecentGpsMotionEvidence: hasRecentGpsMotionEvidence(),
        runUnlocked
      })
    ) {
      currentSpeed.value = 0;
      return;
    }

    if (d >= minD && calculatedSpeed >= tierConfig.minSpeed && calculatedSpeed < maxSpeedForDistance) {
        const gpsLooksGood = (!Number.isFinite(accM) || accM <= 32) && calculatedSpeed >= 1.05 && d >= 4.5;
        const runningFromStart =
          (hasStrongStepMotion() || (stepBoosted && hasRecentStepMotion())) &&
          d >= (stepBoosted ? 2.0 : 2.8) &&
          calculatedSpeed >= (stepBoosted ? 0.5 : 0.75) &&
          calculatedSpeed < maxSpeedForDistance &&
          (!Number.isFinite(accM) || accM <= 55);
        const canTrustThisSegment = runUnlocked
          ? d >= 2.2 && calculatedSpeed >= 0.5 && calculatedSpeed < maxSpeedForDistance
          : gpsLooksGood ||
            runningFromStart ||
            (stepBoosted && d >= 1.8 && calculatedSpeed >= 0.45 && calculatedSpeed < maxSpeedForDistance) ||
            (hasRecentGpsMotionEvidence() && d >= 3 && calculatedSpeed >= 0.7) ||
            (gpsAcceptedPointCount >= 1 && d >= 3.5 && calculatedSpeed >= 0.85);
        const trustedByTier = runUnlocked
          ? true
          : !tierConfig.requiresTrustedMotion ||
            hasRecentGpsMotionEvidence() ||
            runningFromStart ||
            gpsLooksGood;
        if (!runUnlocked && !trustedByTier && !stepBoosted && duration.value >= 12 && distance.value < 120) {
          currentSpeed.value = 0;
          return;
        }
        if (!canTrustThisSegment && !runUnlocked && !stepBoosted && duration.value >= 15 && distance.value < 120) {
          currentSpeed.value = 0;
          return;
        }
        distance.value += d;
        gpsAcceptedPointCount += 1;
        noteGpsMotion(nowTs, d, calculatedSpeed, accM);

        const ft = filterTrackCoordsForMileage(workLat, workLng, accM);
        const point = { latitude: ft.lat, longitude: ft.lng, timestamp: nowTs, speed: speed || calculatedSpeed };
        appendRunTrackPoint(ft.lat, ft.lng, point);

        if (currentMode.value === 'normal') {
           normalProgress.value = Math.min(100, ((distance.value/1000) / dailyTarget.value) * 100);
        } else if (currentMode.value === 'police') {
           policeProgress.value = Math.min(100, (distance.value / policeTargetDistance.value) * 100);
        }
        maybeEstimateStepsFromDistance();
        syncStepsFromDistanceFallback();
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
        const runGpsSpeedWarmup = !hasReliableGpsMovement() && duration.value < 10 && distance.value < 18;
        currentSpeed.value = runGpsSpeedWarmup ? 0 : speedVal;

        updateLocationLogic(newLat, newLng, speedVal, res);
        lastTs = Date.now();
    }).catch(err => {
        console.warn('H5 Polling failed', err);
    });
  }, 2000);
  // #endif
  // #ifdef MP-WEIXIN
  // 鎭睆/鍒囧悗鍙帮細椤诲厛 startLocationUpdate锛屽啀 startLocationUpdateBackground锛沵anifest requiredBackgroundModes + 鐢ㄦ埛鎺堟潈
  if (wxLocationWatchdogTimer) {
    clearTimeout(wxLocationWatchdogTimer);
    wxLocationWatchdogTimer = null;
  }
  mpBackgroundLocationActive = false;
  wxContinuousLocationOk = false;
  lastWxLocationChangeAt = 0;
  const registerLocationChange = () => {
    if (locationCallback) uni.offLocationChange(locationCallback);
    locationCallback = (res) => {
      lastWxLocationChangeAt = Date.now();
      if (!wxContinuousLocationOk) {
        wxContinuousLocationOk = true;
        clearWxRunAssistTimer();
      }
      if (res.direction != null) applyMapHeading(res.direction);
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
      tickPoliceFinishHint();
      getCurrentLocation({ type: preferredType })
        .then((res) => {
          updateLocationLogic(res.latitude, res.longitude, res.speed || 0, res);
        })
        .catch((err) => {
          console.error(`Polling fallback failed for ${preferredType}`, err);
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
  const wxLocOpts = buildWxLocationUpdateOptions();
  uni.startLocationUpdate({
    ...wxLocOpts,
    success: () => {
      registerLocationChange();
      clearWxRunAssistTimer();
      tryStartWxBackgroundAfterForeground();
    },
    fail: () => {
      wxContinuousLocationOk = false;
      uni.showModal({
        title: '连续定位未开启',
        content: '无法启动高精度连续定位，将使用兼容模式（更新较慢）。请检查定位权限后重试。',
        showCancel: false
      });
      startPollFallback();
    }
  });
  wxLocationWatchdogTimer = setTimeout(() => {
    wxLocationWatchdogTimer = null;
    if (!isRunning.value || h5LocationTimer) return;
    const stale =
      !wxContinuousLocationOk ||
      Date.now() - lastWxLocationChangeAt > WX_LOCATION_CHANGE_STALE_MS;
    if (stale) {
      console.log('WX: location change stale, starting assist/poll');
      scheduleWxRunLocationAssist();
      if (distance.value < 12 && stale) {
        startPollFallback();
      }
    }
  }, 8000);
  // #endif
  // #if !defined(H5) && !defined(MP-WEIXIN)
  uni.startLocationUpdate({
    ...buildWxLocationUpdateOptions(),
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
  wxContinuousLocationOk = false;
  lastWxLocationChangeAt = 0;
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
  resetRunGpsRawWindow();
};

// 2. 璺戞鏍稿績閰嶇疆
const currentMode = ref('normal'); // normal-鏅€?police-璀﹀姟 campus-鏍″洯
const isRunning = ref(false);
const duration = ref(0);
/** 寰俊灏忕▼搴?map 椤靛父瑙?setInterval 琚妭娴?鍋滆〃锛岀敤澧欓挓 + 鍒嗘鍩哄噯淇濊瘉鏃堕暱涓庡績鐜囧彲鏇存柊 */
const runActiveBaseSec = ref(0);
const runSegmentStartMs = ref(0);
const distance = ref(0); // 已跑距离（米）
/** 展示用里程：GPS 累计与轨迹长度取较大值，减少界面长期显示 0 */
const displayRunDistanceM = computed(() => {
  const acc = distance.value || 0;
  if (!isRunning.value) return acc;
  const src = getPolylineSourcePoints();
  if (src.length < 2) return acc;
  const trajM = computeTrajectoryPathLengthM(src);
  return Math.max(acc, trajM * 0.92);
});
const distanceToCheckpoint = ref('---');
const isReach = ref(false);
const stepCount = ref(0);
const currentSpeed = ref(0); // 瀹炴椂閫熷害 m/s
const maxSpeed = ref(0); // 鏈€澶ч€熷害 m/s
// 璀﹀姟涓撻」锛坱ickPoliceFinishHint 渚濊禆锛岄』鏃╀簬璺戞鏃堕挓鍑芥暟锛?
const policeTargetDistance = ref(2000); // 鍥哄畾2000绫?
const policeTargetPace = ref(6.5); // 杈炬爣閰嶉€燂細6.5鍒嗛挓/鍏噷锛堢敺鐢熸爣鍑嗭級

const policeTargetKmLabel = computed(() => {
  const km = policeTargetDistance.value / 1000;
  if (!Number.isFinite(km) || km <= 0) return '0km';
  if (km >= 1 && Math.abs(km - Math.round(km)) < 0.05) return `${Math.round(km)}km`;
  return `${km.toFixed(1)}km`;
});
let timer = null;

const isRunPaused = ref(false);
const runControlsLocked = ref(false);

const syncRunElapsedDisplay = () => {
  if (!isRunning.value || isRunPaused.value || !runSegmentStartMs.value) return;
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
  if (!isRunning.value || isRunPaused.value) return;
  const loop = () => {
    if (!isRunning.value || isRunPaused.value) {
      timer = null;
      return;
    }
    syncRunElapsedDisplay();
    tickPoliceFinishHint();
    timer = setTimeout(loop, 1000);
  };
  syncRunElapsedDisplay();
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

  if (km >= 0.02 && overall > 0 && overall < 999) {
    return overall;
  }
  if (duration.value >= 30 && km >= 0.005 && overall > 0 && overall < 999) {
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
  if (duration.value < 6 && distance.value < 10) {
    return '0.0';
  }
  if (!hasReliableGpsMovement() && currentSpeed.value < 0.2 && stepCount.value < 10) {
    return '0.0';
  }
  const v = currentSpeed.value * 3.6;
  if (v < 0.2) return '0.0';
  return v.toFixed(1);
});
// 骞冲潎閫熷害 (km/h)锛氶噷绋嬪皻鐭垨寮€璺戜笉涔呮椂缃?0锛涙棤姝ユ暟鏃舵殏涓嶅睍绀哄钩鍧囬€熷害锛岄伩鍏嶄笌婕傜Щ閲岀▼涓€璧疯瀵?
const avgSpeedKmh = computed(() => {
  if (!isRunning.value) return '0.0';
  if (duration.value < 8 || duration.value === 0) return '0.0';
  if (duration.value < 35 && distance.value < 25) return '0.0';
  if (!hasReliableGpsMovement() && distance.value < 25 && stepCount.value < 12) return '0.0';
  return ((distance.value / 1000) / (duration.value / 3600)).toFixed(1);
});

// Listener for custom location selection
uni.$on('onLocationChosen', (res) => {
  processSelectedLocation(res);
});

// 4. 瀹氫綅浼樺寲锛堝惈鏉冮檺鐢宠+鏍″洯鍥存爮锛?
const stopWxInitialLocateRetry = () => {
  if (wxInitialLocateTimer) {
    clearInterval(wxInitialLocateTimer);
    wxInitialLocateTimer = null;
  }
  wxInitialLocateAttempts = 0;
};

const startWxInitialLocateRetry = () => {
  // #ifdef MP-WEIXIN
  stopWxInitialLocateRetry();
  wxInitialLocateTimer = setInterval(() => {
    if (!isPageActive) {
      stopWxInitialLocateRetry();
      return;
    }
    if (locationState.value === 'success' && !lastLocationFixWasStale.value) {
      stopWxInitialLocateRetry();
      return;
    }
    if (wxInitialLocateAttempts >= WX_INITIAL_LOCATE_MAX) {
      stopWxInitialLocateRetry();
      if (locationState.value === 'locating') {
        locationState.value = 'fail';
      }
      return;
    }
    wxInitialLocateAttempts += 1;
    doGetLocation({ silent: true });
  }, WX_INITIAL_LOCATE_INTERVAL_MS);
  // #endif
};

const startLocationService = () => {
  getLocation();

  // #ifdef MP-WEIXIN
  startWxInitialLocateRetry();
  // #endif

  // Android Polling Optimization
  // #ifdef APP-PLUS
  if (uni.getSystemInfoSync().platform === 'android') {
      if (locationRetryTimer) clearInterval(locationRetryTimer);
      console.log('Starting Android location polling...');
      locationRetryTimer = setInterval(() => {
          if (!isPageActive) return;
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
  stopWxInitialLocateRetry();
  if (locationRetryTimer) {
    clearInterval(locationRetryTimer);
    locationRetryTimer = null;
  }
};

const onLocationStatusBarTap = () => {
  if (!showLocationStatusBar.value || isRunning.value) return;
  wxInitialLocateAttempts = 0;
  lastLocationFixWasStale.value = false;
  stopWxInitialLocateRetry();
  getLocation();
  // #ifdef MP-WEIXIN
  startWxInitialLocateRetry();
  // #endif
};

// onHide logic simulated for component
const onPageHide = () => {
    isPageActive = false;
    saveRunSession();
    stopRunSessionAutosave();
    stopLocationPolling();
};

let runSessionAutosaveTimer = null;
const startRunSessionAutosave = () => {
  stopRunSessionAutosave();
  runSessionAutosaveTimer = setInterval(() => {
    if (isRunning.value) saveRunSession();
  }, 8000);
};
const stopRunSessionAutosave = () => {
  if (runSessionAutosaveTimer != null) {
    clearInterval(runSessionAutosaveTimer);
    runSessionAutosaveTimer = null;
  }
};

watch(isRunning, (running) => {
  refreshMarkers();
  if (running) {
    resetRunSheet();
    saveRunSession();
    startRunSessionAutosave();
  } else {
    stopRunSessionAutosave();
    initRunPrepSheetHeight();
  }
});

watch(currentMode, () => {
  initRunPrepSheetHeight();
});

defineExpose({ onPageShow, onPageHide, saveRunSession, tryRestoreRunSession });

onUnmounted(() => {
  saveRunSession();
  stopRunSessionAutosave();
  if (displayPolylineRebuildTimer != null) {
    clearTimeout(displayPolylineRebuildTimer);
    displayPolylineRebuildTimer = null;
  }
  uni.$off('onLocationChosen');
  stopLocationPolling();
  clearRunTickTimer();
  stopStepCount();
  stopRealLocationTracking();
  stopCompassWatch();
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
          stopWxInitialLocateRetry();
          locationState.value = 'fail';
          uni.showModal({
            title: '需要定位权限',
            content: '新用户首次使用须允许微信获取位置信息。请在设置中开启后，点击地图上方绿色条重新定位。',
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
          stopWxInitialLocateRetry();
          locationState.value = 'fail';
          uni.showModal({
            title: '需要定位权限',
            content: '新用户首次使用须允许微信获取位置信息。请在设置中开启后，点击地图上方绿色条重新定位。',
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
  const acc = res.accuracy ?? res.originalRes?.accuracy ?? res.originalRes?.horizontalAccuracy;
  const accN = acc != null ? Number(acc) : NaN;
  if (Number.isFinite(accN)) {
    lastGpsAccuracyM.value = accN;
  }
  lat.value = res.latitude;
  lng.value = res.longitude;

  const dir =
    res.direction ??
    res.originalRes?.direction ??
    res.originalRes?.heading;
  if (dir != null) applyMapHeading(dir);

  // Cache location for faster load next time
  uni.setStorageSync('lastLocation', { lat: res.latitude, lng: res.longitude });

  patchCurrentLocationMarker();
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
    msg = 'H5 定位需 HTTPS';
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
  
  // 鏇存柊鐘舵€佷负澶辫触
  locationState.value = 'fail';
};

const doGetLocation = async (options = {}) => {
  const silent = options.silent === true;
  if (locationPromise) return locationPromise;

  locationPromise = (async () => {
    const raceGetLocation = (opts = {}) => {
      const locateMs = opts.timeoutMs ?? 22000;
      const locOpts = opts.locationOptions ?? {};
      return Promise.race([
        getCurrentLocation(locOpts),
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
    const isFirstTimeLocate = !lastLoc;

    if (lastLoc) {
      lat.value = lastLoc.lat;
      lng.value = lastLoc.lng;
      refreshMarkers();
    } else if (!silent) {
      uni.showLoading({ title: '定位中，请稍候…' });
    }

    locationState.value = 'locating';

    const fetchOnce = async (accurate) => {
      const timeoutMs = accurate ? 22000 : 14000;
      const locationOptions = accurate ? {} : { fastFix: true };
      return raceGetLocation({ timeoutMs, locationOptions });
    };

    const fetchWithRetries = async () => {
      let res;
      // #ifdef MP-WEIXIN
      if (isFirstTimeLocate) {
        try {
          res = await fetchOnce(false);
        } catch (e1) {
          await new Promise((r) => setTimeout(r, 400));
          try {
            res = await fetchOnce(true);
          } catch (e2) {
            if (isPageActive) {
              await new Promise((r) => setTimeout(r, 520));
              res = await fetchOnce(true);
            } else {
              throw e2;
            }
          }
        }
      } else {
        try {
          res = await fetchOnce(true);
        } catch (e1) {
          if (isPageActive) {
            await new Promise((r) => setTimeout(r, 520));
            res = await fetchOnce(true);
          } else {
            throw e1;
          }
        }
      }
      // #endif
      // #ifndef MP-WEIXIN
      res = await fetchOnce(true);
      // #endif
      return res;
    };

    try {
      const res = await fetchWithRetries();

      if (!isPageActive) {
        if (res && res.success) {
          handleLocationSuccess(res);
          locationState.value = 'success';
          stopWxInitialLocateRetry();
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
        lastLocationFixWasStale.value = false;
        handleLocationSuccess(res);
        refreshMarkers();
        stopWxInitialLocateRetry();
        if (!silent && isFirstTimeLocate) {
          uni.showToast({ title: '定位成功', icon: 'none' });
        }
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
        if (!silent) {
          handleLocationError(err?.originalErr || err);
        }
        locationState.value = 'locating';
      } else {
        lastLocationFixWasStale.value = true;
        if (!silent) {
          uni.showToast({ title: '刷新定位失败，暂用上次位置，请到室外后重试', icon: 'none', duration: 2800 });
        }
        locationState.value = 'success';
      }
    } finally {
      if (!silent) {
        uni.hideLoading();
      }
      locationPromise = null;
    }
  })();

  return locationPromise;
};

const handleRelocate = () => {
  wxInitialLocateAttempts = 0;
  stopWxInitialLocateRetry();
  doGetLocation().then(() => {
    // #ifdef MP-WEIXIN
    startWxInitialLocateRetry();
    // #endif
  });
};

const locationStatusText = computed(() => {
  switch (locationState.value) {
    case 'locating':
      if (!hasPlausibleCoords()) {
        return '首次定位较慢，请到室外 · 点此重试';
      }
      return '正在精确定位… · 点此重试';
    case 'success':
      if (lastLocationFixWasStale.value) {
        return '已用上次位置 · 点此重新定位';
      }
      if (gpsRunReady.value) {
        return 'GPS 已就绪';
      }
      if (Number.isFinite(lastGpsAccuracyM.value) && lastGpsAccuracyM.value > GPS_RUN_READY_ACCURACY_M) {
        return `正在精确定位…（精度约 ${Math.round(lastGpsAccuracyM.value)}m）· 点此刷新`;
      }
      return '正在精确定位… · 点此刷新';
    case 'fail':
      return '定位失败 · 请开定位权限并到室外 · 点此重试';
    default:
      return '等待定位 · 点此重试';
  }
});

const runMileageHint = computed(() => {
  if (!isRunning.value) return '';
  if (distance.value >= 12) return '';
  const acc = lastGpsAccuracyM.value;
  if (locationState.value !== 'success') {
    return '定位未完成，请到室外开阔处';
  }
  if (Number.isFinite(acc) && acc > 80) {
    return 'GPS 信号较弱，请到空旷处再跑';
  }
  if (stepCount.value >= 10 && duration.value >= 6 && !hasRecentGpsMotionEvidence()) {
    return '正在校准 GPS，请正常跑动…';
  }
  if (duration.value >= 8 && stepCount.value < 4) {
    return '请正常跑动，原地不动不计里程';
  }
  if (duration.value >= 4 && distance.value < 8) {
    return '正在校准 GPS…';
  }
  return '';
});

const mapTopHintText = computed(() => {
  if (isRunning.value && runMileageHint.value) return runMileageHint.value;
  return locationStatusText.value;
});

const showMapTopHintBar = computed(
  () =>
    !hideMapCoverLayer.value &&
    ((isRunning.value && !!runMileageHint.value) || showLocationStatusBar.value)
);

const showMapTopHintTappable = computed(
  () => showLocationStatusBar.value && !(isRunning.value && runMileageHint.value)
);

const runPrepSheetHeightPx = ref(280);

const showRunPrepSheet = computed(() => !isRunning.value);

const runPrepSheetTitle = computed(() => {
  if (currentMode.value === 'campus') return '校园打卡 · 选择打卡点';
  if (currentMode.value === 'police') {
    return teacherRunTask.value ? `${teacherRunTask.value} · 任务要求` : '专项跑 · 任务要求';
  }
  return '普通跑步 · 准备开跑';
});

const canStartFromPrepSheet = computed(() => {
  if (currentMode.value === 'campus') return !!checkpoint.value?.name;
  if (currentMode.value === 'police') return !!taskId.value && !taskSubmitHint.value;
  return true;
});

const runPrepSheetStyle = computed(() => ({
  height: `${runPrepSheetHeightPx.value}px`,
  paddingBottom: `${runSheetSafeBottomPx.value}px`
}));

const initRunPrepSheetHeight = () => {
  try {
    const sys = uni.getSystemInfoSync();
    const h = sys.windowHeight || 667;
    const safe = sys.safeAreaInsets?.bottom || 0;
    const mode = currentMode.value;
    const ratio = mode === 'campus' ? 0.38 : mode === 'police' ? 0.34 : 0.32;
    runPrepSheetHeightPx.value = Math.round(h * ratio + safe * 0.35);
  } catch (e) {
    const mode = currentMode.value;
    runPrepSheetHeightPx.value = mode === 'campus' ? 320 : mode === 'police' ? 300 : 280;
  }
};

const formatHudDuration = (sec) => {
  const s = Math.max(0, Math.floor(Number(sec) || 0));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const ss = s % 60;
  const pad = (n) => n.toString().padStart(2, '0');
  if (h > 0) return `${pad(h)}:${pad(m)}:${pad(ss)}`;
  return `${pad(m)}:${pad(ss)}`;
};

const formatHudPace = (paceMinPerKm) => {
  const p = Number(paceMinPerKm);
  if (!Number.isFinite(p) || p <= 0 || p >= 999) return "--'--\"";
  const totalSec = Math.round(p * 60);
  const m = Math.floor(totalSec / 60);
  const ss = totalSec % 60;
  return `${m}'${ss.toString().padStart(2, '0')}"`;
};

const hudAvgPace = computed(() => formatHudPace(currentPace.value));
const hudDistanceKm = computed(() => (displayRunDistanceM.value / 1000).toFixed(2));
const runHudCalories = computed(() =>
  Math.max(0, Math.round((displayRunDistanceM.value / 1000) * 60))
);

/** 跑步中底部可上拉面板（类似 Keep） */
const runSheetSafeBottomPx = ref(0);
const runSheetSnap = ref({ collapsed: 200, expanded: 380 });
const runSheetHeightPx = ref(200);
const runSheetExpanded = ref(false);
const runSheetDragging = ref(false);
let runSheetDragStartY = 0;
let runSheetDragStartH = 200;
let runSheetDragStartAt = 0;
let runSheetDragLastY = 0;

const runSheetExpandProgress = computed(() => {
  const min = runSheetSnap.value.collapsed;
  const max = runSheetSnap.value.expanded;
  const range = max - min;
  if (range <= 0) return runSheetExpanded.value ? 1 : 0;
  return Math.max(0, Math.min(1, (runSheetHeightPx.value - min) / range));
});

const runSheetCompactStyle = computed(() => {
  const p = runSheetExpandProgress.value;
  return {
    opacity: Math.max(0, 1 - p * 1.35)
  };
});

const runSheetExpandedLayerStyle = computed(() => {
  const p = runSheetExpandProgress.value;
  const fade = Math.max(0, Math.min(1, (p - 0.08) / 0.72));
  return { opacity: fade };
});

const runSheetControlsStyle = computed(() => {
  const p = runSheetExpandProgress.value;
  return {
    opacity: 0.78 + p * 0.22
  };
});

const initRunSheetSnap = () => {
  try {
    const sys = uni.getSystemInfoSync();
    const h = sys.windowHeight || 667;
    const safe = sys.safeAreaInsets?.bottom || 0;
    runSheetSafeBottomPx.value = safe;
    runSheetSnap.value = {
      collapsed: Math.round(h * 0.30 + safe * 0.35),
      expanded: Math.round(h * 0.54)
    };
    if (!runSheetDragging.value) {
      runSheetHeightPx.value = runSheetExpanded.value
        ? runSheetSnap.value.expanded
        : runSheetSnap.value.collapsed;
    }
  } catch (e) {
    runSheetSnap.value = { collapsed: 200, expanded: 380 };
  }
};

const runSheetStyle = computed(() => ({
  height: `${runSheetHeightPx.value}px`,
  paddingBottom: `${runSheetSafeBottomPx.value}px`
}));

const recenterFloatStyle = computed(() => {
  let bottomPx = 120;
  if (isRunning.value) {
    bottomPx = runSheetHeightPx.value + 12;
  } else if (showRunPrepSheet.value) {
    bottomPx = runPrepSheetHeightPx.value + 12;
  }
  return { bottom: `${bottomPx}px` };
});

const snapRunSheetHeight = (heightPx) => {
  const min = Math.round(runSheetSnap.value.collapsed * 0.82);
  const max = runSheetSnap.value.expanded;
  return Math.max(min, Math.min(max, heightPx));
};

const settleRunSheetHeight = (velocityPxMs = 0) => {
  const mid = (runSheetSnap.value.collapsed + runSheetSnap.value.expanded) / 2;
  let expand = runSheetHeightPx.value >= mid;
  if (Math.abs(velocityPxMs) > 0.28) {
    expand = velocityPxMs > 0;
  } else if (Math.abs(runSheetHeightPx.value - mid) < 18) {
    expand = runSheetExpanded.value;
  }
  runSheetExpanded.value = expand;
  runSheetHeightPx.value = expand ? runSheetSnap.value.expanded : runSheetSnap.value.collapsed;
};

const toggleRunSheetExpand = () => {
  runSheetExpanded.value = !runSheetExpanded.value;
  runSheetHeightPx.value = runSheetExpanded.value
    ? runSheetSnap.value.expanded
    : runSheetSnap.value.collapsed;
};

const onRunSheetTouchStart = (e) => {
  if (!e.touches?.length) return;
  runSheetDragging.value = true;
  runSheetDragStartY = e.touches[0].clientY;
  runSheetDragStartH = runSheetHeightPx.value;
  runSheetDragStartAt = Date.now();
  runSheetDragLastY = runSheetDragStartY;
};

const onRunSheetTouchMove = (e) => {
  if (!runSheetDragging.value || !e.touches?.length) return;
  const y = e.touches[0].clientY;
  const dy = runSheetDragStartY - y;
  runSheetHeightPx.value = snapRunSheetHeight(runSheetDragStartH + dy);
  runSheetDragLastY = y;
};

const onRunSheetTouchEnd = () => {
  if (!runSheetDragging.value) return;
  const now = Date.now();
  const dt = Math.max(16, now - runSheetDragStartAt);
  const velocity = (runSheetDragStartY - runSheetDragLastY) / dt;
  runSheetDragging.value = false;
  settleRunSheetHeight(velocity);
};

const resetRunSheet = () => {
  runSheetDragging.value = false;
  runSheetExpanded.value = false;
  runSheetHeightPx.value = runSheetSnap.value.collapsed;
};

const pauseRun = () => {
  if (!isRunning.value || isRunPaused.value) return;
  syncRunElapsedDisplay();
  runActiveBaseSec.value = duration.value;
  runSegmentStartMs.value = 0;
  isRunPaused.value = true;
  currentSpeed.value = 0;
  clearRunTickTimer();
  stopStepCount();
  saveRunSession();
};

const resumeRunPaused = () => {
  if (!isRunning.value || !isRunPaused.value) return;
  isRunPaused.value = false;
  runSegmentStartMs.value = Date.now();
  scheduleRunClock();
  startStepCount();
  saveRunSession();
};

const toggleRunPause = () => {
  if (runControlsLocked.value) {
    uni.showToast({ title: '已锁定，请先解锁', icon: 'none' });
    return;
  }
  if (isRunPaused.value) resumeRunPaused();
  else pauseRun();
};

const toggleRunLock = () => {
  runControlsLocked.value = !runControlsLocked.value;
  uni.showToast({
    title: runControlsLocked.value ? '已锁定，防误触' : '已解锁',
    icon: 'none'
  });
};

const onCompactStopTap = () => {
  if (runControlsLocked.value) {
    uni.showToast({ title: '已锁定，请先解锁', icon: 'none' });
    return;
  }
  stopRun();
};
const mainStartLabel = computed(() => {
  if (currentMode.value === 'campus') return '开始打卡';
  if (currentMode.value === 'police') return taskId.value ? '开始任务跑步' : '请先选择任务';
  return '开始跑步';
});

const stopRunLabel = computed(() => {
  if (currentMode.value === 'campus') return '结束打卡';
  if (currentMode.value === 'police') return '结束训练';
  return '结束跑步';
});

const runHudProgressPct = computed(() => {
  if (currentMode.value === 'police') return policeProgress.value;
  if (currentMode.value === 'normal') return normalProgress.value;
  return 0;
});

const goRunHistory = () => {
  uni.navigateTo({ url: '/pages/history/history' });
};

const recenterMap = () => {
  doGetLocation({ silent: false });
};

const onMainStartTap = () => {
  if (!canStartFromPrepSheet.value) {
    if (currentMode.value === 'police' && taskSubmitHint.value) {
      uni.showToast({ title: taskSubmitHint.value, icon: 'none' });
    } else if (currentMode.value === 'police') {
      uni.showToast({ title: '请先选择跑步任务', icon: 'none' });
    }
    return;
  }
  if (currentMode.value === 'campus' && !checkpoint.value?.name) {
    uni.showToast({ title: '请先选择校园打卡点', icon: 'none' });
    return;
  }
  if (currentMode.value === 'normal') startNormalRun();
  else if (currentMode.value === 'police') startPoliceRun();
  else if (checkpoint.value?.name) startCampusRun();
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
    width: 24,
    height: 24,
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

const RUN_SESSION_KEY = 'activeRunSessionV1';

const saveRunSession = () => {
  if (!isRunning.value) {
    uni.removeStorageSync(RUN_SESSION_KEY);
    return;
  }
  syncRunElapsedDisplay();
  uni.setStorageSync(RUN_SESSION_KEY, {
    v: 1,
    savedAt: Date.now(),
    currentMode: currentMode.value,
    duration: duration.value,
    distance: distance.value,
    stepCount: stepCount.value,
    runActiveBaseSec: runActiveBaseSec.value,
    runSegmentStartMs: runSegmentStartMs.value,
    isRunPaused: isRunPaused.value,
    trajectoryPoints: trajectoryPoints.value,
    displayTrackPoints: displayTrackPoints.value,
    lat: lat.value,
    lng: lng.value,
    gpsAcceptedPointCount,
    startFaceUrl: startFaceUrl.value || null,
    taskId: taskId.value,
    taskType: taskType.value,
    taskRunLocked: taskRunLocked.value,
    taskDescription: taskDescription.value,
    taskMinDurationSec: taskMinDurationSec.value,
    policeTargetDistance: policeTargetDistance.value,
    policeTargetPace: policeTargetPace.value,
    teacherRunTask: teacherRunTask.value,
    checkpoint: checkpoint.value,
    checkpointName: checkpointName.value
  });
};

const clearRunSession = () => {
  uni.removeStorageSync(RUN_SESSION_KEY);
};

const tryRestoreRunSession = () => {
  if (isRunning.value) return false;
  let snap = uni.getStorageSync(RUN_SESSION_KEY);
  if (!snap) return false;
  if (typeof snap === 'string') {
    try {
      snap = JSON.parse(snap);
    } catch (e) {
      uni.removeStorageSync(RUN_SESSION_KEY);
      return false;
    }
  }
  if (!snap || snap.v !== 1 || !snap.savedAt) return false;
  if (Date.now() - snap.savedAt > 2 * 60 * 60 * 1000) {
    uni.removeStorageSync(RUN_SESSION_KEY);
    return false;
  }
  currentMode.value = snap.currentMode || 'normal';
  isRunPaused.value = !!snap.isRunPaused;
  const awaySec = Math.max(0, Math.floor((Date.now() - snap.savedAt) / 1000));
  if (isRunPaused.value) {
    duration.value = snap.duration || 0;
    runActiveBaseSec.value = duration.value;
    runSegmentStartMs.value = 0;
  } else {
    duration.value = (snap.duration || 0) + awaySec;
    runActiveBaseSec.value = duration.value;
    runSegmentStartMs.value = Date.now();
  }
  distance.value = snap.distance || 0;
  stepCount.value = snap.stepCount || 0;
  trajectoryPoints.value = Array.isArray(snap.trajectoryPoints) ? snap.trajectoryPoints : [];
  displayTrackPoints.value = Array.isArray(snap.displayTrackPoints)
    ? snap.displayTrackPoints
    : trajectoryPoints.value.map((p) => ({
        latitude: p.latitude,
        longitude: p.longitude,
        timestamp: p.timestamp,
        speed: p.speed
      }));
  runPolyline.value.points = [];
  lat.value = snap.lat ?? lat.value;
  lng.value = snap.lng ?? lng.value;
  gpsAcceptedPointCount = snap.gpsAcceptedPointCount || 0;
  if (snap.startFaceUrl) startFaceUrl.value = snap.startFaceUrl;
  if (snap.taskId) {
    taskId.value = String(snap.taskId);
    taskRunLocked.value = !!snap.taskRunLocked;
    taskType.value = snap.taskType || 'run';
    taskDescription.value = snap.taskDescription || '';
    taskMinDurationSec.value = Number(snap.taskMinDurationSec) || 0;
    teacherRunTask.value = snap.teacherRunTask || teacherRunTask.value;
  }
  if (snap.policeTargetDistance) policeTargetDistance.value = snap.policeTargetDistance;
  if (snap.policeTargetPace) policeTargetPace.value = snap.policeTargetPace;
  if (snap.checkpoint && snap.checkpoint.name) {
    const cp = snap.checkpoint;
    selectCheckpoint({
      name: cp.name,
      latitude: cp.lat ?? cp.latitude,
      longitude: cp.lng ?? cp.longitude,
      radius: cp.radius,
      id: cp.id
    });
  }
  isRunning.value = true;
  runEndMarker.value = null;
  if (trajectoryPoints.value.length > 0) {
    const p0 = trajectoryPoints.value[0];
    runStartMarker.value = createRunPointMarker(2, p0.latitude, p0.longitude, '起');
  }
  refreshMarkers();
  scheduleRebuildDisplayPolyline(true);
  beginRunTrackingAfterFaceDefer();
  uni.showToast({ title: '已恢复上次跑步数据', icon: 'none', duration: 2200 });
  return true;
};

// 7. 切换跑步模式（普通/专项/校园）
const switchMode = (mode) => {
  if (taskRunLocked.value) {
    uni.showToast({ title: '任务跑步模式已锁定', icon: 'none' });
    return;
  }
  if (mode === 'police' && !hasRunTaskAvailable.value) {
    uni.showToast({ title: '暂无进行中的跑步任务', icon: 'none' });
    return;
  }
  if (currentMode.value === mode) return;
  if (isRunning.value) {
    uni.showModal({
      title: '跑步进行中',
      content: '切换模式会清空本次跑步数据。请先点击「结束跑步」，或留在当前模式继续跑。',
      showCancel: false,
      confirmText: '知道了'
    });
    return;
  }
  const wasRunning = isRunning.value;
  const hadStepListener = !!accelerometerCallback;
  const hadLocTracking = !!(locationCallback || h5LocationTimer || wxRunAssistTimer);
  isRunning.value = false;
  clearRunTickTimer();
  runActiveBaseSec.value = 0;
  runSegmentStartMs.value = 0;
  if (wasRunning || hadStepListener) stopStepCount();
  if (wasRunning || hadLocTracking) stopRealLocationTracking();
  duration.value = 0;
  distance.value = 0;
  stepCount.value = 0;
  runPolyline.value.points = [];
  trajectoryPoints.value = [];
  displayTrackPoints.value = [];
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
      width: 24,
      height: 24,
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
  if (mode === 'police' && !taskId.value) {
    if (activeRunTasks.value.length === 1) {
      selectRunTask(activeRunTasks.value[0]);
    }
  } else if (mode !== 'police') {
    if (!taskRunLocked.value) {
      taskId.value = null;
      taskType.value = null;
      taskSubmitHint.value = '';
    }
  }
  initRunPrepSheetHeight();
};

// 8. 步数统计（加速度传感器，step-counter 步频带通计步）
const ensureRunStepCounter = () => {
  if (!runStepCounter) {
    runStepCounter = createStepCounter();
  }
  return runStepCounter;
};

const startAccelerometerWithRetry = (retryCount) => {
  const MAX_RETRIES = 3;
  const intervals = ['game', 'game', 'normal'];
  const interval = intervals[Math.min(retryCount, intervals.length - 1)];

  const bindAccelerometerListener = () => {
    if (accelerometerCallback) {
      try {
        uni.offAccelerometerChange(accelerometerCallback);
      } catch (e) {
        console.warn('offAccelerometerChange:', e);
      }
    }
    const counter = ensureRunStepCounter();
    counter.reset();
    counter.setStepCount(stepCount.value);
    accelerometerCallback = (res) => {
      if (!isRunning.value || isRunPaused.value) return;
      const now = Date.now();
      const result = counter.feed(res.x, res.y, res.z, now);
      if (result.stepped) {
        stepCount.value = result.steps;
        noteStepMotion(now);
      }
    };
    uni.onAccelerometerChange(accelerometerCallback);
  };

  uni.startAccelerometer({
    interval,
    success: () => {
      bindAccelerometerListener();
      resetRunMotionEvidence();
      stepFusionSkewSince = 0;
      stepFusionLastAdjustAt = 0;
    },
    fail: (err) => {
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
        uni.showToast({ title: '传感器启动中，请稍候…', icon: 'none', duration: 1000 });
        setTimeout(() => startStepCount(retryCount + 1), 800);
      } else {
        uni.showModal({
          title: '步数统计启动失败',
          content:
            '无法启动加速度传感器。请在系统设置与微信「小程序」中允许相关权限；若已开启，请完全退出小程序后重试。',
          showCancel: false
        });
      }
    }
  });
};

const startStepCount = (retryCount = 0) => {
  uni.stopAccelerometer({
    complete: () => {
      setTimeout(() => startAccelerometerWithRetry(retryCount), 200);
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
  resetRunMotionEvidence();
  stepFusionSkewSince = 0;
  stepFusionLastAdjustAt = 0;
};

/**
 * 浜鸿劯鎷嶇収 / chooseMedia 鍒氱粨鏉熸椂锛岄儴鍒嗗井淇＄湡鏈洪渶杩囦竴灏忔鍐嶈皟 startLocationUpdate锛屽惁鍒?onLocationChange 涓嶅洖璋冿紙姝ユ暟銆佸閽熴€侀噷绋嬪潎涓嶆定锛夈€?
 * 娴嬭瘯鍙嶉銆岀涓€娆℃媿鐓у悗寮€濮嬭窇姝ョ粺璁′笉宸ヤ綔锛涚偣缁撴潫璺戞鍐嶅彇娑堝悗姝ｅ父銆嶅嵆鍏稿瀷鏃跺簭闂銆?
 */
const beginRunTrackingAfterFaceDefer = () => {
  const go = () => {
    if (!isRunning.value) return;
    startRealLocationTracking();
    if (!isRunPaused.value) {
      startStepCount();
      scheduleRunClock();
    }
  };
  nextTick(() => {
    setTimeout(go, 400);
  });
};

// 9. 开始跑步（分三种模式）
// Common start logic
const initializeRunState = () => {
  if (locationState.value !== 'success') {
    uni.showToast({ title: '定位未成功，无法开始', icon: 'none' });
    doGetLocation(); // Try to refresh
    return false;
  }

  isRunning.value = true;
  isRunPaused.value = false;
  runControlsLocked.value = false;
  duration.value = 0;
  runActiveBaseSec.value = 0;
  runSegmentStartMs.value = Date.now();
  distance.value = 0;
  stepCount.value = 0;
  currentSpeed.value = 0;
  endFaceUrl.value = null;
  gpsAcceptedPointCount = 0;
  resetRunMotionEvidence();
  stepFusionSkewSince = 0;
  stepFusionLastAdjustAt = 0;
  if (runTrajectoryFilter) {
    runTrajectoryFilter.reset();
  } else {
    runTrajectoryFilter = createTrajectoryFilter();
  }
  if (runStepCounter) {
    runStepCounter.reset();
  }
  
  // Clear previous trajectory
  runPolyline.value.points = [];
  trajectoryPoints.value = [];
  displayTrackPoints.value = [];
  runEndMarker.value = null;
  runLocationSmooth = null;
  lastRawLocationSample = null;
  resetRunGpsRawWindow();

  // Add start point immediately to avoid delay in drawing line
  if (lat.value && lng.value) {
    const startPoint = { latitude: lat.value, longitude: lng.value, timestamp: Date.now(), speed: 0 };
    trajectoryPoints.value.push(startPoint);
    displayTrackPoints.value.push({ ...startPoint });
    runStartMarker.value = createRunPointMarker(2, lat.value, lng.value, '起');
    refreshMarkers();
    scheduleRebuildDisplayPolyline(true);
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
      title: '需要相机权限',
      content: '无法打开相机。请在系统设置与微信「小程序」权限中允许使用摄像头后重试。',
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
      ? `${errMsg}\n\n可稍后重试。未完成人脸验证无法开始或结束跑步。`
      : '请检查相机权限、存储空间是否正常，或稍后重试。未完成人脸验证无法开始或结束跑步。',
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
  faceCameraErrorText.value = '';
  faceCameraContext = null;
  if (resolver) resolver(!!result);
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
  faceCameraErrorText.value = '相机不可用，请检查摄像头权限后重试';
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
      title: '未拍到照片',
      content: '请重新拍摄一张正面照。',
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
    if (!url || typeof url !== 'string') {
      uni.showModal({
        title: '上传失败',
        content: '服务器未返回照片地址，请检查网络后重试。',
        showCancel: false,
        confirmText: '知道了'
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
    const msg = e?.message || e?.detail || '上传失败，请稍后重试';
    uni.showModal({
      title: '上传失败',
      content: msg,
      showCancel: false,
      confirmText: '知道了'
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
    faceCameraErrorText.value = '相机未就绪，请稍候再试';
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
      faceCameraErrorText.value = '拍照失败，请重试';
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
        openInlineFaceCamera(phase).then((ok) => resolve(!!ok));
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
    uni.showToast({ title: '定位未成功，请稍候或点击地图旁定位按钮刷新后再试', icon: 'none' });
    doGetLocation();
    return;
  }
  if (lastLocationFixWasStale.value) {
    uni.showToast({
      title: '当前为历史定位，建议先点地图旁「定位」刷新或到室外再跑，以免里程统计偏少',
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
  if (!taskId.value) {
    uni.showToast({ title: '请先选择或进入跑步任务', icon: 'none' });
    return;
  }
  if (taskSubmitHint.value) {
    uni.showToast({ title: taskSubmitHint.value, icon: 'none' });
    return;
  }
  if (locationState.value !== 'success') {
    uni.showToast({ title: '定位未成功，请稍候或点击地图旁定位按钮刷新后再试', icon: 'none' });
    doGetLocation();
    return;
  }
  if (lastLocationFixWasStale.value) {
    uni.showToast({
      title: '当前为历史定位，建议先点地图旁「定位」刷新或到室外再跑，以免里程统计偏少',
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
    uni.showToast({ title: '定位未成功，请稍候或点击地图旁定位按钮刷新后再试', icon: 'none' });
    doGetLocation();
    return;
  }
  if (lastLocationFixWasStale.value) {
    uni.showToast({
      title: '当前为历史定位，建议先点地图旁「定位」刷新或到室外再跑，以免里程统计偏少',
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
  isRunPaused.value = false;
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
      uni.showToast({ title: '页面跳转失败', icon: 'none' });
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
  uni.showLoading({ title: '正在核验运动数据...' });
  try {
    const res = await submitActivity(runData);
    uni.hideLoading();
    console.log('Submit success:', res);
    uni.setStorageSync('tempRunResult', {
      ...res,
      display_mode: currentMode.value,
      campus_reached: currentMode.value === 'campus' ? !!isReach.value : undefined,
      campus_checkpoint: currentMode.value === 'campus' ? (checkpoint.value?.name || '') : ''
    });
    // 同时保存轨迹数据用于结算页展示
    const trajForDisplay = getPolylineSourcePoints();
    uni.setStorageSync('tempRunTrajectory', {
      points: trajForDisplay.map((p) => ({ latitude: p.latitude, longitude: p.longitude })),
      startLat: trajForDisplay.length > 0 ? trajForDisplay[0].latitude : lat.value,
      startLng: trajForDisplay.length > 0 ? trajForDisplay[0].longitude : lng.value,
      endLat: lat.value,
      endLng: lng.value
    });
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
  isRunPaused.value = false;
  runControlsLocked.value = false;
  syncRunElapsedDisplay();
  if (hasPlausibleCoords()) {
    runEndMarker.value = createRunPointMarker(3, lat.value, lng.value, '终');
    refreshMarkers();
  }
  isRunning.value = false;
  clearRunSession();
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
  if (!taskId.value && getPolylineSourcePoints().length >= 2) {
    const trajM = computeTrajectoryPathLengthM(getPolylineSourcePoints());
    if (filtM < 20) {
      reportM = Math.max(filtM, trajM * 0.92);
    } else {
      const relaxedTraj = trajM * 0.94;
      reportM = Math.max(filtM, Math.min(relaxedTraj, filtM * 1.28));
    }
  }
  if (!taskId.value && reportM < 30 && stepCount.value >= 40) {
    const strideM = currentMode.value === 'police' ? 0.72 : 0.78;
    const stepEstM = stepCount.value * strideM;
    reportM = Math.max(reportM, Math.min(stepEstM, stepCount.value * 0.55));
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

<style scoped lang="scss">
@import '@/styles/run-sport-theme.scss';

.run.run-sport {
  padding: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--run-page-bg, #f5f7fa);
  box-sizing: border-box;
}

.run-map-section {
  flex: 1;
  min-height: 0;
  position: relative;
  width: 100%;
}

.task-mode-hint {
  padding: 16rpx 24rpx;
  margin-bottom: 20rpx;
  background: #f0faf6;
  border-radius: 12rpx;
}
.task-mode-hint-text {
  font-size: 28rpx;
  color: #0d8f6e;
  font-weight: 600;
  line-height: 1.5;
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
  max-width: 92%;
}
.location-status-tappable {
  background-color: rgba(32, 201, 151, 0.92);
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
  background: #1976d2;
  border: 3rpx solid #fff;
  box-shadow: 0 0 0 2rpx #0d47a1;
  clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
  border-radius: 0;
  width: 18rpx;
  height: 22rpx;
}
.legend-pin-start {
  background: #2196f3;
  box-shadow: 0 0 0 2rpx #1565c0;
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

.overview-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 16rpx;
  padding: 14rpx 18rpx;
  margin-bottom: 0;
  position: fixed;
  top: calc(44px + var(--status-bar-height, 20px) + 16rpx);
  right: 20rpx;
  z-index: 100;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.15);
  min-width: 220rpx;
}
.overview-title {
  font-size: 26rpx;
  font-weight: bold;
  color: #333;
  display: inline;
  margin-right: 16rpx;
}
.overview-meta {
  font-size: 24rpx;
  color: #666;
  display: inline-flex;
  gap: 24rpx;
  flex-wrap: wrap;
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
.map.map-full {
  width: 100%;
  height: 100%;
  min-height: 360rpx;
  border-radius: 0;
  margin-bottom: 0;
  overflow: hidden;
  position: relative;
  box-sizing: border-box;
}

/* cover-view 浮层（微信小程序地图上层） */
.cover-panel {
  position: absolute;
}
.sport-dash {
  left: 24rpx;
  right: 24rpx;
  top: 16rpx;
  display: flex;
  flex-direction: row;
  background-color: rgba(255, 255, 255, 0.94);
  border-radius: 20rpx;
  padding: 24rpx;
  box-sizing: border-box;
  box-shadow: 0 8rpx 28rpx rgba(0, 0, 0, 0.08);
}
.sport-dash-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.sport-dash-label {
  color: #666;
  font-size: 24rpx;
}
.sport-dash-km-row {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  margin-top: 8rpx;
}
.sport-dash-km {
  color: #20c997;
  font-size: 64rpx;
  font-weight: bold;
  line-height: 1;
}
.sport-dash-unit {
  color: #333;
  font-size: 28rpx;
  margin-left: 8rpx;
  margin-bottom: 8rpx;
}
.sport-dash-sub {
  color: #999;
  font-size: 22rpx;
  margin-top: 8rpx;
}
.sport-dash-link {
  display: flex;
  flex-direction: column;
  justify-content: center;
  flex-shrink: 0;
  padding-left: 20rpx;
}
.sport-dash-link-t {
  color: #20c997;
  font-size: 26rpx;
  font-weight: 600;
}
.sport-mode-pill {
  left: 32rpx;
  right: 32rpx;
  bottom: 200rpx;
  display: flex;
  flex-direction: row;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 999rpx;
  padding: 6rpx;
  box-sizing: border-box;
  box-shadow: 0 6rpx 20rpx rgba(0, 0, 0, 0.08);
}
.sport-pill-item {
  flex: 1;
  text-align: center;
  color: #666;
  font-size: 24rpx;
  padding: 16rpx 8rpx;
  border-radius: 999rpx;
}
.sport-pill-item.active {
  background-color: #20c997;
  color: #ffffff;
  font-weight: bold;
}
.sport-task-hint {
  left: 32rpx;
  right: 32rpx;
  bottom: 200rpx;
  background-color: #f0faf6;
  border-radius: 16rpx;
  padding: 20rpx;
}
.sport-task-hint-t {
  color: #0d8f6e;
  font-size: 26rpx;
  text-align: center;
}
.sport-start-fab {
  left: 48rpx;
  right: 48rpx;
  bottom: 48rpx;
  width: auto;
  height: auto;
  margin-left: 0;
}
.sport-start-inner {
  width: 100%;
  height: 96rpx;
  border-radius: 48rpx;
  background-color: #20c997;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10rpx 24rpx rgba(32, 201, 151, 0.35);
}
.sport-start-text {
  color: #ffffff;
  font-size: 32rpx;
  font-weight: bold;
}
.sport-recenter-float {
  position: absolute;
  right: 24rpx;
  z-index: 120;
  width: 72rpx;
  height: 72rpx;
  border-radius: 36rpx;
  background-color: rgba(255, 255, 255, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6rpx 20rpx rgba(0, 0, 0, 0.1);
  transition: bottom 0.32s cubic-bezier(0.22, 1, 0.36, 1);
}
.sport-recenter-icon {
  color: #333333;
  font-size: 36rpx;
  line-height: 1;
}

/* 跑步中底部上拉面板 */
.run-bottom-sheet {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 130;
  box-sizing: border-box;
  background: linear-gradient(180deg, #252b38 0%, #141820 100%);
  border-top-left-radius: 28rpx;
  border-top-right-radius: 28rpx;
  box-shadow: 0 -12rpx 40rpx rgba(0, 0, 0, 0.22);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: height 0.34s cubic-bezier(0.22, 1, 0.36, 1);
}
.run-bottom-sheet--dragging {
  transition: none;
}
.run-bottom-sheet--expanded .run-sheet-handle {
  background-color: rgba(255, 255, 255, 0.42);
}
.run-sheet-handle-wrap {
  padding: 16rpx 0 8rpx;
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}
.run-sheet-handle {
  width: 72rpx;
  height: 8rpx;
  border-radius: 4rpx;
  background-color: rgba(255, 255, 255, 0.32);
  transition: background-color 0.24s ease;
}
.run-sheet-paused-chip {
  align-self: center;
  margin: 0 0 4rpx;
  padding: 4rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(255, 179, 71, 0.16);
  color: #ffb347;
  font-size: 22rpx;
  font-weight: 600;
  flex-shrink: 0;
}
.run-sheet-body {
  position: relative;
  flex: 1;
  min-height: 120rpx;
  overflow: hidden;
}
.run-sheet-layer {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  display: flex;
  box-sizing: border-box;
}
.run-sheet-layer--compact {
  flex-direction: row;
  align-items: center;
  padding: 4rpx 24rpx 8rpx;
  pointer-events: none;
}
.run-sheet-layer--expanded {
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 0 32rpx 8rpx;
  pointer-events: none;
}
.run-sheet-metric {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.run-sheet-metric-val {
  color: #2ee6b8;
  font-size: 52rpx;
  font-weight: 700;
  line-height: 1.1;
}
.run-sheet-metric-val--dim {
  color: #f2f4f8;
  font-size: 36rpx;
  font-weight: 600;
}
.run-sheet-metric-lbl {
  color: rgba(255, 255, 255, 0.55);
  font-size: 22rpx;
  margin-top: 8rpx;
}
.run-sheet-hero-val {
  color: #ffffff;
  font-size: 112rpx;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -2rpx;
}
.run-sheet-hero-lbl {
  color: rgba(255, 255, 255, 0.5);
  font-size: 24rpx;
  margin-top: 8rpx;
}
.run-sheet-grid {
  width: 100%;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin-top: 28rpx;
}
.run-sheet-grid-item {
  width: 50%;
  padding: 20rpx 8rpx;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.run-sheet-grid-val {
  color: #f2f4f8;
  font-size: 40rpx;
  font-weight: 600;
}
.run-sheet-grid-lbl {
  color: rgba(255, 255, 255, 0.45);
  font-size: 22rpx;
  margin-top: 6rpx;
}
.run-sheet-extra {
  color: rgba(255, 255, 255, 0.65);
  font-size: 24rpx;
  text-align: center;
  padding: 0 24rpx;
  margin-top: 4rpx;
}
.run-sheet-progress {
  height: 8rpx;
  background-color: rgba(255, 255, 255, 0.12);
  border-radius: 4rpx;
  margin: 12rpx 24rpx 0;
  overflow: hidden;
}
.run-sheet-progress-fill {
  height: 8rpx;
  background-color: #20c997;
  border-radius: 4rpx;
}
.run-sheet-controls {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 4rpx 32rpx 0;
  flex-shrink: 0;
  position: relative;
  z-index: 2;
}
.run-ctrl-hover {
  opacity: 0.72;
}
.run-ctrl-side {
  width: 120rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  opacity: 0.85;
}
.run-ctrl-side--on {
  opacity: 1;
}
.run-ctrl-side-icon {
  font-size: 40rpx;
  line-height: 1.1;
}
.run-ctrl-side-lbl {
  color: rgba(255, 255, 255, 0.55);
  font-size: 22rpx;
  margin-top: 6rpx;
}
.run-ctrl-main {
  width: 152rpx;
  height: 152rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  border: 4rpx solid rgba(255, 255, 255, 0.35);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.run-ctrl-main--resume {
  border-color: rgba(46, 230, 184, 0.9);
  background: rgba(46, 230, 184, 0.18);
}
.run-ctrl-main-icon {
  color: #ffffff;
  font-size: 44rpx;
  line-height: 1;
  font-weight: 700;
}
.run-ctrl-main-lbl {
  color: rgba(255, 255, 255, 0.75);
  font-size: 22rpx;
  margin-top: 8rpx;
}
.run-ctrl-end {
  width: 148rpx;
  min-height: 120rpx;
  padding: 12rpx 8rpx;
  box-sizing: border-box;
  border-radius: 20rpx;
  background-color: rgba(255, 255, 255, 0.08);
  border: 2rpx solid rgba(46, 230, 184, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
}
.run-ctrl-end--hover {
  background-color: rgba(46, 230, 184, 0.16);
}
.run-ctrl-end-txt {
  color: #2ee6b8;
  font-size: 26rpx;
  font-weight: 700;
  text-align: center;
  line-height: 1.35;
}
.run-prep-sheet {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 125;
  box-sizing: border-box;
  background: linear-gradient(180deg, #252b38 0%, #141820 100%);
  border-top-left-radius: 28rpx;
  border-top-right-radius: 28rpx;
  box-shadow: 0 -12rpx 40rpx rgba(0, 0, 0, 0.22);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.run-prep-mode-pill {
  display: flex;
  flex-direction: row;
  margin: 0 24rpx 12rpx;
  padding: 6rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}
.run-prep-pill-item {
  flex: 1;
  text-align: center;
  color: rgba(255, 255, 255, 0.55);
  font-size: 24rpx;
  padding: 16rpx 8rpx;
  border-radius: 999rpx;
}
.run-prep-pill-item.active {
  background: #20c997;
  color: #ffffff;
  font-weight: 700;
}
.run-prep-pill-item--hover {
  opacity: 0.85;
}
.run-prep-title {
  color: rgba(255, 255, 255, 0.55);
  font-size: 24rpx;
  text-align: center;
  margin-bottom: 8rpx;
  flex-shrink: 0;
}
.run-prep-desc--center {
  text-align: center;
}
.run-prep-desc--warn {
  color: #ffb347;
  margin-top: 12rpx;
}
.run-prep-task-pick {
  margin-bottom: 16rpx;
}
.run-prep-task-pick-hint {
  display: block;
  color: rgba(255, 255, 255, 0.5);
  font-size: 24rpx;
  margin-bottom: 12rpx;
}
.run-prep-task-pick-item {
  padding: 20rpx 24rpx;
  border-radius: 16rpx;
  background: rgba(255, 255, 255, 0.06);
  border: 1rpx solid rgba(255, 255, 255, 0.08);
  margin-bottom: 12rpx;
}
.run-prep-task-pick-item--active {
  border-color: rgba(46, 230, 184, 0.85);
  background: rgba(46, 230, 184, 0.12);
}
.run-prep-task-pick-item--hover {
  opacity: 0.9;
}
.run-prep-task-pick-title {
  display: block;
  color: #fff;
  font-size: 28rpx;
  font-weight: 600;
}
.run-prep-task-pick-meta {
  display: block;
  margin-top: 8rpx;
  color: rgba(255, 255, 255, 0.55);
  font-size: 24rpx;
}
.run-prep-body {
  flex: 1;
  min-height: 0;
  padding: 0 24rpx;
  overflow: hidden;
}
.run-prep-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1rpx solid rgba(255, 255, 255, 0.08);
  border-radius: 20rpx;
  padding: 20rpx 24rpx;
}
.run-prep-card-head {
  display: block;
  color: #ffb347;
  font-size: 28rpx;
  font-weight: 700;
  text-align: center;
  margin-bottom: 16rpx;
}
.run-prep-row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 10rpx 0;
}
.run-prep-row-lbl {
  color: rgba(255, 255, 255, 0.55);
  font-size: 26rpx;
}
.run-prep-row-val {
  color: #2ee6b8;
  font-size: 28rpx;
  font-weight: 700;
}
.run-prep-desc {
  display: block;
  margin-top: 12rpx;
  color: rgba(255, 255, 255, 0.65);
  font-size: 24rpx;
  line-height: 1.5;
}
.run-prep-select {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 16rpx;
  min-height: 120rpx;
  padding: 20rpx 24rpx;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, 0.06);
  border: 1rpx solid rgba(46, 230, 184, 0.35);
}
.run-prep-select--hover {
  background: rgba(46, 230, 184, 0.12);
}
.run-prep-select-icon {
  font-size: 40rpx;
  line-height: 1;
}
.run-prep-select-copy {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.run-prep-select-title {
  color: #f2f4f8;
  font-size: 30rpx;
  font-weight: 700;
}
.run-prep-select-desc {
  color: rgba(255, 255, 255, 0.5);
  font-size: 24rpx;
  margin-top: 8rpx;
}
.run-prep-select-arrow {
  color: rgba(255, 255, 255, 0.45);
  font-size: 40rpx;
  line-height: 1;
}
.run-prep-start {
  margin: 12rpx 24rpx 8rpx;
  height: 96rpx;
  border-radius: 48rpx;
  background: #20c997;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10rpx 24rpx rgba(32, 201, 151, 0.35);
  flex-shrink: 0;
}
.run-prep-start--hover {
  opacity: 0.88;
}
.run-prep-start--disabled {
  opacity: 0.45;
  box-shadow: none;
}
.run-prep-start-txt {
  color: #ffffff;
  font-size: 32rpx;
  font-weight: 700;
}
.sport-teacher-task {
  flex-shrink: 0;
  padding: 12rpx 24rpx;
  background: #f0faf6;
  color: #0d8f6e;
  font-size: 24rpx;
}
.legend-line-pace {
  width: 36rpx;
  height: 8rpx;
  border-radius: 4rpx;
  margin-right: 10rpx;
  background: linear-gradient(to right, #ff5252, #ffc107, #4caf50);
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
.step-sensor-hint {
  display: block;
  text-align: center;
  font-size: 22rpx;
  color: #888;
  margin: 0 0 8rpx;
  line-height: 1.4;
}
.mileage-hint {
  display: block;
  text-align: center;
  font-size: 24rpx;
  color: #0d9668;
  background: rgba(32, 201, 151, 0.12);
  padding: 14rpx 20rpx;
  border-radius: 12rpx;
  margin: 4rpx 0 16rpx;
  line-height: 1.45;
}
.run-stats {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 16rpx 12rpx;
  margin-bottom: 20rpx;
  padding: 0 8rpx;
}
.stat-cell {
  width: 48%;
  box-sizing: border-box;
  background: #f8f9fa;
  border-radius: 12rpx;
  padding: 16rpx 12rpx;
  text-align: left;
}
.stat-label {
  display: block;
  font-size: 22rpx;
  color: #888;
  line-height: 1.4;
  margin-bottom: 6rpx;
}
.stat-value {
  display: block;
  font-size: 28rpx;
  color: #333;
  font-weight: 600;
  line-height: 1.35;
  word-break: break-all;
}
.data {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 10rpx;
  display: block;
  line-height: 1.5;
  word-break: break-all;
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

.overview-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8rpx 16rpx;
}
/* Map Controls */
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

