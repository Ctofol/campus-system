<template>
  <view class="create-task-page">
    <view class="form-card">
      <view class="form-item">
        <text class="label">任务标题</text>
        <input class="input" v-model="form.title" placeholder="例如：本周5公里耐力跑" />
      </view>
      <!-- 任务类型选择器 -->
      <view class="form-item">
        <text class="label">任务类型</text>
        <picker mode="selector" :range="taskTypeLabels" @change="onTypeChange">
          <view class="picker-box">
            <text>{{ form.typeLabel || '请选择任务类型' }}</text>
            <text class="arrow">→</text>
          </view>
        </picker>
      </view>

      <!-- 体测任务视频上传（第二阶段新增） -->
      <view class="form-item vertical" v-if="form.type === 'test'">
        <text class="label required">体测示范视频</text>
        <view class="video-upload-area">
          <view v-if="!form.videoUrl" class="upload-placeholder" @click="chooseVideo">
            <text class="upload-icon">📹</text>
            <text class="upload-text">点击上传体测示范视频</text>
            <text class="upload-hint">支持mp4/webm格式，最大50MB</text>
          </view>
          <view v-else class="video-preview">
            <video 
              :src="form.videoUrl" 
              class="preview-video"
              controls
              :show-center-play-btn="true"
            ></video>
            <view class="video-actions">
              <button class="action-btn" size="mini" @click="chooseVideo">重新上传</button>
              <button class="action-btn delete" size="mini" @click="deleteVideo">删除</button>
            </view>
          </view>
        </view>
      </view>

      <template v-if="form.type === 'run'">
        <view class="form-item">
          <text class="label">目标距离 (km)</text>
          <input class="input" type="digit" v-model="form.distance" placeholder="例如 3.0" />
        </view>
        <view class="form-item vertical compact-hint">
          <view class="form-item-inner">
            <text class="label">最低时长 (分钟)</text>
            <input
              class="input"
              type="digit"
              v-model="form.minDurationMinutes"
              placeholder="例如 20"
            />
          </view>
          <text class="field-hint">学生单次跑步需同时满足距离与时长下限（与后端自动核验一致）；未填的一项表示不设该下限。</text>
        </view>
      </template>
      
      <view class="form-item">
        <text class="label">开始日期</text>
        <picker mode="date" @change="onStartDateChange">
          <view class="picker-box">
            <text>{{ form.startDate || '选填，默认发布后即可开始' }}</text>
            <text class="arrow">→</text>
          </view>
        </picker>
      </view>

      <view class="form-item">
        <text class="label">截止日期</text>
        <picker mode="date" @change="onDateChange">
          <view class="picker-box">
            <text>{{ form.deadline || '请选择截止日期' }}</text>
            <text class="arrow">→</text>
          </view>
        </picker>
      </view>

      <view class="form-item" v-if="classes.length > 0" @click="showClassSheet = true">
        <text class="label">指派班级</text>
        <view class="picker-box">
          <text class="picker-summary">{{ classSelectionSummary }}</text>
          <text class="arrow">→</text>
        </view>
      </view>
      <view v-else class="form-item vertical compact-hint">
        <text class="label">指派班级</text>
        <text class="field-hint">
          您尚无管辖范围内的行政班（需在教师端绑定班级或管理学员所在班级）。任务只能发布到这些班级，不能面向全员。
        </text>
      </view>

      <view class="form-item vertical">
        <text class="label">任务说明</text>
        <textarea class="textarea" v-model="form.description" placeholder="请输入任务的具体要求和注意事项..." />
      </view>
    </view>

    <view class="footer-btn">
      <button class="submit-btn" @click="submitTask">发布任务</button>
    </view>

    <!-- 多选班级：支持全选，一次向所选班级发布相同任务 -->
    <view v-if="showClassSheet" class="class-sheet-mask" @click.self="showClassSheet = false">
      <view class="class-sheet" @click.stop>
        <view class="class-sheet-head">
          <text class="sheet-link" @click="toggleSelectAllClasses">{{ allClassesSelected ? '取消全选' : '全选' }}</text>
          <text class="sheet-title">指派班级</text>
          <text class="sheet-link primary" @click="showClassSheet = false">完成</text>
        </view>
        <scroll-view scroll-y class="class-sheet-body">
          <view
            v-for="c in classes"
            :key="c.id"
            class="class-sheet-row"
            @click="toggleClassId(c.id)"
          >
            <checkbox
              :checked="selectedClassIds.includes(c.id)"
              color="#20C997"
              style="transform: scale(0.85)"
            />
            <text class="class-sheet-name">{{ formatClassRow(c) }}</text>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { createTeacherTask, request, BASE_URL } from '@/utils/request.js';

const taskTypes = ['run', 'test']; // Simplified to match backend enum/string
const taskTypeLabels = ['跑步任务', '体能测试']; // Display labels
const classes = ref([]);
const selectedClassIds = ref([]);
const showClassSheet = ref(false);

const form = ref({
  title: '',
  type: '',
  typeLabel: '',
  distance: '',
  minDurationMinutes: '',
  startDate: '',
  deadline: '',
  description: '',
  videoUrl: '',  // 第二阶段新增：视频URL
  videoFile: null  // 临时存储视频文件
});

onMounted(() => {
  fetchClasses();
});

const formatClassRow = (c) => `${c.name}（${c.student_count ?? 0}人）`;

const classSelectionSummary = computed(() => {
  const list = classes.value;
  const ids = selectedClassIds.value;
  if (!list.length) return '暂无管辖班级';
  if (!ids.length) return '请至少选择一个班级';
  const picked = list.filter((c) => ids.includes(c.id));
  const n = picked.length;
  const totalPeople = picked.reduce((s, c) => s + (Number(c.student_count) || 0), 0);
  if (n === list.length) return `已全选 ${n} 个班（约 ${totalPeople} 人）`;
  if (n === 1) return `${formatClassRow(picked[0])}（约 ${totalPeople} 人）`;
  const head = picked
    .slice(0, 2)
    .map((c) => formatClassRow(c))
    .join('、');
  return n > 2 ? `${head} 等 ${n} 个班（约 ${totalPeople} 人）` : `${head}（约 ${totalPeople} 人）`;
});

const allClassesSelected = computed(
  () => classes.value.length > 0 && selectedClassIds.value.length === classes.value.length
);

const toggleClassId = (id) => {
  const i = selectedClassIds.value.indexOf(id);
  if (i >= 0) {
    selectedClassIds.value = selectedClassIds.value.filter((x) => x !== id);
  } else {
    selectedClassIds.value = [...selectedClassIds.value, id];
  }
};

const toggleSelectAllClasses = () => {
  if (allClassesSelected.value) {
    selectedClassIds.value = [];
  } else {
    selectedClassIds.value = classes.value.map((c) => c.id);
  }
};

const fetchClasses = async () => {
  try {
    const res = await request({ url: '/teacher/classes' });
    const list = Array.isArray(res) ? res : [];
    classes.value = list;
    selectedClassIds.value = list.map((c) => c.id);
  } catch (e) {
    console.error('Fetch classes failed', e);
  }
};

const onTypeChange = (e) => {
  const index = Number(e.detail.value);
  form.value.type = taskTypes[index];
  form.value.typeLabel = taskTypeLabels[index];
  
  // 如果切换到非体测任务，清空视频
  if (form.value.type !== 'test') {
    form.value.videoUrl = '';
    form.value.videoFile = null;
  }
};

const onStartDateChange = (e) => {
  form.value.startDate = e.detail.value;
};

const onDateChange = (e) => {
  form.value.deadline = e.detail.value;
};

// 第二阶段新增：视频上传功能
const chooseVideo = () => {
  uni.chooseVideo({
    sourceType: ['camera', 'album'],
    maxDuration: 300, // 最长5分钟
    camera: 'back',
    success: async (res) => {
      const tempFilePath = res.tempFilePath;
      const fileSize = res.size;
      
      // 检查文件大小（50MB限制）
      if (fileSize > 50 * 1024 * 1024) {
        return uni.showToast({ title: '视频文件不能超过50MB', icon: 'none' });
      }
      
      // 显示上传中
      uni.showLoading({ title: '上传中...' });
      
      try {
        // 上传视频
        const uploadRes = await uploadVideo(tempFilePath);
        form.value.videoUrl = uploadRes.url;
        uni.hideLoading();
        uni.showToast({ title: '视频上传成功', icon: 'success' });
      } catch (e) {
        uni.hideLoading();
        console.error('Upload failed:', e);
        uni.showToast({ title: '视频上传失败', icon: 'none' });
      }
    }
  });
};

const uploadVideo = (filePath) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token');
    
    uni.uploadFile({
      url: `${BASE_URL}/upload/file`,
      filePath: filePath,
      name: 'file',
      fileName: 'upload.mp4',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const data = JSON.parse(res.data);
          resolve(data);
        } else {
          reject(new Error('Upload failed'));
        }
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
};

const deleteVideo = () => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除已上传的视频吗？',
    success: (res) => {
      if (res.confirm) {
        form.value.videoUrl = '';
        form.value.videoFile = null;
        uni.showToast({ title: '已删除', icon: 'success' });
      }
    }
  });
};

const submitTask = async () => {
  // 验证必填项
  if (!form.value.title || !form.value.type || !form.value.deadline) {
    return uni.showToast({ title: '请完善任务信息', icon: 'none' });
  }

  if (form.value.startDate && form.value.deadline && form.value.startDate > form.value.deadline) {
    return uni.showToast({ title: '开始日期不能晚于截止日期', icon: 'none' });
  }
  
  // 体测任务必须上传视频
  if (form.value.type === 'test' && !form.value.videoUrl) {
    return uni.showToast({ title: '体测任务必须上传示范视频', icon: 'none' });
  }

  if (!classes.value.length || !selectedClassIds.value.length) {
    return uni.showToast({ title: '请在「指派班级」中至少选择一个班级', icon: 'none' });
  }

  const distKm =
    form.value.type === 'run' ? parseFloat(String(form.value.distance).trim()) : 0;
  const durMin =
    form.value.type === 'run' ? parseFloat(String(form.value.minDurationMinutes).trim()) : 0;
  if (form.value.type === 'run') {
    const distOk = !Number.isNaN(distKm) && distKm > 0;
    const durOk = !Number.isNaN(durMin) && durMin > 0;
    if (!distOk && !durOk) {
      return uni.showToast({ title: '跑步任务请填写目标距离或最低时长至少一项', icon: 'none' });
    }
  }

  uni.showLoading({ title: '发布中...' });

  try {
    const minDurationSec =
      form.value.type === 'run' && !Number.isNaN(durMin) && durMin > 0
        ? Math.round(durMin * 60)
        : 0;
    const minDistanceKm =
      form.value.type === 'run' && !Number.isNaN(distKm) && distKm > 0 ? distKm : 0;

    const payload = {
      title: form.value.title,
      type: form.value.type,
      min_distance: minDistanceKm,
      min_duration: minDurationSec,
      min_count: 0,
      starts_at: form.value.startDate ? new Date(form.value.startDate).toISOString() : null,
      deadline: new Date(form.value.deadline).toISOString(),
      description: form.value.description,
      target_group: 'class',
      class_ids: [...selectedClassIds.value],
      video_url: form.value.videoUrl || null  // 第二阶段新增：视频URL
    };

    const created = await createTeacherTask(payload);
    const n = Array.isArray(created) ? created.length : 1;

    uni.hideLoading();
    uni.showToast({
      title: n > 1 ? `已向 ${n} 个班级发布相同任务` : '任务发布成功',
      icon: 'success'
    });
    
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  } catch (e) {
    uni.hideLoading();
    console.error(e);
    uni.showToast({ title: '发布失败', icon: 'none' });
  }
};
</script>

<style scoped>
.create-task-page {
  min-height: 100vh;
  background: #f8f8f8;
  padding: 20rpx;
  padding-bottom: 120rpx;
}

.form-card {
  background: #fff;
  border-radius: 12rpx;
  padding: 0 30rpx;
}

.form-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx 0;
  border-bottom: 1px solid #eee;
}

.form-item:last-child {
  border-bottom: none;
}

.form-item.vertical {
  flex-direction: column;
  align-items: flex-start;
  gap: 20rpx;
}

.form-item.vertical.compact-hint {
  gap: 12rpx;
}

.form-item-inner {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.field-hint {
  font-size: 24rpx;
  color: #999;
  line-height: 1.5;
  width: 100%;
}

.label {
  font-size: 30rpx;
  color: #333;
  width: 200rpx;
}

.input {
  flex: 1;
  text-align: right;
  font-size: 30rpx;
  color: #333;
}

.picker-box {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10rpx;
  font-size: 30rpx;
  color: #666;
}

.picker-summary {
  flex: 1;
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.arrow {
  color: #ccc;
  font-size: 26rpx;
}

.textarea {
  width: 100%;
  height: 200rpx;
  background: #f9f9f9;
  padding: 20rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

/* 第二阶段新增：视频上传样式 */
.label.required::after {
  content: '*';
  color: #ff4d4f;
  margin-left: 4rpx;
}

.video-upload-area {
  width: 100%;
}

.upload-placeholder {
  width: 100%;
  height: 300rpx;
  background: #f9f9f9;
  border: 2rpx dashed #ddd;
  border-radius: 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
}

.upload-icon {
  font-size: 60rpx;
}

.upload-text {
  font-size: 28rpx;
  color: #666;
}

.upload-hint {
  font-size: 24rpx;
  color: #999;
}

.video-preview {
  width: 100%;
}

.preview-video {
  width: 100%;
  height: 400rpx;
  background: #000;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
}

.video-actions {
  display: flex;
  gap: 20rpx;
  justify-content: center;
}

.action-btn {
  margin: 0;
  font-size: 26rpx;
  padding: 0 30rpx;
  background: #fff;
  color: #20C997;
  border: 1px solid #20C997;
}

.action-btn.delete {
  color: #ff4d4f;
  border-color: #ff4d4f;
}

.footer-btn {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: #fff;
  padding: 20rpx 30rpx;
  box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
  box-sizing: border-box;
}

.submit-btn {
  background: #20C997;
  color: #fff;
  border-radius: 40rpx;
  font-size: 32rpx;
  font-weight: bold;
}

.class-sheet-mask {
  position: fixed;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.class-sheet {
  width: 100%;
  max-height: 70vh;
  background: #fff;
  border-radius: 24rpx 24rpx 0 0;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  display: flex;
  flex-direction: column;
}

.class-sheet-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 32rpx;
  border-bottom: 1px solid #eee;
}

.sheet-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #333;
}

.sheet-link {
  font-size: 28rpx;
  color: #666;
  padding: 8rpx;
}

.sheet-link.primary {
  color: #20c997;
  font-weight: 600;
}

.class-sheet-body {
  max-height: 56vh;
  padding: 16rpx 0 32rpx;
}

.class-sheet-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 24rpx 32rpx;
  border-bottom: 1px solid #f5f5f5;
}

.class-sheet-name {
  flex: 1;
  font-size: 30rpx;
  color: #333;
}
</style>