<template>
  <div>
    <el-card style="margin-bottom:16px">
      <template #header>发送新通知</template>
      <el-form :model="form" label-width="100px">
        <el-form-item label="通知标题" required>
          <el-input v-model="form.title" placeholder="请输入通知标题" maxlength="100" />
        </el-form-item>
        <el-form-item label="通知内容">
          <el-input v-model="form.content" type="textarea" :rows="3" placeholder="请输入通知内容" maxlength="500" />
        </el-form-item>
        <el-form-item label="通知类型">
          <el-select v-model="form.ntype" style="width:200px">
            <el-option label="系统通知" value="system" />
            <el-option label="审核结果" value="health_review" />
            <el-option label="任务提醒" value="task" />
          </el-select>
        </el-form-item>
        <el-form-item label="发送范围" required>
          <el-radio-group v-model="form.target">
            <el-radio value="all">全体师生</el-radio>
            <el-radio value="students">所有学生</el-radio>
            <el-radio value="teachers">所有教师</el-radio>
            <el-radio value="single">指定用户</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.target === 'single'" label="用户ID" required>
          <el-input-number v-model="form.target_user_id" :min="1" placeholder="请输入用户ID" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="sending" @click="send">发送通知</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>已发送通知记录</span>
          <el-button @click="loadList">刷新</el-button>
        </div>
      </template>
      <el-table :data="items" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="72" />
        <el-table-column prop="title" label="标题" min-width="160" />
        <el-table-column prop="body" label="内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ntype" label="类型" width="110" />
        <el-table-column prop="user_id" label="接收用户" width="100" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_read ? 'success' : 'info'" size="small">
              {{ row.is_read ? '已读' : '未读' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="发送时间" width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
      </el-table>
      <div style="margin-top:16px;text-align:right">
        <el-pagination
          v-model:current-page="page"
          :page-size="size"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadList"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getNotifications, createNotification } from '../../api/index.js'
import { ElMessage } from 'element-plus'

const form = ref({
  title: '',
  content: '',
  ntype: 'system',
  target: 'all',
  target_user_id: null,
})

const items = ref([])
const loading = ref(false)
const sending = ref(false)
const page = ref(1)
const size = ref(20)
const total = ref(0)

const send = async () => {
  if (!form.value.title.trim()) {
    ElMessage.warning('请输入通知标题')
    return
  }
  if (form.value.target === 'single' && !form.value.target_user_id) {
    ElMessage.warning('请输入目标用户ID')
    return
  }
  sending.value = true
  try {
    const data = {
      title: form.value.title,
      content: form.value.content,
      ntype: form.value.ntype,
      target: form.value.target,
    }
    if (form.value.target === 'single') {
      data.target_user_id = form.value.target_user_id
    }
    const res = await createNotification(data)
    ElMessage.success(`已发送给 ${res.sent} 人`)
    form.value = { title: '', content: '', ntype: 'system', target: 'all', target_user_id: null }
    await loadList()
  } catch (e) {
    ElMessage.error(e?.detail || '发送失败')
  } finally {
    sending.value = false
  }
}

const loadList = async () => {
  loading.value = true
  try {
    const res = await getNotifications({ page: page.value, size: size.value })
    items.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    ElMessage.error(e?.detail || '加载失败')
  } finally {
    loading.value = false
  }
}

const formatTime = (t) => {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN')
}

onMounted(loadList)
</script>
