<template>
  <view class="activity-detail-page">
    <view class="banner">
      <image class="banner-img" src="/static/activity-placeholder.png" mode="aspectFill"></image>
      <view class="banner-overlay">
        <text class="act-title">{{ activity.name }}</text>
        <text class="act-status">{{ activity.status }}</text>
      </view>
    </view>
    
    <view class="content-card">
      <view class="info-row">
        <text class="label">📅 时间</text>
        <text class="value">{{ activity.time }}</text>
      </view>
      <view class="info-row">
        <text class="label">📍 地点</text>
        <text class="value">{{ activity.location }}</text>
      </view>
      <view class="info-row">
        <text class="label">👥 人数</text>
        <text class="value">{{ activity.joined }} / {{ activity.limit }}</text>
      </view>
      
      <view class="divider"></view>
      
      <view class="desc-section">
        <text class="section-title">活动详情</text>
        <text class="desc-text">这是一个模拟的活动详情页面。在这里，同学们可以查看活动的具体安排、注意事项以及奖励规则。参加活动不仅能锻炼身体，还能结识更多志同道合的朋友。</text>
      </view>
    </view>
    
    <view class="bottom-bar">
      <button class="join-btn" @click="handleJoin">立即报名</button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';

const activity = ref({
  name: '加载中...',
  time: '待定',
  location: '待定',
  status: '报名中',
  joined: 0,
  limit: 100
});

onLoad((options) => {
  if (options.name) {
    activity.value.name = options.name;
    // Mock data
    activity.value.time = '2026年5月4日 07:00';
    activity.value.location = '南操场主席台前';
    activity.value.joined = 128;
    activity.value.limit = 200;
  }
});

const handleJoin = () => {
  uni.showToast({ title: '报名成功！', icon: 'success' });
};
</script>

<style scoped>
.activity-detail-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding-bottom: 120rpx;
}
.banner { position: relative; height: 400rpx; width: 100%; }
.banner-img { width: 100%; height: 100%; background-color: #ddd; }
.banner-overlay {
  position: absolute; bottom: 0; left: 0; right: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
  padding: 40rpx 30rpx 20rpx;
  display: flex; flex-direction: column;
}
.act-title { color: #fff; font-size: 40rpx; font-weight: bold; margin-bottom: 10rpx; }
.act-status { color: #20C997; font-size: 28rpx; font-weight: bold; }

.content-card {
  margin: -40rpx 30rpx 0;
  background: #fff;
  border-radius: 20rpx;
  padding: 40rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.05);
  position: relative;
  z-index: 10;
}
.info-row { display: flex; margin-bottom: 24rpx; }
.label { width: 120rpx; color: #999; font-size: 28rpx; }
.value { flex: 1; color: #333; font-size: 28rpx; font-weight: 500; }
.divider { height: 1px; background: #eee; margin: 30rpx 0; }
.section-title { font-size: 32rpx; font-weight: bold; color: #333; margin-bottom: 20rpx; display: block; }
.desc-text { font-size: 28rpx; color: #666; line-height: 1.6; }

.bottom-bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  background: #fff; padding: 20rpx 30rpx;
  box-shadow: 0 -4rpx 12rpx rgba(0,0,0,0.05);
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
}
.join-btn {
  background: linear-gradient(90deg, #20C997, #17a2b8);
  color: #fff; border-radius: 44rpx; font-weight: bold;
}
</style>