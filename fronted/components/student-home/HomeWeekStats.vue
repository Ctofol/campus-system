<template>
  <view class="home-week">
    <view v-if="loading" class="home-week__skeleton">
      <view v-for="i in 4" :key="i" class="home-week__sk-item" />
    </view>
    <view v-else-if="stats && !stats.hasData" class="home-week__empty">
      <image class="home-week__empty-icon" src="/static/home-outdoor-run.png" mode="aspectFit" />
      <text class="home-week__empty-txt">本周还没有跑步记录</text>
      <view class="home-week__empty-btn" @tap="$emit('startRun')">
        <text>去跑一场</text>
      </view>
    </view>
    <view v-else class="home-week__row">
      <view class="home-week-stat">
        <image class="home-week-stat__icon" src="/static/home-distance.png" mode="aspectFit" />
        <text class="home-week-stat__val">{{ stats.distanceKm }}</text>
        <text class="home-week-stat__unit">公里</text>
        <text class="home-week-stat__sub">总距离</text>
      </view>
      <view class="home-week-stat">
        <image class="home-week-stat__icon" src="/static/home-duration.png" mode="aspectFit" />
        <text class="home-week-stat__val home-week-stat__val--sm">{{ stats.durationLabel }}</text>
        <text class="home-week-stat__unit">小时</text>
        <text class="home-week-stat__sub">总时长</text>
      </view>
      <view class="home-week-stat">
        <image class="home-week-stat__icon" src="/static/icon-sport-count.png" mode="aspectFit" />
        <text class="home-week-stat__val home-week-stat__val--sm">{{ stats.paceLabel }}</text>
        <text class="home-week-stat__unit">/km</text>
        <text class="home-week-stat__sub">平均配速</text>
      </view>
      <view class="home-week-stat">
        <image class="home-week-stat__icon" src="/static/home-calories.png" mode="aspectFit" />
        <text class="home-week-stat__val">{{ stats.calories }}</text>
        <text class="home-week-stat__unit">千卡</text>
        <text class="home-week-stat__sub">总消耗</text>
      </view>
    </view>
  </view>
</template>

<script setup>
defineProps({
  stats: { type: Object, default: () => ({ hasData: false }) },
  loading: { type: Boolean, default: false }
});
defineEmits(['startRun']);
</script>

<style lang="scss" scoped>
.home-week__row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 10rpx;
}
.home-week-stat {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 14rpx 6rpx 12rpx;
  position: relative;
  background: #F7FAFB;
  border-radius: 14rpx;
}
.home-week-stat + .home-week-stat::before {
  content: none;
}
.home-week-stat__icon {
  width: 52rpx;
  height: 52rpx;
  margin-bottom: 8rpx;
}
.home-week-stat__val {
  font-size: 28rpx;
  font-weight: 900;
  color: #18232E;
  line-height: 1.2;
  text-align: center;
}
.home-week-stat__val--sm {
  font-size: 22rpx;
}
.home-week-stat__unit {
  font-size: 20rpx;
  font-weight: 700;
  color: #8E8E93;
  margin-top: 4rpx;
}
.home-week-stat__sub {
  font-size: 18rpx;
  font-weight: 700;
  color: #C5CED6;
  margin-top: 10rpx;
}
.home-week__skeleton {
  display: flex;
  flex-direction: row;
  gap: 16rpx;
}
.home-week__sk-item {
  flex: 1;
  height: 140rpx;
  border-radius: 16rpx;
  background: #f0f3f6;
}
.home-week__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24rpx 0 8rpx;
}
.home-week__empty-icon {
  width: 90rpx;
  height: 90rpx;
  opacity: 0.5;
}
.home-week__empty-txt {
  font-size: 26rpx;
  color: #8E8E93;
  margin-top: 12rpx;
}
.home-week__empty-btn {
  margin-top: 20rpx;
  padding: 12rpx 40rpx;
  background: #24BFA2;
  border-radius: 32rpx;
  font-size: 26rpx;
  color: #fff;
}
</style>
