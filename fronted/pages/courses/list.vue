<template>
  <view class="list-container">
    <text class="page-title">我的课程</text>
    
    <view class="course-list">
      <view 
        class="course-card" 
        v-for="course in myCourses" 
        :key="course.id"
        @click="goToCourseDetail(course.id)"
      >
        <image 
          class="course-cover" 
          :src="getFullImageUrl(course.cover_url)" 
          mode="aspectFill"
          @error="handleImageError"
        ></image>
        <view class="course-info">
          <text class="course-title">{{ course.title }}</text>
          <text class="course-progress">学习进度: 0%</text>
        </view>
      </view>
    </view>

    <view class="empty-state" v-if="myCourses.length === 0">
      <text class="empty-text">还没有选课哦</text>
      <button class="goto-btn" @click="goToLearn">去选课</button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { request, BASE_URL } from '@/utils/request.js';

const myCourses = ref([]);

const getFullImageUrl = (url) => {
  if (!url) return '/static/course_default.jpg';
  if (url.startsWith('http')) return url;
  return `${BASE_URL}${url}`;
};

const handleImageError = (e) => {
  console.error('Image load error:', e);
  e.target.src = '/static/course_default.jpg';
};

const loadMyCourses = async () => {
  try {
    const res = await request({
      url: '/courses/my/enrollments',
      method: 'GET'
    });
    myCourses.value = res;
  } catch (e) {
    console.error('Failed to load my courses:', e);
  }
};

const goToCourseDetail = (courseId) => {
  uni.navigateTo({
    url: `/pages/courses/detail?id=${courseId}`
  });
};

const goToLearn = () => {
  uni.switchTab({
    url: '/pages/tab/learn'
  });
};

onShow(() => {
  loadMyCourses();
});
</script>

<style lang="scss" scoped>
.list-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 30rpx;
}

.page-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 30rpx;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.course-card {
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
  
  &:active {
    transform: scale(0.98);
  }
}

.course-cover {
  width: 100%;
  height: 300rpx;
  background: #f0f0f0;
}

.course-info {
  padding: 30rpx;
}

.course-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 16rpx;
}

.course-progress {
  font-size: 26rpx;
  color: #20C997;
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
  background: #20C997;
  color: #fff;
  border-radius: 40rpx;
  font-size: 28rpx;
  border: none;
}
</style>
