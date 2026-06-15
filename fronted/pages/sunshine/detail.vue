<template>
  <view class="page">
    <!-- 自定义导航栏 -->
    <view class="nav-bar">
      <view class="nav-back" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="nav-title">阳光跑详情</text>
      <view class="nav-right"></view>
    </view>

    <view class="content">
      <!-- 核心数据区 -->
      <view class="card core-card">
        <view class="core-top">
          <view class="circle-wrap">
            <view class="circle-outer">
              <view class="circle-progress" :style="circleStyle"></view>
              <view class="circle-inner">
                <text class="circle-count">{{ stats.total_valid_count }}</text>
                <text class="circle-label">有效次数 / 20</text>
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
          <view class="core-info">
            <view class="row">
              <text class="label">当前积分</text>
              <text class="value score">{{ stats.current_score }} 分</text>
            </view>
            <view class="row">
              <text class="label">我的达标进度</text>
              <text class="value progress-text">{{ progressText }}</text>
            </view>
          </view>
        </view>
        <view class="segment-bar">
          <view class="segment pass" :style="{ width: `${passBarWidth}%` }"></view>
          <view class="segment extra" :style="{ width: `${bonusBarWidth}%` }"></view>
          <view class="segment rest" :style="{ width: `${remainingBarWidth}%` }"></view>
        </view>
        <view class="core-tip">
          <text>说明：每次符合规则的阳光跑记为一次有效记录，用于阶梯计分。</text>
        </view>
      </view>

      <!-- 标准说明区 -->
      <view class="card standard-card">
        <text class="section-title">达标要求</text>
        <view class="standard-row">
          <text class="standard-label">里程要求：</text>
          <text class="standard-value">
            男生 ≥ 2.0 km，女生 ≥ 1.2 km
          </text>
        </view>
        <view class="standard-row">
          <text class="standard-label">配速要求：</text>
          <text class="standard-value">3 ~ 10 分/公里</text>
        </view>
        <view class="standard-row">
          <text class="standard-label">频次要求：</text>
          <text class="standard-value">每天最多记 1 次有效记录</text>
        </view>
        <view class="gender-highlight">
          <text>当前性别：</text>
          <text :class="stats.user_gender === 'female' ? 'female' : 'male'">
            {{ stats.user_gender === 'female' ? '女生' : '男生' }}
          </text>
        </view>

        <view class="divider"></view>

        <text class="section-title">积分阶梯说明</text>
        <view class="score-table">
          <view class="table-header">
            <text class="col">有效次数</text>
            <text class="col">对应分值</text>
            <text class="col">说明</text>
          </view>
          <view class="table-row">
            <text class="col">≤ 10 次</text>
            <text class="col">0 分</text>
            <text class="col">未达到基础要求</text>
          </view>
          <view class="table-row">
            <text class="col">11 - 19 次</text>
            <text class="col">42 - 58 分</text>
            <text class="col">每多跑 1 次 +2 分</text>
          </view>
          <view class="table-row key">
            <text class="col">20 次</text>
            <text class="col">60 分</text>
            <text class="col">及格线</text>
          </view>
          <view class="table-row">
            <text class="col">21 - 40 次</text>
            <text class="col">62 - 100 分</text>
            <text class="col">每多跑 1 次 +2 分</text>
          </view>
          <view class="table-row key">
            <text class="col">40 次以上</text>
            <text class="col">100 分</text>
            <text class="col">满分封顶</text>
          </view>
        </view>
      </view>

      <!-- 今日状态明细 / 最近记录 -->
      <view class="card detail-card">
        <text class="section-title">最近运动明细（7 天内）</text>
        <view v-if="stats.daily_records && stats.daily_records.length" class="record-list">
          <view 
            class="record-item" 
            v-for="(item, idx) in stats.daily_records" 
            :key="idx"
          >
            <view class="record-main">
              <text class="record-time">{{ formatDateTime(item.started_at) }}</text>
              <text class="record-meta">
                {{ (item.distance || 0).toFixed(2) }} km · {{ formatDuration(item.duration || 0) }} ·
                <text v-if="item.pace"> {{ Number(item.pace).toFixed(1) }} 分/公里</text>
              </text>
            </view>
            <view class="record-status" :class="item.is_valid ? 'valid' : 'invalid'">
              <text v-if="item.is_valid">有效</text>
              <text v-else>无效</text>
            </view>
          </view>
        </view>
        <view v-else class="empty-tip">
          <text>最近 7 天暂无阳光跑记录</text>
        </view>

        <view v-if="latestFailReason" class="fail-reason">
          <text class="fail-title">最近一次失败原因：</text>
          <text class="fail-text">{{ latestFailReason }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { getSunshineStats } from '@/utils/request.js';

const stats = ref({
  total_valid_count: 0,
  current_score: 0,
  score: 0,
  today_status: 'not_started',
  today_fail_reason: '',
  daily_records: [],
  user_gender: 'male'
});

const circleStyle = computed(() => {
  const total = Math.max(Number(stats.value.total_valid_count) || 0, 0);
  const pass = Math.min(total, 20);
  const extra = Math.max(Math.min(total - 20, 20), 0);
  const remain = Math.max(20 - pass, 0);
  const passDeg = (pass / 40) * 360;
  const extraDeg = (extra / 40) * 360;
  const remainDeg = (remain / 40) * 360;
  return {
    background: `conic-gradient(#20C997 0deg ${passDeg}deg, #ffb020 ${passDeg}deg ${passDeg + extraDeg}deg, #dcefe9 ${passDeg + extraDeg}deg ${passDeg + extraDeg + remainDeg}deg, #8b5cf6 ${passDeg + extraDeg + remainDeg}deg 360deg)`
  };
});

const passCount = computed(() => Math.min(Number(stats.value.total_valid_count) || 0, 20));
const bonusCount = computed(() => Math.max(Math.min((Number(stats.value.total_valid_count) || 0) - 20, 20), 0));
const remainingCount = computed(() => Math.max(20 - passCount.value, 0));
const passBarWidth = computed(() => Math.min((passCount.value / 20) * 100, 100));
const bonusBarWidth = computed(() => Math.min((bonusCount.value / 20) * 100, 100));
const remainingBarWidth = computed(() => Math.max(100 - passBarWidth.value - bonusBarWidth.value, 0));

const progressText = computed(() => {
  const count = stats.value.total_valid_count || 0;
  if (count < 20) {
    const left = 20 - count;
    return `已跑 ${count} 次，离及格还差 ${left} 次`;
  }
  if (count < 40) {
    const extra = count - 20;
    return `已超过及格线 ${extra} 次，继续冲击满分！`;
  }
  return `已达到满分要求，保持良好运动习惯！`;
});

const latestFailReason = computed(() => {
  if (stats.value.today_status === 'failed' && stats.value.today_fail_reason) {
    return stats.value.today_fail_reason;
  }
  const rec = (stats.value.daily_records || []).find(r => r && r.is_valid === false && r.fail_reason);
  return rec ? rec.fail_reason : '';
});

const loadStats = async () => {
  try {
    const res = await getSunshineStats();
    stats.value = {
      ...stats.value,
      ...res,
      current_score: res.current_score || res.score || 0
    };
  } catch (e) {
    console.error('load sunshine stats failed', e);
  }
};

const goBack = () => {
  uni.navigateBack();
};

const formatDateTime = (val) => {
  if (!val) return '';
  const d = new Date(val);
  const m = d.getMonth() + 1;
  const day = d.getDate();
  const h = d.getHours().toString().padStart(2, '0');
  const mi = d.getMinutes().toString().padStart(2, '0');
  return `${m}-${day} ${h}:${mi}`;
};

const formatDuration = (seconds) => {
  const min = Math.floor(seconds / 60);
  const sec = seconds % 60;
  return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
};

onMounted(() => {
  loadStats();
});
</script>

<style scoped>
.page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.nav-bar {
  height: 88rpx;
  padding: 0 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.nav-back {
  padding: 10rpx;
}
.back-icon {
  font-size: 34rpx;
  color: #333;
}
.nav-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}
.nav-right {
  width: 40rpx;
}

.content {
  padding: 20rpx;
}

.card {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.03);
}

.core-card .core-top {
  flex-direction: row;
  display: flex;
}
.circle-wrap {
  width: 200rpx;
  height: 200rpx;
  margin-right: 30rpx;
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
.legend-dot.rest {
  background: #dcefe9;
}
.circle-outer {
  width: 200rpx;
  height: 200rpx;
  border-radius: 50%;
  background-color: #e5f7f3;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.circle-progress {
  position: absolute;
  width: 200rpx;
  height: 200rpx;
  border-radius: 50%;
  z-index: 1;
}
.circle-inner {
  width: 140rpx;
  height: 140rpx;
  border-radius: 50%;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;
}
.circle-count {
  font-size: 40rpx;
  font-weight: bold;
  color: #20C997;
}
.circle-label {
  font-size: 22rpx;
  color: #999;
  margin-top: 8rpx;
}

.segment-bar {
  width: 100%;
  height: 18rpx;
  border-radius: 999rpx;
  overflow: hidden;
  background: #edf4f2;
  display: flex;
  margin: 24rpx 0 12rpx;
}

.segment {
  height: 100%;
}

.segment.pass {
  background: #20C997;
}

.segment.extra {
  background: #ffb020;
}

.segment.rest {
  background: #dcefe9;
}

.core-info {
  flex: 1;
  justify-content: center;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.label {
  font-size: 26rpx;
  color: #666;
}
.value {
  font-size: 28rpx;
  color: #333;
}
.score {
  font-size: 40rpx;
  font-weight: bold;
  color: #ff9800;
}
.progress-text {
  font-size: 26rpx;
  color: #555;
}
.core-tip {
  margin-top: 16rpx;
  font-size: 24rpx;
  color: #999;
}

.section-title {
  font-size: 30rpx;
  font-weight: bold;
  margin-bottom: 16rpx;
  color: #333;
}

.standard-row {
  display: flex;
  margin-bottom: 8rpx;
}
.standard-label {
  width: 180rpx;
  font-size: 26rpx;
  color: #666;
}
.standard-value {
  font-size: 26rpx;
  color: #333;
}
.gender-highlight {
  margin-top: 8rpx;
  font-size: 26rpx;
}
.gender-highlight .male {
  color: #1976d2;
}
.gender-highlight .female {
  color: #d81b60;
}

.divider {
  height: 1rpx;
  background-color: #eee;
  margin: 20rpx 0;
}

.score-table {
  border-radius: 12rpx;
  border: 1rpx solid #e0e0e0;
  overflow: hidden;
}
.score-table .table-header,
.score-table .table-row {
  flex-direction: row;
  display: flex;
}
.score-table .table-header {
  background-color: #f5f5f5;
}
.score-table .col {
  flex: 1;
  padding: 16rpx 10rpx;
  font-size: 24rpx;
  color: #555;
}
.score-table .table-row:nth-child(odd) {
  background-color: #fafafa;
}
.score-table .key {
  background-color: #fffde7;
}
.score-table .key .col {
  font-weight: bold;
  color: #e65100;
}

.record-list {
  margin-top: 8rpx;
}
.record-item {
  flex-direction: row;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12rpx 0;
  border-bottom: 1rpx dashed #eee;
}
.record-item:last-child {
  border-bottom-width: 0;
}
.record-time {
  font-size: 26rpx;
  color: #333;
}
.record-meta {
  font-size: 22rpx;
  color: #777;
}
.record-status {
  font-size: 24rpx;
}
.record-status.valid {
  color: #2e7d32;
}
.record-status.invalid {
  color: #c62828;
}

.empty-tip {
  font-size: 24rpx;
  color: #999;
  text-align: center;
}

.fail-reason {
  margin-top: 16rpx;
  font-size: 24rpx;
}
.fail-title {
  color: #c62828;
  font-weight: bold;
}
.fail-text {
  color: #c62828;
}
</style>

