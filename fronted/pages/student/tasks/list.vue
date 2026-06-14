<template>
  <view class="container">
    <!-- Tabs -->
    <view class="tabs">
      <view class="tab-item" :class="{ active: currentTab === 0 }" @click="currentTab = 0">进行中</view>
      <view class="tab-item" :class="{ active: currentTab === 1 }" @click="currentTab = 1">已结束</view>
    </view>

    <!-- Task List -->
    <!-- 任务说明弹窗 -->
    <view class="modal-mask" v-if="modalTask" @click="closeModal">
      <view class="modal-card" @click.stop>
        <text class="modal-title">{{ modalTask.title }}</text>
        <text class="modal-line">类型：{{ modalTask.type === 'run' ? '跑步任务' : '体测任务' }}</text>
        <text class="modal-line" v-if="modalTask.starts_at">开始：{{ modalTask.starts_at }}</text>
        <text class="modal-line" v-if="modalTask.deadline">截止：{{ modalTask.deadline }}</text>
        <text class="modal-desc">{{ modalTask.desc }}</text>
        <view class="modal-actions">
          <button class="modal-btn ghost" @click="closeModal">取消</button>
          <button
            v-if="modalTask.type === 'run' && (modalTask.status === 'pending' || modalTask.status === 'failed')"
            class="modal-btn primary"
            @click="startTaskRun(modalTask)"
          >进入任务跑步</button>
          <button
            v-else-if="modalTask.type === 'learn' && (modalTask.status === 'pending' || modalTask.status === 'failed')"
            class="modal-btn primary"
            @click="startTestTask(modalTask)"
          >去体测</button>
        </view>
      </view>
    </view>

    <scroll-view scroll-y class="task-list" @scrolltolower="loadMore">
      <view class="task-card" v-for="item in filteredTasks" :key="item.id" @click="openModal(item)">
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
            <text class="deadline" v-if="item.starts_at">开始: {{ item.starts_at }} · </text>
            <text class="deadline">截止: {{ item.deadline }}</text>
          </view>
        </view>
        
        <view class="card-footer">
            <button class="action-btn" v-if="item.status === 'pending' || item.status === 'failed'" @click.stop="openModal(item)">
              {{ item.status === 'failed' ? '查看/重试' : '去完成' }}
            </button>
            <text v-else-if="item.status === 'not_started'" class="expired-text">未到开始时间</text>
            <view v-else-if="item.status === 'completed'" class="completed-wrap">
              <image class="completed-icon-img" src="/static/勾号图标.png" mode="aspectFit" />
              <text class="completed-text">已完成</text>
            </view>
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
const modalTask = ref(null);
const page = ref(1);
const size = ref(20);
const loading = ref(false);

const buildTaskDesc = (t) => {
  const parts = [];
  if (t.description) parts.push(t.description);
  const isRun = t.type === 'run';
  if (isRun) {
    if (t.min_distance) parts.push(`最低距离 ${t.min_distance} km`);
    if (t.min_duration) parts.push(`最低时长 ${Math.floor(Number(t.min_duration) / 60)} 分`);
  }
  return parts.length ? parts.join('；') : '请查看任务说明';
};

const loadTasks = async () => {
    if (loading.value) return;
    loading.value = true;
    try {
        const res = await getStudentTasks({ page: page.value, size: size.value });
        if (res.items) {
            const newTasks = res.items.map(t => ({
                ...t,
                statusText: t.status === 'completed' ? '已完成' : (t.status === 'expired' ? '已过期' : (t.status === 'failed' ? '未达标' : (t.status === 'not_started' ? '未开始' : '进行中'))),
                desc: buildTaskDesc(t),
                starts_at: t.starts_at ? t.starts_at.split('T')[0] : '',
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
        return tasks.value.filter(t => t.status === 'pending' || t.status === 'failed' || t.status === 'not_started');
    }
    return tasks.value.filter(t => t.status === 'completed' || t.status === 'expired');
});

const getTypeClass = (type) => {
    return type === 'learn' ? 'tag-red' : 'tag-blue';
};

const getStatusClass = (status) => {
    if (status === 'completed') return 'text-green';
    if (status === 'expired') return 'text-gray';
    if (status === 'failed') return 'text-warn';
    if (status === 'not_started') return 'text-muted';
    return 'text-orange';
};

const openModal = (item) => {
  modalTask.value = item;
};

const closeModal = () => {
  modalTask.value = null;
};

/** 任务跑步：统一进「专项测试」中间页（与自由跑、校园打卡区分） */
const startTaskRun = (item) => {
  const km = Number(item.min_distance) || 0;
  const targetMeters = km > 0 ? Math.round(km * 1000) : 2000;
  let pace = 8;
  if (item.min_duration && km > 0) {
    pace = (Number(item.min_duration) / 60) / km;
  }
  const taskDesc = encodeURIComponent(item.description || '');
  const url = `/pages/run/run?mode=police&target=${targetMeters}&pace=${pace.toFixed(2)}&taskId=${item.id}&taskTitle=${encodeURIComponent(item.title)}&taskType=run&taskDescription=${taskDesc}&taskMinDurationSec=${Number(item.min_duration) || 0}&taskMinDistanceKm=${km}`;
  closeModal();
  uni.navigateTo({ url });
};

const startTestTask = (item) => {
  closeModal();
  uni.navigateTo({ url: `/pages/test/test?taskId=${item.id}&taskTitle=${encodeURIComponent(item.title)}` });
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
    .completed-wrap {
        display: flex;
        align-items: center;
        gap: 6rpx;
    }
    .completed-icon-img {
        width: 24rpx;
        height: 24rpx;
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

.text-warn {
  color: #ff9800;
}
.text-muted {
  color: #9e9e9e;
}

.modal-mask {
  position: fixed;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  background: rgba(0,0,0,0.45);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40rpx;
}
.modal-card {
  width: 100%;
  max-width: 600rpx;
  background: #fff;
  border-radius: 20rpx;
  padding: 36rpx;
}
.modal-title {
  font-size: 34rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
}
.modal-line {
  font-size: 26rpx;
  color: #666;
  display: block;
  margin-bottom: 8rpx;
}
.modal-desc {
  font-size: 28rpx;
  color: #444;
  line-height: 1.5;
  margin: 20rpx 0;
  display: block;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 20rpx;
  margin-top: 28rpx;
}
.modal-btn {
  margin: 0;
  font-size: 28rpx;
  padding: 12rpx 32rpx;
  border-radius: 40rpx;
}
.modal-btn.ghost {
  background: #f5f5f5;
  color: #666;
}
.modal-btn.primary {
  background: #20C997;
  color: #fff;
}
</style>
