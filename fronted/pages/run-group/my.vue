<template>
  <view class="my-page">
    <!-- 未加入状态 -->
    <view class="no-group" v-if="!hasJoined">
      <image class="empty-icon" src="/static/empty-group.png" mode="aspectFit" />
      <text class="tip-text">您还未加入跑团</text>
      <view class="tip-actions">
        <button class="tip-btn primary" @click="goToDiscover">加入跑团</button>
      </view>
    </view>
    
    <!-- 已加入状态 -->
    <view class="group-content" v-else>
      <!-- 跑团信息卡片 -->
      <view class="group-card">
        <view class="card-header">
          <image class="avatar" :src="myGroup.avatar || '/static/default-avatar.png'" mode="aspectFill" />
          <view class="header-info">
            <text class="name">{{ myGroup.name }}</text>
            <view class="role-badge" :class="'role-' + myGroup.role">
              <text>{{ getRoleText(myRole) }}</text>
            </view>
          </view>
          <view class="rank-badge" v-if="myGroup.rank">
            <text>No.{{ myGroup.rank }}</text>
          </view>
        </view>
        
        <view class="stats-row">
          <view class="stat-item">
            <text class="value">{{ myGroup.member_count }}</text>
            <text class="label">成员数</text>
          </view>
          <view class="stat-item">
            <text class="value">{{ myGroup.total_mileage.toFixed(1) }}km</text>
            <text class="label">总里程</text>
          </view>
          <view class="stat-item">
            <text class="value">{{ myGroup.month_activity_count }}</text>
            <text class="label">本月活动</text>
          </view>
        </view>
        
        <button class="leave-btn" @click="handleLeave" v-if="myRole !== 'creator'">退出跑团</button>
      </view>
      
      <!-- Tab 栏 -->
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
      
      <!-- 概览 -->
      <view class="tab-content" v-if="currentTab === 'overview'">
        <view class="overview-section">
          <text class="section-title">跑团简介</text>
          <text class="section-text">{{ myGroup.description || '暂无简介' }}</text>
        </view>
      </view>
      
      <!-- 成员列表 -->
      <view class="tab-content" v-if="currentTab === 'members'">
        <view class="member-item" v-for="member in members" :key="member.id">
          <text class="member-name">{{ member.user_name }}</text>
          <text class="member-role">{{ getRoleText(member.role) }}</text>
          <text class="member-mileage">{{ member.total_mileage.toFixed(1) }}km</text>
        </view>
      </view>
      
      <!-- 活动列表 -->
      <view class="tab-content" v-if="currentTab === 'activities'">
        <view class="activity-item" v-for="activity in activities" :key="activity.id" @click="goToActivity(activity.id)">
          <text class="activity-title">{{ activity.title }}</text>
          <text class="activity-time">{{ formatTime(activity.activity_time) }}</text>
          <text class="activity-apply">{{ activity.apply_count }}/{{ activity.total_quota }}人</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getMyRunGroup, leaveRunGroup, getGroupMembers, getGroupActivities } from '@/utils/request.js';

const hasJoined = ref(false);
const myGroup = ref(null);
const myRole = ref('member');
const currentTab = ref('overview');
const members = ref([]);
const activities = ref([]);

const loadMyGroup = async () => {
  try {
    const res = await getMyRunGroup();
    
    // 如果返回null，说明用户未加入跑团
    if (!res) {
      hasJoined.value = false;
      return;
    }
    
    myGroup.value = res;
    hasJoined.value = true;
    
    // 获取当前用户角色（需要从成员列表中查找）
    const userId = uni.getStorageSync('userInfo')?.id;
    if (userId) {
      const memberRes = await getGroupMembers(res.id, { page: 1, size: 100 });
      const currentMember = memberRes.find(m => m.user_id === userId);
      if (currentMember) {
        myRole.value = currentMember.role;
      }
    }
  } catch (e) {
    // 任何错误都视为未加入跑团
    console.log('加载跑团信息失败:', e);
    hasJoined.value = false;
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
          hasJoined.value = false;
          myGroup.value = null;
        } catch (e) {
          uni.showToast({ title: e.detail || '退出失败', icon: 'none' });
        }
      }
    }
  });
};

const loadMembers = async () => {
  currentTab.value = 'members';
  if (members.value.length > 0) return;
  
  try {
    const res = await getGroupMembers(myGroup.value.id, { page: 1, size: 50 });
    members.value = res;
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' });
  }
};

const loadActivities = async () => {
  currentTab.value = 'activities';
  if (activities.value.length > 0) return;
  
  try {
    const res = await getGroupActivities(myGroup.value.id, { page: 1, size: 20 });
    activities.value = res.items;
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' });
  }
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

const goToDiscover = () => {
  uni.navigateTo({ url: '/pages/run-group/discover' });
};

const goToActivity = (activityId) => {
  uni.navigateTo({ url: `/pages/run-group/activity-detail?activityId=${activityId}` });
};

onMounted(() => {
  loadMyGroup();
});
</script>

<style scoped>
.my-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.no-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 200rpx 60rpx;
}

.empty-icon {
  width: 200rpx;
  height: 200rpx;
  margin-bottom: 40rpx;
}

.tip-text {
  font-size: 28rpx;
  color: #999;
  margin-bottom: 40rpx;
}

.tip-actions {
  display: flex;
  gap: 20rpx;
}

.tip-btn {
  padding: 16rpx 40rpx;
  border-radius: 30rpx;
  font-size: 26rpx;
  border: none;
}

.tip-btn.primary {
  background: #20C997;
  color: #fff;
}

.group-content {
  padding: 20rpx 30rpx;
}

.group-card {
  background: linear-gradient(135deg, #20C997, #17a589);
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
}

.avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  margin-right: 20rpx;
  background: rgba(255, 255, 255, 0.2);
}

.header-info {
  flex: 1;
}

.name {
  font-size: 32rpx;
  font-weight: bold;
  color: #fff;
  display: block;
  margin-bottom: 8rpx;
}

.role-badge {
  display: inline-block;
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
  font-size: 20rpx;
  color: #fff;
  background: rgba(255, 255, 255, 0.3);
}

.rank-badge {
  padding: 8rpx 16rpx;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 20rpx;
  font-size: 24rpx;
  color: #fff;
}

.stats-row {
  display: flex;
  justify-content: space-around;
  margin-bottom: 30rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.value {
  font-size: 48rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 8rpx;
}

.label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.9);
}

.leave-btn {
  width: 100%;
  padding: 20rpx;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border-radius: 30rpx;
  font-size: 26rpx;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.tab-bar {
  display: flex;
  background: #fff;
  border-radius: 20rpx;
  padding: 10rpx;
  margin-bottom: 20rpx;
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
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.overview-section {
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 16rpx;
}

.section-text {
  font-size: 26rpx;
  color: #666;
  line-height: 1.6;
}

.member-item, .activity-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1px solid #f0f0f0;
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
</style>
