<template>
  <view class="test-page-root">
    <!-- Custom Navigation Bar -->
    <view class="custom-navbar" :style="{paddingTop: statusBarHeight + 'px'}">
      <view class="navbar-content">
        <text class="navbar-title">体能测试</text>
      </view>
    </view>
    
    <!-- Content Wrapper with padding for navbar and tabbar -->
    <view class="content-wrapper" :style="{paddingTop: (statusBarHeight + 44) + 'px'}">
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
        <!-- Removed emoji icon wrapper for space efficiency -->
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
          
          <view v-if="!cameraReady && !cameraError" class="camera-placeholder">
              <text class="loading-text">正在启动摄像头...</text>
          </view>
          <view v-if="cameraError" class="camera-placeholder error-placeholder">
              <text class="error-text">{{ cameraError }}</text>
              <button size="mini" @click="initH5Camera">重试</button>
          </view>

          <view class="camera-overlay-content" v-if="isTesting">
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
        ></camera>
        
        <!-- Switched to view to avoid appendChild error - ensure z-index is high -->
        <view class="camera-overlay-content" style="z-index: 999;" v-if="isTesting">
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
        <!-- #endif -->
      </view>
      
      <view class="action-area">
        <view class="timer-box">
          <text class="timer-label">{{ isTesting ? '测试用时' : (lastResult ? '上次用时' : '测试用时') }}</text>
          <text class="timer-text">{{ isTesting ? formatTime(duration) : (lastResult ? lastResult.duration : '00:00') }}</text>
        </view>
        <!-- Last Result Display -->
        <view v-if="!isTesting && lastResult" class="last-result-box">
            <text class="result-title">上次成绩</text>
            <view class="result-row">
                <text class="result-label">数量：</text>
                <text class="result-value">{{ lastResult.count }} 次</text>
            </view>
            <view class="result-row">
                <text class="result-label">用时：</text>
                <text class="result-value">{{ lastResult.duration }}</text>
            </view>
        </view>

        <view class="btn-group">
          <button v-if="!isTesting" class="main-btn start-btn" hover-class="btn-hover" @click="startTest">
              {{ lastResult ? '再次测试' : '开始测试' }}
          </button>
          <block v-else>
            <button class="sub-btn stop-btn" hover-class="btn-hover" @click="endTest">结束测试</button>
            <button class="sub-btn mock-btn" hover-class="btn-hover" @click="mockCount">+1 (模拟)</button>
            <!-- #ifdef H5 -->
            <button class="sub-btn mock-btn" hover-class="btn-hover" @click="isRecording ? stopH5Record() : startH5Record()">
              {{ isRecording ? '停止录制' : '开始录制' }}
            </button>
            <!-- #endif -->
          </block>
        </view>
      </view>
    </view>

    <!-- Guide Modal -->
    <view v-if="showGuide" class="guide-modal" @click="showGuide = false">
      <view class="guide-content" @click.stop>
        <text class="guide-title">动作指南</text>
        <view class="guide-visual">
          <text class="guide-emoji">{{ projectEmoji }}</text>
        </view>
        <text class="guide-desc">{{ standardDesc }}</text>
        <button class="guide-btn" @click="showGuide = false">我知道了</button>
      </view>
    </view>
    
    </view>
    <!-- TabBar outside of content wrapper - Switched to view to avoid appendChild error -->
    <view class="tab-bar">
      <view class="tab-bar-border"></view>
      <view v-for="(item, index) in tabList" :key="index" class="tab-bar-item" @click="switchTab(item)">
        <image class="tab-icon" :src="currentTab === item.pagePath ? item.selectedIconPath : item.iconPath"></image>
        <view class="tab-text" :style="{ color: currentTab === item.pagePath ? '#20C997' : '#666666' }">{{ item.text }}</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { onLoad, onShow, onHide } from '@dcloudio/uni-app';
import { request, BASE_URL } from '@/utils/request.js';

// 状态栏高度
const statusBarHeight = ref(20);
const cameraContext = ref(null);
const captureTimer = ref(null);
const isTesting = ref(false);
const count = ref(0);
const duration = ref(0);
const timer = ref(null);
const lastResult = ref(null);
const pendingVideoUrl = ref('');
const progressPercent = computed(() => Math.min((count.value / 20) * 100, 100)); // 假设目标20个
const isStandard = ref(false);
const statusText = ref('请做好准备');
const showSelector = ref(false);
const showGuide = ref(false);
const projectEmoji = computed(() => {
  const map = { 'pull-up': '💪', 'sit-up': '🧘', 'push-up': '🙇' };
  return map[testType.value] || '🏃';
});

// #ifdef H5
const cameraReady = ref(false);
const cameraError = ref('');
const isRecording = ref(false);
let mediaRecorder = null;
let recordedChunks = [];
// #endif

// TabBar Logic
const currentTab = '/pages/test/test';
const tabList = computed(() => {
  return role.value === 'teacher' ? [
    { pagePath: "/pages/teacher/home/home", text: "主页", iconPath: "/static/tab/home.png", selectedIconPath: "/static/tab/home-active.png" },
    { pagePath: "/pages/teacher/manage/manage", text: "管理", iconPath: "/static/tab/run.png", selectedIconPath: "/static/tab/run-active.png" },
    { pagePath: "/pages/teacher/mine/mine", text: "我的", iconPath: "/static/tab/mine.png", selectedIconPath: "/static/tab/mine-active.png" }
  ] : [
    { pagePath: "/pages/home/home", text: "首页", iconPath: "/static/tab/home.png", selectedIconPath: "/static/tab/home-active.png" },
    { pagePath: "/pages/run/run", text: "跑步", iconPath: "/static/tab/run.png", selectedIconPath: "/static/tab/run-active.png" },
    { pagePath: "/pages/test/test", text: "体测", iconPath: "/static/tab/test.png", selectedIconPath: "/static/tab/test-active.png" },
    { pagePath: "/pages/mine/mine", text: "我的", iconPath: "/static/tab/mine.png", selectedIconPath: "/static/tab/mine-active.png" }
  ];
});

const switchTab = (item) => {
  if (item.pagePath === currentTab) return;
  uni.redirectTo({ url: item.pagePath });
};

// 页面参数
const projectName = ref('引体向上');
const standardDesc = ref('下颌过杠，双臂伸直');
const testType = ref('pull-up');
const role = ref('student');

onShow(() => {
  const userRole = uni.getStorageSync('userRole') || 'student';
  role.value = userRole;
  
  // #ifndef H5
  // 小程序/App需要创建上下文
  if (!cameraContext.value) {
    cameraContext.value = uni.createCameraContext();
  }
  // #endif
});

const showTypeSelector = () => {
  showSelector.value = !showSelector.value;
};

const switchTestType = (name, type) => {
  projectName.value = name;
  testType.value = type;
  showSelector.value = false;
  
  // 更新标准描述
  if (type === 'pull-up') standardDesc.value = '下颌过杠，双臂伸直';
  else if (type === 'sit-up') standardDesc.value = '双手抱头，肘部触膝';
  else if (type === 'push-up') standardDesc.value = '身体平直，屈臂90度';
  
  // 重置状态
  count.value = 0;
  duration.value = 0;
  isTesting.value = false;
  statusText.value = '请做好准备';
};

// 计时格式化
const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
};

// 模拟计数
const mockCount = () => {
  count.value++;
  isStandard.value = true;
  statusText.value = '动作标准';
  setTimeout(() => {
    isStandard.value = false;
    statusText.value = '保持动作';
  }, 1000);
};

// 开始测试
const startTest = () => {
  if (isTesting.value) return;
  
  isTesting.value = true;
  count.value = 0;
  duration.value = 0;
  statusText.value = '正在识别...';
  pendingVideoUrl.value = '';
  
  // 启动计时器
  timer.value = setInterval(() => {
    duration.value++;
  }, 1000);
  
  // 模拟自动识别 (每3秒一次)
  captureTimer.value = setInterval(() => {
    mockCount();
  }, 3000);
};

// 结束测试
const endTest = async () => {
  if (!isTesting.value) return;
  
  // 停止计时和模拟
  clearInterval(timer.value);
  clearInterval(captureTimer.value);
  isTesting.value = false;
  statusText.value = '测试结束';
  
  lastResult.value = {
    count: count.value,
    duration: formatTime(duration.value),
    date: new Date().toLocaleString()
  };
  
  // #ifdef H5
  if (isRecording.value && mediaRecorder) {
    await stopH5Record(true);
  }
  // #endif
  
  uni.showLoading({ title: '正在上传数据...' });
  
  try {
    // 1. 拍照作为证据
    const snapshotPath = await takeSnapshot();
    
    let evidenceUrl = '';
    if (snapshotPath) {
      // 2. 上传图片
      const uploadRes = await uploadFile(snapshotPath);
      if (uploadRes && uploadRes.url) {
        evidenceUrl = uploadRes.url;
      }
    }
    
    // 3. 提交成绩
    await submitResult(evidenceUrl);
    
    uni.hideLoading();
    uni.showModal({
      title: '测试完成',
      content: `本次成绩：${count.value}次\n用时：${formatTime(duration.value)}`,
      showCancel: false
    });
    
  } catch (e) {
    uni.hideLoading();
    uni.showToast({ title: '数据提交失败', icon: 'none' });
    console.error(e);
  }
};

// 拍照功能
const takeSnapshot = () => {
  return new Promise((resolve, reject) => {
    // #ifdef H5
    if (h5VideoElement && h5VideoElement.videoWidth) {
      try {
        const canvas = document.createElement('canvas');
        canvas.width = h5VideoElement.videoWidth;
        canvas.height = h5VideoElement.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(h5VideoElement, 0, 0, canvas.width, canvas.height);
        canvas.toBlob((blob) => {
          if (!blob) {
              console.error('Canvas toBlob failed');
              resolve(null);
              return;
          }
          // 创建一个指向 blob 的 URL
          const url = URL.createObjectURL(blob);
          resolve(url); // H5下 uni.uploadFile 支持 blob url
        }, 'image/jpeg', 0.8);
      } catch (e) {
        console.error('H5 snapshot failed', e);
        resolve(null);
      }
    } else {
      console.warn('H5 video element not ready for snapshot');
      resolve(null);
    }
    // #endif

    // #ifndef H5
    if (cameraContext.value) {
      cameraContext.value.takePhoto({
        quality: 'normal',
        success: (res) => {
          resolve(res.tempImagePath);
        },
        fail: (err) => {
          console.error('App snapshot failed', err);
          resolve(null);
        }
      });
    } else {
      resolve(null);
    }
    // #endif
  });
};

// 上传文件
const uploadFile = (filePath) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token');
    uni.uploadFile({
      url: `${BASE_URL}/upload`,
      filePath: filePath,
      name: 'file',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (uploadFileRes) => {
        try {
          const data = JSON.parse(uploadFileRes.data);
          resolve(data);
        } catch (e) {
          reject(e);
        }
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
};

// 提交结果
const submitResult = () => {
  return request({
    url: '/activity/finish',
    method: 'POST',
    data: {
      type: 'test',
      source: 'free', // 自由练习
      started_at: new Date(Date.now() - duration.value * 1000).toISOString(),
      ended_at: new Date().toISOString(),
      metrics: {
        count: count.value,
        duration: duration.value,
        qualified: count.value >= 10, // 假设10个及格
        checkpoints: JSON.stringify([]) // 必需字段
      },
      evidence: [
        ...(pendingVideoUrl.value ? [{ evidence_type: 'video', data_ref: pendingVideoUrl.value }] : [])
      ]
    }
  });
};

// #ifdef H5
let h5Stream = null;
let h5VideoElement = null;

const initH5Camera = async () => {
  try {
    cameraError.value = '';
    
    // 检查浏览器支持
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        cameraError.value = '当前浏览器不支持摄像头访问';
        return;
    }

    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'user' }, 
      audio: false 
    });
    h5Stream = stream;
    
    // 使用 nextTick 确保 DOM 更新，增加延时确保 uni-app 渲染完成
    setTimeout(() => {
      let video = document.getElementById('h5-video-el-test');
      
      // 兼容 uni-app H5 渲染结构：如果获取到的是 uni-video 组件包装器，则查找内部 video 标签
      if (video && video.tagName !== 'VIDEO') {
          const innerVideo = video.querySelector('video');
          if (innerVideo) video = innerVideo;
      }

      if (video) {
        h5VideoElement = video;
        // 必须设置 autoplay 和 playsinline
        video.setAttribute('autoplay', '');
        video.setAttribute('playsinline', '');
        video.setAttribute('muted', '');
        
        video.srcObject = stream;
        
        // 监听加载完成
        video.onloadedmetadata = () => {
          const playPromise = video.play();
          if (playPromise !== undefined) {
              playPromise.then(() => {
                  cameraReady.value = true;
                  console.log('Camera started successfully');
              }).catch(error => {
                  console.error('Video play error:', error);
                  cameraError.value = '视频播放失败: ' + error.message;
              });
          } else {
              cameraReady.value = true;
          }
        };
      } else {
        console.error('Video element not found by ID: h5-video-el-test');
        cameraError.value = '无法获取视频元素';
      }
    }, 500); // 增加延时到 500ms
  } catch (err) {
    console.error('Camera init failed:', err);
    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        cameraError.value = '请允许摄像头访问权限';
    } else {
        cameraError.value = '无法访问摄像头: ' + err.message;
    }
    cameraReady.value = false;
  }
};

const stopH5Camera = () => {
  if (h5Stream) {
    h5Stream.getTracks().forEach(track => track.stop());
    h5Stream = null;
  }
  cameraReady.value = false;
};

const startH5Record = () => {
  if (!h5Stream || isRecording.value) return;
  recordedChunks = [];
  try {
    mediaRecorder = new MediaRecorder(h5Stream, { mimeType: 'video/webm;codecs=vp9' });
  } catch (e) {
    try {
      mediaRecorder = new MediaRecorder(h5Stream, { mimeType: 'video/webm' });
    } catch (err) {
      uni.showToast({ title: '浏览器不支持视频录制', icon: 'none' });
      return;
    }
  }
  mediaRecorder.ondataavailable = (event) => {
    if (event.data && event.data.size > 0) recordedChunks.push(event.data);
  };
  mediaRecorder.onstop = async () => {
    const blob = new Blob(recordedChunks, { type: mediaRecorder.mimeType || 'video/webm' });
    await uploadVideoBlob(blob);
  };
  mediaRecorder.start();
  isRecording.value = true;
};

const stopH5Record = async (fromEnd = false) => {
  if (!mediaRecorder || !isRecording.value) return;
  return new Promise((resolve) => {
    mediaRecorder.onstop = async () => {
      const blob = new Blob(recordedChunks, { type: mediaRecorder.mimeType || 'video/webm' });
      const url = await uploadVideoBlob(blob);
      if (url) pendingVideoUrl.value = url;
      isRecording.value = false;
      mediaRecorder = null;
      recordedChunks = [];
      resolve(true);
    };
    mediaRecorder.stop();
    if (!fromEnd) {
      uni.showToast({ title: '视频已保存', icon: 'none' });
    }
  });
};

const uploadVideoBlob = async (blob) => {
  try {
    const token = uni.getStorageSync('token');
    const form = new FormData();
    const fileName = `test-${Date.now()}.webm`;
    form.append('file', blob, fileName);
    const res = await fetch(`${BASE_URL}/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: form
    });
    const data = await res.json();
    return data.url;
  } catch (e) {
    console.error('Upload video failed', e);
    return '';
  }
};

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
  
  if (standards[projectName.value]) {
    standardDesc.value = standards[projectName.value];
  }
};

// 接收参数 (onLoad)
onLoad((options) => {
  const sys = uni.getSystemInfoSync();
  statusBarHeight.value = sys.statusBarHeight || 20;
  if (options) {
    handleOptions(options);
  }
});

const gotoStudents = () => {
  uni.navigateTo({ url: '/pages/teacher/students/students' });
};

const handleCameraError = (e) => {
  console.error('Camera Error:', e);
  let msg = '无法访问摄像头';
  if (e.detail && e.detail.errMsg) {
      msg = e.detail.errMsg;
  }
  // #ifdef H5
  if (e.name === 'NotAllowedError' || e.message === 'Permission denied') {
    msg = '权限被拒绝，请允许摄像头访问';
  } else if (e.name === 'NotFoundError') {
    msg = '未检测到摄像头';
  }
  // #endif
  
  uni.showToast({
    title: msg,
    icon: 'none',
    duration: 3000
  });
};

onMounted(() => {
  initH5Camera();
});

onHide(() => {
    stopH5Camera();
    // 停止测试
    if (isTesting.value) {
      clearInterval(timer.value);
      clearInterval(captureTimer.value);
      isTesting.value = false;
    }
});

onUnmounted(() => {
  stopH5Camera();
});
// #endif
</script>

<style scoped>
.custom-navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: #1a1a1a;
  z-index: 999;
}
.navbar-content {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.navbar-title {
  color: #fff;
  font-size: 16px;
  font-weight: bold;
}

.test-page-root {
  height: 100vh;
  background-color: #1a1a1a;
  position: relative;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  box-sizing: border-box;
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
  color: #fff;
  overflow-y: auto;
}

.teacher-tools, .header-info, .camera-area, .action-area {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.last-result-box {
  margin-top: 20px;
  background-color: #2a2a2a;
  border-radius: 12px;
  padding: 15px;
  width: 80%;
  border: 1px solid #333;
}

.result-title {
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  display: block;
  text-align: center;
}

.result-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.result-label {
  color: #888;
  font-size: 14px;
}

.result-value {
  color: #20C997;
  font-size: 16px;
  font-weight: bold;
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
  width: 100%;
  max-width: 100%;
  /* 4:3 Aspect Ratio approx for mobile screens, not too tall */
  height: 75vw; 
  max-height: 50vh; /* Cap height so it doesn't scroll off on long screens */
  min-height: 500rpx;
  background-color: #000;
  margin: 0;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  border-top: 1px solid #333;
  border-bottom: 1px solid #333;
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
  object-fit: cover;
}

.camera-overlay-content {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 10;
  pointer-events: none; /* Allow clicks to pass through if needed */
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

/* Tab Bar Styles */
.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100rpx;
  background: white;
  display: flex;
  padding-bottom: env(safe-area-inset-bottom);
  z-index: 99999;
}

.tab-bar-border {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 1px;
  background-color: rgba(0, 0, 0, 0.1);
  transform: scaleY(0.5);
}

.tab-bar-item {
  flex: 1;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}

.tab-icon {
  width: 50rpx;
  height: 50rpx;
  margin-bottom: 4rpx;
}

.tab-text {
  font-size: 20rpx;
}
.camera-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 5;
}
.loading-text {
  color: #fff;
  font-size: 28rpx;
}
.error-placeholder {
  background: #333;
  gap: 20rpx;
}
.error-text {
  color: #ff4d4f;
  font-size: 28rpx;
  text-align: center;
  padding: 0 40rpx;
}
</style>
