<template>
  <view v-if="showPopup" class="privacy-mask">
    <view class="privacy-container">
      <view class="privacy-title">用户隐私保护提示</view>
      <view class="privacy-content">
        感谢您使用翊晨运动。在您使用本小程序前，请您务必仔细阅读
        <text class="privacy-link" @click="openPrivacyContract">《用户隐私保护指引》</text>。
        当您点击同意并开始使用后续服务时，即表示您已理解并同意规定内容。
      </view>
      <view class="privacy-footer">
        <button class="btn-refuse" @click="handleRefuse">拒绝</button>
        <button 
          class="btn-agree" 
          open-type="agreePrivacyAuthorization"
          @agreeprivacyauthorization="handleAgree"
        >同意并继续</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const showPopup = ref(false);
let resolvePrivacyAuthorization = null;

onMounted(() => {
  if (wx.onNeedPrivacyAuthorization) {
    wx.onNeedPrivacyAuthorization(resolve => {
      showPopup.value = true;
      resolvePrivacyAuthorization = resolve;
    });
  }
});

const openPrivacyContract = () => {
  wx.openPrivacyContract({
    fail: () => {
      uni.showToast({ title: '打开隐私协议失败', icon: 'none' });
    }
  });
};

const handleRefuse = () => {
  showPopup.value = false;
  uni.showToast({ title: '拒绝后部分功能将无法使用', icon: 'none' });
  if (resolvePrivacyAuthorization) {
    resolvePrivacyAuthorization({ buttonId: 'disagree-btn', event: 'disagree' });
    resolvePrivacyAuthorization = null;
  }
};

const handleAgree = () => {
  showPopup.value = false;
  if (resolvePrivacyAuthorization) {
    resolvePrivacyAuthorization({ buttonId: 'agree-btn', event: 'agree' });
    resolvePrivacyAuthorization = null;
  }
};
</script>

<style scoped>
.privacy-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4rpx);
}

.privacy-container {
  width: 600rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx;
  box-shadow: 0 10rpx 30rpx rgba(0,0,0,0.2);
}

.privacy-title {
  font-size: 34rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 30rpx;
  text-align: center;
}

.privacy-content {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
  margin-bottom: 40rpx;
}

.privacy-link {
  color: #20C997;
  text-decoration: underline;
  margin: 0 4rpx;
}

.privacy-footer {
  display: flex;
  justify-content: space-between;
  gap: 20rpx;
}

.btn-refuse, .btn-agree {
  flex: 1;
  height: 80rpx;
  line-height: 80rpx;
  font-size: 28rpx;
  border-radius: 40rpx;
  margin: 0;
}

.btn-refuse {
  background: #f5f5f5;
  color: #999;
}

.btn-agree {
  background: linear-gradient(90deg, #20C997, #17a2b8);
  color: #fff;
}

.btn-agree::after {
  border: none;
}
</style>
