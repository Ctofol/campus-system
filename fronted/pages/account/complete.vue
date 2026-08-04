<template>
  <view class="page">
    <view class="card">
      <text class="title">首次设置账号</text>
      <text class="desc">为保障账号安全，请核对姓名、绑定手机号并修改初始密码。完成后才能使用运动和教学功能。</text>

      <view class="field">
        <text class="label">真实姓名</text>
        <input v-model="form.realName" class="input" placeholder="请输入学校档案中的姓名" maxlength="30" />
      </view>
      <view class="field">
        <text class="label">手机号</text>
        <input v-model="form.phone" class="input" type="number" maxlength="11" placeholder="用于登录和账号联系" />
      </view>
      <view class="field">
        <text class="label">昵称（选填）</text>
        <input v-model="form.nickname" class="input" maxlength="32" placeholder="用于个人首页和跑团展示" />
      </view>
      <view class="field">
        <text class="label">新密码</text>
        <input v-model="form.password" class="input" password maxlength="20" placeholder="8–20 位，须包含字母和数字" />
      </view>
      <view class="field">
        <text class="label">确认新密码</text>
        <input v-model="form.confirmPassword" class="input" password maxlength="20" placeholder="请再次输入新密码" />
      </view>

      <button class="primary" :loading="loading" @tap="submit">完成设置</button>
      <text class="logout" @tap="logout">退出并返回登录</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { completeAccount, getStoredUserInfo } from '@/utils/request.js';

const loading = ref(false);
const stored = getStoredUserInfo();
const form = ref({
  realName: stored.name || '',
  phone: '',
  nickname: '',
  password: '',
  confirmPassword: ''
});

const submit = async () => {
  const value = form.value;
  if (!value.realName.trim()) return uni.showToast({ title: '请输入真实姓名', icon: 'none' });
  if (!/^1[3-9]\d{9}$/.test(value.phone.trim())) return uni.showToast({ title: '手机号格式不正确', icon: 'none' });
  if (value.password.length < 8 || value.password.length > 20 || !/[A-Za-z]/.test(value.password) || !/\d/.test(value.password)) {
    return uni.showToast({ title: '密码须为 8–20 位并包含字母和数字', icon: 'none' });
  }
  if (value.password !== value.confirmPassword) return uni.showToast({ title: '两次密码不一致', icon: 'none' });

  loading.value = true;
  try {
    const res = await completeAccount({
      real_name: value.realName.trim(),
      phone: value.phone.trim(),
      nickname: value.nickname.trim() || null,
      new_password: value.password
    });
    const userInfo = {
      ...stored,
      userId: res.user_id,
      role: res.role,
      name: res.name,
      nickname: res.nickname || '',
      display_name: res.display_name || res.name,
      phone: res.phone || '',
      mustCompleteAccount: false
    };
    uni.setStorageSync('token', res.access_token);
    uni.setStorageSync('userInfo', userInfo);
    uni.setStorageSync('userRole', res.role);
    uni.showToast({ title: '设置完成', icon: 'success' });
    setTimeout(() => uni.reLaunch({ url: '/pages/tab/home' }), 500);
  } catch (e) {
    uni.showToast({ title: e?.message || '设置失败', icon: 'none', duration: 2500 });
  } finally {
    loading.value = false;
  }
};

const logout = () => {
  uni.removeStorageSync('token');
  uni.removeStorageSync('userInfo');
  uni.removeStorageSync('userRole');
  uni.reLaunch({ url: '/pages/login/login' });
};
</script>

<style scoped>
.page { min-height:100vh; background:#f5f7fa; padding:48rpx 30rpx; box-sizing:border-box; }
.card { background:#fff; border-radius:24rpx; padding:40rpx 32rpx; box-shadow:0 10rpx 30rpx rgba(24,39,75,.06); }
.title { display:block; font-size:40rpx; font-weight:700; color:#1f2d3d; }
.desc { display:block; margin:16rpx 0 34rpx; color:#77808d; font-size:26rpx; line-height:1.6; }
.field { margin-bottom:26rpx; }
.label { display:block; margin-bottom:12rpx; color:#334155; font-size:28rpx; }
.input { height:88rpx; padding:0 24rpx; border-radius:14rpx; background:#f7f9fb; font-size:28rpx; }
.primary { margin-top:16rpx; background:#20c997; color:#fff; border-radius:16rpx; }
.logout { display:block; text-align:center; color:#84909d; font-size:26rpx; margin-top:28rpx; }
</style>
