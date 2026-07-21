<template>
  <view class="home-weather">
    <image class="home-weather__icon" :src="weatherIconSrc" mode="aspectFit" />
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

const weatherIconSrc = computed(() => {
  if (props.placeholder) return '/static/home/weather-default.svg';
  const icon = String(props.weather?.icon || '').toLowerCase();
  const condition = String(props.weather?.condition || '');
  if (icon.includes('rain') || /雨/.test(condition)) return '/static/home/weather-rainy.svg';
  if (icon.includes('sun') || icon.includes('clear') || /晴/.test(condition)) return '/static/home/weather-sunny.svg';
  if (icon.includes('cloud') || /云|阴/.test(condition)) return '/static/home/weather-cloudy.svg';
  return '/static/home/weather-default.svg';
});
</script>

<style lang="scss" scoped>
.home-weather {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 16rpx 22rpx 16rpx 18rpx;
  border-radius: 22rpx;
  background: rgba(255, 255, 255, 0.16);
  border: 1rpx solid rgba(255, 255, 255, 0.24);
  gap: 8rpx;
}
.home-weather__icon {
  width: 44rpx;
  height: 44rpx;
  flex-shrink: 0;
}
.home-weather__temp {
  font-size: 34rpx;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}
.home-weather__divider {
  font-size: 18rpx;
  color: rgba(255, 255, 255, 0.34);
  flex-shrink: 0;
}
.home-weather__cond {
  font-size: 21rpx;
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
  font-size: 19rpx;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}
.home-weather__humid {
  font-size: 19rpx;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}
</style>
