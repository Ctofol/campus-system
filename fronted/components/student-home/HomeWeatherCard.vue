<template>
  <view class="home-weather">
    <text class="home-weather__temp">{{ displayTemp }}</text>
    <view class="home-weather__divider">|</view>
    <text class="home-weather__cond">{{ displayCondition }}</text>
    <view class="home-weather__divider">|</view>
    <view class="home-weather__extra">
      <text class="home-weather__aqi">{{ displayAqi }}</text>
    </view>
    <view v-if="displayHumidity" class="home-weather__divider">|</view>
    <text v-if="displayHumidity" class="home-weather__humid">{{ displayHumidity }}</text>
  </view>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  weather: { type: Object, default: null },
  placeholder: { type: Boolean, default: true }
});

const displayTemp = computed(() => {
  if (props.weather?.temp != null && !props.placeholder) return `${props.weather.temp}°C`;
  return '--°C';
});

const displayCondition = computed(() => {
  if (props.weather?.condition && !props.placeholder) return props.weather.condition;
  return '加载中';
});

const displayAqi = computed(() => {
  if (props.weather?.aqiLabel && !props.placeholder) return props.weather.aqiLabel;
  return '---';
});

const displayHumidity = computed(() => {
  if (props.weather?.humidity != null && !props.placeholder) return String(props.weather.humidity);
  return '';
});
</script>

<style lang="scss" scoped>
.home-weather {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 18rpx 28rpx;
  border-radius: 24rpx;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(12px);
  border: 2rpx solid rgba(255, 255, 255, 0.3);
  gap: 12rpx;
}
.home-weather__temp {
  font-size: 40rpx;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}
.home-weather__divider {
  font-size: 18rpx;
  color: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}
.home-weather__cond {
  font-size: 22rpx;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  flex-shrink: 0;
}
.home-weather__extra {
  display: flex;
  align-items: center;
  gap: 4rpx;
}
.home-weather__aqi {
  font-size: 20rpx;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}
.home-weather__humid {
  font-size: 20rpx;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}
</style>