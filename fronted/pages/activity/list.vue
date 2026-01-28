<template>
  <view class="activity-list-page">
    <view class="header">
      <text class="title">跑团活动</text>
    </view>
    
    <view class="activity-list">
      <view class="activity-card" v-for="(item, index) in activities" :key="index" @click="goDetail(item)">
        <image class="act-img" :src="item.image || '/static/activity-placeholder.png'" mode="aspectFill"></image>
        <view class="act-info">
          <text class="act-name">{{ item.name }}</text>
          <view class="act-meta">
            <text class="act-time">📅 {{ item.time }}</text>
            <text class="act-location">📍 {{ item.location }}</text>
          </view>
          <view class="act-status" :class="item.statusClass">
            <text>{{ item.status }}</text>
            <text class="join-count">{{ item.joined }}人已报名</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';

const activities = ref([
  { id: 1, name: '五四青年节环校跑', time: '5月4日 07:00', location: '南操场', status: '报名中', statusClass: 'status-active', joined: 128, image: '' },
  { id: 2, name: '周末夜跑打卡赛', time: '本周六 19:00', location: '北田径场', status: '进行中', statusClass: 'status-ing', joined: 56, image: '' },
  { id: 3, name: '警务技能交流会', time: '下周三 14:00', location: '体育馆', status: '预告', statusClass: 'status-future', joined: 30, image: '' }
]);

const goDetail = (item) => {
  uni.navigateTo({
    url: `/pages/activity/detail?id=${item.id}&name=${item.name}`
  });
};
</script>

<style scoped>
.activity-list-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 30rpx;
}
.header { margin-bottom: 30rpx; }
.title { font-size: 36rpx; font-weight: bold; color: #333; border-left: 8rpx solid #20C997; padding-left: 20rpx; }

.activity-card {
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05);
}
.act-img {
  width: 100%;
  height: 300rpx;
  background-color: #eee;
}
.act-info { padding: 20rpx; }
.act-name { font-size: 32rpx; font-weight: bold; color: #333; margin-bottom: 10rpx; display: block; }
.act-meta { display: flex; flex-direction: column; gap: 6rpx; margin-bottom: 20rpx; }
.act-time, .act-location { font-size: 24rpx; color: #666; }
.act-status { display: flex; justify-content: space-between; align-items: center; }
.status-active { color: #20C997; font-weight: bold; }
.status-ing { color: #ff9f43; font-weight: bold; }
.status-future { color: #4dabf7; font-weight: bold; }
.join-count { color: #999; font-size: 24rpx; font-weight: normal; }
</style>