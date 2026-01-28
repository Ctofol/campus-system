<template>
  <view class="login-container">
    <!-- 1. 顶部 Logo 与 标题 -->
    <view class="header-section">
      <view class="logo-circle">
        <text class="logo-text">校</text>
      </view>
      <text class="app-name">大学生运动健康管理平台</text>
      <text class="app-sub-name">Professional Sports Management System</text>
    </view>

    <!-- 2. 登录卡片 -->
    <view class="login-card">
      <!-- 角色切换 Tab -->
      <view class="role-tabs">
        <view 
          class="role-tab" 
          :class="{active: currentRole === 'student'}" 
          @click="currentRole = 'student'"
        >
          <text>学生端</text>
        </view>
        <view 
          class="role-tab" 
          :class="{active: currentRole === 'teacher'}" 
          @click="currentRole = 'teacher'"
        >
          <text>教师端</text>
        </view>
      </view>

      <!-- 表单区域 -->
      <view class="form-area">
        <view class="input-group">
          <text class="input-label">{{ currentRole === 'student' ? '学号 / 手机号' : '工号 / 手机号' }}</text>
          <input 
            class="input-field" 
            v-model="loginForm.account" 
            :placeholder="currentRole === 'student' ? '请输入学号/手机号' : '请输入工号/手机号'"
            placeholder-class="placeholder-style"
          />
        </view>
        <view class="input-group">
          <text class="input-label">密码</text>
          <input 
            class="input-field" 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码"
            placeholder-class="placeholder-style"
          />
        </view>

        <!-- 登录按钮 -->
        <button 
          class="submit-btn" 
          :class="{disabled: !canSubmit}" 
          @click="handleLogin"
          :loading="loading"
        >
          登录
        </button>

        <!-- 底部链接 -->
        <view class="footer-links">
          <text class="link-text" @click="goToRegister">注册新账号</text>
          <text class="divider">|</text>
          <text class="link-text" @click="forgotPassword">忘记密码？</text>
        </view>
      </view>
    </view>

    <!-- 底部版权 -->
    <view class="copyright">
      <text>Copyright © 2026 Campus Sports System</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { login } from '@/utils/request.js';

// 状态管理
const currentRole = ref('student'); // student | teacher
const loading = ref(false);
const loginForm = ref({
  account: '',
  password: ''
});

// 计算属性：是否可提交
const canSubmit = computed(() => {
  return loginForm.value.account.length > 0 && loginForm.value.password.length > 0;
});

// 验证函数
const validateForm = () => {
  const { account, password } = loginForm.value;
  
  if (password.length < 6) {
    uni.showToast({ title: '密码长度不能少于6位', icon: 'none' });
    return false;
  }
  return true;
};

// 登录逻辑
const handleLogin = async () => {
  if (!canSubmit.value) return;
  if (!validateForm()) return;

  loading.value = true;
  
  try {
    const res = await login({
      phone: loginForm.value.account,
      password: loginForm.value.password
    });
    
    // 校验角色是否匹配
    if (res.role !== currentRole.value) {
      uni.showToast({
        title: '角色不匹配，请切换角色登录',
        icon: 'none'
      });
      loading.value = false;
      return;
    }

    // 构造用户信息
    const userInfo = {
      userId: res.user_id,
      role: res.role,
      name: res.name,
      phone: loginForm.value.account,
      // 兼容字段
      schoolId: '10001', 
      isPoliceSchool: false
    };

    // 存储全局状态
    uni.setStorageSync('token', res.access_token);
    uni.setStorageSync('userInfo', userInfo);
    uni.setStorageSync('userRole', res.role);

    uni.showToast({
      title: '登录成功',
      icon: 'success'
    });

    // 角色跳转逻辑
    setTimeout(() => {
      if (currentRole.value === 'student') {
        uni.redirectTo({ url: '/pages/home/home' });
      } else {
        uni.redirectTo({ url: '/pages/teacher/home/home' });
      }
    }, 1000);

  } catch (error) {
    console.error('Login failed:', error);
    // 错误提示已在 request.js 中处理，或者是网络层面的 reject
  } finally {
    loading.value = false;
  }
};

// 跳转注册
const goToRegister = () => {
  uni.navigateTo({ url: '/pages/register/register' });
};

// 忘记密码
const forgotPassword = () => {
  uni.showToast({ title: '请联系管理员重置密码', icon: 'none' });
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background-color: #F5F7FA;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 100rpx;
}

.header-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 60rpx;
}

.logo-circle {
  width: 120rpx;
  height: 120rpx;
  background: linear-gradient(135deg, #20C997 0%, #17a2b8 100%);
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
  box-shadow: 0 10rpx 20rpx rgba(32, 201, 151, 0.3);
}

.logo-text {
  font-size: 60rpx;
  color: #fff;
  font-weight: bold;
}

.app-name {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 8rpx;
}

.app-sub-name {
  font-size: 20rpx;
  color: #999;
  letter-spacing: 2rpx;
}

.login-card {
  width: 650rpx;
  background: #fff;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 30rpx rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.role-tabs {
  display: flex;
  background: #F8F9FA;
  border-bottom: 1rpx solid #EEE;
}

.role-tab {
  flex: 1;
  text-align: center;
  padding: 30rpx 0;
  font-size: 28rpx;
  color: #666;
  position: relative;
  transition: all 0.3s;
}

.role-tab.active {
  color: #20C997;
  font-weight: bold;
  background: #fff;
}

.role-tab.active::after {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40rpx;
  height: 6rpx;
  background: #20C997;
  border-radius: 0 0 6rpx 6rpx;
}

.form-area {
  padding: 40rpx;
}

.input-group {
  margin-bottom: 40rpx;
}

.input-label {
  display: block;
  font-size: 26rpx;
  color: #333;
  margin-bottom: 16rpx;
  font-weight: 500;
}

.input-field {
  height: 88rpx;
  background: #F8F9FA;
  border-radius: 12rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #333;
  border: 2rpx solid transparent;
  transition: all 0.3s;
}

.input-field:focus {
  background: #fff;
  border-color: #20C997;
}

.placeholder-style {
  color: #BBB;
}

.submit-btn {
  background: linear-gradient(90deg, #20C997, #17a2b8);
  color: #fff;
  font-size: 32rpx;
  font-weight: bold;
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 44rpx;
  margin-top: 60rpx;
  box-shadow: 0 10rpx 20rpx rgba(32, 201, 151, 0.3);
}

.submit-btn.disabled {
  background: #E0E0E0;
  color: #999;
  box-shadow: none;
}

.submit-btn::after {
  border: none;
}

.footer-links {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 40rpx;
}

.link-text {
  font-size: 26rpx;
  color: #666;
  padding: 10rpx;
}

.divider {
  color: #ddd;
  margin: 0 10rpx;
  font-size: 22rpx;
}

.copyright {
  margin-top: auto;
  margin-bottom: 40rpx;
  font-size: 20rpx;
  color: #ccc;
}
</style>
