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
import { ref, onMounted } from 'vue';
import { getRunGroupActivities } from '@/utils/request.js';

const activities = ref([]);
const loading = ref(false);

const loadActivities = async () => {
  if (loading.value) return;
  
  loading.value = true;
  
  try {
    const res = await getRunGroupActivities({
      page: 1,
      size: 50
    });
    
    // 转换数据格式以适配模板
    activities.value = res.items.map(item => ({
      id: item.id,
      name: item.title,
      time: formatTime(item.activity_time),
      location: item.location || '待定',
      status: getStatusText(item.status),
      statusClass: getStatusClass(item.status),
      joined: item.apply_count,
      image: item.cover_image || '/static/activity-placeholder.png'
    }));
  } catch (e) {
    console.error('加载活动失败:', e);
    uni.showToast({ title: '加载失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
};

const formatTime = (timeStr) => {
  const date = new Date(timeStr);
  return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
};

const getStatusText = (status) => {
  const statusMap = {
    'upcoming': '报名中',
    'ongoing': '进行中',
    'finished': '已结束'
  };
  return statusMap[status] || '报名中';
};

const getStatusClass = (status) => {
  const classMap = {
    'upcoming': 'status-active',
    'ongoing': 'status-ing',
    'finished': 'status-future'
  };
  return classMap[status] || 'status-active';
};

const goDetail = (item) => {
  uni.navigateTo({
    url: `/pages/run-group/activity-detail?activityId=${item.id}`
  });
};

onMounted(() => {
  loadActivities();
});
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