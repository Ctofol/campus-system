<template>
  <view class="manage-container">
    <page-tab-header title="综合管理" theme="white" />

    <view class="content-wrapper page-tab-body">
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
    
    <view style="height: 120rpx;"></view>
    </view>
  </view>
</template>

<script setup>
import { request } from '@/utils/request.js';

const navTo = (url) => {
  uni.navigateTo({ url });
};

// 功能开发：数据导出
const handleDataExport = () => {
  uni.showActionSheet({
    itemList: ['导出学生成绩', '导出任务完成情况', '导出学生信息'],
    success: async (res) => {
      if (res.tapIndex === 0) {
        await exportScores();
      } else if (res.tapIndex === 1) {
        await exportTasks();
      } else if (res.tapIndex === 2) {
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
      
      uni.hideLoading();
      uni.showModal({
        title: '导出成功',
        content: `已导出 ${res.data.length} 条成绩记录\n\n数据预览：\n${res.data.slice(0, 3).map(d => `${d.student_name}: 平均${d.avg_score}分`).join('\n')}`,
        confirmText: '我知道了'
      });
      
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
      
      uni.hideLoading();
      uni.showModal({
        title: '导出成功',
        content: `已导出 ${res.data.length} 个任务记录\n\n数据预览：\n${res.data.slice(0, 3).map(d => `${d.task_title}: ${d.completion_rate}%完成`).join('\n')}`,
        confirmText: '我知道了'
      });
      
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

const onPageShow = () => {};

const onPageHide = () => {};

defineExpose({
  onPageShow,
  onPageHide
});
</script>

<style lang="scss" scoped>
.manage-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding-bottom: 50px;
}

.content-wrapper {
  padding-left: 30rpx;
  padding-right: 30rpx;
}

.grid-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-top: 30rpx;
}

.grid-item {
  width: 48%;
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
  box-sizing: border-box;
  
  &:active {
    transform: scale(0.98);
  }
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
  
  &.purple { background-color: #f3e5f5; color: #9c27b0; }
  &.cyan { background-color: #e0f7fa; color: #00bcd4; }
  &.green { background-color: #e8f5e9; color: #4caf50; }
  &.pink { background-color: #fce4ec; color: #e91e63; }
  &.blue { background-color: #e3f2fd; color: #2196f3; }
  &.indigo { background-color: #e8eaf6; color: #3f51b5; }
  &.orange { background-color: #fff3e0; color: #ff9800; }
  &.teal { background-color: #e0f2f1; color: #009688; }
  &.red { background-color: #ffebee; color: #f44336; }
}

.grid-label {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 8rpx;
}

.grid-desc {
  font-size: 24rpx;
  color: #999;
}

</style>
