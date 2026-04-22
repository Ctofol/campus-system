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
            <text class="arrow">→</text>
          </view>
        </picker>
      </view>

      <!-- 体测任务视频上传（第二阶段新增） -->
      <view class="form-item vertical" v-if="form.type === 'test'">
        <text class="label required">体测示范视频</text>
        <view class="video-upload-area">
          <view v-if="!form.videoUrl" class="upload-placeholder" @click="chooseVideo">
            <text class="upload-icon">📹</text>
            <text class="upload-text">点击上传体测示范视频</text>
            <text class="upload-hint">支持mp4/webm格式，最大50MB</text>
          </view>
          <view v-else class="video-preview">
            <video 
              :src="form.videoUrl" 
              class="preview-video"
              controls
              :show-center-play-btn="true"
            ></video>
            <view class="video-actions">
              <button class="action-btn" size="mini" @click="chooseVideo">重新上传</button>
              <button class="action-btn delete" size="mini" @click="deleteVideo">删除</button>
            </view>
          </view>
        </view>
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
            <text class="arrow">→</text>
          </view>
        </picker>
      </view>

      <view class="form-item">
        <text class="label">指派对象</text>
        <picker mode="selector" :range="groupLabels" @change="onGroupChange">
          <view class="picker-box">
            <text>{{ form.targetLabel || '全员' }}</text>
            <text class="arrow">→</text>
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
import { ref, onMounted, watch } from 'vue';
import { createTeacherTask, request, BASE_URL } from '@/utils/request.js';

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
  description: '',
  videoUrl: '',  // 第二阶段新增：视频URL
  videoFile: null  // 临时存储视频文件
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
  
  // 如果切换到非体测任务，清空视频
  if (form.value.type !== 'test') {
    form.value.videoUrl = '';
    form.value.videoFile = null;
  }
};

const onDateChange = (e) => {
  form.value.deadline = e.detail.value;
};

const onGroupChange = (e) => {
  const index = e.detail.value;
  form.value.target = groupOptions.value[index];
  form.value.targetLabel = groupLabels.value[index];
};

// 第二阶段新增：视频上传功能
const chooseVideo = () => {
  uni.chooseVideo({
    sourceType: ['camera', 'album'],
    maxDuration: 300, // 最长5分钟
    camera: 'back',
    success: async (res) => {
      const tempFilePath = res.tempFilePath;
      const fileSize = res.size;
      
      // 检查文件大小（50MB限制）
      if (fileSize > 50 * 1024 * 1024) {
        return uni.showToast({ title: '视频文件不能超过50MB', icon: 'none' });
      }
      
      // 显示上传中
      uni.showLoading({ title: '上传中...' });
      
      try {
        // 上传视频
        const uploadRes = await uploadVideo(tempFilePath);
        form.value.videoUrl = uploadRes.url;
        uni.hideLoading();
        uni.showToast({ title: '视频上传成功', icon: 'success' });
      } catch (e) {
        uni.hideLoading();
        console.error('Upload failed:', e);
        uni.showToast({ title: '视频上传失败', icon: 'none' });
      }
    }
  });
};

const uploadVideo = (filePath) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token');
    
    uni.uploadFile({
      url: `${BASE_URL}/upload`,
      filePath: filePath,
      name: 'file',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const data = JSON.parse(res.data);
          resolve(data);
        } else {
          reject(new Error('Upload failed'));
        }
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
};

const deleteVideo = () => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除已上传的视频吗？',
    success: (res) => {
      if (res.confirm) {
        form.value.videoUrl = '';
        form.value.videoFile = null;
        uni.showToast({ title: '已删除', icon: 'success' });
      }
    }
  });
};

const submitTask = async () => {
  // 验证必填项
  if (!form.value.title || !form.value.type || !form.value.deadline) {
    return uni.showToast({ title: '请完善任务信息', icon: 'none' });
  }
  
  // 体测任务必须上传视频
  if (form.value.type === 'test' && !form.value.videoUrl) {
    return uni.showToast({ title: '体测任务必须上传示范视频', icon: 'none' });
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
      class_id: typeof form.value.target === 'number' ? form.value.target : null,
      video_url: form.value.videoUrl || null  // 第二阶段新增：视频URL
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
    uni.showToast({ title: '发布失败', icon: 'none' });
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

/* 第二阶段新增：视频上传样式 */
.label.required::after {
  content: '*';
  color: #ff4d4f;
  margin-left: 4rpx;
}

.video-upload-area {
  width: 100%;
}

.upload-placeholder {
  width: 100%;
  height: 300rpx;
  background: #f9f9f9;
  border: 2rpx dashed #ddd;
  border-radius: 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
}

.upload-icon {
  font-size: 60rpx;
}

.upload-text {
  font-size: 28rpx;
  color: #666;
}

.upload-hint {
  font-size: 24rpx;
  color: #999;
}

.video-preview {
  width: 100%;
}

.preview-video {
  width: 100%;
  height: 400rpx;
  background: #000;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
}

.video-actions {
  display: flex;
  gap: 20rpx;
  justify-content: center;
}

.action-btn {
  margin: 0;
  font-size: 26rpx;
  padding: 0 30rpx;
  background: #fff;
  color: #20C997;
  border: 1px solid #20C997;
}

.action-btn.delete {
  color: #ff4d4f;
  border-color: #ff4d4f;
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