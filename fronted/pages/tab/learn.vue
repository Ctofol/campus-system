<template>
  <view class="learn-container">
    <!-- 自定义导航栏 -->
    <view class="custom-nav-bar">
      <view class="nav-status-bar"></view>
      <view class="nav-content">
        <text class="nav-title">体育课程</text>
        <!-- 教师角色显示新增按钮 -->
        <view class="nav-action" v-if="userRole === 'teacher'" @click="createCourse">
          <text class="action-icon">+</text>
        </view>
      </view>
    </view>

    <view class="content-wrapper">
      <!-- 分类筛选 -->
      <scroll-view scroll-x class="category-scroll">
        <view 
          class="category-item" 
          :class="{ active: currentCategory === cat.value }"
          v-for="cat in categories" 
          :key="cat.value"
          @click="selectCategory(cat.value)"
        >
          <text class="category-text">{{ cat.label }}</text>
        </view>
      </scroll-view>

      <!-- 课程列表 -->
      <view class="course-list">
        <view 
          class="course-card" 
          v-for="course in courses" 
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
            <text class="course-desc">{{ course.description }}</text>
            <view class="course-meta">
              <text class="meta-item">📚 {{ course.category_label }}</text>
              <text class="meta-item">👥 {{ course.enrollment_count || 0 }}人</text>
            </view>
            <!-- 学生角色显示选课状态 -->
            <view class="course-status" v-if="userRole === 'student'">
              <view class="status-badge enrolled" v-if="course.enrolled">
                <text>已加入</text>
              </view>
              <view class="status-badge" v-else>
                <text>加入课程</text>
              </view>
            </view>
            <!-- 教师角色显示编辑按钮 -->
            <view class="course-actions" v-if="userRole === 'teacher' && course.teacher_id === userId">
              <view class="action-btn edit" @click.stop="editCourse(course)">
                <text>编辑</text>
              </view>
              <view class="action-btn delete" @click.stop="deleteCourse(course)">
                <text>删除</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-if="courses.length === 0 && !loading">
        <text class="empty-text">暂无课程</text>
        <view class="empty-action" v-if="userRole === 'teacher'" @click="createCourse">
          <text class="action-text">+ 创建第一门课程</text>
        </view>
      </view>

      <!-- 加载中 -->
      <view class="loading-state" v-if="loading">
        <text class="loading-text">加载中...</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onShow, onReachBottom } from '@dcloudio/uni-app';
import { request, BASE_URL } from '@/utils/request.js';

const categories = [
  { label: '全部', value: '' },
  { label: '技能课', value: 'skill' },
  { label: '理论课', value: 'theory' },
  { label: '体能课', value: 'fitness' }
];

const currentCategory = ref('');
const courses = ref([]);
const loading = ref(false);
const page = ref(1);
const hasMore = ref(true);
const userRole = ref('student');
const userId = ref(0);

const getFullImageUrl = (url) => {
  if (!url) return '/static/course_default.jpg';
  if (url.startsWith('http')) return url;
  return `${BASE_URL}${url}`;
};

const handleImageError = (e) => {
  console.error('Image load error:', e);
  e.target.src = '/static/course_default.jpg';
};

const loadCourses = async (reset = false) => {
  if (reset) {
    page.value = 1;
    hasMore.value = true;
    courses.value = [];
  }

  if (!hasMore.value || loading.value) return;

  loading.value = true;
  try {
    const params = {
      page: page.value,
      size: 20
    };
    if (currentCategory.value) {
      params.category = currentCategory.value;
    }

    const res = await request({
      url: '/courses/',
      method: 'GET',
      data: params
    });

    const newCourses = res.items.map(c => ({
      ...c,
      category_label: getCategoryLabel(c.category)
      // 保留后端返回的 enrollment_count 和 enrolled 字段
    }));

    courses.value = [...courses.value, ...newCourses];
    
    if (newCourses.length < 20) {
      hasMore.value = false;
    }
    
    page.value++;
  } catch (e) {
    console.error('Failed to load courses:', e);
    uni.showToast({ title: '加载失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
};

const getCategoryLabel = (category) => {
  const cat = categories.find(c => c.value === category);
  return cat ? cat.label : '其他';
};

const selectCategory = (category) => {
  currentCategory.value = category;
  loadCourses(true);
};

const goToCourseDetail = (courseId) => {
  uni.navigateTo({
    url: `/pages/courses/detail?id=${courseId}`
  });
};

const createCourse = () => {
  uni.navigateTo({
    url: '/pages/courses/create'
  });
};

const editCourse = (course) => {
  uni.navigateTo({
    url: `/pages/courses/edit?id=${course.id}`
  });
};

const deleteCourse = async (course) => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除课程"${course.title}"吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await request({
            url: `/courses/${course.id}`,
            method: 'DELETE'
          });
          uni.showToast({ title: '删除成功', icon: 'success' });
          loadCourses(true);
        } catch (e) {
          console.error('Failed to delete course:', e);
          uni.showToast({ title: '删除失败', icon: 'none' });
        }
      }
    }
  });
};

onShow(() => {
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
  
  loadCourses(true);
});

// 监听课程创建事件
uni.$on('courseCreated', () => {
  loadCourses(true);
});

onReachBottom(() => {
  loadCourses(false);
});
</script>

<style lang="scss" scoped>
.learn-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.custom-nav-bar {
  background-color: #fff;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
  
  .nav-status-bar {
    height: var(--status-bar-height);
  }
  
  .nav-content {
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    
    .nav-title {
      font-size: 18px;
      font-weight: bold;
      color: #333;
    }
    
    .nav-action {
      position: absolute;
      right: 30rpx;
      width: 60rpx;
      height: 60rpx;
      background: #20C997;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      
      .action-icon {
        font-size: 40rpx;
        color: #fff;
        font-weight: bold;
      }
    }
  }
}

.content-wrapper {
  padding-top: calc(var(--status-bar-height) + 44px);
}

.category-scroll {
  white-space: nowrap;
  padding: 20rpx 30rpx;
  background: #fff;
  margin-bottom: 20rpx;
}

.category-item {
  display: inline-block;
  padding: 12rpx 32rpx;
  margin-right: 20rpx;
  background: #f5f7fa;
  border-radius: 40rpx;
  font-size: 28rpx;
  color: #666;
  transition: all 0.3s;
  
  &.active {
    background: #20C997;
    color: #fff;
  }
}

.course-list {
  padding: 0 30rpx;
}

.course-card {
  background: #fff;
  border-radius: 20rpx;
  margin-bottom: 30rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
  
  &:active {
    transform: scale(0.98);
  }
}

.course-cover {
  width: 100%;
  height: 360rpx;
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

.course-desc {
  font-size: 26rpx;
  color: #666;
  display: block;
  margin-bottom: 20rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-meta {
  display: flex;
  gap: 30rpx;
  margin-bottom: 20rpx;
}

.meta-item {
  font-size: 24rpx;
  color: #999;
}

.course-status {
  margin-top: 20rpx;
}

.status-badge {
  display: inline-block;
  padding: 8rpx 24rpx;
  background: #20C997;
  color: #fff;
  border-radius: 30rpx;
  font-size: 24rpx;
  
  &.enrolled {
    background: #adb5bd;
  }
}

.course-actions {
  display: flex;
  gap: 20rpx;
  margin-top: 20rpx;
}

.action-btn {
  flex: 1;
  padding: 16rpx 0;
  text-align: center;
  border-radius: 12rpx;
  font-size: 26rpx;
  
  &.edit {
    background: #20C997;
    color: #fff;
  }
  
  &.delete {
    background: #f5f7fa;
    color: #ff6b6b;
  }
}

.empty-state,
.loading-state {
  padding: 100rpx 0;
  text-align: center;
}

.empty-text,
.loading-text {
  font-size: 28rpx;
  color: #999;
  display: block;
}

.empty-action {
  margin-top: 40rpx;
}

.action-text {
  font-size: 28rpx;
  color: #20C997;
  padding: 20rpx 40rpx;
  border: 2rpx solid #20C997;
  border-radius: 40rpx;
  display: inline-block;
}
</style>
