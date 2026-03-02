<template>
  <view class="detail-container">
    <!-- 加载中骨架屏 -->
    <view class="skeleton-wrapper" v-if="loading">
      <view class="skeleton-banner"></view>
      <view class="skeleton-content">
        <view class="skeleton-title"></view>
        <view class="skeleton-text"></view>
        <view class="skeleton-text short"></view>
        <view class="skeleton-stats">
          <view class="skeleton-stat"></view>
          <view class="skeleton-stat"></view>
        </view>
      </view>
      <view class="skeleton-section">
        <view class="skeleton-section-title"></view>
        <view class="skeleton-item" v-for="i in 3" :key="i"></view>
      </view>
    </view>

    <!-- 课程内容 -->
    <view class="content-wrapper" v-else-if="!loading && course.id">
      <!-- 课程封面 -->
      <view class="banner-wrapper">
        <image 
          class="course-banner" 
          :src="course.cover_url || '/static/course_default.jpg'" 
          mode="aspectFill"
          @error="onImageError"
        ></image>
        <!-- 返回按钮 -->
        <view class="back-btn" @click="goBack">
          <text class="back-icon">‹</text>
        </view>
      </view>

      <!-- 课程基本信息 -->
      <view class="course-header">
        <view class="header-top">
          <text class="course-title">{{ course.title }}</text>
          <view class="course-tag" :class="'tag-' + course.category">
            <text class="tag-text">{{ getCategoryLabel(course.category) }}</text>
          </view>
        </view>

        <view class="course-meta">
          <view class="meta-item">
            <text class="meta-icon">👥</text>
            <text class="meta-text">{{ course.enrollment_count || 0 }}人参与</text>
          </view>
          <view class="meta-item" v-if="course.teacher_name">
            <text class="meta-icon">👨‍🏫</text>
            <text class="meta-text">{{ course.teacher_name }}</text>
          </view>
          <view class="meta-item" v-if="course.created_at">
            <text class="meta-icon">📅</text>
            <text class="meta-text">{{ formatDate(course.created_at) }}</text>
          </view>
        </view>

        <!-- 学习进度（已加入的学生） -->
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

      <!-- 课程简介 -->
      <view class="course-intro">
        <view class="section-title">课程简介</view>
        <text class="intro-text">{{ course.description || '暂无简介' }}</text>
      </view>

      <!-- 课程详细内容（富文本） -->
      <view class="course-detail" v-if="course.content">
        <view class="section-title">课程详情</view>
        <view class="rich-text-wrapper">
          <rich-text :nodes="course.content"></rich-text>
        </view>
      </view>

      <!-- 课程章节列表 -->
      <view class="course-chapters" v-if="course.contents && course.contents.length > 0">
        <view class="section-title">
          <text>课程章节</text>
          <text class="chapter-count">共{{ course.contents.length }}节</text>
        </view>
        <view 
          class="chapter-item" 
          v-for="(content, index) in course.contents" 
          :key="content.id"
          @click="playContent(content)"
        >
          <view class="chapter-left">
            <view class="chapter-index">{{ index + 1 }}</view>
            <view class="chapter-info">
              <text class="chapter-title">{{ content.title }}</text>
              <view class="chapter-meta">
                <text class="chapter-type">{{ getContentTypeLabel(content.content_type) }}</text>
                <text class="chapter-duration" v-if="content.duration">{{ formatDuration(content.duration) }}</text>
              </view>
            </view>
          </view>
          <view class="chapter-right">
            <text class="play-icon">▶</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else-if="!loading && !course.id">
      <text class="empty-icon">📚</text>
      <text class="empty-text">课程不存在或已删除</text>
      <button class="back-home-btn" @click="goBack">返回</button>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar" v-if="!loading && course.id">
      <!-- 学生视图 -->
      <view class="action-wrapper" v-if="userRole === 'student'">
        <button 
          class="action-btn primary" 
          :class="{ enrolled: course.enrolled }"
          @click="handleAction"
          :loading="actionLoading"
        >
          {{ course.enrolled ? '进入学习' : '加入课程' }}
        </button>
      </view>

      <!-- 教师视图（课程创建者） -->
      <view class="action-wrapper teacher" v-else-if="userRole === 'teacher' && course.teacher_id === userId">
        <button class="action-btn secondary" @click="editCourse">
          编辑课程
        </button>
        <button class="action-btn primary" @click="manageContent">
          管理内容
        </button>
      </view>

      <!-- 教师视图（非创建者） -->
      <view class="action-wrapper" v-else-if="userRole === 'teacher'">
        <button class="action-btn disabled" disabled>
          仅供查看
        </button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { request, getCourseDetail, enrollCourse } from '@/utils/request.js';

// 课程分类映射
const categories = {
  'skill': '技能课',
  'theory': '理论课',
  'fitness': '体能课'
};

// 内容类型映射
const contentTypes = {
  'video': '视频',
  'document': '文档',
  'text': '文本'
};

// 数据
const courseId = ref(null);
const course = ref({});
const courseProgress = ref(0);
const loading = ref(true);
const actionLoading = ref(false);
const userRole = ref('student');
const userId = ref(0);

// 获取分类标签
const getCategoryLabel = (category) => {
  return categories[category] || '其他';
};

// 获取内容类型标签
const getContentTypeLabel = (type) => {
  return contentTypes[type] || '内容';
};

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// 格式化时长
const formatDuration = (seconds) => {
  if (!seconds) return '';
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  if (minutes > 0) {
    return `${minutes}分${secs}秒`;
  }
  return `${secs}秒`;
};

// 加载课程详情
const loadCourseDetail = async () => {
  loading.value = true;
  
  try {
    const res = await request({
      url: `/courses/${courseId.value}`,
      method: 'GET'
    });
    
    course.value = res;
    
    // 如果已选课且是学生，加载学习进度
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
      showCancel: false,
      success: () => {
        // 加载失败后返回
        setTimeout(() => {
          uni.navigateBack();
        }, 500);
      }
    });
  } finally {
    loading.value = false;
  }
};

// 加载学习进度
const loadProgress = async () => {
  try {
    const res = await request({
      url: `/courses/me/enrollments/${courseId.value}/progress`,
      method: 'GET'
    });
    courseProgress.value = res.percent || 0;
  } catch (e) {
    console.error('Failed to load progress:', e);
    // 进度加载失败不影响主流程
  }
};

// 处理操作按钮点击
const handleAction = async () => {
  if (course.value.enrolled) {
    // 已加入，进入学习
    enterLearning();
  } else {
    // 未加入，加入课程
    await joinCourse();
  }
};

// 加入课程
const joinCourse = async () => {
  actionLoading.value = true;
  
  try {
    await request({
      url: `/courses/${courseId.value}/enroll`,
      method: 'POST'
    });
    
    uni.showToast({ 
      title: '加入成功', 
      icon: 'success',
      duration: 1500
    });
    
    // 重新加载课程详情以确保状态同步
    await loadCourseDetail();
    
  } catch (e) {
    console.error('Failed to enroll:', e);
    
    let errorMsg = '加入失败';
    if (e.statusCode === 400) {
      errorMsg = '已加入过此课程';
      // 如果已加入，也重新加载一下课程详情
      await loadCourseDetail();
    } else if (e.statusCode === 403) {
      errorMsg = '没有权限加入此课程';
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
    actionLoading.value = false;
  }
};

// 进入学习
const enterLearning = () => {
  if (!course.value.contents || course.value.contents.length === 0) {
    uni.showToast({ 
      title: '暂无课程内容', 
      icon: 'none' 
    });
    return;
  }
  
  // 跳转到第一个章节
  playContent(course.value.contents[0]);
};

// 播放内容
const playContent = (content) => {
  if (!course.value.enrolled && userRole.value === 'student') {
    uni.showModal({
      title: '提示',
      content: '请先加入课程后再学习',
      showCancel: false
    });
    return;
  }
  
  // TODO: 跳转到播放页面
  uni.showToast({ 
    title: '播放功能开发中', 
    icon: 'none' 
  });
  
  // uni.navigateTo({
  //   url: `/pages/courses/player?courseId=${courseId.value}&contentId=${content.id}`
  // });
};

// 编辑课程
const editCourse = () => {
  uni.navigateTo({
    url: `/pages/courses/edit?id=${courseId.value}`
  });
};

// 管理内容
const manageContent = () => {
  uni.showToast({ 
    title: '内容管理功能开发中', 
    icon: 'none' 
  });
  
  // TODO: 跳转到内容管理页面
  // uni.navigateTo({
  //   url: `/pages/courses/manage-content?courseId=${courseId.value}`
  // });
};

// 图片加载失败
const onImageError = () => {
  course.value.cover_url = '/static/course_default.jpg';
};

// 返回
const goBack = () => {
  uni.navigateBack({
    fail: () => {
      // 如果没有上一页，跳转到课程列表
      uni.switchTab({
        url: '/pages/tab/learn'
      });
    }
  });
};

onLoad((options) => {
  if (options.id) {
    courseId.value = options.id;
    
    // 获取用户信息
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
    
    // 加载课程详情
    loadCourseDetail();
  } else {
    uni.showToast({ 
      title: '课程ID不存在', 
      icon: 'none' 
    });
    setTimeout(() => {
      goBack();
    }, 1500);
  }
});
</script>

<style lang="scss" scoped>
.detail-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 140rpx;
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

.skeleton-stats {
  display: flex;
  gap: 20rpx;
  margin-top: 30rpx;
}

.skeleton-stat {
  width: 120rpx;
  height: 32rpx;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 8rpx;
}

.skeleton-section {
  margin-top: 20rpx;
  padding: 30rpx;
  background: #fff;
}

.skeleton-section-title {
  width: 40%;
  height: 36rpx;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 8rpx;
  margin-bottom: 30rpx;
}

.skeleton-item {
  width: 100%;
  height: 80rpx;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 内容样式 */
.content-wrapper {
  background: #f5f7fa;
}

.banner-wrapper {
  position: relative;
  width: 100%;
  height: 400rpx;
}

.course-banner {
  width: 100%;
  height: 100%;
  background: #f0f0f0;
}

.back-btn {
  position: absolute;
  top: calc(var(--status-bar-height) + 20rpx);
  left: 30rpx;
  width: 64rpx;
  height: 64rpx;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.back-icon {
  font-size: 48rpx;
  color: #fff;
  font-weight: bold;
}

.course-header {
  background: #fff;
  padding: 40rpx 30rpx;
  margin-bottom: 20rpx;
}

.header-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.course-title {
  flex: 1;
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  line-height: 1.4;
  margin-right: 20rpx;
}

.course-tag {
  padding: 8rpx 20rpx;
  border-radius: 30rpx;
  flex-shrink: 0;
  
  &.tag-skill {
    background: #e3f2fd;
    color: #1976d2;
  }
  
  &.tag-theory {
    background: #f3e5f5;
    color: #7b1fa2;
  }
  
  &.tag-fitness {
    background: #e8f5e9;
    color: #388e3c;
  }
}

.tag-text {
  font-size: 24rpx;
  font-weight: 500;
}

.course-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 30rpx;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.meta-icon {
  font-size: 28rpx;
}

.meta-text {
  font-size: 26rpx;
  color: #666;
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
  font-weight: 500;
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

.course-intro,
.course-detail,
.course-chapters {
  background: #fff;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chapter-count {
  font-size: 26rpx;
  color: #999;
  font-weight: normal;
}

.intro-text {
  font-size: 28rpx;
  color: #666;
  line-height: 1.8;
  display: block;
}

.rich-text-wrapper {
  font-size: 28rpx;
  color: #333;
  line-height: 1.8;
  
  ::v-deep img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 20rpx 0;
  }
  
  ::v-deep p {
    margin: 16rpx 0;
  }
  
  ::v-deep video {
    width: 100%;
    margin: 20rpx 0;
  }
}

.chapter-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
  
  &:last-child {
    border-bottom: none;
  }
  
  &:active {
    background: #fafafa;
  }
}

.chapter-left {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.chapter-index {
  width: 56rpx;
  height: 56rpx;
  background: linear-gradient(135deg, #20C997, #17a589);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #fff;
  font-weight: bold;
  flex-shrink: 0;
}

.chapter-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.chapter-title {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.chapter-meta {
  display: flex;
  gap: 20rpx;
}

.chapter-type,
.chapter-duration {
  font-size: 24rpx;
  color: #999;
}

.chapter-right {
  flex-shrink: 0;
  margin-left: 20rpx;
}

.play-icon {
  font-size: 32rpx;
  color: #20C997;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 200rpx 60rpx;
}

.empty-icon {
  font-size: 120rpx;
  margin-bottom: 30rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
  margin-bottom: 60rpx;
}

.back-home-btn {
  width: 300rpx;
  height: 80rpx;
  line-height: 80rpx;
  background: #20C997;
  color: #fff;
  border-radius: 40rpx;
  font-size: 28rpx;
  border: none;
}

/* 底部操作栏 */
.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -4rpx 16rpx rgba(0,0,0,0.05);
  z-index: 100;
}

.action-wrapper {
  display: flex;
  gap: 20rpx;
  
  &.teacher {
    .action-btn {
      flex: 1;
    }
  }
}

.action-btn {
  flex: 1;
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 44rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
  
  &.primary {
    background: linear-gradient(90deg, #20C997, #17a589);
    color: #fff;
    
    &.enrolled {
      background: linear-gradient(90deg, #4dabf7, #339af0);
    }
  }
  
  &.secondary {
    background: #f5f7fa;
    color: #333;
  }
  
  &.disabled {
    background: #e9ecef;
    color: #adb5bd;
  }
}
</style>
