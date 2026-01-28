<template>
  <view class="home-container">
    <view class="teacher-dashboard">
      <!-- 自定义导航栏 -->
      <view class="custom-nav-bar">
        <view class="nav-status-bar"></view>
        <view class="nav-content">
          <text class="nav-title">教师工作台</text>
        </view>
      </view>
      
      <!-- 1. 教师头部信息 -->
      <view class="teacher-header">
        <view class="teacher-info">
          <text class="teacher-name">{{ userInfo.name || '老师' }}</text>
          <text class="teacher-title">体育教研室</text>
        </view>
        <view class="teacher-avatar">
                <image class="avatar-img" src="/static/avatar.png" mode="aspectFill"></image>
              </view>
            </view>
            <!-- 2. 核心数据概览 (替代原有功能卡片) -->
      <view class="dashboard-stats">
        <view class="stat-card">
          <text class="stat-num">{{ teacherStats.todayCheckin }}</text>
          <text class="stat-label">今日打卡</text>
        </view>
        <view class="stat-card">
          <text class="stat-num">{{ teacherStats.abnormalCount }}</text>
          <text class="stat-label">异常待处理</text>
        </view>
        <view class="stat-card" @click="goToApprove">
          <text class="stat-num">{{ teacherStats.pendingApprovals || 12 }}</text>
          <text class="stat-label">待审批</text>
        </view>
      </view>

      <!-- 3. 待办事项 (新增) -->
      <view class="section-card todo-section">
        <view class="section-header">
          <text class="section-title">今日待办</text>
          <text class="section-more">全部 ></text>
        </view>
        <view class="todo-list">
          <view class="todo-item">
            <view class="todo-check"></view>
            <view class="todo-content">
              <text class="todo-text">审批 2023级体测成绩</text>
              <text class="todo-time">截止: 17:00</text>
            </view>
          </view>
          <view class="todo-item">
            <view class="todo-check"></view>
            <view class="todo-content">
              <text class="todo-text">发布本周训练计划</text>
              <text class="todo-time">待处理</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 3. 学员整体数据概览 (新增图表) -->
      <view class="section-card chart-section">
        <view class="section-header">
          <text class="section-title">学员体能概览</text>
          <text class="section-more">更多 ></text>
        </view>
        <view class="overview-chart">
          <view class="chart-col">
            <view class="chart-ring ring-green">
              <text class="ring-val">92%</text>
              <text class="ring-label">达标率</text>
            </view>
            <text class="chart-name">体能达标</text>
          </view>
          <view class="chart-col">
            <view class="chart-ring ring-blue">
              <text class="ring-val">85%</text>
              <text class="ring-label">完成率</text>
            </view>
            <text class="chart-name">本周任务</text>
          </view>
          <view class="chart-col">
            <view class="chart-ring ring-red">
              <text class="ring-val">5'45"</text>
              <text class="ring-label">平均配速</text>
            </view>
            <text class="chart-name">跑步状态</text>
          </view>
        </view>
        
        <!-- 新增：本周运动趋势 -->
        <view class="trend-chart">
          <text class="trend-title">本周运动趋势</text>
          <view class="trend-bars">
            <view class="t-bar-group" v-for="(d, i) in weeklyTrend" :key="i">
              <view class="t-bar" :style="{height: d.val + '%', background: d.color}"></view>
              <text class="t-day">{{ d.day }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 4. 任务管理快捷交互 (新增) -->
      <view class="section-card task-widget">
        <view class="section-header">
          <text class="section-title">快速任务管理</text>
          <view class="header-actions">
             <text class="section-action" @click="openTaskModal">+ 发布</text>
          </view>
        </view>
        <scroll-view scroll-x class="quick-task-scroll">
          <view class="quick-task-item" v-for="(task, idx) in quickTasks" :key="idx" @click="handleQuickTask(task)">
            <view class="qt-header">
              <text class="qt-type" :class="task.typeClass">{{ task.type }}</text>
              <text class="qt-status">{{ task.status }}</text>
            </view>
            <text class="qt-title">{{ task.title }}</text>
            <view class="qt-progress">
              <view class="qt-bar-bg">
                <view class="qt-bar-fill" :style="{ width: task.percent + '%' }"></view>
              </view>
              <text class="qt-val">{{ task.percent }}%</text>
            </view>
            <!-- 快捷操作按钮 -->
            <view class="qt-actions" @click.stop>
               <text class="qt-btn" @click="editTask(task)">编辑</text>
               <text class="qt-btn warn" v-if="task.percent < 100" @click="remindTask(task)">催办</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 5. 实时异常警报 (优化样式) -->
      <view class="section-card alert-widget" v-if="abnormalAlerts.length > 0">
        <view class="section-header">
          <text class="section-title red-dot">⚠️ 实时警报</text>
        </view>
        <view class="alert-feed">
          <view class="feed-item" v-for="(alert, idx) in abnormalAlerts" :key="idx">
            <view class="feed-content">
              <text class="feed-msg"><text class="feed-name">{{ alert.student }}</text> {{ alert.type }} ({{ alert.value }})</text>
              <text class="feed-time">{{ alert.time }}</text>
            </view>
            <button class="feed-btn" size="mini" @click="handleResolveAlert(idx)">干预</button>
          </view>
        </view>
      </view>
      
      <!-- 快速发布任务弹窗 -->
      <view class="modal-overlay" v-if="showTaskModal" @click="showTaskModal = false">
        <view class="task-modal" @click.stop>
          <view class="modal-header">
            <text class="modal-title">{{ isEditing ? '编辑任务' : '快速发布任务' }}</text>
            <text class="close-btn" @click="showTaskModal = false">×</text>
          </view>
          <view class="modal-body">
            <input class="modal-input" placeholder="任务标题" v-model="currentTask.title" />
            <view class="modal-types">
              <view class="type-chip" :class="{active: currentTask.type === '考核'}" @click="currentTask.type = '考核'">考核</view>
              <view class="type-chip" :class="{active: currentTask.type === '日常'}" @click="currentTask.type = '日常'">日常</view>
              <view class="type-chip" :class="{active: currentTask.type === '训练'}" @click="currentTask.type = '训练'">训练</view>
            </view>
            <textarea class="modal-textarea" placeholder="任务描述" v-model="currentTask.desc" />
          </view>
          <button class="modal-submit-btn" @click="saveTask">确认发布</button>
        </view>
      </view>

     <view style="height: 120rpx;"></view> <!-- Spacer for TabBar -->
      <CustomTabBar current="/pages/teacher/home/home" />
    </view>
    
    <!-- 快速发布任务弹窗 -->
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import CustomTabBar from '@/components/CustomTabBar/CustomTabBar.vue';

const userInfo = ref({});

const goToApprove = () => {
  uni.navigateTo({ url: '/pages/teacher/approve/approve' });
};

onShow(() => {
  // 隐藏左上角 Home 按钮
  uni.hideHomeButton && uni.hideHomeButton();

  const storedUser = uni.getStorageSync('userInfo');
  if (storedUser) {
    try {
        userInfo.value = typeof storedUser === 'string' ? JSON.parse(storedUser) : storedUser;
    } catch (e) {
        console.error('JSON parse error', e);
        userInfo.value = {};
    }
  }
});

// --- 教师端数据 ---
const teacherStats = ref({
  studentCount: 128,
  todayCheckin: 105,
  abnormalCount: 3,
  avgPace: "5'45\"",
  taskCount: 5,
  complianceRate: 92
});

const weeklyTrend = ref([
  { day: '周一', val: 60, color: '#e0e0e0' },
  { day: '周二', val: 80, color: '#e0e0e0' },
  { day: '周三', val: 45, color: '#e0e0e0' },
  { day: '周四', val: 90, color: '#20C997' },
  { day: '周五', val: 70, color: '#e0e0e0' },
  { day: '周六', val: 30, color: '#e0e0e0' },
  { day: '周日', val: 50, color: '#e0e0e0' }
]);

const showTaskModal = ref(false);
const isEditing = ref(false);
const currentTask = ref({ title: '', type: '日常', desc: '' });

const quickTasks = ref([
  { title: '3000米摸底测试', type: '考核', typeClass: 'tag-red', status: '进行中', percent: 76 },
  { title: '周末晨跑打卡', type: '日常', typeClass: 'tag-green', status: '进行中', percent: 35 },
  { title: '核心力量专项', type: '训练', typeClass: 'tag-blue', status: '即将截止', percent: 88 }
]);

const abnormalAlerts = ref([
  { id: 1, student: '张三', type: '心率过高', value: '195 bpm', time: '10:30' },
  { id: 2, student: '李四', type: '配速异常', value: '过快', time: '10:45' },
  { id: 3, student: '王五', type: '动作不达标', value: '引体向上', time: '10:50' }
]);

const handleTeacherAction = (action) => {
  if (action === '学员管理') {
    uni.navigateTo({ url: '/pages/teacher/students/students' });
  } else if (action === '任务管理') {
    uni.navigateTo({ url: '/pages/teacher/tasks/tasks' });
  } else if (action === '发布任务') {
    uni.navigateTo({ url: '/pages/teacher/tasks/create' });
  } else if (action === '异常处理') {
    uni.navigateTo({ url: '/pages/teacher/exceptions/exceptions' });
  } else if (action === '测试监控') {
    uni.navigateTo({ url: '/pages/teacher/tests/tests' });
  } else {
    uni.showToast({ title: `${action}功能即将上线`, icon: 'none' });
  }
};

const openTaskModal = () => {
  isEditing.value = false;
  currentTask.value = { title: '', type: '日常', desc: '' };
  showTaskModal.value = true;
};

const editTask = (task) => {
  isEditing.value = true;
  currentTask.value = { ...task, desc: '任务描述...' };
  showTaskModal.value = true;
};

const saveTask = () => {
  if (!currentTask.value.title) return uni.showToast({ title: '请输入标题', icon: 'none' });
  uni.showToast({ title: isEditing.value ? '修改成功' : '发布成功', icon: 'success' });
  showTaskModal.value = false;
  // In real app, update list
};

const remindTask = (task) => {
  uni.showToast({ title: `已催办任务: ${task.title}`, icon: 'none' });
};

const handleQuickTask = (task) => {
  uni.navigateTo({
    url: `/pages/teacher/tasks/detail?id=999&title=${task.title}`
  });
};

const handleResolveAlert = (index) => {
  uni.showActionSheet({
    itemList: ['联系学生', '标记已处理', '查看详情'],
    success: (res) => {
      if (res.tapIndex === 1) {
        abnormalAlerts.value.splice(index, 1);
        teacherStats.value.abnormalCount = Math.max(0, teacherStats.value.abnormalCount - 1);
        uni.showToast({ title: '已处理', icon: 'success' });
      } else if (res.tapIndex === 0) {
        uni.showToast({ title: '已发送通知', icon: 'none' });
      } else {
        uni.navigateTo({ url: '/pages/teacher/exceptions/exceptions' });
      }
    }
  });
};
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

/* 自定义导航栏 */
.custom-nav-bar {
  background: #20C997;
  width: 100%;
  position: sticky;
  top: 0;
  z-index: 100;
}
.nav-status-bar {
  height: var(--status-bar-height);
  width: 100%;
}
.nav-content {
  height: 44px; /* 标准导航栏高度 */
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.nav-title {
  color: #fff;
  font-size: 32rpx;
  font-weight: bold;
}

/* 教师端样式 */
.teacher-header {
  background: #20C997;
  padding: 40rpx 30rpx 60rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom-left-radius: 40rpx;
  border-bottom-right-radius: 40rpx;
  color: #fff;
  margin-bottom: 20rpx;
}
.teacher-name { font-size: 36rpx; font-weight: bold; display: block; }
.teacher-title { font-size: 24rpx; opacity: 0.9; }
.teacher-avatar { font-size: 60rpx; background: rgba(255,255,255,0.2); width: 100rpx; height: 100rpx; border-radius: 50%; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.avatar-img { width: 100%; height: 100%; }

/* Dashboard Stats */
.dashboard-stats {
  display: flex;
  justify-content: space-between;
  padding: 0 30rpx;
  margin-top: -40rpx;
  margin-bottom: 30rpx;
}
.stat-card {
  width: 31%;
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.05);
  box-sizing: border-box;
}
.stat-num {
  font-size: 40rpx;
  font-weight: bold;
  color: #20C997;
  margin-bottom: 8rpx;
}
.stat-label {
  font-size: 24rpx;
  color: #666;
}

/* Todo List */
.todo-list {
  display: flex;
  flex-direction: column;
}
.todo-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1px solid #f5f5f5;
}
.todo-item:last-child {
  border-bottom: none;
}
.todo-check {
  width: 36rpx;
  height: 36rpx;
  border: 2rpx solid #ddd;
  border-radius: 50%;
  margin-right: 20rpx;
}
.todo-content {
  display: flex;
  flex-direction: column;
}
.todo-text {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 4rpx;
}
.todo-time {
  font-size: 22rpx;
  color: #999;
}

.module-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 30rpx;
  padding: 0 30rpx;
  margin-top: -40rpx; /* Overlap header */
}

.module-card {
  width: 48%;
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.05);
  position: relative;
  overflow: hidden;
  margin-bottom: 20rpx;
  min-height: 180rpx;
  box-sizing: border-box;
}

.card-icon-container {
  width: 70rpx;
  height: 70rpx;
  background: rgba(0,0,0,0.03);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20rpx;
}

.card-emoji {
  font-size: 36rpx;
}

.card-content {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.card-purple { border-left: 8rpx solid #a55eea; }
.card-green { border-left: 8rpx solid #20C997; }
.card-blue { border-left: 8rpx solid #4dabf7; }
.card-orange { border-left: 8rpx solid #ff9f43; }

.card-title { font-size: 30rpx; font-weight: bold; color: #333; margin-bottom: 8rpx; }
.card-desc { font-size: 24rpx; color: #888; }

.section-card {
  background: #fff;
  border-radius: 20rpx;
  margin: 20rpx 30rpx;
  padding: 30rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.02);
}

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24rpx; }
.section-title { font-size: 32rpx; font-weight: bold; color: #333; }
.section-more, .section-action { font-size: 26rpx; color: #20C997; }
.red-dot { color: #ff6b6b; }

.overview-chart { display: flex; justify-content: space-around; }
.chart-col { text-align: center; }
.chart-ring { width: 120rpx; height: 120rpx; border-radius: 50%; border: 8rpx solid #eee; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 10rpx; }
.ring-green { border-color: #20C997; }
.ring-blue { border-color: #4dabf7; }
.ring-red { border-color: #ff6b6b; }
.ring-val { font-size: 28rpx; font-weight: bold; color: #333; }
.ring-label { font-size: 18rpx; color: #999; }
.chart-name { font-size: 24rpx; color: #666; }

.quick-task-scroll { white-space: nowrap; width: 100%; }
.quick-task-item { display: inline-block; width: 280rpx; background: #f8f9fa; border-radius: 12rpx; padding: 20rpx; margin-right: 20rpx; vertical-align: top; }
.qt-header { display: flex; justify-content: space-between; margin-bottom: 12rpx; }

.qt-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16rpx;
  margin-top: 16rpx;
  border-top: 1px dashed #eee;
  padding-top: 10rpx;
}

.qt-btn {
  font-size: 22rpx;
  color: #666;
  padding: 4rpx 12rpx;
  border: 1px solid #ddd;
  border-radius: 8rpx;
}

.qt-btn.warn {
  color: #ff6b6b;
  border-color: #ff6b6b;
}

.qt-type { font-size: 20rpx; padding: 2rpx 8rpx; border-radius: 6rpx; color: #fff; }
.tag-red { background: #ff6b6b; }
.tag-green { background: #20C997; }
.tag-blue { background: #4dabf7; }
.qt-status { font-size: 20rpx; color: #999; }
.qt-title { font-size: 26rpx; font-weight: bold; color: #333; display: block; margin-bottom: 16rpx; white-space: normal; height: 72rpx; line-height: 36rpx; overflow: hidden; }
.qt-progress { display: flex; align-items: center; }
.qt-bar-bg { flex: 1; height: 8rpx; background: #eee; border-radius: 4rpx; overflow: hidden; margin-right: 10rpx; }
.qt-bar-fill { height: 100%; background: #20C997; }
.qt-val { font-size: 20rpx; color: #666; }

/* Trend Chart */
.trend-chart {
  margin-top: 30rpx;
  border-top: 1px solid #f5f5f5;
  padding-top: 20rpx;
}
.trend-title { font-size: 26rpx; color: #333; font-weight: bold; margin-bottom: 20rpx; display: block; }
.trend-bars {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  height: 120rpx;
}
.t-bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 40rpx;
  height: 100%;
  justify-content: flex-end;
}
.t-bar {
  width: 12rpx;
  border-radius: 6rpx;
  background: #eee;
}
.t-day { font-size: 20rpx; color: #999; margin-top: 8rpx; }

/* Alert Feed */
.alert-feed { display: flex; flex-direction: column; gap: 20rpx; }
.feed-item { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 20rpx; 
  background: #fff5f5; 
  border-radius: 12rpx; 
  border-left: 8rpx solid #ff6b6b; /* Increased border width */
  box-shadow: 0 2rpx 6rpx rgba(255, 107, 107, 0.1); /* Added shadow */
}
.feed-content {
  flex: 1; /* Allow content to take available space */
  margin-right: 20rpx; /* Spacing between text and button */
  overflow: hidden; /* Prevent overflow */
}
.feed-msg { 
  font-size: 26rpx; 
  color: #333; 
  display: block; /* Ensure block display for wrapping */
  word-wrap: break-word; /* Ensure long text wraps */
  line-height: 1.4;
}
.feed-name { font-weight: bold; margin-right: 10rpx; }
.feed-time { font-size: 22rpx; color: #999; display: block; margin-top: 8rpx; }
.feed-btn { 
  flex-shrink: 0; /* Prevent button from shrinking */
  background: #ff6b6b; 
  color: #fff; 
  font-size: 22rpx; 
  padding: 0 24rpx; 
  height: 56rpx; /* Increased height for better touch area */
  line-height: 56rpx; 
  border-radius: 28rpx; /* Rounded corners */
}

/* Modal */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; justify-content: center; align-items: center; }
.task-modal { width: 600rpx; background: #fff; border-radius: 20rpx; padding: 30rpx; }
.modal-header { display: flex; justify-content: space-between; margin-bottom: 30rpx; }
.modal-title { font-size: 32rpx; font-weight: bold; }
.close-btn { font-size: 40rpx; color: #999; line-height: 1; }
.modal-input { background: #f5f7fa; height: 80rpx; padding: 0 20rpx; border-radius: 10rpx; margin-bottom: 20rpx; font-size: 28rpx; }
.modal-types { display: flex; gap: 20rpx; margin-bottom: 20rpx; }
.type-chip { padding: 10rpx 30rpx; background: #f5f7fa; border-radius: 30rpx; font-size: 24rpx; color: #666; }
.type-chip.active { background: #20C997; color: #fff; }
.modal-textarea { width: 100%; height: 160rpx; background: #f5f7fa; padding: 20rpx; border-radius: 10rpx; font-size: 28rpx; box-sizing: border-box; margin-bottom: 30rpx; }
.modal-submit-btn { background: #20C997; color: #fff; border-radius: 40rpx; font-size: 30rpx; }
</style>
