<template>
  <view class="container">
    <student-mine v-if="role === 'student'" ref="studentMineRef" />
    <teacher-mine v-else ref="teacherMineRef" />
  </view>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import { onShow, onHide } from '@dcloudio/uni-app';
import StudentMine from '@/components/student-mine/student-mine.vue';
import TeacherMine from '@/components/teacher-mine/teacher-mine.vue';

const role = ref(uni.getStorageSync('userRole') || 'student');
const studentMineRef = ref(null);
const teacherMineRef = ref(null);

onShow(() => {
  role.value = uni.getStorageSync('userRole') || 'student';
  
  nextTick(() => {
    if (role.value === 'student' && studentMineRef.value && studentMineRef.value.onPageShow) {
      studentMineRef.value.onPageShow();
    } else if (role.value === 'teacher' && teacherMineRef.value && teacherMineRef.value.onPageShow) {
      teacherMineRef.value.onPageShow();
    }
  });
});

onHide(() => {
  if (role.value === 'student' && studentMineRef.value && studentMineRef.value.onPageHide) {
    studentMineRef.value.onPageHide();
  } else if (role.value === 'teacher' && teacherMineRef.value && teacherMineRef.value.onPageHide) {
    teacherMineRef.value.onPageHide();
  }
});
</script>

<style>
.container {
  height: 100%;
}
</style>