<template>
  <el-card>
    <template #header>
      <div class="header-row">
        <span>关键操作记录</span>
        <el-button :loading="loading" @click="loadList">刷新</el-button>
      </div>
    </template>

    <el-form inline class="filters" @submit.prevent>
      <el-form-item label="操作类型">
        <el-select v-model="filters.action" clearable placeholder="全部操作" style="width: 180px">
          <el-option v-for="item in actionOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="对象类型">
        <el-select v-model="filters.resource_type" clearable placeholder="全部对象" style="width: 150px">
          <el-option label="用户" value="user" />
          <el-option label="任务" value="task" />
          <el-option label="活动记录" value="activity" />
          <el-option label="健康报备" value="health_request" />
        </el-select>
      </el-form-item>
      <el-form-item label="操作人 ID">
        <el-input-number v-model="filters.actor_user_id" :controls="false" :min="1" placeholder="全部" style="width: 120px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="items" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="操作人" min-width="130">
        <template #default="{ row }">
          {{ row.actor_name }}
          <span v-if="row.actor_user_id" class="muted">#{{ row.actor_user_id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="160">
        <template #default="{ row }"><el-tag effect="plain">{{ actionLabel(row.action) }}</el-tag></template>
      </el-table-column>
      <el-table-column label="对象" min-width="150">
        <template #default="{ row }">{{ resourceLabel(row.resource_type) }} #{{ row.resource_id || '-' }}</template>
      </el-table-column>
      <el-table-column label="说明" min-width="220" show-overflow-tooltip>
        <template #default="{ row }">{{ detailText(row.detail) }}</template>
      </el-table-column>
      <el-table-column label="时间" width="180">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>
    <div class="pagination">
      <el-pagination
        v-model:current-page="page"
        :page-size="size"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadList"
      />
    </div>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getAuditLogs } from '../../api/index.js'

const actionOptions = [
  { value: 'user.delete', label: '删除用户' },
  { value: 'user.reset_password', label: '重置密码' },
  { value: 'task.create', label: '发布任务' },
  { value: 'task.remind_unfinished', label: '提醒未完成学生' },
  { value: 'health_request.review', label: '审核健康报备' },
  { value: 'activity.score', label: '活动评分' },
]
const actionNames = Object.fromEntries(actionOptions.map(item => [item.value, item.label]))
const resourceNames = { user: '用户', task: '任务', activity: '活动记录', health_request: '健康报备' }

const items = ref([])
const loading = ref(false)
const page = ref(1)
const size = ref(20)
const total = ref(0)
const filters = reactive({ action: '', resource_type: '', actor_user_id: null })

const formatTime = value => value ? new Date(value).toLocaleString('zh-CN') : ''
const actionLabel = value => actionNames[value] || value || '-'
const resourceLabel = value => resourceNames[value] || value || '-'
const detailText = value => {
  if (!value) return '-'
  try {
    const detail = JSON.parse(value)
    return Object.entries(detail).map(([key, item]) => `${key}: ${item}`).join('；') || '-'
  } catch {
    return value
  }
}

const loadList = async () => {
  loading.value = true
  try {
    const params = { page: page.value, size: size.value }
    if (filters.action) params.action = filters.action
    if (filters.resource_type) params.resource_type = filters.resource_type
    if (filters.actor_user_id) params.actor_user_id = filters.actor_user_id
    const res = await getAuditLogs(params)
    items.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    ElMessage.error(error?.detail || '加载操作记录失败')
  } finally {
    loading.value = false
  }
}
const search = () => { page.value = 1; loadList() }
const resetFilters = () => {
  filters.action = ''
  filters.resource_type = ''
  filters.actor_user_id = null
  search()
}

onMounted(loadList)
</script>

<style scoped>
.header-row { display: flex; justify-content: space-between; align-items: center; }
.filters { margin-bottom: 2px; }
.muted { margin-left: 4px; color: #909399; font-size: 12px; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
