<template>
  <view class="container">
    <view class="title">网络连接测试</view>
    
    <view class="info">
      <text>后端地址: {{ baseUrl }}</text>
    </view>
    
    <button @tap="testCaptcha" class="test-btn">测试验证码接口</button>
    <button @tap="testLogin" class="test-btn">测试登录接口</button>
    
    <view class="result" v-if="result">
      <text class="result-title">测试结果:</text>
      <text class="result-text">{{ result }}</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { BASE_URL } from '@/utils/request.js';

const baseUrl = ref(BASE_URL);
const result = ref('');

const testCaptcha = () => {
  result.value = '正在测试...';
  
  uni.request({
    url: `${BASE_URL}/common/captcha`,
    method: 'GET',
    success: (res) => {
      console.log('Captcha test success:', res);
      result.value = `成功! 状态码: ${res.statusCode}\n返回数据: ${JSON.stringify(res.data).substring(0, 100)}...`;
    },
    fail: (err) => {
      console.error('Captcha test fail:', err);
      result.value = `失败! 错误: ${JSON.stringify(err)}`;
    }
  });
};

const testLogin = () => {
  result.value = '正在测试...';
  
  uni.request({
    url: `${BASE_URL}/auth/login`,
    method: 'POST',
    data: {
      phone: '13800138000',
      password: '123456'
    },
    header: {
      'Content-Type': 'application/json'
    },
    success: (res) => {
      console.log('Login test success:', res);
      result.value = `成功! 状态码: ${res.statusCode}\n返回数据: ${JSON.stringify(res.data)}`;
    },
    fail: (err) => {
      console.error('Login test fail:', err);
      result.value = `失败! 错误: ${JSON.stringify(err)}`;
    }
  });
};
</script>

<style scoped>
.container {
  padding: 40rpx;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  margin-bottom: 40rpx;
  text-align: center;
}

.info {
  background: #f5f5f5;
  padding: 20rpx;
  border-radius: 8rpx;
  margin-bottom: 40rpx;
}

.test-btn {
  margin-bottom: 20rpx;
  background: #20C997;
  color: white;
}

.result {
  margin-top: 40rpx;
  padding: 20rpx;
  background: #f5f5f5;
  border-radius: 8rpx;
}

.result-title {
  font-weight: bold;
  display: block;
  margin-bottom: 10rpx;
}

.result-text {
  word-break: break-all;
}
</style>
