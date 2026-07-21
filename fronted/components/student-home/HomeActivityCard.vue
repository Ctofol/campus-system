<template>
  <view v-if="!activity && loading" class="home-activity__sk">
    <view class="home-activity__sk-line" />
  </view>
  <view v-else-if="!activity" class="home-activity-card home-activity-card--empty" @tap="handleTap">
    <view class="home-activity-card__empty">
      <image class="home-activity-card__empty-icon" src="/static/home-run-group.png" mode="aspectFit" />
      <text class="home-activity-card__empty-title">暂无最新活动</text>
      <text class="home-activity-card__empty-sub">去跑团看看附近的报名信息</text>
    </view>
  </view>
  <view v-else class="home-activity-card" @tap="handleTap">
    <view class="home-activity-card__left">
      <view class="home-activity-card__badge" :class="badgeClass">{{ activity.statusLabel }}</view>
      <text class="home-activity-card__title">{{ activity.name }}</text>
      <view class="home-activity-card__meta-row">
        <text class="home-activity-card__meta">
          <image class="home-activity-card__meta-icon" src="/static/icons/icon-calendar.svg" mode="aspectFit" />
          {{ activity.dateLabel }}
        </text>
        <text class="home-activity-card__meta">
          <image class="home-activity-card__meta-icon" src="/static/icons/icon-learning-users.svg" mode="aspectFit" />
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
        <image class="home-activity-card__cover-emoji" src="/static/home-outdoor-run.png" mode="aspectFit" />
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
  border-radius: 18rpx;
  padding: 24rpx 22rpx;
  border: 1rpx solid rgba(24, 35, 46, 0.06);
  box-shadow: 0 8rpx 22rpx rgba(24, 35, 46, 0.045);
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
}
.home-activity-card--empty {
  min-height: 180rpx;
  align-items: center;
  justify-content: center;
}
.home-activity-card:active {
  background: #F7FAFB;
}
.home-activity-card__empty {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.home-activity-card__empty-icon {
  width: 62rpx;
  height: 62rpx;
  opacity: 0.55;
}
.home-activity-card__empty-title {
  margin-top: 10rpx;
  font-size: 28rpx;
  font-weight: 700;
  color: #18232E;
}
.home-activity-card__empty-sub {
  margin-top: 4rpx;
  font-size: 22rpx;
  color: #718094;
}
.home-activity-card__left {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  padding-right: 18rpx;
}
.home-activity-card__badge {
  align-self: flex-start;
  display: inline-flex;
  font-size: 20rpx;
  font-weight: 700;
  color: #fff;
  padding: 4rpx 16rpx;
  border-radius: 6rpx;
  background: #24BFA2;
  margin-bottom: 14rpx;
}
.home-activity-card__badge--active {
  background: #24BFA2;
}
.home-activity-card__badge--running {
  background: #FF9F43;
}
.home-activity-card__title {
  font-size: 29rpx;
  font-weight: 800;
  color: #18232E;
  line-height: 1.3;
}
.home-activity-card__meta-row {
  display: flex;
  flex-direction: row;
  gap: 20rpx;
  margin-top: 12rpx;
  flex-wrap: wrap;
}
.home-activity-card__meta {
  font-size: 22rpx;
  font-weight: 600;
  color: #718094;
  display: flex;
  align-items: center;
}
.home-activity-card__meta-icon {
  width: 32rpx;
  height: 32rpx;
  margin-right: 4rpx;
}
.home-activity-card__progress {
  margin-top: 16rpx;
}
.home-activity-card__progress-bar {
  width: 280rpx;
  height: 8rpx;
  background: #EEF2F5;
  border-radius: 4rpx;
  overflow: hidden;
}
.home-activity-card__progress-fill {
  height: 100%;
  background: #24BFA2;
  border-radius: 4rpx;
}
.home-activity-card__right {
  flex-shrink: 0;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8rpx;
}
.home-activity-card__cover {
  width: 148rpx;
  height: 112rpx;
  border-radius: 14rpx;
  object-fit: cover;
}
.home-activity-card__cover-placeholder {
  width: 148rpx;
  height: 112rpx;
  border-radius: 14rpx;
  background: #F4FAF8;
  display: flex;
  align-items: center;
  justify-content: center;
}
.home-activity-card__cover-emoji {
  width: 72rpx;
  height: 72rpx;
  opacity: 0.55;
}
.home-activity-card__chev {
  font-size: 34rpx;
  color: #B8C3CC;
  line-height: 1;
}
.home-activity__sk {
  background: #fff;
  border-radius: 18rpx;
  padding: 24rpx 22rpx;
  border: 1rpx solid rgba(24, 35, 46, 0.06);
  box-sizing: border-box;
}
.home-activity__sk-line {
  height: 132rpx;
  border-radius: 12rpx;
  background: #EEF2F5;
}
</style>
