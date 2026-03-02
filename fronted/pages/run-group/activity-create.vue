<template>
  <view class="create-page">
    <view class="form">
      <view class="form-item">
        <text class="label">活动标题 *</text>
        <input v-model="form.title" placeholder="请输入活动标题" class="input" />
      </view>
      
      <view class="form-item">
        <text class="label">活动日期 *</text>
        <picker mode="date" :value="form.date" @change="onDateChange">
          <view class="picker">{{ form.date || '选择日期' }}</view>
        </picker>
      </view>
      
      <view class="form-item">
        <text class="label">活动时间 *</text>
        <picker mode="time" :value="form.time" @change="onTimeChange">
          <view class="picker">{{ form.time || '选择时间' }}</view>
        </picker>
      </view>
      
      <view class="form-item">
        <text class="label">活动地点</text>
        <input v-model="form.location" placeholder="请输入活动地点" class="input" />
      </view>
      
      <view class="form-item">
        <text class="label">目标距离(km)</text>
        <input v-model.number="form.distance" type="digit" placeholder="请输入目标距离" class="input" />
      </view>
      
      <view class="form-item">
        <text class="label">总名额 *</text>
        <input v-model.number="form.total_quota" type="number" placeholder="请输入总名额" class="input" />
      </view>
      
      <view class="form-item">
        <text class="label">活动描述</text>
        <textarea v-model="form.description" placeholder="请输入活动描述" class="textarea" />
      </view>
    </view>
    
    <view class="bottom-bar">
      <button class="submit-btn" @click="handleSubmit">发起活动</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { createGroupActivity, getMyRunGroup } from '@/utils/request.js';

const form = ref({
  title: '',
  description: '',
  date: '',
  time: '',
  location: '',
  distance: null,
  total_quota: 50
});

const myGroup = ref(null);

const loadMyGroup = async () => {
  try {
    const res = await getMyRunGroup();
    myGroup.value = res;
  } catch (e) {
    uni.showToast({ title: '请先加入跑团', icon: 'none' });
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  }
};

const onDateChange = (e) => {
  form.value.date = e.detail.value;
};

const onTimeChange = (e) => {
  form.value.time = e.detail.value;
};

const handleSubmit = async () => {
  if (!form.value.title) {
    uni.showToast({ title: '请输入活动标题', icon: 'none' });
    return;
  }
  
  if (!form.value.date || !form.value.time) {
    uni.showToast({ title: '请选择活动时间', icon: 'none' });
    return;
  }
  
  if (!form.value.total_quota || form.value.total_quota < 1) {
    uni.showToast({ title: '请输入有效的总名额', icon: 'none' });
    return;
  }
  
  try {
    const activityTime = `${form.value.date}T${form.value.time}:00`;
    const res = await createGroupActivity({
      group_id: myGroup.value.id,
      title: form.value.title,
      description: form.value.description,
      activity_time: activityTime,
      location: form.value.location,
      distance: form.value.distance,
      total_quota: form.value.total_quota
    });
    
    uni.showToast({ title: '发起成功', icon: 'success' });
    setTimeout(() => {
      uni.redirectTo({ url: `/pages/run-group/activity-detail?activityId=${res.id}` });
    }, 1500);
  } catch (e) {
    uni.showToast({ title: e.detail || '发起失败', icon: 'none' });
  }
};

onMounted(() => {
  loadMyGroup();
});
</script>

<style scoped>
.create-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20rpx 30rpx 140rpx;
}

.form {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.form-item {
  margin-bottom: 30rpx;
}

.label {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
  display: block;
  margin-bottom: 16rpx;
}

.input, .picker {
  width: 100%;
  padding: 20rpx;
  background: #f5f7fa;
  border-radius: 12rpx;
  font-size: 26rpx;
  color: #333;
}

.picker {
  color: #999;
}

.textarea {
  width: 100%;
  min-height: 200rpx;
  padding: 20rpx;
  background: #f5f7fa;
  border-radius: 12rpx;
  font-size: 26rpx;
  color: #333;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 30rpx;
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.submit-btn {
  width: 100%;
  padding: 24rpx;
  background: linear-gradient(135deg, #20C997, #17a589);
  color: #fff;
  border-radius: 30rpx;
  font-size: 30rpx;
  font-weight: bold;
  border: none;
}
</style>
