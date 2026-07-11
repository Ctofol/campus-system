<template>
  <view class="my-page">
    <view class="no-group" v-if="joinedGroups.length === 0">
      <image class="empty-icon" src="/static/主页跑团图标.png" mode="aspectFit" />
      <text class="tip-text">您还未加入跑团</text>
      <view class="tip-actions">
        <button class="tip-btn primary" @click="goToDiscover">加入跑团</button>
      </view>
    </view>

    <view class="group-content" v-else-if="activeGroup">
      <scroll-view class="group-switcher" scroll-x show-scrollbar="false">
        <view class="group-switcher-row">
          <view
            v-for="group in joinedGroups"
            :key="group.id"
            class="group-chip"
            :class="{ active: group.id === activeGroupId }"
            @click="selectGroup(group.id)"
          >
            <text class="group-chip-name">{{ group.name }}</text>
            <text class="group-chip-role">{{ getRoleText(group.role) }}</text>
          </view>
        </view>
      </scroll-view>

      <view class="group-card">
        <view class="card-header">
          <image class="avatar" :src="activeGroupAvatar" mode="aspectFill" />
          <view class="header-info">
            <text class="name">{{ activeGroup.name }}</text>
            <view class="role-badge">
              <text>{{ getRoleText(activeGroup.role) }}</text>
            </view>
          </view>
          <view class="rank-badge" v-if="activeGroup.rank">
            <text>No.{{ activeGroup.rank }}</text>
          </view>
        </view>

        <view class="stats-row">
          <view class="stat-item">
            <text class="value">{{ activeGroup.member_count }}</text>
            <text class="label">成员数</text>
          </view>
          <view class="stat-item">
            <text class="value">{{ (activeGroup.total_mileage || 0).toFixed(1) }}km</text>
            <text class="label">总里程</text>
          </view>
          <view class="stat-item">
            <text class="value">{{ activeGroup.month_activity_count || 0 }}</text>
            <text class="label">本月活动</text>
          </view>
        </view>

        <view class="card-actions">
          <button class="detail-btn" @click="goToDetail">查看详情</button>
          <button class="leave-btn" @click="handleLeave" v-if="activeGroup.role !== 'creator'">退出跑团</button>
          <button class="delete-btn" @click="handleDeleteGroup" v-else>删除跑团</button>
        </view>
      </view>

      <view class="tab-bar">
        <view class="tab-item" :class="{ active: currentTab === 'overview' }" @click="currentTab = 'overview'">
          <text>概览</text>
        </view>
        <view class="tab-item" :class="{ active: currentTab === 'members' }" @click="loadMembers">
          <text>成员</text>
        </view>
        <view class="tab-item" :class="{ active: currentTab === 'activities' }" @click="loadActivities">
          <text>活动</text>
        </view>
      </view>

      <view class="tab-content" v-if="currentTab === 'overview'">
        <view class="overview-section">
          <text class="page-section-title">跑团简介</text>
          <text class="section-text">{{ activeGroup.description || '暂无简介' }}</text>
        </view>
      </view>

      <view class="tab-content" v-if="currentTab === 'members'">
        <view class="member-item" v-for="member in members" :key="member.id">
          <text class="member-name">{{ member.user_name }}</text>
          <text class="member-role">{{ getRoleText(member.role) }}</text>
          <text class="member-mileage">{{ (member.total_mileage || 0).toFixed(1) }}km</text>
        </view>
        <view class="empty-state" v-if="members.length === 0">
          <text>暂无成员数据</text>
        </view>
      </view>

      <view class="tab-content" v-if="currentTab === 'activities'">
        <view class="activity-item" v-for="activity in activities" :key="activity.id" @click="goToActivity(activity.id)">
          <text class="activity-title">{{ activity.title }}</text>
          <text class="activity-time">{{ formatTime(activity.activity_time) }}</text>
          <text class="activity-apply">{{ activity.apply_count }}/{{ activity.total_quota }}人</text>
        </view>
        <view class="empty-state" v-if="activities.length === 0">
          <text>暂无活动数据</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import {
  getMyRunGroups,
  leaveRunGroup,
  deleteRunGroup,
  getGroupMembers,
  getGroupActivities,
  resolveMediaUrl,
  getStoredToken,
  isAuthError
} from '@/utils/request.js';

const joinedGroups = ref([]);
const activeGroupId = ref(null);
const currentTab = ref('overview');
const members = ref([]);
const activities = ref([]);

const activeGroup = computed(() => joinedGroups.value.find(group => group.id === activeGroupId.value) || null);

const activeGroupAvatar = computed(() => {
  if (!activeGroup.value?.avatar) return '/static/default-avatar.svg';
  return resolveMediaUrl(activeGroup.value.avatar);
});

const resetTabData = () => {
  members.value = [];
  activities.value = [];
  currentTab.value = 'overview';
};

const selectGroup = (groupId) => {
  if (activeGroupId.value === groupId) return;
  activeGroupId.value = groupId;
  resetTabData();
};

const loadMyGroups = async () => {
  if (!getStoredToken()) return;
  try {
    const res = await getMyRunGroups();
    joinedGroups.value = Array.isArray(res) ? res : [];
    if (joinedGroups.value.length === 0) {
      activeGroupId.value = null;
      resetTabData();
      return;
    }

    if (!joinedGroups.value.some(group => group.id === activeGroupId.value)) {
      activeGroupId.value = joinedGroups.value[0].id;
    }
  } catch (e) {
    if (isAuthError(e)) return;
    joinedGroups.value = [];
    activeGroupId.value = null;
    resetTabData();
  }
};

const handleLeave = async () => {
  if (!activeGroup.value) return;

  uni.showModal({
    title: '确认退出',
    content: `确认退出 ${activeGroup.value.name} 吗？`,
    success: async (res) => {
      if (!res.confirm) return;
      try {
        await leaveRunGroup(activeGroup.value.id);
        uni.showToast({ title: '退出成功', icon: 'success' });
        await loadMyGroups();
      } catch (e) {
        uni.showToast({ title: e.message || e.detail || '退出失败', icon: 'none' });
      }
    }
  });
};

const handleDeleteGroup = async () => {
  if (!activeGroup.value) return;

  uni.showModal({
    title: '确认删除',
    content: `删除 ${activeGroup.value.name} 后无法恢复，确认继续吗？`,
    confirmColor: '#e03131',
    success: async (res) => {
      if (!res.confirm) return;
      try {
        await deleteRunGroup(activeGroup.value.id);
        uni.showToast({ title: '跑团已删除', icon: 'success' });
        await loadMyGroups();
      } catch (e) {
        uni.showToast({ title: e.message || e.detail || '删除失败', icon: 'none' });
      }
    }
  });
};

const loadMembers = async () => {
  if (!activeGroup.value) return;
  currentTab.value = 'members';
  if (members.value.length > 0) return;

  try {
    const res = await getGroupMembers(activeGroup.value.id, { page: 1, size: 100 });
    members.value = Array.isArray(res) ? res : [];
  } catch (e) {
    uni.showToast({ title: e.message || '加载失败', icon: 'none' });
  }
};

const loadActivities = async () => {
  if (!activeGroup.value) return;
  currentTab.value = 'activities';
  if (activities.value.length > 0) return;

  try {
    const res = await getGroupActivities(activeGroup.value.id, { page: 1, size: 20 });
    activities.value = Array.isArray(res?.items) ? res.items : [];
  } catch (e) {
    uni.showToast({ title: e.message || '加载失败', icon: 'none' });
  }
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
  return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
};

const goToDiscover = () => {
  uni.navigateTo({ url: '/pages/run-group/discover' });
};

const goToDetail = () => {
  if (!activeGroup.value) return;
  uni.navigateTo({ url: `/pages/run-group/detail?groupId=${activeGroup.value.id}` });
};

const goToActivity = (activityId) => {
  uni.navigateTo({ url: `/pages/run-group/activity-detail?activityId=${activityId}` });
};

onMounted(() => {
  loadMyGroups();
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
  min-height: 70vh;
  padding: 80rpx 60rpx;
  box-sizing: border-box;
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
  min-width: 180rpx;
  height: 68rpx;
  line-height: 68rpx;
  padding: 0 36rpx;
  margin: 0;
  border-radius: 30rpx;
  font-size: 26rpx;
  border: none;
  box-sizing: border-box;
}

.tip-btn::after {
  border: none;
}

.tip-btn.primary {
  background: #20C997;
  color: #fff;
}

.group-content {
  padding: 20rpx 30rpx 40rpx;
  box-sizing: border-box;
}

.group-switcher {
  white-space: nowrap;
  margin-bottom: 20rpx;
}

.group-switcher-row {
  display: inline-flex;
  gap: 16rpx;
  padding-right: 20rpx;
}

.group-chip {
  min-width: 200rpx;
  max-width: 320rpx;
  padding: 18rpx 24rpx;
  border-radius: 18rpx;
  background: #fff;
  border: 2rpx solid #e7edf3;
  box-sizing: border-box;
}

.group-chip.active {
  background: #20C997;
  border-color: #20C997;
}

.group-chip-name {
  display: block;
  font-size: 26rpx;
  font-weight: 700;
  color: #243447;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.group-chip-role {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #7b8794;
}

.group-chip.active .group-chip-name,
.group-chip.active .group-chip-role {
  color: #fff;
}

.group-card {
  background: linear-gradient(135deg, #20C997, #17a589);
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-sizing: border-box;
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
  flex-shrink: 0;
}

.header-info {
  flex: 1;
  min-width: 0;
}

.name {
  font-size: 32rpx;
  font-weight: bold;
  color: #fff;
  display: block;
  margin-bottom: 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  flex-shrink: 0;
  margin-left: 16rpx;
}

.stats-row {
  display: flex;
  justify-content: space-around;
  margin-bottom: 24rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.value {
  font-size: 40rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 8rpx;
}

.label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.9);
}

.card-actions {
  display: flex;
  gap: 16rpx;
}

.detail-btn,
.leave-btn,
.delete-btn {
  flex: 1;
  min-width: 0;
  height: 72rpx;
  line-height: 72rpx;
  padding: 0 12rpx;
  margin: 0;
  border-radius: 30rpx;
  font-size: 26rpx;
  border: none;
  box-sizing: border-box;
}

.detail-btn::after,
.leave-btn::after,
.delete-btn::after {
  border: none;
}

.detail-btn {
  background: rgba(255, 255, 255, 0.92);
  color: #0f766e;
}

.leave-btn {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.delete-btn {
  background: rgba(224, 49, 49, 0.22);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.45);
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

.member-item,
.activity-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1px solid #f0f0f0;
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
}

.member-mileage,
.activity-apply {
  font-size: 24rpx;
  color: #20C997;
  font-weight: bold;
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  padding: 24rpx 0 8rpx;
  font-size: 24rpx;
  color: #999;
}
</style>
