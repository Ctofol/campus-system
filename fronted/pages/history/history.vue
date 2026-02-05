<template>
  <view class="container">
    <view class="custom-navbar" :style="{paddingTop: statusBarHeight + 'px'}">
      <view class="navbar-content">
        <view class="back-btn" @click="goBack">
          <text class="back-arrow">←</text>
        </view>
        <text class="navbar-title">全部运动记录</text>
      </view>
    </view>
    
    <view class="content-wrapper" :style="{paddingTop: (statusBarHeight + 44) + 'px'}">
        <scroll-view scroll-y class="record-list" @scrolltolower="loadMore">
        <view class="record-item" v-for="(item, index) in filteredRecords" :key="index">
            <view class="record-type" :style="{backgroundColor: item.modeBg}">
            <text class="type-text">{{item.modeText}}</text>
            </view>
            <view class="record-info">
            <text class="record-date">{{item.createTime}}</text>
            <text class="record-data" v-if="item.type === 'run'">
                {{item.distance}}km | {{item.duration}}<text v-if="item.pace"> | {{Number(item.pace).toFixed(1)}}'</text>
            </text>
            </view>
            <view class="record-status">
            <text class="status-text" :style="{color: item.statusColor}">{{item.statusText}}</text>
            </view>
        </view>
        <view class="loading-more" v-if="loading">加载中...</view>
        <view class="no-more" v-if="!loading && filteredRecords.length === 0">暂无自主运动记录</view>
        </scroll-view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { request } from '@/utils/request.js';

const statusBarHeight = ref(20);
const records = ref([]);
const page = ref(1);
const size = ref(20);
const loading = ref(false);
const hasMore = ref(true);

// Computed to strictly filter out tasks
const filteredRecords = computed(() => {
    return records.value.filter(item => !item.isTask);
});

onShow(() => {
    statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 20;
    page.value = 1;
    records.value = [];
    hasMore.value = true;
    loadHistory();
});

const goBack = () => {
    uni.navigateBack();
};

const loadHistory = async () => {
    if (loading.value || !hasMore.value) return;
    loading.value = true;
    
    try {
        const res = await request({
            url: '/activity/history',
            method: 'GET',
            data: { page: page.value, size: size.value }
        });
        
        if (res.items && res.items.length > 0) {
            const newRecords = res.items.map(item => {
                const isRun = item.type === 'run';
                const date = new Date(item.started_at);
                const dateStr = `${date.getMonth()+1}-${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
                
                return {
                    type: item.type,
                    modeBg: isRun ? '#20C997' : '#FF9F43',
                    modeText: isRun ? '跑步' : '体测',
                    createTime: dateStr,
                    distance: item.metrics?.distance ? Number(item.metrics.distance).toFixed(2) : 0,
                    duration: formatDuration(item.metrics?.duration || 0),
                    pace: item.metrics?.pace,
                    result: item.metrics?.qualified ? '达标' : '未达标',
                    statusText: item.status === 'finished' ? '有效' : '待审核',
                    statusColor: '#20C997',
                    // Flag for task identification
                    isTask: !!(item.task_id || item.plan_id)
                };
            });
            
            records.value = [...records.value, ...newRecords];
            
            if (res.items.length < size.value) {
                hasMore.value = false;
            }
        } else {
            hasMore.value = false;
        }
    } catch (e) {
        console.error('Fetch history failed', e);
    } finally {
        loading.value = false;
    }
};

const loadMore = () => {
    page.value++;
    loadHistory();
};

const formatDuration = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h > 0 ? h + ':' : ''}${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
};
</script>

<style scoped>
.container {
  min-height: 100vh;
  background-color: #f5f7fa;
}
.custom-navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: #fff;
  z-index: 999;
  border-bottom: 1rpx solid #eee;
}
.navbar-content {
  height: 44px;
  display: flex;
  align-items: center;
  padding: 0 15px;
}
.back-btn {
  padding: 10px;
  margin-left: -10px;
}
.back-arrow {
  font-size: 20px;
  color: #333;
}
.navbar-title {
  font-size: 17px;
  font-weight: bold;
  color: #333;
  flex: 1;
  text-align: center;
  margin-right: 30px;
}
.content-wrapper {
    height: 100vh;
    box-sizing: border-box;
}
.record-list {
    height: 100%;
    padding: 20rpx;
    box-sizing: border-box;
}
.record-item {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}
.record-type {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}
.type-text {
  color: #fff;
  font-size: 24rpx;
  font-weight: bold;
}
.record-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.record-date {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 8rpx;
}
.record-data {
  font-size: 28rpx;
  color: #333;
  font-weight: bold;
}
.record-status {
  margin-left: 20rpx;
}
.status-text {
  font-size: 24rpx;
}
.loading-more, .no-more {
    text-align: center;
    padding: 20rpx;
    color: #999;
    font-size: 24rpx;
}
</style>
