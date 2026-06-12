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
    <view v-else class="home-recent__list">
      <view
        v-for="run in items"
        :key="run.id"
        class="home-recent-item"
        @tap="$emit('detail', run)"
      >
        <HomeRecentMapThumb :preview="run.trajectoryPreview" :has-track="run.hasTrack" />
        <view class="home-recent-item__info">
          <view class="home-recent-item__type-row">
            <image class="home-recent-item__type-icon" src="/static/主页户外跑图标.png" mode="aspectFit" />
            <text class="home-recent-item__type-label">{{ run.title }}</text>
          </view>
          <view class="home-recent-item__dist-row">
            <text class="home-recent-item__dist">{{ run.distanceKm }}</text>
            <text class="home-recent-item__dist-unit">公里</text>
          </view>
          <text class="home-recent-item__time">{{ run.timeLabel }}</text>
        </view>
        <view class="home-recent-item__right">
          <text class="home-recent-item__pace">{{ run.paceLabel }}</text>
          <text class="home-recent-item__pace-unit"> 配速</text>
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
.home-recent__list {
  display: flex;
  flex-direction: column;
}
.home-recent-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 22rpx 0;
  border-bottom: 2rpx solid #F0F3F6;
}
.home-recent-item:last-child {
  border-bottom: none;
}
.home-recent-item:active {
  background: #FAFBFC;
  border-radius: 12rpx;
  margin: 0 -8rpx;
  padding-left: 8rpx;
  padding-right: 8rpx;
}
.home-recent-item__info {
  flex: 1;
  min-width: 0;
  margin-left: 16rpx;
}
.home-recent-item__type-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 6rpx;
  margin-bottom: 6rpx;
}
.home-recent-item__type-icon {
  width: 40rpx;
  height: 40rpx;
}
.home-recent-item__type-label {
  font-size: 22rpx;
  font-weight: 700;
  color: #8E8E93;
}
.home-recent-item__dist-row {
  display: flex;
  flex-direction: row;
  align-items: baseline;
}
.home-recent-item__dist {
  font-size: 36rpx;
  font-weight: 900;
  color: #191C1E;
  line-height: 1;
}
.home-recent-item__dist-unit {
  font-size: 20rpx;
  font-weight: 700;
  color: #8E8E93;
  margin-left: 6rpx;
}
.home-recent-item__time {
  font-size: 20rpx;
  font-weight: 600;
  color: #C5CED6;
  margin-top: 6rpx;
  display: block;
}
.home-recent-item__right {
  display: flex;
  flex-direction: row;
  align-items: center;
  flex-shrink: 0;
}
.home-recent-item__pace {
  font-size: 28rpx;
  font-weight: 800;
  color: #33C9AB;
}
.home-recent-item__pace-unit {
  font-size: 18rpx;
  font-weight: 600;
  color: #C5CED6;
}
.home-recent-item__chev {
  font-size: 36rpx;
  color: #C5CED6;
  margin-left: 6rpx;
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
  color: #8E8E93;
}
.home-recent__empty-btn {
  display: inline-block;
  margin-top: 20rpx;
  padding: 12rpx 36rpx;
  border: 2rpx solid #33C9AB;
  border-radius: 32rpx;
  font-size: 26rpx;
  color: #33C9AB;
}
</style>