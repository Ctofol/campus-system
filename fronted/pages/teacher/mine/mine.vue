<template>
  <view class="mine-container">
    <page-tab-header title="个人中心" theme="white" show-back />

    <view class="content-wrapper page-tab-body">
      <!-- 用户信息卡片 -->
      <view class="user-card">
        <image class="avatar-img" :src="avatarDisplay" mode="aspectFill" />
        <view class="info">
          <text class="name">{{ userInfo.name || '教师' }}</text>
          <text class="role">{{ userInfo.subject || userInfo.signature || '公共体育教研部' }}</text>
        </view>
      </view>
    
      <!-- 功能菜单列表 - 全功能打通 -->
      <view class="menu-list">
        <view class="menu-item" @click="handlePersonalInfo">
          <view class="menu-left">
            <image class="menu-icon" src='/static/about-me.png' mode="aspectFit" />
            <text class="menu-text">个人信息设置</text>
          </view>
          <text class="arrow">→</text>
        </view>
        <view class="menu-item" @click="handleAccountSecurity">
          <view class="menu-left">
            <image class="menu-icon" src="/static/叉号图标.png" mode="aspectFit" />
            <text class="menu-text">账号安全</text>
          </view>
          <text class="arrow">→</text>
        </view>
        <view class="menu-item" @click="handleNotifications">
          <view class="menu-left">
            <image class="menu-icon-img" src="/static/通知图标.png" mode="aspectFit" />
            <text class="menu-text">系统通知</text>
          </view>
          <view class="badge" v-if="notificationCount > 0">{{ notificationCount }}</view>
          <text class="arrow">→</text>
        </view>
        <view class="menu-item" @click="handleHelpFeedback">
          <view class="menu-left">
            <image class="menu-icon" src="/static/消息图标.png" mode="aspectFit" />
            <text class="menu-text">帮助与反馈</text>
          </view>
          <text class="arrow">→</text>
        </view>
      </view>
    
      <!-- 退出登录按钮 -->
      <button class="logout-btn" @click="handleLogout">退出登录</button>
    
      <view style="height: 20rpx;"></view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { request, resolveMediaUrl, BASE_URL } from '@/utils/request.js';

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

// 功能打通：个人信息设置
const handlePersonalInfo = () => {
  uni.navigateTo({
    url: '/pages/teacher/profile/edit'
  });
};

// 功能打通：账号安全
const handleAccountSecurity = () => {
  uni.navigateTo({
    url: '/pages/teacher/security/security'
  });
};

// 功能打通：系统通知
const handleNotifications = () => {
  uni.navigateTo({
    url: '/pages/teacher/notifications/list'
  });
};

// 功能打通：帮助与反馈
const handleHelpFeedback = () => {
  uni.showActionSheet({
    itemList: ['使用帮助', '意见反馈', '联系管理员'],
    success: (res) => {
      if (res.tapIndex === 0) {
        // 使用帮助
        uni.showModal({
          title: '使用帮助',
          content: '教师端功能说明：\n\n1. 工作台：查看待办事项和统计数据\n2. 综合管理：学员管理、数据导出等\n3. 测试监控：查看学生测试数据\n4. 个人中心：个人设置和系统通知',
          confirmText: '我知道了'
        });
      } else if (res.tapIndex === 1) {
        // 意见反馈
        uni.showModal({
          title: '意见反馈',
          content: '请描述您的问题或建议',
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
                uni.showToast({ title: '感谢您的反馈', icon: 'success' });
              } catch (e) {
                uni.showToast({ title: '感谢您的反馈', icon: 'success' });
              }
            }
          }
        });
      } else if (res.tapIndex === 2) {
        // 联系管理员
        uni.showModal({
          title: '联系管理员',
          content: '管理员联系方式：\n\n电话：138-0013-8000\n邮箱：admin@campus.edu.cn\n办公室：体育馆201',
          confirmText: '我知道了'
        });
      }
    }
  });
};

// 功能打通：退出登录
const handleLogout = () => {
  uni.showModal({
    title: '退出登录',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        uni.removeStorageSync('userInfo');
        uni.removeStorageSync('userRole');
        uni.removeStorageSync('token');
        uni.reLaunch({
          url: '/pages/login/login'
        });
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
  background: linear-gradient(135deg, #20C997 0%, #17a2b8 100%);
  border-radius: 24rpx;
  padding: 50rpx 40rpx;
  display: flex;
  align-items: center;
  color: #fff;
  margin-bottom: 40rpx;
  box-shadow: 0 8rpx 24rpx rgba(32, 201, 151, 0.2);
}
.avatar-img {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  margin-right: 30rpx;
  background: rgba(255, 255, 255, 0.25);
  border: 2rpx solid rgba(255, 255, 255, 0.5);
  flex-shrink: 0;
}
.info {
  display: flex;
  flex-direction: column;
}
.name {
  font-size: 36rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
  text-shadow: 0 2rpx 4rpx rgba(0,0,0,0.1);
}
.role {
  font-size: 24rpx;
  opacity: 0.9;
  background: rgba(255,255,255,0.2);
  padding: 6rpx 20rpx;
  border-radius: 20rpx;
  display: inline-block;
  align-self: flex-start;
}

.menu-list {
  background: #fff;
  border-radius: 24rpx;
  overflow: hidden;
  margin-bottom: 60rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.03);
}
.menu-item {
  padding: 32rpx 40rpx;
  border-bottom: 1px solid #f5f5f5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 30rpx;
  color: #333;
  transition: background 0.2s ease;
  position: relative;
}
.menu-item:active {
  background: #fafafa;
}
.menu-item:last-child {
  border-bottom: none;
}
.menu-left {
  display: flex;
  align-items: center;
  gap: 20rpx;
}
.menu-icon {
  width: 36rpx;
  height: 36rpx;
}
.menu-icon-img { width: 56rpx; height: 56rpx; }
.menu-text {
  font-size: 30rpx;
  color: #333;
}
.badge {
  background: #ff4d4f;
  color: #fff;
  font-size: 20rpx;
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
  min-width: 32rpx;
  text-align: center;
  font-weight: bold;
  margin-right: 10rpx;
}
.arrow {
  color: #ccc;
  font-size: 28rpx;
}

.logout-btn {
  background: #fff;
  color: #ff6b6b;
  font-size: 30rpx;
  border-radius: 24rpx;
  height: 88rpx;
  line-height: 88rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.03);
  font-weight: 500;
}
.logout-btn:active {
  opacity: 0.9;
}
</style>
