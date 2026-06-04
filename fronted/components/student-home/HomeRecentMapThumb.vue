<template>
  <view class="thumb-wrap">
    <map
      v-if="showMap"
      class="thumb-map"
      :latitude="center.lat"
      :longitude="center.lng"
      :scale="scale"
      :polyline="polyline"
      :include-points="includePoints"
      :enable-scroll="false"
      :enable-zoom="false"
      :show-location="false"
      :show-compass="false"
    />
    <view v-else class="thumb-placeholder">
      <text class="thumb-placeholder__line" />
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
      latitude: Number(p.lat),
      longitude: Number(p.lng)
    }))
    .filter((p) => Number.isFinite(p.latitude) && Number.isFinite(p.longitude))
);

const showMap = computed(() => props.hasTrack && points.value.length >= 2);

const center = computed(() => {
  const pts = points.value;
  if (!pts.length) return { lat: 23.13, lng: 113.26 };
  const lat = pts.reduce((s, p) => s + p.latitude, 0) / pts.length;
  const lng = pts.reduce((s, p) => s + p.longitude, 0) / pts.length;
  return { lat, lng };
});

const includePoints = computed(() => points.value);

const scale = computed(() => (points.value.length > 20 ? 13 : 14));

const polyline = computed(() => {
  if (!showMap.value) return [];
  return [
    {
      points: points.value,
      color: '#26B586',
      width: 4,
      arrowLine: false
    }
  ];
});
</script>

<style lang="scss" scoped>
.thumb-wrap {
  width: 128rpx;
  height: 96rpx;
  border-radius: 14rpx;
  overflow: hidden;
  flex-shrink: 0;
  margin-right: 20rpx;
  background: #e8f8f2;
}
.thumb-map {
  width: 100%;
  height: 100%;
}
.thumb-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(145deg, #e0f5ec 0%, #b8e6d0 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.thumb-placeholder__line {
  width: 70%;
  height: 6rpx;
  background: #9ed4bc;
  border-radius: 4rpx;
  transform: rotate(-8deg);
}
</style>
