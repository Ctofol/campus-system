<template>
  <view class="content-manage-container">
    <page-tab-header title="课程内容管理" show-back theme="white">
      <template #right>
        <view class="page-tab-header-icon-action" @click="addContent">
          <text class="action-icon">+</text>
        </view>
      </template>
    </page-tab-header>

    <view class="page-tab-body">
      <view class="course-info-card">
        <text class="course-title">{{ courseTitle || '课程内容' }}</text>
        <text class="content-count">共 {{ contents.length }} 个内容</text>
      </view>

      <view class="content-list" v-if="contents.length > 0">
        <view
          class="content-item"
          v-for="(content, index) in contents"
          :key="content.id"
        >
          <view class="content-index">{{ index + 1 }}</view>
          <view class="content-info">
            <text class="content-title">{{ content.title }}</text>
            <view class="content-meta">
              <text class="meta-type" :class="'meta-type--' + content.content_type">
                {{ getTypeLabel(content.content_type) }}
              </text>
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

      <view class="empty-state" v-if="contents.length === 0 && !loading">
        <image class="empty-icon-img" src="/static/icons/icon-notification.svg" mode="aspectFit" />
        <text class="empty-text">还没有添加课程内容</text>
        <button class="add-btn" @click="addContent">添加内容</button>
      </view>

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
                  {{ contentForm.content_url ? '重新上传视频' : '上传视频' }}
                </button>
                <view class="upload-hint" v-if="contentForm.content_url">
                  <image class="upload-hint-img" src="/static/icons/icon-check.svg" mode="aspectFit" />
                  <text>已上传</text>
                </view>
              </view>
              <text class="form-hint">支持 MP4 视频，建议单个文件不超过 500MB。上传完成后再点击保存。</text>
            </view>

            <view class="form-item" v-if="contentForm.content_type === 'link'">
              <text class="form-label">外部链接 <text class="required">*</text></text>
              <input
                class="form-input"
                v-model="contentForm.content_url"
                placeholder="粘贴视频、文档或网页链接"
              />
              <text class="form-hint">App 端会复制链接到剪贴板，学生可在浏览器或其他应用打开。</text>
            </view>

            <view class="form-item" v-if="contentForm.content_type === 'document'">
              <text class="form-label">文档文件 <text class="required">*</text></text>
              <view class="upload-section">
                <button class="upload-btn" @click="uploadDocument" :loading="uploading">
                  {{ contentForm.content_url ? '重新上传' : '上传文档' }}
                </button>
                <view class="upload-hint" v-if="contentForm.content_url">
                  <image class="upload-hint-img" src="/static/icons/icon-check.svg" mode="aspectFit" />
                  <text>已上传</text>
                </view>
              </view>
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
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad, onShow } from '@dcloudio/uni-app';
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
  { label: '视频课时', value: 'video' },
  { label: '外部链接', value: 'link' },
  { label: '文档', value: 'document' }
];

const createEmptyForm = () => ({
  title: '',
  content_type: 'video',
  content_url: '',
  duration: null,
  order: contents.value.length
});

const contentForm = ref(createEmptyForm());

const loadCourseInfo = async () => {
  try {
    const res = await request({
      url: `/courses/${courseId.value}`,
      method: 'GET'
    });
    courseTitle.value = res.title || '';
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
    contents.value = Array.isArray(res) ? res : [];
  } catch (e) {
    console.error('Failed to load contents:', e);
    uni.showToast({ title: '加载失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
};

const getTypeLabel = (type) => {
  const typeObj = contentTypes.find(t => t.value === type);
  return typeObj ? typeObj.label : '内容';
};

const formatDuration = (seconds) => {
  const total = Math.max(0, Number(seconds) || 0);
  const minutes = Math.floor(total / 60);
  const secs = total % 60;
  return `${minutes}:${String(secs).padStart(2, '0')}`;
};

const addContent = () => {
  editingContent.value = null;
  contentForm.value = createEmptyForm();
  showPopup.value = true;
};

const editContent = (content) => {
  editingContent.value = content;
  contentForm.value = {
    title: content.title || '',
    content_type: content.content_type || 'video',
    content_url: content.content_url || '',
    duration: content.duration || null,
    order: content.order ?? contents.value.length
  };
  showPopup.value = true;
};

const selectType = (type) => {
  if (contentForm.value.content_type === type) return;
  contentForm.value.content_type = type;
  contentForm.value.content_url = '';
  contentForm.value.duration = null;
};

const uploadVideo = () => {
  uni.chooseVideo({
    sourceType: ['album', 'camera'],
    compressed: false,
    maxDuration: 600,
    success: async (res) => {
      const tempFilePath = res.tempFilePath || res.tempFile;
      if (!tempFilePath) {
        uni.showToast({ title: '未选择视频', icon: 'none' });
        return;
      }

      uploading.value = true;
      try {
        const uploaded = await uploadFile(tempFilePath, 'video');
        contentForm.value.content_url = uploaded.url;
        contentForm.value.duration = Math.max(1, Math.round(Number(res.duration) || 0)) || null;
        if (!contentForm.value.title) {
          contentForm.value.title = uploaded.original_filename || '视频课时';
        }
        uni.showToast({ title: '视频上传成功', icon: 'success' });
      } catch (e) {
        console.error('Upload video failed:', e);
        uni.showToast({ title: e.message || '视频上传失败', icon: 'none' });
      } finally {
        uploading.value = false;
      }
    },
    fail: (err) => {
      if (err && String(err.errMsg || '').includes('cancel')) return;
      uni.showToast({ title: '选择视频失败', icon: 'none' });
    }
  });
};

const uploadDocument = () => {
  uni.showModal({
    title: '提示',
    content: '当前版本暂不支持直接上传文档，请选择“外部链接”类型粘贴文档或网盘地址。',
    showCancel: false
  });
};

const validateForm = () => {
  if (!String(contentForm.value.title || '').trim()) {
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
    const payload = {
      title: String(contentForm.value.title || '').trim(),
      content_type: contentForm.value.content_type,
      content_url: contentForm.value.content_url,
      duration: contentForm.value.duration,
      order: Number(contentForm.value.order) || 0
    };

    if (editingContent.value) {
      await request({
        url: `/courses/${courseId.value}/contents/${editingContent.value.id}`,
        method: 'PUT',
        data: payload
      });
      uni.showToast({ title: '更新成功', icon: 'success' });
    } else {
      await request({
        url: `/courses/${courseId.value}/contents`,
        method: 'POST',
        data: payload
      });
      uni.showToast({ title: '添加成功', icon: 'success' });
    }
    closePopup();
    loadContents();
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
    content: `确定要删除“${content.title}”吗？`,
    success: async (res) => {
      if (!res.confirm) return;
      try {
        await request({
          url: `/courses/${courseId.value}/contents/${content.id}`,
          method: 'DELETE'
        });
        uni.showToast({ title: '已删除', icon: 'success' });
        loadContents();
      } catch (e) {
        console.error('Delete failed:', e);
        uni.showToast({ title: '删除失败', icon: 'none' });
      }
    }
  });
};

const closePopup = () => {
  showPopup.value = false;
};

onLoad((options) => {
  if (options.courseId) {
    courseId.value = options.courseId;
    loadCourseInfo();
    loadContents();
  }
});

onShow(() => {
  if (courseId.value) {
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

.action-icon {
  font-size: 48rpx;
  color: #20C997;
}

.course-info-card {
  background: #fff;
  padding: 30rpx;
  margin: 20rpx 30rpx;
  border-radius: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
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
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
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

.content-meta,
.content-actions,
.upload-section,
.upload-hint {
  display: flex;
  align-items: center;
}

.content-meta {
  gap: 20rpx;
}

.meta-type {
  padding: 4rpx 16rpx;
  background: #e3f2fd;
  color: #2196f3;
  font-size: 22rpx;
  border-radius: 8rpx;
}

.meta-type--video {
  background: #e8f5e9;
  color: #2e7d32;
}

.meta-type--link {
  background: #fff4e5;
  color: #c77800;
}

.meta-duration {
  font-size: 22rpx;
  color: #999;
}

.content-actions {
  gap: 16rpx;
  flex-shrink: 0;
}

.action-btn {
  padding: 12rpx 24rpx;
  border-radius: 8rpx;
  font-size: 24rpx;
}

.action-btn.edit {
  background: #20C997;
  color: #fff;
}

.action-btn.delete {
  background: #f5f7fa;
  color: #ff6b6b;
}

.empty-state {
  padding: 200rpx 60rpx;
  text-align: center;
}

.empty-icon-img {
  width: 120rpx;
  height: 120rpx;
  display: block;
  margin: 0 auto 30rpx;
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
}

.popup-container.show {
  transform: translateY(0);
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

.form-hint {
  display: block;
  margin-top: 12rpx;
  font-size: 24rpx;
  color: #8a9bab;
  line-height: 1.5;
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
}

.type-option.active {
  background: #20C997;
  color: #fff;
}

.upload-section {
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
  gap: 6rpx;
}

.upload-hint-img {
  width: 26rpx;
  height: 26rpx;
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
