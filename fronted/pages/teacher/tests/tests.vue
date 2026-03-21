<template>
  <teacher-tests ref="testsRef"></teacher-tests>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import TeacherTests from '@/components/teacher-tests/teacher-tests.vue';

const testsRef = ref(null);

// Lifecycle hooks for component
onMounted(() => {
  // Component will handle its own initialization
});

// Expose onShow/onHide for page lifecycle
defineExpose({
  onShow: () => {
    if (testsRef.value && testsRef.value.onPageShow) {
      testsRef.value.onPageShow();
    }
  },
  onHide: () => {
    if (testsRef.value && testsRef.value.onPageHide) {
      testsRef.value.onPageHide();
    }
  }
});
</script>

<style scoped>
/* No additional styles needed, component handles its own styling */
</style>
