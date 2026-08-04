<template>
  <el-card v-loading="loading">
    <template #header><div style="display:flex;justify-content:space-between"><span>系统健康状态</span><el-button @click="load">刷新</el-button></div></template>
    <el-alert :title="statusText" :type="data.status === 'ok' ? 'success' : 'warning'" :closable="false" show-icon style="margin-bottom:16px" />
    <el-descriptions :column="1" border>
      <el-descriptions-item label="数据库"><el-tag :type="tagType(data.checks?.database)">{{ data.checks?.database || '-' }}</el-tag></el-descriptions-item>
      <el-descriptions-item label="文件存储"><el-tag :type="tagType(data.checks?.storage)">{{ data.checks?.storage || '-' }}</el-tag></el-descriptions-item>
      <el-descriptions-item label="可用存储空间">{{ data.storage?.free_mb ?? '-' }} MB</el-descriptions-item>
      <el-descriptions-item label="人脸核验"><el-tag :type="tagType(data.checks?.face_verification)">{{ data.checks?.face_verification || '-' }}</el-tag></el-descriptions-item>
    </el-descriptions>
  </el-card>
</template>
<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getSystemHealth } from '../../api/index.js'
const data = ref({ checks: {}, storage: {} }); const loading = ref(false)
const statusText = computed(() => data.value.status === 'ok' ? '系统运行正常' : '系统部分服务需要关注')
const tagType = (value) => ['ok', 'configured'].includes(value) ? 'success' : value === 'disabled' ? 'info' : 'warning'
const load = async () => { loading.value = true; try { data.value = await getSystemHealth() } catch (error) { data.value = error?.detail ? { checks: {}, storage: {}, status: 'degraded' } : data.value; ElMessage.error(error?.detail || '健康检查失败') } finally { loading.value = false } }
onMounted(load)
</script>
