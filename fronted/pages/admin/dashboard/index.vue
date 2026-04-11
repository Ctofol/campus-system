<template>
  <view class="container">
    <view class="header">
      <text class="title">管理控制台</text>
    </view>
    
    <view class="grid-container">
      <view class="grid-item" @click="navigateTo('/pages/admin/classes/list')">
        <text class="icon">🏫</text>
        <text class="label">班级管理</text>
        <text class="desc">创建/删除班级</text>
      </view>
      
      <view class="grid-item" @click="navigateTo('/pages/admin/users/list')">
        <text class="icon">👥</text>
        <text class="label">账号管理</text>
        <text class="desc">学生/教师账号维护</text>
      </view>
      
      <view class="grid-item" @click="navigateTo('/pages/admin/import/index')">
        <text class="icon">📥</text>
        <text class="label">批量导入</text>
        <text class="desc">Excel导入数据</text>
      </view>
    </view>
    
    <view class="footer">
      <button type="warn" @click="logout">退出登录</button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';

const navigateTo = (url) => {
  uni.navigateTo({ url });
};

const logout = () => {
  uni.clearStorageSync();
  uni.reLaunch({ url: '/pages/login/login' });
};
</script>

<style>
.container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.header {
  margin-bottom: 30px;
  text-align: center;
}
.title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}
.grid-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}
.grid-item {
  width: 48%;
  background-color: #fff;
  padding: 20px;
  margin-bottom: 15px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  box-sizing: border-box;
}
.icon {
  font-size: 32px;
  margin-bottom: 10px;
}
.label {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}
.desc {
  font-size: 12px;
  color: #999;
}
.footer {
  margin-top: 40px;
}
</style>
