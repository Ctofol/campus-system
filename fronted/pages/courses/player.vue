<template>
  <view class="player-page">
    <!-- 视频播放器 -->
    <video
      v-if="contentType === 'video' && videoUrl"
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
    <view v-else-if="contentType === 'video'" class="video-placeholder">
      <text class="placeholder-text">{{ loadError || '加载视频中…' }}</text>
    </view>
    <view v-else class="resource-panel">
      <text class="resource-title">{{ contentType === 'document' ? '文档资料' : '外部链接' }}</text>
      <text class="resource-url">{{ resourceUrl || '暂无可访问地址' }}</text>
      <button class="resource-btn" @click="openResource">
        {{ contentType === 'document' ? '打开文档' : '打开链接' }}
      </button>
    </view>
    
    <!-- 课程信息 -->
    <view class="content-info">
      <text class="content-title">{{ contentTitle }}</text>
      <text class="content-desc">{{ contentDesc }}</text>
    </view>
    
    <!-- 课程列表 -->
    <view class="playlist-section">
      <view class="section-header">
        <text class="page-section-title">课程列表</text>
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
import { request, resolveMediaUrl } from '@/utils/request.js';

const contentId = ref(null);
const currentContentId = ref(null);
const videoUrl = ref('');
const contentType = ref('video');
const resourceUrl = ref('');
const contentTitle = ref('');
const contentDesc = ref('');
const lastPosition = ref(0);
const playlist = ref([]);
const progressTimer = ref(null);
const currentTime = ref(0);
const loadError = ref('');

const truncateUrl = (url, max = 120) => {
  if (!url) return '';
  return url.length > max ? `${url.slice(0, max)}...` : url;
};

const copyExternalLink = (url) => {
  uni.setClipboardData({
    data: url,
    success: () => uni.showToast({ title: '链接已复制', icon: 'none' })
  });
};

const openExternalLink = (url) => {
  if (!url) {
    uni.showToast({ title: '暂无可访问地址', icon: 'none' });
    return;
  }

  if (/^https?:\/\//i.test(url)) {
    uni.showModal({
      title: '打开外部链接',
      content: `即将打开：\n${truncateUrl(url)}`,
      confirmText: '打开',
      cancelText: '复制链接',
      success: (res) => {
        if (res.confirm) {
          uni.navigateTo({
            url: `/pages/common/webview?url=${encodeURIComponent(url)}`
          });
        } else if (res.cancel) {
          copyExternalLink(url);
        }
      }
    });
    return;
  }

  copyExternalLink(url);
};

const loadContent = async (id) => {
  videoUrl.value = '';
  loadError.value = '';
  try {
    const res = await request({
      url: `/courses/content/${id}`,
      method: 'GET',
      timeout: 120000
    });
    
    currentContentId.value = res.id;
    contentTitle.value = res.title;
    contentDesc.value = res.description || '';
    contentType.value = res.content_type || 'video';

    if (res.content_url) {
      const fullUrl = resolveMediaUrl(res.content_url);
      resourceUrl.value = fullUrl;
      if (contentType.value === 'video') {
        videoUrl.value = fullUrl;
      } else {
        videoUrl.value = '';
      }
    } else {
      loadError.value = contentType.value === 'video' ? '暂无视频地址' : '暂无内容地址';
    }

    if (contentType.value === 'video') {
      loadProgress(id);
    } else {
      lastPosition.value = 0;
    }
    
  } catch (e) {
    console.error('Failed to load content:', e);
    loadError.value = e?.message || '加载失败';
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
  const msg = e?.detail?.errMsg || e?.errMsg || JSON.stringify(e?.detail || {});
  console.error('Video error:', msg, e);
  uni.showModal({
    title: '播放失败',
    content: '请确认：1) 小程序后台已配置该视频域名为下载/音视频合法域名；2) 地址为 https 且可直连；3) 当前网络正常。',
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

const openResource = () => {
  if (!resourceUrl.value) {
    uni.showToast({ title: '暂无可访问地址', icon: 'none' });
    return;
  }
  if (contentType.value === 'document') {
    uni.downloadFile({
      url: resourceUrl.value,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300 && res.tempFilePath) {
          uni.openDocument({
            filePath: res.tempFilePath,
            showMenu: true,
            fail: () => uni.showToast({ title: '文档打开失败', icon: 'none' })
          });
        } else {
          uni.showToast({ title: '文档下载失败', icon: 'none' });
        }
      },
      fail: () => uni.showToast({ title: '文档下载失败', icon: 'none' })
    });
    return;
  }
  // #ifdef H5
  window.open(resourceUrl.value, '_blank');
  return;
  // #endif
  openExternalLink(resourceUrl.value);
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

.video-placeholder {
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #111;
  display: flex;
  align-items: center;
  justify-content: center;
}
.placeholder-text {
  color: #999;
  font-size: 28rpx;
  padding: 24rpx;
  text-align: center;
}
.video-player {
  width: 100%;
  height: 450rpx;
  background: #000;
}
.resource-panel {
  width: 100%;
  min-height: 280rpx;
  background: #111;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 32rpx;
  box-sizing: border-box;
}
.resource-title {
  font-size: 32rpx;
  font-weight: 600;
  margin-bottom: 16rpx;
}
.resource-url {
  font-size: 24rpx;
  line-height: 1.5;
  color: #cbd5e1;
  word-break: break-all;
}
.resource-btn {
  margin-top: 24rpx;
  width: 240rpx;
  height: 72rpx;
  line-height: 72rpx;
  border-radius: 36rpx;
  background: #20C997;
  color: #fff;
  font-size: 28rpx;
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
