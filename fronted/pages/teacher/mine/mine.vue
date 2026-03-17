<template>
  <view class="mine-container">
    <!-- 自定义导航栏 -->
    <view class="custom-nav-bar">
      <view class="nav-status-bar"></view>
      <view class="nav-content">
        <text class="nav-title">个人中心</text>
      </view>
    </view>

    <view class="content-wrapper">
      <!-- 用户信息卡片 -->
      <view class="user-card">
        <view class="avatar">👮‍♂️</view>
        <view class="info">
          <text class="name">{{ userInfo.name || '拉克丝' }}</text>
          <text class="role">公共体育教研部</text>
        </view>
      </view>
    
      <!-- 功能菜单列表 - 全功能打通 -->
      <view class="menu-list">
        <view class="menu-item" @click="handlePersonalInfo">
          <view class="menu-left">
            <text class="menu-icon">👤</text>
            <text class="menu-text">个人信息设置</text>
          </view>
          <text class="arrow">></text>
        </view>
        <view class="menu-item" @click="handleAccountSecurity">
          <view class="menu-left">
            <text class="menu-icon">🔒</text>
            <text class="menu-text">账号安全</text>
          </view>
          <text class="arrow">></text>
        </view>
        <view class="menu-item" @click="handleNotifications">
          <view class="menu-left">
            <text class="menu-icon">🔔</text>
            <text class="menu-text">系统通知</text>
          </view>
          <view class="badge" v-if="notificationCount > 0">{{ notificationCount }}</view>
          <text class="arrow">></text>
        </view>
        <view class="menu-item" @click="handleHelpFeedback">
          <view class="menu-left">
            <text class="menu-icon">💬</text>
            <text class="menu-text">帮助与反馈</text>
          </view>
          <text class="arrow">></text>
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

const userInfo = ref({});
const notificationCount = ref(0);

onShow(() => {
  uni.hideHomeButton && uni.hideHomeButton();

  const storedUser = uni.getStorageSync('userInfo');
  if (storedUser) {
    try {
      userInfo.value = typeof storedUser === 'string' ? JSON.parse(storedUser) : storedUser;
    } catch (e) {
      userInfo.value = {};
    }
  }
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
          success: (modalRes) => {
            if (modalRes.confirm && modalRes.content) {
              uni.showToast({ title: '感谢您的反馈', icon: 'success' });
              // TODO: 调用反馈提交API
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

/* 自定义导航栏 */
.custom-nav-bar {
  background: #fff;
  width: 100%;
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid #eee;
}
.nav-status-bar {
  height: var(--status-bar-height);
  width: 100%;
}
.nav-content {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.nav-title {
  color: #333;
  font-size: 32rpx;
  font-weight: bold;
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
.avatar {
  width: 120rpx;
  height: 120rpx;
  background: rgba(255,255,255,0.25);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 60rpx;
  margin-right: 30rpx;
  backdrop-filter: blur(10px);
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1);
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
  font-size: 36rpx;
}
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
