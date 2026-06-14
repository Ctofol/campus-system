<template>
  <view class="page">
    <view class="navbar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="navbar-back" @tap="goBack"><text class="navbar-back-icon">‹</text></view>
      <text class="navbar-title">打卡日历</text>
      <text class="navbar-right" @tap="showRules">打卡规则</text>
    </view>

    <scroll-view scroll-y class="scroll" :style="{ top: navHeight + 'px' }">
      <!-- 跑团卡片 -->
      <view class="card group-card">
        <view class="group-info">
          <view class="group-avatar"><image class="group-avatar-img" src="/static/主页户外跑图标.png" mode="aspectFit" /></view>
          <view class="group-detail">
            <view class="group-name-row">
              <text class="group-name">{{ groupName }}</text>
              <text v-if="isGroupLeader" class="group-tag">团长</text>
            </view>
            <text class="group-desc">{{ groupDesc }}</text>
          </view>
          <view class="group-switch" @tap="switchGroup">
            <text>⇄ 切换跑团</text>
          </view>
        </view>
        <view class="group-stats">
          <view class="gs"><text class="gsv">{{ calData.month_count || 0 }}</text><text class="gsl">本月打卡</text></view>
          <view class="gs"><text class="gsv">{{ calData.streak || 0 }}</text><text class="gsl">连续打卡</text></view>
          <view class="gs"><text class="gsv">{{ calData.total_days || 0 }}</text><text class="gsl">累计打卡</text></view>
          <view class="gs"><text class="gsv">{{ rank || '--' }}</text><text class="gsl">排名</text></view>
        </view>
      </view>

      <!-- 日历 -->
      <view class="card cal-card">
        <view class="cal-header">
          <text class="cal-arrow" @tap="prevMonth">‹</text>
          <text class="cal-month">{{ currentYear }}年{{ currentMonth }}月</text>
          <text class="cal-arrow" :class="{ 'cal-arrow--disabled': !canGoNext }" @tap="nextMonth">›</text>
        </view>
        <view class="cal-weekdays">
          <text v-for="d in ['日','一','二','三','四','五','六']" :key="d" class="cal-wd">{{ d }}</text>
        </view>
        <view class="cal-grid">
          <view
            v-for="(cell, idx) in calCells"
            :key="idx"
            class="cal-cell"
            :class="{ 'cc-empty': !cell.day, 'cc-checked': cell.checked, 'cc-today': cell.isToday, 'cc-selected': cell.day === selectedDay }"
            @tap="cell.day && selectDay(cell.day)"
          >
            <text v-if="cell.day" class="cc-txt">{{ cell.day }}</text>
            <image v-if="cell.checked" class="cc-dot-img" src="/static/勾号图标.png" mode="aspectFit" />
          </view>
        </view>
        <view class="cal-legend">
          <view class="cl-item"><view class="cl-dot cl-dot--checked" /><text>已打卡</text></view>
          <view class="cl-item"><view class="cl-dot cl-dot--today" /><text>今天</text></view>
          <view class="cl-item"><view class="cl-dot cl-dot--none" /><text>未打卡</text></view>
        </view>
      </view>

      <!-- 当日记录 -->
      <view class="card rec-card">
        <view class="rec-header">
          <text class="rec-title">{{ currentMonth }}月{{ selectedDay }}日打卡记录</text>
          <text v-if="selectedDayChecked" class="rec-badge">已打卡</text>
          <text class="rec-share" @tap="shareCheckin">分享打卡 ⇧</text>
        </view>
        <view v-if="selectedRecords.length">
          <view v-for="r in selectedRecords" :key="r.id" class="rec-item" @tap="goDetail(r)">
            <image class="rec-icon-img" src="/static/主页户外跑图标.png" mode="aspectFit" />
            <view class="rec-info">
              <view class="rec-main">
                <text class="rec-dist">{{ r.distance_km }} <text class="rec-unit">公里</text></text>
                <view class="rec-stat"><image class="rec-stat-img" src="/static/主页时长图标.png" mode="aspectFit" /><text>{{ formatDuration(r.duration) }}</text><text class="rec-stat-l">用时</text></view>
                <view class="rec-stat"><image class="rec-stat-img" src="/static/主页配速图标.png" mode="aspectFit" /><text>{{ formatPace(r.pace) }}</text><text class="rec-stat-l">配速</text></view>
              </view>
              <view class="rec-meta"><image class="rec-meta-img" src="/static/location.png" mode="aspectFit" /><text>户外跑 · {{ formatTime(r.started_at) }}</text></view>
            </view>
            <text class="rec-chev">›</text>
          </view>
        </view>
        <view v-else class="rec-empty"><text>{{ currentMonth }}月{{ selectedDay }}日无打卡记录</text></view>
      </view>

      <!-- 统计 -->
      <view class="card stat-card">
        <view class="stat-hdr">
          <text class="section-title">打卡统计</text>
          <text class="stat-more" @tap="viewHistory">查看详情 ›</text>
        </view>
        <view class="stat-row">
          <view class="si"><text class="siv">{{ calData.month_count || 0 }}</text><text class="sil">天</text><text class="sid">本月打卡</text></view>
          <view class="si"><text class="siv">{{ calData.streak || 0 }}</text><text class="sil">天</text><text class="sid">连续打卡</text></view>
          <view class="si"><text class="siv">{{ calData.total_days || 0 }}</text><text class="sil">天</text><text class="sid">累计打卡</text></view>
        </view>
      </view>

      <!-- 连续打卡奖励 -->
      <view class="card reward-card">
        <view class="reward-hdr">
          <text class="section-title">连续打卡奖励</text>
          <text class="reward-hint">{{ calData.streak || 0 }}天卡情 ›</text>
        </view>
        <view class="reward-track-wrap">
          <view class="reward-track">
            <view class="reward-progress" :style="{ width: rewardProgress + '%' }" />
          </view>
          <view v-for="m in milestones" :key="m.days" class="reward-node" :style="{ left: m.pct + '%' }">
            <view class="rn-icon" :class="{ 'rn-unlocked': calData.streak >= m.days }">
              <image v-if="calData.streak >= m.days" class="rn-icon-emoji" src="/static/勾号图标.png" mode="aspectFit" /><image v-else class="rn-icon-emoji" src="/static/叉号图标.png" mode="aspectFit" />
            </view>
            <text class="rn-label">{{ m.days }}天</text>
          </view>
        </view>
        <text class="reward-tip">再坚持打卡 {{ nextMilestoneDays }} 天，可获得 {{ nextMilestoneLabel }} 打卡卡片</text>
      </view>

      <view style="height: 60rpx;" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { request } from '@/utils/request.js';

const statusBarHeight = ref(20);
const navHeight = computed(() => statusBarHeight.value + 44);

const currentYear = ref(new Date().getFullYear());
const currentMonth = ref(new Date().getMonth() + 1);
const selectedDay = ref(new Date().getDate());
const calData = ref({ month_count: 0, streak: 0, total_days: 0, checkin_days: [], selected_records: [] });
const rank = ref(null);
const groupName = ref('暂未加入跑团');
const groupDesc = ref('加入跑团，一起跑步打卡');
const isGroupLeader = ref(false);
const loading = ref(false);

const today = new Date();
const canGoNext = computed(() =>
  currentYear.value < today.getFullYear() ||
  (currentYear.value === today.getFullYear() && currentMonth.value < today.getMonth() + 1)
);

const calCells = computed(() => {
  const y = currentYear.value, m = currentMonth.value;
  const firstDay = new Date(y, m - 1, 1).getDay();
  const daysInMonth = new Date(y, m, 0).getDate();
  const checkedSet = new Set(calData.value.checkin_days || []);
  const todayDay = (y === today.getFullYear() && m === today.getMonth() + 1) ? today.getDate() : null;
  const cells = [];
  for (let i = 0; i < firstDay; i++) cells.push({ day: null });
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push({ day: d, checked: checkedSet.has(d), isToday: d === todayDay });
  }
  return cells;
});

const selectedDayChecked = computed(() =>
  (calData.value.checkin_days || []).includes(selectedDay.value)
);

const selectedRecords = computed(() => calData.value.selected_records || []);

const milestones = [
  { days: 3, pct: 10 },
  { days: 7, pct: 30 },
  { days: 14, pct: 55 },
  { days: 21, pct: 75 },
  { days: 30, pct: 95 },
];

const rewardProgress = computed(() => {
  const streak = calData.value.streak || 0;
  const last = milestones[milestones.length - 1];
  return Math.min((streak / last.days) * 100, 100);
});

const nextMilestoneDays = computed(() => {
  const streak = calData.value.streak || 0;
  const next = milestones.find(m => m.days > streak);
  return next ? next.days - streak : 0;
});

const nextMilestoneLabel = computed(() => {
  const streak = calData.value.streak || 0;
  const next = milestones.find(m => m.days > streak);
  return next ? `${next.days}天` : '更多';
});

const loadCalendar = async (year, month, day) => {
  loading.value = true;
  try {
    const res = await request({
      url: `/student/checkin-calendar?year=${year}&month=${month}`,
      method: 'GET'
    });
    calData.value = res;
    if (day != null) selectedDay.value = day;
    else selectedDay.value = res.today || res.selected_day || 1;
  } catch (e) {
    console.error('load calendar failed', e);
  } finally {
    loading.value = false;
  }
};

const loadGroupInfo = async () => {
  try {
    const res = await request({ url: '/run-group/my', method: 'GET' });
    if (res && res.name) {
      groupName.value = res.name;
      groupDesc.value = res.description || '热爱跑步，享受运动的快乐！';
    }
  } catch (e) {}
};

const selectDay = async (day) => {
  selectedDay.value = day;
  try {
    const res = await request({
      url: `/student/checkin-calendar?year=${currentYear.value}&month=${currentMonth.value}&selected_day=${day}`,
      method: 'GET'
    });
    calData.value = { ...calData.value, selected_records: res.selected_records || [] };
  } catch (e) {}
};

const prevMonth = () => {
  if (currentMonth.value === 1) { currentYear.value--; currentMonth.value = 12; }
  else currentMonth.value--;
  selectedDay.value = 1;
  loadCalendar(currentYear.value, currentMonth.value, 1);
};

const nextMonth = () => {
  if (!canGoNext.value) return;
  if (currentMonth.value === 12) { currentYear.value++; currentMonth.value = 1; }
  else currentMonth.value++;
  selectedDay.value = 1;
  loadCalendar(currentYear.value, currentMonth.value, 1);
};

const goBack = () => uni.navigateBack();
const switchGroup = () => uni.navigateTo({ url: '/pages/run-group/discover' });
const shareCheckin = () => uni.showToast({ title: '分享功能即将开放', icon: 'none' });
const viewHistory = () => uni.navigateTo({ url: '/pages/history/history' });
const goDetail = (r) => uni.navigateTo({ url: `/pages/history/detail?id=${r.id}` });

const showRules = () => {
  uni.showModal({
    title: '打卡规则',
    content: '每天完成一次有效阳光跑即算打卡。\n\n有效条件：\n男生 ≥ 2.0 km，女生 ≥ 1.2 km\n配速：3~10 分/公里\n每天限1次有效记录',
    showCancel: false,
    confirmText: '我知道了'
  });
};

const formatDuration = (s) => {
  const m = Math.floor((s || 0) / 60), sec = (s || 0) % 60;
  return `${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;
};

const formatPace = (p) => {
  if (!p) return "--'--\"";
  const n = Number(p);
  const min = Math.floor(n), sec = Math.round((n - min) * 60);
  return `${min}'${String(sec).padStart(2,'0')}"`;
};

const formatTime = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  return `${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
};

onMounted(() => {
  const sys = uni.getSystemInfoSync();
  statusBarHeight.value = sys.statusBarHeight || 20;
  loadCalendar(currentYear.value, currentMonth.value, today.getDate());
  loadGroupInfo();
});
</script>

<style scoped>
.page { min-height: 100vh; background: #f5f7fa; }

.navbar {
  position: fixed; top: 0; left: 0; right: 0;
  background: #fff; z-index: 100;
  display: flex; align-items: center;
  padding: 0 28rpx; height: 44px;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.06);
}
.navbar-back { width: 60rpx; display: flex; align-items: center; }
.navbar-back-icon { font-size: 48rpx; color: #333; line-height: 1; }
.navbar-title { flex: 1; text-align: center; font-size: 32rpx; font-weight: 700; color: #1a2b3c; }
.navbar-right { font-size: 26rpx; color: #26b586; width: 100rpx; text-align: right; }

.scroll { position: fixed; left: 0; right: 0; bottom: 0; overflow-y: auto; }

.card {
  background: #fff; border-radius: 24rpx;
  margin: 24rpx 24rpx 0;
  padding: 28rpx 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}

/* 跑团卡片 */
.group-info { display: flex; align-items: center; margin-bottom: 24rpx; }
.group-avatar {
  width: 80rpx; height: 80rpx; border-radius: 50%;
  background: #e8f8f2; display: flex; align-items: center; justify-content: center;
  font-size: 40rpx; margin-right: 20rpx; flex-shrink: 0;
}
.group-detail { flex: 1; }
.group-name-row { display: flex; align-items: center; gap: 12rpx; }
.group-name { font-size: 30rpx; font-weight: 700; color: #1a2b3c; }
.group-tag { font-size: 20rpx; color: #26b586; background: #e8f8f2; padding: 2rpx 12rpx; border-radius: 20rpx; }
.group-desc { font-size: 24rpx; color: #8a9bab; margin-top: 6rpx; }
.group-switch { font-size: 24rpx; color: #26b586; padding: 10rpx 18rpx; border: 2rpx solid #26b586; border-radius: 28rpx; white-space: nowrap; }
.group-stats { display: flex; justify-content: space-around; padding-top: 20rpx; border-top: 2rpx solid #f0f3f6; }
.gs { display: flex; flex-direction: column; align-items: center; }
.gsv { font-size: 36rpx; font-weight: 800; color: #26b586; }
.gsl { font-size: 22rpx; color: #8a9bab; margin-top: 4rpx; }

/* 日历 */
.cal-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20rpx; }
.cal-arrow { font-size: 44rpx; color: #26b586; padding: 0 20rpx; font-weight: 700; }
.cal-arrow--disabled { color: #ccc; }
.cal-month { font-size: 30rpx; font-weight: 700; color: #1a2b3c; }
.cal-weekdays { display: flex; margin-bottom: 12rpx; }
.cal-wd { flex: 1; text-align: center; font-size: 24rpx; color: #8a9bab; }
.cal-grid { display: flex; flex-wrap: wrap; }
.cal-cell {
  width: calc(100% / 7); aspect-ratio: 1;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  position: relative; border-radius: 50%;
}
.cc-empty {}
.cc-txt { font-size: 28rpx; color: #1a2b3c; }
.cc-checked { background: #26b586; }
.cc-checked .cc-txt { color: #fff; font-weight: 700; }
.cc-dot { position: absolute; bottom: 4rpx; font-size: 18rpx; color: #fff; }
.cc-today { border: 3rpx solid #26b586; }
.cc-selected:not(.cc-checked) { background: rgba(38,181,134,0.15); }
.cal-legend { display: flex; justify-content: center; gap: 40rpx; margin-top: 20rpx; padding-top: 16rpx; border-top: 2rpx solid #f0f3f6; }
.cl-item { display: flex; align-items: center; gap: 8rpx; font-size: 22rpx; color: #8a9bab; }
.cl-dot { width: 20rpx; height: 20rpx; border-radius: 50%; }
.cl-dot--checked { background: #26b586; }
.cl-dot--today { border: 3rpx solid #26b586; background: #fff; }
.cl-dot--none { background: #e0e0e0; }

/* 打卡记录 */
.rec-header { display: flex; align-items: center; margin-bottom: 20rpx; gap: 12rpx; }
.rec-title { font-size: 28rpx; font-weight: 700; color: #1a2b3c; flex: 1; }
.rec-badge { font-size: 22rpx; color: #26b586; background: #e8f8f2; padding: 4rpx 16rpx; border-radius: 20rpx; }
.rec-share { font-size: 24rpx; color: #26b586; padding: 6rpx 16rpx; border: 2rpx solid #26b586; border-radius: 20rpx; }
.rec-item { display: flex; align-items: center; padding: 20rpx 0; border-bottom: 2rpx solid #f0f3f6; }
.rec-item:last-child { border-bottom: none; }
.rec-icon { font-size: 48rpx; margin-right: 20rpx; }
.rec-info { flex: 1; }
.rec-main { display: flex; align-items: baseline; gap: 16rpx; flex-wrap: wrap; }
.rec-dist { font-size: 40rpx; font-weight: 800; color: #1a2b3c; }
.rec-unit { font-size: 24rpx; color: #8a9bab; }
.rec-stat { display: flex; align-items: center; gap: 4rpx; font-size: 24rpx; color: #4a5d6e; }
.rec-stat-l { font-size: 20rpx; color: #8a9bab; }
.rec-meta { font-size: 22rpx; color: #8a9bab; margin-top: 6rpx; display: flex; align-items: center; gap: 4rpx; }
.rec-meta-img { width: 28rpx; height: 28rpx; flex-shrink: 0; }
.group-avatar-img { width: 40rpx; height: 40rpx; }
.cc-dot-img { position: absolute; bottom: 4rpx; width: 18rpx; height: 18rpx; }
.rec-icon-img { width: 40rpx; height: 40rpx; margin-right: 20rpx; flex-shrink: 0; }
.rec-stat-img { width: 28rpx; height: 28rpx; }
.rn-icon-emoji { width: 24rpx; height: 24rpx; }
.rec-chev { font-size: 36rpx; color: #c5ced6; margin-left: 8rpx; }
.rec-empty { text-align: center; padding: 40rpx 0; font-size: 26rpx; color: #8a9bab; }

/* 统计 */
.stat-hdr { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24rpx; }
.section-title { font-size: 30rpx; font-weight: 700; color: #1a2b3c; }
.stat-more { font-size: 24rpx; color: #26b586; }
.stat-row { display: flex; justify-content: space-around; }
.si { display: flex; align-items: baseline; gap: 0; flex-direction: column; align-items: center; }
.siv { font-size: 48rpx; font-weight: 800; color: #26b586; }
.sil { font-size: 24rpx; color: #8a9bab; }
.sid { font-size: 22rpx; color: #8a9bab; margin-top: 4rpx; }

/* 连续打卡奖励 */
.reward-hdr { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40rpx; }
.reward-hint { font-size: 24rpx; color: #8a9bab; }
.reward-track-wrap { position: relative; height: 80rpx; margin: 0 20rpx 16rpx; }
.reward-track {
  position: absolute; top: 30rpx; left: 0; right: 0; height: 12rpx;
  background: #e8f8f2; border-radius: 6rpx; overflow: hidden;
}
.reward-progress { height: 100%; background: #26b586; border-radius: 6rpx; transition: width 0.3s; }
.reward-node { position: absolute; top: 0; transform: translateX(-50%); display: flex; flex-direction: column; align-items: center; }
.rn-icon {
  width: 56rpx; height: 56rpx; border-radius: 50%;
  background: #e0e0e0; display: flex; align-items: center; justify-content: center;
  font-size: 24rpx; color: #999;
}
.rn-unlocked { background: #26b586; color: #fff; }
.rn-label { font-size: 20rpx; color: #8a9bab; margin-top: 6rpx; }
.reward-tip { font-size: 24rpx; color: #8a9bab; text-align: center; display: block; margin-top: 16rpx; }
</style>
