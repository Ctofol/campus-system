<template>
  <view class="container">
    <student-home v-if="role === 'student'" ref="studentHomeRef" />
    <teacher-home v-else-if="role === 'teacher'" ref="teacherHomeRef" />
    <view v-else-if="role === 'admin'" class="admin-redirect">
      <text>正在跳转管理后台...</text>
    </view>
    <view v-else class="unknown-role">
      <text>未知角色: {{ role }}</text>
    </view>
  </view>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import { onShow, onHide } from '@dcloudio/uni-app';
import StudentHome from '@/components/student-home/student-home.vue';
import TeacherHome from '@/components/teacher-home/teacher-home.vue';

const role = ref(uni.getStorageSync('userRole') || 'student');
const studentHomeRef = ref(null);
const teacherHomeRef = ref(null);

onShow(() => {
  role.value = uni.getStorageSync('userRole') || 'student';
  
  if (role.value === 'teacher') {
    uni.setTabBarItem({
      index: 1,
      text: '管理',
      iconPath: '/static/tab/function.png',
      selectedIconPath: '/static/tab/function-active.png'
    });
    uni.setTabBarItem({
      index: 2,
      text: '监控',
      iconPath: '/static/tab/stats.png',
      selectedIconPath: '/static/tab/stats-active.png'
    });
  } else if (role.value === 'admin') {
    // Admin should not be here, redirect to dashboard
    uni.reLaunch({
      url: '/pages/admin/dashboard/index'
    });
  } else {
    uni.setTabBarItem({
      index: 1,
      text: '跑步',
      iconPath: '/static/tab/run.png',
      selectedIconPath: '/static/tab/run-active.png'
    });
    uni.setTabBarItem({
      index: 2,
      text: '体测',
      iconPath: '/static/tab/test.png',
      selectedIconPath: '/static/tab/test-active.png'
    });
  }

  // Lifecycle passing
  nextTick(() => {
    if (role.value === 'student' && studentHomeRef.value && studentHomeRef.value.onPageShow) {
      studentHomeRef.value.onPageShow();
    } else if (role.value === 'teacher' && teacherHomeRef.value && teacherHomeRef.value.onPageShow) {
      teacherHomeRef.value.onPageShow();
    }
  });
});

onHide(() => {
  if (role.value === 'student' && studentHomeRef.value && studentHomeRef.value.onPageHide) {
    studentHomeRef.value.onPageHide();
  } else if (role.value === 'teacher' && teacherHomeRef.value && teacherHomeRef.value.onPageHide) {
    teacherHomeRef.value.onPageHide();
  }
});
</script>

<style>
.container {
  height: 100%;
}
.admin-redirect, .unknown-role {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-size: 16px;
  color: #666;
}
</style>