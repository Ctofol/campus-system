<template>
  <view class="home-recent">
    <view v-if="loading" class="home-recent__skeleton">
      <view v-for="i in 3" :key="i" class="home-recent__sk-row" />
    </view>
    <view v-else-if="!items.length" class="home-recent__empty">
      <text class="home-recent__empty-txt">暂无跑步记录</text>
      <view class="home-recent__empty-btn" @tap="$emit('startRun')">
        <text>开始第一次跑步</text>
      </view>
    </view>
    <view v-else>
      <view
        v-for="run in items"
        :key="run.id"
        class="home-recent-item"
        @tap="$emit('detail', run)"
      >
        <HomeRecentMapThumb :preview="run.trajectoryPreview" :has-track="run.hasTrack" />
        <view class="home-recent-item__info">
          <view class="home-recent-item__title-row">
            <text class="home-recent-item__title">{{ run.title }}</text>
            <text v-if="run.isValid" class="home-recent-item__badge">有效</text>
          </view>
          <text class="home-recent-item__dist">{{ run.distanceKm }} 公里</text>
          <text class="home-recent-item__meta">{{ run.timeLabel }}</text>
        </view>
        <view class="home-recent-item__right">
          <text class="home-recent-item__pace">{{ run.paceLabel }}</text>
          <text class="home-recent-item__chev">›</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import HomeRecentMapThumb from './HomeRecentMapThumb.vue';

defineProps({
  items: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false }
});
defineEmits(['detail', 'startRun']);
</script>

<style lang="scss" scoped>
.home-recent-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 22rpx 0;
  border-bottom: 2rpx solid #f0f3f6;
}
.home-recent-item:last-child {
  border-bottom: none;
}
.home-recent-item__info {
  flex: 1;
  min-width: 0;
}
.home-recent-item__title-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8rpx;
}
.home-recent-item__title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1a2b3c;
}
.home-recent-item__badge {
  font-size: 18rpx;
  color: #26b586;
  background: #e8f8f2;
  padding: 2rpx 10rpx;
  border-radius: 8rpx;
}
.home-recent-item__dist {
  font-size: 24rpx;
  color: #4a5d6e;
  margin-top: 4rpx;
  display: block;
}
.home-recent-item__meta {
  font-size: 22rpx;
  color: #8a9bab;
  margin-top: 4rpx;
  display: block;
}
.home-recent-item__right {
  display: flex;
  flex-direction: row;
  align-items: center;
  flex-shrink: 0;
  margin-left: 8rpx;
}
.home-recent-item__pace {
  font-size: 26rpx;
  font-weight: 700;
  color: #26b586;
}
.home-recent-item__chev {
  font-size: 34rpx;
  color: #c5ced6;
  margin-left: 4rpx;
  line-height: 1;
}
.home-recent__skeleton .home-recent__sk-row {
  height: 100rpx;
  margin-bottom: 16rpx;
  border-radius: 14rpx;
  background: #f0f3f6;
}
.home-recent__empty {
  text-align: center;
  padding: 40rpx 0 16rpx;
}
.home-recent__empty-txt {
  font-size: 26rpx;
  color: #8a9bab;
}
.home-recent__empty-btn {
  display: inline-block;
  margin-top: 20rpx;
  padding: 12rpx 36rpx;
  border: 2rpx solid #26b586;
  border-radius: 32rpx;
  font-size: 26rpx;
  color: #26b586;
}
</style>
