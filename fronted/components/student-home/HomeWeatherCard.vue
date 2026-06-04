<template>
  <view class="home-weather">
    <text class="home-weather__icon">{{ weatherIcon }}</text>
    <view class="home-weather__body">
      <text class="home-weather__temp">{{ displayTemp }}</text>
      <text class="home-weather__cond">{{ displayCondition }}</text>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  weather: {
    type: Object,
    default: null
  },
  placeholder: {
    type: Boolean,
    default: true
  }
});

const weatherIcon = computed(() => {
  const c = props.weather?.condition || '';
  if (c.includes('雨')) return '🌧️';
  if (c.includes('雪')) return '❄️';
  if (c.includes('阴')) return '☁️';
  if (c.includes('晴')) return '☀️';
  return '⛅';
});

const displayTemp = computed(() => {
  if (props.weather?.temp != null && !props.placeholder) {
    return `${props.weather.temp}°C`;
  }
  return '--°C';
});

const displayCondition = computed(() => {
  if (props.weather?.condition && !props.placeholder) {
    const parts = [props.weather.condition];
    if (props.weather.aqiLabel) parts.push(props.weather.aqiLabel);
    if (props.weather.humidity != null) parts.push(String(props.weather.humidity));
    return parts.join(' | ');
  }
  return '天气加载中';
});
</script>

<style lang="scss" scoped>
.home-weather {
  flex: 0 0 auto;
  min-width: 0;
  max-width: 340rpx;
  padding: 16rpx 20rpx;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(12px);
  display: flex;
  flex-direction: row;
  align-items: center;
}
.home-weather__icon {
  font-size: 48rpx;
  margin-right: 12rpx;
  flex-shrink: 0;
}
.home-weather__body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.home-weather__temp {
  font-size: 36rpx;
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
}
.home-weather__cond {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.92);
  margin-top: 4rpx;
}
</style>
