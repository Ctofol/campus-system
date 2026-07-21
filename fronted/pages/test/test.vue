<template>
  <view class="test-prep-page">
    <page-tab-header title="AI 体能测试" show-back theme="brand" />

    <scroll-view scroll-y class="test-prep-scroll">
      <view class="test-prep-body">
        <view class="section">
          <text class="section-title">选择测试项目</text>
          <view class="exercise-grid">
            <view
              v-for="item in exercises"
              :key="item.id"
              class="exercise-card"
              :class="{ 'exercise-card--active': selectedId === item.id }"
              @tap="selectExercise(item.id)"
            >
              <image v-if="selectedId === item.id" class="exercise-card__badge-img" src="/static/icons/icon-check.svg" mode="aspectFit" />
              <view class="exercise-card__icon">
                <image class="exercise-card__icon-img" :src="item.iconPath" mode="aspectFit" />
              </view>
              <text class="exercise-card__label">{{ item.label }}</text>
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
              <image class="instruction-check-img" src="/static/icons/icon-check.svg" mode="aspectFit" />
              <text class="instruction-text">{{ line }}</text>
            </view>
          </view>
        </view>

        <view v-if="taskId" class="task-hint">
          <text class="task-hint-text">已关联教师任务，开始测试后将计入任务成绩</text>
        </view>
      </view>
    </scroll-view>

    <view class="test-prep-footer">
      <button
        class="start-btn"
        :disabled="!selectedId"
        @tap="onStartTest"
      >
        开始测试
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import {
  TEST_EXERCISES,
  TEST_INSTRUCTIONS,
  DEFAULT_EXERCISE_ID,
  normalizeExerciseId
} from '@/utils/test-exercise-config.js';

const exercises = TEST_EXERCISES;
const instructions = TEST_INSTRUCTIONS;
const selectedId = ref(DEFAULT_EXERCISE_ID);
const taskId = ref(null);

onLoad((options) => {
  if (options?.taskId) {
    const id = parseInt(options.taskId, 10);
    if (!Number.isNaN(id)) taskId.value = id;
  }
  if (options?.exercise) {
    selectedId.value = normalizeExerciseId(options.exercise);
  }
});

const selectExercise = (id) => {
  selectedId.value = id;
};

const onStartTest = () => {
  if (!selectedId.value) return;
  let url = `/pages/test/session?exercise=${encodeURIComponent(selectedId.value)}`;
  if (taskId.value) {
    url += `&taskId=${taskId.value}`;
  }
  uni.navigateTo({ url });
};
</script>

<style lang="scss" scoped>
.test-prep-page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.test-prep-scroll {
  flex: 1;
  height: 0;
}

.test-prep-body {
  padding: 32rpx 30rpx 24rpx;
  box-sizing: border-box;
}

.section {
  margin-bottom: 40rpx;
}

.section-title {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: #1a2b3c;
  margin-bottom: 24rpx;
}

.exercise-grid {
  display: flex;
  flex-direction: row;
  gap: 20rpx;
}

.exercise-card {
  flex: 1;
  min-width: 0;
  background: #fff;
  border-radius: 20rpx;
  border: 2rpx solid #e8ecef;
  padding: 28rpx 12rpx 24rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.exercise-card--active {
  border-color: #20c997;
  box-shadow: 0 8rpx 24rpx rgba(32, 201, 151, 0.18);
  background: #f0faf6;
}

.exercise-card__badge-img {
  position: absolute;
  top: 12rpx;
  right: 12rpx;
  width: 36rpx;
  height: 36rpx;
}

.exercise-card__icon {
  width: 116rpx;
  height: 86rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}
.exercise-card__icon-img {
  width: 108rpx;
  height: 78rpx;
}

.exercise-card__label {
  font-size: 26rpx;
  color: #333;
  font-weight: 600;
  text-align: center;
}

.instruction-list {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(26, 43, 60, 0.05);
}

.instruction-item {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  margin-bottom: 20rpx;
}

.instruction-item:last-child {
  margin-bottom: 0;
}

.instruction-check-img {
  width: 36rpx;
  height: 36rpx;
  flex-shrink: 0;
  margin-right: 16rpx;
}

.instruction-text {
  flex: 1;
  font-size: 28rpx;
  color: #4a5568;
  line-height: 1.5;
}

.task-hint {
  padding: 20rpx 24rpx;
  background: rgba(32, 201, 151, 0.1);
  border-radius: 16rpx;
  border: 1rpx solid rgba(32, 201, 151, 0.35);
}

.task-hint-text {
  font-size: 26rpx;
  color: #0d8f6e;
  line-height: 1.45;
}

.test-prep-footer {
  flex-shrink: 0;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background: #f5f7fa;
  box-sizing: border-box;
}

.start-btn {
  width: 100%;
  height: 96rpx;
  line-height: 96rpx;
  background: #20c997;
  color: #fff;
  font-size: 32rpx;
  font-weight: 700;
  border-radius: 48rpx;
  border: none;
}

.start-btn[disabled] {
  background: #c5d0d8;
  color: #fff;
  opacity: 1;
}
</style>
