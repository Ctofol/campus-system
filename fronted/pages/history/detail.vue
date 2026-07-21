<template>
  <view class="container">
    <!-- 运动基本信息 -->
    <view class="info-card">
      <view class="header">
        <text class="title">{{ headerTitle }}</text>
        <text class="status completed">{{ headerSubTitle }}</text>
      </view>
      <view class="detail-row">
        <text class="label">类型:</text>
        <text class="value">{{ activity.type === 'run' ? '跑步' : '体测' }}</text>
      </view>
      <view class="detail-row">
        <text class="label">时间:</text>
        <text class="value">{{ displayTime }}</text>
      </view>
      <view class="detail-row">
        <text class="label">距离:</text>
        <text class="value">{{ distanceKm }} 公里</text>
      </view>
      <view class="detail-row" v-if="paceText">
        <text class="label">平均配速:</text>
        <text class="value">{{ paceText }} 分/公里</text>
      </view>
      <view class="detail-row" v-if="stepCount">
        <text class="label">步数:</text>
        <text class="value">{{ stepCount }} 步</text>
      </view>
      <view class="detail-row" v-if="stepFrequency">
        <text class="label">步频:</text>
        <text class="value">{{ stepFrequency }} 步/分钟</text>
      </view>
    </view>

    <!-- Map Trajectory（微信折线至少 2 点；仅 1 点时只显示标记、不传折线，避免渲染层 MultiPolyline 崩溃） -->
    <view class="map-card" v-if="showMap">
      <text class="page-section-title">运动轨迹</text>
      <map
        id="history-route-map"
        class="map" 
        :latitude="centerLat" 
        :longitude="centerLng" 
        :polyline="polyline"
        :markers="markers"
        :enable-zoom="true"
        :enable-scroll="true"
      ></map>
      <view class="route-pace-legend">
        <text class="route-pace-legend__label">慢</text>
        <view class="route-pace-legend__swatch route-pace-legend__swatch--blue" />
        <view class="route-pace-legend__swatch route-pace-legend__swatch--green" />
        <view class="route-pace-legend__swatch route-pace-legend__swatch--amber" />
        <view class="route-pace-legend__swatch route-pace-legend__swatch--red" />
        <text class="route-pace-legend__label">快</text>
      </view>
    </view>
    <view class="no-data-card" v-else-if="!showMap && activity && (activity.status === 'finished' || activity.status === 'completed')">
        <text class="tip">暂无轨迹数据</text>
    </view>

    <!-- Video Evidence -->
    <view class="video-card" v-if="videoUrl">
      <text class="page-section-title">视频记录</text>
      <video :src="videoUrl" class="video" controls></video>
    </view>
  </view>
</template>

<script setup>
import { nextTick, ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { smoothTrajectoryForMap, DEFAULT_BRAND_POLYLINE_STYLE } from '@/utils/trajectory-smooth.js';
import { buildPaceColoredPolylines } from '@/utils/trajectory-pace-polyline.js';
import { buildRunRouteMarkers } from '@/utils/run-map-markers.js';

const activity = ref({});
const centerLat = ref(39.909);
const centerLng = ref(116.397);
const polyline = ref([]);
const markers = ref([]);
const includePoints = ref([]);
const mapPadding = [18, 18, 18, 18];
const videoUrl = ref('');
/** 是否展示地图区：≥2 点可走折线；1 点仅标记；0 点不展示（避免传非法 polyline） */
const showMap = ref(false);

const headerTitle = ref('运动详情');
const headerSubTitle = ref('');
const displayTime = ref('');
const distanceKm = ref('0.00');
const paceText = ref('');
const stepCount = ref(0);
const stepFrequency = ref('');

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
      out.push({
        latitude: lat,
        longitude: lng,
        timestamp: p.timestamp != null ? Number(p.timestamp) : null,
        speed: p.speed != null ? Number(p.speed) : null
      });
    }
  }
  return out;
}

function fitRouteMap() {
  if (!includePoints.value.length) return;
  nextTick(() => setTimeout(() => {
    const mapContext = uni.createMapContext('history-route-map');
    if (mapContext && typeof mapContext.includePoints === 'function') {
      mapContext.includePoints({
        points: includePoints.value,
        padding: mapPadding
      });
    }
  }, 220));
}

onLoad((options) => {
    if (options.data) {
        try {
            const data = JSON.parse(decodeURIComponent(options.data));
            activity.value = data;
            
            // 基础信息
            if (data.started_at) {
              const d = new Date(data.started_at);
              displayTime.value = `${d.getMonth()+1}-${d.getDate()} ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`;
            }
            if (data.metrics) {
              if (data.metrics.distance != null) {
                distanceKm.value = Number(data.metrics.distance).toFixed(2);
              }
              if (data.metrics.pace != null) {
                paceText.value = Number(data.metrics.pace).toFixed(1);
              }
              if (data.metrics.step_count != null) {
                stepCount.value = data.metrics.step_count;
                if (data.metrics.duration) {
                  const minutes = data.metrics.duration / 60;
                  if (minutes > 0) {
                    stepFrequency.value = Math.round(stepCount.value / minutes);
                  }
                }
              }
            }

            // Process Trajectory（微信 map 折线至少 2 个合法点，否则渲染层报 MultiPolyline / typed array length 错误）
            let points = [];
            if (data.trajectory) {
                points = normalizeTrajectoryPoints(data.trajectory);
            } else if (data.metrics && data.metrics.trajectory) {
                points = normalizeTrajectoryPoints(data.metrics.trajectory);
            }

            polyline.value = [];
            markers.value = [];
            includePoints.value = [];
            showMap.value = false;

            if (points.length >= 2) {
                const paceLines = buildPaceColoredPolylines(points);
                if (paceLines.length > 0) {
                  polyline.value = paceLines;
                } else {
                  const displayPts = smoothTrajectoryForMap(points);
                  polyline.value = [{
                    ...DEFAULT_BRAND_POLYLINE_STYLE,
                    points: displayPts
                  }];
                }
                centerLat.value = points[0].latitude;
                centerLng.value = points[0].longitude;
                markers.value = buildRunRouteMarkers(points);
                includePoints.value = points.map((p) => ({
                  latitude: p.latitude,
                  longitude: p.longitude
                }));
                showMap.value = true;
                fitRouteMap();
            } else if (points.length === 1) {
                centerLat.value = points[0].latitude;
                centerLng.value = points[0].longitude;
                markers.value = buildRunRouteMarkers(points.slice(0, 1));
                includePoints.value = [{
                  latitude: points[0].latitude,
                  longitude: points[0].longitude
                }];
                showMap.value = true;
                fitRouteMap();
            }
            
            // Process Video
            if (data.evidence) {
                // Evidence is usually an array of { type: 'video', url: '...' }
                // or just a string url if simplified
                if (Array.isArray(data.evidence)) {
                    const vid = data.evidence.find((e) => {
                      if (e == null) return false;
                      if (typeof e === 'string') return e.endsWith('.mp4');
                      if (e.type === 'video' && typeof e.url === 'string') return true;
                      return typeof e.url === 'string' && e.url.endsWith('.mp4');
                    });
                    if (vid != null) {
                      videoUrl.value = typeof vid === 'string' ? vid : (vid.url || '');
                    }
                } else if (typeof data.evidence === 'string' && data.evidence.endsWith('.mp4')) {
                    videoUrl.value = data.evidence;
                }
            }
            
        } catch (e) {
            console.error('Parse task detail failed', e);
        }
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
    margin-bottom: 20rpx;
    border-bottom: 1px solid #eee;
    padding-bottom: 20rpx;
    .title { font-size: 36rpx; font-weight: bold; }
    .status { font-size: 28rpx; color: #666; }
    .status.completed { color: #20C997; }
    .status.expired { color: #999; }
  }
  .detail-row {
    display: flex;
    margin-bottom: 10rpx;
    font-size: 28rpx;
    .label { color: #666; width: 160rpx; }
    .value { color: #333; flex: 1; }
    .highlight { color: #20C997; font-weight: bold; }
  }
}
.map-card, .video-card, .no-data-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  .section-title {
    font-size: 32rpx;
    font-weight: bold;
    margin-bottom: 20rpx;
    display: block;
    border-left: 8rpx solid #20C997;
    padding-left: 16rpx;
  }
}
.map-card {
  padding: 24rpx 18rpx 18rpx;
  position: relative;
}
.route-pace-legend {
  position: absolute;
  right: 34rpx;
  bottom: 32rpx;
  z-index: 2;
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
.page-section-title {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 18rpx;
  display: block;
  border-left: 8rpx solid #20C997;
  padding-left: 16rpx;
}
.map {
    width: 100%;
    height: 900rpx;
    min-height: 560rpx;
    border-radius: 12rpx;
    overflow: hidden;
}
.video {
    width: 100%;
    height: 400rpx;
    border-radius: 12rpx;
}
.no-data-card {
    text-align: center;
    color: #999;
    padding: 40rpx;
}
</style>
