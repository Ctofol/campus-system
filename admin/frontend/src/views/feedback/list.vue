<template>
  <el-card>
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span>用户反馈诊断记录</span>
        <el-button @click="load">刷新</el-button>
      </div>
    </template>
    <el-table :data="items" stripe v-loading="loading">
      <el-table-column label="序号" width="60" align="center">
        <template #default="{ $index }">{{ (page - 1) * size + $index + 1 }}</template>
      </el-table-column>
      <el-table-column prop="original_feedback" label="反馈内容" min-width="220" show-overflow-tooltip />
      <el-table-column prop="category" label="分类" width="120">
        <template #default="{ row }">
          <el-tag
            :type="categoryType(row.category)"
            size="small"
          >{{ row.category }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="severity" label="严重等级" width="90">
        <template #default="{ row }">
          <el-tag
            :type="severityType(row.severity)"
            size="small"
          >{{ row.severity }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="diagnosis" label="诊断" min-width="200" show-overflow-tooltip />
      <el-table-column prop="suggested_action" label="建议操作" min-width="220" show-overflow-tooltip />
      <el-table-column prop="logged_at" label="记录时间" width="180">
        <template #default="{ row }">{{ formatTime(row.logged_at) }}</template>
      </el-table-column>
    </el-table>
    <div style="margin-top:16px;text-align:right">
      <el-pagination
        v-model:current-page="page"
        :page-size="size"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="load"
      />
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getFeedback } from '../../api/index.js'
import { ElMessage } from 'element-plus'

const items = ref([])
const loading = ref(false)
const page = ref(1)
const size = ref(20)
const total = ref(0)

const load = async () => {
  loading.value = true
  try {
    const res = await getFeedback({ page: page.value, size: size.value })
    items.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    ElMessage.error(e?.detail || '加载失败')
  } finally {
    loading.value = false
  }
}

const categoryType = (c) => {
  const map = { Network: 'info', Path: 'warning', Permission: 'danger', Logic: '' }
  return map[c] || ''
}

const severityType = (s) => {
  if (s === 'P0') return 'danger'
  if (s === 'P1') return 'warning'
  return 'info'
}

const formatTime = (t) => {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN')
}

onMounted(load)
</script>
