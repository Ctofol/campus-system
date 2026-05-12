<template>
  <view class="page">
    <view class="item" v-for="row in items" :key="row.activity_id">
      <view class="row-top">
        <text class="title">{{ row.task_title || '任务' }}</text>
        <text class="tag" :class="row.completed_ok ? 'ok' : 'bad'">
          {{ row.completed_ok ? '已达标' : '未达标' }}
        </text>
      </view>
      <text class="time">{{ formatTime(row.started_at) }}</text>
      <text class="meta" v-if="row.task_type === 'run'">
        距离 {{ row.distance_km != null ? Number(row.distance_km).toFixed(2) : '--' }} km
        · 时长 {{ row.duration_sec != null ? Math.floor(row.duration_sec / 60) : '--' }} 分
        <text v-if="row.pace"> · 配速 {{ row.pace }}</text>
      </text>
      <text class="fail" v-if="!row.completed_ok && row.fail_reason">{{ row.fail_reason }}</text>
    </view>
    <view v-if="!loading && items.length === 0" class="empty">暂无任务跑步记录</view>
    <view v-if="loading" class="empty">加载中...</view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { getStudentTaskRunHistory } from '@/utils/request.js';

const items = ref([]);
const loading = ref(false);

const formatTime = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
};

const load = async () => {
  loading.value = true;
  try {
    const res = await getStudentTaskRunHistory({ page: 1, size: 50 });
    items.value = res.items || [];
  } catch (e) {
    console.error(e);
    uni.showToast({ title: '加载失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
};

onShow(() => {
  load();
});
</script>

<style lang="scss">
.page {
  padding: 20rpx;
  background: #f5f7fa;
  min-height: 100vh;
}
.item {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
}
.row-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}
.title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  flex: 1;
  padding-right: 16rpx;
}
.tag {
  font-size: 24rpx;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}
.tag.ok {
  background: #e6fff6;
  color: #20c997;
}
.tag.bad {
  background: #fff1f0;
  color: #ff4d4f;
}
.time {
  font-size: 24rpx;
  color: #999;
  display: block;
  margin-bottom: 8rpx;
}
.meta {
  font-size: 26rpx;
  color: #666;
}
.fail {
  font-size: 24rpx;
  color: #ff4d4f;
  margin-top: 10rpx;
  display: block;
}
.empty {
  text-align: center;
  color: #999;
  padding: 80rpx 20rpx;
}
</style>
