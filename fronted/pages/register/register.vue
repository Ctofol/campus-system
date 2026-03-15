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
        <view class="input-item" v-if="registerForm.role === 'student'">
          <input class="input" v-model="registerForm.studentId" placeholder="学号（与档案一致）" />
        </view>
        <view class="hint-text" v-if="registerForm.role === 'student'">
          请输入管理员导入档案时的学号，系统将自动匹配班级与性别信息
        </view>
        <view class="input-item">
          <input class="input" v-model="registerForm.phone" type="number" placeholder="手机号码" />
        </view>
        <view class="input-item code-box">
          <input class="input" v-model="registerForm.code" placeholder="输入右侧验证码" />
          <image :src="captchaImage" class="captcha-img" @click="fetchCaptcha" mode="heightFix" />
        </view>
        <view class="input-item">
          <input class="input" v-model="registerForm.password" type="password" placeholder="设置密码 (6-16位)" />
        </view>
        <view class="input-item">
          <input class="input" v-model="registerForm.confirmPwd" type="password" placeholder="确认密码" />
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
import { ref, onMounted } from 'vue';
import { register, request } from '@/utils/request.js';

const step = ref(1);
const loading = ref(false);
const captchaImage = ref('');
const captchaKey = ref('');

const registerForm = ref({
  role: 'student', // student | teacher
  name: '',
  studentId: '',
  phone: '',
  code: '',
  password: '',
  confirmPwd: '',
  // 扩展（当前版本不再收集学校/班级，由后台档案自动绑定）
  school: '',
  class: '',
  empId: ''
});

const selectRole = (role) => {
  registerForm.value.role = role;
};

const nextStep = () => {
  step.value = 2;
  fetchCaptcha();
};

const fetchCaptcha = () => {
  request({ url: '/common/captcha' }).then(res => {
    captchaImage.value = res.image;
    captchaKey.value = res.key;
  }).catch(err => {
    console.error('Fetch captcha failed', err);
    uni.showToast({ title: '验证码加载失败', icon: 'none' });
  });
};

const goToLogin = () => {
  uni.navigateBack();
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
  
  // 验证码校验
  if (!form.code) {
    uni.showToast({ title: '请输入验证码', icon: 'none' });
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
  if (form.role === 'student' && !form.studentId) {
    uni.showToast({ title: '请输入学号', icon: 'none' });
    return;
  }

  loading.value = true;
  
  try {
    // 调用后端注册接口
    await register({
        phone: form.phone,
        name: form.name,
        role: form.role,
        student_id: form.role === 'student' ? form.studentId : null,
        password: form.password,
        captcha_code: form.code,
        captcha_key: captchaKey.value
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
    // 刷新验证码
    fetchCaptcha();
    form.code = '';
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

.captcha-img {
  height: 60rpx;
  width: 160rpx;
  margin-left: 20rpx;
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
