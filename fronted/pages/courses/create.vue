<template>
  <view class="create-container">
    <view class="form-card">
      <view class="form-item">
        <text class="form-label">课程标题 <text class="required">*</text></text>
        <input 
          class="form-input" 
          v-model="form.title" 
          placeholder="请输入课程标题"
          maxlength="50"
        />
      </view>

      <view class="form-item">
        <text class="form-label">课程分类 <text class="required">*</text></text>
        <picker 
          mode="selector" 
          :range="categories" 
          range-key="label"
          @change="onCategoryChange"
        >
          <view class="picker-view">
            <text :class="form.category ? 'selected' : 'placeholder'">
              {{ selectedCategoryLabel || '请选择课程分类' }}
            </text>
            <text class="arrow">›</text>
          </view>
        </picker>
      </view>

      <view class="form-item">
        <text class="form-label">课程封面</text>
        <view class="cover-upload" @click="uploadCover">
          <image 
            v-if="form.cover_url" 
            class="cover-preview" 
            :src="form.cover_url" 
            mode="aspectFill"
          ></image>
          <view v-else class="upload-placeholder">
            <text class="upload-icon">+</text>
            <text class="upload-text">上传封面</text>
          </view>
        </view>
      </view>

      <view class="form-item">
        <text class="form-label">课程描述</text>
        <textarea 
          class="form-textarea" 
          v-model="form.description" 
          placeholder="请输入课程描述"
          maxlength="500"
        />
      </view>

      <view class="form-item">
        <view class="form-switch">
          <text class="form-label">公开课程</text>
          <switch 
            :checked="form.is_public" 
            @change="onPublicChange"
            color="#20C997"
          />
        </view>
        <text class="form-hint">公开后所有学生可见</text>
      </view>
    </view>

    <view class="action-bar">
      <button class="cancel-btn" @click="goBack">取消</button>
      <button class="submit-btn" @click="handleSubmit" :loading="submitting">创建课程</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { createCourse, uploadFile } from '@/utils/request.js';

const categories = [
  { label: '技能课', value: 'skill' },
  { label: '理论课', value: 'theory' },
  { label: '体能课', value: 'fitness' }
];

const form = ref({
  title: '',
  description: '',
  cover_url: '',
  category: '',
  is_public: true
});

const submitting = ref(false);

const selectedCategoryLabel = computed(() => {
  const cat = categories.find(c => c.value === form.value.category);
  return cat ? cat.label : '';
});

const onCategoryChange = (e) => {
  form.value.category = categories[e.detail.value].value;
};

const onPublicChange = (e) => {
  form.value.is_public = e.detail.value;
};

const uploadCover = () => {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const tempFilePath = res.tempFilePaths[0];
      
      // 验证文件大小和格式
      uni.getFileInfo({
        filePath: tempFilePath,
        success: async (fileInfo) => {
          // 检查文件大小（2MB = 2 * 1024 * 1024 bytes）
          if (fileInfo.size > 2 * 1024 * 1024) {
            uni.showModal({
              title: '文件过大',
              content: '封面图大小不能超过2MB，请重新选择',
              showCancel: false
            });
            return;
          }
          
          // 上传文件
          uni.showLoading({ title: '上传中...', mask: true });
          try {
            const uploadRes = await uploadFile(tempFilePath, 'image');
            form.value.cover_url = uploadRes.url;
            uni.hideLoading();
            uni.showToast({ title: '上传成功', icon: 'success' });
          } catch (e) {
            uni.hideLoading();
            console.error('Upload failed:', e);
            
            // 详细的错误提示
            let errorMsg = '上传失败，请重试';
            if (e.message) {
              errorMsg = e.message;
            } else if (e.type === 'network') {
              errorMsg = '网络连接失败，请检查网络';
            } else if (e.statusCode === 413) {
              errorMsg = '文件过大，服务器拒绝接收';
            } else if (e.statusCode === 415) {
              errorMsg = '文件格式不支持，请上传jpg或png格式';
            }
            
            uni.showModal({
              title: '上传失败',
              content: errorMsg,
              showCancel: false
            });
          }
        },
        fail: () => {
          uni.showToast({ title: '获取文件信息失败', icon: 'none' });
        }
      });
    }
  });
};

const validateForm = () => {
  if (!form.value.title.trim()) {
    uni.showToast({ title: '请输入课程标题', icon: 'none' });
    return false;
  }
  if (!form.value.category) {
    uni.showToast({ title: '请选择课程分类', icon: 'none' });
    return false;
  }
  return true;
};

const handleSubmit = async () => {
  if (!validateForm()) return;
  
  submitting.value = true;
  try {
    await createCourse(form.value);
    uni.showToast({ 
      title: '创建成功', 
      icon: 'success',
      duration: 1500
    });
    setTimeout(() => {
      uni.navigateBack({
        success: () => {
          // 通知列表页刷新
          uni.$emit('courseCreated');
        }
      });
    }, 1500);
  } catch (e) {
    console.error('Create course failed:', e);
    
    // 详细的错误处理
    let errorMsg = '创建失败，请重试';
    if (e.message) {
      errorMsg = e.message;
    } else if (e.type === 'network') {
      errorMsg = '网络连接失败，请检查网络';
    } else if (e.statusCode === 400) {
      errorMsg = '提交数据格式错误，请检查表单';
    } else if (e.statusCode === 401) {
      errorMsg = '登录已过期，请重新登录';
    } else if (e.statusCode === 403) {
      errorMsg = '没有权限创建课程';
    }
    
    uni.showModal({
      title: '创建失败',
      content: errorMsg,
      showCancel: false
    });
    
    submitting.value = false;
  }
};

const goBack = () => {
  uni.navigateBack();
};

onLoad(() => {
  uni.setNavigationBarTitle({ title: '创建课程' });
});
</script>

<style lang="scss" scoped>
.create-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 30rpx;
  padding-bottom: 160rpx;
}

.form-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 40rpx;
}

.form-item {
  margin-bottom: 40rpx;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.form-label {
  display: block;
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
  margin-bottom: 20rpx;
}

.required {
  color: #ff6b6b;
}

.form-input {
  width: 100%;
  height: 88rpx;
  background: #f5f7fa;
  border-radius: 12rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #333;
  box-sizing: border-box;
}

.picker-view {
  width: 100%;
  height: 88rpx;
  background: #f5f7fa;
  border-radius: 12rpx;
  padding: 0 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
}

.selected {
  font-size: 28rpx;
  color: #333;
}

.placeholder {
  font-size: 28rpx;
  color: #999;
}

.arrow {
  font-size: 40rpx;
  color: #999;
}

.cover-upload {
  width: 100%;
  height: 360rpx;
  border-radius: 12rpx;
  overflow: hidden;
  background: #f5f7fa;
}

.cover-preview {
  width: 100%;
  height: 100%;
}

.upload-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.upload-icon {
  font-size: 80rpx;
  color: #ccc;
  margin-bottom: 16rpx;
}

.upload-text {
  font-size: 26rpx;
  color: #999;
}

.form-textarea {
  width: 100%;
  min-height: 200rpx;
  background: #f5f7fa;
  border-radius: 12rpx;
  padding: 24rpx;
  font-size: 28rpx;
  color: #333;
  box-sizing: border-box;
}

.form-switch {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.form-hint {
  font-size: 24rpx;
  color: #999;
}

.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 30rpx;
  box-shadow: 0 -4rpx 16rpx rgba(0,0,0,0.05);
  display: flex;
  gap: 20rpx;
}

.cancel-btn,
.submit-btn {
  flex: 1;
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 44rpx;
  font-size: 30rpx;
  margin: 0;
}

.cancel-btn {
  background: #f5f7fa;
  color: #666;
}

.submit-btn {
  background: linear-gradient(90deg, #20C997, #17a2b8);
  color: #fff;
}
</style>
