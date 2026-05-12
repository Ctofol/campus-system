<template>
  <el-card>
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
        <div>
          <span>班级列表</span>
          <span style="margin-left:12px;color:#888;font-size:13px">「绑定教师」对应班级上的负责教师（教师端按班级管辖学生之一）；另可在账号管理里为教师分配「管辖选科」或按行政班名称关联。</span>
        </div>
        <el-button type="primary" @click="openCreate">+ 新增班级</el-button>
      </div>
    </template>
    <el-table :data="classes" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="major_name" label="所属专业" width="150" />
      <el-table-column prop="name" label="班级名称" min-width="120" />
      <el-table-column label="绑定教师" min-width="200">
        <template #default="{ row }">
          <span v-if="row.teacher_name">{{ row.teacher_name }}</span>
          <span v-else style="color:#999">未绑定</span>
          <span v-if="row.teacher_id" style="color:#aaa;font-size:12px">（ID {{ row.teacher_id }}）</span>
        </template>
      </el-table-column>
      <el-table-column prop="student_count" label="学生人数" width="100" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="openBind(row)">绑定教师</el-button>
          <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="showDialog" title="新增班级" width="440px" @closed="resetCreate">
    <el-form label-width="96px">
      <el-form-item label="所属专业">
        <el-select v-model="selectedMajorId" placeholder="请选择专业" style="width:100%">
          <el-option v-for="m in majors" :key="m.id" :label="m.name" :value="m.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="班级名称">
        <el-input v-model="newName" placeholder="请输入行政班名称（如：信息安全1区）" />
      </el-form-item>
      <el-form-item label="绑定教师">
        <el-select
          v-model="createTeacherId"
          placeholder="可选：指定本班负责教师"
          clearable
          filterable
          style="width:100%"
        >
          <el-option
            v-for="t in teachers"
            :key="t.id"
            :label="`${t.name}（${t.phone}）`"
            :value="t.id"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showDialog=false">取消</el-button>
      <el-button type="primary" @click="handleCreate">确定</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="bindDialog.visible" title="绑定教师" width="440px" @closed="bindDialog.row = null">
    <div v-if="bindDialog.row" style="margin-bottom:12px;color:#666;font-size:13px">
      班级：<strong>{{ bindDialog.row.name }}</strong>
    </div>
    <el-select
      v-model="bindDialog.teacherId"
      placeholder="选择教师，留空并保存则解除绑定"
      clearable
      filterable
      style="width:100%"
    >
      <el-option
        v-for="t in teachers"
        :key="t.id"
        :label="`${t.name}（${t.phone}）`"
        :value="t.id"
      />
    </el-select>
    <template #footer>
      <el-button @click="bindDialog.visible = false">取消</el-button>
      <el-button type="primary" :loading="bindDialog.saving" @click="saveBind">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getClasses, createClass, patchClass, deleteClass, getMajors, getUsers } from '../api/index.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const classes = ref([])
const majors = ref([])
const teachers = ref([])
const showDialog = ref(false)
const newName = ref('')
const selectedMajorId = ref(null)
const createTeacherId = ref(null)

const bindDialog = ref({
  visible: false,
  row: null,
  teacherId: null,
  saving: false
})

const loadTeachers = async () => {
  try {
    teachers.value = await getUsers({ role: 'teacher', limit: 500 })
  } catch (_) {
    teachers.value = []
  }
}

const load = async () => {
  classes.value = await getClasses()
  majors.value = await getMajors()
}

const openCreate = () => {
  resetCreate()
  showDialog.value = true
}

const resetCreate = () => {
  newName.value = ''
  selectedMajorId.value = null
  createTeacherId.value = null
}

const handleCreate = async () => {
  if (!newName.value || !selectedMajorId.value) {
    return ElMessage.warning('请填写专业与班级名称')
  }
  try {
    await createClass({
      name: newName.value.trim(),
      major_id: selectedMajorId.value,
      teacher_id: createTeacherId.value ?? undefined
    })
    ElMessage.success('创建成功')
    showDialog.value = false
    resetCreate()
    load()
  } catch (e) {
    ElMessage.error(e?.detail || '创建失败')
  }
}

const openBind = (row) => {
  bindDialog.value.row = row
  bindDialog.value.teacherId = row.teacher_id ?? null
  bindDialog.value.visible = true
}

const saveBind = async () => {
  const row = bindDialog.value.row
  if (!row) return
  bindDialog.value.saving = true
  try {
    await patchClass(row.id, { teacher_id: bindDialog.value.teacherId ?? null })
    ElMessage.success('已保存')
    bindDialog.value.visible = false
    load()
  } catch (e) {
    ElMessage.error(e?.detail || '保存失败')
  } finally {
    bindDialog.value.saving = false
  }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm(`确定删除班级「${row.name}」？`, '确认', { type: 'warning' })
  try {
    await deleteClass(row.id)
    ElMessage.success('删除成功')
    load()
  } catch (e) {
    ElMessage.error(e?.detail || '删除失败')
  }
}

onMounted(async () => {
  await loadTeachers()
  await load()
})
</script>
