<template>
  <view class="detail-page">
    <view class="header-card" v-if="groupDetail">
      <view class="header-bg"></view>
      <view class="header-content">
        <image class="avatar" :src="groupDetail.avatar || '/static/default-avatar.png'" mode="aspectFill" />
        <text class="name">{{ groupDetail.name }}</text>
        <view class="rank-badge" v-if="groupDetail.rank">
          <text>鎺掑悕 No.{{ groupDetail.rank }}</text>
        </view>
        <view class="stats-row">
          <view class="stat-item">
            <text class="value">{{ groupDetail.member_count }}</text>
            <text class="label">鎴愬憳</text>
          </view>
          <view class="stat-item">
            <text class="value">{{ (groupDetail.total_mileage || 0).toFixed(1) }}km</text>
            <text class="label">鎬婚噷绋?/text>
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
        <text>姒傝</text>
      </view>
      <view 
        class="tab-item" 
        :class="{active: currentTab === 'members'}"
        @click="loadMembers"
      >
        <text>鎴愬憳</text>
      </view>
      <view 
        class="tab-item" 
        :class="{active: currentTab === 'activities'}"
        @click="loadActivities"
      >
        <text>娲诲姩</text>
      </view>
    </view>
    
    <view class="tab-content">
      <!-- 姒傝 -->
      <view v-if="currentTab === 'overview' && groupDetail">
        <view class="desc-card">
          <text class="card-title">璺戝洟绠€浠?/text>
          <text class="desc-text">{{ groupDetail.description || '鏆傛棤绠€浠? }}</text>
        </view>
      </view>
      
      <!-- 鎴愬憳鍒楄〃 -->
      <view v-if="currentTab === 'members'">
        <view class="member-item" v-for="member in members" :key="member.id">
          <text class="member-name">{{ member.user_name }}</text>
          <text class="member-role">{{ getRoleText(member.role) }}</text>
          <text class="member-mileage">{{ (member.total_mileage || 0).toFixed(1) }}km</text>
        </view>
      </view>
      
      <!-- 娲诲姩鍒楄〃 -->
      <view v-if="currentTab === 'activities'">
        <view class="activity-item" v-for="activity in activities" :key="activity.id" @click="goToActivity(activity.id)">
          <text class="activity-title">{{ activity.title }}</text>
          <text class="activity-time">{{ formatTime(activity.activity_time) }}</text>
          <text class="activity-apply">{{ activity.apply_count }}/{{ activity.total_quota }}浜?/text>
        </view>
      </view>
    </view>
    
    <view class="bottom-bar" v-if="groupDetail">
      <button class="action-btn" @click="handleJoin" v-if="!isMember">鍔犲叆璺戝洟</button>
      <button class="action-btn primary" @click="goToCreateActivity" v-else-if="isCreator">鍙戝竷娲诲姩</button>
      <button class="action-btn leave" @click="handleLeave" v-else>閫€鍑鸿窇鍥?/button>
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

// 鑾峰彇URL鍙傛暟
onLoad((options) => {
  if (options.groupId) {
    groupId.value = parseInt(options.groupId);
    loadDetail();
    // 绔嬪嵆鍔犺浇鎴愬憳淇℃伅浠ュ垽鏂敤鎴疯韩浠?
    checkMemberStatus();
  } else {
    uni.showToast({ title: '鍙傛暟閿欒', icon: 'none' });
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  }
});

// 妫€鏌ョ敤鎴峰湪璺戝洟涓殑韬唤
const checkMemberStatus = async () => {
  try {
    const userInfo = uni.getStorageSync('userInfo');
    console.log('褰撳墠鐢ㄦ埛淇℃伅:', userInfo);
    
    const currentUserId = userInfo?.id || userInfo?.userId;
    if (!currentUserId) {
      console.log('鏈壘鍒扮敤鎴蜂俊鎭垨userId');
      return;
    }
    
    const res = await getGroupMembers(groupId.value, { page: 1, size: 100 });
    console.log('鎴愬憳鍒楄〃鍝嶅簲:', res);
    
    // 鍚庣杩斿洖鐨勬槸鏁扮粍锛屼笉鏄垎椤靛璞?
    if (Array.isArray(res)) {
      members.value = res;
      const currentMember = res.find(m => m.user_id === currentUserId);
      console.log('鎵惧埌鐨勫綋鍓嶆垚鍛?', currentMember);
      
      if (currentMember) {
        isMember.value = true;
        isCreator.value = currentMember.role === 'creator';
        console.log('鐢ㄦ埛韬唤:', { isMember: isMember.value, isCreator: isCreator.value, role: currentMember.role });
      } else {
        console.log('鐢ㄦ埛涓嶆槸璇ヨ窇鍥㈡垚鍛?);
      }
    } else {
      console.log('鎴愬憳鍒楄〃鏍煎紡閿欒:', res);
    }
  } catch (e) {
    console.error('妫€鏌ユ垚鍛樿韩浠藉け璐?', e);
  }
};

const loadDetail = async () => {
  try {
    console.log('鍔犺浇璺戝洟璇︽儏, groupId:', groupId.value);
    const res = await getRunGroups({ page: 1, size: 100 });
    console.log('璺戝洟鍒楄〃:', res);
    
    if (res && res.items) {
      // 濡傛灉杩斿洖鐨勬槸鍒嗛〉鏁版嵁
      groupDetail.value = res.items.find(g => g.id === groupId.value);
    } else if (Array.isArray(res)) {
      // 濡傛灉杩斿洖鐨勬槸鏁扮粍
      groupDetail.value = res.find(g => g.id === groupId.value);
    }
    
    console.log('鎵惧埌鐨勮窇鍥㈣鎯?', groupDetail.value);
    
    if (!groupDetail.value) {
      uni.showToast({ title: '璺戝洟涓嶅瓨鍦?, icon: 'none' });
      setTimeout(() => {
        uni.navigateBack();
      }, 1500);
    }
  } catch (e) {
    console.error('鍔犺浇璺戝洟璇︽儏澶辫触:', e);
    uni.showToast({ title: '鍔犺浇澶辫触', icon: 'none' });
  }
};

const loadMembers = async () => {
  currentTab.value = 'members';
  // 濡傛灉宸茬粡鍔犺浇杩囨垚鍛樺垪琛紝鐩存帴杩斿洖
  if (members.value.length > 0) return;
  
  // 鍚﹀垯璋冪敤妫€鏌ュ嚱鏁?
  await checkMemberStatus();
};

const loadActivities = async () => {
  currentTab.value = 'activities';
  if (activities.value.length > 0) return;
  
  try {
    const res = await getGroupActivities(groupId.value, { page: 1, size: 20 });
    activities.value = res.items;
  } catch (e) {
    uni.showToast({ title: '鍔犺浇澶辫触', icon: 'none' });
  }
};

const handleJoin = async () => {
  try {
    const res = await joinRunGroup(groupId.value);
    if (res.joinStatus) {
      uni.showToast({ title: '鍔犲叆鎴愬姛', icon: 'success' });
      isMember.value = true;
      loadMembers();
    } else {
      uni.showToast({ title: res.message, icon: 'none' });
    }
  } catch (e) {
    uni.showToast({ title: '鍔犲叆澶辫触', icon: 'none' });
  }
};

const handleLeave = async () => {
  uni.showModal({
    title: '纭閫€鍑?,
    content: '閫€鍑哄悗灏嗘棤娉曟煡鐪嬭窇鍥俊鎭?,
    success: async (res) => {
      if (res.confirm) {
        try {
          await leaveRunGroup(groupId.value);
          uni.showToast({ title: '閫€鍑烘垚鍔?, icon: 'success' });
          setTimeout(() => {
            uni.navigateBack();
          }, 1500);
        } catch (e) {
          uni.showToast({ title: e.message || e.detail || '退出失败', icon: 'none' });
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
    'creator': '鍒涘缓鑰?,
    'admin': '绠＄悊鍛?,
    'member': '鎴愬憳'
  };
  return roleMap[role] || '鎴愬憳';
};

const formatTime = (timeStr) => {
  const date = new Date(timeStr);
  return `${date.getMonth() + 1}鏈?{date.getDate()}鏃?${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
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

