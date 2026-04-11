<template>
  <view class="rank-page">
    <view class="header">
      <text class="title">跑团排行榜</text>
      <text class="subtitle">按总里程排名</text>
    </view>
    
    <view class="rank-list">
      <view 
        class="rank-item" 
        v-for="(group, index) in rankList" 
        :key="group.group_id"
        :class="{'top-three': index < 3}"
      >
        <view class="rank-number" :class="'rank-' + (index + 1)">
          <text v-if="index < 3">{{ ['🥇', '🥈', '🥉'][index] }}</text>
          <text v-else>{{ index + 1 }}</text>
        </view>
        <view class="group-info">
          <text class="group-name">{{ group.group_name }}</text>
          <text class="member-count">{{ group.member_count }}人</text>
        </view>
        <text class="mileage">{{ (group.total_mileage || 0).toFixed(1) }}km</text>
      </view>
      
      <view class="loading" v-if="loading">
        <text>加载中...</text>
      </view>
      
      <view class="empty" v-if="!loading && rankList.length === 0">
        <text>暂无数据</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getRunGroupRank } from '@/utils/request.js';

const rankList = ref([]);
const loading = ref(false);

const loadRank = async () => {
  loading.value = true;
  try {
    const res = await getRunGroupRank();
    rankList.value = res;
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadRank();
});
</script>

<style scoped>
.rank-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #20C997 0%, #f5f7fa 300rpx);
}

.header {
  padding: 60rpx 30rpx 40rpx;
  text-align: center;
}

.title {
  font-size: 40rpx;
  font-weight: bold;
  color: #fff;
  display: block;
  margin-bottom: 12rpx;
}

.subtitle {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
}

.rank-list {
  padding: 0 30rpx 30rpx;
}

.rank-item {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 16rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.rank-item.top-three {
  box-shadow: 0 4rpx 20rpx rgba(32, 201, 151, 0.2);
}

.rank-number {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: bold;
  margin-right: 20rpx;
  background: #f0f0f0;
  color: #666;
}

.rank-1 {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: #fff;
  font-size: 40rpx;
}

.rank-2 {
  background: linear-gradient(135deg, #C0C0C0, #808080);
  color: #fff;
  font-size: 40rpx;
}

.rank-3 {
  background: linear-gradient(135deg, #CD7F32, #8B4513);
  color: #fff;
  font-size: 40rpx;
}

.group-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.group-name {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 8rpx;
}

.member-count {
  font-size: 22rpx;
  color: #999;
}

.mileage {
  font-size: 32rpx;
  font-weight: bold;
  color: #20C997;
}

.loading, .empty {
  text-align: center;
  padding: 80rpx;
  color: #999;
  font-size: 24rpx;
}
</style>
