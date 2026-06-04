<template>
  <view class="learn-page">
    <page-tab-header title="课程学习" theme="brand" :fixed="false">
      <template #right>
        <view
          v-if="userRole === 'teacher'"
          class="page-tab-header-icon-action"
          @click="createCourse"
        >
          <text class="action-icon">+</text>
        </view>
      </template>
    </page-tab-header>

    <view class="learn-hero">
      <view class="learn-search-row">
        <view class="learn-search">
          <text class="learn-search-icon">⌕</text>
          <input
            class="learn-search-input"
            v-model="searchKeyword"
            placeholder="搜索课程..."
            placeholder-class="learn-search-ph"
            confirm-type="search"
          />
        </view>
      </view>

      <view class="learn-stats" v-if="userRole === 'student'">
        <view class="learn-stat-card">
          <text class="learn-stat-num">{{ stats.inProgress }}</text>
          <text class="learn-stat-lbl">进行中</text>
        </view>
        <view class="learn-stat-card">
          <text class="learn-stat-num">{{ stats.completed }}</text>
          <text class="learn-stat-lbl">已完成</text>
        </view>
        <view class="learn-stat-card">
          <text class="learn-stat-num">{{ stats.learningMinutes }}</text>
          <text class="learn-stat-lbl">学习分钟</text>
        </view>
      </view>
    </view>

    <scroll-view scroll-x class="category-scroll" :show-scrollbar="false">
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

    <view class="course-list">
      <view
        class="course-card"
        v-for="course in displayCourses"
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
          <view
            v-if="course.teacher_name || course.duration_minutes > 0 || course.category_label"
            class="course-meta-row"
          >
            <text v-if="course.teacher_name" class="course-meta">👤 {{ course.teacher_name }}</text>
            <text v-if="course.duration_minutes > 0" class="course-meta">⏱ {{ course.duration_minutes }}分钟</text>
            <text v-if="course.category_label" class="course-meta">📚 {{ course.category_label }}</text>
          </view>
          <view v-if="course.enrollment_count > 0" class="course-meta-row">
            <text class="course-meta">👥 {{ course.enrollment_count }}人在学</text>
          </view>

          <view v-if="course.enrolled && userRole === 'student'" class="course-progress-block">
            <view class="progress-head">
              <text class="progress-lesson">{{ course.lesson_completed || 0 }}/{{ course.lesson_total || 0 }} 课时</text>
              <text class="progress-pct">{{ course.progress_percent || 0 }}%</text>
            </view>
            <view class="progress-track">
              <view
                class="progress-fill"
                :style="{ width: (course.progress_percent || 0) + '%' }"
              />
            </view>
          </view>

          <view
            v-if="userRole === 'student'"
            class="course-action"
            :class="actionBtnClass(course)"
            @click.stop="onCourseAction(course)"
          >
            <text class="course-action-txt">{{ getActionLabel(course) }}</text>
          </view>

          <view class="course-actions" v-if="userRole === 'teacher' && course.teacher_id === userId">
            <view class="action-btn content" @click.stop="manageCourseContent(course)">
              <text>内容</text>
            </view>
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

    <view class="empty-state" v-if="displayCourses.length === 0 && !loading">
      <text class="empty-text">{{ searchKeyword ? '未找到相关课程' : '暂无课程' }}</text>
      <view class="empty-action" v-if="userRole === 'teacher' && !searchKeyword" @click="createCourse">
        <text class="action-text">+ 创建第一门课程</text>
      </view>
    </view>

    <view class="loading-state" v-if="loading">
      <text class="loading-text">加载中...</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onShow, onReachBottom, onHide } from '@dcloudio/uni-app';
import { request, resolveMediaUrl } from '@/utils/request.js';

const categories = [
  { label: '全部', value: '' },
  { label: '技能课', value: 'skill' },
  { label: '理论课', value: 'theory' },
  { label: '体能课', value: 'fitness' }
];

const currentCategory = ref('');
const searchKeyword = ref('');
const courses = ref([]);
const loading = ref(false);
const page = ref(1);
const hasMore = ref(true);
const userRole = ref('student');
const userId = ref(0);
const brokenImages = ref(new Set());
const enrollingId = ref(null);

const getFullImageUrl = (url, id) => {
  if (!url) return '/static/activity-placeholder.png';
  if (brokenImages.value.has(id)) return '/static/activity-placeholder.png';
  if (url.startsWith('http') || url.startsWith('blob:') || url.startsWith('wxfile:')) return url;
  return resolveMediaUrl(url);
};

const handleImageError = (id) => {
  brokenImages.value.add(id);
};

const getCategoryLabel = (category) => {
  const cat = categories.find((c) => c.value === category);
  return cat ? cat.label : '其他';
};

const displayCourses = computed(() => {
  const kw = (searchKeyword.value || '').trim().toLowerCase();
  if (!kw) return courses.value;
  return courses.value.filter((c) => {
    const title = (c.title || '').toLowerCase();
    const desc = (c.description || '').toLowerCase();
    const teacher = (c.teacher_name || '').toLowerCase();
    return title.includes(kw) || desc.includes(kw) || teacher.includes(kw);
  });
});

const stats = computed(() => {
  const enrolled = courses.value.filter((c) => c.enrolled);
  const inProgress = enrolled.filter(
    (c) => (c.progress_percent || 0) > 0 && (c.progress_percent || 0) < 100
  ).length;
  const completed = enrolled.filter((c) => (c.progress_percent || 0) >= 100).length;
  const learningMinutes = enrolled.reduce((sum, c) => {
    const mins = c.duration_minutes || 0;
    const pct = (c.progress_percent || 0) / 100;
    return sum + Math.round(mins * pct);
  }, 0);
  return { inProgress, completed, learningMinutes };
});

const getActionLabel = (course) => {
  if (!course.enrolled) return '加入课程';
  if ((course.progress_percent || 0) > 0) return '继续学习';
  return '进入学习';
};

const actionBtnClass = (course) => {
  if (!course.enrolled) return 'course-action--join';
  if ((course.progress_percent || 0) >= 100) return 'course-action--done';
  return 'course-action--learn';
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
    const params = { page: page.value, size: 20 };
    if (currentCategory.value) params.category = currentCategory.value;

    const res = await request({
      url: '/courses/',
      method: 'GET',
      data: params
    });

    const newCourses = (res.items || []).map((c) => ({
      ...c,
      category_label: getCategoryLabel(c.category),
      progress_percent: c.progress_percent ?? 0,
      lesson_total: c.lesson_total ?? 0,
      lesson_completed: c.lesson_completed ?? 0,
      duration_minutes: c.duration_minutes ?? 0,
      teacher_name: c.teacher_name ? String(c.teacher_name).trim() : ''
    }));

    courses.value = reset ? newCourses : [...courses.value, ...newCourses];
    if (newCourses.length < 20) hasMore.value = false;
    page.value += 1;
  } catch (e) {
    console.error('Failed to load courses:', e);
    uni.showToast({ title: '加载失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
};

const selectCategory = (category) => {
  currentCategory.value = category;
  loadCourses(true);
};

const goToCourseDetail = (courseId) => {
  uni.navigateTo({ url: `/pages/courses/detail?id=${courseId}` });
};

const onCourseAction = async (course) => {
  if (userRole.value !== 'student') return;
  if (course.enrolled) {
    goToCourseDetail(course.id);
    return;
  }
  if (enrollingId.value === course.id) return;
  enrollingId.value = course.id;
  try {
    await request({
      url: `/courses/${course.id}/enroll`,
      method: 'POST'
    });
    uni.showToast({ title: '加入成功', icon: 'success' });
    uni.$emit('courseEnrolled');
    await loadCourses(true);
  } catch (e) {
    console.error('Failed to enroll:', e);
    const msg = e?.statusCode === 400 ? '已加入过此课程' : '加入失败';
    uni.showToast({ title: msg, icon: 'none' });
    if (e?.statusCode === 400) loadCourses(true);
  } finally {
    enrollingId.value = null;
  }
};

const createCourse = () => {
  uni.navigateTo({ url: '/pages/courses/create' });
};

const editCourse = (course) => {
  uni.navigateTo({ url: `/pages/courses/edit?id=${course.id}` });
};

const manageCourseContent = (course) => {
  uni.navigateTo({ url: `/pages/courses/content-manage?courseId=${course.id}` });
};

const deleteCourse = async (course) => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除课程「${course.title}」吗？`,
    success: async (res) => {
      if (!res.confirm) return;
      try {
        await request({ url: `/courses/${course.id}`, method: 'DELETE' });
        uni.showToast({ title: '删除成功', icon: 'success' });
        loadCourses(true);
      } catch (e) {
        uni.showToast({ title: '删除失败', icon: 'none' });
      }
    }
  });
};

onShow(() => {
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

uni.$on('courseCreated', () => loadCourses(true));
uni.$on('courseEnrolled', () => loadCourses(true));

onHide(() => {
  uni.$off('courseCreated');
  uni.$off('courseEnrolled');
});

onReachBottom(() => loadCourses(false));
</script>

<style lang="scss" scoped>
.learn-page {
  min-height: 100vh;
  background: #f0f4f8;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
}

.learn-hero {
  margin: 0 24rpx 20rpx;
  padding: 24rpx 24rpx 20rpx;
  border-radius: 24rpx;
  background: linear-gradient(145deg, #2ee6b8 0%, #20c997 45%, #17b88a 100%);
  box-shadow: 0 12rpx 32rpx rgba(32, 201, 151, 0.28);
}

.learn-search-row {
  margin-bottom: 20rpx;
}

.learn-search {
  display: flex;
  flex-direction: row;
  align-items: center;
  background: #fff;
  border-radius: 40rpx;
  padding: 0 24rpx;
  height: 72rpx;
}

.learn-search-icon {
  font-size: 32rpx;
  color: #20c997;
  margin-right: 12rpx;
}

.learn-search-input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
  height: 72rpx;
}

.learn-search-ph {
  color: #aaa;
}

.learn-stats {
  display: flex;
  flex-direction: row;
  gap: 16rpx;
}

.learn-stat-card {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16rpx;
  padding: 16rpx 8rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.learn-stat-num {
  font-size: 36rpx;
  font-weight: 700;
  color: #1a2b3c;
  line-height: 1.1;
}

.learn-stat-lbl {
  font-size: 22rpx;
  color: #6b7c8f;
  margin-top: 6rpx;
}

.category-scroll {
  white-space: nowrap;
  padding: 0 24rpx 20rpx;
}

.category-item {
  display: inline-block;
  padding: 14rpx 32rpx;
  margin-right: 16rpx;
  background: #fff;
  border-radius: 40rpx;
  border: 2rpx solid #e8ecef;
  transition: all 0.2s;

  &.active {
    background: #20c997;
    border-color: #20c997;

    .category-text {
      color: #fff;
      font-weight: 600;
    }
  }
}

.category-text {
  font-size: 26rpx;
  color: #666;
}

.course-list {
  padding: 0 24rpx;
}

.course-card {
  display: flex;
  flex-direction: row;
  background: #fff;
  border-radius: 24rpx;
  margin-bottom: 24rpx;
  padding: 24rpx;
  box-shadow: 0 8rpx 28rpx rgba(26, 43, 60, 0.06);

  &:active {
    transform: scale(0.99);
  }
}

.course-thumb {
  width: 168rpx;
  height: 168rpx;
  border-radius: 16rpx;
  flex-shrink: 0;
  background: #eef2f5;
}

.course-body {
  flex: 1;
  min-width: 0;
  margin-left: 20rpx;
  display: flex;
  flex-direction: column;
}

.course-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1a2b3c;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-meta-row {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-top: 10rpx;
}

.course-meta {
  font-size: 22rpx;
  color: #8a9bab;
}

.course-progress-block {
  margin-top: 16rpx;
}

.progress-head {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
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
  transition: width 0.3s ease;
}

.course-action {
  margin-top: 16rpx;
  height: 64rpx;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.course-action--join {
  background: #20c997;
  box-shadow: 0 6rpx 16rpx rgba(32, 201, 151, 0.3);
}

.course-action--learn {
  background: #20c997;
  box-shadow: 0 6rpx 16rpx rgba(32, 201, 151, 0.3);
}

.course-action--done {
  background: rgba(32, 201, 151, 0.12);
  border: 2rpx solid #20c997;
}

.course-action-txt {
  font-size: 26rpx;
  font-weight: 600;
  color: #fff;
}

.course-action--done .course-action-txt {
  color: #20c997;
}

.course-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 16rpx;
}

.action-btn {
  flex: 1;
  padding: 14rpx 0;
  text-align: center;
  border-radius: 12rpx;
  font-size: 24rpx;

  &.content {
    background: #e8f8f3;
    color: #20c997;
  }

  &.edit {
    background: #20c997;
    color: #fff;
  }

  &.delete {
    background: #f5f7fa;
    color: #ff6b6b;
  }
}

.empty-state,
.loading-state {
  padding: 80rpx 0;
  text-align: center;
}

.empty-text,
.loading-text {
  font-size: 28rpx;
  color: #999;
}

.empty-action {
  margin-top: 32rpx;
}

.action-text {
  font-size: 28rpx;
  color: #20c997;
  padding: 18rpx 40rpx;
  border: 2rpx solid #20c997;
  border-radius: 40rpx;
  display: inline-block;
}
</style>
