<template>
  <view class="manage-container">
    <page-tab-header title="综合管理" theme="white" />

    <view class="content-wrapper page-tab-body">
      <view class="grid-container">
        <!-- 模块迁移：学员管理（包含原班级管理的排课、考勤） -->
        <view class="grid-item" @click="navTo('/pages/teacher/students/students')">
          <view class="icon-box"><image class="grid-icon-img" src="/static/icons/teacher-student-manage.svg" mode="aspectFit" /></view>
          <text class="grid-label">学员管理</text>
          <text class="grid-desc">分组、档案、排课、考勤</text>
        </view>

        <!-- 任务管理 -->
        <view class="grid-item" @click="navTo('/pages/teacher/tasks/tasks')">
          <view class="icon-box"><image class="grid-icon-img" src="/static/icons/teacher-home-task.svg" mode="aspectFit" /></view>
          <text class="grid-label">任务管理</text>
          <text class="grid-desc">发布、审批</text>
        </view>

        <!-- 常态化活动安排 -->
        <view class="grid-item" @click="navTo('/pages/teacher/sunshine/manage')">
          <view class="icon-box"><image class="grid-icon-img" src="/static/icons/teacher-activity-schedule.svg" mode="aspectFit" /></view>
          <text class="grid-label">常态活动</text>
          <text class="grid-desc">规则、频次、距离</text>
        </view>

        <!-- 功能打通：异常处理 -->
        <view class="grid-item" @click="navTo('/pages/teacher/exceptions/exceptions')">
          <view class="icon-box"><image class="grid-icon-img" src="/static/icons/teacher-pending-alert.svg" mode="aspectFit" /></view>
          <text class="grid-label">异常处理</text>
          <text class="grid-desc">运动异常、防作弊</text>
        </view>

        <!-- 教学资源 -->
        <view class="grid-item" @click="navTo('/pages/teacher/resources/resources')">
          <view class="icon-box"><image class="grid-icon-img" src="/static/icons/teacher-resource.svg" mode="aspectFit" /></view>
          <text class="grid-label">教学资源</text>
          <text class="grid-desc">课件、视频</text>
        </view>

        <!-- 数据导出 -->
        <view class="grid-item" @click="handleDataExport">
          <view class="icon-box"><image class="grid-icon-img" src="/static/icons/teacher-data-stats.svg" mode="aspectFit" /></view>
          <text class="grid-label">数据导出</text>
          <text class="grid-desc">成绩、任务完成情况</text>
        </view>

        <!-- 数据监控 -->
        <view class="grid-item" @click="navTo('/pages/teacher/tests/tests')">
          <view class="icon-box"><image class="grid-icon-img" src="/static/icons/teacher-data-monitor.svg" mode="aspectFit" /></view>
          <text class="grid-label">数据监控</text>
          <text class="grid-desc">数据分析、历史回顾</text>
        </view>

        <!-- 通知中心 -->
        <view class="grid-item" @click="navTo('/pages/teacher/notifications/list')">
          <view class="icon-box"><image class="grid-icon-img" src="/static/icons/teacher-notification-center.svg" mode="aspectFit" /></view>
          <text class="grid-label">通知中心</text>
          <text class="grid-desc">系统、任务、互动消息</text>
        </view>
      </view>

      <view style="height: 20rpx;"></view>
    </view>
  </view>
</template>

<script setup>
import { onShow } from '@dcloudio/uni-app';
import { request, BASE_URL } from '@/utils/request.js';

onShow(() => {
  uni.hideHomeButton && uni.hideHomeButton();
});

const navTo = (url) => {
  uni.navigateTo({ url });
};

// 功能开发：数据导出
const handleDataExport = () => {
  uni.showActionSheet({
    itemList: ['导出学生成绩', '导出任务完成情况', '导出学生信息'],
    success: async (res) => {
      if (res.tapIndex === 0) await exportScores();
      else if (res.tapIndex === 1) await exportTasks();
      else if (res.tapIndex === 2) await exportStudents();
    }
  });
};

const downloadCsvFile = (csvContent, filename) => {
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

const saveCsvFile = (csvContent, filename, onSuccess) => {
  // #ifdef H5
  downloadCsvFile(csvContent, filename);
  if (onSuccess) onSuccess();
  // #endif

  // #ifndef H5
  const fs = uni.getFileSystemManager();
  const tempPath = `${uni.env.USER_DATA_PATH}/${filename}`;
  fs.writeFile({
    filePath: tempPath,
    data: '\uFEFF' + csvContent,
    encoding: 'utf8',
    success: () => {
      uni.openDocument({
        filePath: tempPath,
        showMenu: true,
        success: () => {
          if (onSuccess) onSuccess();
        },
        fail: () => {
          uni.setClipboardData({
            data: csvContent,
            success: () => {
              uni.showToast({ title: '已复制到剪贴板', icon: 'success' });
              if (onSuccess) onSuccess();
            }
          });
        }
      });
    },
    fail: () => {
      uni.setClipboardData({
        data: csvContent,
        success: () => {
          uni.showToast({ title: '已复制到剪贴板', icon: 'success' });
          if (onSuccess) onSuccess();
        }
      });
    }
  });
  // #endif
};

// 导出学生成绩
const exportScores = async () => {
  uni.showLoading({ title: '正在导出...' });
  try {
    const res = await request({ url: '/teacher/export/scores', method: 'GET' });
    if (res.data && res.data.length > 0) {
      const headers = ['学号', '学生姓名', '班级', '平均分', '最高分', '最低分', '打分次数'];
      const rows = res.data.map(item => [
        item.student_id, item.student_name, item.class_name || '未分班',
        item.avg_score, item.max_score, item.min_score, item.score_count
      ].join(','));
      const csvContent = [headers.join(','), ...rows].join('\n');
      uni.hideLoading();
      saveCsvFile(csvContent, `学生成绩_${formatDate()}.csv`, () => {
        uni.showToast({ title: `已导出${res.data.length}条`, icon: 'success' });
      });
    } else {
      uni.hideLoading();
      uni.showToast({ title: '暂无数据可导出', icon: 'none' });
    }
  } catch (e) {
    uni.hideLoading();
    uni.showToast({ title: '导出失败', icon: 'none' });
  }
};

// 导出任务完成情况
const exportTasks = async () => {
  uni.showLoading({ title: '正在导出...' });
  try {
    const res = await request({ url: '/teacher/export/tasks', method: 'GET' });
    if (res.data && res.data.length > 0) {
      const headers = ['任务ID', '任务标题', '任务类型', '开始时间', '结束时间', '目标学生数', '已完成人数', '完成率'];
      const rows = res.data.map(item => [
        item.task_id, item.task_title, item.task_type,
        item.start_time, item.end_time, item.total_students,
        item.completed_count, `${item.completion_rate}%`
      ].join(','));
      const csvContent = [headers.join(','), ...rows].join('\n');
      uni.hideLoading();
      saveCsvFile(csvContent, `任务完成情况_${formatDate()}.csv`, () => {
        uni.showToast({ title: `已导出${res.data.length}条`, icon: 'success' });
      });
    } else {
      uni.hideLoading();
      uni.showToast({ title: '暂无数据可导出', icon: 'none' });
    }
  } catch (e) {
    uni.hideLoading();
    uni.showToast({ title: '导出失败', icon: 'none' });
  }
};

// 导出学生信息（对接已有的 CSV 导出接口）
const exportStudents = async () => {
  uni.showLoading({ title: '正在导出...' });
  try {
    const token = uni.getStorageSync('token');
    const res = await new Promise((resolve, reject) => {
      uni.request({
        url: `${BASE_URL}/teacher/students/export`,
        method: 'POST',
        header: { 'Authorization': `Bearer ${token}` },
        data: {},
        responseType: 'text',
        success: (r) => resolve(r.data),
        fail: reject
      });
    });
    uni.hideLoading();
    if (res && typeof res === 'string' && res.trim().length > 0) {
      saveCsvFile(res, `学生信息_${formatDate()}.csv`, () => {
        uni.showToast({ title: '已导出', icon: 'success' });
      });
    } else {
      uni.showToast({ title: '暂无数据可导出', icon: 'none' });
    }
  } catch (e) {
    uni.hideLoading();
    uni.showToast({ title: '导出失败', icon: 'none' });
  }
};

const formatDate = () => {
  const d = new Date();
  return `${d.getFullYear()}${String(d.getMonth()+1).padStart(2,'0')}${String(d.getDate()).padStart(2,'0')}`;
};
</script>

<style scoped>
.manage-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
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
  border-radius: 22rpx;
  background: #F4FAF8;
  border: 1rpx solid rgba(36, 191, 162, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
  margin-bottom: 20rpx;
}
.grid-icon-img { width: 48rpx; height: 48rpx; }
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

</style>
