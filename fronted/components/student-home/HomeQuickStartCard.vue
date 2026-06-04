<template>
  <view class="home-quick">
    <view class="home-quick__col home-quick__col--left">
      <text class="home-quick__title">开始跑步</text>
      <text class="home-quick__sub" @tap="$emit('go')">自由跑 · 随心跑 ›</text>
      <view class="home-quick__link" @tap="$emit('settings')">
        <text class="home-quick__gear">⚙</text>
        <text>设置</text>
      </view>
    </view>
    <view class="home-quick__center" @tap="$emit('go')">
      <view class="home-quick__go">
        <text class="home-quick__go-icon">🏃</text>
        <text class="home-quick__go-txt">GO</text>
      </view>
    </view>
    <view class="home-quick__col home-quick__col--right">
      <text class="home-quick__title home-quick__title--sm">累计跑步</text>
      <view class="home-quick__km-row">
        <text class="home-quick__km">{{ distanceKm }}</text>
        <text class="home-quick__unit">公里</text>
      </view>
      <view v-if="goalKm > 0" class="home-quick__progress">
        <view class="home-quick__progress-bar">
          <view class="home-quick__progress-fill" :style="{ width: goalProgress + '%' }" />
        </view>
        <text class="home-quick__progress-txt">{{ goalHint }}</text>
      </view>
      <view class="home-quick__goal" @tap="$emit('setGoal')">
        <text>{{ goalKm > 0 ? '修改目标 ›' : '设置目标 ›' }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
defineProps({
  distanceKm: { type: String, default: '0.0' },
  goalKm: { type: Number, default: 0 },
  goalProgress: { type: Number, default: 0 },
  goalHint: { type: String, default: '' }
});
defineEmits(['go', 'settings', 'setGoal']);
</script>

<style lang="scss" scoped>
.home-quick {
  margin: -44rpx 24rpx 0;
  padding: 36rpx 28rpx 32rpx;
  background: #fff;
  border-radius: 28rpx;
  box-shadow: 0 16rpx 48rpx rgba(26, 43, 60, 0.1);
  display: flex;
  flex-direction: row;
  align-items: center;
  position: relative;
  z-index: 2;
}
.home-quick__col {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.home-quick__col--left {
  align-items: flex-start;
}
.home-quick__col--right {
  align-items: flex-end;
}
.home-quick__title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1a2b3c;
}
.home-quick__title--sm {
  font-size: 26rpx;
  color: #6b7c8f;
  font-weight: 600;
}
.home-quick__sub {
  font-size: 24rpx;
  color: #8a9bab;
  margin-top: 8rpx;
}
.home-quick__link {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 20rpx;
  font-size: 24rpx;
  color: #8a9bab;
}
.home-quick__gear {
  margin-right: 8rpx;
  font-size: 26rpx;
}
.home-quick__center {
  flex-shrink: 0;
  padding: 0 16rpx;
}
.home-quick__go {
  width: 148rpx;
  height: 148rpx;
  border-radius: 50%;
  background: linear-gradient(145deg, #2ed9a8 0%, #26b586 55%, #1fa67a 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12rpx 32rpx rgba(38, 181, 134, 0.45);
}
.home-quick__go-icon {
  font-size: 44rpx;
  line-height: 1;
}
.home-quick__go-txt {
  font-size: 38rpx;
  font-weight: 800;
  color: #fff;
  margin-top: 6rpx;
  letter-spacing: 3rpx;
}
.home-quick__km-row {
  display: flex;
  flex-direction: row;
  align-items: baseline;
  margin-top: 6rpx;
}
.home-quick__km {
  font-size: 48rpx;
  font-weight: 800;
  color: #1a2b3c;
  line-height: 1.1;
}
.home-quick__unit {
  font-size: 24rpx;
  color: #6b7c8f;
  margin-left: 6rpx;
}
.home-quick__progress {
  width: 100%;
  margin-top: 12rpx;
  align-items: flex-end;
  display: flex;
  flex-direction: column;
}
.home-quick__progress-bar {
  width: 100%;
  height: 8rpx;
  background: #eef2f5;
  border-radius: 4rpx;
  overflow: hidden;
}
.home-quick__progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #2ed9a8, #26b586);
  border-radius: 4rpx;
  transition: width 0.3s ease;
}
.home-quick__progress-txt {
  font-size: 20rpx;
  color: #26b586;
  margin-top: 6rpx;
}
.home-quick__goal {
  margin-top: 10rpx;
  padding: 8rpx 20rpx;
  border: 2rpx solid #26b586;
  border-radius: 28rpx;
  font-size: 22rpx;
  color: #26b586;
}
</style>
