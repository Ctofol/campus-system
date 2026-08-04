<template>
  <div v-loading="loading">
    <el-card>
      <template #header>
        <div class="header-row">
          <span>上传存储盘点</span>
          <el-button :loading="loading" @click="load">重新盘点</el-button>
        </div>
      </template>

      <el-alert
        title="本页面仅做只读统计，不会移动或删除文件；未引用候选仍需人工确认。"
        type="info"
        :closable="false"
        show-icon
        class="notice"
      />

      <el-row :gutter="16">
        <el-col v-for="item in summaryCards" :key="item.label" :xs="12" :sm="8" :lg="4">
          <div class="stat-card">
            <div class="stat-value">{{ item.value }}</div>
            <div class="stat-label">{{ item.label }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="16" class="content-row">
      <el-col :xs="24" :lg="9">
        <el-card header="按目录统计">
          <el-empty v-if="directoryRows.length === 0" description="暂无文件" :image-size="72" />
          <el-table v-else :data="directoryRows" size="small">
            <el-table-column prop="name" label="目录" />
            <el-table-column prop="count" label="文件数" width="100" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="15">
        <el-card header="未引用候选（按体积排序，最多显示 50 项）">
          <el-empty v-if="candidates.length === 0" description="没有发现候选文件" :image-size="72" />
          <el-table v-else :data="candidates" size="small" max-height="460">
            <el-table-column prop="path" label="相对路径" min-width="280" show-overflow-tooltip />
            <el-table-column label="大小" width="110">
              <template #default="{ row }">{{ formatBytes(row.size_bytes) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getStorageUsage } from '../../api/index.js'

const loading = ref(false)
const data = ref({ by_month: {}, candidates: [] })

const formatBytes = bytes => {
  const value = Number(bytes || 0)
  if (value < 1024) return `${value} B`
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`
  return `${(value / 1024 / 1024).toFixed(2)} MB`
}
const summaryCards = computed(() => [
  { label: '文件总数', value: data.value.total_files ?? 0 },
  { label: '占用空间', value: formatBytes(data.value.total_bytes) },
  { label: '已引用文件', value: data.value.referenced_files ?? 0 },
  { label: '未引用候选', value: data.value.unreferenced_files ?? 0 },
  { label: '缺失引用', value: data.value.missing_references ?? 0 },
  { label: '目录状态', value: data.value.status === 'ok' ? '正常' : '不存在' },
])
const directoryRows = computed(() => Object.entries(data.value.by_month || {}).map(([name, count]) => ({ name, count })))
const candidates = computed(() => data.value.candidates || [])

const load = async () => {
  loading.value = true
  try {
    data.value = await getStorageUsage({ candidate_limit: 50 })
  } catch (error) {
    ElMessage.error(error?.detail || '上传存储盘点失败')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.header-row { display: flex; justify-content: space-between; align-items: center; }
.notice { margin-bottom: 18px; }
.stat-card { padding: 18px 12px; border: 1px solid #ebeef5; border-radius: 6px; text-align: center; }
.stat-value { color: #303133; font-size: 22px; font-weight: 600; }
.stat-label { margin-top: 8px; color: #909399; font-size: 13px; }
.content-row { margin-top: 16px; }
@media (max-width: 1199px) { .content-row .el-col + .el-col { margin-top: 16px; } }
</style>
