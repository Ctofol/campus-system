<template>
  <view class="ai-police">
    <view class="camera-area">
      <!-- 实时摄像头画面 -->
      <!-- #ifdef H5 -->
      <view class="h5-camera-wrapper">
        <video id="h5-video-el" class="real-camera" autoplay playsinline muted :controls="false"></video>
        <view class="camera-overlay">
          <view class="camera-tip" v-if="!isDetecting">请将全身置于摄像头区域内</view>
          <view v-else class="skeleton-overlay">
            <view class="skeleton-box"></view>
          </view>
          <view class="debug-info" v-if="isDetecting">
            置信度: {{ confidence }}% | 姿态: {{ posture }}
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
        <cover-view class="camera-overlay">
          <cover-view class="camera-tip" v-if="!isDetecting">请将全身置于摄像头区域内</cover-view>
          <cover-view v-else class="skeleton-overlay">
            <!-- 简易骨架模拟 (使用cover-view) -->
            <cover-view class="skeleton-box"></cover-view>
          </cover-view>
          <cover-view class="debug-info" v-if="isDetecting">
            置信度: {{ confidence }}% | 姿态: {{ posture }}
          </cover-view>
        </cover-view>
      </camera>
      <!-- #endif -->
    </view>

    <view class="dashboard">
      <view class="counter-box">
        <text class="count-label">有效计数</text>
        <text class="count-val">{{ count }}</text>
      </view>
      <view class="status-box">
        <text class="status-label">当前状态</text>
        <text class="status-val" :class="statusClass">{{ statusText }}</text>
      </view>
    </view>

    <view class="controls">
      <button v-if="!isDetecting" class="btn-start" @click="startDetect">开始AI计数</button>
      <button v-else class="btn-stop" @click="stopDetect">结束训练</button>
      
      <view class="simulation-tools">
        <text class="tool-title">开发调试：模拟场景</text>
        <view class="tool-btns">
          <button size="mini" @click="simValidAction">模拟有效动作</button>
          <button size="mini" @click="simCheat('遮挡')">模拟遮挡</button>
          <button size="mini" @click="simCheat('多人')">模拟多人</button>
          <button size="mini" @click="simCheat('非活体')">模拟照片攻击</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const isDetecting = ref(false);
const count = ref(0);
const statusText = ref('准备就绪');
const statusClass = ref('normal');
const confidence = ref(0);
const posture = ref('Standing');

let timer = null;

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
    // 检查浏览器支持
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('浏览器不支持摄像头访问');
    }
    
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { 
        facingMode: 'user',
        width: { ideal: 640 },
        height: { ideal: 480 }
      } 
    });
    
    h5Stream = stream;
    
    // 延迟确保DOM渲染
    setTimeout(() => {
      let video = document.getElementById('h5-video-el');
      console.log('AI Police Video Element:', video);
      
      // 兼容查找
      if (video && video.tagName !== 'VIDEO') {
        const inner = video.querySelector('video');
        if (inner) video = inner;
      }
      
      if (video && typeof video.play === 'function') {
        video.srcObject = stream;
        video.play().catch(e => console.error('Play error:', e));
      } else {
        console.error('Video element invalid:', video);
        uni.showToast({ title: '画面加载失败', icon: 'none' });
      }
    }, 500);

  } catch (e) {
    handleCameraError(e);
  }
};
// #endif

const startDetect = () => {
  isDetecting.value = true;
  statusText.value = '正在检测...';
  statusClass.value = 'normal';
  count.value = 0;
  startSimulationLoop();
};

const stopDetect = () => {
  isDetecting.value = false;
  statusText.value = '训练结束';
  clearInterval(timer);
  
  uni.showModal({
    title: '训练结束',
    content: `本次训练共完成 ${count.value} 次，是否查看结果？`,
    confirmText: '查看结果',
    cancelText: '取消',
    success: (res) => {
      if (res.confirm) {
        uni.showLoading({ title: '正在保存...' });
        setTimeout(() => {
            uni.hideLoading();
            uni.navigateTo({
              url: `/pages/result/result?mode=test&project=AI智能训练&count=${count.value}&duration=0`
            });
        }, 800);
      }
    }
  });
};

const startSimulationLoop = () => {
  timer = setInterval(() => {
    // 随机波动置信度
    confidence.value = (95 + Math.random() * 5).toFixed(1);
  }, 1000);
};

const simValidAction = () => {
  if (!isDetecting) return;
  statusText.value = '动作标准';
  statusClass.value = 'success';
  posture.value = 'Squat Down';
  setTimeout(() => {
    count.value++;
    posture.value = 'Standing';
    statusText.value = '正在检测...';
    statusClass.value = 'normal';
  }, 800);
};

const simCheat = (type) => {
  if (!isDetecting) return;
  statusText.value = `警告：${type}`;
  statusClass.value = 'warn';
  confidence.value = (Math.random() * 40).toFixed(1);
  
  uni.vibrateLong();
  uni.showToast({
    title: `检测到异常：${type}`,
    icon: 'none',
    duration: 2000
  });

  setTimeout(() => {
    statusText.value = '正在检测...';
    statusClass.value = 'normal';
    confidence.value = 98.5;
  }, 2000);
};

const handleCameraError = (e) => {
  console.error('Camera Error:', e);
  let msg = '无法访问摄像头';
  if (e.name === 'NotAllowedError' || e.message === 'Permission denied') {
    msg = '权限被拒绝，请在设置中允许摄像头访问';
  } else if (e.name === 'NotFoundError') {
    msg = '未检测到摄像头设备';
  } else if (e.name === 'NotSupportedError') {
    msg = '浏览器不支持该摄像头配置';
  }
  
  uni.showToast({
    title: msg,
    icon: 'none',
    duration: 3000
  });
};
</script>

<style scoped>
.ai-police {
  min-height: 100vh;
  background: #1a1a1a;
  color: #fff;
  display: flex;
  flex-direction: column;
}
.camera-area {
  height: 60vh;
  background: #000;
  position: relative;
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
.camera-overlay {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 10;
}
.camera-tip {
  color: #999;
  font-size: 32rpx;
  background-color: rgba(0,0,0,0.3);
  padding: 10rpx 20rpx;
  border-radius: 8rpx;
}
.skeleton-overlay {
  position: relative;
  width: 200rpx;
  height: 400rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}
.skeleton-box {
  width: 200rpx;
  height: 400rpx;
  border-width: 2px;
  border-style: dashed;
  border-color: #20C997;
  background-color: transparent;
}
.debug-info {
  position: absolute;
  bottom: 20rpx;
  left: 20rpx;
  font-size: 24rpx;
  color: #0f0;
  background-color: rgba(0,0,0,0.5);
  padding: 8rpx;
  border-radius: 4rpx;
}
.dashboard {
  flex: 1;
  background: #2c3e50;
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 20rpx;
}
.counter-box, .status-box {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.count-val { font-size: 80rpx; font-weight: bold; color: #20C997; }
.count-label { font-size: 28rpx; color: #ccc; }
.status-val { font-size: 36rpx; font-weight: bold; margin-top: 10rpx; }
.status-val.normal { color: #fff; }
.status-val.success { color: #20C997; }
.status-val.warn { color: #d81e06; }
.status-label { font-size: 28rpx; color: #ccc; }

.controls {
  padding: 30rpx;
  background: #fff;
  border-top-left-radius: 30rpx;
  border-top-right-radius: 30rpx;
  margin-top: -30rpx;
  z-index: 10;
}
.btn-start { background: #20C997; color: #fff; border-radius: 50rpx; }
.btn-stop { background: #d81e06; color: #fff; border-radius: 50rpx; }

.simulation-tools {
  margin-top: 30rpx;
  border-top: 1px solid #eee;
  padding-top: 20rpx;
}
.tool-title { font-size: 26rpx; color: #666; display: block; margin-bottom: 15rpx; }
.tool-btns { display: flex; flex-wrap: wrap; gap: 15rpx; }

@keyframes pulse {
  0% { border-color: #20C997; box-shadow: 0 0 10rpx #20C997; }
  50% { border-color: #fff; box-shadow: 0 0 20rpx #fff; }
  100% { border-color: #20C997; box-shadow: 0 0 10rpx #20C997; }
}
</style>