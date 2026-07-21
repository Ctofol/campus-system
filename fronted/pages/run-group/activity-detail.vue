<template>
  <view class="detail-page">
    <view class="header-bg"></view>
    
    <view class="content" v-if="activity">
      <view class="title-section">
        <text class="title">{{ activity.title }}</text>
        <view class="status-badge" :class="'status-' + activity.status">
          <text>{{ getStatusText(activity.status) }}</text>
        </view>
      </view>
      
      <view class="info-card">
        <view class="info-item">
          <image class="detail-icon-img" src="/static/icons/icon-activity-time.svg" mode="aspectFit" />
          <view class="info-content">
            <text class="label">活动时间</text>
            <text class="value">{{ formatTime(activity.activity_time) }}</text>
          </view>
        </view>
        
        <view class="info-item" v-if="activity.location">
          <image class="detail-icon-img" src="/static/icons/icon-activity-location.svg" mode="aspectFit" />
          <view class="info-content">
            <text class="label">活动地点</text>
            <text class="value">{{ activity.location }}</text>
          </view>
        </view>
        
        <view class="info-item" v-if="activity.distance">
          <image class="detail-icon-img" src="/static/icons/icon-activity-distance.svg" mode="aspectFit" />
          <view class="info-content">
            <text class="label">目标距离</text>
            <text class="value">{{ activity.distance }}km</text>
          </view>
        </view>
        
        <view class="info-item">
          <image class="detail-icon-img" src="/static/icons/icon-learning-users.svg" mode="aspectFit" />
          <view class="info-content">
            <text class="label">报名人数</text>
            <text class="value">{{ activity.apply_count }}/{{ activity.total_quota }}人</text>
          </view>
        </view>
      </view>
      
      <view class="progress-section">
        <text class="progress-label">报名进度</text>
        <view class="progress-bar">
          <view class="progress-fill" :style="{width: progressPercent + '%'}"></view>
        </view>
        <text class="progress-text">{{ progressPercent }}%</text>
      </view>
      
      <view class="desc-section" v-if="activity.description">
        <text class="page-section-title">活动描述</text>
        <text class="desc-text">{{ activity.description }}</text>
      </view>
    </view>
    
    <view class="bottom-bar" v-if="activity && activity.status === 'upcoming'">
      <button class="action-btn cancel" v-if="hasApplied" @click="handleCancel">取消报名</button>
      <button class="action-btn apply" v-else @click="handleApply">立即报名</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { getActivityDetail, applyActivity, cancelActivity } from '@/utils/request.js';

const activityId = ref(0);
const activity = ref(null);
const hasApplied = ref(false);

const progressPercent = computed(() => {
  if (!activity.value) return 0;
  const quota = Number(activity.value.total_quota) || 0;
  if (quota <= 0) return 0;
  const applied = Number(activity.value.apply_count) || 0;
  return Math.min(Math.round((applied / quota) * 100), 100);
});

const loadDetail = async () => {
  try {
    const res = await getActivityDetail(activityId.value);
    activity.value = res;
    
    // TODO: 从后端获取是否已报名状态
    // 暂时通过本地存储判断
    const appliedActivities = uni.getStorageSync('appliedActivities') || [];
    hasApplied.value = appliedActivities.includes(activityId.value);
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' });
  }
};

const handleApply = async () => {
  try {
    const res = await applyActivity(activityId.value);
    if (res.applyStatus) {
      uni.showToast({ title: '报名成功', icon: 'success' });
      hasApplied.value = true;
      activity.value.apply_count += 1;
      
      // 保存到本地
      const appliedActivities = uni.getStorageSync('appliedActivities') || [];
      appliedActivities.push(activityId.value);
      uni.setStorageSync('appliedActivities', appliedActivities);
    } else {
      uni.showToast({ title: res.message, icon: 'none' });
    }
  } catch (e) {
    uni.showToast({ title: '报名失败', icon: 'none' });
  }
};

const handleCancel = async () => {
  uni.showModal({
    title: '确认取消',
    content: '确定要取消报名吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          const result = await cancelActivity(activityId.value);
          if (result.success) {
            uni.showToast({ title: '取消成功', icon: 'success' });
            hasApplied.value = false;
            activity.value.apply_count -= 1;
            
            // 从本地移除
            let appliedActivities = uni.getStorageSync('appliedActivities') || [];
            appliedActivities = appliedActivities.filter(id => id !== activityId.value);
            uni.setStorageSync('appliedActivities', appliedActivities);
          } else {
            uni.showToast({ title: result.message, icon: 'none' });
          }
        } catch (e) {
          uni.showToast({ title: '取消失败', icon: 'none' });
        }
      }
    }
  });
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
  if (Number.isNaN(date.getTime())) return '';
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const hour = date.getHours();
  const minute = date.getMinutes().toString().padStart(2, '0');
  return `${year}年${month}月${day}日 ${hour}:${minute}`;
};

onLoad((options = {}) => {
  const rawId = options.activityId || options.id;
  const id = Number.parseInt(rawId, 10);
  if (!Number.isFinite(id) || id <= 0) {
    uni.showToast({ title: '活动参数错误', icon: 'none' });
    return;
  }
  activityId.value = id;
  loadDetail();
});
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: #F5F8FA;
  padding-bottom: 120rpx;
}

.header-bg {
  height: 286rpx;
  background: #24BFA2;
}

.content {
  margin-top: -200rpx;
  padding: 0 30rpx;
}

.title-section {
  background: #fff;
  border-radius: 18rpx;
  padding: 30rpx 28rpx;
  margin-bottom: 18rpx;
  box-shadow: 0 8rpx 22rpx rgba(24, 35, 46, 0.045);
  border: 1rpx solid rgba(24, 35, 46, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title {
  flex: 1;
  font-size: 36rpx;
  font-weight: bold;
  color: #18232E;
  line-height: 1.4;
}

.status-badge {
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  color: #fff;
  margin-left: 20rpx;
}

.status-upcoming {
  background: #24BFA2;
}

.status-ongoing {
  background: #ff9f43;
}

.status-finished {
  background: #adb5bd;
}

.info-card {
  background: #fff;
  border-radius: 18rpx;
  padding: 28rpx;
  margin-bottom: 18rpx;
  border: 1rpx solid rgba(24, 35, 46, 0.06);
}

.info-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #EEF2F5;
}

.info-item:last-child {
  border-bottom: none;
}

.detail-icon-img { width: 40rpx; height: 40rpx; margin-right: 20rpx; flex-shrink: 0; }

.info-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.label {
  font-size: 24rpx;
  color: #718094;
  margin-bottom: 8rpx;
}

.value {
  font-size: 28rpx;
  color: #18232E;
  font-weight: 500;
}

.progress-section {
  background: #fff;
  border-radius: 18rpx;
  padding: 28rpx;
  margin-bottom: 18rpx;
  border: 1rpx solid rgba(24, 35, 46, 0.06);
}

.progress-label {
  font-size: 26rpx;
  color: #666;
  display: block;
  margin-bottom: 16rpx;
}

.progress-bar {
  height: 16rpx;
  background: #EEF2F5;
  border-radius: 8rpx;
  overflow: hidden;
  margin-bottom: 12rpx;
}

.progress-fill {
  height: 100%;
  background: #24BFA2;
  border-radius: 8rpx;
}

.progress-text {
  font-size: 24rpx;
  color: #24BFA2;
  font-weight: bold;
}

.desc-section {
  background: #fff;
  border-radius: 18rpx;
  padding: 28rpx;
  border: 1rpx solid rgba(24, 35, 46, 0.06);
}

.section-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
}

.desc-text {
  font-size: 26rpx;
  color: #666;
  line-height: 1.8;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.06);
  box-sizing: border-box;
}

.action-btn {
  width: 100%;
  height: 84rpx;
  line-height: 84rpx;
  padding: 0 16rpx;
  margin: 0;
  border-radius: 30rpx;
  font-size: 30rpx;
  font-weight: bold;
  border: none;
  box-sizing: border-box;
}

.action-btn::after {
  border: none;
}

.action-btn.apply {
  background: #24BFA2;
  color: #fff;
}

.action-btn.cancel {
  background: #fff;
  color: #ff6b6b;
  border: 2px solid #ff6b6b;
}
</style>
