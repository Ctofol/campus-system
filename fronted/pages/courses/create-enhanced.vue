<template>
  <view class="create-container">
    <!-- 自定义导航栏 -->
    <view class="custom-nav-bar">
      <view class="nav-status-bar"></view>
      <view class="nav-content">
        <view class="nav-back" @click="goBack">
          <text class="back-icon">‹</text>
        </view>
        <text class="nav-title">发布课程</text>
        <view class="nav-placeholder"></view>
      </view>
    </view>

    <scroll-view class="content-wrapper" scroll-y>
      <view class="form-card">
        <!-- 课程名称 -->
        <view class="form-item">
          <text class="form-label">课程名称 <text class="required">*</text></text>
          <input 
            class="form-input" 
            v-model="form.title" 
            placeholder="请输入课程名称（最多50字）"
            maxlength="50"
          />
          <text class="char-count">{{ form.title.length }}/50</text>
        </view>

        <!-- 课程类型 -->
        <view class="form-item">
          <text class="form-label">课程类型 <text class="required">*</text></text>
          <picker 
            mode="selector" 
            :range="categories" 
            range-key="label"
            @change="onCategoryChange"
          >
            <view class="picker-view">
              <text :class="form.category ? 'selected' : 'placeholder'">
                {{ selectedCategoryLabel || '请选择课程类型' }}
              </text>
              <text class="arrow">›</text>
            </view>
          </picker>
        </view>

        <!-- 课程封面 -->
        <view class="form-item">
          <text class="form-label">课程封面 <text class="required">*</text></text>
          <text class="form-hint">支持jpg/png格式，大小不超过2MB</text>
          <view class="cover-upload" @click="uploadCover">
            <image 
              v-if="form.cover_url" 
              class="cover-preview" 
              :src="form.cover_url" 
              mode="aspectFill"
            ></image>
            <view v-else class="upload-placeholder">
              <text class="upload-icon">📷</text>
              <text class="upload-text">点击上传封面图</text>
            </view>
          </view>
        </view>

        <!-- 课程简介 -->
        <view class="form-item">
          <text class="form-label">课程简介 <text class="required">*</text></text>
          <textarea 
            class="form-textarea" 
            v-model="form.description" 
            placeholder="请输入课程简介（最多200字）"
            maxlength="200"
          />
          <text class="char-count">{{ form.description.length }}/200</text>
        </view>

        <!-- 课程内容（富文本） -->
        <view class="form-item">
          <text class="form-label">课程内容 <text class="required">*</text></text>
          <text class="form-hint">支持插入图片和视频链接</text>
          
          <!-- 富文本编辑器 -->
          <view class="editor-container">
            <editor 
              id="editor" 
              class="ql-container"
              placeholder="请输入课程详细内容..."
              @ready="onEditorReady"
              @input="onEditorInput"
              show-img-size
              show-img-toolbar
              show-img-resize
            ></editor>
          </view>

          <!-- 编辑器工具栏 -->
          <view class="editor-toolbar">
            <view class="toolbar-btn" @click="insertImage">
              <text class="btn-icon">🖼️</text>
              <text class="btn-text">图片</text>
            </view>
            <view class="toolbar-btn" @click="insertVideo">
              <text class="btn-icon">🎬</text>
              <text class="btn-text">视频</text>
            </view>
            <view class="toolbar-btn" @click="formatBold">
              <text class="btn-icon">B</text>
            </view>
            <view class="toolbar-btn" @click="formatItalic">
              <text class="btn-icon">I</text>
            </view>
          </view>
        </view>

        <!-- 参与人数上限 -->
        <view class="form-item">
          <text class="form-label">参与人数上限</text>
          <input 
            class="form-input" 
            v-model.number="form.max_enrollment" 
            type="number"
            placeholder="请输入人数上限（1-1000）"
          />
          <text class="form-hint">不填则不限制人数</text>
        </view>

        <!-- 公开设置 -->
        <view class="form-item">
          <view class="form-switch">
            <view>
              <text class="form-label">公开课程</text>
              <text class="form-hint">公开后所有学生可见</text>
            </view>
            <switch 
              :checked="form.is_public" 
              @change="onPublicChange"
              color="#20C997"
            />
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 底部操作栏 -->
    <view class="action-bar">
      <button class="cancel-btn" @click="goBack">取消</button>
      <button class="submit-btn" @click="handleSubmit" :loading="submitting">发布课程</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onLoad, onReady } from '@dcloudio/uni-app';
import { createCourse, uploadFile } from '@/utils/request.js';

// 课程分类
const categories = [
  { label: '技能课', value: 'skill' },
  { label: '理论课', value: 'theory' },
  { label: '体能课', value: 'fitness' }
];

// 表单数据
const form = ref({
  title: '',
  description: '',
  cover_url: '',
  category: '',
  content: '',  // 富文本内容
  max_enrollment: null,
  is_public: true
});

const submitting = ref(false);
let editorCtx = null;

// 计算属性：选中的分类标签
const selectedCategoryLabel = computed(() => {
  const cat = categories.find(c => c.value === form.value.category);
  return cat ? cat.label : '';
});

// 分类选择
const onCategoryChange = (e) => {
  form.value.category = categories[e.detail.value].value;
};

// 公开设置
const onPublicChange = (e) => {
  form.value.is_public = e.detail.value;
};

// 编辑器准备完成
const onEditorReady = () => {
  uni.createSelectorQuery().select('#editor').context((res) => {
    editorCtx = res.context;
  }).exec();
};

// 编辑器内容变化
const onEditorInput = (e) => {
  form.value.content = e.detail.html;
};

// 上传封面图
const uploadCover = () => {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const tempFilePath = res.tempFilePaths[0];
      
      // 获取文件信息验证大小
      uni.getFileInfo({
        filePath: tempFilePath,
        success: async (fileInfo) => {
          // 检查文件大小（2MB = 2 * 1024 * 1024 bytes）
          if (fileInfo.size > 2 * 1024 * 1024) {
            uni.showToast({ 
              title: '封面图大小不能超过2MB', 
              icon: 'none',
              duration: 2000
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
            console.error('Upload cover failed:', e);
            uni.showModal({
              title: '上传失败',
              content: e.message || '封面图上传失败，请重试',
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

// 插入图片到编辑器
const insertImage = () => {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const tempFilePath = res.tempFilePaths[0];
      
      // 验证文件大小
      uni.getFileInfo({
        filePath: tempFilePath,
        success: async (fileInfo) => {
          if (fileInfo.size > 5 * 1024 * 1024) {
            uni.showToast({ 
              title: '图片大小不能超过5MB', 
              icon: 'none',
              duration: 2000
            });
            return;
          }
          
          // 上传图片
          uni.showLoading({ title: '上传中...', mask: true });
          try {
            const uploadRes = await uploadFile(tempFilePath, 'image');
            
            // 插入到编辑器
            if (editorCtx) {
              editorCtx.insertImage({
                src: uploadRes.url,
                width: '100%',
                success: () => {
                  uni.hideLoading();
                  uni.showToast({ title: '插入成功', icon: 'success' });
                }
              });
            }
          } catch (e) {
            uni.hideLoading();
            console.error('Upload image failed:', e);
            uni.showModal({
              title: '上传失败',
              content: e.message || '图片上传失败，请重试',
              showCancel: false
            });
          }
        }
      });
    }
  });
};

// 插入视频链接
const insertVideo = () => {
  uni.showModal({
    title: '插入视频',
    content: '请输入视频链接地址',
    editable: true,
    placeholderText: 'https://example.com/video.mp4',
    success: (res) => {
      if (res.confirm && res.content) {
        const videoUrl = res.content.trim();
        
        // 简单验证URL格式
        if (!videoUrl.startsWith('http://') && !videoUrl.startsWith('https://')) {
          uni.showToast({ title: '请输入有效的视频链接', icon: 'none' });
          return;
        }
        
        // 插入视频HTML
        if (editorCtx) {
          const videoHtml = `<video src="${videoUrl}" controls style="width:100%;"></video>`;
          editorCtx.insertText({
            text: '\n'
          });
          // 注意：uni-app的editor组件不直接支持insertHTML，这里用文本方式插入链接
          editorCtx.insertText({
            text: `[视频] ${videoUrl}\n`
          });
          uni.showToast({ title: '视频链接已插入', icon: 'success' });
        }
      }
    }
  });
};

// 格式化：加粗
const formatBold = () => {
  if (editorCtx) {
    editorCtx.format('bold');
  }
};

// 格式化：斜体
const formatItalic = () => {
  if (editorCtx) {
    editorCtx.format('italic');
  }
};

// 表单验证
const validateForm = () => {
  // 课程名称
  if (!form.value.title.trim()) {
    uni.showToast({ title: '请输入课程名称', icon: 'none' });
    return false;
  }
  if (form.value.title.length > 50) {
    uni.showToast({ title: '课程名称不能超过50字', icon: 'none' });
    return false;
  }
  
  // 课程类型
  if (!form.value.category) {
    uni.showToast({ title: '请选择课程类型', icon: 'none' });
    return false;
  }
  
  // 课程封面
  if (!form.value.cover_url) {
    uni.showToast({ title: '请上传课程封面', icon: 'none' });
    return false;
  }
  
  // 课程简介
  if (!form.value.description.trim()) {
    uni.showToast({ title: '请输入课程简介', icon: 'none' });
    return false;
  }
  if (form.value.description.length > 200) {
    uni.showToast({ title: '课程简介不能超过200字', icon: 'none' });
    return false;
  }
  
  // 课程内容
  if (!form.value.content || form.value.content.trim() === '<p><br></p>') {
    uni.showToast({ title: '请输入课程内容', icon: 'none' });
    return false;
  }
  
  // 参与人数上限
  if (form.value.max_enrollment !== null && form.value.max_enrollment !== '') {
    const num = Number(form.value.max_enrollment);
    if (isNaN(num) || num < 1 || num > 1000) {
      uni.showToast({ title: '参与人数上限应在1-1000之间', icon: 'none' });
      return false;
    }
  }
  
  return true;
};

// 提交表单
const handleSubmit = async () => {
  if (!validateForm()) return;
  
  submitting.value = true;
  
  try {
    // 准备提交数据
    const submitData = {
      title: form.value.title.trim(),
      description: form.value.description.trim(),
      cover_url: form.value.cover_url,
      category: form.value.category,
      is_public: form.value.is_public
    };
    
    // 可选字段
    if (form.value.max_enrollment) {
      submitData.max_enrollment = Number(form.value.max_enrollment);
    }
    
    // 调用创建接口
    await createCourse(submitData);
    
    uni.showToast({ 
      title: '发布成功', 
      icon: 'success',
      duration: 1500
    });
    
    // 延迟跳转，让用户看到成功提示
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
    
    // 错误处理
    let errorMsg = '发布失败，请重试';
    if (e.message) {
      errorMsg = e.message;
    } else if (e.type === 'network') {
      errorMsg = '网络连接失败，请检查网络';
    } else if (e.statusCode === 400) {
      errorMsg = '提交数据格式错误';
    } else if (e.statusCode === 401) {
      errorMsg = '登录已过期，请重新登录';
    } else if (e.statusCode === 403) {
      errorMsg = '没有权限发布课程';
    }
    
    uni.showModal({
      title: '发布失败',
      content: errorMsg,
      showCancel: false
    });
    
    submitting.value = false;
  }
};

// 返回
const goBack = () => {
  if (form.value.title || form.value.description || form.value.cover_url) {
    uni.showModal({
      title: '确认退出',
      content: '当前内容未保存，确定要退出吗？',
      success: (res) => {
        if (res.confirm) {
          uni.navigateBack();
        }
      }
    });
  } else {
    uni.navigateBack();
  }
};

onLoad(() => {
  // 页面加载时的初始化
});

onReady(() => {
  // 页面渲染完成
});
</script>

<style lang="scss" scoped>
.create-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.custom-nav-bar {
  background-color: #fff;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
  
  .nav-status-bar {
    height: var(--status-bar-height);
  }
  
  .nav-content {
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 30rpx;
    
    .nav-back {
      width: 60rpx;
      height: 60rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      
      .back-icon {
        font-size: 48rpx;
        color: #333;
        font-weight: bold;
      }
    }
    
    .nav-title {
      font-size: 18px;
      font-weight: bold;
      color: #333;
    }
    
    .nav-placeholder {
      width: 60rpx;
    }
  }
}

.content-wrapper {
  padding-top: calc(var(--status-bar-height) + 44px);
  padding-bottom: 160rpx;
  height: 100vh;
}

.form-card {
  background: #fff;
  margin: 30rpx;
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
  margin-bottom: 16rpx;
}

.required {
  color: #ff6b6b;
}

.form-hint {
  display: block;
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
  margin-bottom: 16rpx;
}

.char-count {
  display: block;
  font-size: 24rpx;
  color: #999;
  text-align: right;
  margin-top: 8rpx;
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
  transform: rotate(90deg);
}

.cover-upload {
  width: 100%;
  height: 360rpx;
  border-radius: 12rpx;
  overflow: hidden;
  background: #f5f7fa;
  border: 2rpx dashed #ddd;
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

.editor-container {
  width: 100%;
  min-height: 400rpx;
  background: #f5f7fa;
  border-radius: 12rpx;
  overflow: hidden;
  margin-bottom: 20rpx;
}

.ql-container {
  width: 100%;
  min-height: 400rpx;
  padding: 24rpx;
  box-sizing: border-box;
}

.editor-toolbar {
  display: flex;
  gap: 20rpx;
  padding: 20rpx;
  background: #fff;
  border-radius: 12rpx;
  border: 2rpx solid #f0f0f0;
}

.toolbar-btn {
  flex: 1;
  height: 80rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 12rpx;
  
  &:active {
    background: #e9ecef;
  }
}

.btn-icon {
  font-size: 32rpx;
  margin-bottom: 4rpx;
}

.btn-text {
  font-size: 22rpx;
  color: #666;
}

.form-switch {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  z-index: 99;
}

.cancel-btn,
.submit-btn {
  flex: 1;
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 44rpx;
  font-size: 30rpx;
  margin: 0;
  border: none;
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
