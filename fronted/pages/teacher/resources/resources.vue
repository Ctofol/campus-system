<template>
  <view class="resources-container">
    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="nav-back" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="nav-title">教学资源</text>
      <view class="nav-action" @click="createResource">
        <text class="action-icon">+</text>
      </view>
    </view>

    <!-- 分类标签 -->
    <view class="category-tabs">
      <view 
        class="tab-item" 
        :class="{ active: activeCategory === 'all' }"
        @click="switchCategory('all')"
      >
        全部
      </view>
      <view 
        class="tab-item" 
        :class="{ active: activeCategory === 'theory' }"
        @click="switchCategory('theory')"
      >
        理论课
      </view>
      <view 
        class="tab-item" 
        :class="{ active: activeCategory === 'skill' }"
        @click="switchCategory('skill')"
      >
        技能课
      </view>
      <view 
        class="tab-item" 
        :class="{ active: activeCategory === 'fitness' }"
        @click="switchCategory('fitness')"
      >
        体能课
      </view>
    </view>

    <!-- 资源列表 -->
    <view class="resource-list">
      <view 
        class="resource-card" 
        v-for="resource in filteredResources" 
        :key="resource.id"
      >
        <image 
          class="resource-cover" 
          :src="getFullImageUrl(resource.cover_url)" 
          mode="aspectFill"
          @error="handleImageError"
        ></image>
        <view class="resource-info">
          <text class="resource-title">{{ resource.title }}</text>
          <text class="resource-desc">{{ resource.description || '暂无简介' }}</text>
          <view class="resource-meta">
            <text class="meta-tag">{{ getCategoryName(resource.category) }}</text>
            <text class="meta-status" :class="{ published: resource.is_public }">
              {{ resource.is_public ? '已发布' : '未发布' }}
            </text>
          </view>
        </view>
        <view class="resource-actions">
          <button class="action-btn edit" @click.stop="editResource(resource)">编辑</button>
          <button class="action-btn manage" @click.stop="manageContent(resource)">内容</button>
          <button 
            class="action-btn publish" 
            @click.stop="togglePublish(resource)"
          >
            {{ resource.is_public ? '取消发布' : '发布' }}
          </button>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-if="filteredResources.length === 0 && !loading">
      <text class="empty-icon">📚</text>
      <text class="empty-text">还没有教学资源</text>
      <button class="create-btn" @click="createResource">创建资源</button>
    </view>

    <!-- 加载中 -->
    <view class="loading" v-if="loading">
      <text>加载中...</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onLoad, onShow } from '@dcloudio/uni-app';
import { request, BASE_URL } from '@/utils/request.js';

const activeCategory = ref('all');
const resources = ref([]);
const loading = ref(false);
const userId = ref(0);
const userRole = ref('');

const filteredResources = computed(() => {
  if (activeCategory.value === 'all') {
    return resources.value;
  }
  return resources.value.filter(r => r.category === activeCategory.value);
});

const loadResources = async () => {
  loading.value = true;
  try {
    const params = {
      page: 1,
      size: 100
    };
    
    // 如果是教师端，建议传入老师ID以优先展示自己的课程
    // 如果后端支持根据角色返回数据也可以不用传
    if (userRole.value === 'teacher' && userId.value) {
      params.teacher_id = userId.value;
    }

    const res = await request({
      url: '/courses/',
      method: 'GET',
      data: params
    });
    resources.value = res.items || [];
  } catch (e) {
    console.error('Failed to load resources:', e);
    uni.showToast({
      title: '加载失败',
      icon: 'none'
    });
  } finally {
    loading.value = false;
  }
};

const switchCategory = (category) => {
  activeCategory.value = category;
};

const getCategoryName = (category) => {
  const map = {
    theory: '理论课',
    skill: '技能课',
    fitness: '体能课'
  };
  return map[category] || '未分类';
};

const getFullImageUrl = (url) => {
  if (!url) return '/static/activity-placeholder.png';
  if (url.startsWith('http')) return url;
  return `${BASE_URL}${url}`;
};

const handleImageError = (e) => {
  if (e.target.src.indexOf('activity-placeholder.png') === -1) {
    e.target.src = '/static/activity-placeholder.png';
  }
};

const createResource = () => {
  uni.navigateTo({
    url: '/pages/courses/create'
  });
};

const editResource = (resource) => {
  uni.navigateTo({
    url: `/pages/courses/edit?id=${resource.id}`
  });
};

const manageContent = (resource) => {
  uni.navigateTo({
    url: `/pages/courses/content-manage?courseId=${resource.id}`
  });
};

const togglePublish = async (resource) => {
  try {
    await request({
      url: `/courses/${resource.id}`,
      method: 'PUT',
      data: {
        title: resource.title,
        description: resource.description,
        cover_url: resource.cover_url,
        category: resource.category,
        is_public: !resource.is_public
      }
    });
    
    uni.showToast({
      title: resource.is_public ? '已取消发布' : '发布成功',
      icon: 'success'
    });
    
    // 刷新列表
    loadResources();
  } catch (e) {
    console.error('Failed to toggle publish:', e);
    uni.showToast({
      title: '操作失败',
      icon: 'none'
    });
  }
};

const goBack = () => {
  uni.navigateBack();
};

onShow(() => {
  // 获取当前用户信息
  userRole.value = uni.getStorageSync('userRole') || '';
  const userInfo = uni.getStorageSync('userInfo');
  if (userInfo) {
    try {
      const info = typeof userInfo === 'string' ? JSON.parse(userInfo) : userInfo;
      userId.value = info.userId || info.id || 0;
    } catch (e) {
      console.error('Parse userInfo error:', e);
    }
  }
  
  loadResources();
});

// 监听课程创建/编辑事件
uni.$on('courseCreated', () => {
  loadResources();
});
</script>

<style lang="scss" scoped>
.resources-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 40rpx;
}

.nav-bar {
  background: #fff;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30rpx;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}

.nav-back, .nav-action {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  font-size: 40rpx;
  color: #333;
}

.nav-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.action-icon {
  font-size: 48rpx;
  color: #20C997;
}

.category-tabs {
  display: flex;
  background: #fff;
  padding: 20rpx 30rpx;
  gap: 20rpx;
  overflow-x: auto;
}

.tab-item {
  padding: 16rpx 32rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  color: #666;
  background: #f5f7fa;
  white-space: nowrap;
  
  &.active {
    background: #20C997;
    color: #fff;
  }
}

.resource-list {
  padding: 30rpx;
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.resource-card {
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}

.resource-cover {
  width: 100%;
  height: 300rpx;
  background: #f0f0f0;
}

.resource-info {
  padding: 30rpx;
}

.resource-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 16rpx;
}

.resource-desc {
  font-size: 26rpx;
  color: #666;
  line-height: 1.6;
  display: block;
  margin-bottom: 20rpx;
}

.resource-meta {
  display: flex;
  gap: 20rpx;
  align-items: center;
}

.meta-tag {
  padding: 8rpx 20rpx;
  background: #e3f2fd;
  color: #2196f3;
  font-size: 24rpx;
  border-radius: 8rpx;
}

.meta-status {
  padding: 8rpx 20rpx;
  background: #f5f5f5;
  color: #999;
  font-size: 24rpx;
  border-radius: 8rpx;
  
  &.published {
    background: #e8f5e9;
    color: #4caf50;
  }
}

.resource-actions {
  display: flex;
  border-top: 1rpx solid #f0f0f0;
}

.action-btn {
  flex: 1;
  height: 88rpx;
  font-size: 28rpx;
  border: none;
  background: #fff;
  border-right: 1rpx solid #f0f0f0;
  
  &:last-child {
    border-right: none;
  }
  
  &.edit {
    color: #666;
  }
  
  &.manage {
    color: #2196f3;
  }
  
  &.publish {
    color: #20C997;
  }
}

.empty-state {
  padding: 200rpx 60rpx;
  text-align: center;
}

.empty-icon {
  font-size: 120rpx;
  display: block;
  margin-bottom: 30rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
  display: block;
  margin-bottom: 40rpx;
}

.create-btn {
  width: 300rpx;
  height: 80rpx;
  background: #20C997;
  color: #fff;
  border-radius: 40rpx;
  font-size: 28rpx;
  border: none;
}

.loading {
  padding: 100rpx 0;
  text-align: center;
  color: #999;
}
</style>
