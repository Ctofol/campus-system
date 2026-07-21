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
                <view class="exercise-summary-icon">
                  <image class="exercise-summary-icon-img" :src="exercise.iconPath" mode="aspectFit" />
                </view>
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
        <view class="camera-area" :style="{ height: cameraAreaHeight + 'px' }">
          <camera
            id="testCamera"
            ref="cameraRef"
            device-position="back"
            mode="normal"
            class="camera-live"
            @error="onCameraError"
          />
          <!-- 身体框线引导覆盖层 -->


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

      <template v-if="phase === 'processing'">
        <view class="video-processing-area">
          <view class="processing-spinner"></view>
          <text class="processing-title">视频处理中</text>
          <text class="processing-desc">正在生成预览，请稍候</text>
        </view>
      </template>

      <!-- 视频预览阶段 -->
      <template v-if="phase === 'preview'">
        <view class="video-area" :class="{ 'video-area--loading': !videoReady && !videoError }">
          <view v-if="videoError" class="video-error-mask">
            <view class="preview-loading-card preview-loading-card--error">
              <text class="processing-title">预览失败</text>
              <text class="processing-desc">视频已保存，可以直接提交；如果画面没有出现，也可以重新录制</text>
            </view>
          </view>
          <view v-if="!showPreviewVideo && !videoError" class="video-loading-mask">
            <view class="preview-loading-card">
              <view class="processing-spinner"></view>
              <text class="processing-title">视频正在准备中</text>
              <text class="processing-desc">如果首帧较慢，可以稍等后点击画面播放</text>
            </view>
          </view>
          <view v-if="showPreviewVideo && !videoReady" class="preview-status-card">
            <text class="preview-status-title">视频已录制</text>
            <text class="preview-status-desc">如果画面没有显示，可以先直接提交；系统会使用刚录制的视频进行分析</text>
          </view>
          <video
            v-if="showPreviewVideo"
            :key="previewRenderKey"
            :src="previewVideoSrc || videoPath"
            class="preview-video"
            :class="{ 'preview-video--visible': videoReady || videoError }"
            controls
            object-fit="contain"
            @loadedmetadata="onVideoReady"
            @canplay="onVideoReady"
            @play="onVideoReady"
            @error="onVideoError"
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
            <image class="analyzing-icon-img" src="/static/icons/icon-teacher.svg" mode="aspectFit" />
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
            <image v-if="analysisPassed" class="done-icon-img" src="/static/icons/icon-check.svg" mode="aspectFit" />
            <image v-else class="done-icon-img" src="/static/icons/icon-cross.svg" mode="aspectFit" />
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
import { ref, computed, nextTick } from 'vue';
import { onLoad, onUnload } from '@dcloudio/uni-app';
import {
  getExerciseById,
  normalizeExerciseId,
  TEST_INSTRUCTIONS,
  TEST_FLOW_STEPS,
  exerciseIdToApiType
} from '@/utils/test-exercise-config.js';
import { uploadFile, submitActivity, getTestAnalysisStatus, getFaceProfile } from '@/utils/request.js';

const exerciseId = ref('pull_up');
const taskId = ref(null);
const instructions = TEST_INSTRUCTIONS;
const flowSteps = TEST_FLOW_STEPS;
const exercise = computed(() => getExerciseById(exerciseId.value));

const phase = ref('ready');
const videoPath = ref('');
const previewVideoSrc = ref('');
const showPreviewVideo = ref(false);
const previewRenderKey = ref(0);
const videoUrl = ref('');
const videoReady = ref(false);
const videoError = ref(false);
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
let previewRevealTimer = null;
let videoReadyFallbackTimer = null;
let previewFallbackTried = false;
let convertedPreviewSrc = '';

const formattedTime = computed(() => timerDisplay.value);

const cameraAreaHeight = ref(500);

const isCameraApiAvailable = () => typeof uni.createCameraContext === 'function';

const isNativeVideoCaptureAvailable = () => {
  // #ifdef APP-PLUS
  return typeof plus !== 'undefined' && plus.camera && plus.camera.getCamera;
  // #endif
  return false;
};

const showUnsupportedCameraToast = () => {
  uni.showToast({ title: '当前基座不支持页面内摄像头录制', icon: 'none' });
};

const onVideoReady = () => {
  clearTimeout(videoReadyFallbackTimer);
  videoError.value = false;
  videoReady.value = true;
};

const onVideoError = (e) => {
  if (!previewFallbackTried && convertedPreviewSrc && convertedPreviewSrc !== previewVideoSrc.value) {
    previewFallbackTried = true;
    previewVideoSrc.value = convertedPreviewSrc;
    previewRenderKey.value += 1;
    videoError.value = false;
    return;
  }
  videoError.value = true;
  videoReady.value = false;
  console.error('Video preview error', e);
};

const getConvertedPreviewVideoSrc = (path = '') => {
  const raw = String(path || '').trim();
  if (!raw) return '';

  // #ifdef APP-PLUS
  try {
    if (typeof plus !== 'undefined' && plus.io && typeof plus.io.convertLocalFileSystemURL === 'function') {
      return plus.io.convertLocalFileSystemURL(raw) || raw;
    }
  } catch (e) {
    return raw;
  }
  // #endif

  return raw;
};

const enterPreview = async (path) => {
  clearTimeout(previewRevealTimer);
  clearTimeout(videoReadyFallbackTimer);
  videoPath.value = path || '';
  previewVideoSrc.value = videoPath.value;
  convertedPreviewSrc = getConvertedPreviewVideoSrc(path);
  videoUrl.value = '';
  videoReady.value = false;
  videoError.value = false;
  showPreviewVideo.value = false;
  previewRenderKey.value += 1;
  previewFallbackTried = false;
  phase.value = 'processing';

  await nextTick();
  previewRevealTimer = setTimeout(() => {
    phase.value = 'preview';
    showPreviewVideo.value = true;
    nextTick(() => {
      showPreviewVideo.value = true;
    });
  }, 300);

  videoReadyFallbackTimer = setTimeout(() => {
    if (phase.value !== 'preview') return;
    if (!showPreviewVideo.value) {
      previewRenderKey.value += 1;
      showPreviewVideo.value = true;
    }
    if (!videoReady.value) {
      videoReady.value = true;
    }
  }, 2500);
};

const captureVideoWithNativeCamera = async () => {
  const granted = await ensureCameraPermission();
  if (!granted) {
    showCameraPermissionModal();
    return false;
  }

  // #ifdef APP-PLUS
  return new Promise((resolve) => {
    try {
      const camera = plus.camera.getCamera();
      camera.startVideoCapture(
        (path) => {
          recordStartTime = new Date();
          enterPreview(path);
          resolve(true);
        },
        (err) => {
          if (err && err.code !== 11) {
            uni.showToast({ title: '录制失败，请重试', icon: 'none' });
            console.error('Native video capture fail', err);
          }
          resolve(false);
        },
        {
          filename: '_doc/test_video/',
          videoMaximumDuration: 120
        }
      );
    } catch (e) {
      console.error('Native video capture error', e);
      showUnsupportedCameraToast();
      resolve(false);
    }
  });
  // #endif

  return false;
};

onLoad((options) => {
  try {
    const sys = uni.getSystemInfoSync();
    if (sys) {
      const statusBarH = sys.statusBarHeight || 20;
      cameraAreaHeight.value = sys.windowHeight - statusBarH - 44 - 180;
    }
  } catch (e) { /* ignore */ }

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
  clearTimeout(previewRevealTimer);
  clearTimeout(videoReadyFallbackTimer);
  if (cameraCtx && isRecording.value) {
    try { cameraCtx.stopRecord(); } catch (e) { /* ignore */ }
  }
});

const goBack = () => {
  uni.navigateBack({ fail: () => uni.redirectTo({ url: '/pages/test/test' }) });
};

const ensureCameraPermission = () => {
  return new Promise((resolve) => {
    // #ifdef APP-PLUS
    if (typeof plus !== 'undefined' && plus.android && plus.android.requestPermissions) {
      plus.android.requestPermissions(
        ['android.permission.CAMERA', 'android.permission.RECORD_AUDIO'],
        (result) => {
          const denied = [
            ...(result.deniedAlways || []),
            ...(result.deniedPresent || [])
          ];
          resolve(denied.length === 0);
        },
        () => resolve(false)
      );
      return;
    }
    // #endif
    resolve(true);
  });
};

const openPermissionSettings = () => {
  // #ifdef APP-PLUS
  if (uni.openAppAuthorizeSetting) {
    uni.openAppAuthorizeSetting();
    return;
  }
  // #endif
  if (uni.openSetting) uni.openSetting();
};

const showCameraPermissionModal = () => {
  uni.showModal({
    title: '需要摄像头权限',
    content: '体测录制需要使用摄像头和麦克风。请在系统设置中允许后重试。',
    confirmText: '去设置',
    success: (res) => {
      if (res.confirm) openPermissionSettings();
    }
  });
};

const prepareCameraContext = async () => {
  if (!isCameraApiAvailable()) {
    cameraCtx = null;
    return false;
  }
  await nextTick();
  await new Promise((resolve) => setTimeout(resolve, 120));
  cameraCtx = uni.createCameraContext('testCamera');
  return !!cameraCtx;
};

const ensureFaceProfileReady = async () => {
  try {
    const profile = await getFaceProfile();
    if (profile?.status === 'verified') return true;
    uni.showModal({
      title: '需要人脸认证',
      content: '体测会先校验本人身份，请先完成人脸认证。',
      confirmText: '去认证',
      success: (res) => {
        if (res.confirm) {
          uni.navigateTo({ url: '/pages/mine/face-profile/face-profile' });
        }
      }
    });
    return false;
  } catch (e) {
    uni.showToast({ title: e.message || '认证状态读取失败', icon: 'none' });
    return false;
  }
};

const startRecording = async () => {
  if (!(await ensureFaceProfileReady())) return;
  if (!isCameraApiAvailable()) {
    if (isNativeVideoCaptureAvailable()) {
      await captureVideoWithNativeCamera();
    } else {
      showUnsupportedCameraToast();
    }
    return;
  }
  const granted = await ensureCameraPermission();
  if (!granted) {
    showCameraPermissionModal();
    return;
  }
  phase.value = 'camera';
  const ready = await prepareCameraContext();
  if (!ready) {
    phase.value = 'ready';
    showUnsupportedCameraToast();
  }
};

const onCameraError = (e) => {
  console.error('Camera preview error', e);
  showCameraPermissionModal();
};

const startCamRecord = async () => {
  if (!(await ensureFaceProfileReady())) return;
  if (!isCameraApiAvailable()) {
    if (isNativeVideoCaptureAvailable()) {
      await captureVideoWithNativeCamera();
    } else {
      showUnsupportedCameraToast();
    }
    return;
  }
  const granted = await ensureCameraPermission();
  if (!granted) {
    showCameraPermissionModal();
    return;
  }
  if (!cameraCtx) {
    await prepareCameraContext();
  }
  if (!cameraCtx) {
    uni.showToast({ title: '摄像头未就绪，请重试', icon: 'none' });
    return;
  }
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
      isRecording.value = false;
      clearInterval(timerInterval);
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
      const path = res.tempVideoPath || res.tempFilePath || '';
      if (!path) {
        uni.showToast({ title: '没有获取到视频文件，请重新录制', icon: 'none' });
        phase.value = 'camera';
        prepareCameraContext();
        return;
      }
      enterPreview(path);
    },
    fail: (err) => {
      uni.showToast({ title: '停止录制失败', icon: 'none' });
      console.error('Stop record fail', err);
    }
  });
};

const retakeRecording = () => {
  clearTimeout(previewRevealTimer);
  clearTimeout(videoReadyFallbackTimer);
  videoPath.value = '';
  previewVideoSrc.value = '';
  showPreviewVideo.value = false;
  videoUrl.value = '';
  videoReady.value = false;
  videoError.value = false;
  previewFallbackTried = false;
  convertedPreviewSrc = '';
  isRecording.value = false;
  cameraCtx = null;
  if (!isCameraApiAvailable()) {
    if (isNativeVideoCaptureAvailable()) {
      captureVideoWithNativeCamera();
    } else {
      phase.value = 'ready';
      showUnsupportedCameraToast();
    }
    return;
  }
  phase.value = 'camera';
  prepareCameraContext();
};

const submitTest = async () => {
  if (!videoPath.value) return;
  uploading.value = true;
  showPreviewVideo.value = false;
  clearTimeout(videoReadyFallbackTimer);
  await nextTick();
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
    if (phase.value === 'preview' && videoPath.value) {
      showPreviewVideo.value = true;
    }
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
      if (status === 'needs_review') {
        clearInterval(dotTimer);
        uni.showToast({ title: res?.analysis_error || '需要教师复核', icon: 'none' });
        phase.value = 'preview';
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
  width: 96rpx;
  height: 68rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
  flex-shrink: 0;
}
.exercise-summary-icon-img {
  width: 88rpx;
  height: 62rpx;
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

.video-processing-area,
.video-loading-mask {
  flex: 1;
  min-height: 520rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #f7fbfa 0%, #eef7f4 100%);
  padding: 60rpx 40rpx;
}

.video-loading-mask {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 2;
  background: rgba(247, 248, 250, 0.96);
}

.video-error-mask {
  position: absolute;
  right: 0;
  left: 0;
  bottom: 32rpx;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 36rpx;
  pointer-events: none;
}

.preview-loading-card {
  width: 100%;
  max-width: 560rpx;
  min-height: 320rpx;
  border-radius: 28rpx;
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 16rpx 40rpx rgba(26, 43, 60, 0.08);
  padding: 40rpx 32rpx;
  text-align: center;
}

.preview-loading-card--error {
  min-height: auto;
  padding: 24rpx 28rpx;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, 0.94);
}

.preview-loading-card .processing-desc {
  max-width: 420rpx;
}

.processing-spinner {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  border: 6rpx solid rgba(51, 201, 171, 0.18);
  border-top-color: #33C9AB;
  animation: processing-spin 0.8s linear infinite;
  margin-bottom: 24rpx;
}

.processing-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1a2b3c;
}

.processing-desc {
  margin-top: 12rpx;
  font-size: 24rpx;
  color: #8a9bab;
}

@keyframes processing-spin {
  to { transform: rotate(360deg); }
}

.video-area {
  position: relative;
  flex: 1;
  min-height: 600rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #f7fbfa 0%, #eef7f4 100%);
  overflow: hidden;
}

.video-area--loading {
  background: linear-gradient(180deg, #f7fbfa 0%, #eef7f4 100%);
}

.preview-video {
  width: 100%;
  height: 100%;
  min-height: 600rpx;
  background: #000;
  opacity: 1;
}

.preview-status-card {
  position: absolute;
  left: 48rpx;
  right: 48rpx;
  top: 50%;
  z-index: 1;
  transform: translateY(-50%);
  border-radius: 28rpx;
  background: rgba(255, 255, 255, 0.92);
  padding: 36rpx 30rpx;
  text-align: center;
  box-shadow: 0 16rpx 40rpx rgba(26, 43, 60, 0.08);
}

.preview-status-title {
  display: block;
  font-size: 32rpx;
  font-weight: 800;
  color: #1a2b3c;
}

.preview-status-desc {
  display: block;
  margin-top: 14rpx;
  font-size: 24rpx;
  line-height: 1.5;
  color: #8a9bab;
}

.preview-video--visible {
  position: relative;
  opacity: 1;
}

/* 摄像头实时预览 */
.camera-area {
  position: relative;
  overflow: hidden;
  background: #000;
  width: 100%;
}

.camera-live {
  width: 100%;
  height: 100%;
}



.cam-hint {
  position: absolute;
  top: 60rpx;
  left: 50%;
  transform: translateX(-50%);
  background: #000;
  opacity: 0.55;
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
  background: #000;
  opacity: 0.5;
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
