<template>
  <view class="container">
    <view class="info-card">
      <view class="header">
        <text class="title">任务跑步详情</text>
        <text class="status" :class="activity.is_valid ? 'ok' : 'bad'">
          {{ activity.is_valid ? '任务达标' : '未达标' }}
        </text>
      </view>
      <text class="task-name">{{ activity.task_title }}</text>
      <view class="detail-row">
        <text class="label">学员</text>
        <text class="value">{{ student.name }} {{ student.student_no ? `（${student.student_no}）` : '' }}</text>
      </view>
      <view class="detail-row">
        <text class="label">时间</text>
        <text class="value">{{ displayTime }}</text>
      </view>
      <view class="detail-row" v-if="metrics">
        <text class="label">距离</text>
        <text class="value">{{ distanceKm }} km</text>
      </view>
      <view class="detail-row" v-if="paceText">
        <text class="label">配速</text>
        <text class="value">{{ paceText }} 分/公里</text>
      </view>
      <view class="detail-row" v-if="metrics && metrics.duration != null">
        <text class="label">时长</text>
        <text class="value">{{ Math.floor(metrics.duration / 60) }} 分 {{ metrics.duration % 60 }} 秒</text>
      </view>
      <view class="detail-row" v-if="activity.fail_reason">
        <text class="label">说明</text>
        <text class="value fail-text">{{ activity.fail_reason }}</text>
      </view>
    </view>

    <view class="photo-card" v-if="activity.type === 'run'">
      <text class="page-section-title">起止人脸核验</text>
      <view class="face-verify-meta" v-if="activity.face_verified != null">
        <text class="face-meta-line" :class="activity.face_verified ? 'ok' : 'bad'">
          {{ activity.face_verified ? '系统核验通过' : '系统核验未通过' }}
        </text>
        <text v-if="activity.face_match_score != null" class="face-meta-sub">
          相似度 {{ Number(activity.face_match_score).toFixed(1) }}
        </text>
        <text v-if="activity.face_fail_code" class="face-meta-sub">代码 {{ activity.face_fail_code }}</text>
      </view>
      <view class="photo-grid">
        <view class="photo-item">
          <text class="photo-label">跑前</text>
          <image v-if="startPhotoUrl" class="photo-img" :src="startPhotoUrl" mode="aspectFill" />
          <view v-else class="photo-placeholder">暂无照片</view>
        </view>
        <view class="photo-item">
          <text class="photo-label">跑后</text>
          <image v-if="endPhotoUrl" class="photo-img" :src="endPhotoUrl" mode="aspectFill" />
          <view v-else class="photo-placeholder">暂无照片</view>
        </view>
      </view>
    </view>

    <view class="test-card" v-if="activity.type === 'test' && metrics">
      <text class="page-section-title">体测视频分析</text>
      <view class="detail-row">
        <text class="label">项目</text>
        <text class="value">{{ exerciseLabel }}</text>
      </view>
      <view class="detail-row">
        <text class="label">完成次数</text>
        <text class="value">{{ metrics.count != null ? metrics.count : '—' }} 次</text>
      </view>
      <view class="detail-row">
        <text class="label">分析状态</text>
        <text class="value">{{ analysisStatusText }}</text>
      </view>
      <view class="detail-row" v-if="metrics.score != null">
        <text class="label">AI评分</text>
        <text class="value">{{ metrics.score }} 分</text>
      </view>
      <video
        v-if="testVideoUrl"
        class="test-video"
        :src="testVideoUrl"
        controls
      />
      <text v-if="metrics.analysis_error" class="fail-text">{{ metrics.analysis_error }}</text>
    </view>

    <view class="map-card" v-if="showMap && activity.type === 'run'">
      <text class="page-section-title">运动轨迹</text>
      <map
        class="map"
        :latitude="centerLat"
        :longitude="centerLng"
        :polyline="polyline"
        :markers="markers"
        :enable-zoom="true"
        :enable-scroll="true"
      />
    </view>
    <view class="no-data-card" v-else>
      <text class="tip">暂无轨迹数据</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { getTeacherTaskRunDetail, resolveMediaUrl } from '@/utils/request.js';
import { smoothTrajectoryForMap, DEFAULT_BRAND_POLYLINE_STYLE } from '@/utils/trajectory-smooth.js';
import { buildRunRouteMarkers } from '@/utils/run-map-markers.js';

const activity = ref({});
const student = ref({});
const metrics = ref(null);
const displayTime = ref('');
const distanceKm = ref('0.00');
const paceText = ref('');
const centerLat = ref(39.909);
const centerLng = ref(116.397);
const polyline = ref([]);
const markers = ref([]);
const showMap = ref(false);
const startPhotoUrl = ref('');
const endPhotoUrl = ref('');
const testVideoUrl = ref('');

const exerciseLabel = computed(() => {
  const t = metrics.value?.exercise_type || '';
  const map = { pull_up: '引体向上', sit_up: '仰卧起坐', push_up: '俯卧撑' };
  return map[t] || t || '体测';
});

const analysisStatusText = computed(() => {
  const s = metrics.value?.analysis_status;
  if (s === 'pending') return '分析中';
  if (s === 'success') return '已完成';
  if (s === 'failed') return '分析失败';
  return s || '—';
});

function normalizeTrajectoryPoints(raw) {
  if (raw == null) return [];
  let arr = raw;
  if (typeof raw === 'string') {
    try {
      arr = JSON.parse(raw);
    } catch {
      return [];
    }
  }
  if (!Array.isArray(arr)) return [];
  const out = [];
  for (const p of arr) {
    if (!p || typeof p !== 'object') continue;
    const lat = Number(p.latitude ?? p.lat);
    const lng = Number(p.longitude ?? p.lng ?? p.lon);
    if (Number.isFinite(lat) && Number.isFinite(lng)) {
      out.push({ latitude: lat, longitude: lng });
    }
  }
  return out;
}

onLoad(async (options) => {
  const aid = options.activityId ? parseInt(options.activityId, 10) : 0;
  if (!aid) return;
  try {
    const res = await getTeacherTaskRunDetail(aid);
    activity.value = res.activity || {};
    student.value = res.student || {};
    metrics.value = res.metrics || null;
    startPhotoUrl.value = activity.value.start_photo_url ? resolveMediaUrl(activity.value.start_photo_url) : '';
    endPhotoUrl.value = activity.value.end_photo_url ? resolveMediaUrl(activity.value.end_photo_url) : '';
    testVideoUrl.value =
      metrics.value && metrics.value.video_url ? resolveMediaUrl(metrics.value.video_url) : '';

    if (activity.value.started_at) {
      const d = new Date(activity.value.started_at);
      displayTime.value = `${d.getMonth() + 1}-${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
    }
    if (metrics.value) {
      if (metrics.value.distance != null) {
        distanceKm.value = Number(metrics.value.distance).toFixed(2);
      }
      if (metrics.value.pace != null) {
        paceText.value = Number(metrics.value.pace).toFixed(1);
      }
    }

    let points = [];
    if (metrics.value && metrics.value.trajectory) {
      points = normalizeTrajectoryPoints(metrics.value.trajectory);
    }
    polyline.value = [];
    markers.value = [];
    showMap.value = false;
    if (points.length >= 2) {
      const displayPts = smoothTrajectoryForMap(points);
      polyline.value = [{ ...DEFAULT_BRAND_POLYLINE_STYLE, points: displayPts }];
      centerLat.value = points[0].latitude;
      centerLng.value = points[0].longitude;
      markers.value = buildRunRouteMarkers(points);
      showMap.value = true;
    } else if (points.length === 1) {
      centerLat.value = points[0].latitude;
      centerLng.value = points[0].longitude;
      markers.value = buildRunRouteMarkers(points.slice(0, 1));
      showMap.value = true;
    }

  } catch (e) {
    console.error(e);
    uni.showToast({ title: '加载失败', icon: 'none' });
  }
});
</script>

<style lang="scss">
.container {
  padding: 20rpx;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.info-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16rpx;
    .title {
      font-size: 34rpx;
      font-weight: bold;
    }
    .status {
      font-size: 26rpx;
    }
    .status.ok {
      color: #20c997;
    }
    .status.bad {
      color: #ff4d4f;
    }
  }
  .task-name {
    font-size: 28rpx;
    color: #666;
    margin-bottom: 20rpx;
    display: block;
  }
  .detail-row {
    display: flex;
    margin-bottom: 12rpx;
    font-size: 28rpx;
    .label {
      color: #888;
      width: 140rpx;
    }
    .value {
      flex: 1;
      color: #333;
    }
    .fail-text {
      color: #ff4d4f;
    }
  }
}
.map-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  .section-title {
    font-size: 30rpx;
    font-weight: bold;
    margin-bottom: 16rpx;
    display: block;
  }
}
.photo-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}
.photo-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}
.photo-item {
  display: flex;
  flex-direction: column;
}
.photo-label {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 12rpx;
}
.photo-img,
.photo-placeholder {
  width: 100%;
  height: 220rpx;
  border-radius: 12rpx;
  background: #f3f4f6;
}
.photo-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 24rpx;
}
.map {
  width: 100%;
  height: 420rpx;
  border-radius: 12rpx;
}
.no-data-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 40rpx;
  text-align: center;
  color: #999;
}
.test-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}
.test-video {
  width: 100%;
  height: 360rpx;
  margin-top: 16rpx;
  border-radius: 12rpx;
}
.face-verify-meta {
  margin-bottom: 16rpx;
}
.face-meta-line {
  font-size: 28rpx;
  display: block;
}
.face-meta-line.ok {
  color: #20c997;
}
.face-meta-line.bad {
  color: #e53935;
}
.face-meta-sub {
  font-size: 24rpx;
  color: #888;
  display: block;
  margin-top: 8rpx;
}
</style>
