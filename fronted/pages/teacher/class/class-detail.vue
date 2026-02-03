<template>
  <view class="container">
    <view class="header" v-if="classInfo">
      <view>
        <text class="title">{{ classInfo.name }}</text>
        <text class="sub-title">{{ classInfo.student_count }} 名学生</text>
      </view>
      <button size="mini" type="primary" @click="showAddModal = true">+ 添加学生</button>
    </view>
    
    <view class="stats-card" v-if="stats">
      <view class="stat-item">
        <text class="val">{{ stats.total_distance ? stats.total_distance.toFixed(1) : '0.0' }}</text>
        <text class="label">总里程 (km)</text>
      </view>
      <view class="stat-item">
        <text class="val">{{ stats.total_activities }}</text>
        <text class="label">总运动次数</text>
      </view>
    </view>

    <!-- Filter Section -->
    <view class="filter-card">
      <view class="filter-row">
        <picker class="filter-picker" :range="taskOptions" range-key="title" @change="onTaskChange">
          <view class="picker-view">
            <text>任务筛选:</text>
            <text class="picker-val">{{ selectedTaskIndex > -1 ? taskOptions[selectedTaskIndex].title : '全部任务' }}</text>
          </view>
        </picker>
      </view>
      <view class="filter-row date-row">
        <picker mode="date" @change="onStartDateChange">
          <view class="date-picker">
            {{ startDate || '开始日期' }}
          </view>
        </picker>
        <text class="sep">至</text>
        <picker mode="date" @change="onEndDateChange">
          <view class="date-picker">
            {{ endDate || '结束日期' }}
          </view>
        </picker>
      </view>
      <button class="filter-btn" type="default" size="mini" @click="fetchStats">应用筛选</button>
    </view>

    <view class="list-title">学生列表</view>
    <view class="student-list">
      <view class="student-item" v-for="stu in students" :key="stu.id" @click="navigateToStudent(stu.id)">
        <view class="info">
          <text class="name">{{ stu.name }}</text>
          <text class="detail">里程: {{ stu.distance ? stu.distance.toFixed(1) : '0.0' }}km | 次数: {{ stu.count }}</text>
        </view>
        <text class="remove-btn" @click.stop="removeStudent(stu)">移除</text>
      </view>
      <view v-if="students.length === 0" class="empty-tip">暂无学生</view>
    </view>

    <!-- Add Modal -->
    <view v-if="showAddModal" class="modal-mask">
      <view class="modal">
        <view class="modal-title">添加学生</view>
        <input class="input" v-model="studentPhone" placeholder="请输入学生手机号" type="number" />
        <view class="modal-btns">
          <button size="mini" @click="showAddModal = false">取消</button>
          <button size="mini" type="primary" @click="addStudent">确定</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { onLoad } from '@dcloudio/uni-app';
import { ref } from 'vue';
import { request } from '@/utils/request';

const classId = ref(null);
const classInfo = ref(null);
const stats = ref(null);
const students = ref([]);
const showAddModal = ref(false);
const studentPhone = ref('');

// Filter state
const tasks = ref([]);
const taskOptions = ref([]);
const selectedTaskIndex = ref(-1);
const startDate = ref('');
const endDate = ref('');

onLoad((options) => {
  if (options.id) {
    classId.value = options.id;
    fetchData();
    fetchTasks();
  }
});

const fetchTasks = async () => {
  try {
    const res = await request({ url: '/teacher/tasks', data: { size: 100 } }); // Fetch all tasks
    tasks.value = res.items;
    taskOptions.value = [{ title: '全部任务', id: null }, ...res.items];
  } catch (e) {
    console.error('Fetch tasks failed', e);
  }
};

const fetchData = async () => {
  if (!classId.value) return;
  try {
    // Get basic info
    const info = await request({ url: `/teacher/classes/${classId.value}` });
    classInfo.value = info;
    
    // Get stats
    await fetchStats();
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' });
  }
};

const fetchStats = async () => {
  if (!classId.value) return;
  try {
    const params = {};
    if (selectedTaskIndex.value > -1) {
       const taskId = taskOptions.value[selectedTaskIndex.value].id;
       if (taskId) params.task_id = taskId;
    }
    if (startDate.value) params.start_date = new Date(startDate.value).toISOString();
    if (endDate.value) params.end_date = new Date(endDate.value).toISOString();

    const statRes = await request({ 
      url: `/teacher/classes/${classId.value}/stats`,
      data: params
    });
    stats.value = statRes;
    students.value = statRes.student_stats; 
  } catch (e) {
    uni.showToast({ title: '统计加载失败', icon: 'none' });
  }
};

const onTaskChange = (e) => {
  selectedTaskIndex.value = e.detail.value;
};

const onStartDateChange = (e) => {
  startDate.value = e.detail.value;
};

const onEndDateChange = (e) => {
  endDate.value = e.detail.value;
};

const navigateToStudent = (studentId) => {
    uni.navigateTo({ url: `/pages/teacher/students/detail?id=${studentId}` });
};

const addStudent = async () => {
  if (!studentPhone.value) return;
  try {
    await request({
      url: `/teacher/classes/${classId.value}/students`,
      method: 'POST',
      data: { phone: studentPhone.value }
    });
    showAddModal.value = false;
    studentPhone.value = '';
    fetchData();
    uni.showToast({ title: '添加成功', icon: 'success' });
  } catch (e) {
    uni.showToast({ title: '添加失败: ' + (e.message || '找不到学生'), icon: 'none' });
  }
};

const removeStudent = async (stu) => {
  if (!stu.id) return; 
  
  uni.showModal({
    title: '确认移除',
    content: `确定将 ${stu.name} 移出班级吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await request({ url: `/teacher/classes/${classId.value}/students/${stu.id}`, method: 'DELETE' });
          fetchData();
        } catch (e) {
          uni.showToast({ title: '移除失败', icon: 'none' });
        }
      }
    }
  });
};
</script>

<style>
.container { padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.title { font-size: 22px; font-weight: bold; display: block; }
.sub-title { font-size: 14px; color: #666; }
.stats-card { background: #20C997; color: white; padding: 20px; border-radius: 10px; display: flex; justify-content: space-around; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(32, 201, 151, 0.3); }
.stat-item { display: flex; flex-direction: column; align-items: center; }
.val { font-size: 24px; font-weight: bold; }
.label { font-size: 12px; opacity: 0.9; }

.filter-card { background: #fff; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.filter-row { margin-bottom: 12px; display: flex; align-items: center; }
.filter-picker { flex: 1; border: 1px solid #eee; padding: 8px; border-radius: 4px; }
.picker-view { display: flex; justify-content: space-between; font-size: 14px; }
.picker-val { font-weight: bold; color: #333; }
.date-row { justify-content: space-between; }
.date-picker { border: 1px solid #eee; padding: 8px; border-radius: 4px; font-size: 13px; min-width: 100px; text-align: center; color: #666; }
.sep { margin: 0 10px; color: #999; }
.filter-btn { width: 100%; margin-top: 5px; }

.list-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; border-left: 4px solid #20C997; padding-left: 10px; }
.student-item { background: white; padding: 15px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.name { font-weight: bold; font-size: 16px; margin-right: 10px; }
.detail { color: #666; font-size: 12px; }
.remove-btn { color: #999; font-size: 12px; padding: 5px; }
.empty-tip { text-align: center; color: #999; margin-top: 20px; }
.modal-mask { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 999; }
.modal { background: #fff; padding: 20px; border-radius: 10px; width: 80%; }
.modal-title { font-size: 18px; font-weight: bold; margin-bottom: 15px; text-align: center; }
.input { border: 1px solid #ddd; padding: 10px; border-radius: 5px; margin-bottom: 20px; height: 40px; }
.modal-btns { display: flex; justify-content: space-around; }
</style>