<template>
  <view class="result-page result-sport">
    <view
      class="result-map-wrap"
      v-if="resultMapReady && currentMode !== 'test' && (trajectoryPoints.length >= 1 || mapCenterLat !== 0)"
    >
      <map
        class="result-map-full"
        :latitude="mapCenterLat"
        :longitude="mapCenterLng"
        :polyline="mapPolyline"
        :markers="mapMarkers"
        :enable-zoom="true"
        :enable-scroll="true"
        :scale="mapScale"
        :show-location="false"
      />
      <view class="route-pace-legend">
        <text class="route-pace-legend__label">慢</text>
        <view class="route-pace-legend__swatch route-pace-legend__swatch--blue" />
        <view class="route-pace-legend__swatch route-pace-legend__swatch--green" />
        <view class="route-pace-legend__swatch route-pace-legend__swatch--amber" />
        <view class="route-pace-legend__swatch route-pace-legend__swatch--red" />
        <text class="route-pace-legend__label">快</text>
      </view>
    </view>

    <!-- 跑步结算：深色浮层 -->
    <view class="result-hero" v-if="currentMode !== 'test'">
      <text class="result-mode-tag">{{ modeTitle }}</text>
      <view class="result-distance-row">
        <text class="result-distance-num">{{ distanceKmStr }}</text>
        <text class="result-distance-unit">公里</text>
      </view>
      <view class="result-pace-legend">
        <text class="legend-slow">慢</text>
        <view class="legend-gradient" />
        <text class="legend-fast">快</text>
      </view>
      <view class="result-metrics-row">
        <view class="result-metric">
          <text class="result-metric-val">{{ avgPaceDisplay }}</text>
          <text class="result-metric-lbl">平均配速</text>
        </view>
        <view class="result-metric">
          <text class="result-metric-val">{{ formatDuration(duration) }}</text>
          <text class="result-metric-lbl">用时</text>
        </view>
        <view class="result-metric">
          <text class="result-metric-val">{{ estimatedCalories }}</text>
          <text class="result-metric-lbl">消耗大卡</text>
        </view>
      </view>

      <view class="result-more" @click="showMoreDetail = !showMoreDetail">
        <text class="result-more-title">{{ showMoreDetail ? '收起详情' : '查看核验与任务详情' }}</text>
        <text class="result-more-arrow">{{ showMoreDetail ? '▲' : '▼' }}</text>
      </view>

      <view v-if="showMoreDetail" class="result-more-body">
        <view class="mode-data" v-if="currentMode === 'police'">
          <view class="data-item">
            <text class="item-label">2000米目标</text>
            <text class="item-value" :class="isPoliceFinish ? 'success' : 'fail'">
              {{ isPoliceFinish ? '已完成' : '未完成' }}
            </text>
          </view>
          <view class="data-item">
            <text class="item-label">配速达标</text>
            <text class="item-value" :class="isPaceQualified ? 'success' : 'fail'">
              {{ isPaceQualified ? `达标（${policePace.toFixed(1)} 分/公里）` : `未达标（${policePace.toFixed(1)} 分/公里）` }}
            </text>
          </view>
        </view>
        <view class="mode-data" v-if="currentMode === 'campus'">
          <view class="data-item" v-if="campusCheckpointName">
            <text class="item-label">打卡点</text>
            <text class="item-value">{{ campusCheckpointName }}</text>
          </view>
          <view class="data-item">
            <text class="item-label">到达状态</text>
            <text class="item-value" :class="isReach ? 'success' : 'fail'">
              {{ isReach ? '已到达' : '未到达' }}
            </text>
          </view>
        </view>
        <view class="verify-section" v-if="isTaskRun && taskCompleted !== null">
          <text class="verify-title">任务结果</text>
          <text class="verify-text" :class="taskCompleted ? 'success' : 'fail'">
            {{ taskCompleted ? `已完成：${taskTitle || '本次任务'}` : (failReason || '未满足任务要求') }}
          </text>
        </view>
        <view class="verify-section" v-if="faceVerifyText">
          <text class="verify-title">人脸核验</text>
          <text class="verify-text" :class="faceVerified ? 'success' : 'fail'">{{ faceVerifyText }}</text>
        </view>
        <view class="verify-section" v-if="currentMode === 'normal' && !isTaskRun && isValid !== null">
          <text class="verify-title">阳光跑核验</text>
          <text class="verify-text" :class="isValid ? 'success' : 'fail'">
            {{ isValid ? '本次有效，已计入成绩' : failReasonText }}
          </text>
        </view>
      </view>

      <view
        v-if="currentMode === 'normal' && !isTaskRun && todayCompleted !== null"
        class="result-inline-tip"
      >
        <text :class="todayCompleted ? 'tip-ok' : 'tip-warn'">
          {{ todayCompleted ? '今日阳光跑目标已达成' : '今日尚未达成有效运动目标' }}
        </text>
      </view>

      <view class="ai-insight-card" v-if="aiInsight || aiInsightLoading">
        <text class="ai-insight-title">{{ aiInsightLoading ? 'AI正在生成运动建议' : (aiInsight?.title || 'AI运动报告') }}</text>
        <text class="ai-insight-summary">{{ aiInsight?.summary || '正在结合本次运动数据生成训练建议。' }}</text>
        <view class="ai-insight-list" v-if="aiInsight?.suggestions?.length">
          <text class="ai-insight-item" v-for="item in aiInsight.suggestions" :key="item">{{ item }}</text>
        </view>
      </view>

      <button class="result-primary-btn" @click="backToHome">返回首页</button>
    </view>

    <!-- 体测模式：保留原卡片 -->
    <view class="result-card result-card-test" v-if="currentMode === 'test'">
      <view class="base-data">
        <text class="base-title">测试项目：{{ testProject }}</text>
        <view class="data-item">
          <text class="item-label">完成数量</text>
          <text class="item-value count-text">{{ testCount }} 次</text>
        </view>
        <view class="data-item">
          <text class="item-label">测试用时</text>
          <text class="item-value">{{ formatDuration(duration) }}</text>
        </view>
        <view class="data-item">
          <text class="item-label">动作判定</text>
          <text class="item-value" :class="testQualified ? 'success' : 'fail'">{{ testQualified ? '合格' : '未合格' }}</text>
        </view>
      </view>
      <view class="mode-data">
        <text class="mode-data-title">成绩分析</text>
        <view class="bar-chart">
          <view class="bar-row">
            <text class="bar-label">我的</text>
            <view class="bar-track">
              <view class="bar-fill user-fill" :style="{ width: userScorePercent + '%' }" />
            </view>
          </view>
          <view class="bar-row">
            <text class="bar-label">合格</text>
            <view class="bar-track">
              <view class="bar-fill standard-fill" :style="{ width: standardScorePercent + '%' }" />
            </view>
          </view>
        </view>
        <view class="suggestion-box">
          <text class="sugg-text">{{ suggestionText }}</text>
        </view>
      </view>
      <view class="ai-insight-card" v-if="aiInsight || aiInsightLoading">
        <text class="ai-insight-title">{{ aiInsightLoading ? 'AI正在生成体测反馈' : (aiInsight?.title || 'AI体测反馈') }}</text>
        <text class="ai-insight-summary">{{ aiInsight?.summary || '正在结合体测成绩生成训练建议。' }}</text>
        <view class="ai-insight-list" v-if="aiInsight?.suggestions?.length">
          <text class="ai-insight-item" v-for="item in aiInsight.suggestions" :key="item">{{ item }}</text>
        </view>
      </view>
      <button class="result-primary-btn" @click="backToHome">返回首页</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { buildRunRouteMarkers } from '@/utils/run-map-markers.js';
import { buildPaceColoredPolylines } from '@/utils/trajectory-pace-polyline.js';
import { getAiRunReport, getAiTestFeedback } from '@/utils/request.js';

const currentMode = ref('normal');
const duration = ref(0);
const distance = ref(0);
const isReach = ref(false);
const campusCheckpointName = ref('');
const isPoliceFinish = ref(false);
const policePace = ref(0);
const isValid = ref(null);
const failReason = ref('');
const todayCompleted = ref(null);
const isTaskRun = ref(false);
const taskTitle = ref('');
const taskCompleted = ref(null);
const testProject = ref('');
const testCount = ref(0);
const testQualified = ref(false);
const userScorePercent = ref(0);
const standardScorePercent = ref(0);
const suggestionText = ref('');
const showMoreDetail = ref(false);
const standardReq = ref(0);
const faceVerified = ref(null);
const faceMatchScore = ref(null);
const faceVerifyText = ref('');
const aiInsightLoading = ref(false);
const aiInsight = ref(null);

const trajectoryPoints = ref([]);
const mapCenterLat = ref(0);
const mapCenterLng = ref(0);
const mapPolyline = ref([]);
const mapMarkers = ref([]);
const mapScale = ref(15);
// App native maps must be mounted after their initial polyline is ready.
const resultMapReady = ref(false);
const resultRoutePoints = ref([]);

const setResultRoutePolyline = () => {
  if (resultRoutePoints.value.length < 2) return;
  const paceLines = buildPaceColoredPolylines(resultRoutePoints.value, { maxSegments: 6 });
  if (paceLines.length > 0) {
    mapPolyline.value = paceLines;
    return;
  }
  mapPolyline.value = [{
    points: resultRoutePoints.value.map((point) => ({ ...point })),
    color: '#1E88E5',
    width: 6,
    borderColor: '#FFFFFF',
    borderWidth: 2
  }];
};

const parseStoredTrajectory = (value) => {
  if (typeof value !== 'string') return value;
  try {
    return JSON.parse(value);
  } catch (error) {
    console.warn('[run-result] failed to parse stored trajectory:', error);
    return null;
  }
};

const normalizeStoredPoints = (value) => {
  const parsed = parseStoredTrajectory(value);
  return Array.isArray(parsed) ? parsed : [];
};

const modeTitle = computed(() => {
  if (isTaskRun.value) return '任务跑步';
  switch (currentMode.value) {
    case 'police':
      return '专项跑步';
    case 'campus':
      return '校园打卡';
    case 'test':
      return '体能测试';
    default:
      return '跑步记录';
  }
});

const isPaceQualified = ref(false);

const faceFailCode = ref('');

const buildFaceVerifyText = (data) => {
  const scoreExtra =
    data.face_match_score != null
      ? `（相似度 ${Number(data.face_match_score).toFixed(1)}）`
      : '';
  if (data.face_verified === true) {
    return `起止人脸核验通过${scoreExtra}`;
  }
  if (data.face_verified !== false) return '';

  const code = data.face_fail_code || '';
  if (code === 'NOT_SAME_PERSON') {
    return `起止人脸核验未通过${scoreExtra}：起止照片非同一人`;
  }
  if (code === 'LIVENESS_FAIL') {
    return '起止人脸核验未通过：未通过活体检测';
  }
  if (code === 'MISSING_PHOTO') {
    return '起止人脸核验未通过：缺少起跑或结束人脸照片';
  }
  if (code === 'LOCAL_DETECT_FAIL') {
    const fr = String(data.fail_reason || '');
    if (fr.includes('人脸')) return fr;
    return '起止人脸核验未通过：未检测到有效人脸';
  }
  if (data.face_match_score != null) {
    return `起止人脸核验未通过${scoreExtra}：起止照片非同一人或相似度过低`;
  }
  const fr = String(data.fail_reason || '');
  if (fr.includes('人脸')) return fr;
  return '起止人脸核验未通过';
};

const loadAiInsight = async (data) => {
  aiInsightLoading.value = true;
  aiInsight.value = null;
  try {
    const isTest = currentMode.value === 'test';
    const payload = isTest
      ? {
          project: data.test_project || testProject.value || '体测项目',
          exercise_type: data.metrics?.exercise_type || data.exercise_type || '',
          count: Number(data.metrics?.count || testCount.value || 0),
          score: data.metrics?.score || null,
          qualified: !!(data.metrics?.qualified ?? testQualified.value)
        }
      : {
          activity_id: data.id || data.activity_id || null,
          distance_km: Number(data.metrics?.distance || 0),
          duration_sec: Number(data.metrics?.duration || 0),
          pace: data.metrics?.pace || null,
          qualified: typeof data.is_valid === 'boolean' ? data.is_valid : !!data.metrics?.qualified
        };
    aiInsight.value = isTest ? await getAiTestFeedback(payload) : await getAiRunReport(payload);
  } catch (e) {
    aiInsight.value = {
      title: currentMode.value === 'test' ? 'AI体测反馈' : 'AI运动报告',
      summary: 'AI建议暂时生成失败，可稍后在 AI 体育助手中重试。',
      suggestions: []
    };
  } finally {
    aiInsightLoading.value = false;
  }
};

const failReasonText = computed(() => {
  const r = failReason.value || '';
  if (r.includes('人脸验证') || r.includes('人脸核验')) {
    return '本次未计入成绩（起止人脸核验未通过）';
  }
  if (r.includes('里程不足') && distance.value < 50) {
    return '里程不足（GPS 可能未正常记录，请到室外重试）';
  }
  return r || '原因未知，请联系老师查看详情';
});

const distanceKmStr = computed(() => (distance.value / 1000).toFixed(2));

const estimatedCalories = computed(() => {
  const km = distance.value / 1000;
  return Math.max(0, Math.round(km * 60));
});

const avgPaceDisplay = computed(() => {
  const km = distance.value / 1000;
  if (km < 0.01 || duration.value <= 0) return "--'--\"";
  const pace = duration.value / 60 / km;
  if (!Number.isFinite(pace) || pace <= 0 || pace >= 999) return "--'--\"";
  const totalSec = Math.round(pace * 60);
  const m = Math.floor(totalSec / 60);
  const s = totalSec % 60;
  return `${m}'${s.toString().padStart(2, '0')}"`;
});

const parseCheckpointsReached = (metrics) => {
  if (!metrics || metrics.checkpoints == null) return false;
  try {
    const raw = metrics.checkpoints;
    const arr = typeof raw === 'string' ? JSON.parse(raw) : raw;
    return Array.isArray(arr) && arr.length > 0;
  } catch (e) {
    return false;
  }
};

const getRouteScale = (spanM) => {
  if (spanM <= 120) return 17;
  if (spanM <= 260) return 16;
  if (spanM <= 650) return 15;
  if (spanM <= 1300) return 14;
  if (spanM <= 2600) return 13;
  return 12;
};

const getPointDistanceM = (a, b) => {
  const R = 6371e3;
  const dLat = ((b.latitude - a.latitude) * Math.PI) / 180;
  const dLng = ((b.longitude - a.longitude) * Math.PI) / 180;
  const m =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((a.latitude * Math.PI) / 180) *
      Math.cos((b.latitude * Math.PI) / 180) *
      Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(m), Math.sqrt(1 - m));
};

const applyMapFromTrajectory = (pts, endpoints = {}) => {
  const routePoints = (Array.isArray(pts) ? pts : [])
    .map((point) => ({
      latitude: Number(point?.latitude ?? point?.lat),
      longitude: Number(point?.longitude ?? point?.lng ?? point?.lon),
      timestamp: point?.timestamp != null ? Number(point.timestamp) : null,
      speed: point?.speed != null ? Number(point.speed) : null
    }))
    .filter((point) => Number.isFinite(point.latitude) && Number.isFinite(point.longitude));
  if (routePoints.length < 1) return;
  const mid = Math.floor(routePoints.length / 2);
  mapCenterLat.value = routePoints[mid].latitude;
  mapCenterLng.value = routePoints[mid].longitude;
  const start = endpoints.start || routePoints[0];
  const end = endpoints.end || routePoints[routePoints.length - 1];
  const spanM = routePoints.reduce(
    (max, point) => Math.max(max, getPointDistanceM(start, point), getPointDistanceM(end, point)),
    getPointDistanceM(start, end)
  );
  mapScale.value = getRouteScale(spanM);

  // Keep the saved route as one explicit native-map polyline. The previous
  // pace-segment rebuild can produce no visible line on App after navigation.
  if (routePoints.length >= 2) {
    resultRoutePoints.value = routePoints;
    setResultRoutePolyline();
  }

  mapMarkers.value = buildRunRouteMarkers([start, end]);
};

onLoad((options) => {
  let data = null;

  if (options.useStorage === 'true') {
    data = uni.getStorageSync('tempRunResult');
  } else if (options.data) {
    try {
      data = JSON.parse(decodeURIComponent(options.data));
    } catch (e) {
      console.error('Failed to parse result data', e);
    }
  }

  if (data) {
    isTaskRun.value = data.source === 'task';
    taskTitle.value = data.task_title || '';
    taskCompleted.value = typeof data.task_completed === 'boolean' ? data.task_completed : null;

    if (data.display_mode) {
      currentMode.value = data.display_mode;
    } else if (data.type === 'test') {
      currentMode.value = data.metrics && data.metrics.distance > 0 ? 'police' : 'test';
    } else if (data.type === 'run') {
      if (isTaskRun.value) currentMode.value = 'police';
      else if (parseCheckpointsReached(data.metrics)) currentMode.value = 'campus';
      else currentMode.value = 'normal';
    } else {
      currentMode.value = 'normal';
    }

    if (data.campus_checkpoint) {
      campusCheckpointName.value = data.campus_checkpoint;
    }

    if (data.metrics) {
      duration.value = data.metrics.duration || 0;
      distance.value = (data.metrics.distance || 0) * 1000;
      testCount.value = data.metrics.count || 0;
      testQualified.value = data.metrics.qualified;
      policePace.value = Number(data.metrics.pace) || 0;
      isPaceQualified.value = data.metrics.qualified;
    }

    if (currentMode.value === 'campus') {
      if (typeof data.campus_reached === 'boolean') {
        isReach.value = data.campus_reached;
      } else {
        isReach.value = parseCheckpointsReached(data.metrics);
      }
    }

    if (typeof data.is_valid !== 'undefined') {
      isValid.value = data.is_valid;
    }
    if (typeof data.fail_reason !== 'undefined') {
      failReason.value = data.fail_reason || '';
    }
    if (typeof data.today_completed !== 'undefined') {
      todayCompleted.value = data.today_completed;
    }
    if (typeof data.face_verified !== 'undefined') {
      faceVerified.value = data.face_verified;
    }
    if (data.face_match_score != null) {
      faceMatchScore.value = data.face_match_score;
    }
    if (data.face_fail_code) {
      faceFailCode.value = data.face_fail_code;
    }
    faceVerifyText.value = buildFaceVerifyText(data);

    if (data.is_valid === false || data.face_verified === false) {
      showMoreDetail.value = true;
    }

    if (isTaskRun.value) {
      isPoliceFinish.value = !!taskCompleted.value;
      isPaceQualified.value = !!taskCompleted.value;
    } else if (currentMode.value === 'police' && data.metrics) {
      isPoliceFinish.value = Number(data.metrics.distance || 0) >= 2;
    }

    if (currentMode.value === 'test') {
      testProject.value = data.test_project || '体测项目';
      suggestionText.value = testQualified.value ? '恭喜达标！' : '继续加油！';
      const score = data.metrics?.score || 0;
      userScorePercent.value = Math.min(100, score);
      standardScorePercent.value = 60;
    }

    loadAiInsight(data);
  } else {
    currentMode.value = options.mode || 'normal';
    duration.value = Number(options.duration) || 0;
    distance.value = Number(options.distance) || 0;
    isReach.value = options.isReach === 'true';
    isPoliceFinish.value = options.isPoliceFinish === 'true';
    policePace.value = Number(options.policePace) || 0;
  }

  const trajectoryData = parseStoredTrajectory(uni.getStorageSync('tempRunTrajectory'));
  const storedPoints = normalizeStoredPoints(trajectoryData?.points);
  const storedPolylinePoints = normalizeStoredPoints(trajectoryData?.polylinePoints);
  if (trajectoryData && storedPoints.length >= 1) {
    const start = {
      latitude: trajectoryData.startLat ?? storedPoints[0].latitude,
      longitude: trajectoryData.startLng ?? storedPoints[0].longitude
    };
    const end = {
      latitude: trajectoryData.endLat ?? storedPoints[storedPoints.length - 1].latitude,
      longitude: trajectoryData.endLng ?? storedPoints[storedPoints.length - 1].longitude
    };
    const renderPoints = storedPoints.length >= 2 ? storedPoints : storedPolylinePoints;
    console.info('[run-result] restored route points:', storedPoints.length, renderPoints.length);
    trajectoryPoints.value = renderPoints;
    applyMapFromTrajectory(renderPoints, { start, end });
  } else if (trajectoryData && trajectoryData.startLat) {
    mapCenterLat.value = trajectoryData.startLat;
    mapCenterLng.value = trajectoryData.startLng;
    const fallbackPoints = [
      { latitude: trajectoryData.startLat, longitude: trajectoryData.startLng }
    ];
    if (
      trajectoryData.endLat != null &&
      trajectoryData.endLng != null &&
      (trajectoryData.endLat !== trajectoryData.startLat || trajectoryData.endLng !== trajectoryData.startLng)
    ) {
      fallbackPoints.push({
        latitude: trajectoryData.endLat,
        longitude: trajectoryData.endLng
      });
    }
    mapMarkers.value = buildRunRouteMarkers(fallbackPoints);
  }

  // Mount after the route state has reached Vue. Otherwise App can render
  // markers but silently miss the first polyline assignment.
  nextTick(() => {
    resultMapReady.value = mapCenterLat.value !== 0 && mapCenterLng.value !== 0;
    // Some App native map instances accept markers on first mount but ignore
    // the polyline prop. Re-apply it after the component has attached.
    setTimeout(() => {
      if (!resultMapReady.value || resultRoutePoints.value.length < 2) return;
      mapPolyline.value = [];
      setTimeout(setResultRoutePolyline, 60);
    }, 0);
  });
});

const formatDuration = (seconds) => {
  const s = Math.max(0, Math.floor(Number(seconds) || 0));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  const pad = (n) => n.toString().padStart(2, '0');
  if (h > 0) return `${pad(h)}:${pad(m)}:${pad(sec)}`;
  return `${pad(m)}:${pad(sec)}`;
};

const backToHome = () => {
  uni.reLaunch({ url: '/pages/tab/home' });
};
</script>

<style scoped lang="scss">
@import '@/styles/run-sport-theme.scss';

.result-page.result-sport {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
}

.result-map-wrap {
  width: 100%;
  height: 60vh;
  min-height: 520rpx;
  flex-shrink: 0;
  position: relative;
}

.route-pace-legend {
  position: absolute;
  right: 22rpx;
  bottom: 20rpx;
  z-index: 3;
  display: flex;
  align-items: center;
  padding: 10rpx 14rpx;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 8rpx;
  box-shadow: 0 4rpx 12rpx rgba(24, 35, 46, 0.14);
}
.route-pace-legend__label { color: #64748B; font-size: 20rpx; }
.route-pace-legend__swatch { width: 22rpx; height: 10rpx; margin: 0 3rpx; border-radius: 3rpx; }
.route-pace-legend__swatch--blue { background: #1E88E5; }
.route-pace-legend__swatch--green { background: #4CAF50; }
.route-pace-legend__swatch--amber { background: #FFC107; }
.route-pace-legend__swatch--red { background: #FF5252; }

.result-map-full {
  width: 100%;
  height: 100%;
}

.result-hero {
  margin: -40rpx 24rpx 24rpx;
  position: relative;
  z-index: 2;
  background: #fff;
  border-radius: 20rpx;
  padding: 32rpx 32rpx 28rpx;
  box-shadow: 0 8rpx 28rpx rgba(0, 0, 0, 0.06);
}

.result-mode-tag {
  color: var(--run-text-secondary);
  font-size: 26rpx;
}

.result-distance-row {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  margin-top: 16rpx;
}

.result-distance-num {
  color: #20c997;
  font-size: 96rpx;
  font-weight: 700;
  line-height: 1;
}

.result-distance-unit {
  color: var(--run-text-primary);
  font-size: 32rpx;
  margin-left: 12rpx;
  margin-bottom: 16rpx;
}

.result-pace-legend {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin: 28rpx 0 32rpx;
  gap: 16rpx;
}

.legend-slow,
.legend-fast {
  color: var(--run-text-secondary);
  font-size: 24rpx;
  flex-shrink: 0;
}

.legend-gradient {
  flex: 1;
  height: 12rpx;
  border-radius: 6rpx;
  background: linear-gradient(to right, var(--run-pace-slow), var(--run-pace-mid), var(--run-pace-fast));
}

.result-metrics-row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.result-metric {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.result-metric-val {
  color: var(--run-text-primary);
  font-size: 40rpx;
  font-weight: 600;
}

.result-metric-lbl {
  color: var(--run-text-secondary);
  font-size: 24rpx;
  margin-top: 8rpx;
}

.result-more {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-top: 32rpx;
  padding-top: 24rpx;
  border-top: 1rpx solid #eee;
}

.result-more-title {
  color: var(--run-text-secondary);
  font-size: 28rpx;
}

.result-more-arrow {
  color: var(--run-text-muted);
  font-size: 24rpx;
}

.result-more-body {
  margin-top: 20rpx;
}

.data-item {
  display: flex;
  justify-content: space-between;
  padding: 16rpx 0;
  border-bottom: 1rpx solid rgba(255, 255, 255, 0.06);
}

.item-label {
  color: var(--run-text-secondary);
  font-size: 26rpx;
}

.item-value {
  color: var(--run-text-primary);
  font-size: 26rpx;
  max-width: 60%;
  text-align: right;
}

.item-value.success,
.verify-text.success {
  color: #4caf50;
}

.item-value.fail,
.verify-text.fail {
  color: #ff5252;
}

.verify-section {
  margin-top: 16rpx;
}

.verify-title {
  color: var(--run-text-secondary);
  font-size: 26rpx;
  display: block;
  margin-bottom: 8rpx;
}

.verify-text {
  font-size: 26rpx;
  line-height: 1.5;
}

.result-inline-tip {
  margin-top: 24rpx;
  padding: 16rpx 20rpx;
  border-radius: 12rpx;
  background: #f8f9fb;
  text-align: center;
}

.result-inline-tip .tip-ok {
  color: #4caf50;
  font-size: 26rpx;
}

.result-inline-tip .tip-warn {
  color: #e57373;
  font-size: 26rpx;
}

.result-primary-btn {
  margin-top: 24rpx;
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: #20c997;
  color: #fff;
  border: none;
  border-radius: 16rpx;
  font-size: 32rpx;
  font-weight: 600;
}

.result-primary-btn::after {
  border: none;
}

.result-card-test {
  margin: 24rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
}

.bar-chart {
  margin: 16rpx 0;
}

.bar-row {
  display: flex;
  align-items: center;
  margin-bottom: 12rpx;
}

.bar-label {
  width: 80rpx;
  font-size: 26rpx;
  color: #666;
}

.bar-track {
  flex: 1;
  height: 36rpx;
  background: #f0f0f0;
  border-radius: 18rpx;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
}

.user-fill {
  background: #20c997;
}

.standard-fill {
  background: #ddd;
}

.suggestion-box {
  margin-top: 16rpx;
}

.sugg-text {
  font-size: 26rpx;
  color: #555;
}

.ai-insight-card {
  margin-top: 24rpx;
  padding: 24rpx;
  border-radius: 16rpx;
  background: #f4faf8;
  border: 1rpx solid rgba(32, 201, 151, 0.16);
}

.ai-insight-title {
  display: block;
  color: #102433;
  font-size: 28rpx;
  font-weight: 800;
}

.ai-insight-summary {
  display: block;
  margin-top: 12rpx;
  color: #405160;
  font-size: 26rpx;
  line-height: 1.55;
}

.ai-insight-list {
  margin-top: 12rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.ai-insight-item {
  color: #1f7a68;
  font-size: 24rpx;
  line-height: 1.5;
}
</style>
