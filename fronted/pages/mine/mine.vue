<template>
  <view class="mine-page">
    <!-- 1. 账号主页（顶部） -->
    <view class="user-header">
      <view class="avatar-box">
        <image class="avatar" src="/static/avatar.png" mode="aspectFill"></image>
        <button class="edit-avatar" @click="gotoUserProfile">编辑资料</button>
      </view>
      <view class="user-info">
        <text class="username">{{userName}}</text>
        <text class="user-desc">校园运动打卡 · {{userType}}</text>
      </view>
      <view class="user-stats">
        <view class="stats-item">
          <text class="stats-num">{{totalRunCount}}</text>
          <text class="stats-text">总次数</text>
        </view>
        <view class="stats-item">
          <text class="stats-num">{{totalRunDistance}}km</text>
          <text class="stats-text">总距离</text>
        </view>
        <view class="stats-item">
          <text class="stats-num">{{policeSuccessCount}}</text>
          <text class="stats-text">体测达标</text>
        </view>
      </view>
    </view>

    <!-- 2. 本周跑步统计 -->
    <view class="week-run-card">
      <view class="card-header">
        <text class="card-title">本周跑步</text>
        <text class="date-range">{{weekDateRange}}</text>
      </view>
      <view class="week-stats">
        <view class="week-item">
          <text class="week-num">{{weekRunCount}}</text>
          <text class="week-text">跑步次数</text>
        </view>
        <view class="week-item">
          <text class="week-num">{{weekRunDistance}}km</text>
          <text class="week-text">总距离</text>
        </view>
        <view class="week-item">
          <text class="week-num">{{weekPoliceSuccess}}次</text>
          <text class="week-text">体测达标</text>
        </view>
      </view>
      <!-- 本周目标进度条 -->
      <view class="progress-box">
        <text class="progress-title">本周目标：跑步3次（完成{{weekRunCount}}/3）</text>
        <view class="progress-bar">
          <view class="progress-fill" :style="{width: progressPercent + '%'}"></view>
        </view>
      </view>
    </view>

    <!-- 3. 运动记录列表 -->
    <view class="record-card">
      <view class="card-header">
        <text class="card-title">运动记录</text>
        <button class="view-all" @click="viewAllRecords">查看全部</button>
      </view>
      <!-- 记录列表 -->
      <view class="record-list" v-if="runRecords.length > 0">
        <view class="record-item" v-for="(item, index) in showRecords" :key="index" @click="gotoRecordDetail(item)">
          <view class="record-type" :style="{backgroundColor: item.modeBg}">
            <text class="type-text">{{item.modeText}}</text>
          </view>
          <view class="record-info">
            <text class="record-date">{{item.createTime}}</text>
            <text class="record-data" v-if="item.type === 'run'">
              {{item.distance}}km | {{item.duration}}<text v-if="item.pace"> | 配速：{{Number(item.pace).toFixed(1)}} 分/公里</text>
            </text>
            <text class="record-data" v-else>{{item.testName}} | 次数：{{item.testCount}} | {{item.result}}</text>
          </view>
          <view class="record-status">
            <text class="status-text" :style="{color: item.statusColor}">{{item.statusText}}</text>
          </view>
        </view>
      </view>
      <!-- 空记录提示 -->
      <view class="empty-record" v-else>
        <text class="empty-icon">🏃</text>
        <text class="empty-text">暂无运动记录，快去跑步打卡吧～</text>
      </view>
    </view>

    <!-- 4. 设置中心 -->
    <view class="setting-card">
      <view class="setting-item" @click="gotoDeviceBind">
        <text class="setting-icon">📱</text>
        <text class="setting-text">设备绑定（防代跑）</text>
        <text class="setting-desc">{{deviceId || '未绑定'}}</text>
        <text class="arrow">＞</text>
      </view>
      <view class="setting-item" @click="clearCache">
        <text class="setting-icon">🗑️</text>
        <text class="setting-text">清除缓存</text>
        <text class="setting-desc">释放本地存储空间</text>
        <text class="arrow">＞</text>
      </view>
      <view class="setting-item" @click="gotoAbout">
        <text class="setting-icon">ℹ️</text>
        <text class="setting-text">关于我们</text>
        <text class="setting-desc">版本 v1.0.0</text>
        <text class="arrow">＞</text>
      </view>
      <view class="setting-item logout" @click="logout">
        <text class="setting-icon">🚪</text>
        <text class="setting-text">退出登录</text>
        <text class="arrow">＞</text>
      </view>
    </view>
    <CustomTabBar current="/pages/mine/mine" />
  </view>
</template>

<script setup>
// 统一导入规范
import { ref, computed} from 'vue';
import { onPullDownRefresh , onShow, onLoad } from '@dcloudio/uni-app';
import CustomTabBar from '@/components/CustomTabBar/CustomTabBar.vue';
import { getActivityHistory } from '@/utils/request.js';

// 1. 基础数据
const userName = ref('运动先锋');
const userType = ref('2024级侦查系');
const deviceId = ref('');
const totalRunCount = ref(0);
const totalRunDistance = ref(0);
const policeSuccessCount = ref(0);

// 2. 本周跑步数据
const weekRunCount = ref(0);
const weekRunDistance = ref(0);
const weekPoliceSuccess = ref(0);
const weekDateRange = ref('');
const progressPercent = ref(0);

// 3. 运动记录
const runRecords = ref([]);
const showRecords = ref([]); // 只显示最近5条

// 页面加载时初始化
onLoad(() => {
  // 开启下拉刷新
  uni.startPullDownRefresh();
});

// 页面显示时加载数据
onShow(() => {
  loadUserStats(); // 加载用户总数据
  loadWeekData(); // 加载本周数据
  loadRunRecords(); // 加载运动记录
  loadDeviceInfo(); // 加载设备绑定信息
});

// 下拉刷新
onPullDownRefresh(() => {
  loadUserStats();
  loadWeekData();
  loadRunRecords();
  // 停止下拉刷新
  setTimeout(() => {
    uni.stopPullDownRefresh();
    uni.showToast({ title: '数据已刷新', icon: 'success' });
  }, 500);
});

// 4. 加载用户总数据（本地缓存）
const loadUserStats = () => {
  totalRunCount.value = Number(uni.getStorageSync('totalRunCount')) || 0;
  totalRunDistance.value = (Number(uni.getStorageSync('totalRunDistance')) || 0).toFixed(1);
  policeSuccessCount.value = Number(uni.getStorageSync('policeSuccessCount')) || 0;
};

// 5. 加载本周数据
const loadWeekData = () => {
  // 计算本周日期范围（周一至周日）
  const now = new Date();
  const weekStart = new Date(now.setDate(now.getDate() - now.getDay() + 1));
  const weekEnd = new Date(now.setDate(now.getDate() + 6));
  weekDateRange.value = `${weekStart.getMonth()+1}月${weekStart.getDate()}日 - ${weekEnd.getMonth()+1}月${weekEnd.getDate()}日`;

  // 模拟本周数据（实际可从本地/云端读取）
  // 读取所有记录，筛选本周的
  const allRecords = uni.getStorageSync('runRecordsList') || [];
  let weekCount = 0;
  let weekDistance = 0;
  let weekPolice = 0;

  allRecords.forEach(record => {
    const recordTime = new Date(record.createTime);
    // 判断是否在本周
    if (recordTime >= weekStart && recordTime <= weekEnd) {
      const isRunType = record.type ? record.type === 'run' : true;
      if (isRunType) {
        weekCount++;
        weekDistance += record.distance;
        if (record.mode === 'police' && record.isPaceQualified) {
          weekPolice++;
        }
      } else {
        // 测试记录不计入跑步周统计
      }
    }
  });

  weekRunCount.value = weekCount;
  weekRunDistance.value = weekDistance.toFixed(1);
  weekPoliceSuccess.value = weekPolice;
  // 计算进度（目标3次）
  progressPercent.value = Math.min((weekCount / 3) * 100, 100);
};

// 6. 加载运动记录（API）
const loadRunRecords = async () => {
  try {
    const res = await getActivityHistory({ page: 1, size: 5 });
    if (res && res.items) {
      runRecords.value = res.items.map(item => {
        const isRun = item.type === 'run';
        return {
          id: item.id,
          type: item.type,
          modeText: isRun ? '跑步' : '体测',
          modeBg: isRun ? '#4CAF50' : '#2196F3',
          createTime: new Date(item.started_at).toLocaleString(),
          distance: item.metrics?.distance?.toFixed(2) || '0.00',
          duration: formatDuration(item.metrics?.duration || 0),
          pace: item.metrics?.pace || '--',
          testName: isRun ? '' : '专项测试',
          testCount: item.metrics?.count || 0,
          result: item.status === 'approved' || item.status === 'completed' ? '已完成' : item.status,
          statusText: item.status === 'approved' || item.status === 'completed' ? '已完成' : '审核中',
          statusColor: item.status === 'approved' || item.status === 'completed' ? '#4CAF50' : '#FF9800'
        };
      });
      showRecords.value = runRecords.value;
    }
  } catch (error) {
    console.error('Failed to load history:', error);
    uni.showToast({
      title: '加载历史记录失败',
      icon: 'none'
    });
  }
};

const formatDuration = (seconds) => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s < 10 ? '0' + s : s}`;
};

// 7. 加载设备信息
const loadDeviceInfo = () => {
  deviceId.value = uni.getStorageSync('bindDeviceId') || '';
};

// 8. 事件处理
// 编辑资料/账号主页
const gotoUserProfile = () => {
  uni.showToast({ title: '暂未开放，敬请期待', icon: 'none' });
};

// 查看全部记录
const viewAllRecords = () => {
  if (runRecords.value.length === 0) {
    uni.showToast({ title: '暂无运动记录', icon: 'none' });
    return;
  }
  // 可跳转至全部记录页面，这里先提示
  uni.showToast({ title: '已展示全部记录', icon: 'success' });
};

// 查看记录详情
const gotoRecordDetail = (item) => {
  uni.showModal({
    title: '记录详情',
    content: item.type === 'run'
      ? `模式：${item.modeText}\n时间：${item.createTime}\n距离：${item.distance}km\n时长：${item.duration}\n状态：${item.statusText}`
      : `类型：体能测试\n项目：${item.testName}\n次数：${item.testCount}\n判定：${item.result}\n时长：${item.duration}`,
    showCancel: false
  });
};

const gotoStudentsManage = () => {
  uni.navigateTo({ url: '/pages/teacher/students/students' });
};
const gotoTaskManage = () => {
  uni.showToast({ title: '教学任务管理开发中', icon: 'none' });
};
const gotoExportCenter = () => {
  uni.showToast({ title: '导出中心开发中', icon: 'none' });
};

const handleTeacherMineAction = (action) => {
  if (action === '待审批任务') {
    uni.showToast({ title: '跳转至审批列表', icon: 'none' });
  } else if (action === '学员考试记录') {
    uni.showToast({ title: '跳转至成绩查询', icon: 'none' });
  }
};

// 设备绑定
const gotoDeviceBind = () => {
  if (deviceId.value) {
    // 已绑定，确认是否解绑
    uni.showModal({
      title: '设备绑定',
      content: '是否解除当前设备绑定？',
      success: (res) => {
        if (res.confirm) {
          uni.removeStorageSync('bindDeviceId');
          deviceId.value = '';
          uni.showToast({ title: '已解除绑定', icon: 'success' });
        }
      }
    });
  } else {
    // 未绑定，执行绑定
    uni.getSystemInfo({
      success: (res) => {
        const uniqueId = res.deviceId || `${res.platform}_${res.model}`;
        uni.setStorageSync('bindDeviceId', uniqueId);
        deviceId.value = uniqueId;
        uni.showToast({ title: '设备绑定成功', icon: 'success' });
      },
      fail: () => {
        uni.showToast({ title: '获取设备信息失败', icon: 'none' });
      }
    });
  }
};

// 清除缓存
const clearCache = () => {
  uni.showModal({
    title: '清除缓存',
    content: '确定要清除本地缓存吗？运动记录不会被删除',
    success: (res) => {
      if (res.confirm) {
        // 清除非记录类缓存
        uni.removeStorageSync('checkpoint');
        uni.removeStorageSync('policeFinishTip');
        uni.showToast({ title: '缓存已清除', icon: 'success' });
      }
    }
  });
};

// 关于我们
const gotoAbout = () => {
  uni.showModal({
    title: '关于我们',
    content: '大学生运动健康管理系统 v1.0.0\n专为公安院校定制的跑步打卡工具',
    showCancel: false
  });
};

// 退出登录
const logout = () => {
  uni.showModal({
    title: '退出登录',
    content: '确定要退出当前账号吗？',
    success: (res) => {
      if (res.confirm) {
        uni.clearStorageSync();
        uni.reLaunch({ url: '/pages/login/login' });
      }
    }
  });
};
</script>

<style scoped>
.mine-page {
  min-height: 100vh;
  background-color: #f8f8f8;
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
}

/* 1. 账号主页 */
.user-header {
  background-color: #fff;
  padding: 30rpx 20rpx;
  margin-bottom: 20rpx;
}
.avatar-box {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}
.avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  margin-right: 20rpx;
}
.edit-avatar {
  font-size: 24rpx;
  color: #20C997;
  background-color: #f5f5f5;
  border: none;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
}
.user-info {
  margin-bottom: 20rpx;
}
.username {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  display: block;
}
.user-desc {
  font-size: 26rpx;
  color: #666;
  display: block;
  margin-top: 5rpx;
}
.user-stats {
  display: flex;
  justify-content: space-around;
  padding-top: 20rpx;
  border-top: 1px dashed #eee;
}
.stats-item {
  text-align: center;
}
.stats-num {
  font-size: 32rpx;
  font-weight: bold;
  color: #20C997;
  display: block;
}
.stats-text {
  font-size: 24rpx;
  color: #666;
  margin-top: 5rpx;
  display: block;
}

/* 2. 本周跑步 */
.week-run-card {
  background-color: #fff;
  margin: 0 20rpx 20rpx;
  padding: 20rpx;
  border-radius: 12rpx;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}
.card-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
}
.date-range {
  font-size: 24rpx;
  color: #999;
}
.week-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20rpx;
}
.week-item {
  text-align: center;
}
.week-num {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  display: block;
}
.week-text {
  font-size: 24rpx;
  color: #666;
  margin-top: 5rpx;
}
.progress-box {
  margin-top: 20rpx;
}
.progress-title {
  font-size: 26rpx;
  color: #666;
  display: block;
  margin-bottom: 10rpx;
}
.progress-bar {
  width: 100%;
  height: 10rpx;
  background-color: #f5f5f5;
  border-radius: 5rpx;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background-color: #20C997;
  border-radius: 5rpx;
  transition: width 0.5s;
}

/* 3. 运动记录 */
.record-card {
  background-color: #fff;
  margin: 0 20rpx 20rpx;
  padding: 20rpx;
  border-radius: 12rpx;
}
.view-all {
  font-size: 24rpx;
  color: #20C997;
  background: none;
  border: none;
  padding: 0;
}
.record-list {
  margin-top: 10rpx;
}
.record-item {
  display: flex;
  align-items: center;
  padding: 15rpx 0;
  border-bottom: 1px solid #f5f5f5;
}
.record-type {
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  margin-right: 15rpx;
}
.type-text {
  font-size: 24rpx;
  color: #333;
}
.record-info {
  flex: 1;
}
.record-date {
  font-size: 26rpx;
  color: #333;
  display: block;
}
.record-data {
  font-size: 24rpx;
  color: #999;
  margin-top: 5rpx;
  display: block;
}
.record-status {
  margin-left: 10rpx;
}
.status-text {
  font-size: 24rpx;
}
.empty-record {
  text-align: center;
  padding: 40rpx 0;
}
.empty-img {
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 20rpx;
}
.empty-text {
  font-size: 26rpx;
  color: #999;
}

/* 4. 设置中心 */
.setting-card {
  background-color: #fff;
  margin: 0 20rpx;
  border-radius: 12rpx;
}
.setting-item {
  display: flex;
  align-items: center;
  padding: 20rpx;
  border-bottom: 1px solid #f5f5f5;
}
.setting-item:last-child {
  border-bottom: none;
}
.setting-icon {
  font-size: 28rpx;
  margin-right: 15rpx;
}
.setting-text {
  font-size: 28rpx;
  color: #333;
  flex: 1;
}
.setting-desc {
  font-size: 24rpx;
  color: #999;
  margin-right: 10rpx;
}
.arrow {
  font-size: 24rpx;
  color: #ccc;
}
.logout .setting-text {
  color: #d81e06;
}
</style>
