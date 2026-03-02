<template>
  <view class="free-practice-container">
    <!-- 自定义导航栏 -->
    <view class="custom-nav-bar">
      <view class="nav-status-bar"></view>
      <view class="nav-content">
        <view class="nav-back" @click="goBack">
          <text class="back-icon">‹</text>
        </view>
        <text class="nav-title">自由练习</text>
      </view>
    </view>

    <view class="content-wrapper">
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

.custom-nav-bar {
  background-color: #fff;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
  
  .nav-status-bar {
    height: var(--status-bar-height);
  }
  
  .nav-content {
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    
    .nav-back {
      position: absolute;
      left: 30rpx;
      width: 60rpx;
      height: 60rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      
      .back-icon {
        font-size: 48rpx;
        color: #333;
        font-weight: bold;
      }
    }
    
    .nav-title {
      font-size: 18px;
      font-weight: bold;
      color: #333;
    }
  }
}

.content-wrapper {
  padding-top: calc(var(--status-bar-height) + 44px);
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
