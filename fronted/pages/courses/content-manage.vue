<template>
  <view class="content-manage-container">
    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="nav-back" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="nav-title">课程内容管理</text>
      <view class="nav-action" @click="addContent">
        <text class="action-icon">+</text>
      </view>
    </view>

    <!-- 课程信息 -->
    <view class="course-info-card">
      <text class="course-title">{{ courseTitle }}</text>
      <text class="content-count">共 {{ contents.length }} 个内容</text>
    </view>

    <!-- 内容列表 -->
    <view class="content-list">
      <view 
        class="content-item" 
        v-for="(content, index) in contents" 
        :key="content.id"
      >
        <view class="content-index">{{ index + 1 }}</view>
        <view class="content-info">
          <text class="content-title">{{ content.title }}</text>
          <view class="content-meta">
            <text class="meta-type">{{ getTypeLabel(content.content_type) }}</text>
            <text class="meta-duration" v-if="content.duration">
              {{ formatDuration(content.duration) }}
            </text>
          </view>
        </view>
        <view class="content-actions">
          <view class="action-btn edit" @click="editContent(content)">
            <text>编辑</text>
          </view>
          <view class="action-btn delete" @click="deleteContent(content)">
            <text>删除</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-if="contents.length === 0 && !loading">
      <text class="empty-icon">📹</text>
      <text class="empty-text">还没有添加课程内容</text>
      <button class="add-btn" @click="addContent">添加内容</button>
    </view>

    <!-- 添加/编辑内容弹窗 -->
    <view class="popup-mask" v-if="showPopup" @click="closePopup"></view>
    <view class="popup-container" :class="{ show: showPopup }">
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">{{ editingContent ? '编辑内容' : '添加内容' }}</text>
          <view class="popup-close" @click="closePopup">
            <text>×</text>
          </view>
        </view>

        <view class="form-section">
          <view class="form-item">
            <text class="form-label">内容标题 <text class="required">*</text></text>
            <input 
              class="form-input" 
              v-model="contentForm.title" 
              placeholder="请输入内容标题"
            />
          </view>

          <view class="form-item">
            <text class="form-label">内容类型 <text class="required">*</text></text>
            <view class="type-selector">
              <view 
                class="type-option" 
                :class="{ active: contentForm.content_type === type.value }"
                v-for="type in contentTypes" 
                :key="type.value"
                @click="selectType(type.value)"
              >
                <text>{{ type.label }}</text>
              </view>
            </view>
          </view>

          <view class="form-item" v-if="contentForm.content_type === 'video'">
            <text class="form-label">视频文件 <text class="required">*</text></text>
            <view class="upload-section">
              <button class="upload-btn" @click="uploadVideo" :loading="uploading">
                {{ contentForm.content_url ? '重新上传' : '上传视频' }}
              </button>
              <text class="upload-hint" v-if="contentForm.content_url">
                ✓ 已上传
              </text>
            </view>
          </view>

          <view class="form-item" v-if="contentForm.content_type === 'link'">
            <text class="form-label">视频链接 <text class="required">*</text></text>
            <input 
              class="form-input" 
              v-model="contentForm.content_url" 
              placeholder="请输入视频链接（如B站、优酷等）"
            />
          </view>

          <view class="form-item" v-if="contentForm.content_type === 'document'">
            <text class="form-label">文档文件 <text class="required">*</text></text>
            <view class="upload-section">
              <button class="upload-btn" @click="uploadDocument" :loading="uploading">
                {{ contentForm.content_url ? '重新上传' : '上传文档' }}
              </button>
              <text class="upload-hint" v-if="contentForm.content_url">
                ✓ 已上传
              </text>
            </view>
          </view>

          <view class="form-item" v-if="contentForm.content_type === 'video'">
            <text class="form-label">视频时长（秒）</text>
            <input 
              class="form-input" 
              v-model.number="contentForm.duration" 
              type="number"
              placeholder="请输入视频时长"
            />
          </view>

          <view class="form-item">
            <text class="form-label">排序</text>
            <input 
              class="form-input" 
              v-model.number="contentForm.order" 
              type="number"
              placeholder="数字越小越靠前"
            />
          </view>
        </view>

        <view class="popup-actions">
          <button class="cancel-btn" @click="closePopup">取消</button>
          <button class="submit-btn" @click="saveContent" :loading="submitting">
            保存
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { request, uploadFile } from '@/utils/request.js';

const courseId = ref(null);
const courseTitle = ref('');
const contents = ref([]);
const loading = ref(false);
const uploading = ref(false);
const submitting = ref(false);
const editingContent = ref(null);
const showPopup = ref(false);

const contentTypes = [
  { label: '视频', value: 'video' },
  { label: '外部链接', value: 'link' },
  { label: '文档', value: 'document' }
];

const contentForm = ref({
  title: '',
  content_type: '',
  content_url: '',
  duration: null,
  order: 0
});

const selectedTypeIndex = computed(() => {
  return contentTypes.findIndex(t => t.value === contentForm.value.content_type);
});

const selectedTypeLabel = computed(() => {
  const type = contentTypes.find(t => t.value === contentForm.value.content_type);
  return type ? type.label : '';
});

const loadCourseInfo = async () => {
  try {
    const res = await request({
      url: `/courses/${courseId.value}`,
      method: 'GET'
    });
    courseTitle.value = res.title;
  } catch (e) {
    console.error('Failed to load course info:', e);
  }
};

const loadContents = async () => {
  loading.value = true;
  try {
    const res = await request({
      url: `/courses/${courseId.value}/contents`,
      method: 'GET'
    });
    contents.value = res;
  } catch (e) {
    console.error('Failed to load contents:', e);
    uni.showToast({ title: '加载失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
};

const getTypeLabel = (type) => {
  const typeObj = contentTypes.find(t => t.value === type);
  return typeObj ? typeObj.label : '未知';
};

const formatDuration = (seconds) => {
  if (!seconds) return '';
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
};

const addContent = () => {
  editingContent.value = null;
  contentForm.value = {
    title: '',
    content_type: '',
    content_url: '',
    duration: null,
    order: contents.value.length
  };
  showPopup.value = true;
};

const editContent = (content) => {
  editingContent.value = content;
  contentForm.value = {
    title: content.title,
    content_type: content.content_type,
    content_url: content.content_url,
    duration: content.duration,
    order: content.order
  };
  showPopup.value = true;
};

const selectType = (type) => {
  contentForm.value.content_type = type;
  // 切换类型时清空URL
  contentForm.value.content_url = '';
};

const onTypeChange = (e) => {
  contentForm.value.content_type = contentTypes[e.detail.value].value;
  // 切换类型时清空URL
  contentForm.value.content_url = '';
};

const uploadVideo = () => {
  // H5环境使用input[type=file]
  // #ifdef H5
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'video/*';
  input.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // 检查文件大小（100MB限制）
    if (file.size > 100 * 1024 * 1024) {
      uni.showModal({
        title: '文件过大',
        content: '视频大小不能超过100MB，请重新选择',
        showCancel: false
      });
      return;
    }
    
    // 上传视频
    uploading.value = true;
    uni.showLoading({ title: '上传中...', mask: true });
    
    try {
      // 创建FormData
      const formData = new FormData();
      formData.append('file', file);
      
      // 获取token
      const token = uni.getStorageSync('token');
      
      // 使用fetch上传
      const response = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('上传失败');
      }
      
      const result = await response.json();
      contentForm.value.content_url = result.url;
      
      // 尝试获取视频时长
      const video = document.createElement('video');
      video.preload = 'metadata';
      video.onloadedmetadata = () => {
        contentForm.value.duration = Math.floor(video.duration);
        URL.revokeObjectURL(video.src);
      };
      video.src = URL.createObjectURL(file);
      
      uni.hideLoading();
      uni.showToast({ title: '上传成功', icon: 'success' });
    } catch (e) {
      uni.hideLoading();
      console.error('Upload failed:', e);
      uni.showModal({
        title: '上传失败',
        content: e.message || '上传失败，请重试',
        showCancel: false
      });
    } finally {
      uploading.value = false;
    }
  };
  input.click();
  // #endif
  
  // #ifndef H5
  uni.chooseVideo({
    sourceType: ['album', 'camera'],
    maxDuration: 600, // 最长10分钟
    success: async (res) => {
      const tempFilePath = res.tempFilePath;
      const duration = Math.floor(res.duration);
      
      // 检查文件大小（100MB限制）
      uni.getFileInfo({
        filePath: tempFilePath,
        success: async (fileInfo) => {
          if (fileInfo.size > 100 * 1024 * 1024) {
            uni.showModal({
              title: '文件过大',
              content: '视频大小不能超过100MB，请重新选择',
              showCancel: false
            });
            return;
          }
          
          // 上传视频
          uploading.value = true;
          uni.showLoading({ title: '上传中...', mask: true });
          
          try {
            const uploadRes = await uploadFile(tempFilePath, 'video');
            contentForm.value.content_url = uploadRes.url;
            contentForm.value.duration = duration;
            
            uni.hideLoading();
            uni.showToast({ title: '上传成功', icon: 'success' });
          } catch (e) {
            uni.hideLoading();
            console.error('Upload failed:', e);
            uni.showModal({
              title: '上传失败',
              content: e.message || '上传失败，请重试',
              showCancel: false
            });
          } finally {
            uploading.value = false;
          }
        }
      });
    }
  });
  // #endif
};

const uploadDocument = () => {
  // 注意：uni-app的chooseFile在H5端可能不支持，建议使用input[type=file]
  uni.showModal({
    title: '提示',
    content: '文档上传功能开发中，请使用外部链接方式',
    showCancel: false
  });
};

const validateForm = () => {
  if (!contentForm.value.title.trim()) {
    uni.showToast({ title: '请输入内容标题', icon: 'none' });
    return false;
  }
  if (!contentForm.value.content_type) {
    uni.showToast({ title: '请选择内容类型', icon: 'none' });
    return false;
  }
  if (!contentForm.value.content_url) {
    uni.showToast({ title: '请上传文件或输入链接', icon: 'none' });
    return false;
  }
  return true;
};

const saveContent = async () => {
  if (!validateForm()) return;
  
  submitting.value = true;
  try {
    if (editingContent.value) {
      // 编辑内容（需要后端支持）
      uni.showToast({ title: '编辑功能开发中', icon: 'none' });
    } else {
      // 添加新内容
      await request({
        url: `/courses/${courseId.value}/contents`,
        method: 'POST',
        data: contentForm.value
      });
      
      uni.showToast({ title: '添加成功', icon: 'success' });
      closePopup();
      loadContents();
    }
  } catch (e) {
    console.error('Save content failed:', e);
    uni.showModal({
      title: '保存失败',
      content: e.message || '保存失败，请重试',
      showCancel: false
    });
  } finally {
    submitting.value = false;
  }
};

const deleteContent = (content) => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除"${content.title}"吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          // 删除内容（需要后端支持）
          uni.showToast({ title: '删除功能开发中', icon: 'none' });
        } catch (e) {
          console.error('Delete failed:', e);
          uni.showToast({ title: '删除失败', icon: 'none' });
        }
      }
    }
  });
};

const closePopup = () => {
  showPopup.value = false;
};

const goBack = () => {
  uni.navigateBack();
};

onLoad((options) => {
  if (options.courseId) {
    courseId.value = options.courseId;
    loadCourseInfo();
    loadContents();
  }
});
</script>

<style lang="scss" scoped>
.content-manage-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 40rpx;
}

.nav-bar {
  background: #fff;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30rpx;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}

.nav-back, .nav-action {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  font-size: 40rpx;
  color: #333;
}

.nav-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.action-icon {
  font-size: 48rpx;
  color: #20C997;
}

.course-info-card {
  background: #fff;
  padding: 30rpx;
  margin: 20rpx 30rpx;
  border-radius: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}

.course-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 12rpx;
}

.content-count {
  font-size: 26rpx;
  color: #999;
}

.content-list {
  padding: 0 30rpx;
}

.content-item {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
}

.content-index {
  width: 60rpx;
  height: 60rpx;
  background: #f5f7fa;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #666;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.content-info {
  flex: 1;
  min-width: 0;
}

.content-title {
  font-size: 28rpx;
  color: #333;
  display: block;
  margin-bottom: 12rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.content-meta {
  display: flex;
  gap: 20rpx;
}

.meta-type {
  padding: 4rpx 16rpx;
  background: #e3f2fd;
  color: #2196f3;
  font-size: 22rpx;
  border-radius: 8rpx;
}

.meta-duration {
  font-size: 22rpx;
  color: #999;
}

.content-actions {
  display: flex;
  gap: 16rpx;
  flex-shrink: 0;
}

.action-btn {
  padding: 12rpx 24rpx;
  border-radius: 8rpx;
  font-size: 24rpx;
  
  &.edit {
    background: #20C997;
    color: #fff;
  }
  
  &.delete {
    background: #f5f7fa;
    color: #ff6b6b;
  }
}

.empty-state {
  padding: 200rpx 60rpx;
  text-align: center;
}

.empty-icon {
  font-size: 120rpx;
  display: block;
  margin-bottom: 30rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
  display: block;
  margin-bottom: 40rpx;
}

.add-btn {
  width: 300rpx;
  height: 80rpx;
  background: #20C997;
  color: #fff;
  border-radius: 40rpx;
  font-size: 28rpx;
  border: none;
}

.popup-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

.popup-container {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  transform: translateY(100%);
  transition: transform 0.3s;
  
  &.show {
    transform: translateY(0);
  }
}

.popup-content {
  background: #fff;
  border-radius: 40rpx 40rpx 0 0;
  max-height: 80vh;
  overflow-y: auto;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.popup-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.popup-close {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 60rpx;
  color: #999;
}

.form-section {
  padding: 30rpx;
}

.form-item {
  margin-bottom: 30rpx;
}

.form-label {
  display: block;
  font-size: 28rpx;
  color: #333;
  margin-bottom: 16rpx;
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

.type-selector {
  display: flex;
  gap: 20rpx;
}

.type-option {
  flex: 1;
  height: 88rpx;
  background: #f5f7fa;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  color: #666;
  transition: all 0.3s;
  
  &.active {
    background: #20C997;
    color: #fff;
  }
}

.upload-section {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.upload-btn {
  flex: 1;
  height: 88rpx;
  background: #20C997;
  color: #fff;
  border-radius: 12rpx;
  font-size: 28rpx;
  border: none;
}

.upload-hint {
  font-size: 26rpx;
  color: #4caf50;
}

.popup-actions {
  display: flex;
  gap: 20rpx;
  padding: 30rpx;
  border-top: 1rpx solid #f0f0f0;
}

.cancel-btn,
.submit-btn {
  flex: 1;
  height: 88rpx;
  border-radius: 44rpx;
  font-size: 30rpx;
  border: none;
}

.cancel-btn {
  background: #f5f7fa;
  color: #666;
}

.submit-btn {
  background: #20C997;
  color: #fff;
}
</style>
