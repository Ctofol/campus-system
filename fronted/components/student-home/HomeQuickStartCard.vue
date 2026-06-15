<template>
  <view class="home-quick">
    <view class="home-quick__left">
      <text class="home-quick__title">开始跑步</text>
      <text class="home-quick__sub" @tap="$emit('go')">自由跑 · 随心跑 ›</text>
    </view>
    <view class="home-quick__center" @tap="$emit('go')">
      <view class="home-quick__go">
        <image class="home-quick__go-icon" src="/static/主页GO图标.png" mode="aspectFit" />
      </view>
      <text class="home-quick__go-txt">GO</text>
    </view>
    <view class="home-quick__right">
      <text class="home-quick__label">累计跑步</text>
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
        <text>{{ goalKm > 0 ? '修改目标' : '设置目标' }}</text>
        <text class="home-quick__goal-arrow">›</text>
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
  margin: -48rpx 28rpx 0;
  padding: 40rpx 28rpx 36rpx;
  background: #fff;
  border-radius: 32rpx;
  box-shadow: 0 10rpx 50rpx rgba(0, 0, 0, 0.04), 0 4rpx 20rpx rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: row;
  align-items: center;
  position: relative;
  z-index: 2;
}
.home-quick__left {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.home-quick__title {
  font-size: 34rpx;
  font-weight: 800;
  color: #191C1E;
}
.home-quick__sub {
  font-size: 22rpx;
  color: #8E8E93;
  margin-top: 8rpx;
  font-weight: 600;
}
.home-quick__center {
  flex-shrink: 0;
  padding: 0 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.home-quick__go {
  width: 168rpx;
  height: 168rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s;
}
.home-quick__go:active {
  transform: scale(0.95);
}
.home-quick__go-icon {
  width: 164rpx;
  height: 164rpx;
}
.home-quick__go-txt {
  font-size: 34rpx;
  font-weight: 900;
  color: #33C9AB;
  letter-spacing: 6rpx;
  margin-top: -4rpx;
}
.home-quick__right {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.home-quick__label {
  font-size: 22rpx;
  font-weight: 700;
  color: #8E8E93;
  text-transform: uppercase;
  letter-spacing: 2rpx;
}
.home-quick__km-row {
  display: flex;
  flex-direction: row;
  align-items: baseline;
  margin-top: 8rpx;
}
.home-quick__km {
  font-size: 56rpx;
  font-weight: 900;
  color: #191C1E;
  line-height: 1;
}
.home-quick__unit {
  font-size: 22rpx;
  color: #8E8E93;
  font-weight: 700;
  margin-left: 6rpx;
}
.home-quick__progress {
  width: 100%;
  margin-top: 16rpx;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.home-quick__progress-bar {
  width: 100%;
  height: 10rpx;
  background: #EEF2F5;
  border-radius: 5rpx;
  overflow: hidden;
}
.home-quick__progress-fill {
  height: 100%;
  background: #33C9AB;
  border-radius: 5rpx;
  transition: width 0.3s ease;
}
.home-quick__progress-txt {
  font-size: 20rpx;
  color: #33C9AB;
  margin-top: 8rpx;
  font-weight: 600;
}
.home-quick__goal {
  margin-top: 16rpx;
  padding: 10rpx 24rpx;
  border: 2rpx solid rgba(51, 201, 171, 0.3);
  border-radius: 30rpx;
  display: flex;
  align-items: center;
  gap: 4rpx;
  font-size: 22rpx;
  font-weight: 700;
  color: #33C9AB;
  background: #fff;
}
.home-quick__goal:active {
  background: rgba(51, 201, 171, 0.05);
}
.home-quick__goal-arrow {
  font-size: 26rpx;
}
</style>