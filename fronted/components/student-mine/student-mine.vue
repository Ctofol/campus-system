<template>
  <view class="mine-page">
    <!-- Immersive Header -->
    <view class="profile-header" :style="{ paddingTop: statusBarHeight + 'px', backgroundImage: headerBgUrl ? 'url(' + headerBgUrl + ')' : '' }">
      <view class="header-actions">
        <view class="header-action header-action--notif" @tap="gotoNotifications">
          <image class="action-icon" src="/static/通知图标.png" mode="aspectFit" />
          <view v-if="unreadNotifyCount > 0" class="notif-dot" />
        </view>
      </view>
      <view class="profile-content">
        <view class="avatar-wrap" @tap="gotoUserProfile">
          <image class="avatar" :src="avatarUrl" mode="aspectFill" />
        </view>
        <view class="profile-info" @tap="gotoUserProfile">
          <view class="name-row">
            <text class="name">{{ userName }}</text>
            <text class="edit-btn">✎</text>
          </view>
          <view class="desc-row">
            <text class="desc">{{ userSignature || '跑步爱好者' }}</text>
            <view class="streak-badge">
              <text>已连续运动 {{ totalRunCount }} 次</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- Main Content -->
    <view class="main-content">
      <!-- My Data Grid -->
      <view class="data-card">
        <view class="card-header">
          <text class="card-title">我的数据</text>
          <text class="card-more" @tap="viewAllRecords">查看全部 ›</text>
        </view>
        <view class="data-grid">
          <view class="data-item">
            <image class="data-icon" src="/static/主页里程图标.png" mode="aspectFit" />
            <text class="data-val">{{ totalRunDistance }}</text>
            <text class="data-label">总公里</text>
          </view>
          <view class="data-item">
            <image class="data-icon" src="/static/主页时长图标.png" mode="aspectFit" />
            <text class="data-val">{{ totalDuration }}</text>
            <text class="data-label">总时长</text>
          </view>
          <view class="data-item">
            <image class="data-icon" src="/static/主页卡路里图标.png" mode="aspectFit" />
            <text class="data-val">{{ totalCalories }}</text>
            <text class="data-label">总消耗(千卡)</text>
          </view>
          <view class="data-item">
            <image class="data-icon" src="/static/奖杯图标.png" mode="aspectFit" />
            <text class="data-val">{{ badgeCount }}</text>
            <text class="data-label">获得勋章</text>
          </view>
        </view>
      </view>

      <!-- Weekly Progress -->
      <view class="data-card" v-if="weekRunCount > 0">
        <view class="card-header">
          <text class="card-title">本周跑步</text>
          <text class="card-more">目标 {{ weeklyTarget }} 次</text>
        </view>
        <view class="progress-box">
          <view class="progress-header">
            <text class="progress-info">已完成 {{ weekRunCount }}/{{ weeklyTarget }}</text>
            <text class="progress-pct">{{ Math.round(progressPercent) }}%</text>
          </view>
          <view class="progress-bar">
            <view class="progress-fill" :style="{ width: progressPercent + '%' }" />
          </view>
        </view>
      </view>

      <!-- Common Functions -->
      <view class="data-card">
        <text class="card-title" style="margin-bottom: 24rpx;">常用功能</text>
        <view class="func-grid">
          <view class="func-item" @tap="goMyCourses">
            <image class="func-icon" src="/static/主页课程图标.png" mode="aspectFit" />
            <text class="func-label">我的课程</text>
          </view>
          <view class="func-item" @tap="goMyRoute">
            <image class="func-icon" src="/static/主页户外跑图标.png" mode="aspectFit" />
            <text class="func-label">我的路线</text>
          </view>
          <view class="func-item" @tap="goRunGroup">
            <image class="func-icon" src="/static/主页跑团图标.png" mode="aspectFit" />
            <text class="func-label">我的跑团</text>
          </view>
          <view class="func-item" @tap="goMyData">
            <image class="func-icon" src="/static/数据图标.png" mode="aspectFit" />
            <text class="func-label">我的数据</text>
          </view>
          <view class="func-item" @tap="gotoHealthRequest">
            <image class="func-icon" src="/static/请假申请图标.png" mode="aspectFit" />
            <text class="func-label">请假申请</text>
          </view>
          <view class="func-item" @tap="gotoNotifications">
            <image class="func-icon" src="/static/通知图标.png" mode="aspectFit" />
            <text class="func-label">我的通知</text>
          </view>
        </view>
      </view>

      <!-- Settings List -->
      <view class="setting-list">
        <view class="setting-row" @tap="gotoHelp">
          <view class="setting-left">
            <image class="setting-icon" src="/static/消息图标.png" mode="aspectFit" />
            <text class="setting-label">帮助与反馈</text>
          </view>
          <text class="setting-arrow">›</text>
        </view>
        <view class="setting-row" @tap="gotoDeviceBind">
          <view class="setting-left">
            <image class="setting-icon" src="/static/主页GO图标.png" mode="aspectFit" />
            <text class="setting-label">设备绑定（防代跑）</text>
          </view>
          <text class="setting-arrow">›</text>
        </view>
        <view class="setting-row" @tap="gotoAbout">
          <view class="setting-left">
            <image class="setting-icon" src='/static/about-me.png' mode="aspectFit" />
            <text class="setting-label">关于我们</text>
          </view>
          <text class="setting-arrow">›</text>
        </view>
        <view class="setting-row logout-row" @tap="logout">
          <view class="setting-left">
            <image class="setting-icon" src="/static/叉号图标.png" mode="aspectFit" />
            <text class="setting-label">退出登录</text>
          </view>
          <text class="setting-arrow">›</text>
        </view>
      </view>

      <view style="height: 48rpx;" />
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { request, getStudentTaskRunHistory, avatarImageSrc, resolveMediaUrl } from '@/utils/request.js';
import { mapRecordStatus, isValidSunshineRun } from '@/utils/activity-record.js';

const statusBarHeight = ref(uni.getSystemInfoSync().statusBarHeight || 20);
const currentTime = ref('');
const avatarUrl = ref('/static/default-avatar.svg');

const userName = ref('同学');
const userSignature = ref('');
const userType = ref('学生');
const className = ref('');
const totalRunCount = ref(0);
const totalRunDistance = ref(0.0);
const totalDuration = ref('--');
const totalCalories = ref('--');
const badgeCount = ref(0);
const policeSuccessCount = ref(0);

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
const headerBgUrl = ref('');

const updateTime = () => {
  const now = new Date();
  currentTime.value = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
};

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
    const res = await request({ url: '/activity/history', method: 'GET', data: { page: 1, size: 20 } });
    if (res.items) {
      runRecords.value = res.items.map(item => {
        const isRun = item.type === 'run';
        const date = new Date(item.started_at);
        const dateStr = `${date.getMonth()+1}-${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
        const status = mapRecordStatus(item);
        return {
          id: item.id, type: item.type,
          modeBg: isRun ? '#20C997' : '#FF9F43',
          modeText: isRun ? '跑步' : '体测',
          testName: '体能测试', createTime: dateStr,
          distance: item.metrics?.distance ? Number(item.metrics.distance).toFixed(2) : 0,
          duration: formatDuration(item.metrics?.duration || 0),
          pace: item.metrics?.pace,
          testCount: item.metrics?.count || 0,
          result: item.metrics?.qualified ? '达标' : '未达标',
          statusText: status.statusText, statusColor: status.statusColor,
          isValid: item.is_valid === true,
          isTask: item.source === 'task' || !!item.task_id
        };
      }).filter(item => !item.isTask);

      const validRuns = res.items.filter(isValidSunshineRun);
      totalRunCount.value = validRuns.length;
      totalRunDistance.value = validRuns.reduce((acc, cur) => acc + Number(cur.metrics?.distance || 0), 0).toFixed(2);
      policeSuccessCount.value = runRecords.value.filter(r => r.type === 'test' && r.result === '达标').length;
      badgeCount.value = Math.max(totalRunCount.value, policeSuccessCount.value);

      let totalSec = 0;
      validRuns.forEach(r => { totalSec += Number(r.metrics?.duration || 0); });
      totalDuration.value = formatDuration(totalSec);
      totalCalories.value = validRuns.reduce((acc, cur) => acc + Number(cur.metrics?.calories || 0), 0).toFixed(0);

      const now = new Date();
      const startOfWeek = new Date(now);
      startOfWeek.setDate(now.getDate() - now.getDay());
      startOfWeek.setHours(0, 0, 0, 0);
      const weekRuns = res.items.filter(item => {
        const itemDate = new Date(item.started_at);
        return isValidSunshineRun(item) && itemDate >= startOfWeek;
      });
      weekRunCount.value = weekRuns.length;
      weekRunDistance.value = weekRuns.reduce((acc, cur) => acc + Number(cur.metrics?.distance || 0), 0).toFixed(2);
      weekPoliceSuccess.value = res.items.filter(item => {
        const itemDate = new Date(item.started_at);
        return item.type === 'test' && item.metrics?.qualified && itemDate >= startOfWeek;
      }).length;
      progressPercent.value = Math.min((weekRunCount.value / weeklyTarget.value) * 100, 100);
    }
  } catch (e) { console.error('Fetch history failed', e); }
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
  } catch (e) { taskRunPreview.value = []; }
};

const fetchUserProfile = async () => {
  try {
    const res = await request({ url: '/users/profile', method: 'GET' });
    if (res) {
      if (res.name) userName.value = res.name;
      if (res.class_name) className.value = res.class_name;
      userSignature.value = (res.signature || '').trim();
      avatarUrl.value = res.avatar_url ? avatarImageSrc(res.avatar_url) : '/static/default-avatar.svg';
      if (res.header_bg_url) headerBgUrl.value = resolveMediaUrl(res.header_bg_url);
      let currentUser = uni.getStorageSync('userInfo');
      if (typeof currentUser === 'string') { try { currentUser = JSON.parse(currentUser); } catch(e) { currentUser = {}; } }
      uni.setStorageSync('userInfo', { ...currentUser, ...res });
    }
  } catch (e) { console.error('Fetch profile failed', e); }
};

const loadUnreadNotifyCount = async () => {
  try {
    const res = await request('/student/notifications/unread-count');
    unreadNotifyCount.value = Number(res?.count) || 0;
  } catch (e) { unreadNotifyCount.value = 0; }
};

const onPageShow = () => {
  updateTime();
  const sys = uni.getSystemInfoSync();
  statusBarHeight.value = sys.statusBarHeight || 20;
  loadUnreadNotifyCount();
  const user = uni.getStorageSync('userInfo');
  if (user) {
    let u = user;
    if (typeof user === 'string') { try { u = JSON.parse(user); } catch(e) {} }
    if (u) {
      if (u.name) userName.value = u.name;
      if (u.class_name) className.value = u.class_name;
      userSignature.value = (u.signature || '').trim();
      avatarUrl.value = u.avatar_url ? avatarImageSrc(u.avatar_url) : '/static/default-avatar.svg';
      if (u.header_bg_url) headerBgUrl.value = resolveMediaUrl(u.header_bg_url);
    }
  }
  fetchHistory();
  fetchTaskRuns();
  fetchUserProfile();
};

onMounted(() => { onPageShow(); });

const viewAllRecords = () => uni.navigateTo({ url: '/pages/history/history' });
const gotoUserProfile = () => uni.navigateTo({ url: '/pages/mine/edit-profile/edit-profile' });
const gotoNotifications = () => uni.navigateTo({ url: '/pages/student/notifications/list' });
const gotoHealthRequest = () => uni.navigateTo({ url: '/pages/health/request' });
const goMyCourses = () => uni.switchTab({ url: '/pages/tab/learn' });
const goRunGroup = () => uni.navigateTo({ url: '/pages/run-group/discover' });
const gotoDeviceBind = () => uni.showToast({ title: '功能开发中', icon: 'none' });
const gotoAbout = () => uni.showModal({ title: '关于我们', content: '校园运动打卡系统 v1.0.0', showCancel: false });
const gotoHelp = () => uni.showModal({ title: '帮助与反馈', content: '如有问题请联系管理员', showCancel: false });
const goMyPlan = () => uni.switchTab({ url: '/pages/tab/function' });
const goMyRoute = () => uni.navigateTo({ url: '/pages/sunshine/detail' });
const goMyFavorites = () => uni.showToast({ title: '功能开发中', icon: 'none' });
const goMyData = () => uni.navigateTo({ url: '/pages/history/history' });

const clearCache = () => {
  uni.showModal({
    title: '提示',
    content: '确定要清除缓存吗？',
    success: (res) => {
      if (res.confirm) {
        uni.clearStorageSync();
        uni.showToast({ title: '已清除', icon: 'success' });
        setTimeout(() => { uni.reLaunch({ url: '/pages/login/login' }); }, 1000);
      }
    }
  });
};

const logout = () => {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        uni.removeStorageSync('token');
        uni.removeStorageSync('userInfo');
        uni.reLaunch({ url: '/pages/login/login' });
      }
    }
  });
};

defineExpose({ onPageShow });
</script>

<style scoped>
.mine-page { min-height: 100vh; background: #F7F8FA; }

/* === Immersive Header === */
.profile-header {
  background: linear-gradient(180deg, #33C9AB 0%, #F7F8FA 100%);
  height: 380rpx; position: relative; overflow: hidden;
  background-size: cover; background-position: center;
}
.header-actions {
  position: absolute; top: 20rpx; right: 32rpx;
  display: flex; gap: 32rpx; z-index: 10;
}
.header-action {
  position: relative; width: 48rpx; height: 48rpx;
  display: flex; align-items: center; justify-content: center;
}
.action-icon { width: 40rpx; height: 40rpx; }
.notif-dot {
  position: absolute; top: 2rpx; right: 4rpx;
  width: 16rpx; height: 16rpx; border-radius: 50%;
  background: #ff4d4f; border: 2rpx solid #fff;
}

.profile-content {
  display: flex; align-items: center; gap: 24rpx;
  padding: 0 32rpx; position: relative; z-index: 5;
}
.avatar-wrap {
  width: 120rpx; height: 120rpx; border-radius: 50%;
  border: 4rpx solid rgba(255,255,255,0.8);
  overflow: hidden; flex-shrink: 0;
}
.avatar { width: 100%; height: 100%; }
.profile-info { flex: 1; min-width: 0; }
.name-row { display: flex; align-items: center; gap: 12rpx; }
.name { font-size: 40rpx; font-weight: 700; color: #fff; }
.edit-btn { font-size: 28rpx; color: rgba(255,255,255,0.6); }
.desc-row { margin-top: 6rpx; }
.desc { font-size: 24rpx; color: rgba(255,255,255,0.8); display: block; }
.streak-badge {
  margin-top: 10rpx; display: inline-flex;
  background: rgba(255,255,255,0.25); backdrop-filter: blur(10px);
  border-radius: 40rpx; padding: 4rpx 20rpx;
  font-size: 20rpx; color: #fff;
}

/* === Main Content === */
.main-content {
  margin-top: -80rpx; padding: 0 24rpx; position: relative; z-index: 20;
}

/* === Card === */
.data-card {
  background: #fff; border-radius: 24rpx; padding: 32rpx; margin-bottom: 24rpx;
}
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24rpx; }
.card-title { font-size: 30rpx; font-weight: 700; color: #1a2b3c; }
.card-more { font-size: 22rpx; color: #8a9bab; }

/* === Data Grid === */
.data-grid { display: flex; justify-content: space-between; }
.data-item { display: flex; flex-direction: column; align-items: center; flex: 1; }
.data-item + .data-item { border-left: 1rpx solid #f0f0f0; }
.data-icon { width: 56rpx; height: 56rpx; margin-bottom: 8rpx; }
.data-val { font-size: 32rpx; font-weight: 700; color: #191C1E; }
.data-label { font-size: 18rpx; color: #8a9bab; margin-top: 4rpx; }

/* === Progress === */
.progress-box { padding: 0; }
.progress-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12rpx; }
.progress-info { font-size: 24rpx; color: #666; }
.progress-pct { font-size: 24rpx; font-weight: 600; color: #33C9AB; }
.progress-bar { height: 12rpx; background: #E8F8F2; border-radius: 6rpx; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #33C9AB, #20C997); border-radius: 6rpx; transition: width .3s; }

/* === Functions Grid === */
.func-grid { display: flex; flex-wrap: wrap; }
.func-item {
  width: 25%; display: flex; flex-direction: column; align-items: center;
  margin-bottom: 36rpx;
}
.func-icon { width: 72rpx; height: 72rpx; margin-bottom: 12rpx; }
.func-label { font-size: 22rpx; color: #333; }

/* === Settings List === */
.setting-list {
  background: #fff; border-radius: 24rpx; overflow: hidden; margin-bottom: 24rpx;
}
.setting-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 32rpx 32rpx;
}
.setting-row + .setting-row { border-top: 1rpx solid #f5f5f5; }
.setting-row:active { background: #f9f9f9; }
.setting-left { display: flex; align-items: center; gap: 24rpx; }
.setting-icon { width: 52rpx; height: 52rpx; }
.setting-label { font-size: 28rpx; color: #1a2b3c; }
.setting-right { display: flex; align-items: center; gap: 12rpx; }
.setting-version { font-size: 22rpx; color: #8a9bab; }
.setting-arrow { font-size: 28rpx; color: #c0c8d0; }
.logout-row .setting-label { color: #ff4d4f; }
</style>
