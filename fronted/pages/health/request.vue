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
          <text class="item-reason">{{ item.reason }}</text>
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
import { request } from '@/utils/request.js';

const submitting = ref(false);
const formData = ref({
  type: 'leave',
  reason: ''
});
const history = ref([]);

const loadHistory = async () => {
  try {
    const res = await request('/student/health/requests');
    history.value = res;
  } catch (e) {
    console.error(e);
    // uni.showToast({ title: '加载记录失败', icon: 'none' });
  }
};

const submitRequest = async () => {
  if (!formData.value.reason.trim()) {
    return uni.showToast({ title: '请填写原因', icon: 'none' });
  }
  
  submitting.value = true;
  try {
    await request('/student/health/request', {
      method: 'POST',
      data: {
        type: formData.value.type,
        reason: formData.value.reason
      }
    });
    
    uni.showToast({ title: '提交成功', icon: 'success' });
    formData.value.reason = '';
    
    // 刷新列表
    await loadHistory();
    
  } catch (e) {
    uni.showToast({ title: e.detail || '提交失败', icon: 'none' });
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
</style>