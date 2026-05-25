<template>
  <view class="result-page">
    <!-- 顶部模式标题 -->
    <view class="mode-header" :style="{backgroundColor: modeBgColor}">
      <text class="mode-title">{{modeTitle}}</text>
    </view>

    <!-- 轨迹地图（仅跑步模式显示） -->
    <view class="map-section" v-if="currentMode !== 'test' && (trajectoryPoints.length >= 1 || mapCenterLat !== 0)">
      <map
        class="result-map"
        :latitude="mapCenterLat"
        :longitude="mapCenterLng"
        :polyline="mapPolyline"
        :markers="mapMarkers"
        :enable-zoom="true"
        :enable-scroll="true"
        scale="15"
        :show-location="false"
      />
      <view class="map-label">
        <text class="map-label-text">{{ trajectoryPoints.length >= 2 ? '📍 本次跑步轨迹' : '📍 起跑位置' }}</text>
      </view>
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
        <view class="data-item" v-if="campusCheckpointName">
          <text class="item-label">目标打卡点</text>
          <text class="item-value">{{ campusCheckpointName }}</text>
        </view>
        <view class="data-item">
          <text class="item-label">打卡点到达状态</text>
          <text class="item-value" :class="isReach ? 'success' : 'fail'">
            {{isReach ? '✅ 已到达' : '❌ 未到达'}}
          </text>
        </view>
        <view class="data-item tips" v-if="!isReach">
          <text class="item-label">说明</text>
          <text class="item-value">需在打卡点半径内完成跑步；GPS 弱或距离过短会导致未到达</text>
        </view>
      </view>

      <view class="mode-data" v-if="currentMode === 'normal'">
        <text class="mode-data-title">普通跑步数据</text>
        <view class="data-item tips">
          <text class="item-label">温馨提示</text>
          <text class="item-value">数据已自动记录，可在「我的」页面查看汇总</text>
        </view>
      </view>

      <!-- 任务完成结果 -->
      <view class="verify-section" v-if="isTaskRun && taskCompleted !== null">
        <text class="verify-title">任务是否完成</text>
        <view class="verify-row" v-if="taskCompleted">
          <text class="verify-icon success">✅</text>
          <text class="verify-text success">已满足任务要求（{{ taskTitle || '本次任务' }}）</text>
        </view>
        <view class="verify-row" v-else>
          <text class="verify-icon fail">⚠️</text>
          <text class="verify-text fail">未满足任务要求：{{ failReason || '请查看距离/时长是否达标' }}</text>
        </view>
      </view>

      <!-- 校园打卡：单独说明，不与阳光跑里程规则混用 -->
      <view class="verify-section" v-if="currentMode === 'campus'">
        <text class="verify-title">打卡结果</text>
        <view class="verify-row" v-if="isReach">
          <text class="verify-icon success">✅</text>
          <text class="verify-text success">已成功到达打卡点，本次打卡记录已保存。</text>
        </view>
        <view class="verify-row" v-else>
          <text class="verify-icon fail">⚠️</text>
          <text class="verify-text fail">
            未在打卡点有效范围内完成。请确认已选打卡点，并在室外开阔处跑至点附近再结束。
          </text>
        </view>
      </view>

      <!-- 核验结果（仅普通自由跑） -->
      <view class="verify-section" v-if="currentMode === 'normal' && !isTaskRun && isValid !== null">
        <text class="verify-title">阳光跑核验结果</text>
        <view class="verify-row" v-if="isValid">
          <text class="verify-icon success">✅</text>
          <text class="verify-text success">本次自由跑有效，已计入阳光跑成绩！</text>
        </view>
        <view class="verify-row" v-else>
          <text class="verify-icon fail">⚠️</text>
          <text class="verify-text fail">
            本次运动未计入阳光跑：{{ failReasonText }}
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

    <!-- 今日目标提醒（仅普通阳光跑） -->
    <view class="today-tip" v-if="currentMode === 'normal' && !isTaskRun && todayCompleted !== null">
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
const currentMode = ref('normal');
const duration = ref(0);
const distance = ref(0);
const isReach = ref(false);
const campusCheckpointName = ref('');
const isPoliceFinish = ref(false);
const policePace = ref(0);
const isValid = ref(null);
const failReason = ref('');
const todayCompleted = ref(null);
const isTaskRun = ref(false);
const taskTitle = ref('');
const taskCompleted = ref(null);
const testProject = ref('');
const testType = ref('');
const testCount = ref(0);
const testQualified = ref(false);
const standardReq = ref(0);
const userScorePercent = ref(0);
const standardScorePercent = ref(0);
const suggestionText = ref('');

// 轨迹地图数据
const trajectoryPoints = ref([]);
const mapCenterLat = ref(0);
const mapCenterLng = ref(0);
const mapPolyline = ref([]);
const mapMarkers = ref([]);

// 3. 计算属性：动态标题和背景色
const modeTitle = computed(() => {
  if (isTaskRun.value) return '📋 任务跑步结算';
  switch (currentMode.value) {
    case 'police': return '🎯 专项体能结算';
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
// 警务配速是否达标 (不再硬编码6.5，因为具体项目和性别标准不同)
const isPaceQualified = ref(false);

const failReasonText = computed(() => {
  const r = failReason.value || '';
  if (r.includes('里程不足') && distance.value < 50) {
    return '里程不足（GPS 可能未正常记录，请到室外重试）';
  }
  return r || '原因未知，请联系老师查看详情';
});

const parseCheckpointsReached = (metrics) => {
  if (!metrics || metrics.checkpoints == null) return false;
  try {
    const raw = metrics.checkpoints;
    const arr = typeof raw === 'string' ? JSON.parse(raw) : raw;
    return Array.isArray(arr) && arr.length > 0;
  } catch (e) {
    return false;
  }
};

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
      isTaskRun.value = data.source === 'task';
      taskTitle.value = data.task_title || '';
      taskCompleted.value = typeof data.task_completed === 'boolean' ? data.task_completed : null;

      // Map backend data to frontend display
      if (data.display_mode) {
        currentMode.value = data.display_mode;
      } else if (data.type === 'test') {
        currentMode.value = (data.metrics && data.metrics.distance > 0) ? 'police' : 'test';
      } else if (data.type === 'run') {
        if (isTaskRun.value) {
          currentMode.value = 'police';
        } else if (parseCheckpointsReached(data.metrics)) {
          currentMode.value = 'campus';
        } else {
          currentMode.value = 'normal';
        }
      } else {
        currentMode.value = 'normal';
      }

      if (data.campus_checkpoint) {
        campusCheckpointName.value = data.campus_checkpoint;
      }

      if (data.metrics) {
        duration.value = data.metrics.duration || 0;
        distance.value = (data.metrics.distance || 0) * 1000;
        testCount.value = data.metrics.count || 0;
        testQualified.value = data.metrics.qualified;
        policePace.value = Number(data.metrics.pace) || 0;
        isPaceQualified.value = data.metrics.qualified;
      }

      if (currentMode.value === 'campus') {
        if (typeof data.campus_reached === 'boolean') {
          isReach.value = data.campus_reached;
        } else {
          isReach.value = parseCheckpointsReached(data.metrics);
        }
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

      if (isTaskRun.value) {
        isPoliceFinish.value = !!taskCompleted.value;
        isPaceQualified.value = !!taskCompleted.value;
      } else if (currentMode.value === 'police' && data.metrics) {
        isPoliceFinish.value = Number(data.metrics.distance || 0) >= 2;
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
  // 加载轨迹数据
  const trajectoryData = uni.getStorageSync('tempRunTrajectory');
  if (trajectoryData && trajectoryData.points && trajectoryData.points.length >= 1) {
    trajectoryPoints.value = trajectoryData.points;
    const pts = trajectoryData.points;
    // 地图中心取轨迹中间点
    const mid = Math.floor(pts.length / 2);
    mapCenterLat.value = pts[mid].latitude;
    mapCenterLng.value = pts[mid].longitude;

    if (pts.length >= 2) {
      // 构建轨迹线
      mapPolyline.value = [{
        points: pts,
        color: '#1E88E5',
        width: 6,
        borderColor: '#ffffff',
        borderWidth: 1
      }];
    }

    // 起点标记
    mapMarkers.value = [
      {
        id: 1,
        latitude: pts[0].latitude,
        longitude: pts[0].longitude,
        title: '起点',
        iconPath: '',
        label: { content: '起', color: '#fff', fontSize: 12, bgColor: '#FF6D00', padding: 4, borderRadius: 4 },
        width: 30,
        height: 30
      }
    ];
    // 终点标记（有多个点时）
    if (pts.length >= 2) {
      mapMarkers.value.push({
        id: 2,
        latitude: pts[pts.length - 1].latitude,
        longitude: pts[pts.length - 1].longitude,
        title: '终点',
        iconPath: '',
        label: { content: '终', color: '#fff', fontSize: 12, bgColor: '#20C997', padding: 4, borderRadius: 4 },
        width: 30,
        height: 30
      });
    }
  } else if (trajectoryData && trajectoryData.startLat) {
    // 没有轨迹点但有起点坐标
    mapCenterLat.value = trajectoryData.startLat;
    mapCenterLng.value = trajectoryData.startLng;
    mapMarkers.value = [{
      id: 1,
      latitude: trajectoryData.startLat,
      longitude: trajectoryData.startLng,
      title: '起点',
      iconPath: '',
      label: { content: '起', color: '#fff', fontSize: 12, bgColor: '#FF6D00', padding: 4, borderRadius: 4 },
      width: 30,
      height: 30
    }];
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

/* 轨迹地图 */
.map-section {
  position: relative;
  width: 100%;
  height: 500rpx;
}
.result-map {
  width: 100%;
  height: 500rpx;
}
.map-label {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.45));
  padding: 20rpx 24rpx 16rpx;
}
.map-label-text {
  color: #fff;
  font-size: 24rpx;
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

.verify-section {
  margin-top: 28rpx;
  padding-top: 24rpx;
  border-top: 1rpx dashed #ddd;
}
.verify-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 16rpx;
}
.verify-row {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
}
.verify-icon {
  font-size: 32rpx;
  flex-shrink: 0;
}
.verify-text {
  font-size: 28rpx;
  line-height: 1.5;
  flex: 1;
}
.verify-text.success {
  color: #17a077;
}
.verify-text.fail {
  color: #d81e06;
}

.today-tip {
  margin: 24rpx 20rpx 40rpx;
  padding: 20rpx 24rpx;
  border-radius: 12rpx;
  background: #fafafa;
  text-align: center;
  font-size: 26rpx;
  line-height: 1.5;
}
.today-success {
  color: #17a077;
}
.today-fail {
  color: #888;
}
</style>
