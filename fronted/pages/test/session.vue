<template>
  <view class="test-session-page">
    <page-tab-header :title="exercise.label" show-back theme="brand" />

    <scroll-view scroll-y class="test-session-scroll">
      <view class="test-session-body page-tab-body">
        <view class="status-card">
          <text class="status-icon">🎯</text>
          <text class="status-title">姿态识别能力接入中</text>
          <text class="status-desc">
            当前为测试准备阶段。正式版将支持摄像头录制，并由 AI 自动识别
            {{ exercise.label }} 完成次数。
          </text>
        </view>

        <view class="section">
          <text class="section-title">测试项目</text>
          <view class="exercise-summary">
            <text class="exercise-summary-icon">{{ exercise.icon }}</text>
            <view class="exercise-summary-copy">
              <text class="exercise-summary-name">{{ exercise.label }}</text>
              <text class="exercise-summary-brief">{{ exercise.brief }}</text>
            </view>
          </view>
        </view>

        <view class="section">
          <text class="section-title">预计流程</text>
          <view class="flow-list">
            <view v-for="item in flowSteps" :key="item.step" class="flow-item">
              <view class="flow-step-num">{{ item.step }}</view>
              <view class="flow-step-copy">
                <text class="flow-step-title">{{ item.title }}</text>
                <text class="flow-step-desc">{{ item.desc }}</text>
              </view>
            </view>
          </view>
        </view>

        <view class="section">
          <text class="section-title">测试须知</text>
          <view class="instruction-list">
            <view
              v-for="(line, idx) in instructions"
              :key="idx"
              class="instruction-item"
            >
              <view class="instruction-dot" />
              <text class="instruction-text">{{ line }}</text>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <view class="test-session-footer">
      <button class="btn-secondary" @tap="goBack">返回重新选择</button>
      <button class="btn-disabled" disabled>即将开放</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import {
  getExerciseById,
  normalizeExerciseId,
  TEST_INSTRUCTIONS,
  TEST_FLOW_STEPS
} from '@/utils/test-exercise-config.js';

const exerciseId = ref('pull_up');
const taskId = ref(null);

const instructions = TEST_INSTRUCTIONS;
const flowSteps = TEST_FLOW_STEPS;

const exercise = computed(() => getExerciseById(exerciseId.value));

onLoad((options) => {
  if (options?.exercise) {
    exerciseId.value = normalizeExerciseId(options.exercise);
  }
  if (options?.taskId) {
    const id = parseInt(options.taskId, 10);
    if (!Number.isNaN(id)) taskId.value = id;
  }
});

const goBack = () => {
  uni.navigateBack({
    fail: () => {
      uni.redirectTo({ url: '/pages/test/test' });
    }
  });
};
</script>

<style lang="scss" scoped>
.test-session-page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.test-session-scroll {
  flex: 1;
  height: 0;
}

.test-session-body {
  padding-bottom: 24rpx;
}

.status-card {
  background: linear-gradient(145deg, #2ee6b8 0%, #20c997 50%, #17b88a 100%);
  border-radius: 24rpx;
  padding: 40rpx 32rpx;
  margin-bottom: 32rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: 0 12rpx 32rpx rgba(32, 201, 151, 0.25);
}

.status-icon {
  font-size: 72rpx;
  margin-bottom: 16rpx;
}

.status-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #fff;
  margin-bottom: 16rpx;
}

.status-desc {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.92);
  line-height: 1.55;
}

.section {
  margin-bottom: 32rpx;
}

.section-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: #1a2b3c;
  margin-bottom: 20rpx;
}

.exercise-summary {
  display: flex;
  flex-direction: row;
  align-items: center;
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(26, 43, 60, 0.05);
}

.exercise-summary-icon {
  font-size: 56rpx;
  margin-right: 20rpx;
}

.exercise-summary-copy {
  flex: 1;
  min-width: 0;
}

.exercise-summary-name {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: #333;
}

.exercise-summary-brief {
  display: block;
  margin-top: 8rpx;
  font-size: 26rpx;
  color: #6b7c8f;
}

.flow-list {
  background: #fff;
  border-radius: 20rpx;
  padding: 8rpx 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(26, 43, 60, 0.05);
}

.flow-item {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f2f5;
}

.flow-item:last-child {
  border-bottom: none;
}

.flow-step-num {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: #20c997;
  color: #fff;
  font-size: 26rpx;
  font-weight: 700;
  line-height: 48rpx;
  text-align: center;
  flex-shrink: 0;
  margin-right: 20rpx;
}

.flow-step-copy {
  flex: 1;
  min-width: 0;
}

.flow-step-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.flow-step-desc {
  display: block;
  margin-top: 6rpx;
  font-size: 24rpx;
  color: #8a9bab;
}

.instruction-list {
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(26, 43, 60, 0.05);
}

.instruction-item {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  margin-bottom: 16rpx;
}

.instruction-item:last-child {
  margin-bottom: 0;
}

.instruction-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: #20c997;
  margin-top: 14rpx;
  margin-right: 16rpx;
  flex-shrink: 0;
}

.instruction-text {
  flex: 1;
  font-size: 26rpx;
  color: #4a5568;
  line-height: 1.5;
}

.test-session-footer {
  flex-shrink: 0;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  background: #f5f7fa;
}

.btn-secondary {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: #fff;
  color: #20c997;
  font-size: 30rpx;
  font-weight: 600;
  border-radius: 44rpx;
  border: 2rpx solid #20c997;
}

.btn-disabled {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: #e8ecef;
  color: #8a9bab;
  font-size: 30rpx;
  border-radius: 44rpx;
  border: none;
}
</style>
