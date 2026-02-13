<template>
  <view>
    <StudentMine v-if="role === 'student'" ref="studentMineRef" />
    <TeacherMine v-else-if="role === 'teacher'" ref="teacherMineRef" />
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import StudentMine from '@/components/student-mine/student-mine.vue';
import TeacherMine from '@/components/teacher-mine/teacher-mine.vue';

const role = ref('student');
const studentMineRef = ref(null);
const teacherMineRef = ref(null);

onShow(() => {
  const userRole = uni.getStorageSync('userRole') || uni.getStorageSync('role');
  if (userRole) role.value = userRole;

  setTimeout(() => {
    if (role.value === 'student' && studentMineRef.value) {
      studentMineRef.value.onPageShow();
    } else if (role.value === 'teacher' && teacherMineRef.value) {
      teacherMineRef.value.onPageShow();
    }
  }, 50);
});
</script>
