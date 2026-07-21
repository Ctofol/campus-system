<template>
  <view class="free-practice-container">
    <page-tab-header title="自由练习" show-back theme="white" :back-handler="goBack" />

    <view class="content-wrapper page-tab-body">
      <view class="placeholder-section">
        <image class="placeholder-icon-img" src="/static/icons/icon-route.svg" mode="aspectFit" />
        <text class="placeholder-title">自由练习</text>
        <text class="placeholder-desc">自由跑步，自动记录里程与配速</text>

        <view class="start-btn" @click="startRun">开始跑步</view>
      </view>
    </view>
  </view>
</template>

<script setup>
const goBack = () => {
  uni.switchTab({ url: '/pages/tab/home' });
};
const startRun = () => {
  uni.redirectTo({ url: '/pages/run/run' });
};
</script>

<style lang="scss" scoped>
.free-practice-container {
  min-height: 100vh;
  background: #f5f7fa;
}
.content-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
.placeholder-section {
  padding: 80rpx 60rpx;
  text-align: center;
}
.placeholder-icon-img {
  width: 160rpx;
  height: 160rpx;
  margin-bottom: 40rpx;
}
.placeholder-title {
  font-size: 48rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
}
.placeholder-desc {
  font-size: 28rpx;
  color: #999;
  display: block;
  margin-bottom: 80rpx;
}
.start-btn {
  width: 400rpx;
  height: 96rpx;
  background: #33C9AB;
  color: #fff;
  border-radius: 48rpx;
  font-size: 32rpx;
  font-weight: bold;
  line-height: 96rpx;
  margin: 0 auto;
  box-shadow: 0 8rpx 24rpx rgba(51, 201, 171, 0.3);
}
.start-btn:active {
  opacity: 0.86;
}
</style>
