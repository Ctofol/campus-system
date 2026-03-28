<template>
  <view class="container">
    <view class="form-card">
      <view class="form-header">
        <text class="title">健康报备申请</text>
        <text class="subtitle">请如实填写申请信息，提交后将由老师审批</text>
      </view>
      
      <view class="form-item">
        <text class="label">申请类型</text>
        <view class="type-selector">
          <view 
            class="type-btn" 
            :class="{active: formData.type === 'leave'}"
            @click="formData.type = 'leave'"
          >
            <text class="icon">📅</text>
            <text>请假申请</text>
          </view>
          <view 
            class="type-btn" 
            :class="{active: formData.type === 'injury'}"
            @click="formData.type = 'injury'"
          >
            <text class="icon">🏥</text>
            <text>伤病报告</text>
          </view>
        </view>
      </view>
      
      <!-- 请假时间（仅请假申请显示） -->
      <view class="form-item" v-if="formData.type === 'leave'">
        <text class="label">请假时间</text>
        <view class="time-range">
          <picker mode="date" :value="formData.start_date" @change="onStartDateChange">
            <view class="time-input">
              <text>{{ formData.start_date || '开始日期' }}</text>
            </view>
          </picker>
          <text class="time-separator">至</text>
          <picker mode="date" :value="formData.end_date" @change="onEndDateChange">
            <view class="time-input">
              <text>{{ formData.end_date || '结束日期' }}</text>
            </view>
          </picker>
        </view>
        <text class="label-tip">请假开始和结束日期（精确到天）</text>
      </view>
      
      <view class="form-item">
        <text class="label">申请原因</text>
        <textarea 
          class="reason-input" 
          v-model="formData.reason" 
          placeholder="请详细描述原因（例如：感冒发烧、脚踝扭伤等）"
          maxlength="200"
        />
        <text class="word-count">{{formData.reason.length}}/200</text>
      </view>
      
      <view class="form-item">
        <text class="label">附件上传（选填）</text>
        <text class="label-tip">可上传请假证明、病历单等图片</text>
        <view class="upload-area">
          <view class="image-list">
            <view class="image-item" v-for="(img, index) in uploadedImages" :key="index">
              <image :src="img" mode="aspectFill" class="preview-image" @click="previewImage(index)" />
              <view class="delete-btn" @click="deleteImage(index)">×</view>
            </view>
            <view class="upload-btn" @click="chooseImage" v-if="uploadedImages.length < 3">
              <text class="upload-icon">+</text>
              <text class="upload-text">上传图片</text>
            </view>
          </view>
          <text class="upload-tip">最多上传3张图片</text>
        </view>
      </view>
      
      <button 
        class="submit-btn" 
        :disabled="submitting" 
        @click="submitRequest"
      >
        {{ submitting ? '提交中...' : '提交申请' }}
      </button>
    </view>
    
    <!-- 历史记录 -->
    <view class="history-section">
      <view class="section-title">最近申请记录</view>
      <view class="history-list">
        <view class="history-item" v-for="item in history" :key="item.id">
          <view class="item-header">
            <text class="item-type" :class="item.type">
              {{ item.type === 'leave' ? '请假' : '伤病' }}
            </text>
            <text class="item-status" :class="item.status">
              {{ getStatusText(item.status) }}
            </text>
          </view>
          <view class="item-time-range" v-if="item.type === 'leave' && (item.start_date || item.end_date)">
            <text class="time-range-text">
              {{ (item.start_date || '').substring(0, 10) }} 至 {{ (item.end_date || '').substring(0, 10) }}
            </text>
          </view>
          <text class="item-reason">{{ item.reason }}</text>
          <view class="item-attachments" v-if="item.attachments && item.attachments.length > 0">
            <image 
              v-for="(img, idx) in item.attachments" 
              :key="idx" 
              :src="img" 
              mode="aspectFill" 
              class="attachment-thumb"
              @click="previewHistoryImage(item.attachments, idx)"
            />
          </view>
          <text class="item-time">{{ formatDate(item.created_at) }}</text>
        </view>
        <view class="empty-tip" v-if="history.length === 0">
          暂无申请记录
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad, onShow } from '@dcloudio/uni-app';
import { request, BASE_URL } from '@/utils/request.js';

const submitting = ref(false);
const formData = ref({
  type: 'leave',
  reason: '',
  start_date: '',
  end_date: ''
});
const uploadedImages = ref([]);
const history = ref([]);

const loadHistory = async () => {
  try {
    const res = await request('/student/health/requests');
    // API now returns attachments as array directly
    history.value = res.map(item => ({
      ...item,
      attachments: item.attachments || []
    }));
  } catch (e) {
    console.error(e);
  }
};

const chooseImage = () => {
  uni.chooseImage({
    count: 3 - uploadedImages.value.length,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const tempFilePaths = res.tempFilePaths;
      
      // Show loading
      uni.showLoading({ title: '上传中...' });
      
      try {
        for (const filePath of tempFilePaths) {
          const uploadRes = await uploadImage(filePath);
          if (uploadRes) {
            uploadedImages.value.push(uploadRes);
          }
        }
      } catch (e) {
        uni.showToast({ title: '上传失败', icon: 'none' });
      } finally {
        uni.hideLoading();
      }
    }
  });
};

const uploadImage = (filePath) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token');
    
    uni.uploadFile({
      url: `${BASE_URL}/upload/file`,
      filePath: filePath,
      name: 'file',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const data = JSON.parse(res.data);
          resolve(data.url);
        } else {
          reject(new Error('Upload failed'));
        }
      },
      fail: reject
    });
  });
};

const deleteImage = (index) => {
  uploadedImages.value.splice(index, 1);
};

const previewImage = (index) => {
  uni.previewImage({
    urls: uploadedImages.value,
    current: index
  });
};

const previewHistoryImage = (images, index) => {
  uni.previewImage({
    urls: images,
    current: index
  });
};

const submitRequest = async () => {
  if (!formData.value.reason.trim()) {
    return uni.showToast({ title: '请填写原因', icon: 'none' });
  }
  if (formData.value.type === 'leave') {
    if (!formData.value.start_date || !formData.value.end_date) {
      return uni.showToast({ title: '请选择请假时间', icon: 'none' });
    }
    if (formData.value.end_date < formData.value.start_date) {
      return uni.showToast({ title: '结束日期不能早于开始日期', icon: 'none' });
    }
  }
  
  submitting.value = true;
  try {
    await request('/student/health/request', {
      method: 'POST',
      data: {
        type: formData.value.type,
        reason: formData.value.reason,
        start_date: formData.value.start_date || null,
        end_date: formData.value.end_date || null,
        attachments: uploadedImages.value
      }
    });
    
    uni.showToast({ title: '提交成功', icon: 'success' });
    formData.value.reason = '';
    formData.value.start_date = '';
    formData.value.end_date = '';
    uploadedImages.value = [];
    
    // 刷新列表
    await loadHistory();
    
  } catch (e) {
    uni.showToast({ title: e.message || e.detail || '提交失败', icon: 'none' });
  } finally {
    submitting.value = false;
  }
};

const getStatusText = (status) => {
  const map = {
    pending: '待审批',
    approved: '已通过',
    rejected: '已驳回'
  };
  return map[status] || status;
};

const formatDate = (str) => {
  if (!str) return '';
  return str.replace('T', ' ').substring(0, 16);
};

// 处理日期选择
const onStartDateChange = (e) => {
  formData.value.start_date = e.detail.value;
};

const onEndDateChange = (e) => {
  formData.value.end_date = e.detail.value;
};

onShow(() => {
  loadHistory();
});
</script>

<style lang="scss" scoped>
.container {
  padding: 30rpx;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.form-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 40rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05);
}

.form-header {
  margin-bottom: 40rpx;
  text-align: center;
  
  .title {
    font-size: 36rpx;
    font-weight: bold;
    color: #333;
    display: block;
    margin-bottom: 10rpx;
  }
  
  .subtitle {
    font-size: 24rpx;
    color: #999;
  }
}

.form-item {
  margin-bottom: 30rpx;
  
  .label {
    font-size: 28rpx;
    color: #333;
    margin-bottom: 16rpx;
    display: block;
    font-weight: 500;
  }
  
  .label-tip {
    font-size: 24rpx;
    color: #999;
    margin-bottom: 12rpx;
    display: block;
  }
}

.time-range {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 10rpx;
}

.time-input {
  flex: 1;
  background: #f7f9fc;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 28rpx;
  color: #333;
}

.time-separator {
  margin: 0 20rpx;
  color: #999;
  font-size: 26rpx;
}

.type-selector {
  display: flex;
  gap: 20rpx;
  
  .type-btn {
    flex: 1;
    background: #f8f9fa;
    border: 2rpx solid #eee;
    border-radius: 12rpx;
    padding: 24rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10rpx;
    transition: all 0.3s;
    
    .icon {
      font-size: 40rpx;
    }
    
    &.active {
      background: #e6f7ff;
      border-color: #1890ff;
      color: #1890ff;
    }
  }
}

.reason-input {
  width: 100%;
  height: 200rpx;
  background: #f8f9fa;
  border-radius: 12rpx;
  padding: 20rpx;
  box-sizing: border-box;
  font-size: 28rpx;
}

.word-count {
  text-align: right;
  font-size: 24rpx;
  color: #999;
  display: block;
  margin-top: 8rpx;
}

.submit-btn {
  background: #1890ff;
  color: #fff;
  border-radius: 40rpx;
  margin-top: 20rpx;
  font-size: 32rpx;
  
  &:active {
    opacity: 0.9;
  }
  
  &[disabled] {
    background: #ccc;
  }
}

.history-section {
  .section-title {
    font-size: 30rpx;
    font-weight: bold;
    color: #333;
    margin-bottom: 20rpx;
    padding-left: 10rpx;
  }
}

.history-item {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  
  .item-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12rpx;
    
    .item-type {
      font-size: 26rpx;
      padding: 4rpx 12rpx;
      border-radius: 6rpx;
      background: #eee;
      
      &.leave { color: #fa8c16; background: #fff7e6; }
      &.injury { color: #f5222d; background: #fff1f0; }
    }
    
    .item-status {
      font-size: 26rpx;
      
      &.pending { color: #1890ff; }
      &.approved { color: #52c41a; }
      &.rejected { color: #ff4d4f; }
    }
  }
  
  .item-reason {
    font-size: 28rpx;
    color: #666;
    margin-bottom: 12rpx;
    display: block;
  }
  
  .item-time {
    font-size: 24rpx;
    color: #999;
  }
}

.empty-tip {
  text-align: center;
  color: #999;
  padding: 40rpx;
  font-size: 26rpx;
}

.upload-area {
  .image-list {
    display: flex;
    flex-wrap: wrap;
    gap: 20rpx;
  }
  
  .image-item {
    position: relative;
    width: 200rpx;
    height: 200rpx;
    border-radius: 12rpx;
    overflow: hidden;
    
    .preview-image {
      width: 100%;
      height: 100%;
    }
    
    .delete-btn {
      position: absolute;
      top: 0;
      right: 0;
      width: 50rpx;
      height: 50rpx;
      background: rgba(0, 0, 0, 0.6);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 40rpx;
      line-height: 1;
    }
  }
  
  .upload-btn {
    width: 200rpx;
    height: 200rpx;
    border: 2rpx dashed #ddd;
    border-radius: 12rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #fafafa;
    
    .upload-icon {
      font-size: 60rpx;
      color: #999;
      margin-bottom: 10rpx;
    }
    
    .upload-text {
      font-size: 24rpx;
      color: #999;
    }
  }
  
  .upload-tip {
    font-size: 22rpx;
    color: #999;
    margin-top: 12rpx;
    display: block;
  }
}

.item-attachments {
  display: flex;
  gap: 10rpx;
  margin: 12rpx 0;
  
  .attachment-thumb {
    width: 120rpx;
    height: 120rpx;
    border-radius: 8rpx;
  }
}
</style>