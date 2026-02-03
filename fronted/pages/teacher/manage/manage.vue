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
    <CustomTabBar current="/pages/teacher/manage/manage" />
    </view>
  </view>
</template>

<script setup>
import { onShow } from '@dcloudio/uni-app';
import CustomTabBar from '@/components/CustomTabBar/CustomTabBar.vue';

onShow(() => {
  // 隐藏左上角 Home 按钮
  uni.hideHomeButton && uni.hideHomeButton();
});

const navTo = (url) => {
  uni.navigateTo({ url });
};

const showToast = (title) => {
  uni.showToast({
    title: `${title}功能开发中`,
    icon: 'none'
  });
};
</script>

<style scoped>
.manage-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

/* 自定义导航栏 */
.custom-nav-bar {
  background: #fff;
  width: 100%;
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid #eee;
}
.nav-status-bar {
  height: var(--status-bar-height);
  width: 100%;
}
.nav-content {
  height: 44px; /* 标准导航栏高度 */
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.nav-title {
  color: #333;
  font-size: 32rpx;
  font-weight: bold;
}

.content-wrapper {
  padding: 30rpx;
  flex: 1;
}

.grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30rpx;
  margin-bottom: 40rpx;
}
.grid-item {
  background: #fff;
  padding: 40rpx 30rpx;
  border-radius: 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.03);
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
}
.purple { background: #f3e5f5; color: #9c27b0; }
.green { background: #e8f5e9; color: #4caf50; }
.blue { background: #e3f2fd; color: #2196f3; }
.orange { background: #fff3e0; color: #ff9800; }
.cyan { background: #e0f7fa; color: #00bcd4; }
.pink { background: #fce4ec; color: #e91e63; }
.indigo { background: #e8eaf6; color: #3f51b5; }
.teal { background: #e0f2f1; color: #009688; }

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
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}
.card-header {
  margin-bottom: 30rpx;
  padding-bottom: 20rpx;
  border-bottom: 1px solid #f5f5f5;
}
.card-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}
.stats-row {
  display: flex;
  justify-content: space-around;
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.stat-val {
  font-size: 40rpx;
  font-weight: bold;
  color: #20C997;
  margin-bottom: 10rpx;
}
.stat-label {
  font-size: 24rpx;
  color: #666;
}
</style>