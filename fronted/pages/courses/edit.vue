<template>
  <view class="edit-container">
    <view class="form-card" v-if="!loading">
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
          :value="categoryIndex"
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

    <view class="loading-state" v-if="loading">
      <text class="loading-text">加载中...</text>
    </view>

    <view class="action-bar" v-if="!loading">
      <button class="cancel-btn" @click="goBack">取消</button>
      <button class="submit-btn" @click="handleSubmit" :loading="submitting">保存修改</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { request, updateCourse, uploadFile } from '@/utils/request.js';

const categories = [
  { label: '技能课', value: 'skill' },
  { label: '理论课', value: 'theory' },
  { label: '体能课', value: 'fitness' }
];

const courseId = ref(0);
const loading = ref(true);
const submitting = ref(false);

const form = ref({
  title: '',
  description: '',
  cover_url: '',
  category: '',
  is_public: true
});

const categoryIndex = computed(() => {
  return categories.findIndex(c => c.value === form.value.category);
});

const selectedCategoryLabel = computed(() => {
  const cat = categories.find(c => c.value === form.value.category);
  return cat ? cat.label : '';
});

const loadCourseDetail = async () => {
  loading.value = true;
  try {
    const res = await request({
      url: `/courses/${courseId.value}`,
      method: 'GET'
    });
    
    form.value = {
      title: res.title,
      description: res.description || '',
      cover_url: res.cover_url || '',
      category: res.category || '',
      is_public: res.is_public !== false
    };
  } catch (e) {
    console.error('Load course failed:', e);
    uni.showToast({ title: '加载失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
};

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
      
      uni.showLoading({ title: '上传中...' });
      try {
        const uploadRes = await uploadFile(tempFilePath, 'image');
        form.value.cover_url = uploadRes.url;
        uni.hideLoading();
        uni.showToast({ title: '上传成功', icon: 'success' });
      } catch (e) {
        uni.hideLoading();
        console.error('Upload failed:', e);
      }
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
    await updateCourse(courseId.value, form.value);
    uni.showToast({ 
      title: '保存成功', 
      icon: 'success',
      duration: 1500
    });
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  } catch (e) {
    console.error('Update course failed:', e);
    submitting.value = false;
  }
};

const goBack = () => {
  uni.navigateBack();
};

onLoad((options) => {
  if (options.id) {
    courseId.value = parseInt(options.id);
    uni.setNavigationBarTitle({ title: '编辑课程' });
    loadCourseDetail();
  } else {
    uni.showToast({ title: '参数错误', icon: 'none' });
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  }
});
</script>

<style lang="scss" scoped>
.edit-container {
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

.loading-state {
  padding: 100rpx 0;
  text-align: center;
}

.loading-text {
  font-size: 28rpx;
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
