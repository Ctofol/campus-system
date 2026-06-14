<template>
  <view class="rank-page">
    <page-tab-header title="跑团排行榜" show-back theme="brand" />

    <view class="rank-hero page-tab-body">
      <text class="rank-subtitle">按总里程排名</text>
    </view>

    <view class="rank-list">
      <view
        class="rank-item"
        v-for="(group, index) in rankList"
        :key="group.group_id"
        :class="{ 'top-three': index < 3 }"
      >
        <view class="rank-number" :class="'rank-' + (index + 1)">
          <image v-if="index < 3" class="rank-medal-img" src="/static/奖杯图标.png" mode="aspectFit" />
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
  background: #f5f7fa;
}

.rank-hero {
  padding-top: 16rpx;
  padding-bottom: 8rpx;
  text-align: center;
}

.rank-subtitle {
  font-size: 26rpx;
  color: #6b7c8f;
}

.rank-list {
  padding: 0 30rpx 40rpx;
}

.rank-item {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.rank-item.top-three {
  border: 2rpx solid rgba(32, 201, 151, 0.35);
}

.rank-medal-img { width: 32rpx; height: 32rpx; }

.rank-number {
  width: 72rpx;
  text-align: center;
  font-size: 36rpx;
  flex-shrink: 0;
}

.group-info {
  flex: 1;
  min-width: 0;
  margin-left: 16rpx;
}

.group-name {
  display: block;
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
}

.member-count {
  display: block;
  font-size: 24rpx;
  color: #999;
  margin-top: 6rpx;
}

.mileage {
  font-size: 32rpx;
  font-weight: bold;
  color: #20c997;
  flex-shrink: 0;
}

.loading,
.empty {
  text-align: center;
  padding: 60rpx 0;
  color: #999;
  font-size: 28rpx;
}
</style>
