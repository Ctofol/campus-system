<template>
  <view class="container">
    <view class="info-card">
      <view class="header">
        <text class="title">任务跑步详情</text>
        <text class="status" :class="activity.is_valid ? 'ok' : 'bad'">
          {{ activity.is_valid ? '任务达标' : '未达标' }}
        </text>
      </view>
      <text class="task-name">{{ activity.task_title }}</text>
      <view class="detail-row">
        <text class="label">学员</text>
        <text class="value">{{ student.name }} {{ student.student_no ? `（${student.student_no}）` : '' }}</text>
      </view>
      <view class="detail-row">
        <text class="label">时间</text>
        <text class="value">{{ displayTime }}</text>
      </view>
      <view class="detail-row" v-if="metrics">
        <text class="label">距离</text>
        <text class="value">{{ distanceKm }} km</text>
      </view>
      <view class="detail-row" v-if="paceText">
        <text class="label">配速</text>
        <text class="value">{{ paceText }} 分/公里</text>
      </view>
      <view class="detail-row" v-if="metrics && metrics.duration != null">
        <text class="label">时长</text>
        <text class="value">{{ Math.floor(metrics.duration / 60) }} 分 {{ metrics.duration % 60 }} 秒</text>
      </view>
      <view class="detail-row" v-if="activity.fail_reason">
        <text class="label">说明</text>
        <text class="value fail-text">{{ activity.fail_reason }}</text>
      </view>
    </view>

    <view class="photo-card">
      <text class="section-title">人脸对比</text>
      <view class="photo-grid">
        <view class="photo-item">
          <text class="photo-label">跑前</text>
          <image v-if="startPhotoUrl" class="photo-img" :src="startPhotoUrl" mode="aspectFill" />
          <view v-else class="photo-placeholder">暂无照片</view>
        </view>
        <view class="photo-item">
          <text class="photo-label">跑后</text>
          <image v-if="endPhotoUrl" class="photo-img" :src="endPhotoUrl" mode="aspectFill" />
          <view v-else class="photo-placeholder">暂无照片</view>
        </view>
      </view>
    </view>

    <view class="map-card" v-if="showMap">
      <text class="section-title">运动轨迹</text>
      <map
        class="map"
        :latitude="centerLat"
        :longitude="centerLng"
        :polyline="polyline"
        :markers="markers"
        :enable-zoom="true"
        :enable-scroll="true"
      />
    </view>
    <view class="no-data-card" v-else>
      <text class="tip">暂无轨迹数据</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { getTeacherTaskRunDetail, resolveMediaUrl } from '@/utils/request.js';

const activity = ref({});
const student = ref({});
const metrics = ref(null);
const displayTime = ref('');
const distanceKm = ref('0.00');
const paceText = ref('');
const centerLat = ref(39.909);
const centerLng = ref(116.397);
const polyline = ref([]);
const markers = ref([]);
const showMap = ref(false);
const startPhotoUrl = ref('');
const endPhotoUrl = ref('');

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
      out.push({ latitude: lat, longitude: lng });
    }
  }
  return out;
}

onLoad(async (options) => {
  const aid = options.activityId ? parseInt(options.activityId, 10) : 0;
  if (!aid) return;
  try {
    const res = await getTeacherTaskRunDetail(aid);
    activity.value = res.activity || {};
    student.value = res.student || {};
    metrics.value = res.metrics || null;
    startPhotoUrl.value = activity.value.start_photo_url ? resolveMediaUrl(activity.value.start_photo_url) : '';
    endPhotoUrl.value = activity.value.end_photo_url ? resolveMediaUrl(activity.value.end_photo_url) : '';

    if (activity.value.started_at) {
      const d = new Date(activity.value.started_at);
      displayTime.value = `${d.getMonth() + 1}-${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
    }
    if (metrics.value) {
      if (metrics.value.distance != null) {
        distanceKm.value = Number(metrics.value.distance).toFixed(2);
      }
      if (metrics.value.pace != null) {
        paceText.value = Number(metrics.value.pace).toFixed(1);
      }
    }

    let points = [];
    if (metrics.value && metrics.value.trajectory) {
      points = normalizeTrajectoryPoints(metrics.value.trajectory);
    }
    polyline.value = [];
    markers.value = [];
    showMap.value = false;
    if (points.length >= 2) {
      polyline.value = [{ points, color: '#20C997', width: 4 }];
      centerLat.value = points[0].latitude;
      centerLng.value = points[0].longitude;
      markers.value = [
        {
          id: 0,
          latitude: points[0].latitude,
          longitude: points[0].longitude,
          title: '起点',
          iconPath: '/static/location.png',
          width: 20,
          height: 20,
        },
        {
          id: 1,
          latitude: points[points.length - 1].latitude,
          longitude: points[points.length - 1].longitude,
          title: '终点',
          iconPath: '/static/location.png',
          width: 20,
          height: 20,
        },
      ];
      showMap.value = true;
    } else if (points.length === 1) {
      centerLat.value = points[0].latitude;
      centerLng.value = points[0].longitude;
      markers.value = [
        {
          id: 0,
          latitude: points[0].latitude,
          longitude: points[0].longitude,
          title: '位置',
          iconPath: '/static/location.png',
          width: 20,
          height: 20,
        },
      ];
      showMap.value = true;
    }

  } catch (e) {
    console.error(e);
    uni.showToast({ title: '加载失败', icon: 'none' });
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
    align-items: center;
    margin-bottom: 16rpx;
    .title {
      font-size: 34rpx;
      font-weight: bold;
    }
    .status {
      font-size: 26rpx;
    }
    .status.ok {
      color: #20c997;
    }
    .status.bad {
      color: #ff4d4f;
    }
  }
  .task-name {
    font-size: 28rpx;
    color: #666;
    margin-bottom: 20rpx;
    display: block;
  }
  .detail-row {
    display: flex;
    margin-bottom: 12rpx;
    font-size: 28rpx;
    .label {
      color: #888;
      width: 140rpx;
    }
    .value {
      flex: 1;
      color: #333;
    }
    .fail-text {
      color: #ff4d4f;
    }
  }
}
.map-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  .section-title {
    font-size: 30rpx;
    font-weight: bold;
    margin-bottom: 16rpx;
    display: block;
  }
}
.photo-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}
.photo-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}
.photo-item {
  display: flex;
  flex-direction: column;
}
.photo-label {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 12rpx;
}
.photo-img,
.photo-placeholder {
  width: 100%;
  height: 220rpx;
  border-radius: 12rpx;
  background: #f3f4f6;
}
.photo-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 24rpx;
}
.map {
  width: 100%;
  height: 420rpx;
  border-radius: 12rpx;
}
.no-data-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 40rpx;
  text-align: center;
  color: #999;
}
</style>
