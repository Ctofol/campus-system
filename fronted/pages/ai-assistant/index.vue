<template>
  <view class="ai-page">
    <view class="hero">
      <text class="hero-kicker">Campus Sports AI</text>
      <text class="hero-title">AI 体育助手</text>
      <text class="hero-subtitle">运动报告、体测反馈、校园规则问答和教师班级简报。</text>
      <view class="mode-pill">
        <text>{{ statusText }}</text>
      </view>
    </view>

    <view class="content">
      <view class="card" v-if="role === 'teacher'">
        <view class="card-head">
          <text class="card-title">班级智能简报</text>
          <button class="mini-btn" :loading="briefLoading" @click="loadTeacherBriefing">生成</button>
        </view>
        <text class="summary">{{ teacherBrief.summary || '点击生成，快速查看今日班级运动状态。' }}</text>
        <view class="list" v-if="teacherBrief.alerts && teacherBrief.alerts.length">
          <text class="list-item" v-for="item in teacherBrief.alerts" :key="item">{{ item }}</text>
        </view>
      </view>

      <view class="card" v-else>
        <view class="card-head">
          <text class="card-title">我的训练建议</text>
          <button class="mini-btn" :loading="runLoading" @click="loadRunReport">生成</button>
        </view>
        <text class="summary">{{ runReport.summary || '点击生成，基于你的最近运动数据给出训练建议。' }}</text>
        <view class="list" v-if="runReport.suggestions && runReport.suggestions.length">
          <text class="list-item" v-for="item in runReport.suggestions" :key="item">{{ item }}</text>
        </view>
      </view>

      <view class="card">
        <text class="card-title">校园体育问答</text>
        <view class="chips">
          <view class="chip" v-for="item in prompts" :key="item" @click="askPreset(item)">{{ item }}</view>
        </view>
        <textarea
          class="question"
          v-model="question"
          maxlength="500"
          auto-height
          placeholder="输入你想问的问题"
        />
        <button class="primary-btn" :loading="chatLoading" @click="sendQuestion">发送</button>
      </view>

      <view class="answer-card" v-if="answer">
        <text class="answer-title">AI 回答</text>
        <text class="answer-text">{{ answer }}</text>
        <view class="list" v-if="answerSuggestions.length">
          <text class="list-item" v-for="item in answerSuggestions" :key="item">{{ item }}</text>
        </view>
        <text class="disclaimer" v-if="disclaimer">{{ disclaimer }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import {
  askAiAssistant,
  getAiAssistantStatus,
  getAiRunReport,
  getTeacherAiBriefing
} from '@/utils/request.js';

const role = ref('student');
const status = ref({ mode: 'local_demo', model: 'local-rule-engine' });
const question = ref('');
const answer = ref('');
const answerSuggestions = ref([]);
const disclaimer = ref('');
const chatLoading = ref(false);
const runLoading = ref(false);
const briefLoading = ref(false);
const runReport = ref({});
const teacherBrief = ref({});

const prompts = ['阳光跑怎样才算有效？', '体测视频怎么拍？', '伤病请假怎么报备？'];

const statusText = computed(() => {
  if (status.value.mode === 'llm') return `真实大模型：${status.value.model || '已配置'}`;
  return '本地演示模式：无需 API Key';
});

const askPreset = (text) => {
  question.value = text;
  sendQuestion();
};

const sendQuestion = async () => {
  const q = String(question.value || '').trim();
  if (!q) {
    uni.showToast({ title: '请输入问题', icon: 'none' });
    return;
  }
  chatLoading.value = true;
  try {
    const res = await askAiAssistant(q);
    answer.value = res.answer || '暂时没有生成回答。';
    answerSuggestions.value = res.suggestions || [];
    disclaimer.value = res.disclaimer || '';
  } catch (e) {
    answer.value = 'AI 助手暂时不可用，请稍后重试。';
    answerSuggestions.value = [];
    disclaimer.value = '';
  } finally {
    chatLoading.value = false;
  }
};

const loadRunReport = async () => {
  runLoading.value = true;
  try {
    runReport.value = await getAiRunReport({});
  } catch (e) {
    runReport.value = {
      summary: '暂时无法生成训练建议。',
      suggestions: ['可以先查看历史运动记录，稍后再试。']
    };
  } finally {
    runLoading.value = false;
  }
};

const loadTeacherBriefing = async () => {
  briefLoading.value = true;
  try {
    teacherBrief.value = await getTeacherAiBriefing();
  } catch (e) {
    teacherBrief.value = {
      summary: '暂时无法生成班级简报。',
      alerts: ['可以先查看教师工作台统计，稍后再试。']
    };
  } finally {
    briefLoading.value = false;
  }
};

const loadStatus = async () => {
  try {
    status.value = await getAiAssistantStatus();
  } catch (e) {
    status.value = { mode: 'local_demo', model: 'local-rule-engine' };
  }
};

onLoad(() => {
  role.value = uni.getStorageSync('userRole') || 'student';
  loadStatus();
  if (role.value === 'teacher') loadTeacherBriefing();
  else loadRunReport();
});
</script>

<style scoped>
.ai-page {
  min-height: 100vh;
  background: #f6f8fb;
}

.hero {
  padding: 56rpx 32rpx 42rpx;
  background: linear-gradient(135deg, #102433, #20c997);
  color: #fff;
  display: flex;
  flex-direction: column;
}

.hero-kicker {
  font-size: 22rpx;
  opacity: 0.78;
}

.hero-title {
  margin-top: 10rpx;
  font-size: 48rpx;
  font-weight: 800;
}

.hero-subtitle {
  margin-top: 14rpx;
  max-width: 620rpx;
  font-size: 27rpx;
  line-height: 1.55;
  opacity: 0.9;
}

.mode-pill {
  align-self: flex-start;
  margin-top: 24rpx;
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.16);
  font-size: 23rpx;
}

.content {
  padding: 24rpx;
}

.card,
.answer-card {
  margin-bottom: 22rpx;
  padding: 28rpx;
  border-radius: 18rpx;
  background: #fff;
  box-shadow: 0 8rpx 24rpx rgba(16, 36, 51, 0.06);
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title,
.answer-title {
  display: block;
  font-size: 31rpx;
  color: #18232e;
  font-weight: 800;
}

.mini-btn {
  margin: 0;
  height: 58rpx;
  line-height: 58rpx;
  padding: 0 24rpx;
  border-radius: 999rpx;
  background: #20c997;
  color: #fff;
  font-size: 24rpx;
}

.mini-btn::after,
.primary-btn::after {
  border: none;
}

.summary,
.answer-text {
  display: block;
  margin-top: 16rpx;
  color: #364657;
  font-size: 27rpx;
  line-height: 1.65;
}

.list {
  margin-top: 16rpx;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.list-item {
  padding: 14rpx 18rpx;
  border-radius: 12rpx;
  background: #f4faf8;
  color: #256f61;
  font-size: 25rpx;
  line-height: 1.5;
}

.chips {
  margin-top: 18rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.chip {
  padding: 12rpx 18rpx;
  border-radius: 999rpx;
  background: #eef7f5;
  color: #1f8f7d;
  font-size: 24rpx;
}

.question {
  margin-top: 18rpx;
  width: 100%;
  min-height: 140rpx;
  box-sizing: border-box;
  padding: 20rpx;
  border-radius: 14rpx;
  background: #f6f8fb;
  color: #18232e;
  font-size: 27rpx;
  line-height: 1.5;
}

.primary-btn {
  margin-top: 18rpx;
  width: 100%;
  height: 82rpx;
  line-height: 82rpx;
  border-radius: 14rpx;
  background: #20c997;
  color: #fff;
  font-size: 30rpx;
  font-weight: 700;
}

.disclaimer {
  display: block;
  margin-top: 16rpx;
  color: #8a96a3;
  font-size: 23rpx;
  line-height: 1.5;
}
</style>
