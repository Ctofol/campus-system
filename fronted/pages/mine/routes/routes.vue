<template>
  <view class="routes-page">
    <page-tab-header title="我的路线" show-back theme="white" />

    <view class="routes-body page-tab-body page-tab-body--compact-top">
      <view class="route-hero">
        <view class="route-hero__header">
          <view>
            <text class="route-hero__title">{{ heroTitle }}</text>
            <text class="route-hero__sub">{{ heroSubTitle }}</text>
          </view>
          <view class="route-hero__pill" @tap="goHistory">
            <text>全部记录</text>
          </view>
        </view>

        <view class="route-map" :class="{ 'route-map--empty': !heroHasTrack }">
          <view class="route-map__block route-map__block--a" />
          <view class="route-map__block route-map__block--b" />
          <view class="route-map__block route-map__block--c" />
          <view class="route-map__road route-map__road--main" />
          <view class="route-map__road route-map__road--side" />

          <template v-if="heroHasTrack">
            <view
              v-for="(segment, index) in heroRouteSegments"
              :key="index"
              class="route-segment"
              :style="segment.style"
            />
            <view class="route-dot route-dot--start" :style="heroStartDotStyle" />
            <view class="route-dot route-dot--end" :style="heroEndDotStyle" />
          </template>

          <view v-else class="route-map__empty">
            <text class="route-map__empty-title">暂无可预览路线</text>
            <text class="route-map__empty-sub">完成一次户外跑步后会自动生成</text>
          </view>
        </view>
      </view>

      <view class="stats-grid">
        <view class="stat-card">
          <text class="stat-val">{{ routeStats.count }}</text>
          <text class="stat-label">路线次数</text>
        </view>
        <view class="stat-card">
          <text class="stat-val">{{ routeStats.distance }}</text>
          <text class="stat-label">累计公里</text>
        </view>
        <view class="stat-card">
          <text class="stat-val">{{ routeStats.longest }}</text>
          <text class="stat-label">最长路线</text>
        </view>
        <view class="stat-card">
          <text class="stat-val">{{ routeStats.avgPace }}</text>
          <text class="stat-label">平均配速</text>
        </view>
      </view>

      <view class="route-list-card">
        <view class="section-head">
          <text class="section-title">最近路线</text>
          <text class="section-more" @tap="goHistory">查看全部 ›</text>
        </view>

        <view v-if="loading" class="route-loading">
          <view v-for="i in 3" :key="i" class="route-skeleton" />
        </view>

        <view v-else-if="routes.length === 0" class="route-empty">
          <text>暂无跑步路线</text>
        </view>

        <view v-else class="route-list">
          <view
            v-for="item in routes"
            :key="item.id"
            class="route-item"
            @tap="goDetail(item)"
          >
            <HomeRecentMapThumb :preview="item.preview" :has-track="item.hasTrack" />
            <view class="route-item__info">
              <view class="route-item__top">
                <text class="route-item__title">{{ item.title }}</text>
                <text class="route-item__arrow">›</text>
              </view>
              <text class="route-item__meta">{{ item.dateText }} · {{ item.distanceText }}km · {{ item.durationText }}</text>
              <text class="route-item__sub">{{ item.hasTrack ? '可查看完整轨迹' : '本次暂无轨迹点' }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import PageTabHeader from '@/components/page-tab-header/page-tab-header.vue';
import HomeRecentMapThumb from '@/components/student-home/HomeRecentMapThumb.vue';
import { request } from '@/utils/request.js';
import { isValidSunshineRun } from '@/utils/activity-record.js';

const loading = ref(false);
const routes = ref([]);

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

  return arr
    .map((p) => {
      const lat = Number(p?.latitude ?? p?.lat);
      const lng = Number(p?.longitude ?? p?.lng ?? p?.lon);
      if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
      return { lat, lng };
    })
    .filter(Boolean);
}

function pickRoutePreview(points) {
  if (!points.length) return [];
  if (points.length <= 24) return points;
  const step = Math.ceil(points.length / 24);
  const sampled = points.filter((_, index) => index % step === 0);
  const last = points[points.length - 1];
  const sampledLast = sampled[sampled.length - 1];
  if (sampledLast && (sampledLast.lat !== last.lat || sampledLast.lng !== last.lng)) {
    sampled.push(last);
  }
  return sampled;
}

function formatDuration(seconds) {
  const total = Math.max(0, Number(seconds) || 0);
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = Math.floor(total % 60);
  return `${h > 0 ? h + ':' : ''}${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function formatDateTime(iso) {
  if (!iso) return '未知时间';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '未知时间';
  return `${d.getMonth() + 1}-${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

function mapActivityToRoute(item, index) {
  const rawPoints = normalizeTrajectoryPoints(item.trajectory || item.metrics?.trajectory);
  const preview = pickRoutePreview(rawPoints);
  const distance = Number(item.metrics?.distance || 0);
  const duration = Number(item.metrics?.duration || 0);
  const pace = Number(item.metrics?.pace || 0);
  return {
    id: item.id || `${item.started_at || 'route'}-${index}`,
    raw: item,
    title: item.title || `路线 ${index + 1}`,
    dateText: formatDateTime(item.started_at || item.created_at),
    distance,
    distanceText: distance.toFixed(2),
    duration,
    durationText: formatDuration(duration),
    pace,
    preview,
    hasTrack: preview.length >= 2
  };
}

async function loadRoutes() {
  if (loading.value) return;
  loading.value = true;
  try {
    const res = await request({
      url: '/activity/history',
      method: 'GET',
      data: { page: 1, size: 50 }
    });
    const list = Array.isArray(res?.items) ? res.items : [];
    routes.value = list
      .filter((item) => item.type === 'run')
      .filter((item) => !item.task_id && item.source !== 'task')
      .filter((item) => item.status !== 'cancelled')
      .filter((item) => isValidSunshineRun(item) || Number(item.metrics?.distance || 0) > 0)
      .map(mapActivityToRoute);
  } catch (e) {
    console.error('Fetch my routes failed', e);
    routes.value = [];
    uni.showToast({ title: '路线加载失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
}

const heroRoute = computed(() => routes.value.find((item) => item.hasTrack) || routes.value[0] || null);
const heroPoints = computed(() => heroRoute.value?.preview || []);
const heroHasTrack = computed(() => heroPoints.value.length >= 2);
const heroTitle = computed(() => heroRoute.value ? '最近路线' : '我的路线');
const heroSubTitle = computed(() => {
  if (!heroRoute.value) return '沉淀常跑路线，方便复盘训练习惯';
  return `${heroRoute.value.dateText} · ${heroRoute.value.distanceText}km`;
});

const heroNormalizedPoints = computed(() => {
  const pts = heroPoints.value;
  if (pts.length < 2) return [];
  const minLat = Math.min(...pts.map((p) => p.lat));
  const maxLat = Math.max(...pts.map((p) => p.lat));
  const minLng = Math.min(...pts.map((p) => p.lng));
  const maxLng = Math.max(...pts.map((p) => p.lng));
  const latRange = Math.max(maxLat - minLat, 0.00001);
  const lngRange = Math.max(maxLng - minLng, 0.00001);
  const padding = 10;
  const drawable = 100 - padding * 2;
  return pts.map((p) => ({
    x: padding + ((p.lng - minLng) / lngRange) * drawable,
    y: padding + (1 - (p.lat - minLat) / latRange) * drawable
  }));
});

const heroRouteSegments = computed(() => {
  const pts = heroNormalizedPoints.value;
  return pts.slice(1).map((point, index) => {
    const prev = pts[index];
    const dx = point.x - prev.x;
    const dy = point.y - prev.y;
    const length = Math.sqrt(dx * dx + dy * dy);
    const angle = Math.atan2(dy, dx) * (180 / Math.PI);
    return {
      style: `left:${prev.x}%;top:${prev.y}%;width:${length}%;transform:rotate(${angle}deg);`
    };
  });
});

function dotStyle(point) {
  if (!point) return 'left:50%;top:50%;';
  return `left:${point.x}%;top:${point.y}%;`;
}

const heroStartDotStyle = computed(() => dotStyle(heroNormalizedPoints.value[0]));
const heroEndDotStyle = computed(() => dotStyle(heroNormalizedPoints.value[heroNormalizedPoints.value.length - 1]));

const routeStats = computed(() => {
  const count = routes.value.length;
  const distance = routes.value.reduce((sum, item) => sum + item.distance, 0);
  const longest = routes.value.reduce((max, item) => Math.max(max, item.distance), 0);
  const paceRoutes = routes.value.filter((item) => item.pace > 0);
  const avgPace = paceRoutes.length
    ? (paceRoutes.reduce((sum, item) => sum + item.pace, 0) / paceRoutes.length).toFixed(1)
    : '--';
  return {
    count,
    distance: distance.toFixed(2),
    longest: longest.toFixed(2),
    avgPace
  };
});

function goHistory() {
  uni.navigateTo({ url: '/pages/history/history' });
}

function goDetail(item) {
  try {
    const dataStr = encodeURIComponent(JSON.stringify(item.raw));
    uni.navigateTo({ url: `/pages/history/detail?data=${dataStr}` });
  } catch (e) {
    console.error('Go route detail failed', e);
  }
}

onShow(loadRoutes);
</script>

<style scoped>
.routes-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.routes-body {
  padding: 18rpx 24rpx 40rpx;
  box-sizing: border-box;
}

.route-hero,
.route-list-card,
.stat-card {
  background: #fff;
  border-radius: 24rpx;
}

.route-hero {
  padding: 28rpx;
  margin-bottom: 22rpx;
}

.route-hero__header,
.section-head,
.route-item__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.route-hero__title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: #182b3a;
}

.route-hero__sub {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #7b8b99;
}

.route-hero__pill {
  height: 56rpx;
  padding: 0 22rpx;
  border-radius: 999rpx;
  background: #eef9f5;
  color: #20c997;
  font-size: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.route-map {
  position: relative;
  height: 320rpx;
  margin-top: 24rpx;
  border-radius: 22rpx;
  overflow: hidden;
  background:
    linear-gradient(90deg, rgba(125, 180, 159, 0.14) 1rpx, transparent 1rpx),
    linear-gradient(0deg, rgba(125, 180, 159, 0.12) 1rpx, transparent 1rpx),
    linear-gradient(145deg, #f6fcf9 0%, #dff3ea 100%);
  background-size: 42rpx 42rpx, 42rpx 42rpx, 100% 100%;
}

.route-map--empty {
  background: linear-gradient(145deg, #f8fbfa 0%, #e9f5ef 100%);
}

.route-map__block {
  position: absolute;
  border-radius: 14rpx;
  background: rgba(149, 202, 181, 0.22);
}

.route-map__block--a {
  left: 36rpx;
  top: 34rpx;
  width: 120rpx;
  height: 58rpx;
}

.route-map__block--b {
  right: 46rpx;
  top: 56rpx;
  width: 148rpx;
  height: 72rpx;
}

.route-map__block--c {
  left: 220rpx;
  bottom: 40rpx;
  width: 190rpx;
  height: 54rpx;
}

.route-map__road {
  position: absolute;
  height: 10rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 0 1rpx rgba(112, 170, 148, 0.1);
  transform-origin: left center;
}

.route-map__road--main {
  left: -30rpx;
  top: 182rpx;
  width: 760rpx;
  transform: rotate(-11deg);
}

.route-map__road--side {
  left: 180rpx;
  top: -30rpx;
  width: 430rpx;
  transform: rotate(63deg);
}

.route-segment {
  position: absolute;
  height: 10rpx;
  border-radius: 999rpx;
  background: #18b879;
  box-shadow: 0 4rpx 12rpx rgba(21, 149, 97, 0.24);
  transform-origin: left center;
  margin-top: -5rpx;
  z-index: 3;
}

.route-dot {
  position: absolute;
  width: 20rpx;
  height: 20rpx;
  border-radius: 50%;
  border: 5rpx solid #fff;
  transform: translate(-50%, -50%);
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.14);
  z-index: 4;
}

.route-dot--start {
  background: #2fc88c;
}

.route-dot--end {
  background: #ff6b57;
}

.route-map__empty {
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(244, 250, 247, 0.7);
  z-index: 5;
}

.route-map__empty-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #294156;
}

.route-map__empty-sub {
  margin-top: 10rpx;
  font-size: 23rpx;
  color: #8a9bab;
}

.stats-grid {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -9rpx 22rpx;
}

.stats-grid .stat-card {
  width: calc(50% - 18rpx);
  margin: 0 9rpx 18rpx;
  box-sizing: border-box;
}

.stat-card {
  padding: 24rpx;
  display: flex;
  flex-direction: column;
}

.stat-val {
  font-size: 34rpx;
  font-weight: 700;
  color: #192d3d;
}

.stat-label {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #8a9bab;
}

.route-list-card {
  padding: 28rpx 24rpx 8rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1a2b3c;
}

.section-more {
  font-size: 22rpx;
  color: #8a9bab;
}

.route-list {
  margin-top: 18rpx;
}

.route-item {
  display: flex;
  align-items: center;
  padding: 18rpx 0;
}

.route-item + .route-item {
  border-top: 1rpx solid #f0f3f4;
}

.route-item__info {
  flex: 1;
  min-width: 0;
}

.route-item__title {
  font-size: 28rpx;
  font-weight: 600;
  color: #23384a;
}

.route-item__arrow {
  font-size: 30rpx;
  color: #c0c8d0;
}

.route-item__meta {
  display: block;
  margin-top: 8rpx;
  font-size: 23rpx;
  color: #657786;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.route-item__sub {
  display: block;
  margin-top: 6rpx;
  font-size: 21rpx;
  color: #99a7b3;
}

.route-loading {
  padding-top: 20rpx;
}

.route-skeleton {
  height: 112rpx;
  margin-bottom: 16rpx;
  border-radius: 18rpx;
  background: linear-gradient(90deg, #f3f6f7 0%, #edf2f1 50%, #f3f6f7 100%);
}

.route-empty {
  padding: 56rpx 0;
  text-align: center;
  font-size: 24rpx;
  color: #8a9bab;
}
</style>
