<template>
  <view class="home-feature-grid">
    <view
      v-for="item in items"
      :key="item.id"
      class="home-feature-grid__item"
      @tap="onItemTap(item.id)"
      @click="onItemTap(item.id)"
    >
      <view class="home-feature-grid__icon-wrap">
        <image
          class="home-feature-grid__icon"
          :style="{ transform: `scale(${item.iconScale || 1})` }"
          :src="item.icon"
          mode="aspectFit"
        />
      </view>
      <text class="home-feature-grid__label">{{ item.label }}</text>
      <text class="home-feature-grid__desc">{{ item.desc }}</text>
    </view>
  </view>
</template>

<script setup>
const emit = defineEmits(['feature-tap']);
defineProps({
  items: {
    type: Array,
    default: () => []
  }
});

let lastTapAt = 0;
let lastTapId = '';

const onItemTap = (id) => {
  const now = Date.now();
  if (lastTapId === id && now - lastTapAt < 350) return;
  lastTapAt = now;
  lastTapId = id;
  emit('feature-tap', id);
};
</script>

<style lang="scss" scoped>
.home-feature-grid {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 8rpx;
}
.home-feature-grid__item {
  flex: 1;
  min-width: 0;
  min-height: 148rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10rpx 4rpx 6rpx;
  box-sizing: border-box;
  border-radius: 16rpx;
}
.home-feature-grid__item:active {
  background: #F5FAFA;
}
.home-feature-grid__icon-wrap {
  width: 82rpx;
  height: 82rpx;
  border-radius: 20rpx;
  background: #F4FAF8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10rpx;
  border: 1rpx solid rgba(36, 191, 162, 0.1);
}
.home-feature-grid__icon {
  width: 64rpx;
  height: 64rpx;
  transition: transform 0.18s ease;
  transform-origin: center center;
}
.home-feature-grid__label {
  font-size: 25rpx;
  font-weight: 700;
  color: #18232E;
  text-align: center;
  line-height: 1.25;
}
.home-feature-grid__desc {
  font-size: 19rpx;
  color: #718094;
  text-align: center;
  margin-top: 5rpx;
  line-height: 1.25;
  padding: 0 4rpx;
  max-width: 144rpx;
}
</style>
