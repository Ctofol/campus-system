<template>
  <view class="home-section-header">
    <view class="home-section-header__left">
      <view class="home-section-header__bar" />
      <text class="home-section-header__title">{{ title }}</text>
    </view>
    <view v-if="showMore" class="home-section-header__more" @tap="$emit('more')">
      <text>{{ moreText }}</text>
      <text class="home-section-header__arrow">›</text>
    </view>
  </view>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  moreText: { type: String, default: '查看全部' },
  showMore: { type: Boolean, default: true }
});
defineEmits(['more']);
</script>

<style lang="scss" scoped>
.home-section-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18rpx;
}
.home-section-header__left {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10rpx;
}
.home-section-header__bar {
  width: 6rpx;
  height: 24rpx;
  border-radius: 3rpx;
  background: #24BFA2;
}
.home-section-header__title {
  font-size: 28rpx;
  font-weight: 800;
  color: #18232E;
}
.home-section-header__more {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 22rpx;
  color: #718094;
  font-weight: 600;
  padding: 6rpx 0 6rpx 10rpx;
}
.home-section-header__more:active {
  opacity: 0.72;
}
.home-section-header__arrow {
  margin-left: 2rpx;
  font-size: 26rpx;
  color: #B8C3CC;
}
</style>
