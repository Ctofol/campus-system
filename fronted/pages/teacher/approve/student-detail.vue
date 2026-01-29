<template>
  <view class="container">
    <view class="header">
      <text class="title">{{ studentName }} 的运动记录</text>
    </view>
    
    <view class="stats-card">
      <view class="stat-item">
        <text class="stat-num">{{ totalDistance }}</text>
        <text class="stat-label">总里程(km)</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <text class="stat-num">{{ totalDuration }}</text>
        <text class="stat-label">总时长(min)</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <text class="stat-num">{{ activities.length }}</text>
        <text class="stat-label">总次数</text>
      </view>
    </view>

    <scroll-view scroll-y class="list">
      <view class="item" v-for="item in activities" :key="item.id">
        <view class="info">
          <text class="type">{{ item.type === 'run' ? '跑步' : '体测' }}</text>
          <text class="desc" v-if="item.type === 'test' || item.metrics?.count !== undefined">
             {{ item.metrics?.duration ? Math.floor(item.metrics.duration / 60) : 0 }}分钟 | 
             {{ item.metrics?.count ? item.metrics.count : 0 }}次
          </text>
          <text class="desc" v-else>
             {{ item.metrics?.distance ? Number(item.metrics.distance).toFixed(2) : 0 }}km | 
             {{ item.metrics?.duration ? Math.floor(item.metrics.duration / 60) : 0 }}分钟
          </text>
          <text class="time">{{ new Date(item.started_at).toLocaleString() }}</text>
          
          <view v-if="item.evidence && item.evidence.length > 0" class="evidence-area">
              <view class="evidence-btn" @click.stop="previewEvidence(item.evidence)">
                  <text class="btn-icon">📷</text> 查看媒体
              </view>
          </view>
        </view>
        <view class="status-tag" :class="item.status">
            {{ getStatusText(item.status) }}
        </view>
      </view>
      <view v-if="activities.length === 0" class="empty">暂无运动记录</view>
    </scroll-view>
    <view v-if="showVideoModal" class="video-modal" @click="closeVideo">
      <view class="video-content" @click.stop>
        <video class="video-player" :src="videoUrls[currentVideoIndex]" controls autoplay></video>
        <view class="video-actions">
          <button v-if="videoUrls.length > 1" size="mini" @click="prevVideo">上一个</button>
          <button v-if="videoUrls.length > 1" size="mini" @click="nextVideo">下一个</button>
          <button size="mini" @click="closeVideo">关闭</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { getTeacherStudentActivities, BASE_URL } from '@/utils/request.js';

const studentId = ref(null);
const studentName = ref('');
const activities = ref([]);
const showVideoModal = ref(false);
const videoUrls = ref([]);
const currentVideoIndex = ref(0);

const hasMedia = (evidence) => {
    if (!evidence || evidence.length === 0) return false;
    return evidence.some(e => {
        const url = e.data_ref || '';
        // Check if explicit type or inferred from extension
        if (e.evidence_type === 'video' || e.evidence_type === 'image' || e.evidence_type === 'camera') return true;
        return /\.(mp4|webm|ogg|jpg|jpeg|png|gif)$/i.test(url);
    });
};

const previewEvidence = (evidence) => {
    if (!evidence || evidence.length === 0) return;
    
    const items = evidence.map(e => {
        const url = e.data_ref.startsWith('http') ? e.data_ref : `${BASE_URL}${e.data_ref}`;
        const type = e.evidence_type ? e.evidence_type : (/\.(mp4|webm|ogg)$/i.test(url) ? 'video' : 'image');
        return { url, type };
    });
    const imgList = items.filter(i => i.type === 'image').map(i => i.url);
    const vidList = items.filter(i => i.type === 'video').map(i => i.url);
    if (imgList.length > 0 && vidList.length === 0) {
      uni.previewImage({ urls: imgList, current: 0 });
      return;
    }
    if (vidList.length > 0) {
      videoUrls.value = vidList;
      currentVideoIndex.value = 0;
      showVideoModal.value = true;
    }
};

const totalDistance = computed(() => {
    const dist = activities.value.reduce((acc, cur) => acc + (cur.metrics?.distance || 0), 0);
    return dist.toFixed(2);
});

const totalDuration = computed(() => {
    const dur = activities.value.reduce((acc, cur) => acc + (cur.metrics?.duration || 0), 0);
    return Math.floor(dur / 60);
});

const getStatusText = (status) => {
    const map = {
        'pending': '待审批',
        'approved': '已通过',
        'rejected': '已驳回',
        'completed': '已完成',
        'finished': '已完成' // Default backend status
    };
    return map[status] || status;
};

const loadStudentData = async () => {
    if (!studentId.value) return;
    try {
        const res = await getTeacherStudentActivities(studentId.value, { page: 1, size: 100 });
        if (res && res.items) {
            activities.value = res.items;
        }
    } catch (e) {
        console.error(e);
        uni.showToast({ title: '加载失败', icon: 'none' });
    }
};

onLoad((options) => {
    if (options.studentId) {
        studentId.value = options.studentId;
        studentName.value = options.studentName || '学生';
        loadStudentData();
    }
});

const closeVideo = () => {
  showVideoModal.value = false;
};
const prevVideo = () => {
  if (videoUrls.value.length === 0) return;
  currentVideoIndex.value = (currentVideoIndex.value - 1 + videoUrls.value.length) % videoUrls.value.length;
};
const nextVideo = () => {
  if (videoUrls.value.length === 0) return;
  currentVideoIndex.value = (currentVideoIndex.value + 1) % videoUrls.value.length;
};
</script>

<style>
.container { padding: 20rpx; background-color: #f5f7fa; min-height: 100vh; }
.header { margin-bottom: 20rpx; font-weight: bold; font-size: 32rpx; padding: 10rpx 0; }
.stats-card { display: flex; background: #fff; padding: 30rpx; border-radius: 12rpx; margin-bottom: 20rpx; justify-content: space-around; align-items: center; }
.stat-item { display: flex; flex-direction: column; align-items: center; }
.stat-num { font-size: 36rpx; font-weight: bold; color: #20C997; }
.stat-label { font-size: 24rpx; color: #666; margin-top: 10rpx; }
.stat-divider { width: 1px; height: 60rpx; background: #eee; }

.item { display: flex; justify-content: space-between; align-items: center; background: #fff; padding: 30rpx; margin-bottom: 20rpx; border-radius: 12rpx; }
.info { display: flex; flex-direction: column; }
.type { font-weight: bold; font-size: 30rpx; margin-bottom: 8rpx; }
.desc { color: #666; font-size: 26rpx; margin-bottom: 8rpx; }
.time { color: #999; font-size: 22rpx; }
.evidence-area { margin-top: 10rpx; }
.evidence-btn { display: inline-flex; align-items: center; font-size: 24rpx; color: #20C997; padding: 8rpx 16rpx; background: #e6fcf5; border-radius: 8rpx; }
.btn-icon { margin-right: 6rpx; }
.status-tag { font-size: 24rpx; padding: 4rpx 12rpx; border-radius: 8rpx; background: #eee; color: #666; }
.status-tag.approved, .status-tag.completed { background: #e6fcf5; color: #20C997; }
.status-tag.rejected { background: #fff5f5; color: #fa5252; }
.empty { text-align: center; color: #999; margin-top: 100rpx; font-size: 28rpx; }
.video-modal { position: fixed; top:0; left:0; right:0; bottom:0; background: rgba(0,0,0,0.8); display:flex; align-items:center; justify-content:center; z-index: 9999; }
.video-content { background:#fff; width: 90%; max-width: 700rpx; border-radius: 16rpx; overflow: hidden; display:flex; flex-direction:column; }
.video-player { width: 100%; height: 420rpx; background: #000; }
.video-actions { display:flex; justify-content: space-between; padding: 20rpx; }
</style>
