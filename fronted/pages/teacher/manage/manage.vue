<template>
  <view class="manage-container">
    <!-- 自定义导航栏 -->
    <view class="custom-nav-bar">
      <view class="nav-status-bar"></view>
      <view class="nav-content">
        <text class="nav-title">综合管理</text>
      </view>
    </view>

    <view class="content-wrapper">
      <view class="grid-container">
        <!-- 模块迁移：学员管理（包含原班级管理的排课、考勤） -->
        <view class="grid-item" @click="navTo('/pages/teacher/students/students')">
          <view class="icon-box purple">👥</view>
          <text class="grid-label">学员管理</text>
          <text class="grid-desc">分组、档案、排课、考勤</text>
        </view>

        <!-- 任务管理 -->
        <view class="grid-item" @click="navTo('/pages/teacher/tasks/tasks')">
          <view class="icon-box green">📢</view>
          <text class="grid-label">任务管理</text>
          <text class="grid-desc">发布、审批</text>
        </view>

        <!-- 功能打通：异常处理 -->
        <view class="grid-item" @click="navTo('/pages/teacher/exceptions/exceptions')">
          <view class="icon-box orange">⚠️</view>
          <text class="grid-label">异常处理</text>
          <text class="grid-desc">运动异常、防作弊</text>
        </view>

        <!-- 教学资源 -->
        <view class="grid-item" @click="navTo('/pages/teacher/resources/resources')">
          <view class="icon-box pink">📚</view>
          <text class="grid-label">教学资源</text>
          <text class="grid-desc">课件、视频</text>
        </view>

        <!-- 数据导出 -->
        <view class="grid-item" @click="handleDataExport">
          <view class="icon-box indigo">📥</view>
          <text class="grid-label">数据导出</text>
          <text class="grid-desc">成绩、任务完成情况</text>
        </view>
        
        <!-- 测试监控 -->
        <view class="grid-item" @click="navTo('/pages/teacher/tests/tests')">
          <view class="icon-box teal">📊</view>
          <text class="grid-label">测试监控</text>
          <text class="grid-desc">数据分析、历史回顾</text>
        </view>
      </view>
    
      <!-- 数据概览 -->
      <view class="stats-card">
        <view class="card-header">
          <text class="card-title">数据概览</text>
        </view>
        <view class="stats-row">
          <view class="stat-item">
            <text class="stat-val">{{ stats.studentCount }}</text>
            <text class="stat-label">总学员</text>
          </view>
          <view class="stat-item">
            <text class="stat-val">{{ stats.complianceRate }}%</text>
            <text class="stat-label">达标率</text>
          </view>
          <view class="stat-item">
            <text class="stat-val">{{ stats.taskCount }}</text>
            <text class="stat-label">进行中任务</text>
          </view>
        </view>
      </view>
    
      <view style="height: 20rpx;"></view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { request } from '@/utils/request.js';

const stats = ref({
  studentCount: 0,
  complianceRate: 0,
  taskCount: 0
});

const loadStats = async () => {
  try {
    const res = await request({
      url: '/teacher/stats',
      method: 'GET'
    });
    stats.value = {
      studentCount: res.student_count,
      complianceRate: res.qualified_rate,
      taskCount: res.task_count
    };
  } catch (e) {
    console.error('Failed to load stats:', e);
  }
};

onShow(() => {
  uni.hideHomeButton && uni.hideHomeButton();
  loadStats();
});

const navTo = (url) => {
  uni.navigateTo({ url });
};

// 功能开发：数据导出
const handleDataExport = () => {
  uni.showActionSheet({
    itemList: ['导出学生成绩', '导出任务完成情况', '导出学生信息'],
    success: async (res) => {
      if (res.tapIndex === 0) {
        // 导出学生成绩
        await exportScores();
      } else if (res.tapIndex === 1) {
        // 导出任务完成情况
        await exportTasks();
      } else if (res.tapIndex === 2) {
        // 导出学生信息
        uni.showToast({ title: '学生信息导出功能开发中', icon: 'none' });
      }
    }
  });
};

// 导出学生成绩
const exportScores = async () => {
  uni.showLoading({ title: '正在导出...' });
  try {
    const res = await request({
      url: '/teacher/export/scores',
      method: 'GET'
    });
    
    if (res.data && res.data.length > 0) {
      // 生成CSV内容
      const headers = ['学号', '学生姓名', '班级', '平均分', '最高分', '最低分', '打分次数'];
      const csvContent = [
        headers.join(','),
        ...res.data.map(item => [
          item.student_id,
          item.student_name,
          item.class_name || '未分班',
          item.avg_score,
          item.max_score,
          item.min_score,
          item.score_count
        ].join(','))
      ].join('\n');
      
      // 显示导出结果
      uni.hideLoading();
      uni.showModal({
        title: '导出成功',
        content: `已导出 ${res.data.length} 条成绩记录\n\n数据预览：\n${res.data.slice(0, 3).map(d => `${d.student_name}: 平均${d.avg_score}分`).join('\n')}`,
        confirmText: '我知道了'
      });
      
      // TODO: 在实际应用中，这里应该触发文件下载
      console.log('CSV Content:', csvContent);
    } else {
      uni.hideLoading();
      uni.showToast({ title: '暂无数据可导出', icon: 'none' });
    }
  } catch (e) {
    uni.hideLoading();
    console.error('Export scores failed:', e);
    uni.showToast({ title: '导出失败', icon: 'none' });
  }
};

// 导出任务完成情况
const exportTasks = async () => {
  uni.showLoading({ title: '正在导出...' });
  try {
    const res = await request({
      url: '/teacher/export/tasks',
      method: 'GET'
    });
    
    if (res.data && res.data.length > 0) {
      // 生成CSV内容
      const headers = ['任务ID', '任务标题', '任务类型', '开始时间', '结束时间', '目标学生数', '已完成人数', '完成率'];
      const csvContent = [
        headers.join(','),
        ...res.data.map(item => [
          item.task_id,
          item.task_title,
          item.task_type,
          item.start_time,
          item.end_time,
          item.total_students,
          item.completed_count,
          item.completion_rate + '%'
        ].join(','))
      ].join('\n');
      
      // 显示导出结果
      uni.hideLoading();
      uni.showModal({
        title: '导出成功',
        content: `已导出 ${res.data.length} 个任务记录\n\n数据预览：\n${res.data.slice(0, 3).map(d => `${d.task_title}: ${d.completion_rate}%完成`).join('\n')}`,
        confirmText: '我知道了'
      });
      
      // TODO: 在实际应用中，这里应该触发文件下载
      console.log('CSV Content:', csvContent);
    } else {
      uni.hideLoading();
      uni.showToast({ title: '暂无数据可导出', icon: 'none' });
    }
  } catch (e) {
    uni.hideLoading();
    console.error('Export tasks failed:', e);
    uni.showToast({ title: '导出失败', icon: 'none' });
  }
};

const showToast = (title) => {
  uni.showToast({
    title: `${title}功能开发中`,
    icon: 'none'
  });
};
</script>

<style scoped>
.manage-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

/* 自定义导航栏 */
.custom-nav-bar {
  background: #fff;
  width: 100%;
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid #eee;
}
.nav-status-bar {
  height: var(--status-bar-height);
  width: 100%;
}
.nav-content {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.nav-title {
  color: #333;
  font-size: 32rpx;
  font-weight: bold;
}

.content-wrapper {
  padding: 30rpx;
  flex: 1;
}

.grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30rpx;
  margin-bottom: 40rpx;
}
.grid-item {
  background: #fff;
  padding: 40rpx 30rpx;
  border-radius: 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.03);
  transition: transform 0.2s ease;
}
.grid-item:active {
  transform: scale(0.98);
}
.icon-box {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
  margin-bottom: 20rpx;
}
.purple { background: #f3e5f5; color: #9c27b0; }
.green { background: #e8f5e9; color: #4caf50; }
.blue { background: #e3f2fd; color: #2196f3; }
.orange { background: #fff3e0; color: #ff9800; }
.cyan { background: #e0f7fa; color: #00bcd4; }
.pink { background: #fce4ec; color: #e91e63; }
.indigo { background: #e8eaf6; color: #3f51b5; }
.teal { background: #e0f2f1; color: #009688; }
.red { background: #ffebee; color: #f44336; }

.grid-label {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 8rpx;
}
.grid-desc {
  font-size: 24rpx;
  color: #999;
  text-align: center;
}

.stats-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}
.card-header {
  margin-bottom: 30rpx;
  padding-bottom: 20rpx;
  border-bottom: 1px solid #f5f5f5;
}
.card-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}
.stats-row {
  display: flex;
  justify-content: space-around;
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.stat-val {
  font-size: 40rpx;
  font-weight: bold;
  color: #20C997;
  margin-bottom: 10rpx;
}
.stat-label {
  font-size: 24rpx;
  color: #666;
}
</style>
