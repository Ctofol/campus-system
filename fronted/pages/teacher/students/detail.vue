<template>
  <view class="detail-page">
    <!-- Header Card -->
    <view class="header-card">
      <view class="user-info">
        <view class="avatar">{{ name.slice(0,1) }}</view>
        <view class="info-content">
          <view class="name-row">
            <text class="name">{{ name }}</text>
            <text class="status-badge" :class="healthClass">{{ healthStatus }}</text>
          </view>
          <text class="sub-text">学号：{{ no }} | {{ className }}</text>
          <text class="sub-text">分组：{{ group || '未分组' }}</text>
        </view>
      </view>
      
      <view class="stats-grid">
        <view class="stat-item">
          <text class="stat-val">{{ runList.length }}</text>
          <text class="stat-label">总跑次</text>
        </view>
        <view class="stat-item">
          <text class="stat-val">{{ totalDistance }}</text>
          <text class="stat-label">总里程(km)</text>
        </view>
        <view class="stat-item">
          <text class="stat-val">{{ testList.length }}</text>
          <text class="stat-label">测试次数</text>
        </view>
      </view>
    </view>

    <!-- Tabs -->
    <view class="tabs-container">
      <view class="tabs">
        <view 
          class="tab-item" 
          :class="{ active: activeTab === 'run' }"
          @click="activeTab = 'run'"
        >跑步记录</view>
        <view 
          class="tab-item" 
          :class="{ active: activeTab === 'test' }"
          @click="activeTab = 'test'"
        >体能测试</view>
      </view>
    </view>

    <!-- Content Area -->
    <scroll-view scroll-y class="content-area">
      <!-- Run List -->
      <view v-if="activeTab === 'run'" class="list-container">
        <view class="record-card" v-for="(r, i) in runList" :key="'r'+i">
          <view class="card-left">
            <text class="card-date">{{ r.date }}</text>
            <text class="card-tag">{{ r.modeText }}</text>
          </view>
          <view class="card-right">
            <view class="data-row">
              <text class="data-val">{{ r.distance }}<text class="unit">km</text></text>
              <text class="data-val">{{ r.duration }}</text>
            </view>
            <text class="pace">配速 {{ r.pace || "5'30\"" }}</text>
          </view>
        </view>
        <view class="empty-tip" v-if="runList.length===0">暂无跑步记录</view>
      </view>

      <!-- Test List -->
      <view v-else class="list-container">
        <view class="record-card" v-for="(t, i) in testList" :key="'t'+i">
          <view class="card-left">
            <text class="card-date">{{ t.date }}</text>
            <text class="card-title">{{ t.testName }}</text>
          </view>
          <view class="card-right">
            <text class="test-result" :class="t.result === '合格' ? 'pass' : 'fail'">
              {{ t.result }}
            </text>
            <text class="test-val">成绩：{{ t.testCount }}</text>
          </view>
        </view>
        <view class="empty-tip" v-if="testList.length===0">暂无测试记录</view>
      </view>
    </scroll-view>

    <!-- Footer Actions -->
    <view class="footer-actions">
      <button class="action-btn outline" @click="contactStudent">联系学生</button>
      <button class="action-btn primary" @click="exportReport">导出档案</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onShow, onLoad } from '@dcloudio/uni-app';

const id = ref('');
const name = ref('');
const no = ref('');
const className = ref('');
const group = ref('体能A组'); // Mock group
const healthStatus = ref('良好');
const activeTab = ref('run');

const runList = ref([
  { date: '05-10 07:20', distance: 3.2, duration: '00:22', modeText: '普通跑步', pace: "6'52\"" },
  { date: '05-12 18:05', distance: 2.0, duration: '00:13', modeText: '警务专项', pace: "6'30\"" },
  { date: '05-15 06:40', distance: 5.0, duration: '00:30', modeText: '耐力跑', pace: "6'00\"" }
]);

const testList = ref([
  { date: '05-08 09:30', testName: '引体向上', testCount: 12, result: '合格' },
  { date: '05-14 15:10', testName: '仰卧起坐', testCount: 35, result: '未合格' }
]);

const totalDistance = computed(() => {
  return runList.value.reduce((acc, cur) => acc + cur.distance, 0).toFixed(1);
});

const healthClass = computed(() => {
  return healthStatus.value === '良好' ? 'good' : 'bad';
});

onLoad((opt) => {
  id.value = opt.id || '';
  name.value = opt.name || '';
  no.value = opt.no || '';
  className.value = opt.class || '';
  // In real app, fetch detailed info by id
});

onShow(() => {
  const role = uni.getStorageSync('userRole') || uni.getStorageSync('role');
  if (role !== 'teacher') {
    // Just a safeguard, usually handled by middleware
  }
});

const contactStudent = () => {
  uni.showActionSheet({
    itemList: ['拨打电话', '发送消息'],
    success: (res) => {
      uni.showToast({ title: '操作已模拟', icon: 'none' });
    }
  });
};

const exportReport = () => {
  uni.showToast({ title: '正在生成PDF档案...', icon: 'loading' });
  setTimeout(() => {
    uni.showToast({ title: '导出成功', icon: 'success' });
  }, 1500);
};
</script>

<style scoped>
.detail-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.header-card {
  background: #fff;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
}

.avatar {
  width: 100rpx;
  height: 100rpx;
  background: #20C997;
  color: #fff;
  font-size: 40rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(32, 201, 151, 0.3);
}

.info-content {
  flex: 1;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 8rpx;
}

.name {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

.status-badge {
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
  background: #e0f2f1;
  color: #20C997;
}

.status-badge.bad {
  background: #ffebee;
  color: #d81e06;
}

.sub-text {
  font-size: 26rpx;
  color: #666;
  display: block;
  margin-top: 4rpx;
}

.stats-grid {
  display: flex;
  justify-content: space-around;
  background: #f8f9fa;
  padding: 20rpx;
  border-radius: 12rpx;
}

.stat-item {
  text-align: center;
}

.stat-val {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  display: block;
}

.stat-label {
  font-size: 24rpx;
  color: #999;
  margin-top: 4rpx;
}

.tabs-container {
  background: #fff;
  padding: 0 30rpx;
  border-bottom: 1px solid #eee;
}

.tabs {
  display: flex;
  gap: 40rpx;
}

.tab-item {
  padding: 24rpx 0;
  font-size: 30rpx;
  color: #666;
  position: relative;
}

.tab-item.active {
  color: #20C997;
  font-weight: bold;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40rpx;
  height: 4rpx;
  background: #20C997;
  border-radius: 2rpx;
}

.content-area {
  flex: 1;
  padding: 20rpx 30rpx;
  box-sizing: border-box;
}

.list-container {
  padding-bottom: 120rpx;
}

.record-card {
  background: #fff;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.02);
}

.card-left {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.card-date {
  font-size: 26rpx;
  color: #999;
}

.card-tag {
  font-size: 24rpx;
  color: #fff;
  background: #20C997;
  padding: 2rpx 10rpx;
  border-radius: 4rpx;
  align-self: flex-start;
}

.card-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
}

.card-right {
  text-align: right;
}

.data-row {
  display: flex;
  align-items: baseline;
  justify-content: flex-end;
  gap: 16rpx;
}

.data-val {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.unit {
  font-size: 24rpx;
  font-weight: normal;
  margin-left: 2rpx;
}

.pace {
  font-size: 24rpx;
  color: #999;
  display: block;
  margin-top: 4rpx;
}

.test-result {
  font-size: 28rpx;
  font-weight: bold;
  display: block;
  margin-bottom: 4rpx;
}

.test-result.pass { color: #20C997; }
.test-result.fail { color: #ff9f43; }

.test-val {
  font-size: 26rpx;
  color: #666;
}

.empty-tip {
  text-align: center;
  color: #999;
  padding-top: 100rpx;
  font-size: 28rpx;
}

.footer-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: #fff;
  padding: 20rpx 30rpx;
  box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
  display: flex;
  gap: 20rpx;
  box-sizing: border-box;
}

.action-btn {
  flex: 1;
  margin: 0;
  font-size: 30rpx;
  border-radius: 40rpx;
}

.action-btn.outline {
  background: #fff;
  color: #666;
  border: 1px solid #ddd;
}

.action-btn.primary {
  background: #20C997;
  color: #fff;
}
</style>