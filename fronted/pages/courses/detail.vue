<template>
  <view class="detail-container">
    <!-- 加载中骨架屏 -->
    <view class="skeleton-wrapper" v-if="loading">
      <view class="skeleton-banner"></view>
      <view class="skeleton-content">
        <view class="skeleton-title"></view>
        <view class="skeleton-text"></view>
        <view class="skeleton-text short"></view>
      </view>
    </view>

    <!-- 课程内容 -->
    <view v-else-if="!loading && course.id">
      <!-- 课程封面 -->
      <image 
        class="course-banner" 
        :src="getFullImageUrl(course.cover_url)" 
        mode="aspectFill"
        @error="handleImageError(course.cover_url)"
      ></image>

      <!-- 课程信息 -->
      <view class="course-header">
        <text class="course-title">{{ course.title }}</text>
        <text class="course-desc">{{ course.description }}</text>
        <view class="course-stats">
          <view class="stat-item"><image class="stat-icon-img" src="/static/主页跑团图标.png" mode="aspectFit" /><text> {{ course.enrollment_count || 0 }}人已选</text></view>
          <view class="stat-item"><image class="stat-icon-img" src="/static/主页课程图标.png" mode="aspectFit" /><text> {{ course.contents?.length || 0 }}节课</text></view>
        </view>
        <!-- 学习进度 -->
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

      <!-- 课程内容列表 -->
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
            <text class="content-duration">{{ getContentMeta(content) }}</text>
          </view>
          <text class="content-icon">{{ getContentIcon(content) }}</text>
        </view>
        
        <!-- 空状态 -->
        <view class="empty-content" v-if="!course.contents || course.contents.length === 0">
          <text class="empty-text">暂无课程内容</text>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <image class="empty-icon-img" src="/static/主页课程图标.png" mode="aspectFit" />
      <text class="empty-text">课程不存在</text>
    </view>

    <!-- 底部操作栏 -->
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
    course.value = res;
    
    // 如果已选课，加载学习进度
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
    // 已加入，进入学习
    if (!course.value.contents || course.value.contents.length === 0) {
      uni.showToast({ title: '暂无课程内容', icon: 'none' });
      return;
    }
    playContent(course.value.contents[0]);
    return;
  }

  // 未加入，加入课程
  enrolling.value = true;
  
  try {
    await request({
      url: `/courses/${courseId.value}/enroll`,
      method: 'POST'
    });
    
    // 立即更新本地数据
    course.value.enrolled = true;
    course.value.enrollment_count = (course.value.enrollment_count || 0) + 1;
    
    uni.showToast({ 
      title: '加入成功', 
      icon: 'success',
      duration: 1500
    });
    
    // 通知课程列表页刷新数据
    uni.$emit('courseEnrolled');
    
  } catch (e) {
    console.error('Failed to enroll:', e);
    
    let errorMsg = '加入失败';
    if (e.statusCode === 400) {
      errorMsg = '已加入过此课程';
      // 如果已加入，也重新加载一下课程详情
      await loadCourseDetail();
    } else if (e.type === 'network') {
      errorMsg = '网络连接失败';
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

const playContent = (content) => {
  if (!content.content_url) {
    uni.showToast({ title: '暂无内容地址', icon: 'none' });
    return;
  }

  const fullUrl = resolveMediaUrl(content.content_url);
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
    return;
  }

  return;
};

const manageContent = () => {
  uni.navigateTo({
    url: `/pages/courses/content-manage?courseId=${courseId.value}`
  });
};

const getContentMeta = (content) => {
  if (!content) return '--';
  if (content.content_type === 'document') {
    return '文档资料';
  }
  if (content.content_type === 'link') {
    return '外部链接';
  }
  return '课程内容';
};

const getContentIcon = (content) => {
  if (!content) return '▶';
  if (content.content_type === 'document') return '文';
  if (content.content_type === 'link') return '链';
  return '▶';
};

onLoad((options) => {
  if (options.id) {
    courseId.value = options.id;
    
    // 获取用户角色
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
  }
});
</script>

<style lang="scss" scoped>
.detail-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 120rpx;
}

/* 骨架屏样式 */
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

.skeleton-title {
  width: 60%;
  height: 40rpx;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 8rpx;
  margin-bottom: 20rpx;
}

.skeleton-text {
  width: 100%;
  height: 28rpx;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 8rpx;
  margin-bottom: 16rpx;
  
  &.short {
    width: 80%;
  }
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 空状态 */
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

.course-header {
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
  gap: 40rpx;
  margin-bottom: 30rpx;
}

.stat-item {
  font-size: 26rpx;
  color: #999;
  display: flex;
  align-items: center;
  gap: 6rpx;
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

.progress-label {
  font-size: 28rpx;
  color: #333;
  font-weight: bold;
}

.progress-value {
  font-size: 28rpx;
  color: #20C997;
  font-weight: bold;
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
  background: #fff;
  padding: 30rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 30rpx;
}

.content-item {
  display: flex;
  align-items: center;
  padding: 30rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
  
  &:last-child {
    border-bottom: none;
  }
  
  &:active {
    background: #fafafa;
  }
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
}

.content-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-title {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 8rpx;
}

.content-duration {
  font-size: 24rpx;
  color: #999;
}

.content-icon {
  font-size: 32rpx;
}

.empty-content {
  padding: 80rpx 0;
  text-align: center;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 30rpx;
  box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
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
  
  &.enrolled {
    background: #e0e0e0;
    color: #999;
  }
}

.manage-btn {
  background: #4dabf7;
}
</style>
