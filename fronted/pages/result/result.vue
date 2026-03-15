<template>
  <view class="result-page">
    <!-- 顶部模式标题 -->
    <view class="mode-header" :style="{backgroundColor: modeBgColor}">
      <text class="mode-title">{{modeTitle}}</text>
    </view>

    <!-- 核心数据卡片 -->
    <view class="result-card">
      <!-- 体能测试模式：不显示通用的运动时长/距离，而是显示项目专属数据 -->
      <view class="base-data" v-if="currentMode === 'test'">
        <text class="base-title">测试项目：{{ testProject }}</text>
        <view class="data-item">
          <text class="item-label">完成数量</text>
          <text class="item-value count-text">{{ testCount }} 次</text>
        </view>
        <view class="data-item">
          <text class="item-label">测试用时</text>
          <text class="item-value">{{ formatDuration(duration) }}</text>
        </view>
        <view class="data-item">
          <text class="item-label">动作判定</text>
          <text class="item-value" :class="testQualified ? 'success' : 'fail'">{{ testQualified ? '✅ 合格' : '❌ 未合格' }}</text>
        </view>
      </view>

      <!-- Test Mode Analysis Section -->
      <view class="mode-data" v-if="currentMode === 'test'">
        <text class="mode-data-title">成绩分析</text>
        <view class="bar-chart">
          <view class="bar-row">
            <text class="bar-label">我的</text>
            <view class="bar-track">
              <view class="bar-fill user-fill" :style="{width: userScorePercent + '%'}"></view>
              <text class="bar-val-in" v-if="userScorePercent > 15">{{testCount}}</text>
            </view>
            <text class="bar-val-out" v-if="userScorePercent <= 15">{{testCount}}</text>
          </view>
          <view class="bar-row">
            <text class="bar-label">合格</text>
            <view class="bar-track">
              <view class="bar-fill standard-fill" :style="{width: standardScorePercent + '%'}"></view>
              <text class="bar-val-in" v-if="standardScorePercent > 15">{{standardReq}}</text>
            </view>
            <text class="bar-val-out" v-if="standardScorePercent <= 15">{{standardReq}}</text>
          </view>
        </view>
        
        <view class="suggestion-box">
          <text class="sugg-title">💡 智能反馈</text>
          <text class="sugg-text">{{suggestionText}}</text>
        </view>
      </view>

      <!-- 通用基础数据（非测试模式显示） -->
      <view class="base-data" v-else>
        <text class="base-title">运动基础数据</text>
        <view class="data-item">
          <text class="item-label">运动时长</text>
          <text class="item-value">{{formatDuration(duration)}}</text>
        </view>
        <view class="data-item">
          <text class="item-label">运动距离</text>
          <text class="item-value">{{(distance/1000).toFixed(2)}} 公里</text>
        </view>
      </view>

      <!-- 模式专属数据 -->
      <view class="mode-data" v-if="currentMode === 'police'">
        <text class="mode-data-title">专项体能测试数据</text>
        <!-- 2000米完成状态 -->
        <view class="data-item">
          <text class="item-label">2000米目标完成</text>
          <text class="item-value" :class="isPoliceFinish ? 'success' : 'fail'">
            {{isPoliceFinish ? '✅ 已完成' : '❌ 未完成'}}
          </text>
        </view>
        <!-- 配速达标状态 -->
        <view class="data-item">
          <text class="item-label">配速是否达标</text>
          <text class="item-value" :class="isPaceQualified ? 'success' : 'fail'">
            {{isPaceQualified ? `✅ 达标（${policePace.toFixed(1)} 分/公里）` : `❌ 未达标（${policePace.toFixed(1)} 分/公里）`}}
          </text>
        </view>
        <!-- 考核标准参考 -->
        <view class="data-item tips">
          <text class="item-label">参考标准</text>
          <text class="item-value">可根据学校或课程体测标准配置</text>
        </view>
      </view>

      <view class="mode-data" v-if="currentMode === 'campus'">
        <text class="mode-data-title">校园打卡数据</text>
        <view class="data-item">
          <text class="item-label">打卡点到达状态</text>
          <text class="item-value" :class="isReach ? 'success' : 'fail'">
            {{isReach ? '✅ 已到达' : '❌ 未到达'}}
          </text>
        </view>
      </view>

      <view class="mode-data" v-if="currentMode === 'normal'">
        <text class="mode-data-title">普通跑步数据</text>
        <view class="data-item tips">
          <text class="item-label">温馨提示</text>
          <text class="item-value">数据已自动记录，可在「我的」页面查看汇总</text>
        </view>
      </view>

      <!-- 核验结果 -->
      <view class="verify-section" v-if="isValid !== null">
        <text class="verify-title">核验结果</text>
        <view class="verify-row" v-if="isValid">
          <text class="verify-icon success">✅</text>
          <text class="verify-text success">本次运动有效，已计入成绩！</text>
        </view>
        <view class="verify-row" v-else>
          <text class="verify-icon fail">⚠️</text>
          <text class="verify-text fail">
            本次运动无效：{{ failReason || '原因未知，请联系老师查看详情' }}
          </text>
        </view>
      </view>
    </view>

    <!-- 操作按钮区 -->
    <view class="btn-group">
      <button class="save-btn" disabled>
        ✅ 数据已保存
      </button>
      <button @click="backToHome" class="back-btn">返回首页</button>
    </view>

    <!-- 今日目标提醒 -->
    <view class="today-tip" v-if="todayCompleted !== null">
      <text v-if="todayCompleted" class="today-success">
        ✅ 今日阳光跑目标已达成，明天继续加油！
      </text>
      <text v-else class="today-fail">
        ❌ 今日尚未达成有效运动目标，请重新开始。
      </text>
    </view>
  </view>
</template>

<script setup>
// 统一导入规范
import { ref, computed} from 'vue';
import { onShow, onLoad  } from '@dcloudio/uni-app';

// 1. 接收跑步页传递的参数
const currentMode = ref('normal'); // normal/police/campus
const duration = ref(0); // 运动时长（秒）
const distance = ref(0); // 运动距离（米）
const isReach = ref(false); // 校园打卡是否到达
const isPoliceFinish = ref(false); // 警务2000米是否完成
const policePace = ref(0); // 警务配速（分/公里）
const isValid = ref(null); // 本次运动是否有效（后端判定）
const failReason = ref(''); // 无效原因
const todayCompleted = ref(null); // 今日是否已完成目标
// 测试模式专属
const testProject = ref('');
const testType = ref('');
const testCount = ref(0);
const testQualified = ref(false);
const standardReq = ref(0);
const userScorePercent = ref(0);
const standardScorePercent = ref(0);
const suggestionText = ref('');

// 3. 计算属性：动态标题和背景色
const modeTitle = computed(() => {
  switch (currentMode.value) {
    case 'police': return '🎯 2000米专项体能结算';
    case 'campus': return '🏫 校园打卡跑步结算';
    case 'test': return '💪 体能测试结算';
    default: return '🏃 普通跑步结算';
  }
});
const modeBgColor = computed(() => {
  switch (currentMode.value) {
    case 'police': return '#fdf2f0';
    case 'campus': return '#e8f4f8';
    case 'test': return '#f3f7ff';
    default: return '#f5f5f5';
  }
});
// 警务配速是否达标（男生6.5，女生7.5，这里默认按男生标准）
const isPaceQualified = computed(() => {
  return policePace.value <= 6.5;
});

// 4. 页面加载时接收参数
onLoad((options) => {
  let data = null;
  
  if (options.useStorage === 'true') {
    data = uni.getStorageSync('tempRunResult');
    // Clear storage after reading (optional, keep for debugging if needed)
    // uni.removeStorageSync('tempRunResult');
  } else if (options.data) {
    try {
      data = JSON.parse(decodeURIComponent(options.data));
    } catch (e) {
      console.error('Failed to parse result data', e);
    }
  }

  if (data) {
      // Map backend data to frontend display
      currentMode.value = data.type === 'test' ? 'test' : 'normal'; // Simplify for MVP
      if (data.metrics) {
        duration.value = data.metrics.duration || 0;
        distance.value = (data.metrics.distance || 0) * 1000;
        testCount.value = data.metrics.count || 0;
        testQualified.value = data.metrics.qualified;
        policePace.value = Number(data.metrics.pace) || 0;
      }

      if (typeof data.is_valid !== 'undefined') {
        isValid.value = data.is_valid;
      }
      if (typeof data.fail_reason !== 'undefined') {
        failReason.value = data.fail_reason || '';
      }
      if (typeof data.today_completed !== 'undefined') {
        todayCompleted.value = data.today_completed;
      }
      
      // Additional logic for test mode visualization (simplified)
      if (currentMode.value === 'test') {
        testProject.value = '体测项目'; // Since we don't track specific project name in backend yet, generic
        testQualified.value = data.metrics.qualified;
        if (testQualified.value) {
          suggestionText.value = '恭喜达标！';
        } else {
          suggestionText.value = '继续加油！';
        }
      }
  } else {
    // Fallback to legacy query params
    // Fallback to legacy query params
    currentMode.value = options.mode || 'normal';
    duration.value = Number(options.duration) || 0;
    distance.value = Number(options.distance) || 0;
    isReach.value = options.isReach === 'true';
    isPoliceFinish.value = options.isPoliceFinish === 'true';
    policePace.value = Number(options.policePace) || 0;
  }
});

// 5. 格式化时长（秒 → 分:秒）
const formatDuration = (seconds) => {
  const min = Math.floor(seconds / 60);
  const sec = seconds % 60;
  return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
};

// 7. 返回首页
const backToHome = () => {
  uni.reLaunch({ url: '/pages/tab/home' });
};
</script>

<style scoped>
.result-page {
  min-height: 100vh;
  background-color: #fff;
}

/* 顶部模式标题栏 */
.mode-header {
  padding: 30rpx 20rpx;
  text-align: center;
  border-bottom: 1px solid #eee;
}
.mode-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

/* 核心数据卡片 */
.result-card {
  margin: 20rpx;
  padding: 30rpx;
  background-color: #fafafa;
  border-radius: 16rpx;
}
/* 基础数据模块 */
.base-data {
  margin-bottom: 30rpx;
  padding-bottom: 20rpx;
  border-bottom: 1px dashed #ddd;
}
.base-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}
/* 数据项通用样式 */
.data-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15rpx 0;
  font-size: 30rpx;
}
.item-label {
  color: #666;
  font-size: 28rpx;
}
.item-value {
  font-weight: bold;
  color: #333;
  font-size: 28rpx;
}
.count-text {
  font-size: 40rpx;
  color: #20C997;
}

/* 模式专属数据模块 */
.mode-data {
  margin-top: 20rpx;
}
.mode-data-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #444;
  margin-bottom: 15rpx;
  display: block;
}
/* 状态样式 */
.success {
  color: #20C997 !important;
}
.fail {
  color: #d81e06 !important;
}
.tips .item-value {
  font-weight: normal;
  color: #888;
  font-size: 26rpx;
}

/* 图表与建议 */
.bar-chart {
  margin: 20rpx 0;
}
.bar-row {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}
.bar-label {
  width: 80rpx;
  font-size: 26rpx;
  color: #666;
}
.bar-track {
  flex: 1;
  height: 40rpx;
  background: #f0f0f0;
  border-radius: 20rpx;
  overflow: hidden;
  position: relative;
  margin-right: 10rpx;
}
.bar-fill {
  height: 100%;
  border-radius: 20rpx;
}
.user-fill { background: #20C997; }
.standard-fill { background: #ddd; }

.bar-val-in {
  position: absolute;
  right: 10rpx;
  top: 0;
  line-height: 40rpx;
  font-size: 22rpx;
  color: #fff;
}
.bar-val-out {
  font-size: 26rpx;
  color: #333;
}

.suggestion-box {
  background: #eefbf7;
  padding: 20rpx;
  border-radius: 12rpx;
  margin-top: 20rpx;
  border: 1px solid #d2f4e8;
}
.sugg-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #17a077;
  display: block;
  margin-bottom: 8rpx;
}
.sugg-text {
  font-size: 26rpx;
  color: #555;
  line-height: 1.4;
}

/* 操作按钮区 */
.btn-group {
  margin: 20rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}
.save-btn {
  height: 80rpx;
  line-height: 80rpx;
  background-color: #20C997;
  color: #fff;
  border: none;
  border-radius: 12rpx;
  font-size: 32rpx;
}
.save-btn:disabled {
  background-color: #95e1c8;
  color: #fff;
}
.back-btn {
  height: 80rpx;
  line-height: 80rpx;
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #eee;
  border-radius: 12rpx;
  font-size: 32rpx;
}
</style>
