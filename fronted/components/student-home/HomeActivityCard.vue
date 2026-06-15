<template>
  <view v-if="!activity && loading" class="home-activity__sk">
    <view class="home-activity__sk-line" />
  </view>
  <view v-else-if="!activity" />
  <view v-else class="home-activity-card" @tap="handleTap">
    <view class="home-activity-card__left">
      <view class="home-activity-card__badge" :class="badgeClass">{{ activity.statusLabel }}</view>
      <text class="home-activity-card__title">{{ activity.name }}</text>
      <view class="home-activity-card__meta-row">
        <text class="home-activity-card__meta">
          <image class="home-activity-card__meta-icon" src="/static/日历.png" mode="aspectFit" />
          {{ activity.dateLabel }}
        </text>
        <text class="home-activity-card__meta">
          <image class="home-activity-card__meta-icon" src="/static/主页跑团图标.png" mode="aspectFit" />
          {{ activity.participants }}人已报名
        </text>
      </view>
      <view v-if="activity.progress != null" class="home-activity-card__progress">
        <view class="home-activity-card__progress-bar">
          <view
            class="home-activity-card__progress-fill"
            :style="{ width: activity.progress + '%' }"
          />
        </view>
      </view>
    </view>
    <view class="home-activity-card__right">
      <image
        v-if="activity.cover"
        :src="activity.cover"
        class="home-activity-card__cover"
        mode="aspectFill"
      />
      <view v-else class="home-activity-card__cover-placeholder">
        <image class="home-activity-card__cover-emoji" src="/static/主页户外跑图标.png" mode="aspectFit" />
      </view>
      <text class="home-activity-card__chev">›</text>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  activity: { type: Object, default: null },
  loading: { type: Boolean, default: false }
});

const emit = defineEmits(['tap']);

const badgeClass = computed(() => {
  const s = props.activity?.status || '';
  if (s === 'enrolling') return 'home-activity-card__badge--active';
  if (s === 'running') return 'home-activity-card__badge--running';
  return '';
});

function handleTap() {
  emit('tap', props.activity);
}
</script>

<style lang="scss" scoped>
.home-activity-card {
  display: flex;
  flex-direction: row;
  background: #fff;
  border-radius: 28rpx;
  padding: 28rpx 24rpx;
  box-shadow: 0 8rpx 36rpx rgba(26, 43, 60, 0.06);
  position: relative;
  overflow: hidden;
}
.home-activity-card:active {
  background: #FAFBFC;
}
.home-activity-card__left {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  padding-right: 20rpx;
}
.home-activity-card__badge {
  align-self: flex-start;
  display: inline-flex;
  font-size: 20rpx;
  font-weight: 700;
  color: #fff;
  padding: 4rpx 16rpx;
  border-radius: 6rpx;
  background: #33C9AB;
  margin-bottom: 16rpx;
}
.home-activity-card__badge--active {
  background: #33C9AB;
}
.home-activity-card__badge--running {
  background: #FF9F43;
}
.home-activity-card__title {
  font-size: 30rpx;
  font-weight: 800;
  color: #191C1E;
  line-height: 1.3;
}
.home-activity-card__meta-row {
  display: flex;
  flex-direction: row;
  gap: 24rpx;
  margin-top: 14rpx;
  flex-wrap: wrap;
}
.home-activity-card__meta {
  font-size: 22rpx;
  font-weight: 600;
  color: #8E8E93;
  display: flex;
  align-items: center;
}
.home-activity-card__meta-icon {
  width: 40rpx;
  height: 40rpx;
  margin-right: 4rpx;
}
.home-activity-card__progress {
  margin-top: 18rpx;
}
.home-activity-card__progress-bar {
  width: 280rpx;
  height: 8rpx;
  background: #F0F3F6;
  border-radius: 4rpx;
  overflow: hidden;
}
.home-activity-card__progress-fill {
  height: 100%;
  background: #33C9AB;
  border-radius: 4rpx;
  transition: width 0.3s ease;
}
.home-activity-card__right {
  flex-shrink: 0;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8rpx;
}
.home-activity-card__cover {
  width: 160rpx;
  height: 120rpx;
  border-radius: 16rpx;
  object-fit: cover;
}
.home-activity-card__cover-placeholder {
  width: 160rpx;
  height: 120rpx;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #E8F8F2 0%, #F0FDF6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.home-activity-card__cover-emoji {
  width: 80rpx;
  height: 80rpx;
  opacity: 0.5;
}
.home-activity-card__chev {
  font-size: 36rpx;
  color: #C5CED6;
  line-height: 1;
}
.home-activity__sk {
  background: #fff;
  border-radius: 28rpx;
  padding: 28rpx 24rpx;
  box-shadow: 0 8rpx 36rpx rgba(26, 43, 60, 0.06);
}
.home-activity__sk-line {
  height: 140rpx;
  border-radius: 12rpx;
  background: linear-gradient(90deg, #f0f3f6 25%, #e8ecf0 50%, #f0f3f6 75%);
  background-size: 200% 100%;
  animation: home-shimmer 1.2s ease-in-out infinite;
}
@keyframes home-shimmer {
  0% { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}
</style>