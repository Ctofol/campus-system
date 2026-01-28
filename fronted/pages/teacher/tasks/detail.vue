<template>
  <view class="container">
    <!-- Header Section -->
    <view class="header-card">
      <view class="title-row">
        <text class="task-title">{{ task.title }}</text>
        <view class="status-tag" :class="task.status">{{ task.statusText }}</view>
      </view>
      <text class="due-date">截止日期：{{ task.dueDate }}</text>
    </view>

    <!-- Task Requirements -->
    <view class="section-card">
      <view class="section-header">
        <text class="section-title">任务要求</text>
      </view>
      <view class="requirements-list">
        <view class="req-item" v-for="(req, index) in task.requirements" :key="index">
          <text class="dot">•</text>
          <text class="req-text">{{ req }}</text>
        </view>
      </view>
    </view>

    <!-- Progress Overview -->
    <view class="section-card">
      <view class="section-header">
        <text class="section-title">完成进度</text>
        <text class="progress-stats">{{ task.completedCount }}/{{ task.totalCount }} 人</text>
      </view>
      <view class="progress-box">
        <view class="progress-bar">
          <view class="progress-fill" :style="{ width: completionPercentage + '%' }"></view>
        </view>
        <text class="percentage-text">{{ completionPercentage }}%</text>
      </view>
    </view>

    <!-- Student Participation List -->
    <view class="section-card">
      <view class="section-header">
        <text class="section-title">参与情况</text>
        <view class="filter-tabs">
          <text 
            class="tab-item" 
            :class="{ active: currentFilter === 'all' }"
            @click="currentFilter = 'all'"
          >全部</text>
          <text 
            class="tab-item" 
            :class="{ active: currentFilter === 'uncompleted' }"
            @click="currentFilter = 'uncompleted'"
          >未完成</text>
        </view>
      </view>
      
      <scroll-view scroll-y class="student-list">
        <view class="student-item" v-for="student in filteredStudents" :key="student.id" @click="goToStudentDetail(student)">
          <view class="student-info">
            <image class="avatar" :src="student.avatar || '/static/avatar.png'" mode="aspectFill"></image>
            <view class="info-col">
              <text class="name">{{ student.name }}</text>
              <text class="id">{{ student.studentId }}</text>
              <text v-if="student.metricValue && student.metricValue !== '-'" class="metric-val">成绩: {{ student.metricValue }}</text>
            </view>
          </view>
          <view class="status-col">
            <text class="status-text" :class="student.status">{{ student.statusText }}</text>
            <button 
              v-if="student.status === 'uncompleted'" 
              class="remind-btn" 
              size="mini"
              @click.stop="remindStudent(student)"
            >提醒</button>
          </view>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { getTeacherTaskDetail } from '@/utils/request.js';

const taskId = ref(null);
const loading = ref(true);

const task = ref({
  id: 0,
  title: '',
  status: '',
  statusText: '',
  dueDate: '',
  requirements: [],
  completedCount: 0,
  totalCount: 0
});

const students = ref([]);
const currentFilter = ref('all');

const completionPercentage = computed(() => {
  if (task.value.totalCount === 0) return 0;
  return Math.round((task.value.completedCount / task.value.totalCount) * 100);
});

const filteredStudents = computed(() => {
  if (currentFilter.value === 'all') return students.value;
  return students.value.filter(s => s.status === currentFilter.value);
});

const remindStudent = (student) => {
  uni.showToast({
    title: `已发送提醒给 ${student.name}`,
    icon: 'success'
  });
};

const goToStudentDetail = (student) => {
    uni.navigateTo({
        url: `/pages/teacher/approve/student-detail?studentId=${student.id}&studentName=${student.name}`
    });
};

const fetchTaskDetail = async () => {
    if (!taskId.value) return;
    loading.value = true;
    try {
        const res = await getTeacherTaskDetail(taskId.value);
        
        // Parse Requirements
        const reqs = [];
        if (res.type === 'run') {
            reqs.push('任务类型: 跑步任务');
            if (res.min_distance) reqs.push(`最低距离: ${res.min_distance} km`);
            if (res.min_duration) reqs.push(`最低时长: ${res.min_duration} 分钟`);
        } else {
            reqs.push('任务类型: 体测任务');
            if (res.min_count) reqs.push(`最低次数: ${res.min_count} 次`);
        }
        if (res.description) reqs.push(`备注: ${res.description}`);
        
        // Determine Status
        const now = new Date();
        const deadline = res.deadline ? new Date(res.deadline) : null;
        let status = 'ongoing';
        let statusText = '进行中';
        if (deadline && deadline < now) {
            status = 'ended';
            statusText = '已结束';
        }

        task.value = {
            id: res.id,
            title: res.title,
            status: status,
            statusText: statusText,
            dueDate: res.deadline ? res.deadline.replace('T', ' ') : '无限制',
            requirements: reqs,
            completedCount: res.completed_count,
            totalCount: res.total_students
        };

        // Map Students
        students.value = res.student_statuses.map(s => ({
            id: s.student_id,
            name: s.student_name,
            studentId: `ID:${s.student_id}`, // Mock student ID if not available
            status: s.status === 'completed' ? 'completed' : 'uncompleted',
            statusText: s.status === 'completed' ? '已完成' : '未完成',
            metricValue: s.metric_value,
            avatar: ''
        }));

    } catch (e) {
        console.error(e);
        uni.showToast({ title: '加载失败', icon: 'none' });
    } finally {
        loading.value = false;
    }
};

onLoad((options) => {
    if (options.id) {
        taskId.value = options.id;
        fetchTaskDetail();
    }
});
</script>

<style lang="scss">
.container {
  padding: 20rpx;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.card-base {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.header-card {
  @extend .card-base;
  
  .title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16rpx;
    
    .task-title {
      font-size: 36rpx;
      font-weight: bold;
      color: #333;
    }
    
    .status-tag {
      padding: 6rpx 16rpx;
      border-radius: 8rpx;
      font-size: 24rpx;
      
      &.ongoing {
        background: #e6f7ff;
        color: #1890ff;
      }
      &.ended {
        background: #f5f5f5;
        color: #999;
      }
    }
  }
  
  .due-date {
    font-size: 26rpx;
    color: #666;
  }
}

.section-card {
  @extend .card-base;
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24rpx;
    
    .section-title {
      font-size: 30rpx;
      font-weight: 600;
      color: #333;
      position: relative;
      padding-left: 20rpx;
      
      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 6rpx;
        height: 28rpx;
        background: #20C997;
        border-radius: 3rpx;
      }
    }
    
    .progress-stats {
      font-size: 28rpx;
      color: #666;
    }
  }
}

.requirements-list {
  .req-item {
    display: flex;
    margin-bottom: 12rpx;
    
    .dot {
      color: #20C997;
      margin-right: 12rpx;
    }
    
    .req-text {
      font-size: 28rpx;
      color: #555;
      line-height: 1.5;
    }
  }
}

.progress-box {
  .progress-bar {
    height: 16rpx;
    background: #f0f0f0;
    border-radius: 8rpx;
    overflow: hidden;
    margin-bottom: 12rpx;
    
    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #20C997, #17a2b8);
      border-radius: 8rpx;
      transition: width 0.3s ease;
    }
  }
  
  .percentage-text {
    font-size: 24rpx;
    color: #999;
    display: block;
    text-align: right;
  }
}

.filter-tabs {
  display: flex;
  background: #f5f5f5;
  border-radius: 8rpx;
  padding: 4rpx;
  
  .tab-item {
    padding: 6rpx 20rpx;
    font-size: 24rpx;
    color: #666;
    border-radius: 6rpx;
    
    &.active {
      background: #fff;
      color: #20C997;
      font-weight: 500;
      box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.05);
    }
  }
}

.student-list {
  max-height: 600rpx;
  
  .student-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx 0;
    border-bottom: 1px solid #f0f0f0;
    
    &:last-child {
      border-bottom: none;
    }
    
    .student-info {
      display: flex;
      align-items: center;
      
      .avatar {
        width: 80rpx;
        height: 80rpx;
        border-radius: 50%;
        background: #eee;
        margin-right: 20rpx;
      }
      
      .info-col {
        display: flex;
        flex-direction: column;
        
        .name {
          font-size: 28rpx;
          color: #333;
          font-weight: 500;
        }
        
        .id {
          font-size: 24rpx;
          color: #999;
        }

        .metric-val {
          font-size: 24rpx;
          color: #20C997;
          margin-top: 4rpx;
        }
      }
    }
    
    .status-col {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      
      .status-text {
        font-size: 26rpx;
        margin-bottom: 8rpx;
        
        &.completed {
          color: #20C997;
        }
        &.uncompleted {
          color: #ff4d4f;
        }
      }
      
      .remind-btn {
        margin: 0;
        padding: 0 20rpx;
        height: 48rpx;
        line-height: 48rpx;
        font-size: 24rpx;
        background: #fff;
        color: #ff4d4f;
        border: 1px solid #ff4d4f;
        
        &:active {
          background: #fff1f0;
        }
      }
    }
  }
}
</style>
