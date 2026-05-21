<template>
  <view class="create-page">
    <scroll-view
      class="form-scroll"
      scroll-y
      :scroll-into-view="scrollIntoViewId"
      scroll-with-animation
      :style="{ paddingBottom: scrollPaddingBottom }"
    >
      <view class="form">
        <view id="field-title" class="form-item">
          <text class="label">活动标题 *</text>
          <input
            v-model="form.title"
            placeholder="请输入活动标题"
            class="input"
            adjust-position
            :cursor-spacing="120"
            @focus="onFieldFocus('field-title')"
          />
        </view>

        <view id="field-datetime" class="form-item">
          <text class="label">活动时间 *</text>
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
            v-model="form.location"
            placeholder="请输入活动地点"
            class="input"
            adjust-position
            :cursor-spacing="120"
            @focus="onFieldFocus('field-location')"
          />
        </view>

        <view id="field-distance" class="form-item">
          <text class="label">目标距离(km)</text>
          <input
            v-model.number="form.distance"
            type="digit"
            placeholder="请输入目标距离"
            class="input"
            adjust-position
            :cursor-spacing="160"
            @focus="onFieldFocus('field-distance')"
          />
        </view>

        <view id="field-quota" class="form-item">
          <text class="label">总名额 *</text>
          <input
            v-model.number="form.total_quota"
            type="number"
            placeholder="请输入总名额"
            class="input"
            adjust-position
            :cursor-spacing="160"
            @focus="onFieldFocus('field-quota')"
          />
        </view>

        <view id="field-desc" class="form-item">
          <text class="label">活动描述</text>
          <textarea
            v-model="form.description"
            placeholder="请输入活动描述"
            class="textarea"
            adjust-position
            :cursor-spacing="120"
            @focus="onFieldFocus('field-desc')"
          />
        </view>

        <view id="scroll-anchor" class="scroll-anchor" />
      </view>
    </scroll-view>

    <view class="bottom-bar" :style="{ bottom: keyboardHeight + 'px' }">
      <button class="submit-btn" @click="handleSubmit">发起活动</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue';
import { onUnload } from '@dcloudio/uni-app';
import { createGroupActivity, getMyRunGroup } from '@/utils/request.js';
import {
  createDateTimePickerConfig,
  getDefaultActivityDateTime
} from '@/utils/activity-datetime-picker.js';

const dtPicker = createDateTimePickerConfig();
const dtRanges = ref(dtPicker.buildRanges(0, 0));
const dtIndex = ref([0, 0, 0, 8, 0]);

const activityDateTimeText = computed(() => {
  if (form.value.date && form.value.time) {
    return `${form.value.date} ${form.value.time}`;
  }
  return '';
});

const initActivityDateTime = () => {
  const def = getDefaultActivityDateTime();
  form.value.date = def.date;
  form.value.time = def.time;
  const { index, ranges } = dtPicker.indexFromDateTime(def.date, def.time);
  dtIndex.value = index;
  dtRanges.value = ranges;
};

const onDateTimeChange = (e) => {
  const { date, time, ranges } = dtPicker.dateTimeFromIndex(e.detail.value, dtRanges.value);
  form.value.date = date;
  form.value.time = time;
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
  form.value.date = applied.date;
  form.value.time = applied.time;
};

const scrollIntoViewId = ref('');
const keyboardHeight = ref(0);

const scrollPaddingBottom = computed(() => {
  const kb = keyboardHeight.value;
  const submitBarPx = 120;
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

const form = ref({
  title: '',
  description: '',
  date: '',
  time: '',
  location: '',
  distance: null,
  total_quota: 50
});

const myGroup = ref(null);

const loadMyGroup = async () => {
  try {
    const res = await getMyRunGroup();
    myGroup.value = res;
  } catch (e) {
    uni.showToast({ title: '请先加入跑团', icon: 'none' });
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  }
};

const handleSubmit = async () => {
  if (!form.value.title) {
    uni.showToast({ title: '请输入活动标题', icon: 'none' });
    return;
  }

  if (!form.value.date || !form.value.time) {
    uni.showToast({ title: '请选择活动时间', icon: 'none' });
    return;
  }

  if (!form.value.total_quota || form.value.total_quota < 1) {
    uni.showToast({ title: '请输入有效的总名额', icon: 'none' });
    return;
  }

  try {
    const activityTime = `${form.value.date}T${form.value.time}:00`;
    const res = await createGroupActivity({
      group_id: myGroup.value.id,
      title: form.value.title,
      description: form.value.description,
      activity_time: activityTime,
      location: form.value.location,
      distance: form.value.distance,
      total_quota: form.value.total_quota
    });

    uni.showToast({ title: '发起成功', icon: 'success' });
    setTimeout(() => {
      uni.redirectTo({ url: `/pages/run-group/activity-detail?activityId=${res.id}` });
    }, 1500);
  } catch (e) {
    uni.showToast({ title: e.detail || '发起失败', icon: 'none' });
  }
};

onMounted(() => {
  initActivityDateTime();
  loadMyGroup();
  if (typeof uni.onKeyboardHeightChange === 'function') {
    uni.onKeyboardHeightChange(onKeyboardHeightChange);
  }
});

onUnload(() => {
  if (typeof uni.offKeyboardHeightChange === 'function') {
    uni.offKeyboardHeightChange(onKeyboardHeightChange);
  }
});
</script>

<style scoped>
.create-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
  overflow: hidden;
}

.form-scroll {
  flex: 1;
  height: 0;
  padding: 20rpx 30rpx 0;
  box-sizing: border-box;
}

.scroll-anchor {
  height: 2rpx;
}

.form {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.form-item {
  margin-bottom: 30rpx;
}

.label {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
  display: block;
  margin-bottom: 16rpx;
}

.input,
.picker {
  width: 100%;
  padding: 20rpx;
  background: #f5f7fa;
  border-radius: 12rpx;
  font-size: 26rpx;
  color: #333;
  box-sizing: border-box;
}

.input {
  height: 80rpx;
  line-height: 80rpx;
  padding: 0 20rpx;
}

.picker {
  color: #333;
}

.picker-datetime {
  display: flex;
  align-items: center;
  min-height: 72rpx;
}

.picker-datetime.is-placeholder {
  color: #999;
}

.textarea {
  width: 100%;
  min-height: 200rpx;
  padding: 20rpx;
  background: #f5f7fa;
  border-radius: 12rpx;
  font-size: 26rpx;
  color: #333;
  box-sizing: border-box;
}

.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.06);
  z-index: 10;
}

.submit-btn {
  width: 100%;
  padding: 24rpx;
  background: linear-gradient(135deg, #20c997, #17a589);
  color: #fff;
  border-radius: 30rpx;
  font-size: 30rpx;
  font-weight: bold;
  border: none;
}
</style>
