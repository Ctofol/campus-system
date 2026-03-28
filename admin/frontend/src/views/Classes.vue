<template>
  <el-card>
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span>班级列表</span>
        <el-button type="primary" @click="showDialog=true">+ 新增班级</el-button>
      </div>
    </template>
    <el-table :data="classes" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="major_name" label="所属专业" width="150" />
      <el-table-column prop="name" label="班级名称" />
      <el-table-column prop="teacher_id" label="绑定教师ID" width="120">
        <template #default="{row}">{{ row.teacher_id || '-' }}</template>
      </el-table-column>
      <el-table-column prop="student_count" label="学生人数" width="100" />
      <el-table-column label="操作" width="100">
        <template #default="{row}">
          <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="showDialog" title="新增班级" width="400px">
    <el-form label-width="80px">
      <el-form-item label="所属专业">
        <el-select v-model="selectedMajorId" placeholder="请选择专业" style="width:100%">
          <el-option v-for="m in majors" :key="m.id" :label="m.name" :value="m.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="班级名称">
        <el-input v-model="newName" placeholder="请输入班级名称 (如: 1区)" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showDialog=false">取消</el-button>
      <el-button type="primary" @click="handleCreate">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getClasses, createClass, deleteClass, getMajors } from '../api/index.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const classes = ref([])
const majors = ref([])
const showDialog = ref(false)
const newName = ref('')
const selectedMajorId = ref(null)

const load = async () => {
  classes.value = await getClasses()
  majors.value = await getMajors()
}

const handleCreate = async () => {
  if (!newName.value || !selectedMajorId.value) {
    return ElMessage.warning('请填写完整信息')
  }
  try {
    await createClass({ 
      name: newName.value,
      major_id: selectedMajorId.value 
    })
    ElMessage.success('创建成功')
    showDialog.value = false
    newName.value = ''
    selectedMajorId.value = null
    load()
  } catch(e) { ElMessage.error(e?.detail || '创建失败') }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm(`确定删除班级「${row.name}」？`, '确认', { type: 'warning' })
  try {
    await deleteClass(row.id)
    ElMessage.success('删除成功')
    load()
  } catch(e) { ElMessage.error(e?.detail || '删除失败') }
}

onMounted(load)
</script>
