<template>
  <view class="container">
    <view class="header">
      <text class="page-title">异常处理</text>
      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-num">{{ pendingCount }}</text>
          <text class="stat-desc">待处理</text>
        </view>
        <view class="stat-item">
          <text class="stat-num">{{ todayCount }}</text>
          <text class="stat-desc">今日新增</text>
        </view>
      </view>
    </view>

    <view class="filter-bar">
      <text 
        class="filter-item" 
        :class="{ active: currentFilter === 'all' }" 
        @click="currentFilter = 'all'"
      >全部</text>
      <text 
        class="filter-item" 
        :class="{ active: currentFilter === 'urgent' }" 
        @click="currentFilter = 'urgent'"
      >紧急</text>
      <text 
        class="filter-item" 
        :class="{ active: currentFilter === 'normal' }" 
        @click="currentFilter = 'normal'"
      >一般</text>
    </view>

    <scroll-view scroll-y class="alert-list">
      <view
        class="alert-card"
        v-for="(alert, index) in filteredAlerts"
        :key="alert.id"
        @click="openDetail(alert)"
      >
        <view class="card-header">
          <view class="header-left">
            <view class="type-tag" :class="alert.typeClass">{{ alert.typeText }}</view>
            <text class="student-name">{{ alert.studentName }}</text>
            <text class="student-id">{{ alert.studentId }}</text>
          </view>
          <text class="time">{{ alert.time }}</text>
        </view>

        <view class="card-body">
          <view class="data-row">
            <text class="label">异常类型：</text>
            <text class="value highlight">{{ alert.typeText }}</text>
          </view>
          <view class="data-row">
            <text class="label">配速/里程：</text>
            <text class="value">
              {{ alert.distanceText }} · {{ alert.pace || '--' }}
            </text>
          </view>
          <view class="desc-box">
            <text class="desc-title">异常说明：</text>
            <text class="desc-content">{{ alert.description }}</text>
          </view>
        </view>

        <view class="card-footer">
          <text class="footer-tip">点击卡片查看详情与处理</text>
        </view>
      </view>

      <view v-if="filteredAlerts.length === 0" class="empty-state">
        <text class="empty-text">暂无异常数据</text>
      </view>
    </scroll-view>

    <!-- 异常详情弹窗 -->
    <view v-if="detailVisible" class="detail-mask" @click.self="closeDetail">
      <view class="detail-modal">
        <view class="detail-header">
          <view class="detail-header-main">
            <text class="detail-title">异常处理</text>
            <text class="detail-subtitle">{{ selectedAlert.studentName }}（{{ selectedAlert.studentId }}）</text>
          </view>
          <text class="detail-close" @click="closeDetail">关闭</text>
        </view>
        <view class="detail-photos">
          <view class="photo-box">
            <text class="photo-label">起跑照片</text>
            <image
              v-if="selectedAlert.startPhoto"
              :src="selectedAlert.startPhoto"
              mode="aspectFill"
              class="photo-img"
            />
            <view v-else class="photo-placeholder">无照片</view>
          </view>
          <view class="photo-box">
            <text class="photo-label">终点照片</text>
            <image
              v-if="selectedAlert.endPhoto"
              :src="selectedAlert.endPhoto"
              mode="aspectFill"
              class="photo-img"
            />
            <view v-else class="photo-placeholder">无照片</view>
          </view>
        </view>

        <view class="detail-data">
          <view class="data-row">
            <text class="label">里程：</text>
            <text class="value">{{ selectedAlert.distanceText }}</text>
          </view>
          <view class="data-row">
            <text class="label">时长：</text>
            <text class="value">{{ selectedAlert.durationText }}</text>
          </view>
          <view class="data-row">
            <text class="label">配速：</text>
            <text class="value">{{ selectedAlert.pace || '--' }}</text>
          </view>
          <view class="data-row">
            <text class="label">异常原因：</text>
            <text class="value danger">{{ selectedAlert.description }}</text>
          </view>
        </view>

        <view class="detail-actions">
          <button class="detail-btn warn" @click="sendCheatWarning">发送作弊警告</button>
          <button class="detail-btn success" @click="markAsValid">判定有效</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { request } from '@/utils/request.js';

const currentFilter = ref('all');
const alerts = ref([]);
const loading = ref(false);

const pendingCount = computed(() => alerts.value.length);
const todayCount = ref(0);

const filteredAlerts = computed(() => {
  if (currentFilter.value === 'all') return alerts.value;
  return alerts.value.filter(a => a.level === currentFilter.value);
});

// 详情弹窗
const detailVisible = ref(false);
const selectedAlert = ref({
  id: null,
  studentId: '',
  studentName: '',
  startPhoto: '',
  endPhoto: '',
  distanceText: '',
  durationText: '',
  pace: '',
  description: ''
});

// 从后端获取异常数据
const fetchAbnormalData = async () => {
  loading.value = true;
  try {
    const res = await request({
      url: '/teacher/activities/invalid',
      method: 'GET'
    });

    if (Array.isArray(res)) {
      alerts.value = res.map(item => {
        const reason = item.fail_reason || item.reason || '阳光跑数据存在异常';
        // 判断异常类型和级别（仅关注配速/人脸）
        let typeText = '配速异常';
        let typeClass = 'tag-orange';
        let level = 'normal';

        if (reason.includes('人脸')) {
          typeText = '人脸比对失败';
          typeClass = 'tag-red';
          level = 'urgent';
        } else if (reason.includes('配速')) {
          typeText = '配速异常';
          typeClass = 'tag-orange';
        }

        const distanceKm = typeof item.distance === 'number' ? item.distance : null;
        const durationSec = typeof item.duration === 'number' ? item.duration : null;

        const distanceText = distanceKm != null ? `${distanceKm.toFixed(2)} km` : '--';
        const durationMinutes = durationSec != null ? Math.floor(durationSec / 60) : null;
        const durationSeconds = durationSec != null ? durationSec % 60 : null;
        const durationText = durationSec != null ? `${durationMinutes}分${durationSeconds}秒` : '--';

        return {
          id: item.id || item.activity_id,
          type: item.type || 'run',
          typeText,
          typeClass,
          studentName: item.student_name || '未知学生',
          studentId: item.student_id || '--',
          time: item.started_at ? new Date(item.started_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) : '--',
          distance: distanceKm,
          distanceText,
          duration: durationSec,
          durationText,
          pace: item.pace || '--',
          description: reason,
          startPhoto: item.start_photo_url || item.start_photo || '',
          endPhoto: item.end_photo_url || item.end_photo || '',
          level
        };
      });

      // 统计今日新增
      const today = new Date().toDateString();
      todayCount.value = alerts.value.filter(a => {
        if (!a.time) return false;
        const alertDate = new Date(a.time).toDateString();
        return alertDate === today;
      }).length;
    }
  } catch (e) {
    console.error('Failed to fetch abnormal data:', e);
    uni.showToast({ title: '加载失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
};

onShow(() => {
  fetchAbnormalData();
});

const openDetail = (alert) => {
  selectedAlert.value = { ...alert };
  detailVisible.value = true;
};

const closeDetail = () => {
  detailVisible.value = false;
};

// 发送作弊警告：调用异常处理 & 通知学生
const sendCheatWarning = async () => {
  if (!selectedAlert.value || !selectedAlert.value.id) return;
  const alert = selectedAlert.value;
  try {
    await request({
      url: `/teacher/activities/${alert.id}/resolve`,
      method: 'POST',
      data: {
        action: 'confirm_cheat'
      }
    });

    await request({
      url: `/teacher/students/${alert.studentId}/notify`,
      method: 'POST',
      data: {
        message: `系统检测到您本次阳光跑存在异常（${alert.typeText}），已记为异常记录，如有疑问请联系任课老师。`
      }
    });

    uni.showToast({
      title: '已发送作弊警告',
      icon: 'success'
    });

    alerts.value = alerts.value.filter(a => a.id !== alert.id);
    closeDetail();
  } catch (e) {
    console.error('Failed to send cheat warning:', e);
    const msg = (e && (e.message || e.detail)) || '操作失败';
    uni.showToast({ title: msg, icon: 'none' });
  }
};

// 判定有效：恢复该次阳光跑有效状态
const markAsValid = async () => {
  if (!selectedAlert.value || !selectedAlert.value.id) return;
  const alert = selectedAlert.value;
  try {
    await request({
      url: `/teacher/activities/${alert.id}/resolve`,
      method: 'POST',
      data: {
        action: 'restore_valid'
      }
    });

    uni.showToast({
      title: '已恢复为有效记录',
      icon: 'success'
    });

    alerts.value = alerts.value.filter(a => a.id !== alert.id);
    closeDetail();
  } catch (e) {
    console.error('Failed to mark activity as valid:', e);
    const msg = (e && (e.message || e.detail)) || '操作失败';
    uni.showToast({ title: msg, icon: 'none' });
  }
};
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20rpx;
}

.header {
  background: #fff;
  padding: 30rpx;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);

  .page-title {
    font-size: 36rpx;
    font-weight: bold;
    color: #333;
  }

  .stats-row {
    display: flex;
    gap: 40rpx;

    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;

      .stat-num {
        font-size: 32rpx;
        font-weight: bold;
        color: #ff6b6b;
      }

      .stat-desc {
        font-size: 22rpx;
        color: #999;
      }
    }
  }
}

.filter-bar {
  display: flex;
  margin-bottom: 20rpx;
  background: #fff;
  padding: 10rpx;
  border-radius: 12rpx;

  .filter-item {
    flex: 1;
    text-align: center;
    padding: 16rpx 0;
    font-size: 28rpx;
    color: #666;
    border-radius: 8rpx;
    transition: all 0.3s;

    &.active {
      background: #e6f7ff;
      color: #1890ff;
      font-weight: 500;
    }
  }
}

.alert-list {
  padding-bottom: 40rpx;
}

.alert-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24rpx;
    padding-bottom: 20rpx;
    border-bottom: 1px solid #f0f0f0;

    .header-left {
      display: flex;
      align-items: center;
      gap: 16rpx;

      .type-tag {
        font-size: 22rpx;
        padding: 4rpx 12rpx;
        border-radius: 6rpx;
        color: #fff;

        &.tag-red { background: #ff4d4f; }
        &.tag-orange { background: #faad14; }
        &.tag-blue { background: #1890ff; }
      }

      .student-name {
        font-size: 30rpx;
        font-weight: 500;
        color: #333;
      }

      .student-id {
        font-size: 24rpx;
        color: #999;
      }
    }

    .time {
      font-size: 24rpx;
      color: #999;
    }
  }

  .card-body {
    margin-bottom: 24rpx;

    .data-row {
      margin-bottom: 16rpx;
      font-size: 28rpx;
      
      .label { color: #666; }
      .value { 
        color: #333; 
        font-weight: 500; 
        &.highlight { color: #ff4d4f; }
      }
      .standard { color: #999; font-size: 24rpx; }
    }

    .desc-box {
      background: #f9f9f9;
      padding: 16rpx;
      border-radius: 8rpx;

      .desc-title {
        font-size: 26rpx;
        color: #333;
        font-weight: 500;
        display: block;
        margin-bottom: 8rpx;
      }

      .desc-content {
        font-size: 26rpx;
        color: #666;
        line-height: 1.5;
      }
    }
  }

  .card-footer {
    display: flex;
    justify-content: flex-end;
    align-items: center;

    .footer-tip {
      font-size: 24rpx;
      color: #999;
    }
  }
}

.detail-mask {
  position: fixed;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.detail-modal {
  width: 90%;
  max-width: 700rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
}

.detail-header {
  margin-bottom: 24rpx;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;

  .detail-header-main {
    flex: 1;
  }

  .detail-close {
    font-size: 28rpx;
    color: #1989fa;
    padding: 8rpx 16rpx;
    flex-shrink: 0;
  }

  .detail-title {
    font-size: 32rpx;
    font-weight: bold;
    color: #333;
  }

  .detail-subtitle {
    margin-top: 8rpx;
    font-size: 26rpx;
    color: #666;
  }
}

.detail-photos {
  display: flex;
  gap: 20rpx;
  margin-bottom: 24rpx;
}

.photo-box {
  flex: 1;
}

.photo-label {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 8rpx;
  display: block;
}

.photo-img {
  width: 100%;
  height: 200rpx;
  border-radius: 12rpx;
  background: #f3f4f6;
}

.photo-placeholder {
  width: 100%;
  height: 200rpx;
  border-radius: 12rpx;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #999;
}

.detail-data {
  margin-bottom: 24rpx;
}

.detail-data .data-row .value.danger {
  color: #e03131;
}

.detail-actions {
  display: flex;
  gap: 20rpx;
}

.detail-btn {
  flex: 1;
  border-radius: 999rpx;
  font-size: 26rpx;
}

.detail-btn.warn {
  background: #ffe3e3;
  color: #e03131;
}

.detail-btn.success {
  background: #12b886;
  color: #fff;
}

.empty-state {
  padding: 60rpx;
  text-align: center;
  color: #999;
  font-size: 28rpx;
}
</style>
