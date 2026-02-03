<template>
  <view class="create-task-page">
    <view class="form-card">
      <view class="form-item">
        <text class="label">任务标题</text>
        <input class="input" v-model="form.title" placeholder="例如：本周5公里耐力跑" />
      </view>
      <!-- 任务类型选择器 -->
      <view class="form-item">
        <text class="label">任务类型</text>
        <picker mode="selector" :range="taskTypeLabels" @change="onTypeChange">
          <view class="picker-box">
            <text>{{ form.typeLabel || '请选择任务类型' }}</text>
            <text class="arrow">></text>
          </view>
        </picker>
      </view>

      <view class="form-item">
        <text class="label">目标距离 (km)</text>
        <input class="input" type="digit" v-model="form.distance" placeholder="0.0" />
      </view>
      
      <view class="form-item">
        <text class="label">截止日期</text>
        <picker mode="date" @change="onDateChange">
          <view class="picker-box">
            <text>{{ form.deadline || '请选择截止日期' }}</text>
            <text class="arrow">></text>
          </view>
        </picker>
      </view>

      <view class="form-item">
        <text class="label">指派对象</text>
        <picker mode="selector" :range="groupLabels" @change="onGroupChange">
          <view class="picker-box">
            <text>{{ form.targetLabel || '全员' }}</text>
            <text class="arrow">></text>
          </view>
        </picker>
      </view>

      <view class="form-item vertical">
        <text class="label">任务说明</text>
        <textarea class="textarea" v-model="form.description" placeholder="请输入任务的具体要求和注意事项..." />
      </view>
    </view>

    <view class="footer-btn">
      <button class="submit-btn" @click="submitTask">发布任务</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { createTeacherTask, request } from '@/utils/request.js';

const taskTypes = ['run', 'test']; // Simplified to match backend enum/string
const taskTypeLabels = ['跑步任务', '体能测试']; // Display labels
const groupOptions = ref(['all']);
const groupLabels = ref(['全员']);
const classes = ref([]);

const form = ref({
  title: '',
  type: '',
  typeLabel: '',
  distance: '',
  deadline: '',
  target: 'all',
  targetLabel: '全员',
  description: ''
});

onMounted(() => {
  fetchClasses();
});

const fetchClasses = async () => {
  try {
    const res = await request({ url: '/teacher/classes' });
    classes.value = res;
    // Update group options
    groupLabels.value = ['全员', ...res.map(c => `班级: ${c.name}`)];
    groupOptions.value = ['all', ...res.map(c => c.id)];
  } catch (e) {
    console.error('Fetch classes failed', e);
  }
};

const onTypeChange = (e) => {
  const index = e.detail.value;
  form.value.type = taskTypes[index];
  form.value.typeLabel = taskTypeLabels[index];
};

const onDateChange = (e) => {
  form.value.deadline = e.detail.value;
};

const onGroupChange = (e) => {
  const index = e.detail.value;
  form.value.target = groupOptions.value[index];
  form.value.targetLabel = groupLabels.value[index];
};

const submitTask = async () => {
  if (!form.value.title || !form.value.type || !form.value.deadline) {
    return uni.showToast({ title: '请完善任务信息', icon: 'none' });
  }
  
  uni.showLoading({ title: '发布中...' });
  
  try {
    const payload = {
      title: form.value.title,
      type: form.value.type,
      min_distance: form.value.type === 'run' ? Number(form.value.distance) : 0,
      min_duration: 0,
      min_count: 0,
      deadline: new Date(form.value.deadline).toISOString(),
      description: form.value.description,
      target_group: form.value.target === 'all' ? 'all' : null,
      class_id: typeof form.value.target === 'number' ? form.value.target : null
    };
    
    await createTeacherTask(payload);
    
    uni.hideLoading();
    uni.showToast({ title: '任务发布成功', icon: 'success' });
    
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  } catch (e) {
    uni.hideLoading();
    console.error(e);
  }
};
</script>

<style scoped>
.create-task-page {
  min-height: 100vh;
  background: #f8f8f8;
  padding: 20rpx;
  padding-bottom: 120rpx;
}

.form-card {
  background: #fff;
  border-radius: 12rpx;
  padding: 0 30rpx;
}

.form-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx 0;
  border-bottom: 1px solid #eee;
}

.form-item:last-child {
  border-bottom: none;
}

.form-item.vertical {
  flex-direction: column;
  align-items: flex-start;
  gap: 20rpx;
}

.label {
  font-size: 30rpx;
  color: #333;
  width: 200rpx;
}

.input {
  flex: 1;
  text-align: right;
  font-size: 30rpx;
  color: #333;
}

.picker-box {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10rpx;
  font-size: 30rpx;
  color: #666;
}

.arrow {
  color: #ccc;
  font-size: 26rpx;
}

.textarea {
  width: 100%;
  height: 200rpx;
  background: #f9f9f9;
  padding: 20rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.footer-btn {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: #fff;
  padding: 20rpx 30rpx;
  box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
  box-sizing: border-box;
}

.submit-btn {
  background: #20C997;
  color: #fff;
  border-radius: 40rpx;
  font-size: 32rpx;
  font-weight: bold;
}
</style>