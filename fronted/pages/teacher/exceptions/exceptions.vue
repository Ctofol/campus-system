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

const currentFilter = ref('all');

const alerts = ref([
  {
    id: 1,
    type: 'heart_rate',
    typeText: '心率过高',
    typeClass: 'tag-red',
    studentName: '张三',
    studentId: '2023001',
    time: '10:30',
    value: '195 bpm',
    standard: '60-180 bpm',
    description: '跑步过程中持续3分钟心率超过安全阈值，建议暂停训练并检查身体状况。',
    level: 'urgent'
  },
  {
    id: 2,
    type: 'pace',
    typeText: '配速异常',
    typeClass: 'tag-orange',
    studentName: '李四',
    studentId: '2023002',
    time: '10:45',
    value: '2\'30"/km',
    standard: '4\'00"-8\'00"/km',
    description: '短时间内配速极快，疑似骑车或数据漂移。',
    level: 'normal'
  },
  {
    id: 3,
    type: 'location',
    typeText: '轨迹异常',
    typeClass: 'tag-blue',
    studentName: '王五',
    studentId: '2023003',
    time: '09:15',
    value: '直线穿越',
    standard: '连续轨迹',
    description: '轨迹点之间距离过大，且无中间路径，疑似GPS信号丢失或作弊。',
    level: 'normal'
  }
]);

const pendingCount = computed(() => alerts.value.length);
const todayCount = ref(5); // Mock data

const filteredAlerts = computed(() => {
  if (currentFilter.value === 'all') return alerts.value;
  return alerts.value.filter(a => a.level === currentFilter.value);
});

const ignoreAlert = (id) => {
  uni.showModal({
    title: '确认忽略',
    content: '忽略后该异常将不再提醒，确认操作？',
    success: (res) => {
      if (res.confirm) {
        alerts.value = alerts.value.filter(a => a.id !== id);
        uni.showToast({ title: '已忽略', icon: 'none' });
      }
    }
  });
};

const notifyStudent = (alert) => {
  uni.showToast({
    title: `已发送通知给 ${alert.studentName}`,
    icon: 'success'
  });
};

const handleAlert = (alert) => {
  uni.showActionSheet({
    itemList: ['标记为无效成绩', '标记为设备故障', '要求重测'],
    success: (res) => {
      const actions = ['无效成绩', '设备故障', '重测'];
      uni.showToast({
        title: `已标记为：${actions[res.tapIndex]}`,
        icon: 'success'
      });
      alerts.value = alerts.value.filter(a => a.id !== alert.id);
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
