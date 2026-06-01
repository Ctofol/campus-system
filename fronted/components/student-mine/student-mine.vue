<template>
  <view class="mine-page">
    <page-tab-header title="个人中心" theme="brand" />

    <view class="content-wrapper page-tab-body">
      <!-- 1. 账号主页（顶部） -->
      <view class="user-header">
        <view class="avatar-row">
          <image class="avatar" :src="avatarUrl" mode="aspectFill"></image>
          <view class="user-info">
            <text class="username">{{userName}}</text>
            <text class="user-signature" v-if="userSignature">{{ userSignature }}</text>
            <text class="user-desc">{{ className ? className + ' · ' : '校园运动打卡 · ' }}{{userType}}</text>
          </view>
        </view>
        <view class="edit-profile-row">
          <view class="edit-profile-btn" @click="gotoUserProfile">编辑资料</view>
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
      <view class="week-run-card page-card">
        <view class="card-header">
          <view class="header-left">
            <text class="page-section-title page-section-title--compact">本周跑步</text>
            <text class="target-tag">目标 {{weeklyTarget}} 次</text>
          </view>
          <text class="date-range">{{weekDateRange}}</text>
        </view>
        <view class="week-stats">
          <view class="week-item">
            <text class="week-num">{{weekRunCount}}</text>
            <text class="week-text">跑步次数</text>
          </view>
          <view class="week-item">
            <text class="week-num">{{formatDistance(weekRunDistance)}}</text>
            <text class="week-text">总距离(km)</text>
          </view>
          <view class="week-item">
            <text class="week-num">{{weekPoliceSuccess}}</text>
            <text class="week-text">体测达标</text>
          </view>
        </view>
        <!-- 本周目标进度条 -->
        <view class="progress-box">
          <view class="progress-header">
            <text class="progress-info">已完成 {{weekRunCount}}/{{weeklyTarget}}</text>
            <text class="progress-percent">{{Math.round(progressPercent)}}%</text>
          </view>
          <view class="progress-bar">
            <view class="progress-fill" :style="{width: progressPercent + '%'}"></view>
          </view>
        </view>
      </view>

      <!-- 任务跑步记录（与阳光跑区分） -->
      <view class="task-run-card page-card" v-if="taskRunPreview.length > 0">
        <view class="card-header">
          <text class="page-section-title page-section-title--compact">任务跑步</text>
          <text class="view-all" @click="gotoTaskRuns">查看全部</text>
        </view>
        <view class="task-run-item" v-for="(tr, idx) in taskRunPreview" :key="idx">
          <view class="tr-row">
            <text class="tr-title">{{ tr.task_title || '任务' }}</text>
            <text class="tr-tag" :class="tr.completed_ok ? 'ok' : 'bad'">{{ tr.completed_ok ? '达标' : '未达标' }}</text>
          </view>
          <text class="tr-meta">{{ formatTaskRunTime(tr.started_at) }} · {{ tr.distance_km != null ? Number(tr.distance_km).toFixed(2) : '--' }}km</text>
        </view>
      </view>
      
      <!-- 3. 运动记录列表 -->
      <view class="record-card page-card">
        <view class="card-header">
          <text class="page-section-title page-section-title--compact">运动记录</text>
          <view class="header-actions">
            <text class="history-task-link" @click="gotoHistoryTasks">历史任务</text>
            <button class="view-all" @click="viewAllRecords">查看全部</button>
          </view>
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
        <view class="setting-item" @click="gotoNotifications">
          <text class="setting-icon">🔔</text>
          <text class="setting-text">我的通知</text>
          <text class="setting-desc">{{ unreadNotifyCount > 0 ? `${unreadNotifyCount} 条未读` : '审批与任务提醒' }}</text>
          <view v-if="unreadNotifyCount > 0" class="notify-badge">{{ unreadNotifyCount > 99 ? '99+' : unreadNotifyCount }}</view>
          <text class="arrow">＞</text>
        </view>
        <view class="setting-item" @click="gotoHealthRequest">
          <text class="setting-icon">🩺</text>
          <text class="setting-text">健康报备</text>
          <text class="setting-desc">请假/伤病申请</text>
          <text class="arrow">＞</text>
        </view>
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
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { request, getStudentTaskRunHistory, avatarImageSrc } from '@/utils/request.js';
import { mapRecordStatus, isValidSunshineRun } from '@/utils/activity-record.js';

const avatarUrl = ref('/static/avatar.png');

const userName = ref('同学');
const userSignature = ref('');
const userType = ref('学生');
const className = ref('');
const totalRunCount = ref(0);
const totalRunDistance = ref(0.0);
const policeSuccessCount = ref(0);

const weekDateRange = ref('本周');
const weeklyTarget = ref(3);
const weekRunCount = ref(0);
const weekRunDistance = ref(0.0);
const weekPoliceSuccess = ref(0);
const progressPercent = ref(0);

const runRecords = ref([]);
const showRecords = computed(() => runRecords.value.slice(0, 5));
const taskRunPreview = ref([]);

const deviceId = ref('');
const unreadNotifyCount = ref(0);

const formatDistance = (val) => {
    const num = Number(val);
    if (isNaN(num)) return '0.00';
    return num.toFixed(2);
};

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
                const status = mapRecordStatus(item);
                
                return {
                    id: item.id,
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
                    statusText: status.statusText,
                    statusColor: status.statusColor,
                    isValid: item.is_valid === true,
                    isTask: item.source === 'task' || !!item.task_id
                };
            }).filter(item => !item.isTask)
            
            const validRuns = res.items.filter(isValidSunshineRun);
            totalRunCount.value = validRuns.length;
            totalRunDistance.value = validRuns
                .reduce((acc, cur) => acc + Number(cur.metrics?.distance || 0), 0)
                .toFixed(2);
            policeSuccessCount.value = runRecords.value.filter(r => r.type === 'test' && r.result === '达标').length;
            
            const now = new Date();
            const startOfWeek = new Date(now);
            startOfWeek.setDate(now.getDate() - now.getDay());
            startOfWeek.setHours(0, 0, 0, 0);
            
            const weekRuns = res.items.filter(item => {
                const itemDate = new Date(item.started_at);
                return isValidSunshineRun(item) && itemDate >= startOfWeek;
            });
            
            weekRunCount.value = weekRuns.length;
            weekRunDistance.value = weekRuns
                .reduce((acc, cur) => acc + Number(cur.metrics?.distance || 0), 0)
                .toFixed(2);
            weekPoliceSuccess.value = res.items.filter(item => {
                const itemDate = new Date(item.started_at);
                return item.type === 'test' && 
                       item.metrics?.qualified && 
                       itemDate >= startOfWeek;
            }).length;
            
            progressPercent.value = Math.min((weekRunCount.value / weeklyTarget.value) * 100, 100);
        }
    } catch (e) {
        console.error('Fetch history failed', e);
        // uni.showToast({ title: '获取记录失败', icon: 'none' });
    }
};

const formatTaskRunTime = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`;
};

const fetchTaskRuns = async () => {
  try {
    const res = await getStudentTaskRunHistory({ page: 1, size: 5 });
    taskRunPreview.value = res.items || [];
  } catch (e) {
    console.error(e);
    taskRunPreview.value = [];
  }
};

const fetchUserProfile = async () => {
    try {
        const res = await request({
            url: '/users/profile',
            method: 'GET'
        });
        if (res) {
        if (res.name) userName.value = res.name;
        if (res.class_name) className.value = res.class_name;
        userSignature.value = (res.signature || '').trim();
        avatarUrl.value = res.avatar_url ? avatarImageSrc(res.avatar_url) : '/static/avatar.png';
        
        // Update storage
            let currentUser = uni.getStorageSync('userInfo');
            if (typeof currentUser === 'string') {
                try { currentUser = JSON.parse(currentUser); } catch(e) { currentUser = {}; }
            }
            const newUser = { ...currentUser, ...res };
            uni.setStorageSync('userInfo', newUser);
        }
    } catch (e) {
        console.error('Fetch profile failed', e);
    }
};

// 页面显示逻辑
const loadUnreadNotifyCount = async () => {
  try {
    const res = await request('/student/notifications/unread-count');
    unreadNotifyCount.value = Number(res?.count) || 0;
  } catch (e) {
    unreadNotifyCount.value = 0;
  }
};

const onPageShow = () => {
  loadUnreadNotifyCount();
  const user = uni.getStorageSync('userInfo');
  if (user) {
    let u = user;
    if (typeof user === 'string') {
        try {
            u = JSON.parse(user);
        } catch(e){}
    }
    
    if (u) {
        if(u.name) userName.value = u.name;
        if(u.class_name) className.value = u.class_name;
        userSignature.value = (u.signature || '').trim();
        avatarUrl.value = u.avatar_url ? avatarImageSrc(u.avatar_url) : '/static/avatar.png';
    }
  }
  
  fetchHistory();
  fetchTaskRuns();
  fetchUserProfile();
};

onMounted(() => {
    onPageShow();
});

defineExpose({
    onPageShow
});

const gotoUserProfile = () => {
  uni.navigateTo({ url: '/pages/mine/edit-profile/edit-profile' });
};

const gotoNotifications = () => {
  uni.navigateTo({ url: '/pages/student/notifications/list' });
};

const gotoHealthRequest = () => {
  uni.navigateTo({ url: '/pages/health/request' });
};

const gotoHistoryTasks = () => {
  uni.navigateTo({ url: '/pages/mine/history-tasks/history-tasks' });
};

const gotoTaskRuns = () => {
  uni.navigateTo({ url: '/pages/student/task-runs/task-runs' });
};

const viewAllRecords = () => {
  uni.navigateTo({ url: '/pages/history/history' });
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
.content-wrapper {
  width: 100%;
  box-sizing: border-box;
  padding-bottom: 200rpx;
}

/* 1. 账号主页 */
.user-header {
  background-color: #fff;
  padding: 40rpx 30rpx;
  margin-bottom: 20rpx;
}
.avatar-row {
  display: flex;
  align-items: center;
  gap: 24rpx;
  margin-bottom: 24rpx;
}
.avatar {
  width: 140rpx;
  height: 140rpx;
  flex-shrink: 0;
  border-radius: 50%;
  border: 4rpx solid #fff;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
}
.edit-profile-row {
  display: flex;
  justify-content: center;
  margin-bottom: 32rpx;
}
.edit-profile-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 200rpx;
  padding: 14rpx 40rpx;
  font-size: 26rpx;
  color: #20c997;
  background-color: rgba(32, 201, 151, 0.1);
  border: 1rpx solid #20c997;
  border-radius: 32rpx;
  box-sizing: border-box;
}
.user-info {
  flex: 1;
  min-width: 0;
}
.username {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
}
.user-signature {
  display: block;
  font-size: 26rpx;
  color: #20c997;
  line-height: 1.45;
  margin-bottom: 6rpx;
  max-width: 420rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  padding-top: 30rpx;
  border-top: 1px solid #f5f5f5;
}
.stats-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.stats-num {
  font-size: 36rpx;
  font-weight: bold;
  color: #20C997;
  display: block;
  font-family: DINAlternate-Bold, sans-serif;
}
.stats-text {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
  display: block;
}

/* 2. 本周跑步 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12rpx;
}
.target-tag {
  font-size: 20rpx;
  color: #fff;
  background: #FF9F43;
  padding: 2rpx 10rpx;
  border-radius: 8rpx;
}
.date-range {
  font-size: 24rpx;
  color: #999;
}
.week-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 30rpx;
}
.week-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.week-num {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  font-family: DINAlternate-Bold, sans-serif;
}
.week-text {
  font-size: 24rpx;
  color: #888;
  margin-top: 8rpx;
}
.progress-box {
  background-color: #f8f9fa;
  padding: 20rpx;
  border-radius: 12rpx;
}
.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12rpx;
  font-size: 24rpx;
  color: #666;
}
.progress-info {
  font-weight: 500;
}
.progress-percent {
  color: #20C997;
  font-weight: bold;
}
.progress-bar {
  height: 12rpx;
  background-color: #e9ecef;
  border-radius: 6rpx;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #20C997, #4ECDC4);
  border-radius: 6rpx;
  transition: width 0.5s ease;
}

.task-run-card .view-all {
  font-size: 24rpx;
  color: #20c997;
}
.task-run-item {
  padding: 16rpx 0;
  border-bottom: 1px solid #f0f0f0;
}
.task-run-item:last-child {
  border-bottom: none;
}
.tr-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8rpx;
}
.tr-title {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
  flex: 1;
  padding-right: 12rpx;
}
.tr-tag {
  font-size: 22rpx;
  padding: 4rpx 10rpx;
  border-radius: 8rpx;
}
.tr-tag.ok {
  background: #e6fff6;
  color: #20c997;
}
.tr-tag.bad {
  background: #fff1f0;
  color: #ff4d4f;
}
.tr-meta {
  font-size: 24rpx;
  color: #999;
}

.header-actions {
  display: flex;
  align-items: center;
}
.history-task-link {
  font-size: 24rpx;
  color: #666;
  margin-right: 20rpx;
  padding: 6rpx 16rpx;
  background: #f0f0f0;
  border-radius: 20rpx;
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
.notify-badge {
  min-width: 36rpx;
  height: 36rpx;
  line-height: 36rpx;
  padding: 0 10rpx;
  margin-right: 8rpx;
  border-radius: 18rpx;
  background: #ff4d4f;
  color: #fff;
  font-size: 22rpx;
  text-align: center;
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
