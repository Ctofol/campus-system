<template>
  <view class="students-page">
    <view class="header">
      <view class="title-row">
        <text class="title">学员管理</text>
        <view class="batch-toggle" @click="toggleBatchMode">
          <text>{{ isBatchMode ? '取消批量' : '批量管理' }}</text>
        </view>
      </view>
      <view class="toolbar">
        <input v-model="keyword" class="search" placeholder="输入姓名或学号" />
        <picker mode="selector" :range="classOptions" @change="onClassChange">
          <view class="picker">{{ currentClass || '全部班级' }} ▾</view>
        </picker>
        <picker mode="selector" :range="groupOptions" @change="onGroupChange">
          <view class="picker">{{ currentGroup || '全部小组' }} ▾</view>
        </picker>
      </view>
      <view class="summary">
        <view class="sum-item"><text class="sum-val">{{ total }}</text><text class="sum-label">总人数</text></view>
        <view class="sum-item"><text class="sum-val">{{ abnormal }}</text><text class="sum-label">异常</text></view>
        <view class="sum-item"><text class="sum-val">{{ normal }}</text><text class="sum-label">正常</text></view>
      </view>
    </view>

    <!-- AI Analysis Reports Notification -->
    <view class="report-notice" v-if="sharedReports.length > 0" @click="showReportsModal = true">
      <view class="notice-left">
        <text class="notice-icon">🤖</text>
        <text class="notice-text">收到 {{ sharedReports.length }} 份新的运动分析报告</text>
      </view>
      <text class="notice-arrow">查看 ></text>
    </view>

    <view class="card-list" :class="{ 'has-bottom-bar': isBatchMode }">
      <view class="student-card" v-for="(stu, idx) in filteredStudents" :key="idx" @click="handleCardClick(stu)">
        <view class="card-main">
          <view class="card-left">
            <checkbox v-if="isBatchMode" :checked="selectedIds.includes(stu.id)" @click.stop="toggleSelect(stu)" color="#20C997" style="transform:scale(0.8)" />
            <view class="avatar">{{ stu.name.slice(0,1) }}</view>
            <view class="info">
              <text class="name">{{ stu.name }} <text class="group-tag" v-if="stu.group">({{stu.group}})</text></text>
              <text class="meta">学号：{{ stu.no }}</text>
              <text class="meta">班级：{{ stu.className }}</text>
              <text class="meta">健康：{{ stu.health }}</text>
            </view>
          </view>
          <view class="card-right">
            <text class="status" :class="stu.statusClass">{{ stu.status }}</text>
            <text class="expand-icon" v-if="!isBatchMode">{{ stu.expanded ? '▲' : '▼' }}</text>
          </view>
        </view>
        
        <!-- Expanded Details -->
        <view class="card-expanded" v-if="stu.expanded && !isBatchMode">
          <view class="exp-grid">
            <view class="exp-item">
              <text class="exp-label">最近3km</text>
              <text class="exp-val">{{ stu.recent3km || '无记录' }}</text>
            </view>
            <view class="exp-item">
              <text class="exp-label">本周跑量</text>
              <text class="exp-val">{{ stu.weeklyDistance || '0' }}km</text>
            </view>
            <view class="exp-item">
              <text class="exp-label">出勤率</text>
              <text class="exp-val">{{ stu.attendance || '100%' }}</text>
            </view>
          </view>
          <view class="exp-actions">
            <button size="mini" class="exp-btn" @click.stop="openDetail(stu)">完整档案</button>
            <button size="mini" class="exp-btn outline" @click.stop="editGroup(stu)">调整分组</button>
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
        <button size="mini" class="action-btn warn" @click="batchRemind">一键提醒</button>
        <button size="mini" class="action-btn" @click="batchExport">导出数据</button>
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
import { ref, computed } from 'vue';
import { onShow } from '@dcloudio/uni-app';

const isBatchMode = ref(false);
const selectedIds = ref([]);
const sharedReports = ref([]);
const showReportsModal = ref(false);

const students = ref([
  { id: 'S1001', name: '张三', no: '20240001', className: '侦查一班', group: '体能A组', status: '正常', statusClass: 'ok', health: '良好', expanded: false, recent3km: "12'45\"", weeklyDistance: 15.5, attendance: '100%' },
  { id: 'S1002', name: '李四', no: '20240002', className: '侦查二班', group: '体能B组', status: '异常', statusClass: 'warn', health: '需关注', expanded: false, recent3km: "15'30\"", weeklyDistance: 5.0, attendance: '80%' },
  { id: 'S1003', name: '王五', no: '20240003', className: '治安一班', group: '体能A组', status: '正常', statusClass: 'ok', health: '良好', expanded: false, recent3km: "13'10\"", weeklyDistance: 12.0, attendance: '95%' }
]);
const keyword = ref('');
const classOptions = ref(['侦查一班','侦查二班','治安一班']);
const currentClass = ref('');
const groupOptions = ref(['体能A组', '体能B组', '康复组']);
const currentGroup = ref('');

const filteredStudents = computed(() => {
  return students.value.filter(s => {
    const k = keyword.value.trim();
    const matchK = k ? (s.name.includes(k) || s.no.includes(k)) : true;
    const matchC = currentClass.value ? s.className === currentClass.value : true;
    const matchG = currentGroup.value ? s.group === currentGroup.value : true;
    return matchK && matchC && matchG;
  });
});
const total = computed(() => students.value.length);
const abnormal = computed(() => students.value.filter(s=>s.status==='异常').length);
const normal = computed(() => students.value.filter(s=>s.status==='正常').length);

const onClassChange = (e) => {
  const idx = e.detail.value;
  currentClass.value = classOptions.value[idx];
};

const onGroupChange = (e) => {
  const idx = e.detail.value;
  currentGroup.value = groupOptions.value[idx];
};

// 批量操作逻辑
const isAllSelected = computed(() => {
  return filteredStudents.value.length > 0 && selectedIds.value.length === filteredStudents.value.length;
});

const toggleBatchMode = () => {
  isBatchMode.value = !isBatchMode.value;
  selectedIds.value = [];
  if(isBatchMode.value) {
    students.value.forEach(s => s.expanded = false);
  }
};

const handleCardClick = (stu) => {
  if (isBatchMode.value) {
    toggleSelect(stu);
  } else {
    stu.expanded = !stu.expanded;
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

const batchRemind = () => {
  if (selectedIds.value.length === 0) return uni.showToast({ title: '请先选择学员', icon: 'none' });
  uni.showModal({
    title: '批量提醒',
    content: `确定向选中的 ${selectedIds.value.length} 位学员发送跑步提醒吗？`,
    success: (res) => {
      if (res.confirm) {
        uni.showToast({ title: '发送成功', icon: 'success' });
        toggleBatchMode();
      }
    }
  });
};

const batchExport = () => {
  if (selectedIds.value.length === 0) return uni.showToast({ title: '请先选择学员', icon: 'none' });
  uni.showLoading({ title: '生成报表中...' });
  setTimeout(() => {
    uni.hideLoading();
    uni.showToast({ title: '导出成功，已发送至邮箱', icon: 'success' });
    toggleBatchMode();
  }, 1500);
};

const batchGroup = () => {
  if (selectedIds.value.length === 0) return uni.showToast({ title: '请先选择学员', icon: 'none' });
  uni.showActionSheet({
    itemList: groupOptions.value,
    success: (res) => {
      const groupName = groupOptions.value[res.tapIndex];
      students.value.forEach(s => {
        if(selectedIds.value.includes(s.id)) {
          s.group = groupName;
        }
      });
      uni.showToast({ title: '批量分组成功', icon: 'success' });
      toggleBatchMode();
    }
  });
};

const editGroup = (stu) => {
  uni.showActionSheet({
    itemList: groupOptions.value,
    success: (res) => {
      stu.group = groupOptions.value[res.tapIndex];
      uni.showToast({ title: '已调整分组', icon: 'none' });
    }
  });
};

onShow(() => {
  const role = uni.getStorageSync('userRole') || uni.getStorageSync('role');
  if (role !== 'teacher') {
    uni.showToast({ title: '请使用教师账号登录', icon: 'none' });
    uni.redirectTo({ url: '/pages/login/login' });
  }
  sharedReports.value = uni.getStorageSync('mockSharedReports') || [];
});

const replyStudent = (report) => {
  uni.showModal({
    title: '回复指导',
    editable: true,
    placeholderText: '请输入指导建议...',
    success: (res) => {
      if (res.confirm && res.content) {
        uni.showToast({ title: '已发送指导', icon: 'success' });
        // In real app, send notification to student
      }
    }
  });
};

const openDetail = (stu) => {
  uni.navigateTo({
    url: `/pages/teacher/students/detail?id=${stu.id}&name=${stu.name}&no=${stu.no}&class=${stu.className}`
  });
};
</script>

<style scoped>
.students-page { min-height: 100vh; background: #f8f8f8; }
.header { background: #fff; padding: 24rpx 20rpx; border-bottom: 1px solid #eee; }
.title-row { display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 34rpx; font-weight: bold; color: #333; }
.batch-toggle { font-size: 28rpx; color: #20C997; padding: 10rpx; }
.toolbar { display: flex; gap: 12rpx; margin-top: 12rpx; }
.search { flex: 1; border: 1px solid #eee; border-radius: 8rpx; padding: 12rpx; }
.picker { border: 1px solid #eee; border-radius: 8rpx; padding: 12rpx; color: #333; }
.summary { display: flex; gap: 20rpx; margin-top: 12rpx; }
.sum-item { background: #f7f7f7; padding: 12rpx; border-radius: 8rpx; width: 30%; text-align: center; }
.sum-val { font-size: 30rpx; font-weight: bold; color: #20C997; display: block; }
.sum-label { font-size: 24rpx; color: #666; display: block; }
.card-list { margin-top: 10rpx; padding-bottom: 20rpx; }
.card-list.has-bottom-bar { padding-bottom: 120rpx; }
.student-card { display: flex; justify-content: space-between; align-items: center; background: #fff; margin: 10rpx 0; padding: 20rpx; border-radius: 12rpx; }
.card-left { display: flex; align-items: center; }
.avatar { width: 72rpx; height: 72rpx; border-radius: 50%; background: #4ECDC4; color: #fff; display: flex; align-items: center; justify-content: center; margin-right: 14rpx; }
.info { display: flex; flex-direction: column; }
.name { font-size: 32rpx; font-weight: bold; color: #333; }
.meta { font-size: 26rpx; color: #666; margin-top: 6rpx; }
.card-right { display: flex; align-items: center; gap: 10rpx; }
.status { font-size: 26rpx; }
.status.ok { color: #20C997; }
.status.warn { color: #d81e06; }
.detail-btn { background: #20C997; color: #fff; }
.empty { text-align: center; color: #999; padding: 40rpx 0; }

/* 批量操作栏 */
.batch-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100rpx;
  background: #fff;
  border-top: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30rpx;
  box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
  z-index: 99;
  box-sizing: border-box;
}
.batch-info { display: flex; align-items: center; gap: 10rpx; font-size: 28rpx; color: #333; }
.batch-actions { display: flex; gap: 20rpx; }
.action-btn { background: #20C997; color: #fff; margin: 0; }
.action-btn.warn { background: #ff9f43; }
.action-btn.outline {
  background: #fff;
  color: #20C997;
  border: 1px solid #20C997;
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
  border-radius: 20rpx;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.modal-header {
  padding: 20rpx;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-title { font-size: 32rpx; font-weight: bold; }
.close-btn { font-size: 40rpx; color: #999; }
.report-list { flex: 1; padding: 20rpx; overflow-y: auto; }
.report-item { margin-bottom: 30rpx; background: #f9f9f9; padding: 20rpx; border-radius: 12rpx; }
.report-meta { display: flex; justify-content: space-between; margin-bottom: 10rpx; font-size: 24rpx; color: #666; }
.report-card { background: #fff; padding: 16rpx; border-radius: 8rpx; border: 1px solid #eee; margin-bottom: 10rpx; }
.report-title { font-weight: bold; font-size: 28rpx; display: block; margin-bottom: 10rpx; }
.report-suggestion { font-size: 26rpx; color: #FF9F43; display: block; margin-bottom: 10rpx; }
.mini-bar { display: flex; align-items: center; margin-bottom: 6rpx; }
.mini-label { width: 60rpx; font-size: 22rpx; color: #666; }
.mini-track { flex: 1; height: 10rpx; background: #eee; border-radius: 5rpx; margin: 0 10rpx; }
.mini-fill { height: 100%; border-radius: 5rpx; }
.mini-val { font-size: 22rpx; width: 60rpx; text-align: right; }
.report-actions { text-align: right; }
.reply-btn { background: #3A7BD5; color: #fff; }
</style>
