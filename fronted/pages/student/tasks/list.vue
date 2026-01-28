<template>
  <view class="container">
    <!-- Tabs -->
    <view class="tabs">
      <view class="tab-item" :class="{ active: currentTab === 0 }" @click="currentTab = 0">进行中</view>
      <view class="tab-item" :class="{ active: currentTab === 1 }" @click="currentTab = 1">已结束</view>
    </view>

    <!-- Task List -->
    <scroll-view scroll-y class="task-list" @scrolltolower="loadMore">
      <view class="task-card" v-for="item in filteredTasks" :key="item.id" @click="goToDetail(item)">
        <view class="card-header">
          <view class="title-row">
            <text class="tag" :class="getTypeClass(item.type)">{{ item.type === 'run' ? '跑步' : '体测' }}</text>
            <text class="title">{{ item.title }}</text>
          </view>
          <text class="status" :class="getStatusClass(item.status)">{{ item.statusText }}</text>
        </view>
        
        <view class="card-body">
          <text class="desc">{{ item.desc }}</text>
          <view class="meta-row">
            <text class="deadline">截止: {{ item.deadline }}</text>
          </view>
        </view>
        
        <view class="card-footer">
            <button class="action-btn" v-if="item.status === 'pending'" @click.stop="doTask(item)">去完成</button>
            <text v-else-if="item.status === 'completed'" class="completed-text">✅ 已完成</text>
            <text v-else class="expired-text">已过期</text>
        </view>
      </view>
      <view class="loading-more" v-if="loading">加载中...</view>
      <view class="no-more" v-if="!loading && filteredTasks.length === 0">暂无任务</view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { getStudentTasks } from '@/utils/request.js';

const currentTab = ref(0);
const tasks = ref([]);
const page = ref(1);
const size = ref(20);
const loading = ref(false);

const loadTasks = async () => {
    if (loading.value) return;
    loading.value = true;
    try {
        const res = await getStudentTasks({ page: page.value, size: size.value });
        if (res.items) {
            const newTasks = res.items.map(t => ({
                ...t,
                statusText: t.status === 'completed' ? '已完成' : (t.status === 'expired' ? '已过期' : '进行中'),
                desc: t.description || (t.min_distance ? `目标: ${t.min_distance}km` : '无具体描述'),
                deadline: t.deadline ? t.deadline.split('T')[0] : '无限制'
            }));
            if (page.value === 1) tasks.value = newTasks;
            else tasks.value = [...tasks.value, ...newTasks];
        }
    } catch (e) {
        console.error(e);
        uni.showToast({ title: '加载任务失败', icon: 'none' });
    } finally {
        loading.value = false;
    }
};

const loadMore = () => {
    // page.value++;
    // loadTasks();
};

onShow(() => {
    page.value = 1;
    loadTasks();
});

const filteredTasks = computed(() => {
    if (currentTab.value === 0) {
        return tasks.value.filter(t => t.status === 'pending');
    } else {
        return tasks.value.filter(t => t.status !== 'pending');
    }
});

const getTypeClass = (type) => {
    return type === 'test' ? 'tag-red' : 'tag-blue';
};

const getStatusClass = (status) => {
    if (status === 'completed') return 'text-green';
    if (status === 'expired') return 'text-gray';
    return 'text-orange';
};

const doTask = (item) => {
    if (item.type === 'run') {
        uni.navigateTo({ url: '/pages/run/run' });
    } else {
        uni.navigateTo({ url: '/pages/test/test' });
    }
};

const goToDetail = (item) => {
    // Future: Detail page
};
</script>

<style lang="scss">
.container {
  padding: 20rpx;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.tabs {
  display: flex;
  background: #fff;
  padding: 20rpx;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
  .tab-item {
    flex: 1;
    text-align: center;
    font-size: 28rpx;
    color: #666;
    padding-bottom: 10rpx;
    &.active {
      color: #20C997;
      border-bottom: 4rpx solid #20C997;
      font-weight: bold;
    }
  }
}
.task-list {
    height: calc(100vh - 120rpx);
}
.task-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  .card-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20rpx;
    .title-row {
        display: flex;
        align-items: center;
        .tag {
            font-size: 20rpx;
            padding: 4rpx 12rpx;
            border-radius: 8rpx;
            margin-right: 16rpx;
            &.tag-red { background: #ffebee; color: #f44336; }
            &.tag-blue { background: #e3f2fd; color: #2196f3; }
        }
        .title { font-size: 32rpx; font-weight: bold; }
    }
    .status { font-size: 24rpx; }
    .text-green { color: #4caf50; }
    .text-gray { color: #9e9e9e; }
    .text-orange { color: #ff9800; }
  }
  .card-body {
    margin-bottom: 20rpx;
    .desc { font-size: 28rpx; color: #666; display: block; margin-bottom: 10rpx; }
    .meta-row { font-size: 24rpx; color: #999; }
  }
  .card-footer {
    border-top: 1rpx solid #eee;
    padding-top: 20rpx;
    display: flex;
    justify-content: flex-end;
    .action-btn {
        background: #20C997;
        color: #fff;
        font-size: 24rpx;
        padding: 10rpx 30rpx;
        border-radius: 30rpx;
        margin: 0;
    }
    .completed-text {
        color: #4caf50;
        font-size: 24rpx;
    }
    .expired-text {
        color: #999;
        font-size: 24rpx;
    }
  }
}
.no-more {
    text-align: center;
    color: #999;
    padding: 40rpx;
}
</style>