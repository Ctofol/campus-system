<template>
  <view class="detail-container">
    <view class="skeleton-wrapper" v-if="loading">
      <view class="skeleton-banner"></view>
      <view class="skeleton-content">
        <view class="skeleton-title"></view>
        <view class="skeleton-text"></view>
        <view class="skeleton-text short"></view>
      </view>
    </view>

    <view v-else-if="course.id">
      <image
        class="course-banner"
        :src="getFullImageUrl(course.cover_url)"
        mode="aspectFill"
        @error="handleImageError(course.cover_url)"
      ></image>

      <view class="course-header">
        <text class="course-title">{{ course.title }}</text>
        <text class="course-desc">{{ course.description || '暂无课程简介' }}</text>
        <view class="course-stats">
          <view class="stat-item">
            <image class="stat-icon-img" src="/static/icons/icon-learning-users.svg" mode="aspectFit" />
            <text>{{ course.enrollment_count || 0 }} 人已选</text>
          </view>
          <view class="stat-item">
            <image class="stat-icon-img" src="/static/icons/icon-course-meta.svg" mode="aspectFit" />
            <text>{{ course.contents?.length || 0 }} 节课</text>
          </view>
        </view>

        <view class="progress-section" v-if="course.enrolled && userRole === 'student'">
          <view class="progress-header">
            <text class="progress-label">学习进度</text>
            <text class="progress-value">{{ courseProgress }}%</text>
          </view>
          <view class="progress-bar">
            <view class="progress-fill" :style="{ width: courseProgress + '%' }"></view>
          </view>
        </view>
      </view>

      <view class="content-section">
        <view class="page-section-title">课程内容</view>
        <view
          class="content-item"
          v-for="(content, index) in course.contents"
          :key="content.id"
          @click="playContent(content)"
        >
          <view class="content-index">{{ index + 1 }}</view>
          <view class="content-info">
            <text class="content-title">{{ content.title }}</text>
            <view class="content-meta">
              <text class="content-type" :class="'content-type--' + content.content_type">
                {{ getContentTypeLabel(content.content_type) }}
              </text>
              <text class="content-duration" v-if="content.duration">
                {{ formatDuration(content.duration) }}
              </text>
            </view>
          </view>
          <view class="content-action">
            <view class="play-mark" v-if="content.content_type === 'video'"></view>
            <text class="content-action-text" v-else>打开</text>
          </view>
        </view>

        <view class="empty-content" v-if="!course.contents || course.contents.length === 0">
          <text class="empty-text">暂无课程内容</text>
        </view>
      </view>
    </view>

    <view class="empty-state" v-else>
      <image class="empty-icon-img" src="/static/icons/icon-course.svg" mode="aspectFit" />
      <text class="empty-text">课程不存在</text>
    </view>

    <view class="video-player-mask" v-if="activeVideo" @click="closeVideoPlayer">
      <view class="video-player-panel" @click.stop>
        <view class="video-player-header">
          <text class="video-player-title">{{ activeVideo.title }}</text>
          <view class="video-player-close" @click="closeVideoPlayer">
            <text>×</text>
          </view>
        </view>
        <video
          class="course-video"
          :src="activeVideoUrl"
          :initial-time="videoInitialTime"
          controls
          autoplay
          object-fit="contain"
          @timeupdate="onVideoTimeUpdate"
          @ended="onVideoEnded"
          @error="onVideoError"
        ></video>
      </view>
    </view>

    <view class="bottom-bar" v-if="!loading && course.id">
      <button
        class="enroll-btn"
        :class="{ enrolled: course.enrolled }"
        @click="handleEnroll"
        :loading="enrolling"
        v-if="userRole === 'student'"
      >
        {{ course.enrolled ? '进入学习' : '加入课程' }}
      </button>
      <button
        class="manage-btn"
        @click="manageContent"
        v-if="userRole === 'teacher' && course.teacher_id === userId"
      >
        管理课程内容
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { request, resolveMediaUrl } from '@/utils/request.js';

const courseId = ref(null);
const course = ref({
  title: '',
  description: '',
  cover_url: '',
  enrolled: false,
  enrollment_count: 0,
  contents: [],
  teacher_id: 0,
  id: null
});
const courseProgress = ref(0);
const userRole = ref('student');
const userId = ref(0);
const loading = ref(true);
const enrolling = ref(false);
const brokenImages = ref(new Set());
const activeVideo = ref(null);
const activeVideoUrl = ref('');
const videoInitialTime = ref(0);
const lastProgressSaveAt = ref(0);

const getFullImageUrl = (url) => {
  if (!url) return '/static/home/hero-bg.png';
  if (brokenImages.value.has(url)) return '/static/home/hero-bg.png';
  if (url.startsWith('http') || url.startsWith('blob:') || url.startsWith('wxfile:')) return url;
  return resolveMediaUrl(url);
};

const handleImageError = (url) => {
  if (url) brokenImages.value.add(url);
};

const loadCourseDetail = async () => {
  loading.value = true;
  try {
    const res = await request({
      url: `/courses/${courseId.value}`,
      method: 'GET'
    });
    course.value = {
      ...res,
      contents: Array.isArray(res.contents) ? res.contents : []
    };

    if (res.enrolled && userRole.value === 'student') {
      loadProgress();
    }
  } catch (e) {
    console.error('Failed to load course detail:', e);
    let errorMsg = '加载失败';
    if (e.statusCode === 404) {
      errorMsg = '课程不存在';
    } else if (e.type === 'network') {
      errorMsg = '网络连接失败';
    } else if (e.message) {
      errorMsg = e.message;
    }
    uni.showModal({
      title: '加载失败',
      content: errorMsg,
      showCancel: false
    });
  } finally {
    loading.value = false;
  }
};

const loadProgress = async () => {
  try {
    const res = await request({
      url: `/courses/me/enrollments/${courseId.value}/progress`,
      method: 'GET'
    });
    courseProgress.value = res.percent || 0;
  } catch (e) {
    console.error('Failed to load progress:', e);
  }
};

const handleEnroll = async () => {
  if (course.value.enrolled) {
    if (!course.value.contents || course.value.contents.length === 0) {
      uni.showToast({ title: '暂无课程内容', icon: 'none' });
      return;
    }
    playContent(course.value.contents[0]);
    return;
  }

  enrolling.value = true;
  try {
    await request({
      url: `/courses/${courseId.value}/enroll`,
      method: 'POST'
    });
    course.value.enrolled = true;
    course.value.enrollment_count = (course.value.enrollment_count || 0) + 1;
    uni.showToast({
      title: '加入成功',
      icon: 'success',
      duration: 1500
    });
    uni.$emit('courseEnrolled');
    loadProgress();
  } catch (e) {
    console.error('Failed to enroll:', e);
    let errorMsg = '加入失败';
    if (e.statusCode === 400) {
      errorMsg = '已加入过此课程';
      await loadCourseDetail();
    } else if (e.type === 'network') {
      errorMsg = '网络连接失败';
    } else if (e.message) {
      errorMsg = e.message;
    }
    if (e.statusCode !== 400) {
      uni.showModal({
        title: '加入失败',
        content: errorMsg,
        showCancel: false
      });
    }
  } finally {
    enrolling.value = false;
  }
};

const saveVideoProgress = async (position, completed = false) => {
  if (!activeVideo.value?.id) return;
  const safePosition = Math.max(0, Math.round(Number(position) || 0));
  try {
    await request({
      url: `/courses/content/${activeVideo.value.id}/progress?last_position=${safePosition}&completed=${completed}`,
      method: 'POST'
    });
    if (completed) {
      loadProgress();
    }
  } catch (e) {
    console.error('Save video progress failed:', e);
  }
};

const openVideoContent = async (content) => {
  activeVideo.value = content;
  activeVideoUrl.value = resolveMediaUrl(content.content_url);
  videoInitialTime.value = 0;
  lastProgressSaveAt.value = 0;

  try {
    const progress = await request({
      url: `/courses/content/${content.id}/progress`,
      method: 'GET'
    });
    if (progress && !progress.completed && Number(progress.last_position) > 0) {
      videoInitialTime.value = Number(progress.last_position);
    }
  } catch (e) {
    console.error('Load video progress failed:', e);
  }
};

const closeVideoPlayer = () => {
  if (activeVideo.value && lastProgressSaveAt.value > 0) {
    saveVideoProgress(lastProgressSaveAt.value, false);
  }
  activeVideo.value = null;
  activeVideoUrl.value = '';
  videoInitialTime.value = 0;
  lastProgressSaveAt.value = 0;
};

const onVideoTimeUpdate = (e) => {
  const currentTime = Number(e.detail?.currentTime || 0);
  if (currentTime - lastProgressSaveAt.value >= 5) {
    lastProgressSaveAt.value = currentTime;
    saveVideoProgress(currentTime, false);
  }
};

const onVideoEnded = (e) => {
  const duration = Number(e.detail?.duration || activeVideo.value?.duration || lastProgressSaveAt.value || 0);
  saveVideoProgress(duration, true);
};

const onVideoError = (e) => {
  console.error('Course video error:', e);
  uni.showToast({ title: '视频播放失败', icon: 'none' });
};

const copyExternalLink = (url) => {
  uni.setClipboardData({
    data: url,
    success: () => {
      uni.showToast({ title: '链接已复制', icon: 'none' });
    }
  });
};

const openExternalLink = (url) => {
  if (!url) {
    uni.showToast({ title: '暂无可访问地址', icon: 'none' });
    return;
  }
  uni.showModal({
    title: '外部链接',
    content: `即将复制链接到剪贴板：\n${url}`,
    confirmText: '复制链接',
    showCancel: false,
    success: () => {
      copyExternalLink(url);
    }
  });
};

const playContent = (content) => {
  if (!course.value.enrolled && userRole.value === 'student') {
    uni.showModal({
      title: '提示',
      content: '请先加入课程后再学习',
      showCancel: false
    });
    return;
  }

  if (!content?.content_url) {
    uni.showToast({ title: '暂无内容地址', icon: 'none' });
    return;
  }

  const fullUrl = resolveMediaUrl(content.content_url);
  if (content.content_type === 'video') {
    openVideoContent(content);
    return;
  }

  if (content.content_type === 'document') {
    uni.downloadFile({
      url: fullUrl,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300 && res.tempFilePath) {
          uni.openDocument({
            filePath: res.tempFilePath,
            showMenu: true,
            fail: () => {
              uni.showToast({ title: '文档打开失败', icon: 'none' });
            }
          });
        } else {
          uni.showToast({ title: '文档下载失败', icon: 'none' });
        }
      },
      fail: () => {
        uni.showToast({ title: '文档下载失败', icon: 'none' });
      }
    });
    return;
  }

  if (content.content_type === 'link') {
    openExternalLink(fullUrl);
  }
};

const manageContent = () => {
  uni.navigateTo({
    url: `/pages/courses/content-manage?courseId=${courseId.value}`
  });
};

const getContentTypeLabel = (type) => {
  if (type === 'video') return '视频课时';
  if (type === 'document') return '文档资料';
  if (type === 'link') return '外部链接';
  return '课程内容';
};

const formatDuration = (seconds) => {
  const total = Math.max(0, Number(seconds) || 0);
  const minutes = Math.floor(total / 60);
  const secs = total % 60;
  return `${minutes}:${String(secs).padStart(2, '0')}`;
};

onLoad((options) => {
  if (!options.id) {
    uni.showToast({ title: '课程ID不存在', icon: 'none' });
    loading.value = false;
    return;
  }

  courseId.value = options.id;
  userRole.value = uni.getStorageSync('userRole') || 'student';
  const userInfo = uni.getStorageSync('userInfo');
  if (userInfo) {
    try {
      const info = typeof userInfo === 'string' ? JSON.parse(userInfo) : userInfo;
      userId.value = info.id || 0;
    } catch (e) {
      console.error('Parse userInfo error:', e);
    }
  }

  loadCourseDetail();
});
</script>

<style lang="scss" scoped>
.detail-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 120rpx;
}

.skeleton-wrapper {
  background: #fff;
}

.skeleton-banner {
  width: 100%;
  height: 400rpx;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}

.skeleton-content {
  padding: 40rpx 30rpx;
}

.skeleton-title,
.skeleton-text {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 8rpx;
}

.skeleton-title {
  width: 60%;
  height: 40rpx;
  margin-bottom: 20rpx;
}

.skeleton-text {
  width: 100%;
  height: 28rpx;
  margin-bottom: 16rpx;
}

.skeleton-text.short {
  width: 80%;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 200rpx 60rpx;
}

.empty-icon-img {
  width: 120rpx;
  height: 120rpx;
  display: block;
  margin: 0 auto 30rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}

.course-banner {
  width: 100%;
  height: 400rpx;
  background: #f0f0f0;
}

.course-header,
.content-section {
  background: #fff;
  padding: 40rpx 30rpx;
  margin-bottom: 20rpx;
}

.course-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
  line-height: 1.35;
}

.course-desc {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
  display: block;
  margin-bottom: 30rpx;
}

.course-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 40rpx;
  margin-bottom: 30rpx;
}

.stat-item {
  font-size: 26rpx;
  color: #999;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.stat-icon-img {
  width: 26rpx;
  height: 26rpx;
  flex-shrink: 0;
}

.progress-section {
  margin-top: 30rpx;
  padding-top: 30rpx;
  border-top: 1rpx solid #f0f0f0;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.progress-label,
.progress-value {
  font-size: 28rpx;
  font-weight: bold;
}

.progress-label {
  color: #333;
}

.progress-value {
  color: #20C997;
}

.progress-bar {
  height: 12rpx;
  background: #f0f0f0;
  border-radius: 6rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #20C997, #17a589);
  border-radius: 6rpx;
  transition: width 0.3s;
}

.content-section {
  padding-top: 30rpx;
}

.content-item {
  display: flex;
  align-items: center;
  padding: 30rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.content-item:last-child {
  border-bottom: none;
}

.content-item:active {
  background: #fafafa;
}

.content-index {
  width: 60rpx;
  height: 60rpx;
  background: #f5f7fa;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #666;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.content-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.content-title {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 10rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.content-meta {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.content-type {
  font-size: 22rpx;
  color: #2196f3;
  background: #e3f2fd;
  border-radius: 8rpx;
  padding: 4rpx 14rpx;
}

.content-type--video {
  color: #2e7d32;
  background: #e8f5e9;
}

.content-type--link {
  color: #c77800;
  background: #fff4e5;
}

.content-duration {
  font-size: 24rpx;
  color: #999;
}

.content-action {
  width: 72rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-shrink: 0;
}

.play-mark {
  width: 0;
  height: 0;
  border-top: 16rpx solid transparent;
  border-bottom: 16rpx solid transparent;
  border-left: 24rpx solid #20C997;
}

.content-action-text {
  font-size: 24rpx;
  color: #20C997;
}

.empty-content {
  padding: 80rpx 0;
  text-align: center;
}

.video-player-mask {
  position: fixed;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.72);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32rpx;
  box-sizing: border-box;
}

.video-player-panel {
  width: 100%;
  background: #111;
  border-radius: 24rpx;
  overflow: hidden;
}

.video-player-header {
  min-height: 88rpx;
  padding: 0 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
}

.video-player-title {
  flex: 1;
  min-width: 0;
  color: #fff;
  font-size: 28rpx;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.video-player-close {
  width: 64rpx;
  height: 64rpx;
  margin-left: 20rpx;
  color: #fff;
  font-size: 42rpx;
  line-height: 64rpx;
  text-align: center;
  flex-shrink: 0;
}

.course-video {
  width: 100%;
  height: 420rpx;
  background: #000;
  display: block;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.enroll-btn,
.manage-btn {
  width: 100%;
  height: 88rpx;
  background: #20C997;
  color: #fff;
  border-radius: 44rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
}

.enroll-btn.enrolled {
  background: #4dabf7;
  color: #fff;
}

.manage-btn {
  background: #4dabf7;
}
</style>
