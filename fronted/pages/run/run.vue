<template>
  <view>
    <StudentRun v-if="role === 'student'" ref="studentRunRef" />
    <view v-else-if="role === 'teacher'" class="teacher-placeholder">
      <text>教师端无跑步功能，请使用管理端</text>
    </view>
  </view>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import { onShow, onLoad, onHide, onUnload } from '@dcloudio/uni-app';
import StudentRun from '@/components/student-run/student-run.vue';

const role = ref('student');
const studentRunRef = ref(null);
/** 由 onLoad 传入，再交给跑步组件（任务跑带 taskId / mode 等） */
const runLaunchOptions = ref({});

/** 子组件 ref 在首帧可能未就绪：nextTick + 短重试，避免从未触发 onPageShow（定位/概览不初始化） */
const invokeStudentRunShow = (attempt = 0) => {
  if (role.value !== 'student') return;
  nextTick(() => {
    if (studentRunRef.value?.onPageShow) {
      studentRunRef.value.onPageShow(runLaunchOptions.value || {});
    } else if (attempt < 40) {
      setTimeout(() => invokeStudentRunShow(attempt + 1), 50);
    }
  });
};

onLoad((options) => {
  runLaunchOptions.value = options || {};
  // onShow 偶发早于子组件挂载：onLoad 后再触发一次，减少「从未 onPageShow → 定位未初始化」
  nextTick(() => invokeStudentRunShow(0));
});

onShow(() => {
  const userRole = uni.getStorageSync('userRole') || uni.getStorageSync('role');
  if (userRole) role.value = userRole;
  invokeStudentRunShow(0);
});

const persistRunSession = () => {
  if (studentRunRef.value?.onPageHide) {
    studentRunRef.value.onPageHide();
  } else if (studentRunRef.value?.saveRunSession) {
    studentRunRef.value.saveRunSession();
  }
};

onHide(() => {
  persistRunSession();
});

onUnload(() => {
  persistRunSession();
});
</script>

<style>
.teacher-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  color: #999;
}
</style>
