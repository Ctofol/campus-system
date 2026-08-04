<template>
  <view class="page"><view class="card">
    <view class="field"><text>当前密码</text><input v-model="form.oldPassword" class="input" password placeholder="请输入当前密码" /></view>
    <view class="field"><text>新密码</text><input v-model="form.newPassword" class="input" password maxlength="20" placeholder="8–20 位，包含字母和数字" /></view>
    <view class="field"><text>确认新密码</text><input v-model="form.confirmPassword" class="input" password maxlength="20" placeholder="再次输入新密码" /></view>
    <button class="primary" :loading="loading" @tap="submit">确认修改</button>
  </view></view>
</template>

<script setup>
import { ref } from 'vue';
import { changePassword } from '@/utils/request.js';
const loading = ref(false);
const form = ref({ oldPassword:'', newPassword:'', confirmPassword:'' });
const submit = async () => {
  const f = form.value;
  if (!f.oldPassword) return uni.showToast({ title:'请输入当前密码', icon:'none' });
  if (f.newPassword.length < 8 || f.newPassword.length > 20 || !/[A-Za-z]/.test(f.newPassword) || !/\d/.test(f.newPassword)) return uni.showToast({ title:'新密码须包含字母和数字', icon:'none' });
  if (f.newPassword !== f.confirmPassword) return uni.showToast({ title:'两次密码不一致', icon:'none' });
  loading.value = true;
  try {
    await changePassword({ old_password:f.oldPassword, new_password:f.newPassword });
    uni.removeStorageSync('token'); uni.removeStorageSync('userInfo'); uni.removeStorageSync('userRole');
    uni.showModal({ title:'修改成功', content:'请使用新密码重新登录', showCancel:false, success:() => uni.reLaunch({ url:'/pages/login/login' }) });
  } catch(e) { uni.showToast({ title:e?.message || '修改失败', icon:'none' }); }
  finally { loading.value = false; }
};
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fa;padding:30rpx;box-sizing:border-box}.card{background:#fff;border-radius:20rpx;padding:32rpx}.field{margin-bottom:28rpx;font-size:28rpx}.input{height:88rpx;background:#f7f9fb;border-radius:14rpx;padding:0 22rpx;margin-top:12rpx}.primary{background:#20c997;color:#fff;border-radius:16rpx}
</style>
