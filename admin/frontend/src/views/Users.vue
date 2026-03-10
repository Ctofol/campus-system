<template>
  <el-card>
    <template #header>
      <el-radio-group v-model="role" @change="load">
        <el-radio-button label="student">学生</el-radio-button>
        <el-radio-button label="teacher">教师</el-radio-button>
      </el-radio-group>
    </template>
    <el-table :data="users" stripe>
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="phone" label="手机号" width="140" />
      <el-table-column label="班级/工号">
        <template #default="{row}">{{ role==='student' ? row.class_name : row.student_id }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{row}">{{ row.created_at ? new Date(row.created_at).toLocaleDateString() : '-' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{row}">
          <el-button size="small" @click="handleReset(row)">重置密码</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getUsers, deleteUser, resetPassword } from '../api/index.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const role = ref('student')
const users = ref([])

const load = async () => {
  users.value = await getUsers({ role: role.value })
}

const handleReset = async (row) => {
  await ElMessageBox.confirm(`重置「${row.name}」的密码为 123456？`, '确认')
  try {
    await resetPassword(row.id)
    ElMessage.success('重置成功')
  } catch(e) { ElMessage.error(e?.detail || '失败') }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm(`确定删除用户「${row.name}」？`, '确认', { type: 'warning' })
  try {
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    load()
  } catch(e) { ElMessage.error(e?.detail || '删除失败') }
}

onMounted(load)
</script>
