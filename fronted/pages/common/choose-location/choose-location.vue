<template>
  <view class="choose-location-container">
    <!-- Map Component -->
    <map 
      id="choose-map"
      class="map"
      :latitude="latitude"
      :longitude="longitude"
      :show-location="true"
      :enable-zoom="true"
      :enable-scroll="true"
      @regionchange="onRegionChange"
    >
      <!-- Center Pin (simulated with cover-view centered) -->
      <cover-view class="center-pin">
        <cover-image src="/static/location.png" class="pin-icon"></cover-image>
      </cover-view>
      
      <!-- Back Button -->
      <cover-view class="back-btn" @click="goBack" :style="{ top: backButtonTop }">
        <text class="back-text">返回</text>
      </cover-view>
    </map>

    <!-- Bottom Panel -->
    <view class="bottom-panel">
      <view class="location-info">
        <text class="info-title">已选位置</text>
        <text class="info-coords">经度: {{ currentCenter.lng.toFixed(6) }}</text>
        <text class="info-coords">纬度: {{ currentCenter.lat.toFixed(6) }}</text>
      </view>
      <button class="confirm-btn" @click="confirmSelection">确认选择</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getCurrentLocation } from '@/utils/location.js';

const latitude = ref(39.909);
const longitude = ref(116.397);
const currentCenter = ref({ lat: 39.909, lng: 116.397 });
const backButtonTop = ref('40px'); // Default safe top
let mapContext = null;

onMounted(() => {
  // Adjust back button position based on status bar height
  try {
    const sysInfo = uni.getSystemInfoSync();
    if (sysInfo.statusBarHeight) {
      // Status bar height + 10px padding
      backButtonTop.value = (sysInfo.statusBarHeight + 10) + 'px';
    }
  } catch (e) {
    console.error('Get system info failed', e);
  }

  mapContext = uni.createMapContext('choose-map');
  
  // Get initial location
  getCurrentLocation().then(res => {
    if (res.success) {
      latitude.value = res.latitude;
      longitude.value = res.longitude;
      currentCenter.value = { lat: res.latitude, lng: res.longitude };
    }
  }).catch(err => {
    console.error('Init location failed', err);
    uni.showToast({ title: '定位失败，请手动移动地图', icon: 'none' });
  });
});

const onRegionChange = (e) => {
  if (e.type === 'end' || (e.detail && (e.detail.type === 'end' || e.detail.type === 'regionchange'))) {
    mapContext.getCenterLocation({
      success: (res) => {
        currentCenter.value = { lat: res.latitude, lng: res.longitude };
      },
      fail: (err) => {
        console.error('Get center failed', err);
      }
    });
  }
};

const goBack = () => {
  uni.navigateBack();
};

const confirmSelection = () => {
  // Fire event to previous page
  const eventChannel = uni.getFileSystemManager ? null : getCurrentPages()[getCurrentPages().length - 1].getOpenerEventChannel(); 
  
  // Vue3 uni-app uses uni.$emit for global or event channel
  uni.$emit('onLocationChosen', {
    latitude: currentCenter.value.lat,
    longitude: currentCenter.value.lng,
    name: '自选打卡点',
    address: `经纬度: ${currentCenter.value.lng.toFixed(4)}, ${currentCenter.value.lat.toFixed(4)}`
  });
  
  uni.navigateBack();
};
</script>

<style scoped>
.choose-location-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.map {
  flex: 1;
  width: 100%;
  position: relative;
}

.center-pin {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -100%); /* Pin tip at center */
  pointer-events: none;
  display: flex;
  justify-content: center;
  align-items: center;
}

.pin-icon {
  width: 60rpx;
  height: 60rpx;
}

.back-btn {
  position: absolute;
  /* top is set dynamically via inline style */
  left: 30rpx;
  background-color: rgba(255, 255, 255, 0.95);
  padding: 16rpx 30rpx; /* Increased padding for easier clicking */
  border-radius: 8rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.15);
  z-index: 999; /* Ensure it's on top */
}

.back-text {
  font-size: 28rpx;
  color: #333;
}

.bottom-panel {
  height: 200rpx;
  background-color: #fff;
  padding: 30rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 -4rpx 20rpx rgba(0,0,0,0.05);
}

.location-info {
  display: flex;
  flex-direction: column;
}

.info-title {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
}

.info-coords {
  font-size: 24rpx;
  color: #666;
}

.confirm-btn {
  background-color: #20C997;
  color: #fff;
  font-size: 32rpx;
  border-radius: 40rpx;
  margin-top: 20rpx;
}
</style>