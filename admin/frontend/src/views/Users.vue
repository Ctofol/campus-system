<template>
  <el-card>
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap">
        <el-radio-group v-model="role" @change="load">
          <el-radio-button label="student">学生</el-radio-button>
          <el-radio-button label="teacher">教师</el-radio-button>
        </el-radio-group>
        <div style="display:flex;gap:8px;align-items:center" v-if="role === 'student'">
          <el-select v-model="filters.class_name" placeholder="按班级筛选" clearable style="min-width:140px" @change="load">
            <el-option
              v-for="cls in classOptions"
              :key="cls.name"
              :label="cls.name"
              :value="cls.name"
            />
          </el-select>
          <el-select v-model="filters.major" placeholder="按专业筛选" clearable style="min-width:140px" @change="load">
            <el-option
              v-for="m in majorOptions"
              :key="m"
              :label="m"
              :value="m"
            />
          </el-select>
        </div>
      </div>
    </template>
    <el-table :data="users" stripe>
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="phone" label="手机号" width="140" />
      <el-table-column v-if="role==='student'" prop="class_name" label="班级" width="140" />
      <el-table-column v-if="role==='student'" prop="major" label="专业" width="160" />
      <el-table-column v-if="role==='teacher'" label="工号/标识" width="140">
        <template #default="{row}">{{ row.student_id }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{row}">{{ row.created_at ? new Date(row.created_at).toLocaleDateString() : '-' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="260">
        <template #default="{row}">
          <el-button size="small" @click="handleReset(row)">重置密码</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          <el-button
            v-if="role==='teacher'"
            size="small"
            type="primary"
            @click="openAssignClasses(row)"
          >分配管辖班级</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="assignDialog.visible"
      title="分配管辖班级"
      width="480px"
    >
      <div style="margin-bottom:8px;color:#666">
        为教师「{{ assignDialog.teacher?.name || '' }}」选择可管辖的班级：
      </div>
      <el-checkbox-group v-model="assignDialog.selected">
        <el-checkbox
          v-for="cls in classOptions"
          :key="cls.name"
          :label="cls.name"
        >
          {{ cls.name }}
        </el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="assignDialog.visible=false">取 消</el-button>
        <el-button type="primary" @click="saveAssignClasses">保 存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getUsers, getUserMajors, deleteUser, resetPassword, getClasses, getTeacherClasses, updateTeacherClasses } from '../api/index.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const role = ref('student')
const users = ref([])
const classOptions = ref([])
const majorOptions = ref([])
const filters = ref({
  class_name: '',
  major: ''
})

const assignDialog = ref({
  visible: false,
  teacher: null,
  selected: []
})

const load = async () => {
  const params = { role: role.value }
  if (role.value === 'student') {
    if (filters.value.class_name) params.class_name = filters.value.class_name
    if (filters.value.major) params.major = filters.value.major
  }
  users.value = await getUsers(params)
  if (role.value === 'student' && majorOptions.value.length === 0) {
    try {
      majorOptions.value = await getUserMajors()
    } catch (_) {
      const majors = new Set()
      users.value.forEach(u => { if (u.major) majors.add(u.major) })
      majorOptions.value = Array.from(majors)
    }
  }
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

const openAssignClasses = async (teacher) => {
  assignDialog.value.teacher = teacher
  assignDialog.value.visible = true
  // 确保已有班级列表
  if (!classOptions.value.length) {
    classOptions.value = await getClasses()
  }
  const bound = await getTeacherClasses(teacher.id)
  assignDialog.value.selected = bound.map(item => item.class_name || item)
}

const saveAssignClasses = async () => {
  const t = assignDialog.value.teacher
  if (!t) return
  await updateTeacherClasses(t.id, { class_names: assignDialog.value.selected })
  assignDialog.value.visible = false
}

onMounted(async () => {
  classOptions.value = await getClasses()
  if (role.value === 'student') {
    try { majorOptions.value = await getUserMajors() } catch (_) {}
  }
  await load()
})
</script>
