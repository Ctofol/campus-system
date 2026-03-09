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
      <view class="alert-card" v-for="(alert, index) in filteredAlerts" :key="alert.id">
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
            <text class="label">异常数据：</text>
            <text class="value highlight">{{ alert.value }}</text>
            <text class="standard">（标准范围：{{ alert.standard }}）</text>
          </view>
          <view class="desc-box">
            <text class="desc-title">异常说明：</text>
            <text class="desc-content">{{ alert.description }}</text>
          </view>
        </view>

        <view class="card-footer">
          <button class="action-btn ignore" size="mini" @click="ignoreAlert(alert.id)">忽略</button>
          <button class="action-btn notify" size="mini" @click="notifyStudent(alert)">通知学生</button>
          <button class="action-btn handle" size="mini" @click="handleAlert(alert)">处理</button>
        </view>
      </view>

      <view v-if="filteredAlerts.length === 0" class="empty-state">
        <text class="empty-text">暂无异常数据</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onLoad, onShow } from '@dcloudio/uni-app';
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

// 从后端获取异常数据
const fetchAbnormalData = async () => {
  loading.value = true;
  try {
    const res = await request({
      url: '/teacher/activities/abnormal',
      method: 'GET'
    });
    
    if (Array.isArray(res)) {
      alerts.value = res.map(item => {
        // 判断异常类型和级别
        let typeText = '数据异常';
        let typeClass = 'tag-orange';
        let level = 'normal';
        let description = item.reason || '运动数据存在异常';
        
        // 根据异常原因判断类型
        if (item.reason && item.reason.includes('心率')) {
          typeText = '心率异常';
          typeClass = 'tag-red';
          level = 'urgent';
        } else if (item.reason && item.reason.includes('配速')) {
          typeText = '配速异常';
          typeClass = 'tag-orange';
        } else if (item.reason && (item.reason.includes('轨迹') || item.reason.includes('GPS'))) {
          typeText = '轨迹异常';
          typeClass = 'tag-blue';
        } else if (item.reason && item.reason.includes('距离')) {
          typeText = '距离异常';
          typeClass = 'tag-orange';
        }
        
        return {
          id: item.activity_id || item.id,
          type: item.type || 'unknown',
          typeText: typeText,
          typeClass: typeClass,
          studentName: item.student_name || '未知学生',
          studentId: item.student_id || '--',
          time: item.created_at ? new Date(item.created_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) : '--',
          value: item.abnormal_value || '异常',
          standard: item.standard_range || '--',
          description: description,
          level: level
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

const ignoreAlert = (id) => {
  uni.showModal({
    title: '确认忽略',
    content: '忽略后该异常将不再提醒，确认操作？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await request({
            url: `/teacher/activities/${id}/ignore`,
            method: 'POST'
          });
          alerts.value = alerts.value.filter(a => a.id !== id);
          uni.showToast({ title: '已忽略', icon: 'success' });
        } catch (e) {
          console.error('Failed to ignore alert:', e);
          uni.showToast({ title: '操作失败', icon: 'none' });
        }
      }
    }
  });
};

const notifyStudent = async (alert) => {
  try {
    await request({
      url: `/teacher/students/${alert.studentId}/notify`,
      method: 'POST',
      data: {
        message: `您的运动数据存在异常：${alert.typeText}，请注意查看。`
      }
    });
    uni.showToast({
      title: `已发送通知给 ${alert.studentName}`,
      icon: 'success'
    });
  } catch (e) {
    console.error('Failed to notify student:', e);
    uni.showToast({ title: '通知发送失败', icon: 'none' });
  }
};

const handleAlert = (alert) => {
  uni.showActionSheet({
    itemList: ['标记为无效成绩', '标记为设备故障', '要求重测'],
    success: async (res) => {
      const actions = ['invalid', 'device_error', 'retest'];
      const actionTexts = ['无效成绩', '设备故障', '重测'];
      
      try {
        await request({
          url: `/teacher/activities/${alert.id}/handle`,
          method: 'POST',
          data: {
            action: actions[res.tapIndex],
            reason: alert.description
          }
        });
        
        uni.showToast({
          title: `已标记为：${actionTexts[res.tapIndex]}`,
          icon: 'success'
        });
        
        alerts.value = alerts.value.filter(a => a.id !== alert.id);
      } catch (e) {
        console.error('Failed to handle alert:', e);
        uni.showToast({ title: '处理失败', icon: 'none' });
      }
    }
  });
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
    gap: 20rpx;

    .action-btn {
      margin: 0;
      font-size: 24rpx;
      padding: 0 30rpx;
      border-radius: 30rpx;
      background: #fff;
      
      &.ignore {
        color: #999;
        border: 1px solid #ddd;
      }

      &.notify {
        color: #1890ff;
        border: 1px solid #1890ff;
      }

      &.handle {
        background: #20C997;
        color: #fff;
        border: none;
      }
    }
  }
}

.empty-state {
  padding: 60rpx;
  text-align: center;
  color: #999;
  font-size: 28rpx;
}
</style>
