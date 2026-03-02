<template>
  <view class="container">
    <view class="header">
      <text class="title">网络连接测试</text>
    </view>
    
    <view class="test-section">
      <button class="test-btn" @click="testConnection">测试后端连接</button>
      <view class="result" v-if="testResult">
        <text class="result-title">测试结果:</text>
        <text class="result-text" :class="{ success: testResult.success, error: !testResult.success }">
          {{ testResult.message }}
        </text>
        <view v-if="testResult.data" class="result-data">
          <text class="data-title">返回数据:</text>
          <text class="data-text">{{ JSON.stringify(testResult.data, null, 2) }}</text>
        </view>
      </view>
    </view>
    
    <view class="config-section">
      <text class="config-title">当前配置:</text>
      <text class="config-text">BASE_URL: {{ baseUrl }}</text>
      <text class="config-text">平台: {{ platform }}</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { BASE_URL } from '@/utils/request.js';

const testResult = ref(null);
const baseUrl = ref(BASE_URL);
const platform = ref('');

// 获取平台信息
uni.getSystemInfo({
  success: (res) => {
    platform.value = res.platform;
  }
});

const testConnection = async () => {
  testResult.value = null;
  
  try {
    uni.showLoading({ title: '测试中...' });
    
    const response = await new Promise((resolve, reject) => {
      uni.request({
        url: `${BASE_URL}/common/captcha`,
        method: 'GET',
        success: resolve,
        fail: reject
      });
    });
    
    uni.hideLoading();
    
    if (response.statusCode === 200) {
      testResult.value = {
        success: true,
        message: '连接成功！',
        data: response.data
      };
    } else {
      testResult.value = {
        success: false,
        message: `连接失败: ${response.statusCode} ${response.errMsg || ''}`
      };
    }
  } catch (error) {
    uni.hideLoading();
    testResult.value = {
      success: false,
      message: `连接错误: ${error.errMsg || error.message || JSON.stringify(error)}`
    };
  }
};
</script>

<style lang="scss" scoped>
.container {
  padding: 40rpx;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  text-align: center;
  margin-bottom: 60rpx;
}

.title {
  font-size: 48rpx;
  font-weight: bold;
  color: #333;
}

.test-section {
  margin-bottom: 60rpx;
}

.test-btn {
  width: 100%;
  height: 100rpx;
  background-color: #007aff;
  color: white;
  border: none;
  border-radius: 20rpx;
  font-size: 32rpx;
  margin-bottom: 40rpx;
}

.result {
  background-color: white;
  padding: 40rpx;
  border-radius: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.result-title {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
  color: #333;
}

.result-text {
  display: block;
  font-size: 28rpx;
  margin-bottom: 20rpx;
  
  &.success {
    color: #4cd964;
  }
  
  &.error {
    color: #ff3b30;
  }
}

.result-data {
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 2rpx solid #eee;
}

.data-title {
  display: block;
  font-size: 28rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
  color: #666;
}

.data-text {
  display: block;
  font-size: 24rpx;
  color: #999;
  background-color: #f8f8f8;
  padding: 20rpx;
  border-radius: 10rpx;
  font-family: monospace;
  white-space: pre-wrap;
}

.config-section {
  background-color: white;
  padding: 40rpx;
  border-radius: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.config-title {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
  color: #333;
}

.config-text {
  display: block;
  font-size: 28rpx;
  margin-bottom: 10rpx;
  color: #666;
}
</style>