<template>
  <view class="container">
    <student-run v-if="role === 'student'" ref="studentRunRef" />
    <teacher-manage v-else ref="teacherManageRef" />
  </view>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import { onShow, onHide } from '@dcloudio/uni-app';
import StudentRun from '@/components/student-run/student-run.vue';
import TeacherManage from '@/components/teacher-manage/teacher-manage.vue';

const role = ref(uni.getStorageSync('userRole') || 'student');
const studentRunRef = ref(null);
const teacherManageRef = ref(null);

onShow(() => {
  role.value = uni.getStorageSync('userRole') || 'student';
  
  // 确保组件已挂载后调用生命周期
  nextTick(() => {
    if (role.value === 'student' && studentRunRef.value && studentRunRef.value.onPageShow) {
      studentRunRef.value.onPageShow();
    } else if (role.value === 'teacher' && teacherManageRef.value && teacherManageRef.value.onPageShow) {
      teacherManageRef.value.onPageShow();
    }
  });
});

onHide(() => {
  if (role.value === 'student' && studentRunRef.value && studentRunRef.value.onPageHide) {
    studentRunRef.value.onPageHide();
  } else if (role.value === 'teacher' && teacherManageRef.value && teacherManageRef.value.onPageHide) {
    teacherManageRef.value.onPageHide();
  }
});
</script>

<style>
.container {
  height: 100%;
}
</style>