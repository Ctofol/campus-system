<template>
  <el-card>
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
        <span>维护全校可选的<strong>体育选科</strong>名称；教师在「账号管理」中只能从本列表勾选管辖选科。</span>
      </div>
    </template>
    <div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;align-items:center">
      <el-input
        v-model="newName"
        placeholder="新选科名称，如：足球"
        clearable
        style="max-width:280px"
        @keyup.enter="addOne"
      />
      <el-button type="primary" :loading="adding" @click="addOne">添加</el-button>
      <el-button @click="load">刷新</el-button>
    </div>
    <el-table :data="rows" stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="72" />
      <el-table-column prop="name" label="选科名称" min-width="160" />
      <el-table-column label="操作" width="120" align="center">
        <template #default="{ row }">
          <el-button type="danger" link @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSubjects, createSubject, deleteSubject } from '../api/index.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const rows = ref([])
const newName = ref('')
const loading = ref(false)
const adding = ref(false)

const load = async () => {
  loading.value = true
  try {
    rows.value = await getSubjects()
  } catch (e) {
    ElMessage.error(e?.detail || '加载失败')
    rows.value = []
  } finally {
    loading.value = false
  }
}

const addOne = async () => {
  const name = (newName.value || '').trim()
  if (!name) {
    ElMessage.warning('请输入选科名称')
    return
  }
  adding.value = true
  try {
    await createSubject({ name })
    newName.value = ''
    ElMessage.success('已添加')
    await load()
  } catch (e) {
    ElMessage.error(e?.detail || '添加失败')
  } finally {
    adding.value = false
  }
}

const remove = async (row) => {
  await ElMessageBox.confirm(
    `确定删除选科「${row.name}」？已勾选该科的教师管辖绑定会被一并移除。`,
    '确认',
    { type: 'warning' }
  )
  try {
    await deleteSubject(row.id)
    ElMessage.success('已删除')
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e?.detail || '删除失败')
  }
}

onMounted(load)
</script>
