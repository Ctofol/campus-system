<template>
  <view>
    <StudentHome v-if="role === 'student'" ref="studentHomeRef" />
    <TeacherHome v-else-if="role === 'teacher'" ref="teacherHomeRef" />
    <view v-else class="loading-container">
      <text>加载中...</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import StudentHome from '@/components/student-home/student-home.vue';
import TeacherHome from '@/components/teacher-home/teacher-home.vue';

const role = ref('');
const studentHomeRef = ref(null);
const teacherHomeRef = ref(null);

onShow(() => {
  // Check token
  const token = uni.getStorageSync('token');
  if (!token) {
    uni.reLaunch({ url: '/pages/login/login' });
    return;
  }

  const userRole = uni.getStorageSync('userRole') || uni.getStorageSync('role');
  if (userRole) {
    role.value = userRole;
  } else {
     role.value = 'student'; // Default fallback
  }

  // Trigger child component onPageShow
  setTimeout(() => {
    if (role.value === 'student' && studentHomeRef.value) {
      studentHomeRef.value.onPageShow();
    } else if (role.value === 'teacher' && teacherHomeRef.value) {
      teacherHomeRef.value.onPageShow();
    }
  }, 50);
});
</script>

<style>
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
</style>
