<template>
  <view class="test-session-page">
    <page-tab-header :title="exercise.label" show-back theme="brand" />

    <view class="test-session-body">
      <!-- 录制阶段 -->
      <template v-if="phase === 'ready'">
        <scroll-view scroll-y class="test-session-scroll">
          <view class="page-tab-body">
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
                <view v-for="(line, idx) in instructions" :key="idx" class="instruction-item">
                  <view class="instruction-dot" />
                  <text class="instruction-text">{{ line }}</text>
                </view>
              </view>
            </view>
          </view>
        </scroll-view>

        <view class="test-session-footer">
          <button class="btn-back" @tap="goBack">返回重新选择</button>
          <button class="btn-primary" @tap="startRecording">开始录制</button>
        </view>
      </template>

      <!-- 摄像头实时预览 + 身体框线引导 -->
      <template v-if="phase === 'camera' || phase === 'recording'">
        <view class="camera-area">
          <camera
            ref="cameraRef"
            device-position="back"
            mode="normal"
            class="camera-live"
            @error="onCameraError"
          />
          <!-- 身体框线引导覆盖层 -->
          <cover-view class="body-guide-overlay">
            <!-- 头部圆 -->
            <cover-view class="guide-head" />
            <!-- 连接线：头-肩 -->
            <cover-view class="guide-line guide-line-neck" />
            <!-- 肩线 -->
            <cover-view class="guide-line guide-line-shoulders" />
            <!-- 躯干 -->
            <cover-view class="guide-line guide-line-torso" />
            <!-- 腿 - 用两个V形 -->
            <cover-view class="guide-line guide-line-left-leg" />
            <cover-view class="guide-line guide-line-right-leg" />
            <!-- 肩膀圆点 -->
            <cover-view class="guide-dot guide-dot-ls" />
            <cover-view class="guide-dot guide-dot-rs" />
            <!-- 手肘圆点 -->
            <cover-view class="guide-dot guide-dot-le" />
            <cover-view class="guide-dot guide-dot-re" />
            <!-- 手腕圆点 -->
            <cover-view class="guide-dot guide-dot-lw" />
            <cover-view class="guide-dot guide-dot-rw" />
            <!-- 髋圆点 -->
            <cover-view class="guide-dot guide-dot-lh" />
            <cover-view class="guide-dot guide-dot-rh" />
            <!-- 膝盖圆点 -->
            <cover-view class="guide-dot guide-dot-lk" />
            <cover-view class="guide-dot guide-dot-rk" />
            <!-- 脚踝圆点 -->
            <cover-view class="guide-dot guide-dot-la" />
            <cover-view class="guide-dot guide-dot-ra" />
          </cover-view>

          <cover-view class="cam-hint">{{ isRecording ? '录制中...请完成动作' : '对准框线，确保全身入镜' }}</cover-view>
          <cover-view v-if="isRecording" class="cam-timer">{{ formattedTime }}</cover-view>
          <cover-view v-if="isRecording" class="cam-rec-dot" />
        </view>

        <view class="test-session-footer">
          <button v-if="!isRecording" class="btn-secondary" @tap="goBack">返回重新选择</button>
          <button v-if="!isRecording" class="btn-primary" @tap="startCamRecord">开始录制</button>
          <button v-if="isRecording" class="btn-danger" @tap="stopCamRecord">结束录制</button>
        </view>
      </template>

      <!-- 视频预览阶段 -->
      <template v-if="phase === 'preview'">
        <view class="video-area">
          <video
            :src="videoPath"
            class="preview-video"
            controls
            object-fit="contain"
          />
        </view>
        <view class="test-session-footer">
          <button class="btn-secondary" @tap="retakeRecording">重新录制</button>
          <button class="btn-primary" :disabled="uploading" @tap="submitTest">
            {{ uploading ? '上传中...' : '提交测试' }}
          </button>
        </view>
      </template>

      <!-- 分析阶段 -->
      <template v-if="phase === 'analyzing'">
        <view class="analyzing-area">
          <view class="analyzing-animation">
            <image class="analyzing-icon-img" src="/static/主页GO图标.PNG" mode="aspectFit" />
          </view>
          <text class="analyzing-title">AI 正在分析中...</text>
          <text class="analyzing-desc">系统正在识别您的动作次数，请稍候</text>
          <view class="analyzing-dots">
            <text v-for="i in 3" :key="i" class="dot" :class="{ active: dotIndex >= i }">●</text>
          </view>
        </view>
      </template>

      <!-- 完成阶段 -->
      <template v-if="phase === 'done'">
        <view class="done-area">
          <view class="done-icon-wrap" :class="analysisPassed ? 'done-pass' : 'done-fail'">
            <image v-if="analysisPassed" class="done-icon-img" src="/static/勾号图标.png" mode="aspectFit" />
            <image v-else class="done-icon-img" src="/static/叉号图标.png" mode="aspectFit" />
          </view>
          <text class="done-title">{{ analysisPassed ? '测试完成' : '未达标' }}</text>
          <text class="done-count">{{ analysisCount }} 次</text>
          <text class="done-score">得分 {{ analysisScore }} 分</text>
          <button class="btn-primary" @tap="goToResult">查看详情</button>
        </view>
      </template>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onLoad, onUnload } from '@dcloudio/uni-app';
import {
  getExerciseById,
  normalizeExerciseId,
  TEST_INSTRUCTIONS,
  TEST_FLOW_STEPS,
  exerciseIdToApiType
} from '@/utils/test-exercise-config.js';
import { uploadFile, submitActivity, getTestAnalysisStatus } from '@/utils/request.js';

const exerciseId = ref('pull_up');
const taskId = ref(null);
const instructions = TEST_INSTRUCTIONS;
const flowSteps = TEST_FLOW_STEPS;
const exercise = computed(() => getExerciseById(exerciseId.value));

const phase = ref('ready');
const videoPath = ref('');
const videoUrl = ref('');
const uploading = ref(false);
const dotIndex = ref(0);
const analysisCount = ref(0);
const analysisScore = ref(0);
const analysisPassed = ref(false);
const isRecording = ref(false);
const cameraRef = ref(null);
let cameraCtx = null;
let dotTimer = null;
let pollTimer = null;
let activityId = null;
let recordStartTime = null;
const timerDisplay = ref('0:00');
let timerInterval = null;

const formattedTime = computed(() => timerDisplay.value);

onLoad((options) => {
  if (options?.exercise) {
    exerciseId.value = normalizeExerciseId(options.exercise);
  }
  if (options?.taskId) {
    const id = parseInt(options.taskId, 10);
    if (!Number.isNaN(id)) taskId.value = id;
  }
});

onUnload(() => {
  clearInterval(timerInterval);
  clearInterval(dotTimer);
  clearTimeout(pollTimer);
  if (cameraCtx && isRecording.value) {
    try { cameraCtx.stopRecord(); } catch (e) { /* ignore */ }
  }
});

const goBack = () => {
  uni.navigateBack({ fail: () => uni.redirectTo({ url: '/pages/test/test' }) });
};

const startRecording = () => {
  phase.value = 'camera';
};

const onCameraError = (e) => {
  uni.showToast({ title: '摄像头不可用，请授权或重试', icon: 'none' });
};

const startCamRecord = () => {
  cameraCtx = uni.createCameraContext();
  recordStartTime = new Date();
  isRecording.value = true;
  timerDisplay.value = '0:00';

  timerInterval = setInterval(() => {
    const elapsed = Math.floor((Date.now() - recordStartTime) / 1000);
    const min = Math.floor(elapsed / 60);
    const sec = elapsed % 60;
    timerDisplay.value = `${min}:${sec.toString().padStart(2, '0')}`;
  }, 500);

  cameraCtx.startRecord({
    success: () => {},
    fail: (err) => {
      uni.showToast({ title: '启动录制失败', icon: 'none' });
      console.error('Start record fail', err);
    }
  });
};

const stopCamRecord = () => {
  isRecording.value = false;
  clearInterval(timerInterval);

  if (!cameraCtx) return;

  cameraCtx.stopRecord({
    success: (res) => {
      videoPath.value = res.tempVideoPath || res.tempFilePath;
      phase.value = 'preview';
    },
    fail: (err) => {
      uni.showToast({ title: '停止录制失败', icon: 'none' });
      console.error('Stop record fail', err);
    }
  });
};

const retakeRecording = () => {
  videoPath.value = '';
  videoUrl.value = '';
  isRecording.value = false;
  cameraCtx = null;
  phase.value = 'camera';
};

const submitTest = async () => {
  if (!videoPath.value) return;
  uploading.value = true;
  try {
    const uploadRes = await uploadFile(videoPath.value, 'video');
    const url = uploadRes.url;
    if (!url) throw new Error('上传返回URL为空');

    videoUrl.value = url;
    const now = new Date();
    const startedAt = recordStartTime || new Date(now.getTime() - 60000);
    const endedAt = now;

    const res = await submitActivity({
      type: 'test',
      source: taskId.value ? 'task' : 'free',
      started_at: startedAt.toISOString(),
      ended_at: endedAt.toISOString(),
      task_id: taskId.value || undefined,
      metrics: {
        video_url: url,
        duration: Math.round((endedAt - startedAt) / 1000),
        exercise_type: exerciseIdToApiType(exerciseId.value),
        count: 0,
        qualified: false
      },
      evidence: []
    });

    activityId = res?.id;
    if (!activityId) throw new Error('提交活动失败');

    phase.value = 'analyzing';
    startDotAnimation();
    pollAnalysis();
  } catch (e) {
    uni.showToast({ title: e.message || '提交失败', icon: 'none' });
  } finally {
    uploading.value = false;
  }
};

const startDotAnimation = () => {
  dotIndex.value = 0;
  dotTimer = setInterval(() => {
    dotIndex.value = (dotIndex.value + 1) % 4;
  }, 600);
};

const pollAnalysis = () => {
  let attempts = 0;
  const maxAttempts = 60;

  const check = async () => {
    if (!activityId) return;
    attempts++;
    try {
      const res = await getTestAnalysisStatus(activityId);
      const status = res?.analysis_status;
      if (status === 'success' || status === 'completed') {
        clearInterval(dotTimer);
        analysisCount.value = res?.count || 0;
        analysisScore.value = res?.score || 0;
        analysisPassed.value = !!res?.qualified;
        phase.value = 'done';
        return;
      }
      if (status === 'failed') {
        clearInterval(dotTimer);
        uni.showToast({ title: res?.analysis_error || '分析失败', icon: 'none' });
        phase.value = 'preview';
        return;
      }
    } catch (e) {
      // continue polling
    }

    if (attempts < maxAttempts) {
      pollTimer = setTimeout(check, 2000);
    } else {
      clearInterval(dotTimer);
      uni.showToast({ title: '分析超时，请稍后查看', icon: 'none' });
      phase.value = 'preview';
    }
  };

  pollTimer = setTimeout(check, 1500);
};

const goToResult = () => {
  const data = {
    type: 'test',
    test_project: exercise.value.label,
    metrics: {
      count: analysisCount.value,
      qualified: analysisPassed.value,
      score: analysisScore.value,
      duration: 0,
      distance: 0
    },
    display_mode: 'test'
  };
  const dataStr = encodeURIComponent(JSON.stringify(data));
  uni.redirectTo({ url: `/pages/result/result?data=${dataStr}` });
};
</script>

<style lang="scss" scoped>
.test-session-page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.test-session-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.test-session-scroll {
  flex: 1;
  height: 0;
}

.page-tab-body {
  padding: 32rpx 30rpx 24rpx;
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
  background: #33C9AB;
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
  background: #33C9AB;
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

.btn-primary {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: #33C9AB;
  color: #fff;
  font-size: 30rpx;
  font-weight: 700;
  border-radius: 44rpx;
  border: none;
}

.btn-primary[disabled] {
  background: #c5d0d8;
  color: #fff;
  opacity: 1;
}

.btn-secondary {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: #fff;
  color: #33C9AB;
  font-size: 30rpx;
  font-weight: 600;
  border-radius: 44rpx;
  border: 2rpx solid #33C9AB;
}

.btn-danger {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: #F87171;
  color: #fff;
  font-size: 30rpx;
  font-weight: 700;
  border-radius: 44rpx;
  border: none;
}

.btn-back {
  width: 100%;
  height: 80rpx;
  line-height: 80rpx;
  background: transparent;
  color: #8a9bab;
  font-size: 26rpx;
  border: none;
}

.video-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000;
  overflow: hidden;
}

.preview-video {
  width: 100%;
  height: 100%;
}

/* 摄像头实时预览 */
.camera-area {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: #000;
}

.camera-live {
  width: 100%;
  height: 100%;
}

/* 身体框线引导覆盖层 */
.body-guide-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 320rpx;
  height: 560rpx;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.guide-head {
  position: absolute;
  top: 0;
  left: 50%;
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  border: 3rpx dashed rgba(51, 201, 171, 0.5);
  transform: translateX(-50%);
}

.guide-line {
  position: absolute;
  background: rgba(51, 201, 171, 0.35);
}

.guide-line-neck {
  top: 60rpx;
  left: 50%;
  width: 2rpx;
  height: 40rpx;
  transform: translateX(-50%);
}

.guide-line-shoulders {
  top: 100rpx;
  left: 50%;
  width: 180rpx;
  height: 2rpx;
  transform: translateX(-50%);
}

.guide-line-torso {
  top: 102rpx;
  left: 50%;
  width: 2rpx;
  height: 200rpx;
  transform: translateX(-50%);
}

.guide-line-left-leg {
  top: 302rpx;
  left: 50%;
  width: 2rpx;
  height: 120rpx;
  transform: rotate(12deg);
  transform-origin: top center;
}

.guide-line-right-leg {
  top: 302rpx;
  left: 50%;
  width: 2rpx;
  height: 120rpx;
  transform: rotate(-12deg);
  transform-origin: top center;
}

.guide-dot {
  position: absolute;
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  background: rgba(51, 201, 171, 0.6);
  border: 2rpx solid rgba(51, 201, 171, 0.8);
}

.guide-dot-ls { top: 100rpx; left: 50%; transform: translate(-90rpx, -7rpx); }
.guide-dot-rs { top: 100rpx; left: 50%; transform: translate(76rpx, -7rpx); }
.guide-dot-le { top: 168rpx; left: 50%; transform: translate(-110rpx, -7rpx); }
.guide-dot-re { top: 168rpx; left: 50%; transform: translate(96rpx, -7rpx); }
.guide-dot-lw { top: 236rpx; left: 50%; transform: translate(-100rpx, -7rpx); }
.guide-dot-rw { top: 236rpx; left: 50%; transform: translate(86rpx, -7rpx); }
.guide-dot-lh { top: 302rpx; left: 50%; transform: translate(-40rpx, -7rpx); }
.guide-dot-rh { top: 302rpx; left: 50%; transform: translate(26rpx, -7rpx); }
.guide-dot-lk { top: 390rpx; left: 50%; transform: translate(-24rpx, -7rpx); }
.guide-dot-rk { top: 390rpx; left: 50%; transform: translate(10rpx, -7rpx); }
.guide-dot-la { top: 490rpx; left: 50%; transform: translate(-18rpx, -7rpx); }
.guide-dot-ra { top: 490rpx; left: 50%; transform: translate(4rpx, -7rpx); }

.cam-hint {
  position: absolute;
  top: 60rpx;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 24rpx;
  padding: 10rpx 28rpx;
  border-radius: 36rpx;
  white-space: nowrap;
}

.cam-timer {
  position: absolute;
  top: 120rpx;
  right: 30rpx;
  color: #F87171;
  font-size: 36rpx;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  background: rgba(0, 0, 0, 0.5);
  padding: 6rpx 20rpx;
  border-radius: 28rpx;
}

.cam-rec-dot {
  position: absolute;
  top: 130rpx;
  right: 28rpx;
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #F87171;
  animation: rec-blink 1s ease-in-out infinite;
  display: none;
}

@keyframes rec-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.analyzing-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60rpx 40rpx;
}

.analyzing-animation {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #E8F8F2, #F0FDF6);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 40rpx;
}

.analyzing-icon-img {
  width: 72rpx;
  height: 72rpx;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.15); }
}

.analyzing-title {
  font-size: 36rpx;
  font-weight: 800;
  color: #191C1E;
  margin-bottom: 16rpx;
}

.analyzing-desc {
  font-size: 26rpx;
  color: #8E8E93;
  text-align: center;
  line-height: 1.5;
}

.analyzing-dots {
  margin-top: 40rpx;
  display: flex;
  gap: 12rpx;
}

.analyzing-dots .dot {
  font-size: 24rpx;
  color: #D1D5DB;
  transition: color 0.3s;
}

.analyzing-dots .dot.active {
  color: #33C9AB;
}

.done-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60rpx 40rpx;
}

.done-icon-wrap {
  width: 140rpx;
  height: 140rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32rpx;
}

.done-pass {
  background: #E8F8F2;
}

.done-fail {
  background: #FFF0F0;
}

.done-icon-img {
  width: 64rpx;
  height: 64rpx;
}

.done-title {
  font-size: 36rpx;
  font-weight: 800;
  color: #191C1E;
  margin-bottom: 16rpx;
}

.done-count {
  font-size: 72rpx;
  font-weight: 900;
  color: #33C9AB;
  margin-bottom: 8rpx;
}

.done-score {
  font-size: 28rpx;
  color: #8E8E93;
  margin-bottom: 48rpx;
}
</style>
