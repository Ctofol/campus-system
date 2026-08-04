<template>
  <view class="page">
    <page-tab-header title="发送通知" show-back theme="white" />
    <view class="content page-tab-body">
      <view class="card">
        <text class="label">通知标题</text>
        <input v-model.trim="form.title" class="input" maxlength="60" placeholder="请输入标题" />
        <text class="label">通知正文</text>
        <textarea v-model.trim="form.content" class="textarea" maxlength="500" placeholder="请输入需要学生查看的内容" />
        <text class="label">接收范围</text>
        <picker :range="targetLabels" :value="targetIndex" @change="changeTarget"><view class="picker">{{ targetLabels[targetIndex] }}<text>›</text></view></picker>

        <checkbox-group v-if="form.target_type !== 'all_managed'" class="options" @change="changeValues">
          <label v-for="item in currentOptions" :key="item.value" class="option">
            <checkbox :value="String(item.value)" color="#20c997" :checked="form.target_values.map(String).includes(String(item.value))" />
            <view><text class="option-name">{{ item.label }}</text><text v-if="item.sub" class="option-sub">{{ item.sub }}</text></view>
          </label>
        </checkbox-group>
        <view v-else class="scope-tip">将发送给你当前管辖的全部 {{ targets.recipient_count || 0 }} 名学生</view>

        <view v-if="preview.recipient_count" class="preview">
          <text>预计接收 {{ preview.recipient_count }} 人</text>
          <text v-if="preview.sample_users?.length" class="sample">示例：{{ preview.sample_users.map(item => item.name).join('、') }}</text>
        </view>
        <button class="preview-btn" :loading="previewing" @tap="previewSend">预览接收人数</button>
        <button class="send-btn" :disabled="!preview.recipient_count" :loading="sending" @tap="send">确认发送</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, reactive, ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { request } from '@/utils/request.js';

const targetTypes = [
  { label: '全部管辖学生', value: 'all_managed' }, { label: '指定班级', value: 'classes' },
  { label: '指定体育选科', value: 'subjects' }, { label: '指定学生', value: 'users' },
];
const targetLabels = targetTypes.map(item => item.label);
const targetIndex = ref(0);
const targets = reactive({ recipient_count: 0, classes: [], subjects: [], students: [] });
const form = reactive({ title: '', content: '', ntype: 'teacher_message', target_type: 'all_managed', target_values: [], action_type: null, action_data: {} });
const preview = reactive({ recipient_count: 0, sample_users: [] });
const previewing = ref(false);
const sending = ref(false);
const currentOptions = computed(() => {
  if (form.target_type === 'classes') return targets.classes.map(item => ({ value: item.id, label: item.name, sub: item.major }));
  if (form.target_type === 'subjects') return targets.subjects.map(item => ({ value: item, label: item }));
  if (form.target_type === 'users') return targets.students.map(item => ({ value: item.id, label: item.name, sub: `${item.student_id || ''} ${item.class_name || ''}`.trim() }));
  return [];
});
const changeTarget = event => {
  targetIndex.value = Number(event.detail.value);
  form.target_type = targetTypes[targetIndex.value].value;
  form.target_values = [];
  Object.assign(preview, { recipient_count: 0, sample_users: [] });
};
const changeValues = event => { form.target_values = event.detail.value; Object.assign(preview, { recipient_count: 0, sample_users: [] }); };
const validate = () => {
  if (!form.title || !form.content) { uni.showToast({ title: '请填写标题和正文', icon: 'none' }); return false; }
  if (form.target_type !== 'all_managed' && !form.target_values.length) { uni.showToast({ title: '请选择接收范围', icon: 'none' }); return false; }
  return true;
};
const previewSend = async () => {
  if (!validate()) return;
  previewing.value = true;
  try { Object.assign(preview, await request({ url: '/teacher/notification-campaigns/preview', method: 'POST', data: form })); }
  catch (e) { uni.showToast({ title: e?.message || '预览失败', icon: 'none' }); }
  finally { previewing.value = false; }
};
const send = () => {
  if (!preview.recipient_count) return;
  uni.showModal({ title: '确认发送', content: `通知将发送给 ${preview.recipient_count} 名学生，发送后不可修改。`, success: async result => {
    if (!result.confirm) return;
    sending.value = true;
    try {
      const sent = await request({ url: '/teacher/notification-campaigns', method: 'POST', data: form });
      uni.showToast({ title: `已发送给${sent.recipient_count}人`, icon: 'success' });
      setTimeout(() => uni.navigateBack(), 800);
    } catch (e) { uni.showToast({ title: e?.message || '发送失败', icon: 'none' }); }
    finally { sending.value = false; }
  }});
};
onLoad(async (options = {}) => {
  try { Object.assign(targets, await request({ url: '/teacher/notification-targets', method: 'GET' })); }
  catch (e) { uni.showToast({ title: '接收范围加载失败', icon: 'none' }); }
  if (options.studentId) {
    const exists = targets.students.some(item => String(item.id) === String(options.studentId));
    if (!exists) {
      uni.showToast({ title: '该学生不在你的管辖范围内', icon: 'none' });
      return;
    }
    targetIndex.value = targetTypes.findIndex(item => item.value === 'users');
    form.target_type = 'users';
    form.target_values = [String(options.studentId)];
    form.title = options.studentName ? `给${decodeURIComponent(options.studentName)}的通知` : '';
  }
});
</script>

<style scoped>
.page { min-height: 100vh; background: #f5f7fa; }
.content { padding: 24rpx; }
.card { background: #fff; border-radius: 22rpx; padding: 30rpx 26rpx; }
.label { display: block; margin: 24rpx 0 12rpx; color: #34414e; font-size: 26rpx; font-weight: 700; }
.label:first-child { margin-top: 0; }
.input, .textarea, .picker { box-sizing: border-box; width: 100%; padding: 20rpx; border-radius: 14rpx; background: #f6f8fa; color: #18232e; font-size: 26rpx; }
.textarea { height: 220rpx; }
.picker { display: flex; justify-content: space-between; }
.options { display: block; max-height: 480rpx; overflow-y: auto; margin-top: 14rpx; border: 1rpx solid #edf0f3; border-radius: 14rpx; }
.option { display: flex; gap: 12rpx; align-items: center; padding: 20rpx; border-bottom: 1rpx solid #edf0f3; }
.option:last-child { border-bottom: 0; }
.option-name, .option-sub, .sample { display: block; }
.option-name { color: #34414e; font-size: 25rpx; }
.option-sub, .sample { color: #8a96a3; font-size: 22rpx; margin-top: 4rpx; }
.scope-tip, .preview { margin-top: 16rpx; padding: 20rpx; border-radius: 14rpx; background: #eef9f6; color: #178d73; font-size: 25rpx; }
.preview-btn, .send-btn { margin-top: 24rpx; border-radius: 999rpx; font-size: 27rpx; }
.preview-btn { background: #eef9f6; color: #159b7e; }
.send-btn { background: #20c997; color: #fff; }
.send-btn[disabled] { opacity: .45; }
</style>
