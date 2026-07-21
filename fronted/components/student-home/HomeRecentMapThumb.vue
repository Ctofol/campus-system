<template>
  <view class="thumb-wrap" :class="{ 'thumb-wrap--empty': !showTrack }">
    <view class="thumb-map">
      <view class="thumb-map__block thumb-map__block--one" />
      <view class="thumb-map__block thumb-map__block--two" />
      <view class="thumb-map__block thumb-map__block--three" />
      <view class="thumb-map__road thumb-map__road--main" />
      <view class="thumb-map__road thumb-map__road--side" />

      <template v-if="showTrack">
        <view
          v-for="(segment, index) in routeSegments"
          :key="index"
          class="thumb-route-segment"
          :style="segment.style"
        />
        <view class="thumb-route-dot thumb-route-dot--start" :style="startDotStyle" />
        <view class="thumb-route-dot thumb-route-dot--end" :style="endDotStyle" />
      </template>

      <view v-else class="thumb-placeholder">
        <text class="thumb-placeholder__line" />
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  preview: { type: Array, default: () => [] },
  hasTrack: { type: Boolean, default: false }
});

const points = computed(() =>
  (props.preview || [])
    .map((p) => ({
      lat: Number(p.lat),
      lng: Number(p.lng)
    }))
    .filter((p) => Number.isFinite(p.lat) && Number.isFinite(p.lng))
);

const showTrack = computed(() => props.hasTrack && points.value.length >= 2);

const normalizedPoints = computed(() => {
  const pts = points.value;
  if (pts.length < 2) return [];

  const minLat = Math.min(...pts.map((p) => p.lat));
  const maxLat = Math.max(...pts.map((p) => p.lat));
  const minLng = Math.min(...pts.map((p) => p.lng));
  const maxLng = Math.max(...pts.map((p) => p.lng));
  const latRange = Math.max(maxLat - minLat, 0.00001);
  const lngRange = Math.max(maxLng - minLng, 0.00001);
  const padding = 14;
  const drawable = 100 - padding * 2;

  return pts.map((p) => ({
    x: padding + ((p.lng - minLng) / lngRange) * drawable,
    y: padding + (1 - (p.lat - minLat) / latRange) * drawable
  }));
});

const routeSegments = computed(() => {
  const pts = normalizedPoints.value;
  const heightRatio = 96 / 128;
  return pts.slice(1).map((point, index) => {
    const prev = pts[index];
    const dx = point.x - prev.x;
    const dy = (point.y - prev.y) * heightRatio;
    const length = Math.sqrt(dx * dx + dy * dy);
    const angle = Math.atan2(dy, dx) * (180 / Math.PI);

    return {
      style: `left:${prev.x}%;top:${prev.y}%;width:${length}%;transform:rotate(${angle}deg);`
    };
  });
});

const dotStyle = (point) => {
  if (!point) return 'left:50%;top:50%;';
  return `left:${point.x}%;top:${point.y}%;`;
};

const startDotStyle = computed(() => dotStyle(normalizedPoints.value[0]));
const endDotStyle = computed(() => dotStyle(normalizedPoints.value[normalizedPoints.value.length - 1]));
</script>

<style lang="scss" scoped>
.thumb-wrap {
  width: 128rpx;
  height: 96rpx;
  border-radius: 14rpx;
  overflow: hidden;
  flex-shrink: 0;
  margin-right: 20rpx;
  background: #eef8f4;
  border: 1rpx solid rgba(63, 151, 123, 0.16);
}

.thumb-wrap--empty {
  opacity: 0.86;
}

.thumb-map {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  background:
    linear-gradient(90deg, rgba(125, 180, 159, 0.14) 1rpx, transparent 1rpx),
    linear-gradient(0deg, rgba(125, 180, 159, 0.12) 1rpx, transparent 1rpx),
    linear-gradient(145deg, #f5fbf8 0%, #dff3ea 100%);
  background-size: 32rpx 32rpx, 32rpx 32rpx, 100% 100%;
}

.thumb-map__block {
  position: absolute;
  border-radius: 8rpx;
  background: rgba(149, 202, 181, 0.2);
}

.thumb-map__block--one {
  left: 10rpx;
  top: 10rpx;
  width: 36rpx;
  height: 22rpx;
}

.thumb-map__block--two {
  right: 12rpx;
  top: 14rpx;
  width: 42rpx;
  height: 26rpx;
}

.thumb-map__block--three {
  left: 54rpx;
  bottom: 10rpx;
  width: 50rpx;
  height: 18rpx;
}

.thumb-map__road {
  position: absolute;
  height: 5rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 0 1rpx rgba(112, 170, 148, 0.08);
  transform-origin: left center;
}

.thumb-map__road--main {
  left: -8rpx;
  top: 54rpx;
  width: 160rpx;
  transform: rotate(-14deg);
}

.thumb-map__road--side {
  left: 40rpx;
  top: -8rpx;
  width: 118rpx;
  transform: rotate(67deg);
}

.thumb-route-segment {
  position: absolute;
  height: 6rpx;
  border-radius: 999rpx;
  background: #1fc083;
  box-shadow: 0 2rpx 6rpx rgba(21, 149, 97, 0.24);
  transform-origin: left center;
  margin-top: -3rpx;
  z-index: 3;
}

.thumb-route-dot {
  position: absolute;
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  border: 3rpx solid #ffffff;
  transform: translate(-50%, -50%);
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.12);
  z-index: 4;
}

.thumb-route-dot--start {
  background: #2fc88c;
}

.thumb-route-dot--end {
  background: #ff6b57;
}

.thumb-placeholder {
  width: 100%;
  height: 100%;
  position: absolute;
  left: 0;
  top: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(227, 245, 237, 0.58);
  z-index: 5;
}

.thumb-placeholder__line {
  width: 70%;
  height: 6rpx;
  background: rgba(110, 171, 146, 0.55);
  border-radius: 4rpx;
  transform: rotate(-8deg);
}
</style>
