<template>
  <view class="manage-container">
    <!-- 自定义导航栏 -->
    <view class="custom-nav-bar">
      <view class="nav-status-bar"></view>
      <view class="nav-content">
        <text class="nav-title">综合管理</text>
      </view>
    </view>

    <view class="content-wrapper">
      <view class="grid-container">
        <!-- 基础管理 -->
        <view class="grid-item" @click="navTo('/pages/teacher/students/students')">
          <view class="icon-box purple">👥</view>
          <text class="grid-label">学员管理</text>
          <text class="grid-desc">分组、档案</text>
        </view>
        
        <view class="grid-item" @click="navTo('/pages/teacher/class/class-list')">
          <view class="icon-box cyan">🏫</view>
          <text class="grid-label">班级管理</text>
          <text class="grid-desc">排课、考勤</text>
        </view>

        <!-- 教学任务 -->
        <view class="grid-item" @click="navTo('/pages/teacher/tasks/tasks')">
          <view class="icon-box green">📢</view>
          <text class="grid-label">任务管理</text>
          <text class="grid-desc">发布、审批</text>
        </view>

        <view class="grid-item" @click="showToast('教学资源')">
          <view class="icon-box pink">📚</view>
          <text class="grid-label">教学资源</text>
          <text class="grid-desc">课件、视频</text>
        </view>
        
        <!-- 监控与数据 -->
        <view class="grid-item" @click="navTo('/pages/teacher/tests/tests')">
          <view class="icon-box blue">📊</view>
          <text class="grid-label">测试监控</text>
          <text class="grid-desc">实时数据</text>
        </view>
        
        <view class="grid-item" @click="showToast('数据导出')">
          <view class="icon-box indigo">📥</view>
          <text class="grid-label">数据导出</text>
          <text class="grid-desc">报表下载</text>
        </view>
        
        <!-- 异常与通知 -->
        <view class="grid-item" @click="navTo('/pages/teacher/exceptions/exceptions')">
          <view class="icon-box orange">⚠️</view>
          <text class="grid-label">异常处理</text>
          <text class="grid-desc">预警干预</text>
        </view>

        <view class="grid-item" @click="showToast('通知公告')">
          <view class="icon-box teal">🔔</view>
          <text class="grid-label">通知公告</text>
          <text class="grid-desc">消息推送</text>
        </view>
      </view>
    
    <view class="stats-card">
      <view class="card-header">
        <text class="card-title">数据概览</text>
      </view>
      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-val">128</text>
          <text class="stat-label">总学员</text>
        </view>
        <view class="stat-item">
          <text class="stat-val">92%</text>
          <text class="stat-label">达标率</text>
        </view>
        <view class="stat-item">
          <text class="stat-val">5</text>
          <text class="stat-label">进行中任务</text>
        </view>
      </view>
    </view>
    
    <view style="height: 120rpx;"></view>
    </view>
  </view>
</template>

<script setup>
import { onShow } from '@dcloudio/uni-app';

const navTo = (url) => {
  uni.navigateTo({ url });
};

const showToast = (title) => {
  uni.showToast({
    title: `${title} 功能开发中`,
    icon: 'none'
  });
};

const onPageShow = () => {};
const onPageHide = () => {};

defineExpose({
  onPageShow,
  onPageHide
});
</script>

<style lang="scss" scoped>
.manage-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding-bottom: 50px;
}

.custom-nav-bar {
  background-color: #fff;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  
  .nav-status-bar {
    height: var(--status-bar-height);
  }
  
  .nav-content {
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .nav-title {
      font-size: 18px;
      font-weight: bold;
      color: #333;
    }
  }
}

.content-wrapper {
  padding-top: calc(var(--status-bar-height) + 44px);
  padding-left: 30rpx;
  padding-right: 30rpx;
}

.grid-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-top: 30rpx;
}

.grid-item {
  width: 48%;
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
  box-sizing: border-box;
  
  &:active {
    transform: scale(0.98);
  }
}

.icon-box {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
  margin-bottom: 20rpx;
  
  &.purple { background-color: #f3e5f5; color: #9c27b0; }
  &.cyan { background-color: #e0f7fa; color: #00bcd4; }
  &.green { background-color: #e8f5e9; color: #4caf50; }
  &.pink { background-color: #fce4ec; color: #e91e63; }
  &.blue { background-color: #e3f2fd; color: #2196f3; }
  &.indigo { background-color: #e8eaf6; color: #3f51b5; }
  &.orange { background-color: #fff3e0; color: #ff9800; }
  &.teal { background-color: #e0f2f1; color: #009688; }
}

.grid-label {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 8rpx;
}

.grid-desc {
  font-size: 24rpx;
  color: #999;
}

.stats-card {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-top: 10rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
  
  .card-header {
    margin-bottom: 30rpx;
    padding-bottom: 20rpx;
    border-bottom: 1rpx solid #eee;
    
    .card-title {
      font-size: 32rpx;
      font-weight: bold;
      color: #333;
      border-left: 8rpx solid #20C997;
      padding-left: 20rpx;
    }
  }
  
  .stats-row {
    display: flex;
    justify-content: space-around;
    
    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      
      .stat-val {
        font-size: 40rpx;
        font-weight: bold;
        color: #20C997;
        margin-bottom: 10rpx;
      }
      
      .stat-label {
        font-size: 26rpx;
        color: #666;
      }
    }
  }
}
</style>