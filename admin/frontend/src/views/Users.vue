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
      <el-table-column v-if="role==='student'" label="班级（行政班）" width="160">
        <template #default="{ row }">{{ row.plain_class_name || '-' }}</template>
      </el-table-column>
      <el-table-column v-if="role==='student'" prop="major" label="专业（Major）" width="160" />
      <el-table-column v-if="role==='student'" prop="subject" label="体育选科" width="120" />
      <el-table-column v-if="role==='teacher'" label="工号/标识" width="140">
        <template #default="{row}">{{ row.student_id }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{row}">{{ row.created_at ? new Date(row.created_at).toLocaleDateString() : '-' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="480">
        <template #default="{row}">
          <el-button
            v-if="role==='student'"
            size="small"
            type="primary"
            plain
            @click="openSportDialog(row)"
          >运动记录</el-button>
          <el-button size="small" @click="handleReset(row)">重置密码</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          <el-button
            v-if="role==='teacher'"
            size="small"
            type="primary"
            @click="openAssignSubjects(row)"
          >分配管辖选科</el-button>
          <el-button
            v-if="role==='teacher'"
            size="small"
            type="success"
            plain
            @click="openBindStudents(row)"
          >绑定学员</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="sportDialog.visible"
      :title="sportDialog.title"
      width="920px"
      destroy-on-close
      @closed="onSportDialogClosed"
    >
      <div style="margin-bottom:12px;color:#666;font-size:13px">
        含阳光跑、任务跑步、体测等提交记录；「类型」为业务归类，便于与管理口径一致。
      </div>
      <el-table :data="sportDialog.rows" stripe v-loading="sportDialog.loading" max-height="420">
        <el-table-column prop="record_kind" label="类型" width="100" />
        <el-table-column prop="started_at" label="开始时间" width="170">
          <template #default="{ row }">{{ formatDt(row.started_at) }}</template>
        </el-table-column>
        <el-table-column prop="ended_at" label="结束时间" width="170">
          <template #default="{ row }">{{ formatDt(row.ended_at) }}</template>
        </el-table-column>
        <el-table-column label="达标" width="72" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_valid ? 'success' : 'info'" size="small">{{ row.is_valid ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="距离(km)" width="88" align="right">
          <template #default="{ row }">{{ row.distance_km != null ? Number(row.distance_km).toFixed(2) : '-' }}</template>
        </el-table-column>
        <el-table-column prop="duration_sec" label="时长(秒)" width="88" align="right">
          <template #default="{ row }">{{ row.duration_sec != null ? row.duration_sec : '-' }}</template>
        </el-table-column>
        <el-table-column prop="pace" label="配速" width="90" show-overflow-tooltip />
        <el-table-column prop="task_title" label="关联任务" min-width="120" show-overflow-tooltip />
        <el-table-column prop="fail_reason" label="说明" min-width="140" show-overflow-tooltip />
      </el-table>
      <div style="margin-top:12px;display:flex;justify-content:flex-end">
        <el-pagination
          layout="total, prev, pager, next"
          :total="sportDialog.total"
          :page-size="sportDialog.size"
          :current-page="sportDialog.page"
          @current-change="onSportPageChange"
        />
      </div>
    </el-dialog>

    <el-dialog
      v-model="assignDialog.visible"
      title="分配管辖选科"
      width="480px"
    >
      <div style="margin-bottom:8px;color:#666">
        为教师「{{ assignDialog.teacher?.name || '' }}」选择可管辖的体育选科（列表来自「选科管理」）：
      </div>
      <el-checkbox-group v-model="assignDialog.selected">
        <el-checkbox
          v-for="sub in subjectOptions"
          :key="sub.id"
          :label="sub.name"
        >
          {{ sub.name }}
        </el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="assignDialog.visible=false">取 消</el-button>
        <el-button type="primary" @click="saveAssignSubjects">保 存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="bindStudentsDialog.visible"
      title="绑定学员"
      width="640px"
      destroy-on-close
      @closed="onBindStudentsClosed"
    >
      <div v-if="bindStudentsDialog.teacher" style="margin-bottom:12px;color:#666;font-size:13px">
        教师：<strong>{{ bindStudentsDialog.teacher.name }}</strong>
        （显式绑定的学员会出现在该教师小程序「学员管理」中，与选科/班级管辖<strong>合并</strong>）
      </div>
      <div v-loading="bindStudentsDialog.loading">
        <div style="margin-bottom:16px;font-weight:600">已绑定学员</div>
        <el-table :data="bindStudentsDialog.bound" size="small" max-height="220" stripe>
          <el-table-column prop="name" label="姓名" width="100" />
          <el-table-column prop="phone" label="手机号" width="130" />
          <el-table-column label="学号" min-width="120">
            <template #default="{ row }">{{ row.student_id || '—' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="88" align="center">
            <template #default="{ row }">
              <el-button type="danger" link size="small" @click="removeBoundStudent(row)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div style="margin:20px 0 8px;font-weight:600">添加学员</div>
        <el-select
          v-model="bindStudentsDialog.toAddIds"
          multiple
          filterable
          collapse-tags
          collapse-tags-tooltip
          placeholder="搜索姓名/手机号，可多选"
          style="width:100%"
        >
          <el-option
            v-for="s in bindStudentsPickerOptions"
            :key="s.id"
            :label="`${s.name} · ${s.phone}${s.student_id ? ' · ' + s.student_id : ''}`"
            :value="s.id"
          />
        </el-select>
        <div style="margin-top:12px">
          <el-button type="primary" :loading="bindStudentsDialog.adding" :disabled="!bindStudentsDialog.toAddIds.length" @click="submitAddBoundStudents">
            添加选中
          </el-button>
        </div>
      </div>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import {
  getUsers,
  getUserMajors,
  deleteUser,
  resetPassword,
  getClasses,
  getTeacherSubjects,
  updateTeacherSubjects,
  getStudentActivities,
  getSubjects,
  getTeacherBoundStudents,
  addTeacherBoundStudents,
  removeTeacherBoundStudent
} from '../api/index.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const role = ref('student')
const users = ref([])
const classOptions = ref([])
const majorOptions = ref([])
const subjectOptions = ref([])
const filters = ref({
  class_name: '',
  major: ''
})

const assignDialog = ref({
  visible: false,
  teacher: null,
  selected: []
})

const bindStudentsDialog = ref({
  visible: false,
  teacher: null,
  bound: [],
  allStudents: [],
  toAddIds: [],
  loading: false,
  adding: false
})

const bindStudentsPickerOptions = computed(() => {
  const boundIds = new Set((bindStudentsDialog.value.bound || []).map((b) => b.id))
  return (bindStudentsDialog.value.allStudents || []).filter((s) => !boundIds.has(s.id))
})

const sportDialog = ref({
  visible: false,
  title: '运动记录',
  student: null,
  rows: [],
  total: 0,
  page: 1,
  size: 20,
  loading: false
})

const formatDt = (v) => {
  if (!v) return '-'
  const d = new Date(v)
  if (Number.isNaN(d.getTime())) return String(v)
  return d.toLocaleString('zh-CN', { hour12: false })
}

const loadSportPage = async () => {
  const stu = sportDialog.value.student
  if (!stu) return
  sportDialog.value.loading = true
  try {
    const res = await getStudentActivities(stu.id, {
      page: sportDialog.value.page,
      size: sportDialog.value.size
    })
    sportDialog.value.rows = res.items || []
    sportDialog.value.total = res.total || 0
  } catch (e) {
    ElMessage.error(e?.detail || '加载运动记录失败')
    sportDialog.value.rows = []
    sportDialog.value.total = 0
  } finally {
    sportDialog.value.loading = false
  }
}

const openSportDialog = (row) => {
  sportDialog.value.student = row
  sportDialog.value.title = `运动记录 — ${row.name || ''}（学号 ${row.student_id || '-'}）`
  sportDialog.value.page = 1
  sportDialog.value.visible = true
  loadSportPage()
}

const onSportPageChange = (p) => {
  sportDialog.value.page = p
  loadSportPage()
}

const onSportDialogClosed = () => {
  sportDialog.value.student = null
  sportDialog.value.rows = []
  sportDialog.value.total = 0
  sportDialog.value.page = 1
}

const load = async () => {
  const params = { role: role.value }
  if (role.value === 'student') {
    if (filters.value.class_name) params.class_name = filters.value.class_name
    if (filters.value.major) params.major = filters.value.major
  }
  users.value = await getUsers(params)
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

const loadSubjectOptions = async () => {
  try {
    subjectOptions.value = await getSubjects()
  } catch (_) {
    subjectOptions.value = []
  }
}

const openAssignSubjects = async (teacher) => {
  await loadSubjectOptions()
  assignDialog.value.teacher = teacher
  assignDialog.value.visible = true
  const bound = await getTeacherSubjects(teacher.id)
  assignDialog.value.selected = bound.map(item => item.name || item)
}

const saveAssignSubjects = async () => {
  const t = assignDialog.value.teacher
  if (!t) return
  await updateTeacherSubjects(t.id, { subject_names: assignDialog.value.selected })
  assignDialog.value.visible = false
  ElMessage.success('分配成功')
}

const onBindStudentsClosed = () => {
  bindStudentsDialog.value.teacher = null
  bindStudentsDialog.value.bound = []
  bindStudentsDialog.value.allStudents = []
  bindStudentsDialog.value.toAddIds = []
}

const openBindStudents = async (teacher) => {
  bindStudentsDialog.value.teacher = teacher
  bindStudentsDialog.value.visible = true
  bindStudentsDialog.value.loading = true
  bindStudentsDialog.value.toAddIds = []
  try {
    const [bound, all] = await Promise.all([
      getTeacherBoundStudents(teacher.id),
      getUsers({ role: 'student', limit: 500 })
    ])
    bindStudentsDialog.value.bound = bound || []
    bindStudentsDialog.value.allStudents = all || []
  } catch (e) {
    ElMessage.error(e?.detail || '加载失败')
    bindStudentsDialog.value.bound = []
    bindStudentsDialog.value.allStudents = []
  } finally {
    bindStudentsDialog.value.loading = false
  }
}

const reloadBoundStudents = async () => {
  const t = bindStudentsDialog.value.teacher
  if (!t) return
  bindStudentsDialog.value.bound = await getTeacherBoundStudents(t.id)
}

const submitAddBoundStudents = async () => {
  const t = bindStudentsDialog.value.teacher
  const ids = bindStudentsDialog.value.toAddIds
  if (!t || !ids.length) return
  bindStudentsDialog.value.adding = true
  try {
    const res = await addTeacherBoundStudents(t.id, { student_user_ids: ids })
    ElMessage.success(res.added != null ? `已添加 ${res.added} 人` : '已保存')
    bindStudentsDialog.value.toAddIds = []
    await reloadBoundStudents()
  } catch (e) {
    ElMessage.error(e?.detail || '添加失败')
  } finally {
    bindStudentsDialog.value.adding = false
  }
}

const removeBoundStudent = async (row) => {
  const t = bindStudentsDialog.value.teacher
  if (!t) return
  await ElMessageBox.confirm(`移除「${row.name}」与该教师的绑定？`, '确认', { type: 'warning' })
  try {
    await removeTeacherBoundStudent(t.id, row.id)
    ElMessage.success('已移除')
    await reloadBoundStudents()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e?.detail || '移除失败')
  }
}

onMounted(async () => {
  classOptions.value = await getClasses()
  try { majorOptions.value = await getUserMajors() } catch (_) {}
  await loadSubjectOptions()
  await load()
})
</script>
