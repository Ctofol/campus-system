<template>
  <el-alert
    title="导入后会直接创建账号，用户使用学号/手机号与统一初始密码登录，并在首次登录时强制修改密码。"
    type="info"
    :closable="false"
    style="margin-bottom:16px"
  />
  <el-row :gutter="16">
    <el-col :span="12">
      <el-card>
        <template #header>批量导入学生</template>
        <p style="color:#666;font-size:14px;margin-bottom:16px">
          Excel 列：学号、姓名、性别、所属班级名称、专业/课程；选科可选。无需填写手机号和密码，学生首次登录时自行绑定手机号并设置新密码。
        </p>
        <el-space direction="vertical" style="width:100%">
          <el-upload :before-upload="(f) => selectFile(f, 'student')" :show-file-list="false" accept=".xls,.xlsx">
            <el-button type="primary" :loading="loading.student">选择文件并预览</el-button>
          </el-upload>
          <el-button @click="downloadTpl('student')">下载学生模板</el-button>
        </el-space>
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card>
        <template #header>批量导入教师</template>
        <p style="color:#666;font-size:14px;margin-bottom:16px">Excel 列：姓名、手机号、工号。教师首次登录后同样必须修改初始密码。</p>
        <el-space direction="vertical" style="width:100%">
          <el-upload :before-upload="(f) => selectFile(f, 'teacher')" :show-file-list="false" accept=".xls,.xlsx">
            <el-button type="primary" :loading="loading.teacher">选择文件并预览</el-button>
          </el-upload>
          <el-button @click="downloadTpl('teacher')">下载教师模板</el-button>
        </el-space>
      </el-card>
    </el-col>
  </el-row>

  <el-card style="margin-top:16px">
    <template #header>最近导入批次</template>
    <el-table :data="batches" empty-text="暂无导入记录">
      <el-table-column prop="id" label="批次" width="80" />
      <el-table-column label="类型" width="90"><template #default="{ row }">{{ row.import_type === 'student' ? '学生' : '教师' }}</template></el-table-column>
      <el-table-column prop="filename" label="文件" min-width="180" show-overflow-tooltip />
      <el-table-column prop="success_count" label="成功" width="80" />
      <el-table-column prop="failed_count" label="失败" width="80" />
      <el-table-column label="状态" width="130"><template #default="{ row }"><el-tag :type="row.status === 'rolled_back' ? 'info' : (row.failed_count ? 'warning' : 'success')">{{ statusText(row.status) }}</el-tag></template></el-table-column>
      <el-table-column label="时间" width="180"><template #default="{ row }">{{ formatTime(row.created_at) }}</template></el-table-column>
      <el-table-column label="操作" width="110"><template #default="{ row }"><el-button v-if="row.status !== 'rolled_back'" link type="danger" @click="rollbackBatch(row)">安全回滚</el-button></template></el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="previewVisible" title="导入预览" width="620px">
    <el-descriptions :column="3" border>
      <el-descriptions-item label="总行数">{{ preview.total }}</el-descriptions-item>
      <el-descriptions-item label="可导入">{{ preview.valid }}</el-descriptions-item>
      <el-descriptions-item label="有问题">{{ preview.invalid }}</el-descriptions-item>
    </el-descriptions>
    <el-alert v-if="preview.invalid" title="请先修正表格中的问题后重新选择文件，本次不会写入任何数据。" type="error" :closable="false" style="margin-top:16px" />
    <el-table v-if="preview.errors?.length" :data="preview.errors" max-height="260" style="margin-top:12px">
      <el-table-column prop="row" label="行" width="70" /><el-table-column prop="error" label="问题" />
    </el-table>
    <template #footer>
      <el-button @click="previewVisible = false">取消</el-button>
      <el-button type="primary" :disabled="!preview.can_import" :loading="confirming" @click="confirmImport">确认导入 {{ preview.valid }} 条</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api, { importStudents, importTeachers, previewImport, getImportBatches, rollbackImportBatch } from '../api/index.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref({ student: false, teacher: false })
const batches = ref([])
const previewVisible = ref(false)
const preview = ref({ total: 0, valid: 0, invalid: 0, errors: [], can_import: false })
const pendingFile = ref(null)
const pendingType = ref('student')
const confirming = ref(false)

const selectFile = async (file, type) => {
  loading.value[type] = true
  try {
    preview.value = await previewImport(file, type)
    pendingFile.value = file
    pendingType.value = type
    previewVisible.value = true
  } catch (e) {
    ElMessage.error(e?.detail || '文件预览失败')
  } finally {
    loading.value[type] = false
  }
  return false
}

const confirmImport = async () => {
  if (!pendingFile.value || !preview.value.can_import) return
  confirming.value = true
  try {
    const fn = pendingType.value === 'student' ? importStudents : importTeachers
    const data = await fn(pendingFile.value)
    const ok = data.success ?? 0
    const bad = data.failed ?? 0
    let msg = `导入完成：成功 ${ok} 条，失败 ${bad} 条`
    const errs = data.errors || []
    if (errs.length > 0) {
      const lines = errs.slice(0, 8).map((e) => `第${e.row}行：${e.error}`)
      msg += ' — ' + lines.join('；')
      if (errs.length > 8) msg += `（共 ${errs.length} 条错误）`
    }
    ElMessage({
      message: msg,
      type: bad ? 'warning' : 'success',
      duration: bad ? 14000 : 4000,
      showClose: true
    })
    previewVisible.value = false
    await loadBatches()
  } catch (e) {
    ElMessage.error(e?.detail || '导入失败')
  } finally {
    confirming.value = false
  }
}

const loadBatches = async () => { try { batches.value = await getImportBatches() } catch { batches.value = [] } }
const statusText = status => ({ completed: '已完成', completed_with_errors: '部分失败', rolled_back: '已回滚', processing: '处理中' }[status] || status)
const formatTime = value => value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '-'
const rollbackBatch = async row => {
  try {
    await ElMessageBox.confirm('仅当本批次账号尚未产生运动、课程、通知等业务数据时才能回滚。确认继续？', `回滚批次 #${row.id}`, { type: 'warning', confirmButtonText: '确认回滚' })
    const result = await rollbackImportBatch(row.id)
    ElMessage.success(`已回滚 ${result.deleted_users || 0} 个账号`)
    await loadBatches()
  } catch (e) {
    if (e === 'cancel' || e === 'close') return
    const detail = e?.detail
    ElMessage.error(typeof detail === 'string' ? detail : (detail?.message || '回滚失败'))
  }
}

const TEMPLATE_PATHS = {
  student: '/manage/import/template/students',
  teacher: '/manage/import/template/teachers'
}
const TEMPLATE_FILES = {
  student: 'student_import_template.xlsx',
  teacher: 'teacher_import_template.xlsx'
}

const downloadTpl = async (type) => {
  try {
    const blob = await api.get(TEMPLATE_PATHS[type], { responseType: 'blob' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = TEMPLATE_FILES[type]
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error(e?.detail || '下载失败（请确认已登录）')
  }
}

onMounted(loadBatches)
</script>
