<template>
  <view class="activity-list-page">
    <view class="filter-bar">
      <view 
        class="filter-item" 
        :class="{active: currentStatus === ''}"
        @click="changeStatus('')"
      >
        <text>全部</text>
      </view>
      <view 
        class="filter-item" 
        :class="{active: currentStatus === 'upcoming'}"
        @click="changeStatus('upcoming')"
      >
        <text>报名中</text>
      </view>
      <view 
        class="filter-item" 
        :class="{active: currentStatus === 'ongoing'}"
        @click="changeStatus('ongoing')"
      >
        <text>进行中</text>
      </view>
      <view 
        class="filter-item" 
        :class="{active: currentStatus === 'finished'}"
        @click="changeStatus('finished')"
      >
        <text>已结束</text>
      </view>
    </view>
    
    <scroll-view 
      scroll-y 
      class="activity-scroll"
      @scrolltolower="loadMore"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
      <view 
        class="activity-card" 
        v-for="activity in activities" 
        :key="activity.id"
        @click="goToDetail(activity.id)"
      >
        <view class="status-badge" :class="'status-' + activity.status">
          <text>{{ getStatusText(activity.status) }}</text>
        </view>
        <text class="title">{{ activity.title }}</text>
        <view class="info-row">
          <image class="info-icon-img" src="/static/日历.png" mode="aspectFit" />
          <text class="text">{{ formatTime(activity.activity_time) }}</text>
        </view>
        <view class="info-row" v-if="activity.location">
          <image class="info-icon-img" src="/static/location.png" mode="aspectFit" />
          <text class="text">{{ activity.location }}</text>
        </view>
        <view class="info-row" v-if="activity.distance">
          <image class="info-icon-img" src="/static/主页户外跑图标.png" mode="aspectFit" />
          <text class="text">{{ activity.distance }}km</text>
        </view>
        <view class="apply-info">
          <text class="apply-text">{{ activity.apply_count }}/{{ activity.total_quota }}人已报名</text>
          <view class="progress-bar">
            <view class="progress-fill" :style="{width: (activity.apply_count / activity.total_quota * 100) + '%'}"></view>
          </view>
        </view>
      </view>
      
      <view class="loading" v-if="loading">
        <text>加载中...</text>
      </view>
      
      <view class="no-more" v-if="!loading && noMore">
        <text>没有更多了</text>
      </view>
      
      <view class="empty" v-if="!loading && activities.length === 0">
        <text>暂无活动</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getRunGroupActivities } from '@/utils/request.js';

const activities = ref([]);
const currentStatus = ref('');
const page = ref(1);
const loading = ref(false);
const refreshing = ref(false);
const noMore = ref(false);

const loadActivities = async (refresh = false) => {
  if (loading.value) return;
  
  if (refresh) {
    page.value = 1;
    noMore.value = false;
  }
  
  loading.value = true;
  
  try {
    const res = await getRunGroupActivities({
      page: page.value,
      size: 10,
      status: currentStatus.value || undefined
    });
    
    if (refresh) {
      activities.value = res.items;
    } else {
      activities.value.push(...res.items);
    }
    
    if (res.items.length < 10) {
      noMore.value = true;
    }
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' });
  } finally {
    loading.value = false;
    refreshing.value = false;
  }
};

const changeStatus = (status) => {
  currentStatus.value = status;
  loadActivities(true);
};

const onRefresh = () => {
  refreshing.value = true;
  loadActivities(true);
};

const loadMore = () => {
  if (!loading.value && !noMore.value) {
    page.value += 1;
    loadActivities();
  }
};

const getStatusText = (status) => {
  const statusMap = {
    'upcoming': '报名中',
    'ongoing': '进行中',
    'finished': '已结束'
  };
  return statusMap[status] || '报名中';
};

const formatTime = (timeStr) => {
  const date = new Date(timeStr);
  return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
};

const goToDetail = (activityId) => {
  uni.navigateTo({ url: `/pages/run-group/activity-detail?activityId=${activityId}` });
};

onMounted(() => {
  loadActivities(true);
});
</script>

<style scoped>
.activity-list-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.filter-bar {
  display: flex;
  background: #fff;
  padding: 18rpx 30rpx;
  gap: 16rpx;
  box-sizing: border-box;
}

.filter-item {
  flex: 1;
  min-width: 0;
  text-align: center;
  height: 60rpx;
  line-height: 60rpx;
  padding: 0 8rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
  color: #666;
  background: #f5f7fa;
  box-sizing: border-box;
}

.filter-item.active {
  background: #20C997;
  color: #fff;
}

.activity-scroll {
  height: calc(100vh - 104rpx);
  padding: 18rpx 30rpx 30rpx;
  box-sizing: border-box;
}

.activity-card {
  background: #fff;
  border-radius: 18rpx;
  padding: 28rpx 24rpx;
  margin-bottom: 18rpx;
  box-shadow: 0 6rpx 18rpx rgba(26, 43, 60, 0.05);
  position: relative;
  box-sizing: border-box;
}

.status-badge {
  position: absolute;
  top: 20rpx;
  right: 20rpx;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  font-size: 20rpx;
  color: #fff;
}

.status-upcoming {
  background: #20C997;
}

.status-ongoing {
  background: #ff9f43;
}

.status-finished {
  background: #adb5bd;
}

.title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
  padding-right: 140rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 12rpx;
}

.info-icon-img { width: 28rpx; height: 28rpx; margin-right: 12rpx; vertical-align: middle; flex-shrink: 0; }

.text {
  flex: 1;
  min-width: 0;
  font-size: 24rpx;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.apply-info {
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 1px solid #f0f0f0;
}

.apply-text {
  font-size: 24rpx;
  color: #999;
  display: block;
  margin-bottom: 12rpx;
}

.progress-bar {
  height: 8rpx;
  background: #f0f0f0;
  border-radius: 4rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #20C997;
  border-radius: 4rpx;
}

.loading, .no-more, .empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
  font-size: 24rpx;
}
</style>
