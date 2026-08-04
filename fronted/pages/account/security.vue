<template>
  <view class="page">
    <view class="item" @tap="goPassword"><text>修改密码</text><text class="right">›</text></view>
    <view class="item" @tap="goPhone">
      <text>修改手机号</text><view><text class="muted">{{ maskedPhone }}</text><text class="right">›</text></view>
    </view>
    <text class="tip">修改密码后，其他设备上的登录状态将失效。</text>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { request, patchStoredUserInfo } from '@/utils/request.js';

const phone = ref('');
const maskedPhone = computed(() => phone.value ? phone.value.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '未绑定');
onShow(async () => {
  try {
    const profile = await request({ url: '/users/profile', method: 'GET' });
    phone.value = profile.phone || '';
    patchStoredUserInfo({ phone: phone.value });
  } catch (_) {}
});
const goPassword = () => uni.navigateTo({ url: '/pages/account/change-password' });
const goPhone = () => uni.navigateTo({ url: '/pages/account/change-phone' });
</script>

<style scoped>
.page { min-height:100vh; background:#f5f7fa; padding:30rpx; box-sizing:border-box; }
.item { background:#fff; border-radius:16rpx; padding:32rpx; margin-bottom:18rpx; display:flex; justify-content:space-between; font-size:30rpx; }
.muted { color:#8a94a2; font-size:26rpx; margin-right:16rpx; }.right { color:#aab2bd; }.tip { color:#8a94a2; font-size:24rpx; line-height:1.6; }
</style>
