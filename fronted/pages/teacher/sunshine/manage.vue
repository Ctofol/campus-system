<template>
  <view class="page">
    <page-tab-header title="阳光跑管理" show-back theme="white" />
    <scroll-view scroll-y class="content page-tab-body">
      <view class="class-card">
        <picker mode="selector" :range="classOptions" range-key="class_name" @change="onClassChange">
          <view class="class-picker">
            <view>
              <text class="label">管理班级</text>
              <text class="class-name">{{ currentRule.class_name || '请选择班级' }}</text>
            </view>
            <view class="picker-arrow"></view>
          </view>
        </picker>
        <text class="class-desc">教师配置长期规则，学生日常阳光跑自动计入本周目标。</text>
      </view>

      <view class="overview-grid">
        <view class="overview-item">
          <text class="overview-num">{{ dashboard.completion_rate || 0 }}%</text>
          <text class="overview-label">本周完成率</text>
        </view>
        <view class="overview-item">
          <text class="overview-num">{{ dashboard.completed_count || 0 }}</text>
          <text class="overview-label">已完成</text>
        </view>
        <view class="overview-item">
          <text class="overview-num">{{ dashboard.incomplete_count || 0 }}</text>
          <text class="overview-label">未完成</text>
        </view>
      </view>

      <view class="section-card">
        <view class="section-header">
          <text class="section-title">常态化规则</text>
          <switch :checked="ruleForm.enabled" color="#20C997" @change="onEnabledChange" />
        </view>
        <view class="form-row">
          <text class="form-label">每周次数</text>
          <input class="form-input" type="number" v-model.number="ruleForm.weekly_required_count" />
          <text class="form-unit">次</text>
        </view>
        <view class="form-row">
          <text class="form-label">单次距离</text>
          <input class="form-input" type="digit" v-model.number="ruleForm.min_distance_km" />
          <text class="form-unit">km</text>
        </view>
        <view class="form-row">
          <text class="form-label">最低时长</text>
          <input class="form-input" type="number" v-model.number="minDurationMinutes" />
          <text class="form-unit">分钟</text>
        </view>
        <view class="form-row">
          <text class="form-label">有效配速</text>
          <input class="pace-input" type="digit" v-model.number="ruleForm.min_pace" />
          <text class="pace-sep">-</text>
          <input class="pace-input" type="digit" v-model.number="ruleForm.max_pace" />
          <text class="form-unit">分/km</text>
        </view>
        <button class="save-btn" :loading="saving" @click="saveRule">保存规则</button>
      </view>

      <view class="section-card">
        <view class="section-header">
          <text class="section-title">学生完成明细</text>
          <text class="section-sub">{{ dashboard.valid_run_count || 0 }} 次有效跑</text>
        </view>
        <view class="student-row" v-for="student in dashboard.students" :key="student.student_id">
          <view class="student-main">
            <text class="student-name">{{ student.name }}</text>
            <text class="student-meta">{{ student.student_no || '暂无学号' }} · {{ student.valid_count }}/{{ ruleForm.weekly_required_count }} 次</text>
          </view>
          <view class="student-status" :class="{ done: student.completed }">
            <text>{{ student.completed ? '已完成' : '未完成' }}</text>
          </view>
        </view>
        <view class="empty" v-if="!loading && (!dashboard.students || dashboard.students.length === 0)">
          <text>当前班级暂无学生数据</text>
        </view>
      </view>
      <view class="bottom-space"></view>
    </scroll-view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { request } from '@/utils/request.js';

const loading = ref(false);
const saving = ref(false);
const classOptions = ref([]);
const currentIndex = ref(0);
const dashboard = ref({ students: [] });

const ruleForm = ref({
  class_id: 0,
  class_name: '',
  weekly_required_count: 3,
  min_distance_km: 2,
  min_duration_sec: 0,
  min_pace: 3,
  max_pace: 10,
  enabled: true
});

const currentRule = computed(() => classOptions.value[currentIndex.value] || ruleForm.value);
const minDurationMinutes = computed({
  get: () => Math.round((Number(ruleForm.value.min_duration_sec) || 0) / 60),
  set: (val) => {
    ruleForm.value.min_duration_sec = Math.max(0, Math.round((Number(val) || 0) * 60));
  }
});

const normalizeRule = (rule) => ({
  class_id: rule.class_id || 0,
  class_name: rule.class_name || '',
  weekly_required_count: Number(rule.weekly_required_count || 3),
  min_distance_km: Number(rule.min_distance_km || 2),
  min_duration_sec: Number(rule.min_duration_sec || 0),
  min_pace: Number(rule.min_pace || 3),
  max_pace: Number(rule.max_pace || 10),
  enabled: rule.enabled !== false
});

const loadRules = async () => {
  const res = await request({ url: '/teacher/sunshine/rules', method: 'GET' });
  classOptions.value = Array.isArray(res) ? res.map(normalizeRule) : [];
  if (currentIndex.value >= classOptions.value.length) currentIndex.value = 0;
  if (classOptions.value.length > 0) {
    ruleForm.value = normalizeRule(classOptions.value[currentIndex.value]);
    await loadDashboard();
  }
};

const loadDashboard = async () => {
  const cls = currentRule.value;
  if (!cls?.class_id) return;
  const res = await request({
    url: `/teacher/sunshine/dashboard?class_id=${cls.class_id}`,
    method: 'GET'
  });
  dashboard.value = res || { students: [] };
  if (res?.rule) {
    ruleForm.value = normalizeRule(res.rule);
    classOptions.value[currentIndex.value] = normalizeRule(res.rule);
  }
};

const loadPage = async () => {
  if (!uni.getStorageSync('token')) return;
  loading.value = true;
  try {
    await loadRules();
  } catch (e) {
    console.error('load sunshine manage failed', e);
    uni.showToast({ title: e.message || '加载失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
};

const onClassChange = async (e) => {
  currentIndex.value = Number(e.detail.value) || 0;
  ruleForm.value = normalizeRule(classOptions.value[currentIndex.value] || {});
  await loadDashboard();
};

const onEnabledChange = (e) => {
  ruleForm.value.enabled = !!e.detail.value;
};

const saveRule = async () => {
  if (!ruleForm.value.class_id) return;
  saving.value = true;
  try {
    const payload = {
      weekly_required_count: Number(ruleForm.value.weekly_required_count || 0),
      min_distance_km: Number(ruleForm.value.min_distance_km || 0),
      min_duration_sec: Number(ruleForm.value.min_duration_sec || 0),
      min_pace: Number(ruleForm.value.min_pace || 0),
      max_pace: Number(ruleForm.value.max_pace || 0),
      enabled: !!ruleForm.value.enabled
    };
    const res = await request({
      url: `/teacher/sunshine/rules/${ruleForm.value.class_id}`,
      method: 'PUT',
      data: payload
    });
    classOptions.value[currentIndex.value] = normalizeRule(res);
    ruleForm.value = normalizeRule(res);
    await loadDashboard();
    uni.showToast({ title: '规则已保存', icon: 'success' });
  } catch (e) {
    console.error('save sunshine rule failed', e);
    uni.showToast({ title: e.message || '保存失败', icon: 'none' });
  } finally {
    saving.value = false;
  }
};

onShow(loadPage);
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f7fa;
}

.content {
  min-height: 100vh;
}

.class-card,
.section-card {
  margin: 24rpx 28rpx;
  padding: 28rpx;
  border-radius: 20rpx;
  background: #fff;
  box-shadow: 0 4rpx 18rpx rgba(0, 0, 0, 0.04);
}

.class-picker,
.section-header,
.form-row,
.student-row {
  display: flex;
  align-items: center;
}

.class-picker,
.section-header,
.student-row {
  justify-content: space-between;
}

.label,
.form-label,
.section-sub,
.student-meta,
.class-desc {
  color: #8a9bab;
  font-size: 24rpx;
}

.class-name {
  display: block;
  margin-top: 8rpx;
  color: #1f2d3d;
  font-size: 34rpx;
  font-weight: 700;
}

.class-desc {
  display: block;
  margin-top: 18rpx;
  line-height: 1.5;
}

.picker-arrow {
  width: 16rpx;
  height: 16rpx;
  border-right: 3rpx solid #98a6b3;
  border-bottom: 3rpx solid #98a6b3;
  transform: rotate(45deg);
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18rpx;
  margin: 0 28rpx 24rpx;
}

.overview-item {
  background: #fff;
  border-radius: 18rpx;
  padding: 26rpx 12rpx;
  text-align: center;
}

.overview-num {
  display: block;
  color: #20c997;
  font-size: 40rpx;
  font-weight: 800;
}

.overview-label {
  display: block;
  margin-top: 8rpx;
  color: #8a9bab;
  font-size: 23rpx;
}

.section-title {
  color: #1f2d3d;
  font-size: 30rpx;
  font-weight: 700;
}

.form-row {
  min-height: 88rpx;
  border-bottom: 1rpx solid #eef2f5;
}

.form-label {
  width: 150rpx;
}

.form-input,
.pace-input {
  flex: 1;
  height: 64rpx;
  text-align: right;
  color: #1f2d3d;
  font-size: 30rpx;
}

.pace-input {
  max-width: 120rpx;
}

.pace-sep {
  color: #8a9bab;
  padding: 0 12rpx;
}

.form-unit {
  min-width: 72rpx;
  margin-left: 12rpx;
  color: #8a9bab;
  font-size: 24rpx;
  text-align: right;
}

.save-btn {
  height: 84rpx;
  line-height: 84rpx;
  margin-top: 28rpx;
  border-radius: 42rpx;
  background: #20c997;
  color: #fff;
  font-size: 30rpx;
  border: none;
}

.student-row {
  padding: 22rpx 0;
  border-bottom: 1rpx solid #eef2f5;
}

.student-row:last-child {
  border-bottom: none;
}

.student-main {
  flex: 1;
  min-width: 0;
}

.student-name {
  display: block;
  color: #1f2d3d;
  font-size: 28rpx;
  font-weight: 600;
}

.student-meta {
  display: block;
  margin-top: 6rpx;
}

.student-status {
  padding: 8rpx 18rpx;
  border-radius: 999rpx;
  background: #fff4e5;
  color: #c77800;
  font-size: 23rpx;
}

.student-status.done {
  background: #e8f8f2;
  color: #20c997;
}

.empty {
  padding: 60rpx 0;
  text-align: center;
  color: #9ca3af;
  font-size: 25rpx;
}

.bottom-space {
  height: 60rpx;
}
</style>
