<template>
  <view class="page">
    <page-tab-header title="消息通知" show-back theme="white">
      <template #right><text class="header-action" @tap="goSend">发送</text></template>
    </page-tab-header>
    <view class="body page-tab-body">
      <scroll-view scroll-x class="filters"><view class="filter-row">
        <view v-for="item in filterTabs" :key="item.key" class="chip" :class="{ active: filter === item.key }" @tap="filter = item.key">{{ item.label }}</view>
      </view></scroll-view>
      <view class="toolbar"><text>共 {{ filtered.length }} 条</text><text class="read-all" @tap="markAllRead">全部已读</text></view>
      <view v-for="item in filtered" :key="item.id" class="notice" :class="{ unread: !item.is_read }" @tap="openDetail(item)">
        <view class="notice-head"><text class="title">{{ item.title }}</text><text class="time">{{ formatTime(item.created_at) }}</text></view>
        <text class="body-text">{{ item.body || '暂无正文' }}</text>
        <view class="notice-foot"><text class="tag">{{ typeLabel(item.ntype) }}</text><view v-if="!item.is_read" class="dot" /></view>
      </view>
      <view v-if="!loading && !filtered.length" class="empty"><text class="empty-title">暂无通知</text><text class="empty-tip">学生留言、任务与系统消息会显示在这里</text></view>
      <view v-if="loading" class="loading">加载中...</view>
      <button v-if="hasMore && !loading" class="more" @tap="loadMore">加载更多</button>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { request } from '@/utils/request.js';

const notifications = ref([]);
const loading = ref(false);
const page = ref(1);
const hasMore = ref(true);
const filter = ref('all');
const filterTabs = [
  { key: 'all', label: '全部' }, { key: 'student', label: '学生消息' },
  { key: 'task', label: '任务' }, { key: 'run', label: '跑团' }, { key: 'system', label: '系统' },
];
const category = type => {
  if (type === 'student_message') return 'student';
  if (['task', 'task_reminder', 'score'].includes(type)) return 'task';
  if (['run_group', 'run_group_activity', 'run_group_apply'].includes(type)) return 'run';
  return 'system';
};
const filtered = computed(() => filter.value === 'all' ? notifications.value : notifications.value.filter(item => category(item.ntype) === filter.value));
const typeLabel = type => ({ student_message: '学生消息', teacher_message: '教师消息', task: '任务通知', task_reminder: '任务提醒', run_group: '跑团', run_group_activity: '跑团活动', run_group_apply: '报名提醒', health_review: '健康审批', score: '成绩', system: '系统公告' }[type] || '通知');
const formatTime = value => value ? new Date(value).toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-') : '';
const load = async (reset = true) => {
  if (loading.value) return;
  loading.value = true;
  if (reset) { page.value = 1; hasMore.value = true; }
  try {
    const rows = await request({ url: `/notifications?page=${page.value}&limit=30`, method: 'GET' });
    const list = Array.isArray(rows) ? rows : rows?.items || [];
    notifications.value = reset ? list : [...notifications.value, ...list];
    hasMore.value = list.length === 30;
  } catch (e) { uni.showToast({ title: e?.message || '通知加载失败', icon: 'none' }); }
  finally { loading.value = false; }
};
const loadMore = () => { if (hasMore.value) { page.value += 1; load(false); } };
const openDetail = async item => {
  if (!item.is_read) {
    item.is_read = true;
    try { await request({ url: `/notifications/${item.id}/read`, method: 'PUT' }); } catch (e) {}
    uni.$emit('notifications:changed');
  }
  uni.navigateTo({ url: `/pages/notifications/detail?id=${item.id}` });
};
const markAllRead = async () => {
  try {
    await request({ url: '/notifications/read-all', method: 'PUT' });
    notifications.value.forEach(item => { item.is_read = true; });
    uni.$emit('notifications:changed');
    uni.showToast({ title: '已全部标记为已读', icon: 'success' });
  } catch (e) { uni.showToast({ title: '操作失败', icon: 'none' }); }
};
const goSend = () => uni.navigateTo({ url: '/pages/teacher/notifications/send' });
onShow(() => load(true));
</script>

<style scoped>
.page { min-height: 100vh; background: #f5f7fa; }
.body { padding: 20rpx 24rpx 50rpx; }
.header-action, .read-all { color: #20b995; font-size: 26rpx; }
.filters { white-space: nowrap; margin-bottom: 18rpx; }
.filter-row { display: inline-flex; gap: 12rpx; }
.chip { padding: 12rpx 22rpx; border-radius: 999rpx; background: #fff; color: #718094; font-size: 24rpx; }
.chip.active { color: #159b7e; background: #e8f8f3; font-weight: 700; }
.toolbar { display: flex; justify-content: space-between; padding: 4rpx 4rpx 18rpx; color: #8a96a3; font-size: 24rpx; }
.notice { background: #fff; border-radius: 18rpx; padding: 26rpx; margin-bottom: 16rpx; border-left: 6rpx solid transparent; }
.notice.unread { border-left-color: #20c997; background: #f7fffc; }
.notice-head, .notice-foot { display: flex; align-items: center; justify-content: space-between; }
.title { flex: 1; color: #18232e; font-size: 29rpx; font-weight: 700; }
.time { margin-left: 18rpx; color: #9aa5b1; font-size: 21rpx; }
.body-text { display: block; margin: 14rpx 0; color: #596675; font-size: 25rpx; line-height: 1.6; }
.tag { color: #159b7e; background: #e8f8f3; border-radius: 999rpx; padding: 5rpx 14rpx; font-size: 21rpx; }
.dot { width: 14rpx; height: 14rpx; border-radius: 50%; background: #ff5364; }
.empty { padding: 150rpx 30rpx; text-align: center; }
.empty-title, .empty-tip { display: block; }
.empty-title { color: #4d5966; font-size: 30rpx; }
.empty-tip { color: #9aa5b1; font-size: 24rpx; margin-top: 12rpx; }
.loading { text-align: center; padding: 40rpx; color: #9aa5b1; }
.more { background: transparent; color: #20b995; font-size: 25rpx; }
</style>
