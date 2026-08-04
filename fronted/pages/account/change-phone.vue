<template>
  <view class="page"><view class="card">
    <view class="field"><text>新手机号</text><input v-model="form.phone" class="input" type="number" maxlength="11" placeholder="请输入新手机号" /></view>
    <view class="field"><text>当前密码</text><input v-model="form.password" class="input" password placeholder="用于确认本人操作" /></view>
    <button class="primary" :loading="loading" @tap="submit">确认修改</button>
  </view></view>
</template>

<script setup>
import { ref } from 'vue';
import { changePhone, patchStoredUserInfo } from '@/utils/request.js';
const loading = ref(false);
const form = ref({ phone:'', password:'' });
const submit = async () => {
  if (!/^1[3-9]\d{9}$/.test(form.value.phone)) return uni.showToast({ title:'手机号格式不正确', icon:'none' });
  if (!form.value.password) return uni.showToast({ title:'请输入当前密码', icon:'none' });
  loading.value = true;
  try {
    const res = await changePhone({ current_password:form.value.password, new_phone:form.value.phone });
    patchStoredUserInfo({ phone:res.phone });
    uni.showToast({ title:'手机号已更新', icon:'success' });
    setTimeout(() => uni.navigateBack(), 600);
  } catch(e) { uni.showToast({ title:e?.message || '修改失败', icon:'none' }); }
  finally { loading.value = false; }
};
</script>

<style scoped>
.page{min-height:100vh;background:#f5f7fa;padding:30rpx;box-sizing:border-box}.card{background:#fff;border-radius:20rpx;padding:32rpx}.field{margin-bottom:28rpx;font-size:28rpx}.input{height:88rpx;background:#f7f9fb;border-radius:14rpx;padding:0 22rpx;margin-top:12rpx}.primary{background:#20c997;color:#fff;border-radius:16rpx}
</style>
