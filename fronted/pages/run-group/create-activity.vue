<template>
  <view class="create-activity-page">
    <view class="navbar">
      <text class="back-btn" @click="goBack">←</text>
      <text class="title">发布活动</text>
    </view>
    
    <view class="form-container">
      <view class="form-item">
        <text class="label">活动封面</text>
        <view class="cover-upload" @click="chooseCover">
          <image v-if="coverImage" :src="coverImage" mode="aspectFill" class="cover-preview" />
          <view v-else class="cover-placeholder">
            <text class="upload-icon">📷</text>
            <text class="upload-text">点击上传封面</text>
          </view>
        </view>
      </view>
      
      <view class="form-item">
        <text class="label">活动标题</text>
        <input 
          class="input" 
          v-model="formData.title" 
          placeholder="请输入活动标题" 
          maxlength="30"
        />
      </view>
      
      <view class="form-item">
        <text class="label">活动描述</text>
        <textarea 
          class="textarea" 
          v-model="formData.description" 
          placeholder="请输入活动描述" 
          maxlength="200"
        />
      </view>
      
      <view class="form-item">
        <text class="label">活动时间</text>
        <picker 
          mode="date" 
          :value="activityDate"
          @change="onDateChange"
        >
          <view class="picker">
            {{ activityDate || '请选择日期' }}
          </view>
        </picker>
        <picker 
          mode="time" 
          :value="activityTimeValue"
          @change="onTimeChange"
        >
          <view class="picker">
            {{ activityTimeValue || '请选择时间' }}
          </view>
        </picker>
      </view>
      
      <view class="form-item">
        <text class="label">活动地点</text>
        <input 
          class="input" 
          v-model="formData.location" 
          placeholder="请输入活动地点" 
          maxlength="50"
        />
      </view>
      
      <view class="form-item">
        <text class="label">目标距离（公里）</text>
        <input 
          class="input" 
          type="digit"
          v-model="formData.distance" 
          placeholder="请输入目标距离" 
        />
      </view>
      
      <view class="form-item">
        <text class="label">活动名额</text>
        <input 
          class="input" 
          type="number"
          v-model="formData.total_quota" 
          placeholder="请输入活动名额" 
        />
      </view>
      
      <button class="submit-btn" @click="handleSubmit">发布活动</button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { createGroupActivity, uploadFile } from '@/utils/request.js';

const groupId = ref(0);
const activityDate = ref('');
const activityTimeValue = ref('');
const coverImage = ref('');
const coverUrl = ref('');
const formData = ref({
  title: '',
  description: '',
  location: '',
  distance: '',
  total_quota: 50
});

onLoad((options) => {
  if (options.groupId) {
    groupId.value = parseInt(options.groupId);
  } else {
    uni.showToast({ title: '参数错误', icon: 'none' });
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  }
});

const onDateChange = (e) => {
  activityDate.value = e.detail.value;
};

const onTimeChange = (e) => {
  activityTimeValue.value = e.detail.value;
};

const goBack = () => {
  uni.navigateBack();
};

const chooseCover = () => {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const tempFilePath = res.tempFilePaths[0];
      coverImage.value = tempFilePath;
      
      try {
        uni.showLoading({ title: '上传中...' });
        const uploadResult = await uploadFile(tempFilePath, 'image');
        coverUrl.value = uploadResult.url;
        uni.hideLoading();
        uni.showToast({ title: '上传成功', icon: 'success' });
      } catch (e) {
        uni.hideLoading();
        console.error('上传失败:', e);
        uni.showToast({ title: '上传失败', icon: 'none' });
      }
    }
  });
};

const handleSubmit = async () => {
  // 验证表单
  if (!formData.value.title) {
    uni.showToast({ title: '请输入活动标题', icon: 'none' });
    return;
  }
  
  if (!formData.value.description) {
    uni.showToast({ title: '请输入活动描述', icon: 'none' });
    return;
  }
  
  if (!activityDate.value || !activityTimeValue.value) {
    uni.showToast({ title: '请选择活动时间', icon: 'none' });
    return;
  }
  
  if (!formData.value.location) {
    uni.showToast({ title: '请输入活动地点', icon: 'none' });
    return;
  }
  
  if (!formData.value.distance || parseFloat(formData.value.distance) <= 0) {
    uni.showToast({ title: '请输入有效的目标距离', icon: 'none' });
    return;
  }
  
  if (!formData.value.total_quota || parseInt(formData.value.total_quota) <= 0) {
    uni.showToast({ title: '请输入有效的活动名额', icon: 'none' });
    return;
  }
  
  try {
    uni.showLoading({ title: '发布中...' });
    
    // 组合日期和时间
    const activityTimeStr = `${activityDate.value} ${activityTimeValue.value}:00`;
    
    const data = {
      group_id: groupId.value,
      title: formData.value.title,
      description: formData.value.description,
      cover_image: coverUrl.value || null,
      activity_time: activityTimeStr,
      location: formData.value.location,
      distance: parseFloat(formData.value.distance),
      total_quota: parseInt(formData.value.total_quota)
    };
    
    console.log('提交数据:', data);
    
    await createGroupActivity(data);
    
    uni.hideLoading();
    uni.showToast({ title: '发布成功', icon: 'success' });
    
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  } catch (e) {
    uni.hideLoading();
    console.error('发布失败:', e);
    const errorMsg = e.message || e.detail || '发布失败，请重试';
    uni.showToast({ title: errorMsg, icon: 'none' });
  }
};
</script>

<style scoped>
.create-activity-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.navbar {
  position: sticky;
  top: 0;
  background: #20C997;
  padding: 20rpx 30rpx;
  display: flex;
  align-items: center;
  z-index: 100;
}

.back-btn {
  font-size: 36rpx;
  color: #fff;
  margin-right: 20rpx;
}

.title {
  font-size: 32rpx;
  font-weight: bold;
  color: #fff;
}

.form-container {
  padding: 40rpx 30rpx;
}

.form-item {
  margin-bottom: 40rpx;
}

.label {
  display: block;
  font-size: 28rpx;
  color: #333;
  margin-bottom: 16rpx;
  font-weight: bold;
}

.input, .textarea, .picker {
  width: 100%;
  padding: 24rpx;
  background: #fff;
  border-radius: 16rpx;
  font-size: 28rpx;
  border: 2rpx solid #e0e0e0;
  box-sizing: border-box;
}

.input {
  height: 80rpx;
  line-height: 80rpx;
}

.textarea {
  min-height: 200rpx;
  line-height: 1.5;
}

.cover-upload {
  width: 100%;
  height: 300rpx;
  border-radius: 16rpx;
  overflow: hidden;
  background: #f5f7fa;
  border: 2rpx dashed #e0e0e0;
}

.cover-preview {
  width: 100%;
  height: 100%;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.upload-icon {
  font-size: 60rpx;
  margin-bottom: 16rpx;
}

.upload-text {
  font-size: 24rpx;
  color: #999;
}

.picker {
  color: #333;
}

.submit-btn {
  width: 100%;
  padding: 28rpx;
  background: linear-gradient(135deg, #4dabf7, #339af0);
  color: #fff;
  border-radius: 50rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
  margin-top: 40rpx;
}
</style>
