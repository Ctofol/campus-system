<template>
  <view class="home-section-header">
    <text class="home-section-header__title">{{ title }}</text>
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
.home-section-header__title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1a2b3c;
}
.home-section-header__more {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 24rpx;
  color: #8a9bab;
}
.home-section-header__arrow {
  margin-left: 4rpx;
  font-size: 28rpx;
}
</style>
