<template>
  <view class="free-practice-container">
    <page-tab-header title="自由练习" show-back theme="white" :back-handler="goBack" />

    <view class="content-wrapper page-tab-body">
      <!-- 占位内容 -->
      <view class="placeholder-section">
        <view class="placeholder-icon">💪</view>
        <text class="placeholder-title">自由练习</text>
        <text class="placeholder-desc">手动记录您的运动数据</text>
        
        <view class="feature-list">
          <view class="feature-item">
            <text class="feature-icon">✓</text>
            <text class="feature-text">灵活记录运动类型</text>
          </view>
          <view class="feature-item">
            <text class="feature-icon">✓</text>
            <text class="feature-text">手动输入运动数据</text>
          </view>
          <view class="feature-item">
            <text class="feature-icon">✓</text>
            <text class="feature-text">上传运动凭证</text>
          </view>
        </view>

        <view class="status-badge">
          <text class="status-text">功能开发中，敬请期待</text>
        </view>

        <button class="back-btn" @click="goBack">返回首页</button>
      </view>
    </view>
  </view>
</template>

<script setup>
const goBack = () => {
  uni.switchTab({
    url: '/pages/tab/home'
  });
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

.placeholder-icon {
  font-size: 160rpx;
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
  margin-bottom: 60rpx;
}

.feature-list {
  margin-bottom: 60rpx;
}

.feature-item {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30rpx;
}

.feature-icon {
  width: 40rpx;
  height: 40rpx;
  background: #20C997;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  margin-right: 20rpx;
}

.feature-text {
  font-size: 28rpx;
  color: #666;
}

.status-badge {
  background: #fff3cd;
  border: 2rpx solid #ffc107;
  border-radius: 40rpx;
  padding: 20rpx 40rpx;
  margin-bottom: 60rpx;
  display: inline-block;
}

.status-text {
  font-size: 26rpx;
  color: #856404;
}

.back-btn {
  width: 400rpx;
  height: 88rpx;
  background: #20C997;
  color: #fff;
  border-radius: 44rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
  margin: 0 auto;
}
</style>
