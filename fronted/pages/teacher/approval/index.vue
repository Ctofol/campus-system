<template>
  <view class="approval-container">
    <!-- Custom Navigation Bar -->
    <view class="custom-nav-bar">
      <view class="nav-status-bar"></view>
      <view class="nav-content">
        <view class="nav-back" @click="goBack">
          <text class="nav-back-icon">←</text>
        </view>
        <text class="nav-title">待审批</text>
      </view>
    </view>

    <!-- Approval List -->
    <view class="approval-list">
      <view v-if="loading" class="loading-state">
        <text class="loading-text">加载中...</text>
      </view>

      <view v-else-if="approvals.length === 0" class="empty-state">
        <text class="empty-icon">✓</text>
        <text class="empty-text">暂无待审批项</text>
      </view>

      <view v-else>
        <view 
          class="approval-item" 
          v-for="item in approvals" 
          :key="item.id"
        >
          <view class="approval-header">
            <view class="student-info">
              <text class="student-name">{{ item.student_name }}</text>
              <text class="approval-type" :class="getTypeClass(item.type)">{{ item.type }}</text>
            </view>
            <text class="approval-time">{{ formatTime(item.created_at) }}</text>
          </view>

          <view class="approval-content">
            <text class="reason-label">原因：</text>
            <text class="reason-text">{{ item.reason }}</text>
          </view>

          <view class="approval-actions">
            <button 
              class="action-btn reject-btn" 
              @click="handleReject(item.id)"
              :disabled="processing"
            >
              驳回
            </button>
            <button 
              class="action-btn approve-btn" 
              @click="handleApprove(item.id)"
              :disabled="processing"
            >
              通过
            </button>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { request } from '@/utils/request.js';

const approvals = ref([]);
const loading = ref(true);
const processing = ref(false);

const goBack = () => {
  uni.navigateBack();
};

const fetchApprovals = async () => {
  loading.value = true;
  try {
    const res = await request({
      url: '/approvals/pending',
      method: 'GET'
    });
    approvals.value = Array.isArray(res) ? res : [];
  } catch (e) {
    console.error('Failed to fetch approvals:', e);
    uni.showToast({ title: '加载失败', icon: 'none' });
    approvals.value = [];
  } finally {
    loading.value = false;
  }
};

const handleApprove = async (id) => {
  processing.value = true;
  try {
    await request({
      url: `/approvals/${id}/approve`,
      method: 'POST'
    });
    uni.showToast({ title: '已通过', icon: 'success' });
    // Remove from list
    approvals.value = approvals.value.filter(item => item.id !== id);
  } catch (e) {
    console.error('Failed to approve:', e);
    uni.showToast({ title: '操作失败', icon: 'none' });
  } finally {
    processing.value = false;
  }
};

const handleReject = async (id) => {
  uni.showModal({
    title: '确认驳回',
    content: '确定要驳回此申请吗？',
    success: async (res) => {
      if (res.confirm) {
        processing.value = true;
        try {
          await request({
            url: `/approvals/${id}/reject`,
            method: 'POST'
          });
          uni.showToast({ title: '已驳回', icon: 'success' });
          // Remove from list
          approvals.value = approvals.value.filter(item => item.id !== id);
        } catch (e) {
          console.error('Failed to reject:', e);
          uni.showToast({ title: '操作失败', icon: 'none' });
        } finally {
          processing.value = false;
        }
      }
    }
  });
};

const getTypeClass = (type) => {
  if (type.includes('请假')) return 'type-leave';
  if (type.includes('受伤')) return 'type-injury';
  return 'type-default';
};

const formatTime = (dateStr) => {
  if (!dateStr) return '--';
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (hours < 1) {
      const minutes = Math.floor(diff / (1000 * 60));
      return `${minutes}分钟前`;
    } else if (hours < 24) {
      return `${hours}小时前`;
    } else {
      const month = date.getMonth() + 1;
      const day = date.getDate();
      return `${month}月${day}日`;
    }
  } catch (e) {
    return '--';
  }
};

onMounted(() => {
  fetchApprovals();
});
</script>

<style scoped>
.approval-container {
  min-height: 100vh;
  background: #f5f7fa;
}

/* Custom Navigation Bar */
.custom-nav-bar {
  background: #20C997;
  width: 100%;
  position: sticky;
  top: 0;
  z-index: 100;
}
.nav-status-bar {
  height: var(--status-bar-height);
  width: 100%;
}
.nav-content {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.nav-back {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  padding: 0 30rpx;
}
.nav-back-icon {
  color: #fff;
  font-size: 40rpx;
  font-weight: bold;
}
.nav-title {
  color: #fff;
  font-size: 32rpx;
  font-weight: bold;
}

/* Approval List */
.approval-list {
  padding: 30rpx;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 200rpx 0;
}

.loading-text {
  font-size: 28rpx;
  color: #999;
}

.empty-icon {
  font-size: 120rpx;
  color: #20C997;
  margin-bottom: 30rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}

.approval-item {
  background: #fff;
  border-radius: 24rpx;
  padding: 36rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.03);
}

.approval-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.student-info {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.student-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.approval-type {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  color: #fff;
}

.type-leave {
  background: #4dabf7;
}

.type-injury {
  background: #ff6b6b;
}

.type-default {
  background: #999;
}

.approval-time {
  font-size: 24rpx;
  color: #999;
}

.approval-content {
  padding: 24rpx;
  background: #f8f9fa;
  border-radius: 16rpx;
  margin-bottom: 30rpx;
}

.reason-label {
  font-size: 26rpx;
  color: #666;
  font-weight: 500;
}

.reason-text {
  font-size: 28rpx;
  color: #333;
  line-height: 1.6;
  margin-left: 10rpx;
}

.approval-actions {
  display: flex;
  gap: 24rpx;
}

.action-btn {
  flex: 1;
  height: 80rpx;
  line-height: 80rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  font-weight: 500;
  border: none;
  margin: 0;
  padding: 0;
}

.reject-btn {
  background: #fff;
  color: #666;
  border: 2rpx solid #e0e0e0;
}

.reject-btn:active {
  background: #f5f5f5;
}

.approve-btn {
  background: #20C997;
  color: #fff;
}

.approve-btn:active {
  opacity: 0.9;
}

.action-btn[disabled] {
  opacity: 0.5;
}
</style>
