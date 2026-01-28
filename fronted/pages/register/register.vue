<template>
  <view class="register-container">
    <view class="header-section">
      <text class="title">注册新账号</text>
      <text class="sub-title">加入校园运动健康平台</text>
    </view>

    <view class="register-card">
      <!-- 步骤1：角色选择 -->
      <view class="role-select-box" v-if="step === 1">
        <text class="step-title">请选择您的身份</text>
        <view class="role-options">
          <view 
            class="role-option" 
            :class="{active: registerForm.role === 'student'}"
            @click="selectRole('student')"
          >
            <text class="role-icon">👨‍🎓</text>
            <text class="role-name">我是学生</text>
          </view>
          <view 
            class="role-option" 
            :class="{active: registerForm.role === 'teacher'}"
            @click="selectRole('teacher')"
          >
            <text class="role-icon">👨‍🏫</text>
            <text class="role-name">我是教师</text>
          </view>
        </view>
        <button class="next-btn" @click="nextStep">下一步</button>
      </view>

      <!-- 步骤2：信息填写 -->
      <view class="form-box" v-else>
        <view class="form-header">
          <text class="back-text" @click="step = 1">返回修改身份</text>
          <text class="current-role">当前身份：{{ registerForm.role === 'student' ? '学生' : '教师' }}</text>
        </view>

        <!-- 基础信息 -->
        <view class="section-title">基础信息</view>
        <view class="input-item">
          <input class="input" v-model="registerForm.name" placeholder="真实姓名" />
        </view>
        <view class="input-item">
          <input class="input" v-model="registerForm.phone" type="number" placeholder="手机号码" />
        </view>
        <view class="input-item code-box">
          <input class="input" v-model="registerForm.code" type="number" placeholder="验证码" />
          <text class="get-code" @click="getCode">获取验证码</text>
        </view>
        <view class="input-item">
          <input class="input" v-model="registerForm.password" type="password" placeholder="设置密码 (6-16位)" />
        </view>
        <view class="input-item">
          <input class="input" v-model="registerForm.confirmPwd" type="password" placeholder="确认密码" />
        </view>

        <!-- 身份扩展信息 -->
        <view class="section-title">身份信息</view>
        
        <!-- 学生扩展字段 -->
        <template v-if="registerForm.role === 'student'">
          <view class="input-item">
            <input class="input" v-model="registerForm.school" placeholder="学校名称" />
          </view>
          <view class="input-item">
            <input class="input" v-model="registerForm.college" placeholder="所属学院" />
          </view>
          <view class="input-item">
            <input class="input" v-model="registerForm.major" placeholder="专业" />
          </view>
          <view class="input-item">
            <input class="input" v-model="registerForm.class" placeholder="班级 (如: 22级3班)" />
          </view>
        </template>

        <!-- 教师扩展字段 -->
        <template v-if="registerForm.role === 'teacher'">
          <view class="input-item">
            <input class="input" v-model="registerForm.school" placeholder="学校名称" />
          </view>
          <view class="input-item">
            <input class="input" v-model="registerForm.empId" placeholder="教师工号" />
          </view>
          <view class="input-item">
            <input class="input" v-model="registerForm.department" placeholder="所属部门 (如: 警体教研室)" />
          </view>
        </template>

        <!-- 学校类型适配 -->
        <view class="police-switch-box">
          <view class="switch-header">
            <text class="switch-label">警校/军校用户</text>
            <switch :checked="registerForm.isPoliceSchool" @change="togglePolice" color="#20C997" style="transform:scale(0.8)" />
          </view>
          <text class="switch-tip" v-if="registerForm.isPoliceSchool">
            * 勾选后，系统将开启适配警校/军校体测标准的专项训练模块
          </text>
        </view>

        <!-- 注册按钮 -->
        <button class="submit-btn" @click="handleRegister" :loading="loading">立即注册</button>
      </view>

      <view class="footer-link">
        <text class="link-text" @click="goToLogin">已有账号？返回登录</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { register } from '@/utils/request.js';

const step = ref(1);
const loading = ref(false);

const registerForm = ref({
  role: 'student', // student | teacher
  name: '',
  phone: '',
  code: '',
  password: '',
  confirmPwd: '',
  // 扩展
  school: '',
  college: '',
  major: '',
  class: '',
  empId: '',
  department: '',
  isPoliceSchool: false
});

const selectRole = (role) => {
  registerForm.value.role = role;
};

const nextStep = () => {
  step.value = 2;
};

const togglePolice = (e) => {
  registerForm.value.isPoliceSchool = e.detail.value;
};

const goToLogin = () => {
  uni.navigateBack();
};

const getCode = () => {
  if (!registerForm.value.phone) {
    uni.showToast({ title: '请先输入手机号', icon: 'none' });
    return;
  }
  const phoneRegex = /^1[3-9]\d{9}$/;
  if (!phoneRegex.test(registerForm.value.phone)) {
    uni.showToast({ title: '手机号格式不正确', icon: 'none' });
    return;
  }
  
  uni.showToast({ title: '验证码已发送', icon: 'success' });
};

const handleRegister = async () => {
  const form = registerForm.value;
  
  // 基础非空校验
  if (!form.name || !form.phone || !form.password) {
    uni.showToast({ title: '请完善基础信息', icon: 'none' });
    return;
  }

  // 手机号格式校验
  const phoneRegex = /^1[3-9]\d{9}$/;
  if (!phoneRegex.test(form.phone)) {
    uni.showToast({ title: '请输入正确的手机号', icon: 'none' });
    return;
  }

  // 密码长度校验
  if (form.password.length < 6) {
    uni.showToast({ title: '密码长度不能少于6位', icon: 'none' });
    return;
  }

  // 确认密码校验
  if (form.password !== form.confirmPwd) {
    uni.showToast({ title: '两次密码不一致', icon: 'none' });
    return;
  }
  
  // 身份校验
  if (form.role === 'student' && (!form.school || !form.class)) {
    uni.showToast({ title: '请完善学生信息', icon: 'none' });
    return;
  }
  if (form.role === 'teacher' && (!form.empId || !form.department)) {
    uni.showToast({ title: '请完善教师信息', icon: 'none' });
    return;
  }

  loading.value = true;
  
  try {
    // 调用后端注册接口
    // 注意：后端目前MVP版本只接收基础字段，扩展字段（school, college等）暂未存储
    await register({
        phone: form.phone,
        name: form.name,
        role: form.role,
        password: form.password
    });

    uni.showToast({
      title: '注册成功',
      icon: 'success'
    });
    
    // 注册成功后返回登录页
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);

  } catch (error) {
    console.error('Register failed:', error);
    // 错误处理已在 request.js 中包含
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background-color: #F5F7FA;
  padding: 40rpx;
  padding-top: 80rpx;
}

.header-section {
  margin-bottom: 50rpx;
}

.title {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.sub-title {
  font-size: 26rpx;
  color: #999;
}

.register-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
}

/* 步骤1 */
.step-title {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  text-align: center;
  margin-bottom: 60rpx;
}

.role-options {
  display: flex;
  justify-content: space-between;
  margin-bottom: 60rpx;
}

.role-option {
  width: 45%;
  background: #F8F9FA;
  border: 2rpx solid transparent;
  border-radius: 16rpx;
  padding: 40rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all 0.3s;
}

.role-option.active {
  background: #E3FDF5;
  border-color: #20C997;
}

.role-icon {
  font-size: 60rpx;
  margin-bottom: 20rpx;
}

.role-name {
  font-size: 28rpx;
  color: #333;
  font-weight: bold;
}

.role-option.active .role-name {
  color: #20C997;
}

.next-btn {
  background: #20C997;
  color: #fff;
  border-radius: 44rpx;
  font-size: 30rpx;
}

/* 步骤2 */
.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40rpx;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #eee;
}

.back-text {
  font-size: 24rpx;
  color: #666;
}

.current-role {
  font-size: 24rpx;
  color: #20C997;
  font-weight: bold;
}

.section-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin: 30rpx 0 20rpx;
  padding-left: 16rpx;
  border-left: 6rpx solid #20C997;
}

.input-item {
  margin-bottom: 24rpx;
  background: #F8F9FA;
  border-radius: 12rpx;
  padding: 20rpx;
}

.input {
  font-size: 28rpx;
  color: #333;
  width: 100%;
}

.code-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.get-code {
  font-size: 24rpx;
  color: #20C997;
  padding: 10rpx 20rpx;
  border-left: 1rpx solid #ddd;
}

.police-switch-box {
  background: #F0F7FF;
  padding: 20rpx;
  border-radius: 12rpx;
  margin: 40rpx 0;
}

.switch-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10rpx;
}

.switch-label {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
}

.switch-tip {
  font-size: 22rpx;
  color: #666;
  display: block;
  line-height: 1.4;
}

.submit-btn {
  background: linear-gradient(90deg, #20C997, #17a2b8);
  color: #fff;
  border-radius: 44rpx;
  margin-top: 40rpx;
  font-weight: bold;
}

.footer-link {
  text-align: center;
  margin-top: 40rpx;
}

.link-text {
  font-size: 26rpx;
  color: #666;
}
</style>
