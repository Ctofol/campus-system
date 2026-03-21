<template>
  <view class="player-page">
    <!-- 视频播放器 -->
    <video
      :src="videoUrl"
      class="video-player"
      controls
      :show-center-play-btn="true"
      :show-play-btn="true"
      :enable-progress-gesture="true"
      :initial-time="lastPosition"
      @timeupdate="onTimeUpdate"
      @ended="onVideoEnded"
      @error="onVideoError"
    ></video>
    
    <!-- 课程信息 -->
    <view class="content-info">
      <text class="content-title">{{ contentTitle }}</text>
      <text class="content-desc">{{ contentDesc }}</text>
    </view>
    
    <!-- 课程列表 -->
    <view class="playlist-section">
      <view class="section-header">
        <text class="section-title">课程列表</text>
        <text class="section-count">共{{ playlist.length }}节</text>
      </view>
      
      <view 
        class="playlist-item"
        :class="{ active: item.id === currentContentId }"
        v-for="(item, index) in playlist"
        :key="item.id"
        @click="switchContent(item)"
      >
        <view class="item-index">{{ index + 1 }}</view>
        <view class="item-info">
          <text class="item-title">{{ item.title }}</text>
          <text class="item-duration">{{ formatDuration(item.duration) }}</text>
        </view>
        <text class="item-status" v-if="item.completed">✓</text>
        <text class="item-icon" v-else>▶️</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad, onUnload } from '@dcloudio/uni-app';
import { request, BASE_URL } from '@/utils/request.js';

const contentId = ref(null);
const currentContentId = ref(null);
const videoUrl = ref('');
const contentTitle = ref('');
const contentDesc = ref('');
const lastPosition = ref(0);
const playlist = ref([]);
const progressTimer = ref(null);
const currentTime = ref(0);

const loadContent = async (id) => {
  try {
    const res = await request({
      url: `/courses/content/${id}`,
      method: 'GET'
    });
    
    currentContentId.value = res.id;
    contentTitle.value = res.title;
    contentDesc.value = res.description || '';
    
    // 拼接完整视频URL
    if (res.content_url) {
      videoUrl.value = res.content_url.startsWith('http') 
        ? res.content_url 
        : `${BASE_URL}${res.content_url}`;
    }
    
    // 加载播放进度
    loadProgress(id);
    
  } catch (e) {
    console.error('Failed to load content:', e);
    uni.showToast({ title: '加载失败', icon: 'none' });
  }
};

const loadProgress = async (id) => {
  try {
    const res = await request({
      url: `/courses/content/${id}/progress`,
      method: 'GET'
    });
    
    lastPosition.value = res.last_position || 0;
    
  } catch (e) {
    console.error('Failed to load progress:', e);
  }
};

const loadPlaylist = async (courseId) => {
  try {
    const res = await request({
      url: `/courses/${courseId}`,
      method: 'GET'
    });
    
    playlist.value = res.contents || [];
    
  } catch (e) {
    console.error('Failed to load playlist:', e);
  }
};

const onTimeUpdate = (e) => {
  currentTime.value = e.detail.currentTime;
  
  // 每10秒保存一次进度
  if (!progressTimer.value) {
    progressTimer.value = setInterval(() => {
      saveProgress();
    }, 10000);
  }
};

const saveProgress = async () => {
  if (!currentContentId.value || currentTime.value === 0) return;
  
  try {
    await request({
      url: `/courses/content/${currentContentId.value}/progress?last_position=${Math.floor(currentTime.value)}&completed=false`,
      method: 'POST'
    });
  } catch (e) {
    console.error('Failed to save progress:', e);
  }
};

const onVideoEnded = async () => {
  // 视频播放完成，标记为已完成
  try {
    await request({
      url: `/courses/content/${currentContentId.value}/progress?last_position=0&completed=true`,
      method: 'POST'
    });
    
    uni.showToast({ title: '已完成本节课程', icon: 'success' });
    
    // 自动播放下一节
    const currentIndex = playlist.value.findIndex(item => item.id === currentContentId.value);
    if (currentIndex < playlist.value.length - 1) {
      const nextContent = playlist.value[currentIndex + 1];
      setTimeout(() => {
        switchContent(nextContent);
      }, 2000);
    }
    
  } catch (e) {
    console.error('Failed to mark as completed:', e);
  }
};

const onVideoError = (e) => {
  console.error('Video error:', e);
  uni.showModal({
    title: '播放失败',
    content: '视频加载失败，请检查网络连接',
    showCancel: false
  });
};

const switchContent = (content) => {
  if (content.id === currentContentId.value) return;
  
  // 保存当前进度
  saveProgress();
  
  // 切换到新内容
  loadContent(content.id);
};

const formatDuration = (seconds) => {
  if (!seconds) return '--';
  const minutes = Math.floor(seconds / 60);
  return `${minutes}分钟`;
};

onLoad((options) => {
  if (options.contentId) {
    contentId.value = options.contentId;
    loadContent(options.contentId);
  }
  
  if (options.courseId) {
    loadPlaylist(options.courseId);
  }
});

onUnload(() => {
  // 页面卸载时保存进度
  saveProgress();
  
  if (progressTimer.value) {
    clearInterval(progressTimer.value);
    progressTimer.value = null;
  }
});
</script>

<style scoped>
.player-page {
  min-height: 100vh;
  background: #000;
}

.video-player {
  width: 100%;
  height: 450rpx;
  background: #000;
}

.content-info {
  background: #fff;
  padding: 30rpx;
}

.content-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 16rpx;
}

.content-desc {
  font-size: 26rpx;
  color: #666;
  line-height: 1.6;
  display: block;
}

.playlist-section {
  background: #fff;
  margin-top: 20rpx;
  padding: 30rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
}

.section-count {
  font-size: 24rpx;
  color: #999;
}

.playlist-item {
  display: flex;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.playlist-item.active {
  background: #f5f7fa;
  margin: 0 -30rpx;
  padding: 24rpx 30rpx;
}

.playlist-item.active .item-title {
  color: #20C997;
}

.item-index {
  width: 50rpx;
  height: 50rpx;
  background: #f5f7fa;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  color: #666;
  margin-right: 20rpx;
}

.playlist-item.active .item-index {
  background: #20C997;
  color: #fff;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.item-title {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 8rpx;
}

.item-duration {
  font-size: 24rpx;
  color: #999;
}

.item-status {
  font-size: 32rpx;
  color: #20C997;
}

.item-icon {
  font-size: 28rpx;
  color: #ccc;
}
</style>
