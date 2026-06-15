<template>
  <view class="home-week">
    <view v-if="loading" class="home-week__skeleton">
      <view v-for="i in 4" :key="i" class="home-week__sk-item" />
    </view>
    <view v-else-if="stats && !stats.hasData" class="home-week__empty">
      <image class="home-week__empty-icon" src="/static/主页户外跑图标.png" mode="aspectFit" />
      <text class="home-week__empty-txt">本周还没有跑步记录</text>
      <view class="home-week__empty-btn" @tap="$emit('startRun')">
        <text>去跑一场</text>
      </view>
    </view>
    <view v-else class="home-week__row">
      <view class="home-week-stat">
        <image class="home-week-stat__icon" src="/static/主页里程图标.png" mode="aspectFit" />
        <text class="home-week-stat__val">{{ stats.distanceKm }}</text>
        <text class="home-week-stat__unit">公里</text>
        <text class="home-week-stat__sub">总距离</text>
      </view>
      <view class="home-week-stat">
        <image class="home-week-stat__icon" src="/static/主页时长图标.png" mode="aspectFit" />
        <text class="home-week-stat__val home-week-stat__val--sm">{{ stats.durationLabel }}</text>
        <text class="home-week-stat__unit">小时</text>
        <text class="home-week-stat__sub">总时长</text>
      </view>
      <view class="home-week-stat">
        <image class="home-week-stat__icon" src="/static/主页配速图标.png" mode="aspectFit" />
        <text class="home-week-stat__val home-week-stat__val--sm">{{ stats.paceLabel }}</text>
        <text class="home-week-stat__unit">/km</text>
        <text class="home-week-stat__sub">平均配速</text>
      </view>
      <view class="home-week-stat">
        <image class="home-week-stat__icon" src="/static/主页卡路里图标.png" mode="aspectFit" />
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
}
.home-week-stat {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12rpx 6rpx;
  position: relative;
}
.home-week-stat + .home-week-stat::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 2rpx;
  height: 80rpx;
  background: #F0F3F6;
}
.home-week-stat__icon {
  width: 56rpx;
  height: 56rpx;
  margin-bottom: 10rpx;
}
.home-week-stat__val {
  font-size: 30rpx;
  font-weight: 900;
  color: #191C1E;
  line-height: 1.2;
  text-align: center;
}
.home-week-stat__val--sm {
  font-size: 24rpx;
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
  background: linear-gradient(90deg, #f0f3f6 25%, #e8ecf0 50%, #f0f3f6 75%);
  background-size: 200% 100%;
  animation: home-shimmer 1.2s ease-in-out infinite;
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
  background: #33C9AB;
  border-radius: 32rpx;
  font-size: 26rpx;
  color: #fff;
}
@keyframes home-shimmer {
  0% { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}
</style>