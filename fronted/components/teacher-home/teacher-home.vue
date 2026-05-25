<template>
  <HomePage ref="homeRef" />
</template>

<script setup>
import { ref } from 'vue';
import HomePage from '@/pages/teacher/home/home.vue';

const homeRef = ref(null);

const onPageShow = () => {
  homeRef.value?.onPageShow?.();
};

defineExpose({
  onPageShow
});
</script>

<style scoped>
/* 这里可以按需覆盖额外样式，目前直接使用 HomePage 自带样式 */
</style>
