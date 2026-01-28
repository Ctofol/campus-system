<template>
  <view class="test-page">
    <view v-if="role === 'teacher'" class="teacher-tools">
      <view class="teacher-card">
        <text class="teacher-title">教师工具</text>
        <view class="teacher-actions">
          <button class="teacher-btn" @click="gotoStudents">学员管理</button>
        </view>
      </view>
    </view>
    <view v-else class="student-container">
      <view class="header-info">
        <text class="project-name">{{ projectName }}</text>
        <view class="standard-badge">
          <text class="badge-text">国家学生体质健康标准</text>
        </view>
        <text class="standard-desc">动作标准：{{ standardDesc }}</text>
        <view class="project-icon-wrapper">
          <text class="project-emoji">{{ projectEmoji }}</text>
        </view>
        <view class="test-type-switch">
          <button class="switch-btn" @click="showTypeSelector">切换测试类型</button>
          <view class="type-selector" v-if="showSelector">
            <view class="type-item" @click="switchTestType('引体向上', 'pull-up')">引体向上</view>
            <view class="type-item" @click="switchTestType('仰卧起坐', 'sit-up')">仰卧起坐</view>
            <view class="type-item" @click="switchTestType('俯卧撑', 'push-up')">俯卧撑</view>
          </view>
        </view>
      </view>
      
      <view class="camera-area">
        <!-- #ifdef H5 -->
        <view class="h5-camera-wrapper">
          <video id="h5-video-el-test" class="real-camera" autoplay playsinline muted :controls="false"></video>
          <view class="camera-overlay-content">
            <view class="count-overlay">
              <view class="count-val">{{ count }}</view>
              <view class="count-label">次</view>
            </view>
            
            <view class="progress-bar-container">
              <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
            </view>

            <view class="status-tips">
              <view class="status-text" :class="{ 'valid-text': isStandard }">{{ statusText }}</view>
            </view>
          </view>
        </view>
        <!-- #endif -->

        <!-- #ifndef H5 -->
        <camera
          class="real-camera"
          device-position="front"
          flash="off"
          @error="handleCameraError"
        >
          <cover-view class="camera-overlay-content">
            <cover-view class="count-overlay">
              <cover-view class="count-val">{{ count }}</cover-view>
              <cover-view class="count-label">次</cover-view>
            </cover-view>
            
            <cover-view class="progress-bar-container">
              <cover-view class="progress-fill" :style="{ width: progressPercent + '%' }"></cover-view>
            </cover-view>

            <cover-view class="status-tips">
              <cover-view class="status-text" :class="{ 'valid-text': isStandard }">{{ statusText }}</cover-view>
            </cover-view>
          </cover-view>
        </camera>
        <!-- #endif -->
      </view>
      
      <view class="action-area">
        <view class="timer-box">
          <text class="timer-label">测试用时</text>
          <text class="timer-text">{{ formatTime(duration) }}</text>
        </view>
        <view class="btn-group">
          <button v-if="!isTesting" class="main-btn start-btn" hover-class="btn-hover" @click="startTest">开始测试</button>
          <block v-else>
            <button class="sub-btn stop-btn" hover-class="btn-hover" @click="endTest">结束测试</button>
            <button class="sub-btn mock-btn" hover-class="btn-hover" @click="mockCount">+1 (模拟)</button>
          </block>
        </view>
      </view>
    </view>
    <CustomTabBar current="/pages/test/test" />
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { onLoad, onShow } from '@dcloudio/uni-app';

// 页面参数
const projectName = ref('引体向上');
const standardDesc = ref('下颌过杠，双臂伸直');
const testType = ref('pull-up');
const role = ref('student');

// #ifdef H5
let h5Stream = null;

onMounted(() => {
  initH5Camera();
});

onUnmounted(() => {
  if (h5Stream) {
    h5Stream.getTracks().forEach(track => track.stop());
  }
});

const initH5Camera = async () => {
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.warn('Browser does not support camera access');
      uni.showToast({ title: '当前环境不支持摄像头', icon: 'none' });
      return;
    }
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'user',
        width: { ideal: 640 },
        height: { ideal: 480 }
      }
    });
    h5Stream = stream;
    
    // 确保DOM已渲染
    // #ifdef H5
    setTimeout(() => {
      let video = document.getElementById('h5-video-el-test');
      console.log('H5 Camera Element:', video);
      
      // 如果uni-app把video标签封装成了组件，尝试查找内部video
      if (video && video.tagName !== 'VIDEO') {
        const innerVideo = video.querySelector('video');
        if (innerVideo) {
          video = innerVideo;
          console.log('Found inner video element:', video);
        }
      }

      if (video && typeof video.play === 'function') {
        video.srcObject = stream;
        video.play().catch(e => {
          console.error('Video play error:', e);
          // 某些浏览器可能需要用户交互才能播放，这里静音播放通常允许
        });
      } else {
        console.error('Video element not found or invalid:', video);
        uni.showToast({ title: '摄像头初始化失败：DOM异常', icon: 'none' });
      }
    }, 500); // 稍微延迟确保渲染
    // #endif

  } catch (e) {
    handleCameraError(e);
  }
};
// #endif

// 状态变量
const isTesting = ref(false);
const count = ref(0);
const duration = ref(0);
const timer = ref(null);
const isStandard = ref(true); // 模拟动作是否标准
const statusText = ref('准备就绪');
const showGuide = ref(false);
const targetCount = ref(10); // 默认目标

const projectEmoji = computed(() => {
  const map = {
    'pull-up': '💪',
    'sit-up': '🧘',
    'push-up': '🤸',
    'run-1000': '🏃',
    'run-800': '🏃‍♀️'
  };
  return map[testType.value] || '🏋️';
});

const progressPercent = computed(() => {
  return Math.min((count.value / targetCount.value) * 100, 100);
});

// 处理参数逻辑
const handleOptions = (options) => {
  if (options.project) projectName.value = options.project;
  if (options.type) testType.value = options.type;
  
  // 简单的标准文案映射
  const standards = {
    '引体向上': '下颌过杠，双臂伸直',
    '仰卧起坐': '双手抱头，肘部触膝',
    '俯卧撑': '身体平直，屈臂90度'
  };
  const targets = {
    '引体向上': 10,
    '仰卧起坐': 40,
    '俯卧撑': 30
  };
  
  if (standards[projectName.value]) {
    standardDesc.value = standards[projectName.value];
  }
  if (targets[projectName.value]) {
    targetCount.value = targets[projectName.value];
  }
};

// 接收参数 (onLoad)
onLoad((options) => {
  handleOptions(options);
});

// 接收参数 (onShow - 处理 tabBar 跳转传参)
onShow(() => {
  const r = uni.getStorageSync('userRole') || uni.getStorageSync('role');
  if (r) role.value = r;
  const storedProject = uni.getStorageSync('testProject');
  const storedType = uni.getStorageSync('testType');
  
  if (storedProject) {
    handleOptions({ project: storedProject, type: storedType });
    uni.removeStorageSync('testProject');
    uni.removeStorageSync('testType');
    uni.showToast({ title: '已清理传参缓存', icon: 'none' });
  }
});

const showSelector = ref(false);
const showTypeSelector = () => {
  showSelector.value = !showSelector.value;
};
const switchTestType = (project, type) => {
  handleOptions({ project, type });
  showSelector.value = false;
};

// 计时格式化
const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
};

// 开始测试
const startTest = () => {
  isTesting.value = true;
  count.value = 0;
  duration.value = 0;
  statusText.value = '正在识别动作...';
  
  timer.value = setInterval(() => {
    duration.value++;
  }, 1000);
};

// 模拟计数
const mockCount = () => {
  count.value++;
  statusText.value = '动作标准 ✅';
  setTimeout(() => {
    statusText.value = '正在识别动作...';
  }, 800);
};

// 结束测试
const endTest = () => {
  clearInterval(timer.value);
  isTesting.value = false;
  
  uni.showModal({
    title: '测试结束',
    content: `共完成 ${count.value} 次，用时 ${formatTime(duration.value)}，是否提交成绩？`,
    confirmText: '提交结果',
    cancelText: '放弃',
    success: (res) => {
      if (res.confirm) {
        submitResult();
      } else {
        // 重置
        count.value = 0;
        duration.value = 0;
        statusText.value = '准备就绪';
      }
    }
  });
};

// 提交结果
const submitResult = () => {
  uni.showLoading({ title: '正在提交成绩...' });
  
  const resultData = {
    mode: 'test',
    testProject: projectName.value,
    count: count.value,
    duration: duration.value,
    isStandard: true,
    testDate: new Date().getTime()
  };
  
  // 模拟网络请求延迟
  setTimeout(() => {
    uni.hideLoading();
    uni.navigateTo({
      url: `/pages/result/result?mode=test&project=${projectName.value}&count=${count.value}&duration=${duration.value}`
    });
  }, 1000);
};

const gotoStudents = () => {
  uni.navigateTo({ url: '/pages/teacher/students/students' });
};

const handleCameraError = (e) => {
  console.error('Camera Error:', e);
  let msg = '无法访问摄像头';
  if (e.name === 'NotAllowedError' || e.message === 'Permission denied') {
    msg = '权限被拒绝，请允许摄像头访问';
  } else if (e.name === 'NotFoundError') {
    msg = '未检测到摄像头';
  }
  
  uni.showToast({
    title: msg,
    icon: 'none',
    duration: 3000
  });
};
</script>

<style scoped>
.test-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #1a1a1a;
  color: #fff;
  align-items: center;
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
}

.teacher-tools, .header-info, .camera-area, .action-area {
  width: 100%;
  max-width: 600px; /* Optimize for larger screens */
  box-sizing: border-box;
}

.teacher-tools {
  padding: 40rpx 30rpx;
}
.teacher-card {
  background: #fff;
  color: #333;
  border-radius: 12rpx;
  padding: 20rpx;
}
.teacher-title {
  font-size: 34rpx;
  font-weight: bold;
  display: block;
  margin-bottom: 10rpx;
}
.teacher-actions {
  display: flex;
  gap: 20rpx;
}
.teacher-btn {
  background: #20C997;
  color: #fff;
}

.student-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  align-items: center;
}

.header-info {
  padding: 40rpx 30rpx 20rpx;
  text-align: center;
  flex-shrink: 0;
}

.project-name {
  font-size: 1.8rem;
  font-weight: bold;
  display: block;
  margin-bottom: 10rpx;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.project-icon-wrapper {
  width: 120rpx;
  height: 120rpx;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20rpx auto 0;
}

.project-emoji {
  font-size: 60rpx;
}

.test-type-switch {
  margin-top: 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}
.switch-btn {
  background: rgba(255,255,255,0.1);
  color: #20C997;
  font-size: 28rpx;
  padding: 12rpx 36rpx;
  border-radius: 30rpx;
  border: 1px solid rgba(32, 201, 151, 0.3);
}
.type-selector {
  background: rgba(0,0,0,0.4);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16rpx;
  overflow: hidden;
}
.type-item {
  padding: 16rpx 40rpx;
  color: #fff;
  font-size: 28rpx;
  text-align: center;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.type-item:last-child {
  border-bottom: none;
}

.standard-badge {
  display: inline-block;
  background: rgba(32, 201, 151, 0.2);
  padding: 8rpx 20rpx;
  border-radius: 12rpx;
  margin-bottom: 16rpx;
  backdrop-filter: blur(4px);
}

.badge-text {
  color: #20C997;
  font-size: 0.9rem;
  font-weight: bold;
}

.standard-desc {
  display: block;
  font-size: 1rem;
  color: #aaa;
  margin-top: 10rpx;
}

.guide-trigger {
  margin-top: 20rpx;
  background: rgba(255,255,255,0.1);
  color: #20C997;
  font-size: 24rpx;
  padding: 10rpx 30rpx;
  border-radius: 30rpx;
  border: 1px solid rgba(32, 201, 151, 0.3);
}

.camera-area {
  flex: 1;
  width: 90%;
  max-width: 600px;
  background-color: #000;
  margin: 20rpx 0;
  border-radius: 30rpx;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  border: 1px solid #333;
}

/* #ifdef H5 */
.h5-camera-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}
/* #endif */

.real-camera {
  width: 100%;
  height: 100%;
}

.camera-overlay-content {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 10;
}

.count-overlay {
  position: absolute;
  top: 45%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  display: flex;
  align-items: baseline;
  justify-content: center;
  z-index: 5;
}

.count-val {
  font-size: 6rem; /* Enhanced visibility */
  font-weight: 800;
  color: #20C997; 
  line-height: 1;
  text-shadow: 0 4px 12px rgba(32, 201, 151, 0.3);
  animation: countPop 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes countPop {
  from { transform: scale(0.8); opacity: 0.8; }
  to { transform: scale(1); opacity: 1; }
}

.count-label {
  font-size: 1.5rem;
  color: rgba(255,255,255,0.8);
  margin-left: 12rpx;
  font-weight: bold;
}

.progress-bar-container {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 10rpx;
  background: rgba(255,255,255,0.1);
}
.progress-fill {
  height: 100%;
  background: #20C997;
  transition: width 0.3s ease;
  box-shadow: 0 0 10px #20C997;
}

.status-tips {
  position: absolute;
  bottom: 60rpx; 
  left: 0;
  width: 100%;
  display: flex;
  justify-content: center;
  z-index: 10;
  pointer-events: none;
}

.status-text {
  background-color: rgba(0,0,0,0.7);
  padding: 16rpx 48rpx;
  border-radius: 50rpx;
  font-size: 1.1rem;
  color: #fff;
  /* backdrop-filter: blur(8px); cover-view不支持 */
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
  border-width: 1px;
  border-style: solid;
  border-color: rgba(255,255,255,0.1);
}

.status-text.valid-text {
  color: #20C997;
  background-color: rgba(32, 201, 151, 0.15);
  border-color: rgba(32, 201, 151, 0.4);
  /* box-shadow: 0 0 20px rgba(32, 201, 151, 0.2); cover-view support limited */
}

.action-area {
  width: 100%;
  max-width: 600px;
  padding: 20rpx 40rpx 60rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.timer-box {
  text-align: center;
  margin-bottom: 40rpx;
  background: rgba(255,255,255,0.05);
  padding: 16rpx 40rpx;
  border-radius: 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid rgba(255,255,255,0.05);
}

.timer-label {
  font-size: 0.9rem;
  color: #888;
  margin-bottom: 4rpx;
}

.timer-text {
  font-family: 'Roboto Mono', monospace;
  font-size: 2rem;
  font-weight: bold;
  color: #fff;
  letter-spacing: 2px;
}

.btn-group {
  display: flex;
  gap: 30rpx;
  width: 100%;
  justify-content: center;
}

.main-btn, .sub-btn {
  border-radius: 60rpx;
  height: 110rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  border: none;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.main-btn {
  flex: 1;
  background: linear-gradient(135deg, #20C997, #17a077);
  color: #fff;
  font-weight: bold;
  box-shadow: 0 6px 16px rgba(32, 201, 151, 0.3);
}

.sub-btn {
  flex: 1;
  font-size: 1.1rem;
  font-weight: 500;
}

.stop-btn {
  background: linear-gradient(135deg, #ff6b6b, #ee5253);
  color: #fff;
  box-shadow: 0 6px 16px rgba(238, 82, 83, 0.3);
}

.mock-btn {
  background: rgba(255,255,255,0.1);
  color: #ccc;
  border: 1px solid rgba(255,255,255,0.1);
}

.btn-hover {
  transform: scale(0.96);
  opacity: 0.9;
}

/* Responsive Media Queries */
@media (max-width: 600px) {
  .count-val {
    font-size: 5rem;
  }
  
  .camera-area {
    margin: 10rpx 20rpx;
  }
  
  .action-area {
    padding: 20rpx 30rpx 50rpx;
  }
  
  .status-tips {
    bottom: 40rpx;
  }
  
  .timer-text {
    font-size: 1.8rem;
  }
  
  .main-btn, .sub-btn {
    height: 100rpx;
    font-size: 1.1rem;
  }
}

@media (min-height: 800px) {
  .camera-area {
    margin: 40rpx 30rpx;
  }
  .action-area {
    padding-bottom: 100rpx;
  }
}

.guide-modal {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}
.guide-content {
  background: #fff;
  width: 80%;
  max-width: 600rpx;
  border-radius: 20rpx;
  padding: 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #333;
}
.guide-title {
  font-size: 36rpx;
  font-weight: bold;
  margin-bottom: 30rpx;
}
.guide-visual {
  width: 200rpx;
  height: 200rpx;
  background: #f5f5f5;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30rpx;
}
.guide-emoji {
  font-size: 80rpx;
}
.guide-desc {
  font-size: 28rpx;
  color: #666;
  text-align: center;
  margin-bottom: 40rpx;
}
.guide-btn {
  background: #20C997;
  color: #fff;
  padding: 0 60rpx;
  border-radius: 40rpx;
  font-size: 30rpx;
}
</style>
