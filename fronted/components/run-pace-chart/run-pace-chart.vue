<template>
  <view v-if="normalizedSeries.length >= 3" class="pace-chart">
    <view class="pace-chart__head">
      <text class="pace-chart__title">配速变化</text>
      <text class="pace-chart__unit">分/公里</text>
    </view>
    <canvas :canvas-id="canvasId" :id="canvasId" class="pace-chart__canvas" />
  </view>
</template>

<script setup>
import { computed, getCurrentInstance, nextTick, onMounted, watch } from 'vue';

const props = defineProps({
  series: { type: Array, default: () => [] }
});

const instance = getCurrentInstance();
const canvasId = `run-pace-${instance?.uid || Date.now()}`;
const normalizedSeries = computed(() => (props.series || [])
  .map((item) => Number(item?.pace ?? item))
  .filter((pace) => Number.isFinite(pace) && pace > 0));

const draw = () => {
  const values = normalizedSeries.value;
  if (values.length < 2) return;
  const width = 640;
  const height = 220;
  const pad = { left: 24, right: 18, top: 20, bottom: 26 };
  const min = Math.min(...values);
  const max = Math.max(...values);
  const spread = Math.max(1, max - min);
  const ctx = uni.createCanvasContext(canvasId, instance?.proxy);
  ctx.setFillStyle('#F5FAF9');
  ctx.fillRect(0, 0, width, height);
  ctx.setStrokeStyle('#DDEAE6');
  ctx.setLineWidth(1);
  for (let row = 0; row < 3; row += 1) {
    const y = pad.top + ((height - pad.top - pad.bottom) * row) / 2;
    ctx.beginPath();
    ctx.moveTo(pad.left, y);
    ctx.lineTo(width - pad.right, y);
    ctx.stroke();
  }
  ctx.setStrokeStyle('#20C997');
  ctx.setLineWidth(4);
  ctx.setLineJoin('round');
  ctx.setLineCap('round');
  values.forEach((pace, index) => {
    const x = pad.left + ((width - pad.left - pad.right) * index) / (values.length - 1);
    // Faster pace (smaller value) appears higher in the chart.
    const y = pad.top + ((pace - min) / spread) * (height - pad.top - pad.bottom);
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
  ctx.draw();
};

const scheduleDraw = () => nextTick(() => setTimeout(draw, 40));
onMounted(scheduleDraw);
watch(normalizedSeries, scheduleDraw, { deep: true });
</script>

<style scoped>
.pace-chart { margin-top: 22rpx; }
.pace-chart__head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 12rpx; }
.pace-chart__title { color: #18232E; font-size: 28rpx; font-weight: 700; }
.pace-chart__unit { color: #8E8E93; font-size: 22rpx; }
.pace-chart__canvas { width: 100%; height: 220rpx; background: #F5FAF9; border-radius: 8rpx; }
</style>
