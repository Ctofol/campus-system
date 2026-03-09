<template>
  <view class="score-page">
    <!-- Header -->
    <view class="header-card">
      <text class="task-title">{{ taskTitle }}</text>
      <text class="student-info">学生：{{ studentName }}</text>
    </view>

    <!-- Activity Info -->
    <view class="info-card">
      <view class="info-row">
        <text class="label">活动类型</text>
        <text class="value">{{ activityType }}</text>
      </view>
      <view class="info-row">
        <text class="label">完成时间</text>
        <text class="value">{{ completedTime }}</text>
      </view>
      <view class="info-row">
        <text class="label">活动数据</text>
        <text class="value">{{ activityData }}</text>
      </view>
      <view class="info-row" v-if="aiScore">
        <text class="label">AI评分</text>
        <text class="value highlight">{{ aiScore }}分</text>
      </view>
    </view>

    <!-- Video Preview (if exists) -->
    <view class="video-card" v-if="videoUrl">
      <text class="card-title">📹 活动视频</text>
      <video 
        :src="videoUrl" 
        class="activity-video"
        controls
        :show-center-play-btn="true"
      ></video>
    </view>

    <!-- Score Input -->
    <view class="score-card">
      <text class="card-title">教师打分</text>
      
      <view class="score-input-area">
        <text class="score-label">分数 (0-100)</text>
        <view class="score-slider-container">
          <slider 
            :value="score" 
            @change="onScoreChange" 
            min="0" 
            max="100" 
            step="1"
            activeColor="#20C997"
            backgroundColor="#f0f0f0"
            block-size="24"
          />
          <text class="score-display">{{ score }}分</text>
        </view>
      </view>

      <view class="comment-area">
        <text class="comment-label">评语（选填）</text>
        <textarea 
          class="comment-input" 
          v-model="comment" 
          placeholder="请输入评语，如：动作标准，完成质量高..."
          maxlength="200"
        />
        <text class="char-count">{{ comment.length }}/200</text>
      </view>
    </view>

    <!-- History Scores (if exists) -->
    <view class="history-card" v-if="hasHistory">
      <text class="card-title">历史打分</text>
      <view class="history-item">
        <text class="history-score">上次打分：{{ lastScore }}分</text>
        <text class="history-time">{{ lastScoreTime }}</text>
      </view>
      <text class="history-comment" v-if="lastComment">{{ lastComment }}</text>
    </view>

    <!-- Footer Actions -->
    <view class="footer-actions">
      <button class="action-btn cancel" @click="goBack">取消</button>
      <button class="action-btn submit" @click="submitScore">提交打分</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { request, BASE_URL } from '@/utils/request.js';

const activityId = ref(0);
const taskTitle = ref('');
const studentName = ref('');
const activityType = ref('');
const completedTime = ref('');
const activityData = ref('');
const aiScore = ref(0);
const videoUrl = ref('');

const score = ref(85); // 默认85分
const comment = ref('');

// 历史打分
const hasHistory = ref(false);
const lastScore = ref(0);
const lastScoreTime = ref('');
const lastComment = ref('');

const onScoreChange = (e) => {
  score.value = e.detail.value;
};

const loadActivityData = async () => {
  try {
    // 获取活动详情
    const activity = await request({
      url: `/teacher/activities/${activityId.value}`,
      method: 'GET'
    });
    
    studentName.value = activity.student_name || '未知学生';
    activityType.value = activity.type === 'run' ? '跑步' : '体能测试';
    completedTime.value = activity.ended_at ? new Date(activity.ended_at).toLocaleString() : '未知';
    
    // 活动数据
    if (activity.metrics) {
      if (activity.type === 'run') {
        activityData.value = `${activity.metrics.distance || 0}km / ${Math.floor((activity.metrics.duration || 0) / 60)}分钟`;
      } else {
        activityData.value = `${activity.metrics.count || 0}次`;
      }
      
      aiScore.value = activity.metrics.score || 0;
      
      // 视频URL
      if (activity.metrics.video_url) {
        videoUrl.value = activity.metrics.video_url.startsWith('http') 
          ? activity.metrics.video_url 
          : `${BASE_URL}${activity.metrics.video_url}`;
      }
      
      // 历史打分
      if (activity.metrics.teacher_score) {
        hasHistory.value = true;
        lastScore.value = activity.metrics.teacher_score;
        lastComment.value = activity.metrics.teacher_comment || '';
        lastScoreTime.value = activity.metrics.scored_at 
          ? new Date(activity.metrics.scored_at).toLocaleString() 
          : '';
        
        // 如果有历史打分，使用历史分数作为默认值
        score.value = activity.metrics.teacher_score;
        comment.value = activity.metrics.teacher_comment || '';
      }
    }
    
  } catch (e) {
    console.error('加载活动数据失败:', e);
    uni.showToast({ title: '加载失败', icon: 'none' });
  }
};

const submitScore = async () => {
  if (score.value < 0 || score.value > 100) {
    return uni.showToast({ title: '分数必须在0-100之间', icon: 'none' });
  }
  
  uni.showLoading({ title: '提交中...' });
  
  try {
    const method = hasHistory.value ? 'PUT' : 'POST';
    const res = await request({
      url: `/teacher/activities/${activityId.value}/score`,
      method: method,
      data: {
        activity_id: activityId.value,
        score: score.value,
        comment: comment.value || null
      }
    });
    
    uni.hideLoading();
    uni.showToast({ 
      title: hasHistory.value ? '打分更新成功' : '打分成功', 
      icon: 'success' 
    });
    
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
    
  } catch (e) {
    uni.hideLoading();
    console.error('提交打分失败:', e);
    uni.showToast({ title: '提交失败', icon: 'none' });
  }
};

const goBack = () => {
  uni.navigateBack();
};

onLoad((options) => {
  if (options.activityId) {
    activityId.value = parseInt(options.activityId);
    taskTitle.value = options.taskTitle || '任务打分';
    loadActivityData();
  }
});
</script>

<style scoped>
.score-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20rpx;
  padding-bottom: 120rpx;
}

.header-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}

.task-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 12rpx;
}

.student-info {
  font-size: 26rpx;
  color: #666;
}

.info-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1px solid #f5f5f5;
}

.info-row:last-child {
  border-bottom: none;
}

.label {
  font-size: 28rpx;
  color: #666;
}

.value {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.value.highlight {
  color: #20C997;
  font-weight: bold;
}

.video-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}

.card-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
}

.activity-video {
  width: 100%;
  height: 400rpx;
  background: #000;
  border-radius: 12rpx;
}

.score-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}

.score-input-area {
  margin-bottom: 30rpx;
}

.score-label {
  font-size: 28rpx;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
}

.score-slider-container {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.score-slider-container slider {
  flex: 1;
}

.score-display {
  font-size: 36rpx;
  font-weight: bold;
  color: #20C997;
  min-width: 100rpx;
  text-align: right;
}

.comment-area {
  position: relative;
}

.comment-label {
  font-size: 28rpx;
  color: #333;
  display: block;
  margin-bottom: 16rpx;
}

.comment-input {
  width: 100%;
  height: 200rpx;
  background: #f9f9f9;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.char-count {
  font-size: 24rpx;
  color: #999;
  text-align: right;
  display: block;
  margin-top: 8rpx;
}

.history-card {
  background: #fff5e6;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  border: 1px solid #ffe0b3;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.history-score {
  font-size: 28rpx;
  color: #ff9f43;
  font-weight: bold;
}

.history-time {
  font-size: 24rpx;
  color: #999;
}

.history-comment {
  font-size: 26rpx;
  color: #666;
  line-height: 1.6;
}

.footer-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: #fff;
  padding: 20rpx 30rpx;
  box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
  display: flex;
  gap: 20rpx;
  box-sizing: border-box;
}

.action-btn {
  flex: 1;
  margin: 0;
  font-size: 30rpx;
  border-radius: 40rpx;
  height: 80rpx;
  line-height: 80rpx;
}

.action-btn.cancel {
  background: #fff;
  color: #666;
  border: 1px solid #ddd;
}

.action-btn.submit {
  background: #20C997;
  color: #fff;
}
</style>
