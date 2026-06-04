<template>
  <view class="home-week">
    <view v-if="loading" class="home-week__skeleton">
      <view v-for="i in 4" :key="i" class="home-week__sk-item" />
    </view>
    <view v-else-if="!stats.hasData" class="home-week__empty">
      <text class="home-week__empty-icon">🏃</text>
      <text class="home-week__empty-txt">本周还没有跑步记录</text>
      <view class="home-week__empty-btn" @tap="$emit('startRun')">
        <text>去跑一场</text>
      </view>
    </view>
    <view v-else class="home-week__row">
      <view class="home-week-stat">
        <view class="home-week-stat__icon home-week-stat__icon--dist">📍</view>
        <text class="home-week-stat__val">{{ stats.distanceKm }}</text>
        <text class="home-week-stat__unit">公里</text>
      </view>
      <view class="home-week-stat">
        <view class="home-week-stat__icon home-week-stat__icon--time">⏱</view>
        <text class="home-week-stat__val home-week-stat__val--sm">{{ stats.durationLabel }}</text>
        <text class="home-week-stat__unit">时长</text>
      </view>
      <view class="home-week-stat">
        <view class="home-week-stat__icon home-week-stat__icon--pace">⚡</view>
        <text class="home-week-stat__val home-week-stat__val--sm">{{ stats.paceLabel }}</text>
        <text class="home-week-stat__unit">配速</text>
      </view>
      <view class="home-week-stat">
        <view class="home-week-stat__icon home-week-stat__icon--cal">🔥</view>
        <text class="home-week-stat__val">{{ stats.calories }}</text>
        <text class="home-week-stat__unit">千卡</text>
      </view>
    </view>
  </view>
</template>

<script setup>
defineProps({
  stats: { type: Object, required: true },
  loading: { type: Boolean, default: false }
});
defineEmits(['startRun']);
</script>

<style lang="scss" scoped>
.home-week__row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 8rpx;
}
.home-week-stat {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.home-week-stat__icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  margin-bottom: 12rpx;
}
.home-week-stat__icon--dist {
  background: #e8f8f2;
}
.home-week-stat__icon--time {
  background: #e8f4fc;
}
.home-week-stat__icon--pace {
  background: #fff4e6;
}
.home-week-stat__icon--cal {
  background: #ffeee8;
}
.home-week-stat__val {
  font-size: 30rpx;
  font-weight: 800;
  color: #1a2b3c;
  line-height: 1.2;
  text-align: center;
}
.home-week-stat__val--sm {
  font-size: 24rpx;
}
.home-week-stat__unit {
  font-size: 20rpx;
  color: #8a9bab;
  margin-top: 6rpx;
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
  font-size: 56rpx;
  opacity: 0.5;
}
.home-week__empty-txt {
  font-size: 26rpx;
  color: #8a9bab;
  margin-top: 12rpx;
}
.home-week__empty-btn {
  margin-top: 20rpx;
  padding: 12rpx 40rpx;
  background: #26b586;
  border-radius: 32rpx;
  font-size: 26rpx;
  color: #fff;
}
@keyframes home-shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}
</style>
