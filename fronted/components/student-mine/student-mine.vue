<template>
  <view class="mine-page">
    <!-- Immersive Header -->
    <view class="profile-header" :style="{ paddingTop: statusBarHeight + 'px', backgroundImage: headerBgUrl ? 'url(' + headerBgUrl + ')' : '' }">
      <view class="header-actions">
        <view class="header-action header-action--notif" @tap="gotoNotifications">
          <image class="action-icon" src="/static/icons/icon-notification.svg" mode="aspectFit" />
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
            <view class="edit-btn">
              <image class="edit-btn-img" src="/static/icons/icon-edit-profile.svg" mode="aspectFit" />
            </view>
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
            <image class="data-icon data-icon--distance" src="/static/home-distance.png" mode="aspectFit" />
            <text class="data-val">{{ totalRunDistance }}</text>
            <text class="data-label">总公里</text>
          </view>
          <view class="data-item">
            <image class="data-icon" src="/static/home-duration.png" mode="aspectFit" />
            <text class="data-val">{{ totalDuration }}</text>
            <text class="data-label">总时长</text>
          </view>
          <view class="data-item">
            <image class="data-icon" src="/static/home-calories.png" mode="aspectFit" />
            <text class="data-val">{{ totalCalories }}</text>
            <text class="data-label">总消耗(千卡)</text>
          </view>
          <view class="data-item">
            <image class="data-icon" src="/static/icon-trophy.png" mode="aspectFit" />
            <text class="data-val">{{ medalEarnedCount }}</text>
            <text class="data-label">获得勋章</text>
          </view>
        </view>
      </view>

      <!-- Medal Display -->
      <view class="data-card" @tap="showMedalPopup = true">
        <view class="card-header">
          <text class="card-title">我的勋章</text>
          <text class="card-more">{{ medalEarnedCount }}/{{ medalTotalCount }} ›</text>
        </view>
        <view v-if="medalList.length === 0" class="medal-empty">
          <text class="medal-empty-text">暂无勋章</text>
        </view>
        <view v-else class="medal-row">
          <view
            v-for="m in medalList.slice(0, 6)"
            :key="m.id"
            class="medal-item"
            :class="{ 'medal-item--locked': !m.earned }"
            @tap.stop="openMedalDetail(m)"
          >
            <image class="medal-icon" :src="normalizeMedalIcon(m.icon_path)" mode="aspectFit" />
            <text class="medal-name">{{ m.name }}</text>
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
        <text class="card-title card-title--section">常用功能</text>
        <view class="func-grid">
          <view
            v-for="item in commonFunctions"
            :key="item.key"
            class="func-item"
            @tap="item.action()"
          >
            <view class="func-icon-shell">
              <image
                class="func-icon"
                :class="item.iconClass"
                :style="{ transform: 'scale(' + (item.iconScale || 1) + ')' }"
                :src="item.icon"
                mode="aspectFit"
              />
            </view>
            <text class="func-label">{{ item.label }}</text>
          </view>
        </view>
      </view>

      <!-- Settings List -->
      <view class="setting-list">
        <view class="setting-row" @tap="gotoHelp">
          <view class="setting-left">
            <image class="setting-icon" src="/static/icons/icon-feedback.svg" mode="aspectFit" />
            <text class="setting-label">帮助与反馈</text>
          </view>
          <text class="setting-arrow">›</text>
        </view>
        <view class="setting-row" @tap="gotoDeviceBind">
          <view class="setting-left">
            <image class="setting-icon" src="/static/icons/icon-lock.svg" mode="aspectFit" />
            <text class="setting-label">设备绑定（防代跑）</text>
          </view>
          <text class="setting-arrow">›</text>
        </view>
        <view class="setting-row" @tap="gotoAbout">
          <view class="setting-left">
            <image class="setting-icon" src="/static/icons/icon-about.svg" mode="aspectFit" />
            <text class="setting-label">关于我们</text>
          </view>
          <text class="setting-arrow">›</text>
        </view>
        <view class="setting-row logout-row" @tap="logout">
          <view class="setting-left">
            <image class="setting-icon" src="/static/icons/icon-logout.svg" mode="aspectFit" />
            <text class="setting-label">退出登录</text>
          </view>
          <text class="setting-arrow">›</text>
        </view>
      </view>

      <view style="height: 48rpx;" />
    </view>

    <!-- Medal Detail Popup -->
    <view v-if="showMedalPopup" class="medal-popup-mask" @tap="showMedalPopup = false">
      <view class="medal-popup" @tap.stop>
        <view class="medal-popup-header">
          <text class="medal-popup-title">我的勋章</text>
          <view class="medal-popup-close" @tap="showMedalPopup = false">
            <AppIcon name="close" :size="32" tone="muted" />
          </view>
        </view>
        <view class="medal-popup-body">
          <view v-if="medalList.length === 0" class="medal-popup-empty">
            <text>暂无勋章，继续努力吧！</text>
          </view>
          <view v-else class="medal-popup-grid">
            <view
              v-for="m in medalList"
              :key="m.id"
              class="medal-popup-item"
              :class="{ 'medal-popup-item--locked': !m.earned }"
              @tap="openMedalDetail(m)"
            >
              <image class="medal-popup-icon" :src="normalizeMedalIcon(m.icon_path)" mode="aspectFit" />
              <text class="medal-popup-name">{{ m.name }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- Single Medal Detail Modal -->
    <view v-if="showSingleMedal" class="medal-detail-mask" @tap="showSingleMedal = false">
      <view class="medal-detail-card" @tap.stop>
        <image class="medal-detail-icon" :src="normalizeMedalIcon(currentMedal.icon_path)" mode="aspectFit" />
        <text class="medal-detail-name">{{ currentMedal.name }}</text>
        <text class="medal-detail-desc">{{ currentMedal.description }}</text>
        <view v-if="currentMedal.earned" class="medal-detail-time">
          <text>获得时间：{{ formatMedalTime(currentMedal.earned_at) }}</text>
        </view>
        <view v-else class="medal-detail-locked">
          <text>未解锁</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { request, getStudentTaskRunHistory, avatarImageSrc, resolveMediaUrl } from '@/utils/request.js';
import { mapRecordStatus, isValidSunshineRun } from '@/utils/activity-record.js';
import AppIcon from '@/components/app-icon/app-icon.vue';

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
const medalList = ref([]);
const medalEarnedCount = ref(0);
const medalTotalCount = ref(0);
const showMedalPopup = ref(false);
const showSingleMedal = ref(false);
const currentMedal = ref({});

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
    const res = await request('/notifications/unread-count');
    unreadNotifyCount.value = Number(res?.count) || 0;
  } catch (e) { unreadNotifyCount.value = 0; }
};

const fetchMedals = async () => {
  try {
    const res = await request({ url: '/medals', method: 'GET' });
    if (res.medals) {
      const visibleMedals = res.medals.filter((m) => !String(m.name || m.title || '').includes('体测达人'));
      medalList.value = visibleMedals;
      medalEarnedCount.value = visibleMedals.filter((m) => m.earned).length;
      medalTotalCount.value = visibleMedals.length;
    }
  } catch (e) {
    medalList.value = [];
    medalEarnedCount.value = 0;
    medalTotalCount.value = 0;
    if (e?.statusCode !== 404) console.error('Fetch medals failed', e);
  }
};

const openMedalDetail = (medal) => {
  currentMedal.value = medal;
  showSingleMedal.value = true;
  showMedalPopup.value = false;
};

const formatMedalTime = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
};

const normalizeMedalIcon = (path = '') => {
  const iconMap = {
    '5k距离勋章.png': 'medal-distance-5k.png',
    '10k距离勋章.png': 'medal-distance-10k.png',
    '21k距离勋章.png': 'medal-distance-21k.png',
    '42k距离勋章.png': 'medal-distance-42k.png',
    '打卡100天勋章.png': 'medal-streak-100.png',
    '奖杯图标.png': 'medal-trophy.png'
  };
  const fileName = String(path).split('/').pop();
  return iconMap[fileName]
    ? `/static/medals/${iconMap[fileName]}`
    : (path || '/static/icon-trophy.png');
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
  fetchMedals();
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
const goMyRoute = () => uni.navigateTo({ url: '/pages/mine/routes/routes' });
const goMyFavorites = () => uni.showToast({ title: '功能开发中', icon: 'none' });
const goMyData = () => uni.navigateTo({ url: '/pages/history/history' });

const commonFunctions = [
  { key: 'courses', label: '我的课程', icon: '/static/icons/icon-course.svg', action: goMyCourses },
  { key: 'route', label: '我的路线', icon: '/static/icons/icon-route.svg', action: goMyRoute },
  { key: 'group', label: '我的跑团', icon: '/static/icons/icon-group.svg', action: goRunGroup },
  { key: 'history', label: '训练记录', icon: '/static/icons/icon-training.svg', action: goMyData },
  { key: 'favorite', label: '我的收藏', icon: '/static/icons/icon-favorite.svg', action: goMyFavorites },
  { key: 'leave', label: '请假申请', icon: '/static/icons/icon-leave-request.svg', action: gotoHealthRequest },
  { key: 'notice', label: '我的通知', icon: '/static/icons/icon-notification.svg', action: gotoNotifications }
];

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
  padding: 46rpx 32rpx 0; position: relative; z-index: 5;
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
.edit-btn {
  width: 30rpx;
  height: 30rpx;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
}
.edit-btn-img { width: 28rpx; height: 28rpx; }
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
  margin-top: -58rpx; padding: 0 24rpx; position: relative; z-index: 20;
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
.data-icon--distance { width: 62rpx; height: 62rpx; }
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
.card-title--section { margin-bottom: 24rpx; display: block; }
.func-grid {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -8rpx;
}
.func-item {
  width: 25%;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24rpx;
  padding: 0 8rpx;
  box-sizing: border-box;
}
.func-icon-shell {
  width: 88rpx;
  height: 88rpx;
  border-radius: 24rpx;
  background: linear-gradient(180deg, #F7FBFA 0%, #EEF7F4 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12rpx;
  box-shadow: inset 0 0 0 1rpx rgba(51, 201, 171, 0.08);
}
.func-icon {
  width: 66rpx;
  height: 66rpx;
  transform-origin: center center;
}
.func-icon--route {
  width: 62rpx;
  height: 62rpx;
}
.func-label {
  font-size: 22rpx;
  line-height: 30rpx;
  color: #333;
  text-align: center;
  max-width: 100%;
}

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

/* === Medal Display === */
.medal-row {
  display: flex;
  justify-content: space-between;
  gap: 8rpx;
}
.medal-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 0;
}
.medal-item--locked { opacity: 0.55; }
.medal-icon { width: 92rpx; height: 92rpx; margin-bottom: 8rpx; }
.medal-name { font-size: 20rpx; color: #333; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
.medal-empty { padding: 20rpx 0; text-align: center; }
.medal-empty-text { font-size: 24rpx; color: #999; }

/* === Medal Popup === */
.medal-popup-mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); z-index: 999;
  display: flex; align-items: flex-end; justify-content: center;
}
.medal-popup {
  width: 100%; max-height: 70vh;
  background: #fff; border-radius: 32rpx 32rpx 0 0;
  padding: 32rpx; overflow-y: auto;
}
.medal-popup-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 32rpx;
}
.medal-popup-title { font-size: 34rpx; font-weight: 700; color: #1a2b3c; }
.medal-popup-close {
  width: 40rpx;
  height: 40rpx;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4rpx;
}
.medal-popup-grid {
  display: flex; flex-wrap: wrap; gap: 24rpx;
}
.medal-popup-item {
  width: calc(33.33% - 16rpx);
  display: flex; flex-direction: column; align-items: center;
  padding: 16rpx 0;
}
.medal-popup-item--locked { opacity: 0.55; }
.medal-popup-icon { width: 104rpx; height: 104rpx; margin-bottom: 12rpx; }
.medal-popup-name { font-size: 22rpx; color: #333; text-align: center; }
.medal-popup-empty { padding: 60rpx 0; text-align: center; color: #999; font-size: 26rpx; }

/* === Single Medal Detail === */
.medal-detail-mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6); z-index: 1000;
  display: flex; align-items: center; justify-content: center;
}
.medal-detail-card {
  width: 520rpx; background: #fff; border-radius: 32rpx;
  padding: 48rpx 32rpx; display: flex; flex-direction: column; align-items: center;
}
.medal-detail-icon { width: 188rpx; height: 188rpx; margin-bottom: 24rpx; }
.medal-detail-name { font-size: 36rpx; font-weight: 700; color: #1a2b3c; margin-bottom: 12rpx; }
.medal-detail-desc { font-size: 26rpx; color: #666; text-align: center; margin-bottom: 20rpx; }
.medal-detail-time { font-size: 22rpx; color: #33C9AB; }
.medal-detail-locked { font-size: 22rpx; color: #999; }
</style>
