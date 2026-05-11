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
      <el-table-column label="操作" width="360">
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
        为教师「{{ assignDialog.teacher?.name || '' }}」选择可管辖的体育选科：
      </div>
      <el-checkbox-group v-model="assignDialog.selected">
        <el-checkbox
          v-for="sub in subjectOptions"
          :key="sub"
          :label="sub"
        >
          {{ sub }}
        </el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="assignDialog.visible=false">取 消</el-button>
        <el-button type="primary" @click="saveAssignSubjects">保 存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getUsers, getUserMajors, deleteUser, resetPassword, getClasses, getTeacherSubjects, updateTeacherSubjects, getStudentActivities } from '../api/index.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const role = ref('student')
const users = ref([])
const classOptions = ref([])
const majorOptions = ref([])
const subjectOptions = ref(['篮球', '羽毛球', '乒乓球', '游泳', '跆拳道'])
const filters = ref({
  class_name: '',
  major: ''
})

const assignDialog = ref({
  visible: false,
  teacher: null,
  selected: []
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

const openAssignSubjects = async (teacher) => {
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

onMounted(async () => {
  classOptions.value = await getClasses()
  try { majorOptions.value = await getUserMajors() } catch (_) {}
  await load()
})
</script>
