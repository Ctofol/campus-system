<template>
  <view>
    <StudentRun v-if="role === 'student'" ref="studentRunRef" />
    <view v-else-if="role === 'teacher'" class="teacher-placeholder">
      <text>教师端无跑步功能，请使用管理端</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import StudentRun from '@/components/student-run/student-run.vue';

const role = ref('student');
const studentRunRef = ref(null);

onShow(() => {
  const userRole = uni.getStorageSync('userRole') || uni.getStorageSync('role');
  if (userRole) role.value = userRole;

  if (role.value === 'student') {
     setTimeout(() => {
       if (studentRunRef.value) studentRunRef.value.onPageShow();
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
