<template>
  <view class="container">
    <!-- Task Info -->
    <view class="info-card">
      <view class="header">
        <text class="title">{{ task.title }}</text>
        <text class="status" :class="task.status">{{ task.statusText }}</text>
      </view>
      <view class="detail-row">
        <text class="label">任务类型:</text>
        <text class="value">{{ task.type === 'run' ? '跑步' : '体测' }}</text>
      </view>
      <view class="detail-row">
        <text class="label">截止时间:</text>
        <text class="value">{{ task.deadline }}</text>
      </view>
      <view class="detail-row" v-if="task.description">
        <text class="label">任务描述:</text>
        <text class="value">{{ task.description }}</text>
      </view>
       <view class="detail-row" v-if="task.resultText">
        <text class="label">考核结果:</text>
        <text class="value highlight">{{ task.resultText }}</text>
      </view>
    </view>

    <!-- Map Trajectory -->
    <view class="map-card" v-if="hasTrajectory">
      <text class="section-title">运动轨迹</text>
      <map 
        class="map" 
        :latitude="centerLat" 
        :longitude="centerLng" 
        :polyline="polyline"
        :markers="markers"
        :enable-zoom="true"
        :enable-scroll="true"
      ></map>
    </view>
    <view class="no-data-card" v-else-if="task.status === 'completed'">
        <text class="tip">暂无轨迹数据</text>
    </view>

    <!-- Video Evidence -->
    <view class="video-card" v-if="videoUrl">
      <text class="section-title">视频记录</text>
      <video :src="videoUrl" class="video" controls></video>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onLoad } from '@dcloudio/uni-app';

const task = ref({});
const centerLat = ref(39.909);
const centerLng = ref(116.397);
const polyline = ref([]);
const markers = ref([]);
const videoUrl = ref('');

const hasTrajectory = computed(() => {
    return polyline.value.length > 0 && polyline.value[0].points.length > 0;
});

onLoad((options) => {
    if (options.data) {
        try {
            const data = JSON.parse(decodeURIComponent(options.data));
            task.value = data;
            
            // Process Trajectory
            // Assuming task.metrics.trajectory or task.trajectory exists if completed
            // If the backend returns trajectory in the task object
            let points = [];
            if (data.trajectory) {
                points = typeof data.trajectory === 'string' ? JSON.parse(data.trajectory) : data.trajectory;
            } else if (data.metrics && data.metrics.trajectory) {
                points = typeof data.metrics.trajectory === 'string' ? JSON.parse(data.metrics.trajectory) : data.metrics.trajectory;
            }
            
            if (points && points.length > 0) {
                polyline.value = [{
                    points: points,
                    color: '#20C997',
                    width: 4
                }];
                // Set center to start point
                centerLat.value = points[0].latitude;
                centerLng.value = points[0].longitude;
                // Add start/end markers
                markers.value = [
                    {
                        id: 0,
                        latitude: points[0].latitude,
                        longitude: points[0].longitude,
                        title: '起点',
                        iconPath: '/static/location.png',
                        width: 20,
                        height: 20
                    },
                    {
                        id: 1,
                        latitude: points[points.length-1].latitude,
                        longitude: points[points.length-1].longitude,
                        title: '终点',
                        iconPath: '/static/location.png',
                        width: 20,
                        height: 20
                    }
                ];
            }
            
            // Process Video
            if (data.evidence) {
                // Evidence is usually an array of { type: 'video', url: '...' }
                // or just a string url if simplified
                if (Array.isArray(data.evidence)) {
                    const vid = data.evidence.find(e => e.type === 'video' || e.url.endsWith('.mp4'));
                    if (vid) videoUrl.value = vid.url;
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
.map {
    width: 100%;
    height: 400rpx;
    border-radius: 12rpx;
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
