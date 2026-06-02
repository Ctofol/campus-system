<template>
  <view class="list-page">
    <text class="page-title">我的课程</text>

    <view class="course-list">
      <view
        class="course-card"
        v-for="course in myCourses"
        :key="course.id"
        @click="goToCourseDetail(course.id)"
      >
        <image
          class="course-thumb"
          :src="getFullImageUrl(course.cover_url, course.id)"
          mode="aspectFill"
          @error="handleImageError(course.id)"
        />
        <view class="course-body">
          <text class="course-title">{{ course.title }}</text>
          <view class="course-meta-row">
            <text class="course-meta" v-if="course.duration_minutes > 0">⏱ {{ course.duration_minutes }}分钟</text>
            <text class="course-meta">{{ course.lesson_completed || 0 }}/{{ course.lesson_total || 0 }} 课时</text>
          </view>
          <view class="course-progress-block">
            <view class="progress-head">
              <text class="progress-lesson">学习进度</text>
              <text class="progress-pct">{{ course.progress_percent || 0 }}%</text>
            </view>
            <view class="progress-track">
              <view class="progress-fill" :style="{ width: (course.progress_percent || 0) + '%' }" />
            </view>
          </view>
          <view class="course-action course-action--learn" @click.stop="goToCourseDetail(course.id)">
            <text class="course-action-txt">{{ (course.progress_percent || 0) > 0 ? '继续学习' : '进入学习' }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="empty-state" v-if="myCourses.length === 0 && !loading">
      <text class="empty-text">还没有选课哦</text>
      <button class="goto-btn" @click="goToLearn">去选课</button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { request, resolveMediaUrl } from '@/utils/request.js';

const myCourses = ref([]);
const brokenImages = ref(new Set());
const loading = ref(false);

const getFullImageUrl = (url, id) => {
  if (!url) return '/static/activity-placeholder.png';
  if (brokenImages.value.has(id)) return '/static/activity-placeholder.png';
  if (url.startsWith('http')) return url;
  return resolveMediaUrl(url);
};

const handleImageError = (id) => {
  brokenImages.value.add(id);
};

const loadMyCourses = async () => {
  loading.value = true;
  try {
    const res = await request({ url: '/courses/', method: 'GET', data: { page: 1, size: 100 } });
    myCourses.value = (res.items || []).filter((c) => c.enrolled);
  } catch (e) {
    console.error('Failed to load my courses:', e);
  } finally {
    loading.value = false;
  }
};

const goToCourseDetail = (courseId) => {
  uni.navigateTo({ url: `/pages/courses/detail?id=${courseId}` });
};

const goToLearn = () => {
  uni.switchTab({ url: '/pages/tab/learn' });
};

onShow(() => {
  loadMyCourses();
});
</script>

<style lang="scss" scoped>
.list-page {
  min-height: 100vh;
  background: #f0f4f8;
  padding: 30rpx;
}

.page-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #1a2b3c;
  display: block;
  margin-bottom: 24rpx;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.course-card {
  display: flex;
  flex-direction: row;
  background: #fff;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 8rpx 28rpx rgba(26, 43, 60, 0.06);
}

.course-thumb {
  width: 168rpx;
  height: 168rpx;
  border-radius: 16rpx;
  background: #eef2f5;
  flex-shrink: 0;
}

.course-body {
  flex: 1;
  margin-left: 20rpx;
  min-width: 0;
}

.course-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1a2b3c;
  margin-bottom: 10rpx;
}

.course-meta-row {
  display: flex;
  gap: 16rpx;
  margin-bottom: 12rpx;
}

.course-meta {
  font-size: 22rpx;
  color: #8a9bab;
}

.course-progress-block {
  margin-bottom: 12rpx;
}

.progress-head {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8rpx;
}

.progress-lesson {
  font-size: 22rpx;
  color: #6b7c8f;
}

.progress-pct {
  font-size: 24rpx;
  font-weight: 700;
  color: #20c997;
}

.progress-track {
  height: 12rpx;
  background: #eef2f5;
  border-radius: 6rpx;
  overflow: hidden;
}

.progress-fill {
  height: 12rpx;
  background: linear-gradient(90deg, #2ee6b8, #20c997);
  border-radius: 6rpx;
}

.course-action {
  height: 64rpx;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #20c997;
}

.course-action-txt {
  color: #fff;
  font-size: 26rpx;
  font-weight: 600;
}

.empty-state {
  padding: 100rpx 0;
  text-align: center;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
  display: block;
  margin-bottom: 40rpx;
}

.goto-btn {
  width: 300rpx;
  height: 80rpx;
  background: #20c997;
  color: #fff;
  border-radius: 40rpx;
  font-size: 28rpx;
  border: none;
}
</style>
