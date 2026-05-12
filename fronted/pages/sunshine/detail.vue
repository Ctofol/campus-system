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
            </view>
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
            <text class="col">&gt; 40 次</text>
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
  const max = 20;
  const percent = Math.min(1, (stats.value.total_valid_count || 0) / max);
  const deg = 360 * percent;
  return {
    backgroundImage: `conic-gradient(#20C997 ${deg}deg, #e5f7f3 ${deg}deg 360deg)`
  };
});

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

