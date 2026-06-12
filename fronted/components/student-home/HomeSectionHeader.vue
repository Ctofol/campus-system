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
  margin-bottom: 20rpx;
}
.home-section-header__left {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12rpx;
}
.home-section-header__bar {
  width: 4rpx;
  height: 28rpx;
  border-radius: 2rpx;
  background: #33C9AB;
}
.home-section-header__title {
  font-size: 30rpx;
  font-weight: 800;
  color: #191C1E;
}
.home-section-header__more {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 24rpx;
  color: #8E8E93;
  font-weight: 600;
}
.home-section-header__arrow {
  margin-left: 4rpx;
  font-size: 28rpx;
}
</style>