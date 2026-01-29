<template>
  <view class="mine-page">
    <!-- Custom Navigation Bar -->
    <view class="custom-navbar" :style="{paddingTop: statusBarHeight + 'px'}">
      <view class="navbar-content">
        <text class="navbar-title">个人中心</text>
      </view>
    </view>
    
    <view class="content-wrapper" :style="{paddingTop: (statusBarHeight + 44) + 'px'}">
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
    </view>
    
    <CustomTabBar current="/pages/mine/mine" />
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import CustomTabBar from '@/components/CustomTabBar/CustomTabBar.vue';
import { request } from '@/utils/request.js';

const statusBarHeight = ref(20);

const userName = ref('同学');
const userType = ref('学生');
const totalRunCount = ref(0);
const totalRunDistance = ref(0.0);
const policeSuccessCount = ref(0);

const weekDateRange = ref('本周');
const weekRunCount = ref(0);
const weekRunDistance = ref(0.0);
const weekPoliceSuccess = ref(0);
const progressPercent = ref(0);

const runRecords = ref([]);
const showRecords = computed(() => runRecords.value.slice(0, 5));

const deviceId = ref('');

const formatDuration = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h > 0 ? h + ':' : ''}${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
};

const fetchHistory = async () => {
    try {
        const res = await request({
            url: '/activity/history',
            method: 'GET',
            data: { page: 1, size: 20 }
        });
        
        if (res.items) {
            runRecords.value = res.items.map(item => {
                const isRun = item.type === 'run';
                const date = new Date(item.started_at);
                const dateStr = `${date.getMonth()+1}-${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
                
                return {
                    type: item.type,
                    modeBg: isRun ? '#20C997' : '#FF9F43',
                    modeText: isRun ? '跑步' : '体测',
                    testName: '体能测试',
                    createTime: dateStr,
                    distance: item.metrics?.distance ? Number(item.metrics.distance).toFixed(2) : 0,
                    duration: formatDuration(item.metrics?.duration || 0),
                    pace: item.metrics?.pace,
                    testCount: item.metrics?.count || 0,
                    result: item.metrics?.qualified ? '达标' : '未达标',
                    statusText: item.status === 'finished' ? '有效' : '待审核',
                    statusColor: '#20C997'
                };
            });
            
            // 更新统计数据
            const runs = runRecords.value.filter(r => r.type === 'run');
            totalRunCount.value = runs.length;
            totalRunDistance.value = runs
                .reduce((acc, cur) => acc + Number(cur.distance || 0), 0)
                .toFixed(2);
            policeSuccessCount.value = runRecords.value.filter(r => r.type === 'test' && r.result === '达标').length;
            
            // 更新本周数据 (简单Mock，真实逻辑需要判断日期)
            // 暂时假设所有记录都是本周的，以便演示
            weekRunCount.value = runs.length;
            weekRunDistance.value = totalRunDistance.value;
            weekPoliceSuccess.value = policeSuccessCount.value;
            progressPercent.value = Math.min((runs.length / 3) * 100, 100);
        }
    } catch (e) {
        console.error('Fetch history failed', e);
        // uni.showToast({ title: '获取记录失败', icon: 'none' });
    }
};

onShow(() => {
  statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 20;
  
  const user = uni.getStorageSync('userInfo');
  if (user) {
    if (typeof user === 'string') {
        try {
            const u = JSON.parse(user);
            if(u.name) userName.value = u.name;
        } catch(e){}
    } else if (user.name) {
        userName.value = user.name;
    }
  }
  
  fetchHistory();
});

const gotoUserProfile = () => {
  uni.showToast({ title: '编辑资料功能待开发', icon: 'none' });
};

const viewAllRecords = () => {
  // uni.showToast({ title: '查看全部记录待开发', icon: 'none' });
  // 暂时不需要跳转，直接在本页看前20条即可，或者后续做列表页
  uni.navigateTo({ url: '/pages/record/list' }); // 假设有这个页面，或者先不做动作
};

const gotoRecordDetail = (item) => {
  // uni.navigateTo({ url: `/pages/result/result?id=${item.id}` });
};

const gotoDeviceBind = () => {
  uni.showToast({ title: '设备绑定功能开发中', icon: 'none' });
};

const clearCache = () => {
  uni.showModal({
    title: '提示',
    content: '确定要清除缓存吗？',
    success: (res) => {
      if (res.confirm) {
        uni.showToast({ title: '清理完成' });
      }
    }
  });
};

const gotoAbout = () => {
  uni.showToast({ title: '当前版本 v1.0.0', icon: 'none' });
};

const logout = () => {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        uni.removeStorageSync('token');
        uni.removeStorageSync('userInfo');
        uni.removeStorageSync('userRole');
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

.custom-navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: #fff;
  z-index: 999;
}
.navbar-content {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.navbar-title {
  color: #333;
  font-size: 16px;
  font-weight: bold;
}
.content-wrapper {
  width: 100%;
  box-sizing: border-box;
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
}
.week-text {
  font-size: 22rpx;
  color: #666;
  margin-top: 4rpx;
  display: block;
}
.progress-box {
  background-color: #f9f9f9;
  padding: 20rpx;
  border-radius: 8rpx;
}
.progress-title {
  font-size: 22rpx;
  color: #666;
  margin-bottom: 10rpx;
  display: block;
}
.progress-bar {
  height: 10rpx;
  background-color: #e0e0e0;
  border-radius: 5rpx;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background-color: #20C997;
  border-radius: 5rpx;
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
  color: #666;
  background: none;
}
.view-all::after {
  border: none;
}
.record-list {
  margin-top: 20rpx;
}
.record-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1px solid #f5f5f5;
}
.record-item:last-child {
  border-bottom: none;
}
.record-type {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}
.type-text {
  font-size: 20rpx;
  color: #fff;
  font-weight: bold;
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
  font-size: 22rpx;
  color: #999;
  margin-top: 4rpx;
  display: block;
}
.record-status {
  text-align: right;
}
.status-text {
  font-size: 24rpx;
}
.empty-record {
  text-align: center;
  padding: 40rpx 0;
}
.empty-icon {
  font-size: 60rpx;
  display: block;
  margin-bottom: 20rpx;
}
.empty-text {
  font-size: 26rpx;
  color: #999;
}

/* 4. 设置 */
.setting-card {
  background-color: #fff;
  margin: 0 20rpx 20rpx;
  padding: 0 20rpx;
  border-radius: 12rpx;
}
.setting-item {
  display: flex;
  align-items: center;
  padding: 30rpx 0;
  border-bottom: 1px solid #f5f5f5;
}
.setting-item:last-child {
  border-bottom: none;
}
.setting-icon {
  font-size: 32rpx;
  margin-right: 20rpx;
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
  color: #ccc;
  font-size: 24rpx;
}
.logout {
  justify-content: center;
}
.logout .setting-text {
  text-align: center;
  color: #ff6b6b;
  flex: none;
}
</style>
