<template>
  <view class="detail-page">
    <view class="header-card" v-if="groupDetail">
      <view class="header-bg"></view>
      <view class="header-content">
        <image class="avatar" :src="groupDetail.avatar || '/static/default-avatar.png'" mode="aspectFill" />
        <text class="name">{{ groupDetail.name }}</text>
        <view class="rank-badge" v-if="groupDetail.rank">
          <text>排名 No.{{ groupDetail.rank }}</text>
        </view>
        <view class="stats-row">
          <view class="stat-item">
            <text class="value">{{ groupDetail.member_count }}</text>
            <text class="label">成员</text>
          </view>
          <view class="stat-item">
            <text class="value">{{ groupDetail.total_mileage.toFixed(1) }}km</text>
            <text class="label">总里程</text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="tab-bar">
      <view 
        class="tab-item" 
        :class="{active: currentTab === 'overview'}"
        @click="currentTab = 'overview'"
      >
        <text>概览</text>
      </view>
      <view 
        class="tab-item" 
        :class="{active: currentTab === 'members'}"
        @click="loadMembers"
      >
        <text>成员</text>
      </view>
      <view 
        class="tab-item" 
        :class="{active: currentTab === 'activities'}"
        @click="loadActivities"
      >
        <text>活动</text>
      </view>
    </view>
    
    <view class="tab-content">
      <!-- 概览 -->
      <view v-if="currentTab === 'overview' && groupDetail">
        <view class="desc-card">
          <text class="card-title">跑团简介</text>
          <text class="desc-text">{{ groupDetail.description || '暂无简介' }}</text>
        </view>
      </view>
      
      <!-- 成员列表 -->
      <view v-if="currentTab === 'members'">
        <view class="member-item" v-for="member in members" :key="member.id">
          <text class="member-name">{{ member.user_name }}</text>
          <text class="member-role">{{ getRoleText(member.role) }}</text>
          <text class="member-mileage">{{ member.total_mileage.toFixed(1) }}km</text>
        </view>
      </view>
      
      <!-- 活动列表 -->
      <view v-if="currentTab === 'activities'">
        <view class="activity-item" v-for="activity in activities" :key="activity.id" @click="goToActivity(activity.id)">
          <text class="activity-title">{{ activity.title }}</text>
          <text class="activity-time">{{ formatTime(activity.activity_time) }}</text>
          <text class="activity-apply">{{ activity.apply_count }}/{{ activity.total_quota }}人</text>
        </view>
      </view>
    </view>
    
    <view class="bottom-bar" v-if="groupDetail">
      <button class="action-btn" @click="handleJoin" v-if="!isMember">加入跑团</button>
      <button class="action-btn primary" @click="goToCreateActivity" v-else-if="isCreator">发布活动</button>
      <button class="action-btn leave" @click="handleLeave" v-else>退出跑团</button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { getRunGroups, joinRunGroup, leaveRunGroup, getGroupMembers, getGroupActivities } from '@/utils/request.js';

const groupId = ref(0);
const groupDetail = ref(null);
const currentTab = ref('overview');
const members = ref([]);
const activities = ref([]);
const isMember = ref(false);
const isCreator = ref(false);

// 获取URL参数
onLoad((options) => {
  if (options.groupId) {
    groupId.value = parseInt(options.groupId);
    loadDetail();
    // 立即加载成员信息以判断用户身份
    checkMemberStatus();
  } else {
    uni.showToast({ title: '参数错误', icon: 'none' });
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  }
});

// 检查用户在跑团中的身份
const checkMemberStatus = async () => {
  try {
    const userInfo = uni.getStorageSync('userInfo');
    console.log('当前用户信息:', userInfo);
    
    if (!userInfo || !userInfo.userId) {
      console.log('未找到用户信息或userId');
      return;
    }
    
    const res = await getGroupMembers(groupId.value, { page: 1, size: 100 });
    console.log('成员列表响应:', res);
    
    // 后端返回的是数组，不是分页对象
    if (Array.isArray(res)) {
      members.value = res;
      const currentMember = res.find(m => m.user_id === userInfo.userId);
      console.log('找到的当前成员:', currentMember);
      
      if (currentMember) {
        isMember.value = true;
        isCreator.value = currentMember.role === 'creator';
        console.log('用户身份:', { isMember: isMember.value, isCreator: isCreator.value, role: currentMember.role });
      } else {
        console.log('用户不是该跑团成员');
      }
    } else {
      console.log('成员列表格式错误:', res);
    }
  } catch (e) {
    console.error('检查成员身份失败:', e);
  }
};

const loadDetail = async () => {
  try {
    console.log('加载跑团详情, groupId:', groupId.value);
    const res = await getRunGroups({ page: 1, size: 100 });
    console.log('跑团列表:', res);
    
    if (res && res.items) {
      // 如果返回的是分页数据
      groupDetail.value = res.items.find(g => g.id === groupId.value);
    } else if (Array.isArray(res)) {
      // 如果返回的是数组
      groupDetail.value = res.find(g => g.id === groupId.value);
    }
    
    console.log('找到的跑团详情:', groupDetail.value);
    
    if (!groupDetail.value) {
      uni.showToast({ title: '跑团不存在', icon: 'none' });
      setTimeout(() => {
        uni.navigateBack();
      }, 1500);
    }
  } catch (e) {
    console.error('加载跑团详情失败:', e);
    uni.showToast({ title: '加载失败', icon: 'none' });
  }
};

const loadMembers = async () => {
  currentTab.value = 'members';
  // 如果已经加载过成员列表，直接返回
  if (members.value.length > 0) return;
  
  // 否则调用检查函数
  await checkMemberStatus();
};

const loadActivities = async () => {
  currentTab.value = 'activities';
  if (activities.value.length > 0) return;
  
  try {
    const res = await getGroupActivities(groupId.value, { page: 1, size: 20 });
    activities.value = res.items;
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' });
  }
};

const handleJoin = async () => {
  try {
    const res = await joinRunGroup(groupId.value);
    if (res.joinStatus) {
      uni.showToast({ title: '加入成功', icon: 'success' });
      isMember.value = true;
      loadMembers();
    } else {
      uni.showToast({ title: res.message, icon: 'none' });
    }
  } catch (e) {
    uni.showToast({ title: '加入失败', icon: 'none' });
  }
};

const handleLeave = async () => {
  uni.showModal({
    title: '确认退出',
    content: '退出后将无法查看跑团信息',
    success: async (res) => {
      if (res.confirm) {
        try {
          await leaveRunGroup();
          uni.showToast({ title: '退出成功', icon: 'success' });
          setTimeout(() => {
            uni.navigateBack();
          }, 1500);
        } catch (e) {
          uni.showToast({ title: '退出失败', icon: 'none' });
        }
      }
    }
  });
};

const goToCreateActivity = () => {
  uni.navigateTo({ 
    url: `/pages/run-group/create-activity?groupId=${groupId.value}` 
  });
};

const getRoleText = (role) => {
  const roleMap = {
    'creator': '创建者',
    'admin': '管理员',
    'member': '成员'
  };
  return roleMap[role] || '成员';
};

const formatTime = (timeStr) => {
  const date = new Date(timeStr);
  return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
};

const goToActivity = (activityId) => {
  uni.navigateTo({ url: `/pages/run-group/activity-detail?activityId=${activityId}` });
};
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 120rpx;
}

.header-card {
  position: relative;
  margin-bottom: 20rpx;
}

.header-bg {
  height: 300rpx;
  background: linear-gradient(135deg, #20C997, #17a589);
}

.header-content {
  position: absolute;
  top: 100rpx;
  left: 30rpx;
  right: 30rpx;
  background: #fff;
  border-radius: 20rpx;
  padding: 40rpx 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  margin-bottom: 20rpx;
  background: #e0e0e0;
}

.name {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 12rpx;
}

.rank-badge {
  padding: 8rpx 20rpx;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border-radius: 20rpx;
  font-size: 22rpx;
  color: #fff;
  margin-bottom: 30rpx;
}

.stats-row {
  display: flex;
  gap: 80rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.value {
  font-size: 40rpx;
  font-weight: bold;
  color: #20C997;
  margin-bottom: 8rpx;
}

.label {
  font-size: 24rpx;
  color: #999;
}

.tab-bar {
  display: flex;
  background: #fff;
  margin: 220rpx 30rpx 20rpx;
  border-radius: 20rpx;
  padding: 10rpx;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 16rpx;
  border-radius: 16rpx;
  font-size: 26rpx;
  color: #666;
}

.tab-item.active {
  background: #20C997;
  color: #fff;
}

.tab-content {
  padding: 0 30rpx;
}

.desc-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.card-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
}

.desc-text {
  font-size: 26rpx;
  color: #666;
  line-height: 1.8;
}

.member-item, .activity-item {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 16rpx;
  display: flex;
  align-items: center;
}

.member-name, .activity-title {
  flex: 1;
  font-size: 26rpx;
  color: #333;
}

.member-role, .activity-time {
  font-size: 24rpx;
  color: #999;
  margin-right: 20rpx;
}

.member-mileage, .activity-apply {
  font-size: 24rpx;
  color: #20C997;
  font-weight: bold;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 30rpx;
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.action-btn {
  width: 100%;
  padding: 24rpx;
  background: linear-gradient(135deg, #20C997, #17a589);
  color: #fff;
  border-radius: 30rpx;
  font-size: 30rpx;
  font-weight: bold;
  border: none;
}

.action-btn.primary {
  background: linear-gradient(135deg, #4dabf7, #339af0);
}

.action-btn.leave {
  background: #fff;
  color: #ff6b6b;
  border: 2px solid #ff6b6b;
}
</style>
