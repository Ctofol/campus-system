<template>
  <view class="ai-robot-container" v-if="visible">
    <view class="robot-mask" @click="close"></view>
    <view class="robot-window">
      <!-- Header -->
      <view class="robot-header">
        <view class="header-left">
          <view class="robot-avatar">🤖</view>
          <view class="robot-info">
            <text class="robot-name">运动小助手</text>
            <text class="robot-status">在线分析中...</text>
          </view>
        </view>
        <view class="header-right">
          <text class="close-btn" @click="close">×</text>
        </view>
      </view>

      <!-- Chat Area -->
      <scroll-view scroll-y class="chat-area" :scroll-top="scrollTop">
        <view class="message-list">
          <view v-for="(msg, index) in messages" :key="index" class="message-item" :class="msg.type">
            <view class="msg-avatar" v-if="msg.type === 'robot'">🤖</view>
            <view class="msg-content-box">
              <view class="msg-content">
                <text>{{ msg.text }}</text>
              </view>
              <!-- Card Content for Robot -->
              <view v-if="msg.card" class="msg-card">
                <view class="card-title">{{ msg.card.title }}</view>
                <view class="card-chart" v-if="msg.card.chartData">
                  <view class="chart-bar-item" v-for="(item, idx) in msg.card.chartData" :key="idx">
                    <text class="bar-label">{{ item.label }}</text>
                    <view class="bar-track">
                      <view class="bar-fill" :style="{ width: item.value + '%', background: item.color }"></view>
                    </view>
                    <text class="bar-val">{{ item.valText }}</text>
                  </view>
                </view>
                <view class="card-suggestion" v-if="msg.card.suggestion">
                  <text class="suggestion-icon">💡</text>
                  <text>{{ msg.card.suggestion }}</text>
                </view>
                <button v-if="msg.card.shareable" class="share-btn" size="mini" @click="shareToTeacher(msg.card)">分享给教官</button>
              </view>
            </view>
            <view class="msg-avatar" v-if="msg.type === 'user'">👤</view>
          </view>
        </view>
      </scroll-view>

      <!-- Input Area -->
      <view class="input-area">
        <scroll-view scroll-x class="quick-replies" :show-scrollbar="false">
          <view class="chip" @click="ask('我的配速怎么样？')">配速分析</view>
          <view class="chip" @click="ask('今天运动量够吗？')">运动量评估</view>
          <view class="chip" @click="ask('给点建议')">改进建议</view>
        </scroll-view>
        <view class="input-box">
          <input class="text-input" v-model="inputText" placeholder="输入问题..." confirm-type="send" @confirm="sendText" />
          <view class="send-btn" @click="sendText">发送</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';

const props = defineProps({
  visible: Boolean,
  runData: {
    type: Object,
    default: () => ({ distance: 0, pace: 0, heartRate: 0 })
  }
});

const emit = defineEmits(['update:visible', 'share']);

const messages = ref([
  { type: 'robot', text: '你好！我是你的专属运动小助手。我正在实时分析你的跑步数据，有什么可以帮你的吗？' }
]);

const inputText = ref('');
const scrollTop = ref(0);

const close = () => {
  emit('update:visible', false);
};

const scrollToBottom = () => {
  nextTick(() => {
    scrollTop.value = 99999;
  });
};

const sendText = () => {
  if (!inputText.value.trim()) return;
  ask(inputText.value);
  inputText.value = '';
};

const ask = (text) => {
  // User message
  messages.value.push({ type: 'user', text });
  scrollToBottom();

  // Robot thinking simulation
  setTimeout(() => {
    analyzeAndReply(text);
  }, 800);
};

const analyzeAndReply = (question) => {
  let reply = { type: 'robot', text: '', card: null };
  const { distance, pace, heartRate } = props.runData;

  if (question.includes('配速')) {
    reply.text = `当前配速 ${pace.toFixed(2)} 分钟/公里。`;
    let suggestion = '';
    let color = '#20C997';
    if (pace < 4) {
      suggestion = '速度很快，请注意保持心率稳定！';
      color = '#FF6B6B';
    } else if (pace > 8) {
      suggestion = '速度稍慢，建议加快摆臂频率来提升速度。';
      color = '#FF9F43';
    } else {
      suggestion = '配速保持得很好，继续加油！';
    }
    
    reply.card = {
      title: '🏃 配速分析',
      chartData: [
        { label: '当前', value: Math.min(100, (10/pace)*50), valText: `${pace.toFixed(1)}`, color: color },
        { label: '目标', value: 70, valText: '6.0', color: '#3A7BD5' } // Assume target 6.0
      ],
      suggestion,
      shareable: true
    };
  } else if (question.includes('运动量') || question.includes('够吗')) {
    const km = (distance / 1000).toFixed(2);
    reply.text = `你今天已经跑了 ${km} 公里。`;
    let suggestion = '';
    if (km < 2) {
      suggestion = '建议今天至少完成 3 公里，加油！';
    } else if (km > 10) {
      suggestion = '运动量非常充足，注意跑后拉伸。';
    } else {
      suggestion = '运动量适中，保持这个节奏。';
    }
    reply.card = {
      title: '📊 运动量评估',
      chartData: [
        { label: '今日', value: Math.min(100, (km/5)*100), valText: `${km}km`, color: '#20C997' },
        { label: '目标', value: 100, valText: '5.0km', color: '#eee' }
      ],
      suggestion,
      shareable: true
    };
  } else if (question.includes('建议') || question.includes('分析')) {
    reply.text = '基于你的实时数据，我生成了一份简报：';
    reply.card = {
      title: '💡 综合改进建议',
      suggestion: heartRate > 160 ? '心率偏高，建议适当放慢速度，调整呼吸。' : '心率控制良好，可以尝试进行间歇跑训练提升耐力。',
      chartData: [
        { label: '心率', value: Math.min(100, (heartRate/200)*100), valText: `${heartRate}bpm`, color: heartRate > 160 ? '#FF4757' : '#20C997' },
        { label: '配速', value: Math.min(100, (10/pace)*50), valText: `${pace.toFixed(1)}`, color: '#3A7BD5' }
      ],
      shareable: true
    };
  } else {
    reply.text = '抱歉，我还在学习中，暂时只能回答关于配速、运动量和改进建议的问题。';
  }

  messages.value.push(reply);
  scrollToBottom();
};

const shareToTeacher = (card) => {
  uni.showToast({ title: '已发送给教官', icon: 'success' });
  emit('share', card);
};

// Auto welcome message update when visible changes
watch(() => props.visible, (val) => {
  if (val && messages.value.length === 0) {
    messages.value.push({ type: 'robot', text: '你好！我是你的专属运动小助手。' });
  }
});
</script>

<style scoped>
.ai-robot-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 999;
  display: flex;
  justify-content: center;
  align-items: flex-end;
}

.robot-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.4);
}

.robot-window {
  position: relative;
  width: 100%;
  height: 75vh;
  background: #F5F7FA;
  border-radius: 30rpx 30rpx 0 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 -4rpx 20rpx rgba(0,0,0,0.1);
}

.robot-header {
  background: #fff;
  padding: 20rpx 30rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
}

.header-left {
  display: flex;
  align-items: center;
}

.robot-avatar {
  width: 80rpx;
  height: 80rpx;
  background: #E3F2FD;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  margin-right: 20rpx;
}

.robot-info {
  display: flex;
  flex-direction: column;
}

.robot-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.robot-status {
  font-size: 24rpx;
  color: #20C997;
}

.close-btn {
  font-size: 40rpx;
  color: #999;
  padding: 10rpx;
}

.chat-area {
  flex: 1;
  padding: 20rpx;
  box-sizing: border-box;
  overflow-y: auto;
}

.message-item {
  display: flex;
  margin-bottom: 30rpx;
}

.message-item.robot {
  justify-content: flex-start;
}

.message-item.user {
  justify-content: flex-end;
}

.msg-avatar {
  width: 70rpx;
  height: 70rpx;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  margin: 0 16rpx;
  flex-shrink: 0;
}

.message-item.user .msg-avatar {
  background: #DCF8C6;
  order: 2;
}

.msg-content-box {
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.message-item.user .msg-content-box {
  align-items: flex-end;
}

.msg-content {
  background: #fff;
  padding: 20rpx;
  border-radius: 20rpx;
  font-size: 28rpx;
  color: #333;
  line-height: 1.5;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}

.message-item.user .msg-content {
  background: #95EC69;
}

/* Card Style */
.msg-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  margin-top: 16rpx;
  width: 100%;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.08);
}

.card-title {
  font-size: 28rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
  color: #333;
  border-left: 6rpx solid #3A7BD5;
  padding-left: 16rpx;
}

.card-chart {
  margin-bottom: 20rpx;
}

.chart-bar-item {
  display: flex;
  align-items: center;
  margin-bottom: 12rpx;
}

.bar-label {
  font-size: 24rpx;
  color: #666;
  width: 60rpx;
}

.bar-track {
  flex: 1;
  height: 16rpx;
  background: #f0f0f0;
  border-radius: 8rpx;
  margin: 0 16rpx;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 8rpx;
  transition: width 0.5s ease;
}

.bar-val {
  font-size: 24rpx;
  color: #333;
  width: 80rpx;
  text-align: right;
}

.card-suggestion {
  background: #FFF9C4;
  padding: 16rpx;
  border-radius: 12rpx;
  font-size: 24rpx;
  color: #FBC02D;
  display: flex;
  align-items: flex-start;
  margin-bottom: 16rpx;
}

.suggestion-icon {
  margin-right: 8rpx;
}

.share-btn {
  width: 100%;
  background: #3A7BD5;
  color: #fff;
  border: none;
}

/* Input Area */
.input-area {
  background: #fff;
  padding: 20rpx;
  border-top: 1px solid #eee;
}

.quick-replies {
  white-space: nowrap;
  margin-bottom: 20rpx;
}

.chip {
  display: inline-block;
  padding: 10rpx 24rpx;
  background: #F0F2F5;
  color: #333;
  border-radius: 30rpx;
  font-size: 24rpx;
  margin-right: 16rpx;
}

.input-box {
  display: flex;
  align-items: center;
}

.text-input {
  flex: 1;
  background: #F0F2F5;
  height: 72rpx;
  border-radius: 36rpx;
  padding: 0 30rpx;
  font-size: 28rpx;
  margin-right: 20rpx;
}

.send-btn {
  background: #20C997;
  color: #fff;
  padding: 14rpx 30rpx;
  border-radius: 36rpx;
  font-size: 28rpx;
  font-weight: bold;
}
</style>