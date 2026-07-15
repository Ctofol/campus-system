<template>
  <view class="mine-container">
    <page-tab-header title="个人中心" theme="white" show-back />

    <view class="content-wrapper page-tab-body">
      <view class="user-card">
        <image class="avatar-img" :src="avatarDisplay" mode="aspectFill" />
        <view class="info">
          <view class="name-row" @tap="handlePersonalInfo">
            <text class="name">{{ userInfo.name || '教师' }}</text>
            <image class="edit-icon-img" src="/static/icons/icon-edit-profile.svg" mode="aspectFit" />
          </view>
          <text class="role">{{ userInfo.subject || userInfo.signature || '公共体育教研部' }}</text>
        </view>
      </view>

      <view class="menu-list">
        <view class="menu-item" @tap="handlePersonalInfo">
          <view class="menu-left">
            <view class="menu-icon-shell">
              <image class="menu-icon-img" src="/static/icons/teacher-about.svg" mode="aspectFit" />
            </view>
            <text class="menu-text">个人信息设置</text>
          </view>
          <view class="arrow"></view>
        </view>

        <view class="menu-item" @tap="handleAccountSecurity">
          <view class="menu-left">
            <view class="menu-icon-shell">
              <image class="menu-icon-img" src="/static/icons/teacher-lock.svg" mode="aspectFit" />
            </view>
            <text class="menu-text">账号安全</text>
          </view>
          <view class="arrow"></view>
        </view>

        <view class="menu-item" @tap="handleNotifications">
          <view class="menu-left">
            <view class="menu-icon-shell">
              <image class="menu-icon-img" src="/static/icons/teacher-notification.svg" mode="aspectFit" />
            </view>
            <text class="menu-text">系统通知</text>
          </view>
          <view class="badge" v-if="notificationCount > 0">{{ notificationCount }}</view>
          <view class="arrow"></view>
        </view>

        <view class="menu-item" @tap="handleHelpFeedback">
          <view class="menu-left">
            <view class="menu-icon-shell">
              <image class="menu-icon-img" src="/static/icons/teacher-feedback.svg" mode="aspectFit" />
            </view>
            <text class="menu-text">帮助与反馈</text>
          </view>
          <view class="arrow"></view>
        </view>
      </view>

      <button class="logout-btn" @tap="handleLogout">退出登录</button>
      <view style="height: 20rpx;"></view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { request, resolveMediaUrl } from '@/utils/request.js';

const userInfo = ref({});
const avatarDisplay = ref('/static/default-avatar.svg');
const notificationCount = ref(0);

const syncFromStorage = () => {
  const storedUser = uni.getStorageSync('userInfo');
  if (!storedUser) return;
  try {
    userInfo.value = typeof storedUser === 'string' ? JSON.parse(storedUser) : storedUser;
  } catch (e) {
    userInfo.value = {};
  }
  avatarDisplay.value = userInfo.value.avatar_url
    ? resolveMediaUrl(userInfo.value.avatar_url)
    : '/static/default-avatar.svg';
};

const fetchProfile = async () => {
  try {
    const res = await request({ url: '/users/profile', method: 'GET' });
    if (!res) return;
    userInfo.value = { ...userInfo.value, ...res };
    avatarDisplay.value = res.avatar_url ? resolveMediaUrl(res.avatar_url) : '/static/default-avatar.svg';
    uni.setStorageSync('userInfo', userInfo.value);
  } catch (e) {
    console.error('fetch teacher profile failed', e);
  }
};

onShow(() => {
  uni.hideHomeButton && uni.hideHomeButton();
  syncFromStorage();
  fetchProfile();
});

const handlePersonalInfo = () => {
  uni.navigateTo({ url: '/pages/teacher/profile/edit' });
};

const handleAccountSecurity = () => {
  uni.navigateTo({ url: '/pages/teacher/security/security' });
};

const handleNotifications = () => {
  uni.navigateTo({ url: '/pages/teacher/notifications/list' });
};

const handleHelpFeedback = () => {
  uni.showActionSheet({
    itemList: ['使用帮助', '意见反馈', '联系管理员'],
    success: (res) => {
      if (res.tapIndex === 0) {
        uni.showModal({
          title: '使用帮助',
          content: '教师端主要功能：\n\n1. 工作台：查看待办和统计\n2. 综合管理：学员、任务、导出\n3. 测试监控：查看测试数据\n4. 个人中心：个人设置和通知',
          confirmText: '我知道了'
        });
      } else if (res.tapIndex === 1) {
        uni.showModal({
          title: '意见反馈',
          content: '请描述你的问题或建议',
          editable: true,
          placeholderText: '请输入反馈内容',
          success: async (modalRes) => {
            if (modalRes.confirm && modalRes.content) {
              try {
                await request({
                  url: '/feedback/diagnose',
                  method: 'POST',
                  data: { feedback: modalRes.content.trim(), prefer_llm: true }
                });
              } catch (e) {
                console.error('feedback submit failed', e);
              }
              uni.showToast({ title: '感谢你的反馈', icon: 'success' });
            }
          }
        });
      } else if (res.tapIndex === 2) {
        uni.showModal({
          title: '联系管理员',
          content: '电话：138-0013-8000\n邮箱：admin@campus.edu.cn\n办公地点：体育馆201',
          confirmText: '我知道了'
        });
      }
    }
  });
};

const handleLogout = () => {
  uni.showModal({
    title: '退出登录',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        uni.removeStorageSync('userInfo');
        uni.removeStorageSync('userRole');
        uni.removeStorageSync('token');
        uni.reLaunch({ url: '/pages/login/login' });
      }
    }
  });
};
</script>

<style scoped>
.mine-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  padding: 30rpx;
  flex: 1;
}

.user-card {
  background: linear-gradient(135deg, #20c997 0%, #17a2b8 100%);
  border-radius: 24rpx;
  padding: 46rpx 40rpx;
  display: flex;
  align-items: center;
  color: #fff;
  margin-bottom: 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(32, 201, 151, 0.2);
}

.avatar-img {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  margin-right: 28rpx;
  background: rgba(255, 255, 255, 0.25);
  border: 2rpx solid rgba(255, 255, 255, 0.5);
  flex-shrink: 0;
}

.info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.name-row {
  display: flex;
  align-items: center;
  align-self: flex-start;
  min-width: 0;
  margin-bottom: 10rpx;
}

.name {
  font-size: 36rpx;
  font-weight: 800;
  line-height: 1.25;
  max-width: 360rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.edit-icon-img {
  width: 34rpx;
  height: 34rpx;
  margin-left: 12rpx;
  flex-shrink: 0;
}

.role {
  font-size: 24rpx;
  opacity: 0.92;
  background: rgba(255, 255, 255, 0.18);
  padding: 6rpx 18rpx;
  border-radius: 999rpx;
  display: inline-block;
  align-self: flex-start;
}

.menu-list {
  background: #fff;
  border-radius: 24rpx;
  overflow: hidden;
  margin-bottom: 28rpx;
  box-shadow: 0 8rpx 24rpx rgba(24, 39, 75, 0.05);
}

.menu-item {
  padding: 28rpx 32rpx;
  border-bottom: 1rpx solid #f1f4f7;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #233244;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:active {
  background: #f8fafc;
}

.menu-left {
  display: flex;
  align-items: center;
  min-width: 0;
  flex: 1;
}

.menu-icon-shell {
  width: 64rpx;
  height: 64rpx;
  border-radius: 18rpx;
  background: #f7f8fa;
  box-shadow: inset 0 0 0 1rpx #edf0f3;
  margin-right: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.menu-icon-img {
  width: 42rpx;
  height: 42rpx;
}

.menu-text {
  font-size: 30rpx;
  color: #233244;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.badge {
  background: #ff4d4f;
  color: #fff;
  font-size: 20rpx;
  padding: 4rpx 12rpx;
  border-radius: 999rpx;
  min-width: 32rpx;
  text-align: center;
  font-weight: bold;
  margin-right: 10rpx;
  flex-shrink: 0;
}

.arrow {
  width: 18rpx;
  height: 18rpx;
  border-top: 3rpx solid #c5ced6;
  border-right: 3rpx solid #c5ced6;
  transform: rotate(45deg);
  display: inline-block;
  flex-shrink: 0;
}

.logout-btn {
  background: #fff;
  color: #ff6b6b;
  font-size: 30rpx;
  border-radius: 24rpx;
  height: 88rpx;
  line-height: 88rpx;
  box-shadow: 0 8rpx 24rpx rgba(24, 39, 75, 0.05);
  font-weight: 700;
}

.logout-btn:active {
  opacity: 0.92;
}
</style>
