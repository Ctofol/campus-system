<template>
  <view class="run run-sport">
    <page-tab-header title="跑步" show-back theme="white" />

    <view class="run-map-section">
      <map
        v-if="isMapReady"
        id="runMap"
        class="map map-full"
        :latitude="mapCenterLat"
        :longitude="mapCenterLng"
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
          v-show="showMapTopHintBar"
          class="location-status-bar"
          :class="{ 'location-status-tappable': showMapTopHintTappable }"
          @tap="onLocationStatusBarTap"
        >
          <cover-view class="status-text">{{ mapTopHintText }}</cover-view>
        </cover-view>

        <cover-view
          v-show="!hideMapCoverLayer && !isRunning"
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
          v-show="!hideMapCoverLayer && taskRunLocked && !isRunning"
          class="sport-task-hint cover-panel"
          :style="taskHintStyle"
        >
          <cover-view class="sport-task-hint-t">任务跑步 · 专项模式已锁定</cover-view>
        </cover-view>

      </map>

      <view
        v-show="locationState !== 'success' && !isRunning"
        class="location-overlay"
      >
        <view v-if="locationState === 'idle' || locationState === 'locating'" class="location-overlay-body">
          <view class="location-loading-spinner" />
          <view class="location-overlay-text">正在获取定位</view>
        </view>
        <view v-else class="location-overlay-body">
          <view class="location-overlay-icon">!</view>
          <view class="location-overlay-text">定位失败</view>
          <view class="location-overlay-sub">请确保定位权限已开启</view>
          <view class="location-overlay-btn" @tap="onLocationStatusBarTap">重新定位</view>
        </view>
      </view>

      <view v-if="isRunCalibrating" class="run-calibration-overlay">
        <text class="run-calibration-count">{{ runCalibrationCountdown }}</text>
      </view>

      <view
        v-if="!hideMapCoverLayer"
        class="sport-recenter-float"
        :style="recenterFloatStyle"
        @tap="recenterMap"
      >
        <image class="sport-recenter-icon" src="/static/icons/icon-recenter.svg" mode="aspectFit" />
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
            <view class="run-sheet-expanded-stack">
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
              <view
                v-if="runSheetControlsInline"
                class="run-sheet-controls run-sheet-controls--inline"
              >
                <view
                  class="run-ctrl-side"
                  hover-class="run-ctrl-hover"
                  :class="{ 'run-ctrl-side--on': runControlsLocked }"
                  @tap="toggleRunLock"
                >
                  <image
                    class="run-ctrl-lock-img"
                    :src="runControlsLocked ? '/static/icons/icon-lock-filled-white.svg' : '/static/icons/icon-unlock-filled-white.svg'"
                    mode="aspectFit"
                  />
                  <text class="run-ctrl-side-lbl">{{ runControlsLocked ? '已锁' : '锁定' }}</text>
                </view>
                <view
                  class="run-ctrl-main"
                  hover-class="run-ctrl-hover"
                  :class="{ 'run-ctrl-main--resume': isRunPaused }"
                  @tap="toggleRunPause"
                >
                  <AppIcon :name="isRunPaused ? 'play' : 'pause'" :size="34" tone="white" />
                  <text class="run-ctrl-main-lbl">{{ isRunPaused ? '继续' : '暂停' }}</text>
                </view>
                <view class="run-ctrl-end" hover-class="run-ctrl-end--hover" @tap="onCompactStopTap">
                  <text class="run-ctrl-end-txt">{{ stopRunLabel }}</text>
                </view>
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

        <view
          v-if="!runSheetControlsInline"
          class="run-sheet-controls"
          :style="runSheetControlsStyle"
        >
          <view
            class="run-ctrl-side"
            hover-class="run-ctrl-hover"
            :class="{ 'run-ctrl-side--on': runControlsLocked }"
            @tap="toggleRunLock"
          >
            <image
              class="run-ctrl-lock-img"
              :src="runControlsLocked ? '/static/icons/icon-lock-filled-white.svg' : '/static/icons/icon-unlock-filled-white.svg'"
              mode="aspectFit"
            />
            <text class="run-ctrl-side-lbl">{{ runControlsLocked ? '已锁' : '锁定' }}</text>
          </view>
          <view
            class="run-ctrl-main"
            hover-class="run-ctrl-hover"
            :class="{ 'run-ctrl-main--resume': isRunPaused }"
            @tap="toggleRunPause"
          >
            <AppIcon :name="isRunPaused ? 'play' : 'pause'" :size="34" tone="white" />
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
            <AppIcon name="pin" :size="34" tone="brand" />
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
import { createRunEndpointMarker } from '@/utils/run-map-markers.js';
import { createStepCounter } from '@/utils/step-counter.js';
import { createTrajectoryFilter } from '@/utils/trajectory-filter.js';
import { wgs84ToGcj02 } from '@/utils/coord-transform.js';
import { buildRunPaceSeries } from '@/utils/run-pace-series.js';
import AppIcon from '@/components/app-icon/app-icon.vue';
import {
  pushRunGpsRawSample,
  resetRunGpsRawWindow,
  shouldRejectMileageSegment,
  computeDynamicMinDistanceM,
  isGpsClusterStationary,
  bearingDeg,
  recordAcceptedSegment,
  getDirectionReversalStatus
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
      // The result page is opened with navigateTo, so this page stays alive
      // underneath it. Clear the completed run's in-memory map state when
      // returning to the preparation screen; saved history is unaffected.
      runPolyline.value.points = [];
      trajectoryPoints.value = [];
      displayTrackPoints.value = [];
      runStartMarker.value = null;
      runEndMarker.value = null;
      lastPolylineJson = '';
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
const faceCameraLayerVisible = ref(false);
const faceCapturePhase = ref('start');
const faceCameraBusy = ref(false);
const faceCameraErrorText = ref('');
let faceCameraResolve = null;
let faceCameraContext = null;
let faceCameraTimeout = null;
let lastMarkerJson = '';
let lastPolylineJson = '';

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
// Steps only bound implausible GPS movement; they are never converted into distance.
let lastAcceptedMileageStepCount = 0;
/** 宸茶閲岀▼閫昏緫鎺ョ撼鐨勬湁鏁堣建杩圭偣鏁帮紝鐢ㄤ簬鍒ゆ柇 GPS 閫熷害鏄剧ず鏄惁杩涘叆绋冲畾闃舵 */
let gpsAcceptedPointCount = 0;
/** 鏈€杩戜竴娆″師濮嬪畾浣嶉噰鏍凤細鐢ㄤ簬鍘婚噸鍜屾姂鍒跺苟琛屽洖璋冨鑷寸殑闈欐鎶栧姩 */
let lastRawLocationSample = null;
let lastRouteFixInput = null;
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

const getMergePolylineGapM = () => 0.5;

/** 仅“站着抖手机、GPS 几乎不动”时冻结；起跑就开跑（有位移/步频）不冻结 */
const shouldFreezeRunPosition = (rawLat, rawLng) => {
  return false;
  /*
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
  */
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
      getCurrentLocation({ type: 'gcj02', fastFix: true, timeout: 5000 })
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
const mapCenterLat = ref(DEFAULT_MAP_LAT);
const mapCenterLng = ref(DEFAULT_MAP_LNG);
let lastLiveMapCenterAt = 0;
const markers = ref([]);
const checkpointMarker = ref(null);
const runStartMarker = ref(null);
const runEndMarker = ref(null);
let pendingRunTrajectoryForResult = null;

const hasPlausibleCoords = () => {
  if (!Number.isFinite(lat.value) || !Number.isFinite(lng.value)) return false;
  return !(
    Math.abs(lat.value - DEFAULT_MAP_LAT) < 0.0002 &&
    Math.abs(lng.value - DEFAULT_MAP_LNG) < 0.0002
  );
};

/** Always use one compass-driven custom arrow. The native location dot cannot
 * follow heading consistently on App and stays north-facing before a run. */
const showMapNativeLocation = computed(() => false);

const showCurrentLocationMarker = computed(
  () => hasPlausibleCoords() && locationState.value === 'success'
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
  if (locationState.value !== 'success' || !hasPlausibleCoords()) return;
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
  if (!hasPlausibleCoords()) return;
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

/** 人脸验证打开/关闭瞬间隐藏地图浮层，错开 camera 与 map 原生层切换 */
const hideMapCoverLayer = computed(() => showFaceCamera.value || faceCameraLayerVisible.value);

const showLocationStatusBar = computed(
  () =>
    locationState.value !== 'success' ||
    lastLocationFixWasStale.value
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
  return true;
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
  if (!isMapReady.value) return;
  const nextMarkers = [];
  if (showCurrentLocationMarker.value) {
    nextMarkers.push(createCurrentLocationMarker(lat.value, lng.value));
  }
  if (runStartMarker.value && showRunStartOnMap.value) {
    nextMarkers.push({ ...runStartMarker.value });
  }
  if (runEndMarker.value) {
    nextMarkers.push({ ...runEndMarker.value });
  }
  if (checkpointMarker.value) {
    nextMarkers.push({ ...checkpointMarker.value });
  }
  const j = JSON.stringify(nextMarkers);
  if (j === lastMarkerJson) return;
  lastMarkerJson = j;
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
const MERGE_POLYLINE_GAP_IDLE_M = 0.5;
/** 已确认在跑后：合并间距（慢走也能连续记里程） */
const MERGE_POLYLINE_GAP_RUN_M = 0.5;
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

// The finish marker and result map must end on the same accepted track that
// produced mileage. A raw latest GPS callback can be a short-lived drift.
const getValidatedRunFinishPoint = () => {
  const points = getPolylineSourcePoints();
  const last = points[points.length - 1];
  if (last && Number.isFinite(last.latitude) && Number.isFinite(last.longitude)) {
    return { latitude: last.latitude, longitude: last.longitude };
  }
  return { latitude: lat.value, longitude: lng.value };
};

// Helper to update map polyline with deep clone to force render
const updateMapPolyline = () => {
  const lines = [];
  // One smoothed line is visually continuous. Splitting every GPS pair into
  // pace-coloured segments makes Android maps look like stacked dashes.
  if (runPolyline.value.points && runPolyline.value.points.length >= 2) {
    lines.push({ ...runPolyline.value, points: [...runPolyline.value.points] });
  }
  if (navPolyline.value && navPolyline.value.points && navPolyline.value.points.length >= 2) {
    lines.push(JSON.parse(JSON.stringify(navPolyline.value)));
  }
  const j = JSON.stringify(lines);
  if (j === lastPolylineJson) return;
  lastPolylineJson = j;
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
    runPolyline.value.points = smoothTrajectoryForMap(flat, { sampleStepM: 1.5 });
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
  return { lat: latIn, lng: lngIn };
};

const clearRunCalibrationTimer = () => {
  if (runCalibrationTimer != null) {
    clearInterval(runCalibrationTimer);
    runCalibrationTimer = null;
  }
};

const finishRunCalibration = () => {
  if (!isRunning.value || !isRunCalibrating.value || !lastRunCalibrationFix) return false;
  const anchor = { ...lastRunCalibrationFix, speed: 0 };
  clearRunCalibrationTimer();
  isRunCalibrating.value = false;
  runCalibrationCountdown.value = 0;
  duration.value = 0;
  runActiveBaseSec.value = 0;
  runSegmentStartMs.value = Date.now();
  stepCount.value = 0;
  trajectoryPoints.value = [anchor];
  displayTrackPoints.value = [];
  runPolyline.value.points = [];
  lastRouteFixInput = { ...anchor };
  lastAcceptedMileageStepCount = 0;
  appendDisplayTrackPoint(anchor.latitude, anchor.longitude, anchor);
  runStartMarker.value = createRunPointMarker(2, anchor.latitude, anchor.longitude, '起');
  refreshMarkers();
  return true;
};

const startRunCalibrationCountdown = () => {
  clearRunCalibrationTimer();
  runCalibrationCountdownDone = false;
  lastRunCalibrationFix = null;
  runCalibrationCountdown.value = 3;
  runCalibrationTimer = setInterval(() => {
    if (!isRunning.value || !isRunCalibrating.value) {
      clearRunCalibrationTimer();
      return;
    }
    runCalibrationCountdown.value = Math.max(0, runCalibrationCountdown.value - 1);
    if (runCalibrationCountdown.value === 0) {
      runCalibrationCountdownDone = true;
      finishRunCalibration();
      if (runCalibrationCountdownDone) clearRunCalibrationTimer();
    }
  }, 1000);
};

// Unified location update logic
const updateLocationLogicLegacy = (newLat, newLng, speed, accuracyOrRes) => {
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
    if (true) {
      runLocationSmooth = { lat: newLat, lng: newLng };
      workLat = newLat;
      workLng = newLng;
    } else {
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
    }
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

    // One real location update drives the marker, route, mileage, and result data.
    mapCenterLat.value = workLat;
    mapCenterLng.value = workLng;
    const lastPoint = trajectoryPoints.value[trajectoryPoints.value.length - 1];
    if (lastPoint) {
      const segmentM = getDistance(lastPoint.latitude, lastPoint.longitude, workLat, workLng);
      const segmentSeconds = Math.max(0.1, (nowTs - lastPoint.timestamp) / 1000);
      if (segmentM >= 0.5) {
        const segmentSpeed = segmentM / segmentSeconds;
        distance.value += segmentM;
        currentSpeed.value = segmentSpeed;
        gpsAcceptedPointCount += 1;
        noteGpsMotion(nowTs, segmentM, segmentSpeed, getHorizontalAccuracyM(accuracyOrRes));
        appendRunTrackPoint(workLat, workLng, {
          latitude: workLat,
          longitude: workLng,
          timestamp: nowTs,
          speed: segmentSpeed
        });
        if (currentMode.value === 'normal') {
          normalProgress.value = Math.min(100, ((distance.value / 1000) / dailyTarget.value) * 100);
        } else if (currentMode.value === 'police') {
          policeProgress.value = Math.min(100, (distance.value / policeTargetDistance.value) * 100);
        }
      }
      if (currentMode.value === 'campus' && checkpoint.value.lat) {
        distanceToCheckpoint.value = Math.floor(
          getDistance(workLat, workLng, checkpoint.value.lat, checkpoint.value.lng)
        );
        isReach.value = distanceToCheckpoint.value <= (checkpoint.value.radius || 100);
      }
      return;
    }
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
    const segmentBearing = trajectoryPoints.value.length > 0
      ? bearingDeg(lastPoint.latitude, lastPoint.longitude, workLat, workLng)
      : NaN;
    const directionStatus = getDirectionReversalStatus();
    const oscillationActive = directionStatus === 'oscillating';
    const accM = getHorizontalAccuracyM(accuracyOrRes);
    if (Number.isFinite(accM)) {
      lastGpsAccuracyM.value = accM;
    }
    /** 开跑后 GPS 防抖；有步频时放宽，避免「有步数无里程」 */
    const runUnlocked = true;
    const stableCadence = true;
    const coldPhase = false;
    const recentStepMotion = hasRecentStepMotion();
    const trustedMotion = hasTrustedRunMotion();
    const stepBoosted = recentStepMotion && stepCount.value >= 8;
    const tightenNoSteps = false;
    const driftTight = false;
    const driftOscillation = driftTight && oscillationActive;
    const weakGpsSignal = false;
    const veryWeakGpsSignal = false;
    const earlyMotionStrict = false;
    const motionTier = 'walk';
    const tierConfig = {
      minDistance: 0.5,
      maxSpeed: 12,
      minSpeed: 0,
      maxStepDistance: 50,
      requiresTrustedMotion: false
    };

    let minD = 0.5;

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
      false &&
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

    if (driftOscillation && !hasStrongStepMotion() && !hasRecentStepMotion() && d < 5) {
      currentSpeed.value = 0;
      return;
    }

    if (
      shouldRejectMileageSegment({
        segmentM: d,
        timeDiffS: timeDiff,
        speedMps: calculatedSpeed,
        accuracyM: accM,
        hasRecentStepMotion: recentStepMotion,
        hasStrongStepMotion: hasStrongStepMotion(),
        hasRecentGpsMotionEvidence: hasRecentGpsMotionEvidence(),
        runUnlocked,
        bearingDeg: segmentBearing
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
        recordAcceptedSegment(segmentBearing, calculatedSpeed);

        const ft = filterTrackCoordsForMileage(workLat, workLng, accM);
        const point = { latitude: ft.lat, longitude: ft.lng, timestamp: nowTs, speed: speed || calculatedSpeed };
        appendRunTrackPoint(ft.lat, ft.lng, point);

        if (currentMode.value === 'normal') {
           normalProgress.value = Math.min(100, ((distance.value/1000) / dailyTarget.value) * 100);
        } else if (currentMode.value === 'police') {
           policeProgress.value = Math.min(100, (distance.value / policeTargetDistance.value) * 100);
        }
    }
  }
};

// Keep the running data path deliberately simple: every real GPS fix updates
// the live marker, route, mileage, and the route stored for the result page.
const updateLocationLogic = (newLat, newLng, speed, accuracyOrRes) => {
  let latitude = Number(newLat);
  let longitude = Number(newLng);
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    console.warn('[run-gps] ignored invalid coordinates:', newLat, newLng);
    return;
  }

  const nowTs = Date.now();
  const accuracyM = getHorizontalAccuracyM(accuracyOrRes);
  if (Number.isFinite(accuracyM)) lastGpsAccuracyM.value = accuracyM;

  if (isRunning.value && !isRunPaused.value && runTrajectoryFilter) {
    const filtered = runTrajectoryFilter.filter(latitude, longitude, accuracyM);
    if (Number.isFinite(filtered.latitude) && Number.isFinite(filtered.longitude)) {
      latitude = filtered.latitude;
      longitude = filtered.longitude;
    }
  }

  // A live run fix is authoritative. Do not leave the UI in "locating"
  // after the continuous location channel has already delivered coordinates.
  locationState.value = 'success';
  lastLocationFixWasStale.value = false;

  lat.value = latitude;
  lng.value = longitude;
  runLocationSmooth = { lat: latitude, lng: longitude };
  patchCurrentLocationMarker();

  if (!isRunning.value || isRunPaused.value) return;
  syncRunElapsedDisplay();

  // Keep the native map following real movement. This changes map attributes
  // only; it never mounts or unmounts the map view.
  if (nowTs - lastLiveMapCenterAt >= 350) {
    mapCenterLat.value = latitude;
    mapCenterLng.value = longitude;
    lastLiveMapCenterAt = nowTs;
  }

  if (isRunCalibrating.value) {
    runCalibrationFixCount += 1;
    lastRunCalibrationFix = { latitude, longitude, timestamp: nowTs };
    if (runCalibrationCountdownDone) finishRunCalibration();
    return;
  }

  const lastPoint = trajectoryPoints.value[trajectoryPoints.value.length - 1];
  if (!lastPoint) {
    const firstPoint = { latitude, longitude, timestamp: nowTs, speed: 0 };
    trajectoryPoints.value.push(firstPoint);
    appendDisplayTrackPoint(latitude, longitude, firstPoint);
    runStartMarker.value = createRunPointMarker(2, latitude, longitude, '起');
    refreshMarkers();
    lastRouteFixInput = { latitude, longitude, timestamp: nowTs };
    return;
  }

  const segmentM = getDistance(lastPoint.latitude, lastPoint.longitude, latitude, longitude);
  const inputGapM = lastRouteFixInput
    ? getDistance(lastRouteFixInput.latitude, lastRouteFixInput.longitude, latitude, longitude)
    : Infinity;
  const inputGapMs = lastRouteFixInput ? nowTs - lastRouteFixInput.timestamp : Infinity;
  // The system watcher and uni callback can report the same fix milliseconds
  // apart. Ignore only that duplicate; the next genuine movement is preserved.
  if (inputGapMs < 700 && inputGapM < 1.2) return;
  const elapsedS = Math.max(0.1, (nowTs - lastPoint.timestamp) / 1000);
  const segmentSpeed = segmentM / elapsedS;
  // A human run cannot cover hundreds of metres within a few seconds. Keep
  // high-frequency points, but never turn a one-off GPS teleport into mileage.
  if (segmentM > Math.max(35, elapsedS * 8.5)) {
    console.warn('[run-gps] ignored implausible segment:', segmentM, elapsedS);
    return;
  }
  lastRouteFixInput = { latitude, longitude, timestamp: nowTs };
  currentSpeed.value = Number.isFinite(speed) && speed >= 0 ? speed : segmentSpeed;

  // Display and mileage deliberately have different gates. A point that is
  // plausible enough to show can make the route follow a turn immediately,
  // while it still must pass the stricter cadence/noise rules before it adds
  // any distance.
  appendDisplayTrackPoint(latitude, longitude, {
    timestamp: nowTs,
    speed: currentSpeed.value
  });

  // 里程 anchor 要超过当前定位噪声半径才移动。小于门槛的真实位移不会丢失，
  // 因为下一个点仍然相对旧 anchor 累积；反之则不会把原地 GPS 抖动计成里程。
  const dynamicMinSegmentM = Number.isFinite(accuracyM)
    ? Math.max(3, Math.min(8, accuracyM * 0.6))
    : 4;
  const hasStepEvidence = hasRecentStepMotion() || hasStrongStepMotion();
  // GPS is the distance source. Step callbacks can arrive late on Android, so
  // they must not hold a real walking route at 0.00 before the first steps.
  const hasPlausibleMotion = segmentM >= dynamicMinSegmentM;
  const implausibleSpeed = shouldRejectMileageSegment({ segmentM, timeDiffS: elapsedS });
  const stepsSinceLastAccepted = Math.max(0, stepCount.value - lastAcceptedMileageStepCount);
  // Walking drift often reports a large displacement after only one or two
  // steps. This only rejects GPS outliers; it never derives distance from steps.
  const maxSegmentFromCadence = hasStepEvidence
    ? Math.max(4.5, stepsSinceLastAccepted * 1.55 + 3)
    : Math.max(7, elapsedS * 2.2);
  const exceedsCadenceLimit = segmentM > maxSegmentFromCadence;

  // Keep the high-frequency marker responsive, but only add route distance
  // after movement is larger than the current GPS noise floor and is backed by
  // cadence (or is unambiguously large). This prevents GPS jitter from
  // becoming extra distance while preserving accumulated real movement.
  if (
    !implausibleSpeed &&
    !exceedsCadenceLimit &&
    hasPlausibleMotion &&
    segmentM >= dynamicMinSegmentM
  ) {
    distance.value += segmentM;
    gpsAcceptedPointCount += 1;
    lastAcceptedMileageStepCount = stepCount.value;
    noteGpsMotion(nowTs, segmentM, segmentSpeed, accuracyM);
    appendRunTrackPoint(latitude, longitude, {
      latitude,
      longitude,
      timestamp: nowTs,
      speed: currentSpeed.value
    });

    if (currentMode.value === 'normal') {
      normalProgress.value = Math.min(100, ((distance.value / 1000) / dailyTarget.value) * 100);
    } else if (currentMode.value === 'police') {
      policeProgress.value = Math.min(100, (distance.value / policeTargetDistance.value) * 100);
    }
  }

  if (currentMode.value === 'campus' && checkpoint.value.lat) {
    distanceToCheckpoint.value = Math.floor(
      getDistance(latitude, longitude, checkpoint.value.lat, checkpoint.value.lng)
    );
    isReach.value = distanceToCheckpoint.value <= (checkpoint.value.radius || 100);
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
      getCurrentLocation({ type: preferredType, fastFix: true, timeout: 5000 })
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
      scheduleWxRunLocationAssist();
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
  // #ifdef APP-PLUS
  const claimAppRunLocationSource = (source) => {
    if (!isRunning.value) return true;
    if (appRunLocationSource === source) return true;
    if (appRunLocationSource) return false;
    if (source === 'uni' && appNativeWatchStartedAt > 0 && Date.now() - appNativeWatchStartedAt < 2500) {
      return false;
    }
    appRunLocationSource = source;
    return true;
  };
  const startAppNativeLocationWatch = (provider = 'tencent') => {
    if (typeof plus === 'undefined' || !plus.geolocation) return false;
    if (appLocationWatchId != null) {
      try {
        plus.geolocation.clearWatch(appLocationWatchId);
      } catch (e) {}
    }
    lastAppLocationFixAt = 0;
    lastAppNativeWatchFixAt = 0;
    appNativeWatchStartedAt = Date.now();
    try {
      appLocationWatchId = plus.geolocation.watchPosition(
        (position) => {
          lastAppLocationFixAt = Date.now();
          lastAppNativeWatchFixAt = lastAppLocationFixAt;
          // A late watch callback means the temporary polling fallback is no
          // longer needed. Keeping both would duplicate fixes and distort the
          // route even when their coordinate system is the same.
          if (appLocationPollingActive) {
            appLocationPollingActive = false;
            if (h5LocationTimer) {
              clearTimeout(h5LocationTimer);
              h5LocationTimer = null;
            }
          }
          const coords = position?.coords;
          if (!coords) return;
          if (!claimAppRunLocationSource('native')) return;
          const point = wgs84ToGcj02(coords.latitude, coords.longitude);
          updateLocationLogic(point.latitude, point.longitude, coords.speed, {
            accuracy: coords.accuracy,
            direction: coords.heading
          });
        },
        (error) => {
          console.warn('App native location watch failed:', error?.message || error);
          // Tencent SDK is configured in manifest.json. Some devices can still
          // reject that provider, in which case stay on one system source
          // rather than enabling uni.onLocationChange in parallel.
          if (provider === 'tencent' && isRunning.value) {
            startAppNativeLocationWatch('system');
          } else if (isRunning.value) {
            startAppLocationPolling();
          }
        },
        {
          provider,
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 500,
          // plus.geolocation on Android supports WGS84 only. Convert at the
          // boundary above so every point used by the Tencent map is GCJ02.
          coordsType: 'wgs84',
          geocode: false
        }
      );
    } catch (error) {
      console.warn('App native location watch unavailable:', error);
      appLocationWatchId = null;
      return false;
    }

    if (appLocationWatchdogTimer) clearTimeout(appLocationWatchdogTimer);
    appLocationWatchdogTimer = setTimeout(() => {
      appLocationWatchdogTimer = null;
      if (isRunning.value && !lastAppNativeWatchFixAt) startAppLocationPolling();
    }, 3000);
    return true;
  };
  const requestAppSystemLocation = () =>
    new Promise((resolve, reject) => {
      if (typeof plus === 'undefined' || !plus.geolocation) {
        reject(new Error('system geolocation unavailable'));
        return;
      }
      try {
        plus.geolocation.getCurrentPosition(
          (position) => {
            const coords = position?.coords;
            if (!coords) {
              reject(new Error('system geolocation returned no coordinates'));
              return;
            }
            const point = wgs84ToGcj02(coords.latitude, coords.longitude);
            resolve({
              latitude: point.latitude,
              longitude: point.longitude,
              speed: coords.speed,
              accuracy: coords.accuracy,
              direction: coords.heading
            });
          },
          reject,
          {
            provider: 'system',
            enableHighAccuracy: true,
            timeout: 8000,
            maximumAge: 0,
            coordsType: 'wgs84',
            geocode: false
          }
        );
      } catch (error) {
        reject(error);
      }
    });
  const startAppLocationPolling = () => {
    if (appLocationPollingActive) return;
    appLocationPollingActive = true;
    if (h5LocationTimer) {
      clearTimeout(h5LocationTimer);
      clearInterval(h5LocationTimer);
    }
    const poll = () => {
      if (!isRunning.value || !appLocationPollingActive) return;
      requestAppSystemLocation()
        .then((res) => ({ res, source: 'native' }))
        .catch(() =>
          getCurrentLocation({ type: 'gcj02', timeout: 5000 }).then((res) => ({ res, source: 'uni' }))
        )
        .then(({ res, source }) => {
          if (claimAppRunLocationSource(source)) {
            updateLocationLogic(res.latitude, res.longitude, res.speed, res);
          }
        })
        .catch((err) => console.warn('[run-gps] App location poll failed:', err))
        .finally(() => {
          if (isRunning.value && appLocationPollingActive) {
            h5LocationTimer = setTimeout(poll, 1000);
          }
        });
    };
    poll();
  };
  // App runs use one native location channel for the entire session. Mixing
  // plus.geolocation and uni.onLocationChange was the source of the flashing
  // marker and sudden kilometre jumps reported on Android devices.
  lastAppLocationFixAt = 0;
  if (!startAppNativeLocationWatch('tencent')) {
    startAppLocationPolling();
  }
  // #endif
};

const stopRealLocationTracking = () => {
  clearRunCalibrationTimer();
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
  // #ifdef APP-PLUS
  if (appLocationWatchdogTimer) {
    clearTimeout(appLocationWatchdogTimer);
    appLocationWatchdogTimer = null;
  }
  if (appLocationWatchId != null && typeof plus !== 'undefined' && plus.geolocation) {
    try {
      plus.geolocation.clearWatch(appLocationWatchId);
    } catch (e) {}
  }
  appLocationWatchId = null;
  lastAppLocationFixAt = 0;
  lastAppNativeWatchFixAt = 0;
  appLocationPollingActive = false;
  appRunLocationSource = null;
  appNativeWatchStartedAt = 0;
  // #endif
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
const isRunCalibrating = ref(false);
const runCalibrationCountdown = ref(3);
let runCalibrationFixCount = 0;
let runCalibrationTimer = null;
let runCalibrationCountdownDone = false;
let lastRunCalibrationFix = null;
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
let appLocationWatchId = null;
let appLocationWatchdogTimer = null;
let lastAppLocationFixAt = 0;
let lastAppNativeWatchFixAt = 0;
let appLocationPollingActive = false;
let appRunLocationSource = null;
let appNativeWatchStartedAt = 0;
let appAccelerometerWatchId = null;
let appAccelerometerWatchdogTimer = null;
let lastAppAccelerometerAt = 0;
let isStepActive = false;
let lastStepTime = 0;
const STEP_THRESHOLD_UP = 1.25;
const STEP_THRESHOLD_DOWN = 1.05;
const MIN_STEP_INTERVAL = 300;
const STEP_RESET_TIMEOUT = 1500;
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
      locationRetryTimer = setInterval(() => {
          if (!isPageActive) return;
          if (locationState.value !== 'success') {
              doGetLocation();
          } else {
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

﻿const getLocation = () => {
  // #ifdef MP-WEIXIN
  const scheduleWxInitialLocate = () => {
    nextTick(() => {
      setTimeout(() => {
        if (!isPageActive) return;
        doGetLocation();
      }, 340);
    });
  };

  const showPermissionDialog = () => {
    stopWxInitialLocateRetry();
    locationState.value = 'fail';
    uni.showModal({
      title: '需要定位权限',
      content: '跑步功能需要获取您的位置信息。请在弹窗中点击「允许」，或在系统设置中开启定位权限。',
      confirmText: '去设置',
      cancelText: '重试',
      success: (res) => {
        if (res.confirm) {
          uni.openSetting({
            success: () => {
              setTimeout(() => {
                locationState.value = 'idle';
                getLocation();
              }, 500);
            }
          });
        } else {
          wxInitialLocateAttempts = 0;
          lastLocationFixWasStale.value = false;
          locationState.value = 'idle';
          setTimeout(() => getLocation(), 300);
        }
      }
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
        fail: showPermissionDialog
      });
    },
    fail: () => {
      uni.authorize({
        scope: 'scope.userLocation',
        success: () => scheduleWxInitialLocate(),
        fail: showPermissionDialog
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
  // Reset retry counter on any successful fix
  wxInitialLocateAttempts = 0;
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
        // Sync map center on first good fix; avoid re-binding lat/lng
        // every update (triggers uni-app view-layer null refs on App)
        if (mapCenterLat.value === DEFAULT_MAP_LAT) {
          mapCenterLat.value = lat.value;
          mapCenterLng.value = lng.value;
        }
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
        if (true) {
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
    if (false && Number.isFinite(acc) && acc > 80) {
    return 'GPS 信号较弱，请到空旷处再跑';
  }
    if (false && stepCount.value >= 10 && duration.value >= 6 && !hasRecentGpsMotionEvidence()) {
    return '正在校准 GPS，请正常跑动…';
  }
  if (duration.value >= 12 && stepCount.value < 4 && distance.value < 5) {
    return '正在等待稳定定位';
  }
    if (false && duration.value >= 4 && distance.value < 8) {
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

const taskHintStyle = computed(() => ({
  bottom: `${runPrepSheetHeightPx.value + 18}px`
}));

const initRunPrepSheetHeight = () => {
  try {
    const sys = uni.getSystemInfoSync();
    const h = sys.windowHeight || 667;
    const safe = sys.safeAreaInsets?.bottom || 0;
    const mode = currentMode.value;
    const ratio = mode === 'campus' ? 0.36 : mode === 'police' ? 0.31 : 0.30;
    runPrepSheetHeightPx.value = Math.round(h * ratio + safe * 0.35);
  } catch (e) {
    const mode = currentMode.value;
    runPrepSheetHeightPx.value = mode === 'campus' ? 310 : mode === 'police' ? 280 : 260;
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

const runSheetControlsInline = computed(() => runSheetExpandProgress.value >= 0.55);

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
      expanded: Math.round(h * 0.48 + safe * 0.15)
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
  if (isRunning.value) {
    mapCenterLat.value = lat.value;
    mapCenterLng.value = lng.value;
    return;
  }
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
  lastAcceptedMileageStepCount = 0;
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

defineExpose({ onPageShow, onPageHide, saveRunSession, tryRestoreRunSession });

// 8. 步数统计（加速度传感器，step-counter 步频带通计步）
const ensureRunStepCounter = () => {
  if (!runStepCounter) {
    runStepCounter = createStepCounter();
  }
  return runStepCounter;
};

const feedRunStepMotion = (x, y, z) => {
  if (!isRunning.value || isRunPaused.value) return;
  let acceleration = Math.sqrt(x * x + y * y + z * z);
  if (!Number.isFinite(acceleration)) return;
  if (acceleration > 5) acceleration /= 9.8;

  const now = Date.now();
  if (isStepActive && now - lastStepTime > STEP_RESET_TIMEOUT) {
    isStepActive = false;
  }
  if (!isStepActive && acceleration > STEP_THRESHOLD_UP && now - lastStepTime > MIN_STEP_INTERVAL) {
    stepCount.value += 1;
    if (runStepCounter) runStepCounter.setStepCount(stepCount.value);
    lastStepTime = now;
    isStepActive = true;
    noteStepMotion(now);
  } else if (isStepActive && acceleration < STEP_THRESHOLD_DOWN) {
    isStepActive = false;
  }
};

const startAppNativeStepCount = () => {
  if (typeof plus === 'undefined' || !plus.accelerometer) return false;
  if (appAccelerometerWatchId != null) {
    try {
      plus.accelerometer.clearWatch(appAccelerometerWatchId);
    } catch (e) {}
  }
  lastAppAccelerometerAt = 0;
  const counter = ensureRunStepCounter();
  counter.reset();
  counter.setStepCount(stepCount.value);
  try {
    appAccelerometerWatchId = plus.accelerometer.watchAcceleration(
      (acceleration) => {
        lastAppAccelerometerAt = Date.now();
        feedRunStepMotion(
          Number(acceleration?.xAxis) || 0,
          Number(acceleration?.yAxis) || 0,
          Number(acceleration?.zAxis) || 0
        );
      },
      (error) => {
        console.warn('App native accelerometer failed:', error?.message || error);
        appAccelerometerWatchId = null;
      },
      { frequency: 60 }
    );
    if (appAccelerometerWatchdogTimer) clearTimeout(appAccelerometerWatchdogTimer);
    appAccelerometerWatchdogTimer = setTimeout(() => {
      appAccelerometerWatchdogTimer = null;
      if (!isRunning.value || lastAppAccelerometerAt) return;
      if (appAccelerometerWatchId != null) {
        try {
          plus.accelerometer.clearWatch(appAccelerometerWatchId);
        } catch (e) {}
        appAccelerometerWatchId = null;
      }
      startAccelerometerWithRetry(0);
    }, 1500);
    resetRunMotionEvidence();
    return true;
  } catch (error) {
    console.warn('App native accelerometer unavailable:', error);
    appAccelerometerWatchId = null;
    return false;
  }
};

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
    const counter = ensureRunStepCounter();
    counter.reset();
    counter.setStepCount(stepCount.value);
    accelerometerCallback = (res) => {
      feedRunStepMotion(res.x, res.y, res.z);
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
  isStepActive = false;
  lastStepTime = Date.now();
  uni.stopAccelerometer({
    complete: () => {
      setTimeout(() => startAccelerometerWithRetry(retryCount), 200);
    }
  });
};

const stopStepCount = () => {
  // #if !defined(H5) && !defined(MP-WEIXIN)
  if (appAccelerometerWatchdogTimer) {
    clearTimeout(appAccelerometerWatchdogTimer);
    appAccelerometerWatchdogTimer = null;
  }
  if (appAccelerometerWatchId != null && typeof plus !== 'undefined' && plus.accelerometer) {
    try {
      plus.accelerometer.clearWatch(appAccelerometerWatchId);
    } catch (e) {}
  }
  appAccelerometerWatchId = null;
  lastAppAccelerometerAt = 0;
  // #endif
  if (accelerometerCallback) {
    uni.stopAccelerometer();
    uni.offAccelerometerChange(accelerometerCallback);
    accelerometerCallback = null;
  }
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
  isRunCalibrating.value = true;
  runCalibrationCountdown.value = 3;
  runCalibrationFixCount = 0;
  isRunPaused.value = false;
  runControlsLocked.value = false;
  duration.value = 0;
  runActiveBaseSec.value = 0;
  runSegmentStartMs.value = Date.now();
  distance.value = 0;
  // Center map on start position
  mapCenterLat.value = lat.value;
  mapCenterLng.value = lng.value;
  stepCount.value = 0;
  currentSpeed.value = 0;
  endFaceUrl.value = null;
  gpsAcceptedPointCount = 0;
  lastAcceptedMileageStepCount = 0;
  resetRunMotionEvidence();
  stepFusionSkewSince = 0;
  stepFusionLastAdjustAt = 0;
  if (runTrajectoryFilter) {
    runTrajectoryFilter.reset();
  } else {
    runTrajectoryFilter = createTrajectoryFilter({
      medianWindow: 3,
      processNoise: 6e-8,
      measurementNoiseBase: 2e-8
    });
  }
  if (runStepCounter) {
    runStepCounter.reset();
  }
  
  // Clear previous trajectory
  runPolyline.value.points = [];
  trajectoryPoints.value = [];
  displayTrackPoints.value = [];
  pendingRunTrajectoryForResult = null;
  runStartMarker.value = null;
  runEndMarker.value = null;
  runLocationSmooth = null;
  lastRawLocationSample = null;
  lastRouteFixInput = null;
  resetRunGpsRawWindow();
  startRunCalibrationCountdown();
  refreshMarkers();
  updateMapPolyline();
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
  if (faceCameraTimeout) {
    clearTimeout(faceCameraTimeout);
    faceCameraTimeout = null;
  }
  const resolver = faceCameraResolve;
  faceCameraResolve = null;
  showFaceCamera.value = false;
  faceCameraBusy.value = false;
  faceCameraErrorText.value = '';
  faceCameraContext = null;
  setTimeout(() => {
    faceCameraLayerVisible.value = false;
  }, 180);
  if (resolver) resolver(!!result);
};

const cancelFaceCamera = () => finishFaceCamera(false);

const handleFaceCameraReady = () => {
  // #ifdef MP-WEIXIN
  if (!showFaceCamera.value) return;
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
  faceCameraLayerVisible.value = true;
  showFaceCamera.value = true;
  return new Promise((resolve) => {
    faceCameraResolve = resolve;
    faceCameraTimeout = setTimeout(() => {
      if (faceCameraResolve) {
        uni.showToast({ title: '相机启动超时，请检查摄像头权限', icon: 'none' });
        finishFaceCamera(false);
      }
    }, 15000);
    nextTick(() => {
      // #ifdef MP-WEIXIN
      if (!showFaceCamera.value) return;
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
  pendingRunTrajectoryForResult = null;
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
  runEndMarker.value = null;
  refreshMarkers();
  // Use navigateTo instead of redirectTo to avoid destroying the current
  // page's native map component (which triggers view-layer DOM errors on App)
  uni.navigateTo({
    url: '/pages/result/result?useStorage=true',
    fail: (err) => {
      console.error('Navigate failed:', err);
      uni.showToast({ title: '页面跳转失败', icon: 'none' });
    }
  });
};

/** Run record storage helper. */
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

// Freeze the display route before end-face capture can trigger lifecycle cleanup.
const captureRunTrajectoryForResult = () => {
  rebuildDisplayPolyline();
  const source = getPolylineSourcePoints();
  const points = source.map((point) => ({
    latitude: point.latitude,
    longitude: point.longitude,
    timestamp: point.timestamp,
    speed: point.speed
  }));
  const endPoint = getValidatedRunFinishPoint();
  if (
    points.length === 0 ||
    getDistance(
      points[points.length - 1].latitude,
      points[points.length - 1].longitude,
      endPoint.latitude,
      endPoint.longitude
    ) > 0.2
  ) {
    points.push(endPoint);
  }
  const polylinePoints = runPolyline.value.points.length >= 2
    ? runPolyline.value.points.map((point) => ({ latitude: point.latitude, longitude: point.longitude }))
    : smoothTrajectoryForMap(points, { sampleStepM: 1.5 });
  return {
    points,
    mileagePoints: trajectoryPoints.value.map((point) => ({
      latitude: point.latitude,
      longitude: point.longitude,
      timestamp: point.timestamp,
      speed: point.speed
    })),
    polylinePoints,
    startLat: points.length > 0 ? points[0].latitude : endPoint.latitude,
    startLng: points.length > 0 ? points[0].longitude : endPoint.longitude,
    endLat: endPoint.latitude,
    endLng: endPoint.longitude
  };
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
    uni.setStorageSync('tempRunPaceSeries', runData?.metrics?.pace_series || []);
    // 同时保存轨迹数据用于结算页展示
    const trajectoryForResult = pendingRunTrajectoryForResult || captureRunTrajectoryForResult();
    console.info(
      '[run-result] stored route points:',
      trajectoryForResult.points.length,
      trajectoryForResult.polylinePoints.length
    );
    uni.setStorageSync('tempRunTrajectory', trajectoryForResult);
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
    const finishPoint = getValidatedRunFinishPoint();
    runEndMarker.value = createRunPointMarker(3, finishPoint.latitude, finishPoint.longitude, '终');
    refreshMarkers();
  }
  pendingRunTrajectoryForResult = captureRunTrajectoryForResult();
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
  const distKm = reportM / 1000;
  const durSec = Math.max(duration.value, 1);
  const paceFromDist = distKm > 1e-6 ? (durSec / 60) / distKm : Number(currentPace.value) || 0;
  const paceStr = Number.isFinite(paceFromDist) && paceFromDist > 0 ? paceFromDist.toFixed(1) : String(currentPace.value || '0');
  const reportedStepCount = stepCount.value;
  const durOk = !taskMinDurationSec.value || duration.value >= taskMinDurationSec.value;
  const distOk = !policeTargetDistance.value || reportM >= policeTargetDistance.value;
  const taskMetPreview = !taskId.value || (distOk && durOk);
  const trajectoryForHistory = pendingRunTrajectoryForResult?.mileagePoints || trajectoryPoints.value;
  const paceSeries = buildRunPaceSeries(trajectoryForHistory);

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
      trajectory: JSON.stringify(trajectoryForHistory),
      pace_series: paceSeries,
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
  background-color: rgba(51, 201, 171, 0.92);
}
.status-text {
  color: #ffffff;
  font-size: 24rpx;
  line-height: 1.4;
  text-align: center;
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
  color: #33C9AB;
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
  color: #33C9AB;
  font-size: 26rpx;
  font-weight: 600;
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
  width: 42rpx;
  height: 42rpx;
}

.location-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(245, 247, 250, 0.95);
}
.location-overlay-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.location-overlay-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 40rpx;
  background-color: #f5f5f5;
  color: #999;
  font-size: 44rpx;
  text-align: center;
  line-height: 80rpx;
  margin-bottom: 16rpx;
}
.location-overlay-text {
  font-size: 30rpx;
  color: #333;
  font-weight: 500;
  margin-bottom: 8rpx;
}
.location-overlay-sub {
  font-size: 26rpx;
  color: #999;
  margin-bottom: 24rpx;
}
.location-overlay-btn {
  padding: 16rpx 48rpx;
  border-radius: 40rpx;
  background-color: #07c160;
  color: #fff;
  font-size: 28rpx;
  font-weight: 500;
}
.location-loading-spinner {
  width: 60rpx;
  height: 60rpx;
  border: 4rpx solid #e0e0e0;
  border-top-color: #07c160;
  border-radius: 50%;
  animation: location-spin 0.8s linear infinite;
  margin-bottom: 20rpx;
}
@keyframes location-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

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
.run-bottom-sheet--expanded .run-sheet-body {
  justify-content: center;
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
  justify-content: center;
  padding: 0 32rpx 8rpx;
  pointer-events: auto;
}
.run-sheet-expanded-stack {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
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
  margin-top: 20rpx;
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
  background-color: #33C9AB;
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
  width: 100%;
  box-sizing: border-box;
}
.run-sheet-controls--inline {
  margin-top: 36rpx;
  padding: 0 8rpx 4rpx;
  pointer-events: auto;
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

.run-calibration-overlay {
  position: absolute;
  top: 34%;
  left: 50%;
  z-index: 180;
  width: 132rpx;
  height: 132rpx;
  margin-left: -66rpx;
  border-radius: 66rpx;
  background-color: rgba(19, 32, 48, 0.78);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.run-calibration-count {
  color: #ffffff;
  font-size: 76rpx;
  font-weight: 700;
  line-height: 1;
}
.run-ctrl-lock-img {
  width: 34rpx;
  height: 34rpx;
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
  background: #33C9AB;
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
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
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
  background: #33C9AB;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10rpx 24rpx rgba(51, 201, 171, 0.35);
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
/* 跑步通用模块样式 */

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
  background: #33C9AB;
  color: #fff;
}

@keyframes pulse {
  0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(51, 201, 171, 0.4); }
  70% { transform: scale(1.05); box-shadow: 0 0 0 20rpx rgba(51, 201, 171, 0); }
  100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(51, 201, 171, 0); }
}
</style>

