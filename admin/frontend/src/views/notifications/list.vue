<template>
  <div class="notification-page">
    <el-card class="composer-card">
      <template #header>
        <div class="card-title">
          <span>发送站内通知</span>
          <el-tag type="info">站内消息</el-tag>
        </div>
      </template>

      <el-steps :active="step" finish-status="success" align-center class="steps">
        <el-step title="填写内容" />
        <el-step title="选择范围" />
        <el-step title="预览确认" />
      </el-steps>

      <el-form v-if="step === 0" :model="form" label-width="90px" class="step-form">
        <el-form-item label="通知标题" required>
          <el-input v-model="form.title" maxlength="60" show-word-limit placeholder="请输入清晰、可识别的标题" />
        </el-form-item>
        <el-form-item label="通知正文" required>
          <el-input v-model="form.content" type="textarea" :rows="5" maxlength="500" show-word-limit placeholder="请输入通知内容" />
        </el-form-item>
        <el-form-item label="通知分类">
          <el-select v-model="form.ntype" style="width:220px">
            <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-form v-else-if="step === 1" label-width="90px" class="step-form">
        <el-form-item label="接收范围" required>
          <el-select v-model="form.target_type" style="width:260px" @change="clearTargetValues">
            <el-option v-for="item in targetTypes" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="form.target_type === 'classes'" label="选择班级" required>
          <el-select v-model="form.target_values" multiple filterable collapse-tags collapse-tags-tooltip style="width:520px">
            <el-option v-for="item in targetOptions.classes" :key="item.id" :label="`${item.major || ''} ${item.name}`.trim()" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.target_type === 'majors'" label="选择专业" required>
          <el-select v-model="form.target_values" multiple filterable style="width:520px">
            <el-option v-for="item in targetOptions.majors" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.target_type === 'subjects'" label="体育选科" required>
          <el-select v-model="form.target_values" multiple filterable style="width:520px">
            <el-option v-for="item in targetOptions.subjects" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.target_type === 'users'" label="指定用户" required>
          <el-select
            v-model="form.target_values"
            multiple
            filterable
            remote
            reserve-keyword
            :remote-method="searchUsers"
            :loading="userSearching"
            placeholder="输入姓名、学号、工号或手机号（至少2个字）"
            style="width:620px"
          >
            <el-option v-for="item in userOptions" :key="item.id" :label="userLabel(item)" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-alert
          v-if="form.target_type === 'all'"
          type="warning"
          :closable="false"
          title="全体师生属于全校发送，下一步会显示预计人数并要求再次确认。"
        />
      </el-form>

      <div v-else class="preview-panel" v-loading="previewing">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="标题">{{ form.title }}</el-descriptions-item>
          <el-descriptions-item label="分类">{{ typeLabel(form.ntype) }}</el-descriptions-item>
          <el-descriptions-item label="发送范围">{{ targetLabel(form.target_type) }}</el-descriptions-item>
          <el-descriptions-item label="预计接收"><strong class="recipient-count">{{ preview.recipient_count }} 人</strong></el-descriptions-item>
          <el-descriptions-item label="通知正文" :span="2">{{ form.content }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="preview.sample_users?.length" class="sample-row">
          <span class="sample-label">接收人示例：</span>
          <el-tag v-for="item in preview.sample_users" :key="item.id" type="info" class="sample-tag">{{ item.name }}</el-tag>
        </div>
        <el-alert v-if="form.target_type === 'all'" type="warning" :closable="false" show-icon title="请再次确认：此通知将发送给全体学生和教师，发送后不可撤回或修改。" />
      </div>

      <div class="step-actions">
        <el-button v-if="step > 0" @click="step--">上一步</el-button>
        <el-button v-if="step < 2" type="primary" @click="nextStep">下一步</el-button>
        <el-button v-else type="primary" :loading="sending" :disabled="preview.recipient_count < 1" @click="confirmSend">确认发送</el-button>
      </div>
    </el-card>

    <el-card>
      <template #header><div class="card-title"><span>已发送批次</span><el-button @click="loadCampaigns">刷新</el-button></div></template>
      <el-form :inline="true" class="filters" @submit.prevent>
        <el-form-item label="标题"><el-input v-model="filters.title" clearable placeholder="标题关键词" @keyup.enter="searchCampaigns" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filters.ntype" clearable style="width:150px">
            <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="范围">
          <el-select v-model="filters.target_type" clearable style="width:160px">
            <el-option v-for="item in targetTypes" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button type="primary" @click="searchCampaigns">查询</el-button><el-button @click="resetFilters">重置</el-button></el-form-item>
      </el-form>

      <el-table :data="campaigns" stripe v-loading="loading">
        <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
        <el-table-column label="分类" width="110"><template #default="{ row }">{{ typeLabel(row.ntype) }}</template></el-table-column>
        <el-table-column label="接收范围" width="130"><template #default="{ row }">{{ targetLabel(row.target_type) }}</template></el-table-column>
        <el-table-column prop="sender_name" label="发送人" width="110" />
        <el-table-column prop="recipient_count" label="接收" width="80" />
        <el-table-column prop="read_count" label="已读" width="80" />
        <el-table-column label="阅读率" width="150">
          <template #default="{ row }"><el-progress :percentage="row.read_rate" :stroke-width="8" /></template>
        </el-table-column>
        <el-table-column label="发送时间" width="180"><template #default="{ row }">{{ formatTime(row.created_at) }}</template></el-table-column>
        <el-table-column label="操作" width="90" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="openDetail(row)">详情</el-button></template></el-table-column>
      </el-table>
      <div class="pagination"><el-pagination v-model:current-page="page" :page-size="size" :total="total" layout="total, prev, pager, next" @current-change="loadCampaigns" /></div>
    </el-card>

    <el-dialog v-model="detailVisible" title="通知批次详情" width="860px" destroy-on-close>
      <el-descriptions v-if="detail.id" :column="3" border>
        <el-descriptions-item label="标题" :span="2">{{ detail.title }}</el-descriptions-item>
        <el-descriptions-item label="发送人">{{ detail.sender_name }}</el-descriptions-item>
        <el-descriptions-item label="接收人数">{{ detail.recipient_count }}</el-descriptions-item>
        <el-descriptions-item label="已读人数">{{ detail.read_count }}</el-descriptions-item>
        <el-descriptions-item label="未读人数">{{ detail.unread_count }}</el-descriptions-item>
        <el-descriptions-item label="正文" :span="3">{{ detail.body }}</el-descriptions-item>
      </el-descriptions>
      <div class="recipient-toolbar">
        <strong>接收明细</strong>
        <el-radio-group v-model="recipientFilter" size="small" @change="loadRecipients(1)">
          <el-radio-button value="">全部</el-radio-button><el-radio-button value="read">已读</el-radio-button><el-radio-button value="unread">未读</el-radio-button>
        </el-radio-group>
      </div>
      <el-table :data="recipients" v-loading="recipientLoading" height="330">
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="student_id" label="学号/工号" />
        <el-table-column label="身份" width="90"><template #default="{ row }">{{ row.role === 'teacher' ? '教师' : '学生' }}</template></el-table-column>
        <el-table-column label="状态" width="90"><template #default="{ row }"><el-tag :type="row.is_read ? 'success' : 'info'">{{ row.is_read ? '已读' : '未读' }}</el-tag></template></el-table-column>
        <el-table-column label="阅读时间" width="180"><template #default="{ row }">{{ formatTime(row.read_at) || '-' }}</template></el-table-column>
      </el-table>
      <div class="pagination"><el-pagination v-model:current-page="recipientPage" :page-size="20" :total="recipientTotal" layout="total, prev, pager, next" @current-change="loadRecipients" /></div>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createNotificationCampaign, getNotificationCampaign, getNotificationCampaigns,
  getNotificationRecipients, getNotificationTargetOptions, previewNotificationCampaign,
  searchNotificationUsers,
} from '../../api/index.js'

const typeOptions = [
  { label: '系统公告', value: 'system' }, { label: '任务通知', value: 'task' },
  { label: '教师消息', value: 'teacher_message' }, { label: '学生消息', value: 'student_message' },
  { label: '健康审批', value: 'health_review' }, { label: '跑团消息', value: 'run_group' },
  { label: '成绩通知', value: 'score' },
]
const targetTypes = [
  { label: '全体师生', value: 'all' }, { label: '全部学生', value: 'students' },
  { label: '全部教师', value: 'teachers' }, { label: '指定班级', value: 'classes' },
  { label: '指定专业', value: 'majors' }, { label: '体育选科', value: 'subjects' },
  { label: '指定用户', value: 'users' },
]
const emptyForm = () => ({ title: '', content: '', ntype: 'system', target_type: 'students', target_values: [], action_type: null, action_data: {} })
const form = ref(emptyForm())
const step = ref(0)
const preview = ref({ recipient_count: 0, sample_users: [] })
const previewing = ref(false)
const sending = ref(false)
const targetOptions = reactive({ classes: [], majors: [], subjects: [] })
const userOptions = ref([])
const userSearching = ref(false)
const campaigns = ref([])
const loading = ref(false)
const page = ref(1)
const size = 20
const total = ref(0)
const filters = reactive({ title: '', ntype: '', target_type: '' })
const detailVisible = ref(false)
const detail = ref({})
const recipients = ref([])
const recipientLoading = ref(false)
const recipientFilter = ref('')
const recipientPage = ref(1)
const recipientTotal = ref(0)

const typeLabel = value => typeOptions.find(item => item.value === value)?.label || '通知'
const targetLabel = value => targetTypes.find(item => item.value === value)?.label || value
const clearTargetValues = () => { form.value.target_values = []; preview.value = { recipient_count: 0, sample_users: [] } }
const userLabel = item => `${item.name} · ${item.student_id || item.phone || (item.role === 'teacher' ? '教师' : '学生')}`
const payload = () => ({ ...form.value, title: form.value.title.trim(), content: form.value.content.trim() })

const searchUsers = async keyword => {
  if (!keyword || keyword.trim().length < 2) return
  userSearching.value = true
  try {
    const rows = await searchNotificationUsers(keyword.trim())
    const selected = userOptions.value.filter(item => form.value.target_values.includes(item.id))
    userOptions.value = [...new Map([...selected, ...rows].map(item => [item.id, item])).values()]
  } finally { userSearching.value = false }
}

const validateTarget = () => {
  if (['classes', 'majors', 'subjects', 'users'].includes(form.value.target_type) && !form.value.target_values.length) {
    ElMessage.warning('请选择具体接收范围')
    return false
  }
  return true
}
const nextStep = async () => {
  if (step.value === 0) {
    if (!form.value.title.trim() || !form.value.content.trim()) return ElMessage.warning('请填写通知标题和正文')
    step.value = 1
    return
  }
  if (!validateTarget()) return
  previewing.value = true
  try {
    preview.value = await previewNotificationCampaign(payload())
    step.value = 2
  } catch (e) { ElMessage.error(e?.detail || '无法预览接收范围') }
  finally { previewing.value = false }
}
const confirmSend = async () => {
  const text = form.value.target_type === 'all' ? `确认向全体师生 ${preview.value.recipient_count} 人发送？` : `确认向 ${preview.value.recipient_count} 人发送？`
  try { await ElMessageBox.confirm(`${text} 发送后不可修改或撤回。`, '发送确认', { type: 'warning', confirmButtonText: '确认发送' }) }
  catch { return }
  sending.value = true
  try {
    const result = await createNotificationCampaign(payload())
    ElMessage.success(`通知已发送给 ${result.recipient_count} 人`)
    form.value = emptyForm(); preview.value = { recipient_count: 0, sample_users: [] }; step.value = 0; page.value = 1
    await loadCampaigns()
  } catch (e) { ElMessage.error(e?.detail || '发送失败') }
  finally { sending.value = false }
}

const loadCampaigns = async () => {
  loading.value = true
  try {
    const params = { page: page.value, size, ...Object.fromEntries(Object.entries(filters).filter(([, value]) => value)) }
    const result = await getNotificationCampaigns(params)
    campaigns.value = result.items || []; total.value = result.total || 0
  } catch (e) { ElMessage.error(e?.detail || '加载通知批次失败') }
  finally { loading.value = false }
}
const searchCampaigns = () => { page.value = 1; loadCampaigns() }
const resetFilters = () => { Object.assign(filters, { title: '', ntype: '', target_type: '' }); searchCampaigns() }
const openDetail = async row => {
  detailVisible.value = true; detail.value = await getNotificationCampaign(row.id)
  recipientFilter.value = ''; await loadRecipients(1)
}
const loadRecipients = async (nextPage = recipientPage.value) => {
  if (!detail.value.id) return
  recipientPage.value = nextPage; recipientLoading.value = true
  try {
    const result = await getNotificationRecipients(detail.value.id, { page: nextPage, size: 20, read_status: recipientFilter.value || undefined })
    recipients.value = result.items || []; recipientTotal.value = result.total || 0
  } catch (e) { ElMessage.error(e?.detail || '加载接收明细失败') }
  finally { recipientLoading.value = false }
}
const formatTime = value => value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : ''

onMounted(async () => {
  try { Object.assign(targetOptions, await getNotificationTargetOptions()) } catch (e) { ElMessage.error(e?.detail || '加载接收范围失败') }
  loadCampaigns()
})
</script>

<style scoped>
.notification-page { display: grid; gap: 16px; }
.composer-card { min-height: 410px; }
.card-title { display: flex; justify-content: space-between; align-items: center; }
.steps { margin: 8px auto 32px; max-width: 760px; }
.step-form, .preview-panel { max-width: 900px; margin: 0 auto; }
.step-actions { display: flex; justify-content: center; gap: 12px; margin-top: 28px; }
.recipient-count { color: #e6a23c; font-size: 20px; }
.sample-row { margin: 18px 0; color: #606266; }
.sample-label { margin-right: 8px; }
.sample-tag { margin: 3px; }
.filters { margin-bottom: 4px; }
.pagination { display: flex; justify-content: flex-end; margin-top: 16px; }
.recipient-toolbar { display: flex; justify-content: space-between; align-items: center; margin: 20px 0 10px; }
</style>
