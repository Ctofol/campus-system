<template>
  <view class="page">
    <page-tab-header title="通知详情" show-back theme="white" />
    <view class="content page-tab-body">
      <view v-if="loading" class="state">加载中...</view>
      <view v-else-if="error" class="state"><text>{{ error }}</text><button class="secondary" @tap="load">重新加载</button></view>
      <view v-else class="card">
        <view class="meta"><text class="tag">{{ typeLabel(note.ntype) }}</text><text class="time">{{ formatTime(note.created_at) }}</text></view>
        <text class="title">{{ note.title }}</text>
        <text class="sender">发送人：{{ note.sender_name || '系统' }}</text>
        <text class="body">{{ note.body || '暂无正文' }}</text>
        <view v-if="note.action_type && !note.action_available" class="unavailable">{{ note.action_message || '关联内容已删除或暂不可用' }}</view>
        <button v-else-if="note.action_type" class="primary" @tap="openRelated">查看关联内容</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { request } from '@/utils/request.js';

const id = ref(0);
const note = ref({});
const loading = ref(true);
const error = ref('');
const typeLabel = type => ({ system: '系统公告', task: '任务通知', task_reminder: '任务提醒', teacher_message: '教师消息', student_message: '学生消息', health_review: '健康审批', run_group: '跑团', run_group_activity: '跑团活动', run_group_apply: '报名提醒', score: '成绩通知' }[type] || '通知');
const formatTime = value => value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '';
const load = async () => {
  loading.value = true; error.value = '';
  try {
    note.value = await request({ url: `/notifications/${id.value}`, method: 'GET' });
    if (!note.value.is_read) await request({ url: `/notifications/${id.value}/read`, method: 'PUT' });
    uni.$emit('notifications:changed');
  } catch (e) { error.value = e?.message || '通知不存在或已无法访问'; }
  finally { loading.value = false; }
};
const openRelated = () => {
  const data = note.value.action_data || {};
  const role = uni.getStorageSync('userInfo')?.role || '';
  const routes = {
    task_detail: role === 'teacher' ? `/pages/teacher/tasks/detail?id=${data.task_id}` : '/pages/student/tasks/list',
    health_request: '/pages/health/request',
    run_group: `/pages/run-group/detail?groupId=${data.group_id}`,
    run_group_activity: `/pages/run-group/activity-detail?activityId=${data.activity_id}`,
    score_detail: role === 'teacher' && data.task_id
      ? `/pages/teacher/tasks/detail?id=${data.task_id}`
      : (data.task_id ? '/pages/student/tasks/list' : '/pages/history/history'),
    student_detail: `/pages/teacher/students/detail?id=${data.student_id}`,
  };
  const url = routes[note.value.action_type];
  if (!url || /undefined|null/.test(url)) return uni.showToast({ title: '关联内容暂不可用', icon: 'none' });
  uni.navigateTo({ url, fail: () => uni.showToast({ title: '关联内容暂不可用', icon: 'none' }) });
};
onLoad(options => {
  id.value = Number(options.id) || 0;
  if (!id.value) { loading.value = false; error.value = '通知参数不正确'; return; }
  load();
});
</script>

<style scoped>
.page { min-height: 100vh; background: #f5f7fa; }
.content { padding: 28rpx; }
.card { background: #fff; border-radius: 22rpx; padding: 34rpx 30rpx; box-shadow: 0 8rpx 28rpx rgba(24,35,46,.05); }
.meta { display: flex; justify-content: space-between; align-items: center; }
.tag { color: #159b7e; background: #e8f8f3; border-radius: 999rpx; padding: 7rpx 16rpx; font-size: 22rpx; }
.time, .sender { color: #96a1ad; font-size: 23rpx; }
.title { display: block; margin-top: 26rpx; font-size: 36rpx; line-height: 1.35; color: #18232e; font-weight: 800; }
.sender { display: block; margin-top: 14rpx; }
.body { display: block; margin-top: 34rpx; color: #465360; font-size: 28rpx; line-height: 1.85; white-space: pre-wrap; }
.primary, .secondary { margin-top: 40rpx; border-radius: 999rpx; font-size: 27rpx; }
.primary { background: #20c997; color: #fff; }
.secondary { color: #20a985; background: #e8f8f3; }
.unavailable { margin-top: 38rpx; padding: 22rpx; border-radius: 14rpx; background: #fff7e8; color: #9a6b16; font-size: 25rpx; }
.state { padding: 180rpx 40rpx; color: #8a96a3; text-align: center; font-size: 27rpx; }
</style>
