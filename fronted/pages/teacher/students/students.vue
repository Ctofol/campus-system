<template>
  <view class="students-page">
    <page-tab-header title="学员管理" show-back theme="white">
      <template #right>
        <view class="batch-btn" @click="toggleBatchMode" :class="{active: isBatchMode}">
          <text>{{ isBatchMode ? '完成' : '批量管理' }}</text>
        </view>
      </template>
    </page-tab-header>

    <view class="header page-tab-body">
      <!-- 2. 数据概览栏 -->
      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-num">{{ total }}</text>
          <text class="stat-label">总人数</text>
        </view>
        <view class="stat-item warn">
          <text class="stat-num">{{ abnormal }}</text>
          <text class="stat-label">档案异常</text>
        </view>
        <view class="stat-item success">
          <text class="stat-num">{{ normal }}</text>
          <text class="stat-label">正常</text>
        </view>
      </view>

      <!-- 3. 工具栏 -->
      <view class="tools-section">
        <view class="search-bar">
           <text class="search-icon">🔍</text>
           <input v-model="keyword" class="search-input" placeholder="搜索姓名/学号..." confirm-type="search" @confirm="onSearchConfirm" />
        </view>
        
        <view class="filters-bar">
          <picker mode="selector" :range="classNames" @change="onClassChange" class="filter-item">
            <view class="picker-box">
              <text class="picker-text">{{ currentClassName || '全部班级' }}</text>
              <text class="picker-icon">▼</text>
            </view>
          </picker>
          <picker mode="selector" :range="groupOptions" @change="onGroupChange" class="filter-item">
             <view class="picker-box">
              <text class="picker-text">{{ groupPickerLabel }}</text>
              <text class="picker-icon">▼</text>
            </view>
          </picker>
          <picker mode="selector" :range="statusOptions" @change="onStatusChange" class="filter-item">
             <view class="picker-box">
              <text class="picker-text">{{ currentStatusLabel || '全部状态' }}</text>
              <text class="picker-icon">▼</text>
            </view>
          </picker>
        </view>
      </view>
      
      <!-- 4. 通知栏: 请假审批 -->
      <view class="notice-bar" v-if="(pendingRequests||[]).length > 0" @click="showHealthModal = true">
        <view class="notice-content">
          <text class="notice-icon">📋</text>
          <text>有 {{ (pendingRequests||[]).length }} 条请假申请待处理</text>
        </view>
        <text class="arrow">去处理 →</text>
      </view>

      <!-- 5. 通知栏: 运动异常 (新增) -->
      <view class="notice-bar exception" v-if="pendingExceptionCount > 0" @click="goToExceptions">
        <view class="notice-content">
          <text class="notice-icon">🏃</text>
          <text>有 {{ pendingExceptionCount }} 条运动异常待核实</text>
        </view>
        <text class="arrow">去核实 →</text>
      </view>
    </view>

    <!-- AI Analysis Reports Notification -->
    <view class="report-notice" v-if="(sharedReports||[]).length > 0" @click="showReportsModal = true">
      <view class="notice-left">
        <text class="notice-icon">🤖</text>
        <text class="notice-text">收到 {{ (sharedReports||[]).length }} 份新的运动分析报告</text>
      </view>
      <text class="notice-arrow">查看 →</text>
    </view>

    <view class="card-list" :class="{ 'has-bottom-bar': isBatchMode }">
      <view class="student-card" v-for="(stu, idx) in filteredStudents" :key="stu.id" @click="handleCardClick(stu)">
        <view class="card-main">
          <view class="card-left">
            <checkbox v-if="isBatchMode" :checked="selectedIds.includes(stu.id)" @click.stop="toggleSelect(stu)" color="#20C997" style="transform:scale(0.8)" />
            <view class="avatar">{{ stu.name.slice(0,1) }}</view>
            <view class="info">
              <text class="name">{{ stu.name }} <text class="group-tag" v-if="stu.groupName">({{stu.groupName}})</text></text>
              <text class="meta">学号：{{ stu.student_id || '未录入' }}</text>
              <text class="meta">班级：{{ stu.className }}</text>
              <text class="meta">专业：{{ stu.majorLabel }}</text>
              <text class="meta">{{ stu.health_status === 'normal' ? '健康：良好' : '原因：' + (stu.abnormal_reason || '未说明') }}</text>
            </view>
          </view>
          <view class="card-right">
            <text class="status" :class="stu.statusClass">{{ stu.statusLabel }}</text>
            <text class="expand-icon" v-if="!isBatchMode">{{ stu.expanded ? '▲' : '▼' }}</text>
          </view>
        </view>
        
        <!-- Expanded Details -->
        <view class="card-expanded" v-if="stu.expanded && !isBatchMode">
          <view class="exp-grid">
             <!-- Metrics could be fetched separately or included in student detail -->
            <view class="exp-item">
              <text class="exp-label">状态</text>
              <text class="exp-val">{{ stu.statusLabel }}</text>
            </view>
            <view class="exp-item">
              <text class="exp-label">原因</text>
              <text class="exp-val">{{ stu.abnormal_reason || '-' }}</text>
            </view>
          </view>
          <view class="exp-actions">
            <button size="mini" class="exp-btn" @click.stop="openDetail(stu)">完整档案</button>
            <button size="mini" class="exp-btn outline" @click.stop="editStudent(stu)">编辑信息</button>
          </view>
        </view>
      </view>
      <view class="empty" v-if="filteredStudents.length===0">
        <text>暂无符合条件的学员</text>
      </view>
    </view>

    <!-- 批量操作栏 -->
    <view class="batch-bar" v-if="isBatchMode">
      <view class="batch-info">
        <checkbox :checked="isAllSelected" @click="toggleSelectAll" color="#20C997" style="transform:scale(0.8)" />
        <text>已选 {{ selectedIds.length }} 人</text>
      </view>
      <view class="batch-actions">
        <button size="mini" class="action-btn outline" @click="batchGroup">批量分组</button>
        <button size="mini" class="action-btn warn" @click="batchStatus">更新状态</button>
        <button size="mini" class="action-btn" @click="batchExport">导出数据</button>
      </view>
    </view>

    <!-- Health Requests Modal -->
    <view class="modal-overlay" v-if="showHealthModal" @click="showHealthModal = false">
      <view class="report-modal" @click.stop>
        <view class="modal-header">
          <text class="modal-title">🔔 请假/伤病审批</text>
          <text class="close-btn" @click="showHealthModal = false">×</text>
        </view>
        <scroll-view scroll-y class="report-list">
          <view class="report-item" v-for="(req, idx) in pendingRequests" :key="req.id">
            <view class="report-meta">
              <text class="report-stu">{{ healthStudentLabel(req) }}</text>
              <text class="report-time">{{ formatDate(req.created_at) }}</text>
            </view>
            <view class="report-card" :class="req.type">
              <view class="card-header">
                <text class="report-type-tag" :class="req.type">
                  {{ req.type === 'leave' ? '📅 请假申请' : '🏥 伤病报告' }}
                </text>
              </view>
              <view class="report-body">
                <text class="report-time-range" v-if="req.type === 'leave' && (req.start_date || req.end_date)">
                  请假时间：{{ (req.start_date || '').substring(0, 10) }} 至 {{ (req.end_date || '').substring(0, 10) }}
                </text>
                <text class="report-content">{{ req.reason }}</text>
              </view>
            </view>
            <view class="report-actions">
              <button size="mini" class="action-btn reject" @click="handleRequest(req, 'rejected')">驳回</button>
              <button size="mini" class="action-btn approve" @click="handleRequest(req, 'approved')">批准</button>
            </view>
          </view>
          <view class="empty" v-if="pendingRequests.length===0">
            <text>暂无待审批请求</text>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- Reports Modal -->
    <view class="modal-overlay" v-if="showReportsModal" @click="showReportsModal = false">
      <view class="report-modal" @click.stop>
        <view class="modal-header">
          <text class="modal-title">📄 学员运动分析报告</text>
          <text class="close-btn" @click="showReportsModal = false">×</text>
        </view>
        <scroll-view scroll-y class="report-list">
          <view class="report-item" v-for="(report, idx) in sharedReports" :key="idx">
            <view class="report-meta">
              <text class="report-stu">{{ report.studentName }}</text>
              <text class="report-time">{{ report.time }}</text>
            </view>
            <view class="report-card">
              <text class="report-title">{{ report.card.title }}</text>
              <text class="report-suggestion" v-if="report.card.suggestion">💡 {{ report.card.suggestion }}</text>
              <view class="report-chart" v-if="report.card.chartData">
                <view class="mini-bar" v-for="(d, i) in report.card.chartData" :key="i">
                  <text class="mini-label">{{ d.label }}</text>
                  <view class="mini-track">
                    <view class="mini-fill" :style="{ width: d.value + '%', background: d.color }"></view>
                  </view>
                  <text class="mini-val">{{ d.valText }}</text>
                </view>
              </view>
            </view>
            <view class="report-actions">
              <button size="mini" class="reply-btn" @click="replyStudent(report)">回复指导</button>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { onShow, onReachBottom, onLoad } from '@dcloudio/uni-app';
import { request, BASE_URL } from '@/utils/request';

const isBatchMode = ref(false);
const selectedIds = ref([]);
const sharedReports = ref([]);
const showReportsModal = ref(false);
const showHealthModal = ref(false);

const students = ref([]);
const pendingRequests = ref([]);
const pendingExceptionCount = ref(0);
const keyword = ref('');
/** 小组筛选：空字符串表示不按组过滤；须与 groupPickerLabel、loadStudents 同步声明 */
const currentGroupName = ref('');

// Pagination
const page = ref(1);
const pageSize = 20;
const hasMore = ref(true);
const isLoading = ref(false);
/** onShow 等场景下连续触发 loadStudents(true) 时，避免「先清空列表再因 isLoading 直接 return」导致列表一直为空 */
const studentsReloadQueued = ref(false);

// Total counts from server
const totalCount = ref(0);
const abnormalCount = ref(0);
const normalCount = ref(0);

// Filters
const classList = ref([]);
const classNames = computed(() => ['全部班级', ...classList.value.map(c => c.name)]);
const currentClassName = ref('');
const currentClassId = ref(null);

const statusOptions = ['全部状态', '正常', '请假', '受伤', '异常'];
const currentStatusLabel = ref('');
const currentStatusValue = ref(null);

const DEFAULT_TEACHER_GROUPS = ['体能A组', '体能B组', '康复组'];

/** 与后端 /teacher/student-groups 返回的已有分组名合并（默认组在前，其余按拼音序） */
function mergeTeacherGroupNames(apiNames) {
  const seen = new Set(DEFAULT_TEACHER_GROUPS);
  const extra = [];
  for (const n of apiNames || []) {
    const t = String(n || '').trim();
    if (!t || seen.has(t)) continue;
    seen.add(t);
    extra.push(t);
  }
  extra.sort((a, b) => a.localeCompare(b, 'zh-CN'));
  return [...DEFAULT_TEACHER_GROUPS, ...extra];
}

const teacherGroupNames = ref([...DEFAULT_TEACHER_GROUPS]);

const groupOptions = computed(() => ['全部小组', ...teacherGroupNames.value]);

const groupPickerLabel = computed(() => {
  const g = currentGroupName.value;
  return g && String(g).trim() ? g : '全部小组';
});

async function loadTeacherGroups() {
  try {
    const res = await request({ url: '/teacher/student-groups', method: 'GET' });
    const apiNames = res && res.names ? res.names : [];
    teacherGroupNames.value = mergeTeacherGroupNames(apiNames);
  } catch (e) {
    // 线上旧后端可能未部署该接口（404），仅用默认组名即可，勿阻塞学员列表
    teacherGroupNames.value = [...DEFAULT_TEACHER_GROUPS];
  }
}

// Computed
const filteredStudents = computed(() => {
  // Client-side filtering if needed, but we mostly rely on server for main filters
  // Here we can do extra keyword filtering if we loaded all
  return students.value;
});

const total = computed(() => totalCount.value);
const abnormal = computed(() => abnormalCount.value);
const normal = computed(() => normalCount.value);

const isAllSelected = computed(() => {
  return filteredStudents.value.length > 0 && selectedIds.value.length === filteredStudents.value.length;
});

// Load Data
const loadClasses = async () => {
  try {
    const res = await request('/teacher/classes', { method: 'GET' });
    classList.value = res;
  } catch (e) {
    console.error(e);
  }
};

const loadStats = async () => {
  try {
    const res = await request('/teacher/stats', { method: 'GET' });
    totalCount.value = res.student_count;
    abnormalCount.value = res.abnormal_count;
    normalCount.value = res.student_count - res.abnormal_count;
    pendingExceptionCount.value = res.pending_activities || 0;
  } catch (e) {
    console.error(e);
  }
};

const onSearchConfirm = () => {
  loadStudents(true);
};

const loadStudents = async (reset = false) => {
  if (reset && isLoading.value) {
    studentsReloadQueued.value = true;
    return;
  }
  if (!reset && (!hasMore.value || isLoading.value)) return;
  if (reset) {
    page.value = 1;
    hasMore.value = true;
    students.value = [];
  }
  isLoading.value = true;
  try {
    const params = {
      page: page.value,
      size: pageSize
    };
    if (currentClassId.value) params.class_id = currentClassId.value;
    if (keyword.value) params.name = keyword.value;
    if (currentStatusValue.value) params.status = currentStatusValue.value;
    if (currentGroupName.value) params.group_name = currentGroupName.value;
    
    const res = await request('/teacher/students', {
      method: 'GET',
      data: params
    });
    const list = Array.isArray(res) ? res : (res && Array.isArray(res.items) ? res.items : []);

    // Process data
    const newStudents = list.map(s => {
      const className = s.class_name || s.plain_class_name || '未分配';
      
      let statusLabel = '正常';
      let statusClass = 'ok';
      if (s.health_status === 'leave') { statusLabel = '请假'; statusClass = 'warn'; }
      if (s.health_status === 'injured') { statusLabel = '受伤'; statusClass = 'warn'; }
      if (s.health_status === 'abnormal') { statusLabel = '异常'; statusClass = 'warn'; }
      
      return {
        ...s,
        className,
        majorLabel: s.major_name || '—',
        statusLabel,
        statusClass,
        expanded: false
      };
    });
    
    if (newStudents.length < pageSize) {
      hasMore.value = false;
    }
    
    students.value = [...students.value, ...newStudents];
    page.value++;
    
  } catch (e) {
    console.error(e);
    let msg = '加载失败';
    if (e && typeof e.message === 'string' && e.message.trim()) {
      msg = e.message.trim();
    } else if (e && e.data) {
      const d = e.data.detail;
      if (typeof d === 'string') msg = d;
      else if (Array.isArray(d) && d[0] && d[0].msg) msg = String(d[0].msg);
    }
    uni.showToast({ title: msg.length > 40 ? msg.slice(0, 40) + '…' : msg, icon: 'none', duration: 3800 });
  } finally {
    isLoading.value = false;
    if (studentsReloadQueued.value) {
      studentsReloadQueued.value = false;
      loadStudents(true);
    }
  }
};

onReachBottom(() => {
  loadStudents(false);
});

const loadHealthRequests = async () => {
  try {
    const res = await request('/teacher/health/requests', { method: 'GET' });
    const list = Array.isArray(res) ? res : (res?.items || res?.data || []);
    pendingRequests.value = list;
  } catch (e) {
    console.error(e);
  }
};

onLoad((options) => {
  if (options.showHealth === 'true') {
    showHealthModal.value = true;
  }
});

onShow(() => {
  const info = uni.getSystemInfoSync();
  const role = uni.getStorageSync('userRole') || uni.getStorageSync('role');
  if (role !== 'teacher') {
    uni.showToast({ title: '请使用教师账号登录', icon: 'none' });
    uni.redirectTo({ url: '/pages/login/login' });
    return;
  }
  
  loadStats(); // Load statistics first
  loadTeacherGroups();
  loadClasses().then(() => {
    loadStudents(true);
  });
  loadHealthRequests();
  
  sharedReports.value = uni.getStorageSync('mockSharedReports') || [];
});

// Events
const onClassChange = (e) => {
  const idx = Number(e.detail.value);
  if (idx === 0) {
    currentClassName.value = '';
    currentClassId.value = null;
  } else {
    currentClassName.value = classNames.value[idx];
    currentClassId.value = classList.value[idx-1].id;
  }
  loadStudents(true);
};

const onGroupChange = (e) => {
  const idx = Number(e.detail.value);
  const opts = groupOptions.value;
  if (idx === 0) {
    currentGroupName.value = '';
  } else {
    currentGroupName.value = opts[idx] || '';
  }
  loadStudents(true);
};

const onStatusChange = (e) => {
  const idx = Number(e.detail.value);
  currentStatusLabel.value = statusOptions[idx];
  if (idx === 0) currentStatusValue.value = null;
  else if (idx === 1) currentStatusValue.value = 'normal';
  else if (idx === 2) currentStatusValue.value = 'leave';
  else if (idx === 3) currentStatusValue.value = 'injured';
  else if (idx === 4) currentStatusValue.value = 'abnormal';
  loadStudents(true);
};

const handleCardClick = (stu) => {
  if (isBatchMode.value) {
    toggleSelect(stu);
  } else {
    stu.expanded = !stu.expanded;
  }
};

const toggleBatchMode = () => {
  isBatchMode.value = !isBatchMode.value;
  selectedIds.value = [];
  if(isBatchMode.value) {
    students.value.forEach(s => s.expanded = false);
  }
};

const toggleSelect = (stu) => {
  const idx = selectedIds.value.indexOf(stu.id);
  if (idx > -1) {
    selectedIds.value.splice(idx, 1);
  } else {
    selectedIds.value.push(stu.id);
  }
};

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value = [];
  } else {
    selectedIds.value = filteredStudents.value.map(s => s.id);
  }
};

// Batch Actions
const MAX_GROUP_SHEET = 5; // 与「新建小组」合计≤6 条，兼容微信小程序 actionSheet 上限

function promptNewGroupName() {
  return new Promise((resolve) => {
    uni.showModal({
      title: '新建小组',
      editable: true,
      placeholderText: '请输入小组名称',
      success: (res) => {
        if (res.confirm && res.content) {
          resolve(String(res.content).trim());
        } else {
          resolve(null);
        }
      },
      fail: () => resolve(null)
    });
  });
}

async function applyGroupToStudents(studentIds, groupName) {
  const name = String(groupName || '').trim();
  if (!name) {
    uni.showToast({ title: '小组名称不能为空', icon: 'none' });
    return;
  }
  if (name.length > 40) {
    uni.showToast({ title: '名称过长（最多40字）', icon: 'none' });
    return;
  }
  await request('/teacher/students/bulk-update', {
    method: 'POST',
    data: {
      student_ids: studentIds,
      group_name: name
    }
  });
}

const batchGroup = () => {
  if (selectedIds.value.length === 0) return uni.showToast({ title: '请先选择学员', icon: 'none' });
  const names = teacherGroupNames.value;
  const sheetItems = names.slice(0, MAX_GROUP_SHEET);
  sheetItems.push('新建小组…');
  uni.showActionSheet({
    itemList: sheetItems,
    success: async (res) => {
      const idx = res.tapIndex;
      let groupName = null;
      if (idx === sheetItems.length - 1) {
        groupName = await promptNewGroupName();
      } else {
        groupName = sheetItems[idx];
      }
      if (!groupName) return;
      try {
        await applyGroupToStudents(selectedIds.value, groupName);
        uni.showToast({ title: '批量分组成功', icon: 'success' });
        await loadTeacherGroups();
        loadStudents(true);
        toggleBatchMode();
      } catch (e) {
        console.error(e);
        uni.showToast({ title: '操作失败', icon: 'none' });
      }
    }
  });
};

const batchStatus = () => {
  if (selectedIds.value.length === 0) return uni.showToast({ title: '请先选择学员', icon: 'none' });
  const statusItems = ['恢复正常', '标记请假', '标记受伤', '标记异常'];
  const statusMap = ['normal', 'leave', 'injured', 'abnormal'];
  
  uni.showActionSheet({
    itemList: statusItems,
    success: async (res) => {
      const status = statusMap[res.tapIndex];
      try {
        await request('/teacher/students/bulk-update', {
          method: 'POST',
          data: {
            student_ids: selectedIds.value,
            health_status: status
          }
        });
        uni.showToast({ title: '状态更新成功', icon: 'success' });
        loadStudents(true);
        toggleBatchMode();
      } catch (e) {
        uni.showToast({ title: '操作失败', icon: 'none' });
      }
    }
  });
};

const batchExport = () => {
  if (selectedIds.value.length > 0) {
    doExport({ student_ids: selectedIds.value });
  } else {
    uni.showModal({
      title: '导出确认',
      content: '未选择学员，是否导出当前筛选条件下的所有学员？',
      success: (res) => {
        if (res.confirm) {
          const params = {};
          if (currentClassId.value) params.class_id = currentClassId.value;
          if (currentStatusValue.value) params.health_status = currentStatusValue.value;
          if (currentGroupName.value) params.group_name = currentGroupName.value;
          doExport(params);
        }
      }
    });
  }
};

const doExport = (data) => {
  uni.showLoading({ title: '生成报表中...' });
  const token = uni.getStorageSync('token');
  uni.request({
      url: `${BASE_URL}/teacher/students/export`,
      method: 'POST',
      header: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
      },
      data: data,
      responseType: 'arraybuffer',
      success: (res) => {
          uni.hideLoading();
          if (res.statusCode === 200) {
               // #ifdef H5
               if (typeof window !== 'undefined' && window.Blob) {
                   const blob = new Blob([res.data], { type: 'text/csv' });
                   const link = document.createElement('a');
                   link.href = window.URL.createObjectURL(blob);
                   link.download = `students_export_${new Date().getTime()}.csv`;
                   link.click();
               }
               // #endif
               uni.showToast({ title: '导出成功', icon: 'success' });
               if (isBatchMode.value) toggleBatchMode();
          } else {
              uni.showToast({ title: '导出失败', icon: 'none' });
          }
      },
      fail: () => {
          uni.hideLoading();
          uni.showToast({ title: '请求失败', icon: 'none' });
      }
  });
};

const goToExceptions = () => {
    uni.navigateTo({ url: '/pages/teacher/exceptions/exceptions' });
};

const editStudent = (stu) => {
  uni.showActionSheet({
    itemList: ['修改状态: 正常', '修改状态: 请假', '修改状态: 受伤', '修改状态: 异常', '修改分组'],
    success: async (res) => {
      if (res.tapIndex < 4) {
        const statuses = ['normal', 'leave', 'injured', 'abnormal'];
        const newStatus = statuses[res.tapIndex];
        
        if (newStatus !== 'normal') {
             uni.showModal({
                 title: '异常原因',
                 editable: true,
                 placeholder: '请输入原因（如：感冒、扭伤）',
                 success: async (mRes) => {
                     if (mRes.confirm) {
                         await updateStudentStatus(stu.id, newStatus, mRes.content);
                     }
                 }
             });
        } else {
             await updateStudentStatus(stu.id, newStatus, '');
        }
      } else {
        // Change group
        const names = teacherGroupNames.value;
        const sheetItems = names.slice(0, MAX_GROUP_SHEET);
        sheetItems.push('新建小组…');
        uni.showActionSheet({
          itemList: sheetItems,
          success: async (r2) => {
            let groupName = null;
            if (r2.tapIndex === sheetItems.length - 1) {
              groupName = await promptNewGroupName();
            } else {
              groupName = sheetItems[r2.tapIndex];
            }
            if (!groupName) return;
            try {
              await request(`/teacher/students/${stu.id}`, {
                method: 'PUT',
                data: { group_name: groupName }
              });
              uni.showToast({ title: '已更新', icon: 'success' });
              await loadTeacherGroups();
              loadStudents(true);
            } catch (e) {
              console.error(e);
              uni.showToast({ title: '更新失败', icon: 'none' });
            }
          }
        });
      }
    }
  });
};

const updateStudentStatus = async (id, status, reason) => {
    try {
      await request(`/teacher/students/${id}`, {
        method: 'PUT',
        data: { health_status: status, abnormal_reason: reason }
      });
      uni.showToast({ title: '已更新', icon: 'success' });
      loadStudents(true);
    } catch(e) { console.error(e); }
};


const openDetail = (stu) => {
  uni.navigateTo({
    url: `/pages/teacher/students/detail?id=${stu.id}`
  });
};

const findStudentById = (id) => {
  if (id == null || id === '') return null;
  const nid = Number(id);
  return students.value.find(
    (x) => Number(x.id) === nid || String(x.id) === String(id)
  ) || null;
};

const getStudentName = (id) => {
  const s = findStudentById(id);
  return s ? s.name : '未知学员';
};

/** 请假列表姓名：优先接口字段，避免仅依赖分页学员列表 */
const healthStudentLabel = (req) => {
  const apiName = (req?.student_name || '').trim();
  if (apiName && apiName !== '未知' && !apiName.startsWith('未知学员')) {
    return apiName;
  }
  if (req?.student_id != null) {
    const fromList = getStudentName(req.student_id);
    if (fromList !== '未知学员') return fromList;
  }
  return apiName || getStudentName(req?.student_id);
};

const handleRequest = async (req, action) => {
  try {
    await request(`/teacher/health/requests/${req.id}/review`, {
      method: 'PUT',
      data: { status: action }
    });
    uni.showToast({ title: '已处理', icon: 'success' });
    loadHealthRequests();
    loadStudents(true); // Reset and reload full list
    loadStats();      // Refresh top counters
  } catch (e) {
    uni.showToast({ title: '处理失败', icon: 'none' });
  }
};

const formatDate = (str) => {
  if (!str) return '';
  return new Date(str).toLocaleDateString();
};

const replyStudent = (report) => {
    // ... existing logic ...
};

const handleBack = () => {
  try {
    uni.navigateBack({
      delta: 1,
      fail() {
        uni.reLaunch({
          url: '/pages/teacher/dashboard/index'
        });
      }
    });
  } catch (e) {
    uni.reLaunch({
      url: '/pages/teacher/dashboard/index'
    });
  }
};
</script>

<style scoped>
.students-page { min-height: 100vh; background: #f8f8f8; }

/* New Header Styles */
.header { 
  background: #fff; 
  padding: 30rpx; 
  border-bottom: 1px solid #eee; 
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.nav-row { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
}
.nav-back {
  display: flex;
  align-items: center;
  padding: 0 10rpx;
}
.nav-back-icon {
  font-size: 32rpx;
  color: #333;
  margin-right: 4rpx;
}
.nav-back-text {
  font-size: 26rpx;
  color: #666;
}
.page-title { 
  font-size: 40rpx; 
  font-weight: 800; 
  color: #333; 
}
.batch-btn { 
  font-size: 28rpx; 
  color: #20C997; 
  padding: 10rpx 20rpx;
  background: rgba(32, 201, 151, 0.1);
  border-radius: 30rpx;
  transition: all 0.2s;
}
.batch-btn.active {
  background: #20C997;
  color: #fff;
}

.stats-row { 
  display: flex; 
  gap: 20rpx; 
}
.stat-item { 
  background: #f8f9fa; 
  padding: 20rpx; 
  border-radius: 16rpx; 
  flex: 1; 
  text-align: center; 
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.stat-item.warn { background: #fff7e6; }
.stat-item.success { background: #f6ffed; }

.stat-num { 
  font-size: 36rpx; 
  font-weight: bold; 
  color: #333; 
  line-height: 1.2;
  margin-bottom: 4rpx;
}
.stat-item.warn .stat-num { color: #fa8c16; }
.stat-item.success .stat-num { color: #52c41a; }

.stat-label { 
  font-size: 24rpx; 
  color: #999; 
}

.tools-section {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.search-bar {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 12rpx;
  padding: 16rpx 24rpx;
  height: 72rpx;
  box-sizing: border-box;
}
.search-icon { font-size: 32rpx; margin-right: 16rpx; color: #999; }
.search-input { flex: 1; font-size: 28rpx; color: #333; }

.filters-bar {
  display: flex;
  gap: 16rpx;
}
.filter-item {
  flex: 1;
}
.picker-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12rpx;
  padding: 0 20rpx;
  height: 64rpx;
  font-size: 26rpx;
  color: #666;
}
.picker-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 80%;
}
.picker-icon { font-size: 20rpx; color: #ccc; }

.notice-bar {
  margin-top: 10rpx;
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 12rpx;
  padding: 16rpx 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.notice-content {
  display: flex;
  align-items: center;
  font-size: 26rpx;
  color: #d48806;
}
.notice-icon { margin-right: 12rpx; }
.arrow { font-size: 24rpx; color: #d48806; opacity: 0.8; }

.card-list { margin-top: 20rpx; padding: 0 20rpx 40rpx; }
.card-list.has-bottom-bar { padding-bottom: 120rpx; }

.student-card { 
  display: block; 
  background: #fff; 
  margin-bottom: 20rpx; 
  padding: 24rpx; 
  border-radius: 16rpx; 
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.02);
}

.card-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start; /* Top align for better handling of multi-line info */
  width: 100%;
}

.card-left { 
  display: flex; 
  align-items: center; 
  flex: 1; 
  overflow: hidden; /* Critical for truncation */
}
.avatar { 
  width: 80rpx; 
  height: 80rpx; 
  border-radius: 50%; 
  background: #e0f7fa; 
  color: #00acc1; 
  font-weight: bold;
  font-size: 32rpx;
  display: flex; 
  align-items: center; 
  justify-content: center; 
  margin-right: 20rpx; 
  flex-shrink: 0;
}
.info { 
  display: flex; 
  flex-direction: column; 
  flex: 1;
  overflow: hidden;
  margin-right: 16rpx;
}
.name { font-size: 32rpx; font-weight: bold; color: #333; display: flex; align-items: center; }
.meta { 
  font-size: 26rpx; 
  color: #666; 
  margin-top: 8rpx; 
  white-space: nowrap; 
  overflow: hidden; 
  text-overflow: ellipsis;
  display: block;
}

.card-right { 
  display: flex; 
  flex-direction: column;
  align-items: flex-end; 
  gap: 16rpx; 
  flex-shrink: 0;
}
.status { 
  font-size: 24rpx; 
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  background: #f0fdf4;
}
.status.ok { color: #20C997; background: rgba(32, 201, 151, 0.1); }
.status.warn { color: #ff9f43; background: rgba(255, 159, 67, 0.1); }

.detail-btn { background: #20C997; color: #fff; }
.empty { text-align: center; color: #999; padding: 40rpx 0; }

/* Pending Notice */
.pending-notice {
  margin-top: 24rpx;
  background: #fff7e6;
  border: 1px solid #ffd591;
  border-radius: 12rpx;
  padding: 16rpx 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.notice-icon { margin-right: 16rpx; font-size: 30rpx; }
.notice-text { font-size: 26rpx; color: #d46b08; flex: 1; }
.notice-arrow { font-size: 24rpx; color: #d46b08; opacity: 0.8; }

/* 批量操作栏 */
.batch-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  min-height: 100rpx; /* 改为最小高度 */
  background: #fff;
  border-top: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 30rpx; /* 增加上下内边距 */
  /* Safe Area Support */
  padding-bottom: calc(20rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-sizing: border-box;
  box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
  z-index: 99;
}
.batch-info { 
  display: flex; 
  align-items: center; 
  gap: 10rpx; 
  font-size: 28rpx; 
  color: #333;
  flex-shrink: 0; /* 防止被压缩 */
}
.batch-actions { 
  display: flex; 
  gap: 16rpx; /* 减小间距 */
  flex-wrap: nowrap; /* 防止换行 */
  align-items: center;
}
.batch-actions .action-btn { 
  background: #20C997; 
  color: #fff; 
  margin: 0;
  padding: 0 20rpx; /* 添加内边距 */
  height: 60rpx; /* 固定高度 */
  line-height: 60rpx; /* 垂直居中 */
  font-size: 26rpx; /* 稍微减小字体 */
  border-radius: 30rpx;
  white-space: nowrap; /* 防止文字换行 */
  flex-shrink: 0; /* 防止被压缩 */
}
.batch-actions .action-btn.warn { 
  background: #ff9f43; 
}
.batch-actions .action-btn.outline {
  background: #fff;
  color: #20C997;
  border: 1px solid #20C997;
}

.has-bottom-bar {
  padding-bottom: calc(120rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));
}

.card-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
.student-card {
  display: block; /* Changed from flex to block to accommodate expanded area */
}
.group-tag {
  font-size: 24rpx;
  color: #666;
  font-weight: normal;
  margin-left: 10rpx;
}
.expand-icon {
  font-size: 24rpx;
  color: #999;
  padding: 10rpx;
}
.card-expanded {
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 1px dashed #eee;
  animation: fadeIn 0.3s ease;
}
.exp-grid {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20rpx;
}
.exp-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}
.exp-label {
  font-size: 22rpx;
  color: #999;
}
.exp-val {
  font-size: 28rpx;
  color: #333;
  font-weight: bold;
  margin-top: 6rpx;
}
.exp-actions {
  display: flex;
  justify-content: flex-end;
  gap: 20rpx;
}
.exp-btn {
  margin: 0;
  background: #20C997;
  color: #fff;
  font-size: 24rpx;
}
.exp-btn.outline {
  background: #fff;
  color: #20C997;
  border: 1px solid #20C997;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10rpx); }
  to { opacity: 1; transform: translateY(0); }
}

.notice-bar.exception {
  background-color: #FFF5F5;
  border-color: #FFD1D1;
  color: #E53E3E;
  margin-top: 10rpx;
}
.notice-bar.exception .notice-icon { color: #E53E3E; }
.notice-bar.exception .arrow { color: #E53E3E; }

/* Report Notification */
.report-notice {
  margin: 20rpx;
  background: #E3F2FD;
  padding: 20rpx;
  border-radius: 12rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #BBDEFB;
}
.notice-left { display: flex; align-items: center; gap: 10rpx; }
.notice-icon { font-size: 32rpx; }
.notice-text { font-size: 28rpx; color: #1976D2; }
.notice-arrow { font-size: 24rpx; color: #1976D2; }

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  z-index: 999;
  display: flex;
  justify-content: center;
  align-items: center;
}
.report-modal {
  width: 90%;
  max-height: 80%;
  background: #fff;
  border-radius: 24rpx;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 8rpx 24rpx rgba(0,0,0,0.15);
}
.modal-header {
  padding: 30rpx;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f8f9fa;
}
.modal-title { font-size: 32rpx; font-weight: bold; }
.close-btn { font-size: 40rpx; color: #999; }
.report-list { flex: 1; padding: 30rpx 0; overflow-y: auto; }
.report-item { margin-bottom: 40rpx; padding: 0 30rpx; }
.report-meta { 
  display: flex; 
  justify-content: space-between; 
  margin-bottom: 16rpx; 
  font-size: 26rpx; 
  color: #666;
  padding: 0 8rpx;
}
.report-card { 
  background: #f9f9f9; 
  padding: 30rpx; 
  border-radius: 20rpx; 
  border: 2rpx solid #eee;
  box-sizing: border-box;
  width: 100%;
}
.report-card.leave { 
  background: #fff7e6; 
  border-color: #ffd591;
}
.report-card.injury { 
  background: #fff1f0; 
  border-color: #ffa39e;
}

.card-header { 
  display: flex;
  align-items: center;
  margin-bottom: 20rpx; 
  border-bottom: 2rpx dashed rgba(0,0,0,0.08);
  padding-bottom: 16rpx;
}

.report-type-tag {
  font-size: 30rpx;
  font-weight: bold;
  display: flex;
  align-items: center;
}
.report-type-tag.leave { color: #d46b08; }
.report-type-tag.injury { color: #cf1322; }

.report-content { 
  font-size: 32rpx; 
  color: #333; 
  line-height: 1.6; 
  display: block;
  word-wrap: break-word;
  word-break: break-all;
  white-space: pre-wrap;
  text-align: justify;
}

.report-time-range {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 8rpx;
  display: block;
}

.report-actions { 
  display: flex; 
  justify-content: space-between; 
  gap: 24rpx; 
  margin-top: 24rpx;
}
.action-btn { 
  flex: 1;
  margin: 0; 
  height: 72rpx; 
  line-height: 72rpx; 
  font-size: 28rpx;
  border-radius: 36rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}
.action-btn.reject { 
  background: #ff4d4f; 
  color: #fff; 
  border: 1px solid #ff4d4f; 
}
.action-btn.approve { 
  background: #20C997; 
  color: #fff; 
  border: 1px solid #20C997; 
}

/* Original styles below */
.mini-bar { display: flex; align-items: center; margin-bottom: 6rpx; }
.mini-label { width: 60rpx; font-size: 22rpx; color: #666; }
.mini-track { flex: 1; height: 10rpx; background: #eee; border-radius: 5rpx; margin: 0 10rpx; }
.mini-fill { height: 100%; border-radius: 5rpx; }
.mini-val { font-size: 22rpx; width: 60rpx; text-align: right; }
.reply-btn { background: #3A7BD5; color: #fff; }
</style>
