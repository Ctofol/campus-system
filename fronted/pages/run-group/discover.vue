<template>
  <view class="discover-page">
    <view class="navbar">
      <text class="back-btn" @click="goBack" v-if="showCreateForm">鈫?/text>
      <text class="title">{{ showCreateForm ? '鍒涘缓璺戝洟' : '璺戝洟鍙戠幇' }}</text>
      <text class="rank-btn" @click="goToRank" v-if="!showCreateForm">鎺掕姒?/text>
    </view>
    
    <!-- 鍒涘缓璺戝洟琛ㄥ崟 -->
    <view class="create-form" v-if="showCreateForm">
      <view class="form-item">
        <text class="label">璺戝洟鍚嶇О</text>
        <input class="input" v-model="formData.name" placeholder="璇疯緭鍏ヨ窇鍥㈠悕绉? maxlength="20" />
      </view>
      
      <view class="form-item">
        <text class="label">璺戝洟绠€浠?/text>
        <textarea 
          class="textarea" 
          v-model="formData.description" 
          placeholder="璇疯緭鍏ヨ窇鍥㈢畝浠? 
          maxlength="200"
        />
      </view>
      
      <button class="submit-btn" @click="handleCreate">鍒涘缓璺戝洟</button>
    </view>
    
    <!-- 璺戝洟鍒楄〃 -->
    <scroll-view 
      v-else
      scroll-y 
      class="group-list"
      @scrolltolower="loadMore"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
      <view 
        class="group-card" 
        v-for="(group, index) in groups" 
        :key="group.id"
        @click="goToDetail(group.id)"
      >
        <view class="rank-badge" v-if="index < 3" :class="'rank-' + (index + 1)">
          <text>No.{{ index + 1 }}</text>
        </view>
        <image class="avatar" :src="group.avatar || '/static/default-avatar.png'" mode="aspectFill" />
        <view class="info">
          <text class="name">{{ group.name }}</text>
          <text class="desc">{{ group.description || '鏆傛棤鎻忚堪' }}</text>
          <text class="stats">{{ group.member_count }}浜?路 {{ (group.total_mileage || 0).toFixed(1) }}km</text>
        </view>
        <button class="join-btn" @click.stop="handleJoin(group.id)">鍔犲叆</button>
      </view>
      
      <view class="loading" v-if="loading">
        <text>鍔犺浇涓?..</text>
      </view>
      
      <view class="no-more" v-if="!loading && noMore">
        <text>娌℃湁鏇村浜?/text>
      </view>
      
      <view class="empty" v-if="!loading && groups.length === 0">
        <text>鏆傛棤璺戝洟</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { getRunGroups, joinRunGroup, createRunGroup } from '@/utils/request.js';

const groups = ref([]);
const page = ref(1);
const loading = ref(false);
const refreshing = ref(false);
const noMore = ref(false);
const showCreateForm = ref(false);
const formData = ref({
  name: '',
  description: ''
});

onLoad((options) => {
  // 妫€鏌ユ槸鍚︽槸鍒涘缓妯″紡
  if (options.action === 'create') {
    showCreateForm.value = true;
  }
});

const loadGroups = async (refresh = false) => {
  if (loading.value) return;
  
  if (refresh) {
    page.value = 1;
    noMore.value = false;
  }
  
  loading.value = true;
  
  try {
    const res = await getRunGroups({
      page: page.value,
      size: 20
    });
    
    // 鏁版嵁楠岃瘉锛氱‘淇濊繑鍥炵殑鏄湁鏁堟暟缁?
    const validGroups = Array.isArray(res) ? res.filter(g => g && g.id) : [];
    
    if (refresh) {
      groups.value = validGroups;
    } else {
      groups.value.push(...validGroups);
    }
    
    if (validGroups.length < 20) {
      noMore.value = true;
    }
  } catch (e) {
    uni.showToast({ title: '鍔犺浇澶辫触', icon: 'none' });
  } finally {
    loading.value = false;
    refreshing.value = false;
  }
};

const onRefresh = () => {
  refreshing.value = true;
  loadGroups(true);
};

const loadMore = () => {
  if (!loading.value && !noMore.value) {
    page.value += 1;
    loadGroups();
  }
};

const handleJoin = async (groupId) => {
  try {
    console.log('灏濊瘯鍔犲叆璺戝洟:', groupId);
    const res = await joinRunGroup(groupId);
    console.log('鍔犲叆璺戝洟鍝嶅簲:', res);
    
    if (res && res.joinStatus) {
      uni.showToast({ title: '鍔犲叆鎴愬姛', icon: 'success' });
      // 鍒锋柊椤甸潰鎴栬烦杞埌鎴戠殑璺戝洟
      setTimeout(() => {
        uni.redirectTo({ url: '/pages/run-group/my' });
      }, 1500);
    } else {
      const message = res?.message || '鍔犲叆澶辫触';
      uni.showToast({ title: message, icon: 'none' });
    }
  } catch (e) {
    console.error('鍔犲叆璺戝洟澶辫触:', e);
    const errorMsg = e.message || e.detail || '加入失败，请重试';
    uni.showToast({ title: errorMsg, icon: 'none' });
  }
};

const handleCreate = async () => {
  if (!formData.value.name) {
    uni.showToast({ title: '璇疯緭鍏ヨ窇鍥㈠悕绉?, icon: 'none' });
    return;
  }
  
  if (!formData.value.description) {
    uni.showToast({ title: '璇疯緭鍏ヨ窇鍥㈢畝浠?, icon: 'none' });
    return;
  }
  
  try {
    uni.showLoading({ title: '鍒涘缓涓?..' });
    await createRunGroup(formData.value);
    uni.hideLoading();
    uni.showToast({ title: '鍒涘缓鎴愬姛', icon: 'success' });
    
    // 璺宠浆鍒版垜鐨勮窇鍥㈤〉闈?
    setTimeout(() => {
      uni.redirectTo({ url: '/pages/run-group/my' });
    }, 1500);
  } catch (e) {
    uni.hideLoading();
    uni.showToast({ title: e.message || e.detail || '创建失败', icon: 'none' });
  }
};

const goBack = () => {
  showCreateForm.value = false;
  // 杩斿洖鍚庨噸鏂板姞杞借窇鍥㈠垪琛?
  loadGroups(true);
};

const goToDetail = (groupId) => {
  uni.navigateTo({ url: `/pages/run-group/detail?groupId=${groupId}` });
};

const goToRank = () => {
  uni.navigateTo({ url: '/pages/run-group/rank' });
};

onMounted(() => {
  if (!showCreateForm.value) {
    loadGroups(true);
  }
});
</script>

<style scoped>
.discover-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.navbar {
  position: sticky;
  top: 0;
  background: #20C997;
  padding: 20rpx 30rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;
}

.back-btn {
  font-size: 36rpx;
  color: #fff;
  cursor: pointer;
}

.title {
  font-size: 32rpx;
  font-weight: bold;
  color: #fff;
}

.rank-btn {
  font-size: 26rpx;
  color: #fff;
  padding: 8rpx 20rpx;
  border: 1px solid #fff;
  border-radius: 20rpx;
}

.create-form {
  padding: 40rpx 30rpx;
}

.form-item {
  margin-bottom: 40rpx;
}

.label {
  display: block;
  font-size: 28rpx;
  color: #333;
  margin-bottom: 16rpx;
  font-weight: bold;
}

.input {
  width: 100%;
  padding: 24rpx;
  background: #fff;
  border-radius: 16rpx;
  font-size: 28rpx;
  border: 2rpx solid #e0e0e0;
}

.textarea {
  width: 100%;
  min-height: 200rpx;
  padding: 24rpx;
  background: #fff;
  border-radius: 16rpx;
  font-size: 28rpx;
  border: 2rpx solid #e0e0e0;
}

.submit-btn {
  width: 100%;
  padding: 28rpx;
  background: #20C997;
  color: #fff;
  border-radius: 50rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
  margin-top: 40rpx;
}

.group-list {
  height: calc(100vh - 80rpx);
  padding: 20rpx 30rpx;
}

.group-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
  position: relative;
}

.rank-badge {
  position: absolute;
  top: 10rpx;
  left: 10rpx;
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
  font-size: 20rpx;
  color: #fff;
}

.rank-1 {
  background: linear-gradient(135deg, #FFD700, #FFA500);
}

.rank-2 {
  background: linear-gradient(135deg, #C0C0C0, #808080);
}

.rank-3 {
  background: linear-gradient(135deg, #CD7F32, #8B4513);
}

.avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  margin-right: 20rpx;
  background: #e0e0e0;
}

.info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.name {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 8rpx;
}

.desc {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 8rpx;
}

.stats {
  font-size: 22rpx;
  color: #666;
}

.join-btn {
  padding: 12rpx 30rpx;
  background: #20C997;
  color: #fff;
  border-radius: 30rpx;
  font-size: 24rpx;
  border: none;
}

.loading, .no-more, .empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
  font-size: 24rpx;
}
</style>

