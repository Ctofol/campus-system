<template>
  <!-- 复用真正的教师首页页面，实现与线上一致的样式 -->
  <HomePage />
</template>

<script setup>
// HBuilderX tab 页入口使用的教师首页包装组件，
// 直接复用 pages/teacher/home/home.vue，确保样式和逻辑保持一致。
import HomePage from '@/pages/teacher/home/home.vue';
</script>

<style scoped>
/* 这里可以按需覆盖额外样式，目前直接使用 HomePage 自带样式 */
</style>
