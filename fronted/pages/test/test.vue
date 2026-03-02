<template>
  <view class="test-container">
    <!-- 自定义导航栏 -->
    <view class="custom-navbar" :style="{paddingTop: statusBarHeight + 'px'}">
      <view class="navbar-content">
        <view class="navbar-left" @click="goBack">
          <text class="back-icon">←</text>
        </view>
        <text class="navbar-title">体能测试</text>
        <view class="navbar-right"></view>
      </view>
    </view>
    
    <view class="content-wrapper" :style="{paddingTop: (statusBarHeight + 44) + 'px'}">
      <!-- 测试项目选择 -->
      <view class="test-header">
        <text class="test-title">{{ currentTest.name }}</text>
        <view class="standard-badge">
          <text class="badge-text">国家学生体质健康标准</text>
        </view>
        <text class="standard-desc">{{ currentTest.desc }}</text>
        
        <button class="switch-btn" @click="showTestSelector">
          切换测试类型
        </button>
      </view>
      
      <!-- 文件上传区域 -->
      <view class="upload-area">
        <view v-if="!uploadedFile" class="upload-placeholder" @click="showUploadOptions">
          <text class="upload-icon">📹</text>
          <text class="upload-text">点击上传测试视频</text>
          <text class="upload-hint">支持MP4格式，最大100MB</text>
        </view>
        
        <view v-else class="upload-preview">
          <video 
            v-if="uploadedFile.type === 'video'" 
            :src="uploadedFile.url" 
            class="preview-video"
            controls
            poster=""
          ></video>
          <image 
            v-else 
            :src="uploadedFile.url" 
            class="preview-image"
            mode="aspectFit"
          ></image>
          <view class="upload-actions">
            <button class="reupload-btn" @click="showUploadOptions">重新上传</button>
          </view>
        </view>
      </view>
      
      <!-- 测试控制 -->
      <view class="test-controls">
        <view class="timer-display">
          <text class="timer-label">测试用时</text>
          <text class="timer-value">{{ formatTime(testDuration) }}</text>
        </view>
        
        <button 
          class="test-btn" 
          :class="{ active: isTesting }"
          @click="toggleTest"
        >
          {{ isTesting ? '结束测试' : '开始测试' }}
        </button>
      </view>
      
      <!-- 测试结果 -->
      <view class="test-result" v-if="testResult">
        <text class="result-title">测试结果</text>
        <view class="result-data">
          <text class="result-count">完成次数：{{ testResult.count }}</text>
          <text class="result-status" :class="{ qualified: testResult.qualified }">
            {{ testResult.qualified ? '✓ 达标' : '✗ 未达标' }}
          </text>
        </view>
        
        <!-- AI评分显示 -->
        <view v-if="testResult.score" class="ai-score">
          <text class="score-title">AI评分</text>
          <text class="score-value">{{ testResult.score }}分</text>
          <text class="score-detail" v-if="testResult.score_detail">{{ testResult.score_detail }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { uploadFile, submitActivity } from '@/utils/request.js';

const statusBarHeight = ref(20);
const currentTest = ref({
  name: '引体向上',
  type: 'pull-up',
  desc: '动作标准：下颏过杠，双臂伸直'
});

const testTypes = [
  { name: '引体向上', type: 'pull-up', desc: '动作标准：下颏过杠，双臂伸直' },
  { name: '仰卧起坐', type: 'sit-up', desc: '动作标准：双手抱头，起身触膝' },
  { name: '俯卧撑', type: 'push-up', desc: '动作标准：身体平直，胸部触地' }
];

const isTesting = ref(false);
const testDuration = ref(0);
const testResult = ref(null);
const uploadedFile = ref(null);

let timer = null;

const goBack = () => {
  uni.navigateBack();
};

const showTestSelector = () => {
  const itemList = testTypes.map(t => t.name);
  uni.showActionSheet({
    itemList,
    success: (res) => {
      currentTest.value = testTypes[res.tapIndex];
      testResult.value = null;
    }
  });
};

const showUploadOptions = () => {
  uni.showActionSheet({
    itemList: ['从相册选择视频', '从相册选择图片', '拍摄视频', '拍摄照片'],
    success: (res) => {
      if (res.tapIndex === 0) {
        chooseVideoFromGallery();
      } else if (res.tapIndex === 1) {
        chooseImageFromGallery();
      } else if (res.tapIndex === 2) {
        recordVideo();
      } else if (res.tapIndex === 3) {
        takePhoto();
      }
    }
  });
};

const chooseVideoFromGallery = () => {
  // #ifdef MP-WEIXIN
  // 微信小程序使用 chooseMedia
  uni.chooseMedia({
    count: 1,
    mediaType: ['video'],
    sourceType: ['album'],
    maxDuration: 300,
    success: (res) => {
      console.log('Choose video success:', res);
      const media = res.tempFiles[0];
      validateAndUpload(media.tempFilePath, 'video');
    },
    fail: (err) => {
      console.error('Choose video failed:', err);
      uni.showToast({
        title: '选择视频失败',
        icon: 'none'
      });
    }
  });
  // #endif
  
  // #ifndef MP-WEIXIN
  uni.chooseVideo({
    sourceType: ['album'],
    maxDuration: 300,
    success: (res) => {
      validateAndUpload(res.tempFilePath, 'video');
    },
    fail: (err) => {
      console.error('Choose video failed:', err);
      uni.showToast({
        title: '选择视频失败',
        icon: 'none'
      });
    }
  });
  // #endif
};

const chooseImageFromGallery = () => {
  uni.chooseImage({
    count: 1,
    sourceType: ['album'],
    success: (res) => {
      console.log('Choose image success:', res);
      validateAndUpload(res.tempFilePaths[0], 'image');
    },
    fail: (err) => {
      console.error('Choose image failed:', err);
      uni.showToast({
        title: '选择图片失败',
        icon: 'none'
      });
    }
  });
};

const recordVideo = () => {
  // #ifdef MP-WEIXIN
  uni.chooseMedia({
    count: 1,
    mediaType: ['video'],
    sourceType: ['camera'],
    maxDuration: 300,
    success: (res) => {
      console.log('Record video success:', res);
      const media = res.tempFiles[0];
      validateAndUpload(media.tempFilePath, 'video');
    },
    fail: (err) => {
      console.error('Record video failed:', err);
      uni.showToast({
        title: '拍摄视频失败',
        icon: 'none'
      });
    }
  });
  // #endif
  
  // #ifndef MP-WEIXIN
  uni.chooseVideo({
    sourceType: ['camera'],
    maxDuration: 300,
    success: (res) => {
      validateAndUpload(res.tempFilePath, 'video');
    },
    fail: (err) => {
      console.error('Record video failed:', err);
      uni.showToast({
        title: '拍摄视频失败',
        icon: 'none'
      });
    }
  });
  // #endif
};

const takePhoto = () => {
  uni.chooseImage({
    count: 1,
    sourceType: ['camera'],
    success: (res) => {
      console.log('Take photo success:', res);
      validateAndUpload(res.tempFilePaths[0], 'image');
    },
    fail: (err) => {
      console.error('Take photo failed:', err);
      uni.showToast({
        title: '拍照失败',
        icon: 'none'
      });
    }
  });
};

// 移除旧的 chooseFromGallery 函数

const validateAndUpload = async (filePath, fileType) => {
  try {
    // 获取文件信息进行前端验证
    const fileInfo = await new Promise((resolve, reject) => {
      uni.getFileInfo({
        filePath,
        success: resolve,
        fail: reject
      });
    });
    
    // 文件大小验证
    const maxSize = fileType === 'video' ? 100 * 1024 * 1024 : 5 * 1024 * 1024; // 100MB for video, 5MB for image
    if (fileInfo.size > maxSize) {
      uni.showToast({
        title: `文件大小超过限制（${fileType === 'video' ? '100MB' : '5MB'}）`,
        icon: 'none'
      });
      return;
    }
    
    // 显示上传进度
    uni.showLoading({ title: '上传中...' });
    
    // 上传文件
    const uploadResult = await uploadFile(filePath, fileType);
    
    uploadedFile.value = {
      url: uploadResult.url,
      type: uploadResult.type,
      size: uploadResult.size,
      originalName: uploadResult.original_filename
    };
    
    uni.hideLoading();
    uni.showToast({
      title: '上传成功',
      icon: 'success'
    });
    
  } catch (error) {
    uni.hideLoading();
    console.error('Upload error:', error);
    uni.showToast({
      title: '上传失败，请重试',
      icon: 'none'
    });
  }
};

const toggleTest = () => {
  if (isTesting.value) {
    stopTest();
  } else {
    startTest();
  }
};

const startTest = () => {
  isTesting.value = true;
  testDuration.value = 0;
  testResult.value = null;
  
  timer = setInterval(() => {
    testDuration.value++;
  }, 1000);
  
  uni.showToast({ title: '测试开始', icon: 'none' });
};

const stopTest = async () => {
  isTesting.value = false;
  clearInterval(timer);
  
  // 模拟测试结果
  const count = Math.floor(Math.random() * 20) + 5;
  const qualified = count >= 10;
  
  // 准备活动数据
  const activityData = {
    type: 'test',
    source: 'manual',
    started_at: new Date(Date.now() - testDuration.value * 1000).toISOString(),
    ended_at: new Date().toISOString(),
    metrics: {
      duration: testDuration.value,
      count: count,
      qualified: qualified,
      video_url: uploadedFile.value ? uploadedFile.value.url : null
    },
    evidence: []
  };
  
  try {
    // 提交活动数据
    uni.showLoading({ title: '提交中...' });
    const result = await submitActivity(activityData);
    
    testResult.value = {
      count,
      qualified,
      duration: testDuration.value,
      score: result.metrics?.score,
      score_detail: result.metrics?.score_detail ? JSON.parse(result.metrics.score_detail) : null
    };
    
    uni.hideLoading();
    uni.showToast({ title: '测试结束，数据已提交', icon: 'success' });
    
  } catch (error) {
    uni.hideLoading();
    console.error('Submit error:', error);
    
    // 即使提交失败，也显示本地结果
    testResult.value = {
      count,
      qualified,
      duration: testDuration.value
    };
    
    uni.showToast({ title: '测试结束，提交失败', icon: 'none' });
  }
};

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

onLoad(() => {
  uni.getSystemInfo({
    success: (res) => {
      statusBarHeight.value = res.statusBarHeight || 20;
    }
  });
});
</script>

<style lang="scss" scoped>
.test-container {
  min-height: 100vh;
  background-color: #1a1a1a;
}

.custom-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: #1a1a1a;
  z-index: 100;
}

.navbar-content {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 15px;
}

.navbar-left,
.navbar-right {
  width: 60rpx;
}

.back-icon {
  color: #fff;
  font-size: 40rpx;
}

.navbar-title {
  color: #fff;
  font-size: 18px;
  font-weight: bold;
}

.content-wrapper {
  padding: 20rpx;
}

.test-header {
  text-align: center;
  margin-bottom: 40rpx;
}

.test-title {
  font-size: 48rpx;
  color: #fff;
  font-weight: bold;
  display: block;
  margin-bottom: 20rpx;
}

.standard-badge {
  display: inline-block;
  padding: 8rpx 24rpx;
  background: rgba(32, 201, 151, 0.2);
  border: 2rpx solid #20C997;
  border-radius: 30rpx;
  margin-bottom: 20rpx;
}

.badge-text {
  color: #20C997;
  font-size: 24rpx;
}

.standard-desc {
  display: block;
  color: #999;
  font-size: 28rpx;
  margin-bottom: 30rpx;
}

.switch-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #20C997;
  border: 2rpx solid #20C997;
  border-radius: 40rpx;
  padding: 16rpx 48rpx;
  font-size: 28rpx;
}

.camera-area {
  width: 100%;
  height: 500rpx;
  background: #000;
  border-radius: 20rpx;
  overflow: hidden;
  margin-bottom: 40rpx;
}

.upload-area {
  width: 100%;
  height: 500rpx;
  background: #000;
  border-radius: 20rpx;
  overflow: hidden;
  margin-bottom: 40rpx;
}

.upload-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 2rpx dashed #20C997;
  cursor: pointer;
}

.upload-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.upload-text {
  color: #fff;
  font-size: 32rpx;
  margin-bottom: 10rpx;
}

.upload-hint {
  color: #999;
  font-size: 24rpx;
}

.upload-preview {
  width: 100%;
  height: 100%;
  position: relative;
}

.preview-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-actions {
  position: absolute;
  bottom: 20rpx;
  right: 20rpx;
}

.reupload-btn {
  background: rgba(32, 201, 151, 0.8);
  color: #fff;
  border: none;
  border-radius: 20rpx;
  padding: 10rpx 20rpx;
  font-size: 24rpx;
}

.h5-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
}

.placeholder-text {
  color: #fff;
  font-size: 32rpx;
  margin-bottom: 20rpx;
}

.placeholder-hint {
  color: #999;
  font-size: 24rpx;
}

.camera {
  width: 100%;
  height: 100%;
}

.test-controls {
  text-align: center;
  margin-bottom: 40rpx;
}

.timer-display {
  margin-bottom: 30rpx;
}

.timer-label {
  display: block;
  color: #999;
  font-size: 24rpx;
  margin-bottom: 10rpx;
}

.timer-value {
  display: block;
  color: #fff;
  font-size: 64rpx;
  font-weight: bold;
  font-family: 'Courier New', monospace;
}

.test-btn {
  width: 80%;
  height: 100rpx;
  background: #20C997;
  color: #fff;
  border-radius: 50rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
  
  &.active {
    background: #ff6b6b;
  }
}

.test-result {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20rpx;
  padding: 40rpx;
}

.result-title {
  display: block;
  color: #fff;
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 30rpx;
  text-align: center;
}

.result-data {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-count {
  color: #fff;
  font-size: 28rpx;
}

.result-status {
  color: #ff6b6b;
  font-size: 32rpx;
  font-weight: bold;
  
  &.qualified {
    color: #20C997;
  }
}

.ai-score {
  margin-top: 30rpx;
  padding-top: 30rpx;
  border-top: 2rpx solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.score-title {
  display: block;
  color: #20C997;
  font-size: 28rpx;
  margin-bottom: 10rpx;
}

.score-value {
  display: block;
  color: #fff;
  font-size: 48rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
}

.score-detail {
  display: block;
  color: #999;
  font-size: 24rpx;
}
</style>
