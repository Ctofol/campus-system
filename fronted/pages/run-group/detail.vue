<template>
  <view class="detail-page">
    <view class="header-card" v-if="groupDetail">
      <view class="header-bg"></view>
      <view class="header-content">
        <image class="avatar" :src="groupAvatar" mode="aspectFill" />
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
            <text class="value">{{ (groupDetail.total_mileage || 0).toFixed(1) }}km</text>
            <text class="label">总里程</text>
          </view>
        </view>
      </view>
    </view>

    <view class="tab-bar">
      <view
        class="tab-item"
        :class="{ active: currentTab === 'overview' }"
        @click="currentTab = 'overview'"
      >
        <text>概览</text>
      </view>
      <view
        class="tab-item"
        :class="{ active: currentTab === 'members' }"
        @click="loadMembers"
      >
        <text>成员</text>
      </view>
      <view
        class="tab-item"
        :class="{ active: currentTab === 'activities' }"
        @click="loadActivities"
      >
        <text>活动</text>
      </view>
    </view>

    <view class="tab-content">
      <view v-if="currentTab === 'overview' && groupDetail">
        <view class="desc-card">
          <text class="card-title">跑团简介</text>
          <text class="desc-text">{{ groupDetail.description || '暂无简介' }}</text>
        </view>
      </view>

      <view v-if="currentTab === 'members'">
        <view class="member-item" v-for="member in members" :key="member.id">
          <text class="member-name">{{ member.user_name }}</text>
          <text class="member-role">{{ getRoleText(member.role) }}</text>
          <text class="member-mileage">{{ (member.total_mileage || 0).toFixed(1) }}km</text>
        </view>
      </view>

      <view v-if="currentTab === 'activities'">
        <view
          class="activity-item"
          v-for="activity in activities"
          :key="activity.id"
          @click="goToActivity(activity.id)"
        >
          <text class="activity-title">{{ activity.title }}</text>
          <text class="activity-time">{{ formatTime(activity.activity_time) }}</text>
          <text class="activity-apply">{{ activity.apply_count }}/{{ activity.total_quota }}人</text>
        </view>
      </view>
    </view>

    <view class="bottom-bar" v-if="groupDetail">
      <button class="action-btn" @click="handleJoin" v-if="!isMember">加入跑团</button>
      <view class="creator-actions" v-else-if="isCreator">
        <button class="action-btn edit" @click="goToEditGroup">编辑跑团</button>
        <button class="action-btn primary" @click="goToCreateActivity">发布活动</button>
      </view>
      <button class="action-btn leave" @click="handleLeave" v-else>退出跑团</button>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import {
  getRunGroups,
  joinRunGroup,
  leaveRunGroup,
  getGroupMembers,
  getGroupActivities,
  resolveMediaUrl
} from '@/utils/request.js';

const groupId = ref(0);
const groupDetail = ref(null);
const currentTab = ref('overview');
const members = ref([]);
const activities = ref([]);
const isMember = ref(false);
const isCreator = ref(false);

const groupAvatar = computed(() => {
  if (!groupDetail.value || !groupDetail.value.avatar) return '/static/default-avatar.svg';
  return resolveMediaUrl(groupDetail.value.avatar);
});

onLoad((options) => {
  if (options.groupId) {
    groupId.value = parseInt(options.groupId, 10);
    loadDetail();
    checkMemberStatus();
  } else {
    uni.showToast({ title: '参数错误', icon: 'none' });
    setTimeout(() => uni.navigateBack(), 1500);
  }
});

const checkMemberStatus = async () => {
  try {
    const stored = uni.getStorageSync('userInfo');
    let userInfo = stored;
    if (typeof stored === 'string') {
      try {
        userInfo = JSON.parse(stored);
      } catch (e) {
        userInfo = {};
      }
    }

    const currentUserId = userInfo?.id || userInfo?.userId;
    if (!currentUserId) return;

    const res = await getGroupMembers(groupId.value, { page: 1, size: 100 });
    if (!Array.isArray(res)) return;

    members.value = res;
    const currentMember = res.find((m) => m.user_id === currentUserId);
    if (currentMember) {
      isMember.value = true;
      isCreator.value = currentMember.role === 'creator';
    }
  } catch (e) {
    console.error('checkMemberStatus failed', e);
  }
};

const loadDetail = async () => {
  try {
    const res = await getRunGroups({ page: 1, size: 100 });

    if (res && res.items) {
      groupDetail.value = res.items.find((g) => g.id === groupId.value);
    } else if (Array.isArray(res)) {
      groupDetail.value = res.find((g) => g.id === groupId.value);
    }

    if (!groupDetail.value) {
      uni.showToast({ title: '跑团不存在', icon: 'none' });
      setTimeout(() => uni.navigateBack(), 1500);
    }
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' });
  }
};

const loadMembers = async () => {
  currentTab.value = 'members';
  if (members.value.length > 0) return;
  await checkMemberStatus();
};

const loadActivities = async () => {
  currentTab.value = 'activities';
  if (activities.value.length > 0) return;

  try {
    const res = await getGroupActivities(groupId.value, { page: 1, size: 20 });
    activities.value = res.items || [];
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
      await checkMemberStatus();
    } else {
      uni.showToast({ title: res.message || '加入失败', icon: 'none' });
    }
  } catch (e) {
    uni.showToast({ title: '加入失败', icon: 'none' });
  }
};

const handleLeave = async () => {
  uni.showModal({
    title: '确认退出',
    content: '退出后将无法查看该跑团信息',
    success: async (res) => {
      if (!res.confirm) return;
      try {
        await leaveRunGroup(groupId.value);
        uni.showToast({ title: '退出成功', icon: 'success' });
        setTimeout(() => uni.navigateBack(), 1500);
      } catch (e) {
        uni.showToast({ title: e.message || e.detail || '退出失败', icon: 'none' });
      }
    }
  });
};

const goToCreateActivity = () => {
  uni.navigateTo({
    url: `/pages/run-group/create-activity?groupId=${groupId.value}`
  });
};

const goToEditGroup = () => {
  uni.navigateTo({
    url: `/pages/run-group/edit?groupId=${groupId.value}`
  });
};

const getRoleText = (role) => {
  const roleMap = {
    creator: '创建者',
    admin: '管理员',
    member: '成员'
  };
  return roleMap[role] || '成员';
};

const formatTime = (timeStr) => {
  const date = new Date(timeStr);
  return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
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
  background: linear-gradient(135deg, #20c997, #17a589);
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
  box-sizing: border-box;
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
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rank-badge {
  padding: 8rpx 20rpx;
  background: linear-gradient(135deg, #ffd700, #ffa500);
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
  color: #20c997;
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
  box-sizing: border-box;
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
  background: #20c997;
  color: #fff;
}

.tab-content {
  padding: 0 30rpx;
  box-sizing: border-box;
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

.member-item,
.activity-item {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.member-name,
.activity-title {
  flex: 1;
  min-width: 0;
  font-size: 26rpx;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.member-role,
.activity-time {
  font-size: 24rpx;
  color: #999;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.member-mileage,
.activity-apply {
  font-size: 24rpx;
  color: #20c997;
  font-weight: bold;
  flex-shrink: 0;
}
.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.06);
  box-sizing: border-box;
}

.creator-actions {
  display: flex;
  gap: 16rpx;
}

.action-btn {
  width: 100%;
  flex: 1;
  height: 84rpx;
  line-height: 84rpx;
  padding: 0 16rpx;
  margin: 0;
  background: linear-gradient(135deg, #20c997, #17a589);
  color: #fff;
  border-radius: 30rpx;
  font-size: 30rpx;
  font-weight: bold;
  border: none;
  box-sizing: border-box;
}

.action-btn::after {
  border: none;
}

.action-btn.edit {
  background: #effaf6;
  color: #0f766e;
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
