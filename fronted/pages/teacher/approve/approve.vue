<template>
  <view class="container">
    <view class="header">
      <text class="title">待审批活动</text>
    </view>
    <scroll-view scroll-y class="list">
      <view class="item" v-for="item in activities" :key="item.id" @click="goToDetail(item)">
        <view class="info">
          <text class="name">{{ item.student_name }}</text>
          <view class="desc-row">
            <text class="desc" v-if="item.type === 'run'">跑步 - {{ item.metrics?.distance ? Number(item.metrics.distance).toFixed(2) : 0 }}km</text>
            <text class="desc" v-else>体测 - {{ item.metrics?.count ? item.metrics.count : 0 }}次</text>
          </view>
          <text class="time">{{ new Date(item.started_at).toLocaleString() }}</text>
        </view>
        <button class="btn" @click.stop="handleApprove(item.id)" :disabled="item.status === 'approved' || item.status === 'completed'" :style="{ backgroundColor: (item.status === 'approved' || item.status === 'completed') ? '#ccc' : '#20C997' }">
          {{ (item.status === 'approved' || item.status === 'completed') ? '已通过' : '通过' }}
        </button>
      </view>
      <view v-if="activities.length === 0" class="empty">暂无待审批活动</view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { getTeacherActivities, approveActivity } from '@/utils/request.js';

const activities = ref([]);

const loadData = async () => {
  try {
    const res = await getTeacherActivities({ page: 1, size: 20 });
    if (res && res.items) {
      activities.value = res.items;
    }
  } catch (e) {
    console.error(e);
    uni.showToast({ title: '加载待审批活动失败', icon: 'none' });
  }
};

const handleApprove = async (id) => {
  try {
    await approveActivity(id);
    uni.showToast({ title: '审批成功' });
    loadData(); // Reload
  } catch (e) {
    console.error(e);
    uni.showToast({ title: '审批失败，请稍后重试', icon: 'none' });
  }
};

const goToDetail = (item) => {
  // Navigate to student detail page with student ID
  uni.navigateTo({
    url: `/pages/teacher/approve/student-detail?studentId=${item.user_id}&studentName=${item.student_name}`
  });
};

onShow(() => {
  loadData();
});
</script>

<style>
.container { padding: 20rpx; background-color: #f5f7fa; min-height: 100vh; }
.header { margin-bottom: 20rpx; font-weight: bold; font-size: 32rpx; padding: 10rpx 0; }
.item { display: flex; justify-content: space-between; align-items: center; background: #fff; padding: 30rpx; margin-bottom: 20rpx; border-radius: 12rpx; box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.05); }
.info { display: flex; flex-direction: column; }
.name { font-weight: bold; font-size: 30rpx; margin-bottom: 8rpx; }
.desc { color: #666; font-size: 26rpx; margin-bottom: 8rpx; }
.time { color: #999; font-size: 22rpx; }
.btn { font-size: 24rpx; color: #fff; padding: 0 30rpx; height: 60rpx; line-height: 60rpx; border-radius: 30rpx; }
.empty { text-align: center; color: #999; margin-top: 100rpx; font-size: 28rpx; }
</style>
