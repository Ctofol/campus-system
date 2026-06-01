<template>
  <view class="create-activity-page">
    <page-tab-header title="发布活动" show-back theme="white" />

    <scroll-view
      class="form-scroll page-tab-body"
      scroll-y
      :scroll-into-view="scrollIntoViewId"
      scroll-with-animation
      :style="{ paddingBottom: scrollPaddingBottom }"
    >
      <view class="form-container">
        <view id="field-cover" class="form-item">
          <text class="label">活动封面</text>
          <view class="cover-upload" @click="chooseCover">
            <image v-if="coverImage" :src="coverImage" mode="aspectFill" class="cover-preview" />
            <view v-else class="cover-placeholder">
              <text class="upload-icon">📷</text>
              <text class="upload-text">点击上传封面</text>
            </view>
          </view>
        </view>

        <view id="field-title" class="form-item">
          <text class="label">活动标题</text>
          <input
            class="input"
            v-model="formData.title"
            placeholder="请输入活动标题"
            maxlength="30"
            adjust-position
            :cursor-spacing="120"
            @focus="onFieldFocus('field-title')"
          />
        </view>

        <view id="field-desc" class="form-item">
          <text class="label">活动描述</text>
          <textarea
            class="textarea"
            v-model="formData.description"
            placeholder="请输入活动描述"
            maxlength="200"
            adjust-position
            :cursor-spacing="120"
            @focus="onFieldFocus('field-desc')"
          />
        </view>

        <view id="field-time" class="form-item">
          <text class="label">活动时间</text>
          <picker
            mode="multiSelector"
            :range="dtRanges"
            :value="dtIndex"
            @change="onDateTimeChange"
            @columnchange="onDateTimeColumnChange"
          >
            <view class="picker picker-datetime" :class="{ 'is-placeholder': !activityDateTimeText }">
              {{ activityDateTimeText || '请选择活动时间' }}
            </view>
          </picker>
        </view>

        <view id="field-location" class="form-item">
          <text class="label">活动地点</text>
          <input
            class="input"
            v-model="formData.location"
            placeholder="请输入活动地点"
            maxlength="50"
            adjust-position
            :cursor-spacing="120"
            @focus="onFieldFocus('field-location')"
          />
        </view>

        <view id="field-distance" class="form-item">
          <text class="label">目标距离（公里）</text>
          <input
            class="input"
            type="digit"
            v-model="formData.distance"
            placeholder="请输入目标距离"
            adjust-position
            :cursor-spacing="160"
            @focus="onFieldFocus('field-distance')"
          />
        </view>

        <view id="field-quota" class="form-item">
          <text class="label">活动名额</text>
          <input
            class="input"
            type="number"
            v-model="formData.total_quota"
            placeholder="请输入活动名额"
            adjust-position
            :cursor-spacing="160"
            @focus="onFieldFocus('field-quota')"
          />
        </view>

        <view id="scroll-anchor" class="scroll-anchor" />
      </view>
    </scroll-view>

    <view class="submit-bar" :style="{ bottom: keyboardHeight + 'px' }">
      <button class="submit-btn" @click="handleSubmit">发布活动</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue';
import { onLoad, onUnload } from '@dcloudio/uni-app';
import { createGroupActivity, uploadFile } from '@/utils/request.js';
import {
  createDateTimePickerConfig,
  getDefaultActivityDateTime
} from '@/utils/activity-datetime-picker.js';

const dtPicker = createDateTimePickerConfig();
const dtRanges = ref(dtPicker.buildRanges(0, 0));
const dtIndex = ref([0, 0, 0, 8, 0]);
const activityDate = ref('');
const activityTimeValue = ref('');

const activityDateTimeText = computed(() => {
  if (activityDate.value && activityTimeValue.value) {
    return `${activityDate.value} ${activityTimeValue.value}`;
  }
  return '';
});

const initActivityDateTime = () => {
  const def = getDefaultActivityDateTime();
  activityDate.value = def.date;
  activityTimeValue.value = def.time;
  const { index, ranges } = dtPicker.indexFromDateTime(def.date, def.time);
  dtIndex.value = index;
  dtRanges.value = ranges;
};

const onDateTimeChange = (e) => {
  const { date, time, ranges } = dtPicker.dateTimeFromIndex(e.detail.value, dtRanges.value);
  activityDate.value = date;
  activityTimeValue.value = time;
  dtRanges.value = ranges;
  dtIndex.value = e.detail.value;
};

const onDateTimeColumnChange = (e) => {
  const { index, ranges } = dtPicker.adjustIndexOnColumnChange(
    e.detail.column,
    e.detail.value,
    dtIndex.value,
    dtRanges.value
  );
  dtIndex.value = index;
  dtRanges.value = ranges;
  const applied = dtPicker.dateTimeFromIndex(index, ranges);
  activityDate.value = applied.date;
  activityTimeValue.value = applied.time;
};

const scrollIntoViewId = ref('');
const keyboardHeight = ref(0);

const scrollPaddingBottom = computed(() => {
  const kb = keyboardHeight.value;
  const submitBarPx = 140;
  return kb > 0 ? `${kb + submitBarPx}px` : `${submitBarPx}px`;
});

const onFieldFocus = (fieldId) => {
  scrollIntoViewId.value = '';
  nextTick(() => {
    scrollIntoViewId.value = fieldId;
    if (fieldId === 'field-distance' || fieldId === 'field-quota') {
      setTimeout(() => {
        scrollIntoViewId.value = 'scroll-anchor';
      }, 80);
    }
  });
};

const onKeyboardHeightChange = (res) => {
  keyboardHeight.value = res.height || 0;
};

const groupId = ref(0);
const coverImage = ref('');
const coverUrl = ref('');
const formData = ref({
  title: '',
  description: '',
  location: '',
  distance: '',
  total_quota: 50
});

onLoad((options) => {
  if (options.groupId) {
    groupId.value = parseInt(options.groupId);
  } else {
    uni.showToast({ title: '参数错误', icon: 'none' });
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  }
  if (typeof uni.onKeyboardHeightChange === 'function') {
    uni.onKeyboardHeightChange(onKeyboardHeightChange);
  }
  initActivityDateTime();
});

onUnload(() => {
  if (typeof uni.offKeyboardHeightChange === 'function') {
    uni.offKeyboardHeightChange(onKeyboardHeightChange);
  }
});

const goBack = () => {
  uni.navigateBack();
};

const chooseCover = () => {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const tempFilePath = res.tempFilePaths[0];
      coverImage.value = tempFilePath;
      
      try {
        uni.showLoading({ title: '上传中...' });
        const uploadResult = await uploadFile(tempFilePath, 'image');
        coverUrl.value = uploadResult.url;
        uni.hideLoading();
        uni.showToast({ title: '上传成功', icon: 'success' });
      } catch (e) {
        uni.hideLoading();
        console.error('上传失败:', e);
        uni.showToast({ title: '上传失败', icon: 'none' });
      }
    }
  });
};

const handleSubmit = async () => {
  // 验证表单
  if (!formData.value.title) {
    uni.showToast({ title: '请输入活动标题', icon: 'none' });
    return;
  }
  
  if (!formData.value.description) {
    uni.showToast({ title: '请输入活动描述', icon: 'none' });
    return;
  }
  
  if (!activityDate.value || !activityTimeValue.value) {
    uni.showToast({ title: '请选择活动时间', icon: 'none' });
    return;
  }
  
  if (!formData.value.location) {
    uni.showToast({ title: '请输入活动地点', icon: 'none' });
    return;
  }
  
  if (!formData.value.distance || parseFloat(formData.value.distance) <= 0) {
    uni.showToast({ title: '请输入有效的目标距离', icon: 'none' });
    return;
  }
  
  if (!formData.value.total_quota || parseInt(formData.value.total_quota) <= 0) {
    uni.showToast({ title: '请输入有效的活动名额', icon: 'none' });
    return;
  }
  
  try {
    uni.showLoading({ title: '发布中...' });
    
    // 组合日期和时间
    const activityTimeStr = `${activityDate.value} ${activityTimeValue.value}:00`;
    
    const data = {
      group_id: groupId.value,
      title: formData.value.title,
      description: formData.value.description,
      cover_image: coverUrl.value || null,
      activity_time: activityTimeStr,
      location: formData.value.location,
      distance: parseFloat(formData.value.distance),
      total_quota: parseInt(formData.value.total_quota)
    };
    
    console.log('提交数据:', data);
    
    await createGroupActivity(data);
    
    uni.hideLoading();
    uni.showToast({ title: '发布成功', icon: 'success' });
    
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  } catch (e) {
    uni.hideLoading();
    console.error('发布失败:', e);
    const errorMsg = e.message || e.detail || '发布失败，请重试';
    uni.showToast({ title: errorMsg, icon: 'none' });
  }
};
</script>

<style scoped>
.create-activity-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
  overflow: hidden;
}

.form-scroll {
  flex: 1;
  height: 0;
  box-sizing: border-box;
}

.scroll-anchor {
  height: 2rpx;
}

.form-container {
  padding: 40rpx 30rpx 24rpx;
}

.form-item {
  margin-bottom: 40rpx;
}

.label {
  display: block;
  font-size: 28rpx;
  color: #333;
  margin-bottom: 16rpx;
  font-weight: bold;
}

.input, .textarea, .picker {
  width: 100%;
  padding: 24rpx;
  background: #fff;
  border-radius: 16rpx;
  font-size: 28rpx;
  border: 2rpx solid #e0e0e0;
  box-sizing: border-box;
}

.input {
  height: 80rpx;
  line-height: 80rpx;
}

.textarea {
  min-height: 200rpx;
  line-height: 1.5;
}

.cover-upload {
  width: 100%;
  height: 300rpx;
  border-radius: 16rpx;
  overflow: hidden;
  background: #f5f7fa;
  border: 2rpx dashed #e0e0e0;
}

.cover-preview {
  width: 100%;
  height: 100%;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.upload-icon {
  font-size: 60rpx;
  margin-bottom: 16rpx;
}

.upload-text {
  font-size: 24rpx;
  color: #999;
}

.picker {
  color: #333;
}

.picker-datetime {
  display: flex;
  align-items: center;
  min-height: 80rpx;
}

.picker-datetime.is-placeholder {
  color: #999;
}

.submit-bar {
  position: fixed;
  left: 0;
  right: 0;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.06);
  z-index: 10;
}

.submit-btn {
  width: 100%;
  padding: 28rpx;
  background: linear-gradient(135deg, #4dabf7, #339af0);
  color: #fff;
  border-radius: 50rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
  margin: 0;
}
</style>
