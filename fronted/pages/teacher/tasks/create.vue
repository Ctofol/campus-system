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
            <image class="upload-icon" src="/static/通知图标.png" mode="aspectFit" />
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

      <view class="form-item vertical">
        <view class="form-item-inner">
          <text class="label">同步课程资料</text>
          <switch :checked="attachCourse" @change="attachCourse = !!$event.detail.value" color="#20C997" />
        </view>
        <text class="field-hint">发布任务时可同时生成配套课程，学生在课程页直接查看资料。</text>
      </view>

      <view v-if="attachCourse" class="course-section">
        <view class="course-section-head">
          <text class="course-section-title">配套课程</text>
          <text class="course-section-tip">课程管理页主要看数据，内容在这里一次配好。</text>
        </view>

        <view class="form-item">
          <text class="label">课程标题</text>
          <input class="input" v-model="courseForm.title" @blur="syncCourseDefaults" placeholder="默认沿用任务标题" />
        </view>

        <view class="form-item">
          <text class="label">课程分类</text>
          <picker mode="selector" :range="courseCategoryOptions" range-key="label" @change="onCourseCategoryChange">
            <view class="picker-box">
              <text>{{ selectedCourseCategoryLabel }}</text>
              <text class="arrow">→</text>
            </view>
          </picker>
        </view>

        <view class="form-item vertical">
          <view class="form-item-inner">
            <text class="label">课程封面</text>
            <button class="mini-btn" @click="uploadCourseCover">{{ courseForm.cover_url ? '重新上传' : '上传封面' }}</button>
          </view>
          <image v-if="courseForm.cover_url" class="course-cover-preview" :src="getCourseCoverUrl(courseForm.cover_url)" mode="aspectFill"></image>
        </view>

        <view class="form-item vertical">
          <view class="form-item-inner">
            <text class="label">公开课程</text>
            <switch :checked="courseForm.is_public" @change="courseForm.is_public = !!$event.detail.value" color="#20C997" />
          </view>
        </view>

        <view class="content-block" v-for="(content, idx) in courseForm.contents" :key="idx">
          <view class="content-block-head">
            <text class="content-block-title">内容 {{ idx + 1 }}</text>
            <text class="content-remove" @click="removeCourseContent(idx)">删除</text>
          </view>
          <view class="form-item">
            <text class="label">标题</text>
            <input class="input" v-model="content.title" placeholder="例如：动作示范 / 任务说明" />
          </view>
          <view class="form-item">
            <text class="label">类型</text>
            <picker mode="selector" :range="['视频','链接','文件']" @change="onCourseContentTypeChange(idx, $event)">
              <view class="picker-box">
                <text>{{ getCourseContentTypeLabel(content.content_type) }}</text>
                <text class="arrow">→</text>
              </view>
            </picker>
          </view>
          <view class="form-item vertical" v-if="content.content_type === 'video'">
            <view class="form-item-inner">
              <text class="label">视频地址</text>
              <button class="mini-btn" @click="uploadCourseVideo(idx)">{{ content.content_url ? '重新上传' : '上传视频' }}</button>
            </view>
            <text class="field-hint" v-if="content.content_url">{{ content.content_url }}</text>
          </view>
          <view class="form-item vertical" v-else>
            <text class="label">{{ content.content_type === 'link' ? '链接地址' : '文件地址' }}</text>
            <input class="input input-left" v-model="content.content_url" :placeholder="content.content_type === 'link' ? '粘贴网页链接' : '粘贴文件 URL'" />
          </view>
        </view>

        <button class="add-content-btn" @click="addCourseContent">新增课程内容</button>
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
import { createTeacherTask, request, BASE_URL, uploadFile } from '@/utils/request.js';

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

const attachCourse = ref(true);
const courseForm = ref({
  title: '',
  category: 'fitness',
  cover_url: '',
  is_public: true,
  contents: [
    { title: '任务说明', content_type: 'link', content_url: '', duration: 0 }
  ]
});
const courseCategoryOptions = [
  { label: '体能课', value: 'fitness' },
  { label: '技能课', value: 'skill' },
  { label: '理论课', value: 'theory' }
];

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

const selectedCourseCategoryLabel = computed(() => {
  const hit = courseCategoryOptions.find((item) => item.value === courseForm.value.category);
  return hit ? hit.label : '请选择课程分类';
});

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

const onCourseCategoryChange = (e) => {
  const idx = Number(e.detail.value);
  const picked = courseCategoryOptions[idx];
  courseForm.value.category = picked ? picked.value : 'fitness';
};

const syncCourseDefaults = () => {
  if (!courseForm.value.title) {
    courseForm.value.title = form.value.title || '';
  }
};

const addCourseContent = () => {
  courseForm.value.contents.push({
    title: '',
    content_type: 'link',
    content_url: '',
    duration: 0
  });
};

const removeCourseContent = (idx) => {
  courseForm.value.contents.splice(idx, 1);
  if (!courseForm.value.contents.length) {
    addCourseContent();
  }
};

const onCourseContentTypeChange = (idx, e) => {
  const values = ['video', 'link', 'document'];
  const nextType = values[Number(e.detail.value)] || 'link';
  const row = courseForm.value.contents[idx];
  row.content_type = nextType;
  row.content_url = '';
  row.duration = 0;
};

const uploadCourseCover = () => {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const filePath = res.tempFilePaths && res.tempFilePaths[0];
      if (!filePath) return;
      uni.showLoading({ title: '上传中..', mask: true });
      try {
        const uploadRes = await uploadFile(filePath, 'image');
        courseForm.value.cover_url = uploadRes.url;
        uni.hideLoading();
        uni.showToast({ title: '封面已上传', icon: 'success' });
      } catch (e) {
        uni.hideLoading();
        uni.showToast({ title: '封面上传失败', icon: 'none' });
      }
    }
  });
};

const uploadCourseVideo = (idx) => {
  uni.chooseVideo({
    sourceType: ['camera', 'album'],
    maxDuration: 300,
    camera: 'back',
    success: async (res) => {
      const filePath = res.tempFilePath;
      if (!filePath) return;
      uni.showLoading({ title: '上传中..', mask: true });
      try {
        const uploadRes = await uploadFile(filePath, 'video');
        courseForm.value.contents[idx].content_url = uploadRes.url;
        courseForm.value.contents[idx].duration = Math.round(Number(res.duration) || 0);
        uni.hideLoading();
        uni.showToast({ title: '视频已上传', icon: 'success' });
      } catch (e) {
        uni.hideLoading();
        uni.showToast({ title: '视频上传失败', icon: 'none' });
      }
    }
  });
};

const getCourseContentTypeLabel = (type) => {
  if (type === 'video') return '视频';
  if (type === 'document') return '文件';
  return '链接';
};

const getCourseCoverUrl = (url) => {
  if (!url) return '';
  return url.startsWith('http') ? url : `${BASE_URL}${url}`;
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

const createAttachedCourseIfNeeded = async () => {
  if (!attachCourse.value) return null;

  const courseTitle = (courseForm.value.title || form.value.title || '').trim();
  const contents = (courseForm.value.contents || [])
    .map((item, index) => ({
      title: (item.title || '').trim(),
      content_type: item.content_type || 'link',
      content_url: (item.content_url || '').trim(),
      duration: Number(item.duration) || 0,
      order: index + 1
    }))
    .filter((item) => item.title && item.content_url);

  if (!courseTitle || !contents.length) {
    return null;
  }

  const createdCourse = await request({
    url: '/courses/',
    method: 'POST',
    data: {
      title: courseTitle,
      description: form.value.description,
      cover_url: courseForm.value.cover_url || null,
      category: courseForm.value.category || 'fitness',
      is_public: courseForm.value.is_public
    }
  });

  for (const item of contents) {
    await request({
      url: `/courses/${createdCourse.id}/contents`,
      method: 'POST',
      data: item
    });
  }

  return createdCourse;
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
    await createAttachedCourseIfNeeded();
    const n = Array.isArray(created) ? created.length : 1;

    uni.hideLoading();
    uni.showToast({
      title: attachCourse.value ? '任务和课程资料已发布' : (n > 1 ? `已向 ${n} 个班级发布相同任务` : '任务发布成功'),
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

.input-left {
  text-align: left;
  width: 100%;
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

.course-section {
  margin-top: 10rpx;
  padding: 24rpx;
  background: #f7fbfa;
  border-radius: 16rpx;
}

.course-section-head {
  margin-bottom: 16rpx;
}

.course-section-title {
  font-size: 30rpx;
  color: #333;
  font-weight: 700;
  display: block;
  margin-bottom: 8rpx;
}

.course-section-tip {
  font-size: 24rpx;
  color: #7a7a7a;
  line-height: 1.5;
}

.mini-btn {
  margin: 0;
  min-width: 160rpx;
  height: 60rpx;
  line-height: 60rpx;
  border-radius: 30rpx;
  background: #20C997;
  color: #fff;
  font-size: 24rpx;
}

.course-cover-preview {
  width: 100%;
  height: 220rpx;
  border-radius: 12rpx;
  background: #eef3f2;
}

.content-block {
  margin-top: 18rpx;
  background: #fff;
  border-radius: 14rpx;
  padding: 0 20rpx 16rpx;
}

.content-block-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 0 10rpx;
}

.content-block-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.content-remove {
  font-size: 24rpx;
  color: #e03131;
}

.add-content-btn {
  margin-top: 20rpx;
  background: #e8faf4;
  color: #12b886;
  border-radius: 30rpx;
  font-size: 26rpx;
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
  width: 60rpx;
  height: 60rpx;
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
