<template>
  <view class="home-feature-grid">
    <view
      v-for="item in items"
      :key="item.id"
      class="home-feature-grid__item"
      @tap="$emit('tap', item.id)"
    >
      <view class="home-feature-grid__icon-wrap">
        <text class="home-feature-grid__icon">{{ item.icon }}</text>
      </view>
      <text class="home-feature-grid__label">{{ item.label }}</text>
      <text class="home-feature-grid__desc">{{ item.desc }}</text>
    </view>
  </view>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  }
});
defineEmits(['tap']);
</script>

<style lang="scss" scoped>
.home-feature-grid {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 4rpx;
}
.home-feature-grid__item {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8rpx 4rpx 4rpx;
}
.home-feature-grid__icon-wrap {
  width: 88rpx;
  height: 88rpx;
  border-radius: 24rpx;
  background: linear-gradient(180deg, #f4fcf9 0%, #e8f8f2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12rpx;
  box-shadow: 0 4rpx 16rpx rgba(38, 181, 134, 0.08);
}
.home-feature-grid__icon {
  font-size: 44rpx;
  line-height: 1;
}
.home-feature-grid__label {
  font-size: 26rpx;
  font-weight: 700;
  color: #1a2b3c;
  text-align: center;
}
.home-feature-grid__desc {
  font-size: 20rpx;
  color: #8a9bab;
  text-align: center;
  margin-top: 6rpx;
  line-height: 1.3;
  padding: 0 4rpx;
}
</style>
