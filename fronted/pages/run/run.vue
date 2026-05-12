<template>
  <view>
    <StudentRun v-if="role === 'student'" ref="studentRunRef" />
    <view v-else-if="role === 'teacher'" class="teacher-placeholder">
      <text>教师端无跑步功能，请使用管理端</text>
    </view>
    <!-- 与首页一致：微信隐私合规模块，未同意时 getLocation/选图等会失败 -->
    <privacy-popup />
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow, onLoad } from '@dcloudio/uni-app';
import StudentRun from '@/components/student-run/student-run.vue';
import PrivacyPopup from '@/components/privacy-popup/privacy-popup.vue';

const role = ref('student');
const studentRunRef = ref(null);
/** 由 onLoad 传入，再交给跑步组件（任务跑带 taskId / mode 等） */
const runLaunchOptions = ref({});

onLoad((options) => {
  runLaunchOptions.value = options || {};
});

onShow(() => {
  const userRole = uni.getStorageSync('userRole') || uni.getStorageSync('role');
  if (userRole) role.value = userRole;

  if (role.value === 'student') {
     setTimeout(() => {
       if (studentRunRef.value) {
         studentRunRef.value.onPageShow(runLaunchOptions.value || {});
       }
     }, 50);
  }
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
