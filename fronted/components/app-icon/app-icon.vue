<template>
  <view class="app-icon" :class="[`app-icon--${name}`, `app-icon--${tone}`]" :style="rootStyle">
    <view v-if="name === 'bot'" class="app-icon__bot">
      <view class="app-icon__bot-stem" />
      <view class="app-icon__bot-eye app-icon__bot-eye--left" />
      <view class="app-icon__bot-eye app-icon__bot-eye--right" />
      <view class="app-icon__bot-mouth" />
    </view>
    <view v-else-if="name === 'user'" class="app-icon__user">
      <view class="app-icon__user-head" />
      <view class="app-icon__user-body" />
    </view>
    <view v-else-if="name === 'bulb'" class="app-icon__bulb">
      <view class="app-icon__bulb-core" />
      <view class="app-icon__bulb-base" />
    </view>
    <view v-else-if="name === 'run'" class="app-icon__run">
      <view class="app-icon__run-head" />
      <view class="app-icon__run-body" />
      <view class="app-icon__run-arm app-icon__run-arm--front" />
      <view class="app-icon__run-arm app-icon__run-arm--back" />
      <view class="app-icon__run-leg app-icon__run-leg--front" />
      <view class="app-icon__run-leg app-icon__run-leg--back" />
    </view>
    <view v-else-if="name === 'chart'" class="app-icon__chart">
      <view class="app-icon__chart-bar app-icon__chart-bar--one" />
      <view class="app-icon__chart-bar app-icon__chart-bar--two" />
      <view class="app-icon__chart-bar app-icon__chart-bar--three" />
    </view>
    <view v-else-if="name === 'lock' || name === 'unlock'" class="app-icon__lock">
      <view class="app-icon__lock-shackle" :class="{ 'app-icon__lock-shackle--open': name === 'unlock' }" />
      <view class="app-icon__lock-body" />
    </view>
    <view v-else-if="name === 'play'" class="app-icon__play" />
    <view v-else-if="name === 'pause'" class="app-icon__pause">
      <view class="app-icon__pause-bar" />
      <view class="app-icon__pause-bar" />
    </view>
    <view v-else-if="name === 'pin'" class="app-icon__pin">
      <view class="app-icon__pin-dot" />
    </view>
    <view v-else-if="name === 'camera'" class="app-icon__camera">
      <view class="app-icon__camera-top" />
      <view class="app-icon__camera-lens" />
    </view>
    <view v-else-if="name === 'edit'" class="app-icon__edit">
      <view class="app-icon__edit-line" />
      <view class="app-icon__edit-tip" />
    </view>
    <view v-else-if="name === 'close'" class="app-icon__close">
      <view class="app-icon__close-line app-icon__close-line--one" />
      <view class="app-icon__close-line app-icon__close-line--two" />
    </view>
    <view v-else-if="name === 'check'" class="app-icon__check">
      <view class="app-icon__check-arm app-icon__check-arm--short" />
      <view class="app-icon__check-arm app-icon__check-arm--long" />
    </view>
    <view v-else-if="name === 'calendar'" class="app-icon__calendar">
      <view class="app-icon__calendar-top" />
      <view class="app-icon__calendar-ring app-icon__calendar-ring--left" />
      <view class="app-icon__calendar-ring app-icon__calendar-ring--right" />
      <view class="app-icon__calendar-grid" />
    </view>
    <view v-else-if="name === 'notification'" class="app-icon__notification">
      <view class="app-icon__notification-bell" />
      <view class="app-icon__notification-clapper" />
      <view class="app-icon__notification-dot" />
    </view>
    <view v-else-if="name === 'trophy'" class="app-icon__trophy">
      <view class="app-icon__trophy-cup" />
      <view class="app-icon__trophy-handle app-icon__trophy-handle--left" />
      <view class="app-icon__trophy-handle app-icon__trophy-handle--right" />
      <view class="app-icon__trophy-stand" />
      <view class="app-icon__trophy-base" />
    </view>
    <view v-else-if="name === 'pull-up'" class="app-icon__exercise app-icon__exercise--pull">
      <view class="app-icon__bar" />
      <view class="app-icon__figure-head" />
      <view class="app-icon__figure-body" />
      <view class="app-icon__figure-arm app-icon__figure-arm--left" />
      <view class="app-icon__figure-arm app-icon__figure-arm--right" />
    </view>
    <view v-else-if="name === 'push-up'" class="app-icon__exercise app-icon__exercise--push">
      <view class="app-icon__push-body" />
      <view class="app-icon__push-arm app-icon__push-arm--left" />
      <view class="app-icon__push-arm app-icon__push-arm--right" />
    </view>
    <view v-else-if="name === 'sit-up'" class="app-icon__exercise app-icon__exercise--sit">
      <view class="app-icon__sit-body" />
      <view class="app-icon__sit-leg" />
      <view class="app-icon__sit-head" />
    </view>
    <view v-else class="app-icon__default" />
  </view>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  name: { type: String, default: 'default' },
  size: { type: [Number, String], default: 48 },
  tone: { type: String, default: 'brand' }
});

const rootStyle = computed(() => {
  const value = typeof props.size === 'number' ? `${props.size}rpx` : props.size;
  return {
    width: value,
    height: value
  };
});
</script>

<style scoped>
.app-icon {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #20C997;
}
.app-icon--white { color: #fff; }
.app-icon--muted { color: #7A8B9A; }
.app-icon--danger { color: #FF6B6B; }
.app-icon--warning { color: #FF9F43; }

.app-icon__bot {
  position: relative;
  width: 78%;
  height: 64%;
  border: 4rpx solid currentColor;
  border-radius: 16rpx;
}
.app-icon__bot-stem {
  position: absolute;
  top: -14rpx;
  left: 50%;
  width: 4rpx;
  height: 12rpx;
  background: currentColor;
  transform: translateX(-50%);
}
.app-icon__bot-eye {
  position: absolute;
  top: 28%;
  width: 9rpx;
  height: 9rpx;
  border-radius: 50%;
  background: currentColor;
}
.app-icon__bot-eye--left { left: 26%; }
.app-icon__bot-eye--right { right: 26%; }
.app-icon__bot-mouth {
  position: absolute;
  left: 30%;
  right: 30%;
  bottom: 24%;
  height: 4rpx;
  border-radius: 999rpx;
  background: currentColor;
}
.app-icon__user-head {
  width: 34%;
  height: 34%;
  border-radius: 50%;
  background: currentColor;
}
.app-icon__user-body {
  position: absolute;
  bottom: 14%;
  width: 62%;
  height: 32%;
  border-radius: 999rpx 999rpx 12rpx 12rpx;
  background: currentColor;
}
.app-icon__bulb-core {
  width: 52%;
  height: 58%;
  border: 4rpx solid currentColor;
  border-radius: 50% 50% 44% 44%;
}
.app-icon__bulb-base {
  position: absolute;
  bottom: 14%;
  width: 30%;
  height: 12%;
  border-radius: 4rpx;
  background: currentColor;
}
.app-icon__run-head {
  position: absolute;
  top: 12%;
  right: 28%;
  width: 18%;
  height: 18%;
  border-radius: 50%;
  background: currentColor;
}
.app-icon__run-body,
.app-icon__run-arm,
.app-icon__run-leg {
  position: absolute;
  height: 6rpx;
  border-radius: 999rpx;
  background: currentColor;
  transform-origin: center;
}
.app-icon__run-body { top: 42%; left: 34%; width: 34%; transform: rotate(-52deg); }
.app-icon__run-arm--front { top: 44%; left: 48%; width: 28%; transform: rotate(28deg); }
.app-icon__run-arm--back { top: 44%; left: 25%; width: 26%; transform: rotate(-26deg); }
.app-icon__run-leg--front { top: 66%; left: 47%; width: 34%; transform: rotate(-28deg); }
.app-icon__run-leg--back { top: 66%; left: 24%; width: 34%; transform: rotate(42deg); }
.app-icon__chart {
  position: relative;
  width: 72%;
  height: 66%;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}
.app-icon__chart-bar {
  width: 24%;
  border-radius: 999rpx 999rpx 4rpx 4rpx;
  background: currentColor;
}
.app-icon__chart-bar--one { height: 42%; opacity: .55; }
.app-icon__chart-bar--two { height: 70%; opacity: .8; }
.app-icon__chart-bar--three { height: 100%; }
.app-icon__lock-shackle {
  position: absolute;
  top: 13%;
  width: 44%;
  height: 38%;
  border: 5rpx solid currentColor;
  border-bottom: 0;
  border-radius: 999rpx 999rpx 0 0;
}
.app-icon__lock-shackle--open {
  transform: translateX(14%) rotate(18deg);
}
.app-icon__lock-body {
  position: absolute;
  bottom: 18%;
  width: 62%;
  height: 44%;
  border-radius: 10rpx;
  background: currentColor;
}
.app-icon__play {
  width: 0;
  height: 0;
  border-top: 17rpx solid transparent;
  border-bottom: 17rpx solid transparent;
  border-left: 25rpx solid currentColor;
  margin-left: 6rpx;
}
.app-icon__pause {
  display: flex;
  gap: 9rpx;
}
.app-icon__pause-bar {
  width: 10rpx;
  height: 34rpx;
  border-radius: 999rpx;
  background: currentColor;
}
.app-icon__pin {
  width: 52%;
  height: 66%;
  border-radius: 50% 50% 50% 0;
  background: currentColor;
  transform: rotate(-45deg);
}
.app-icon__pin-dot {
  position: absolute;
  top: 31%;
  left: 31%;
  width: 38%;
  height: 38%;
  border-radius: 50%;
  background: #fff;
}
.app-icon__camera {
  position: relative;
  width: 72%;
  height: 52%;
  border-radius: 10rpx;
  border: 4rpx solid currentColor;
}
.app-icon__camera-top {
  position: absolute;
  top: -11rpx;
  left: 16%;
  width: 28%;
  height: 10rpx;
  border-radius: 6rpx 6rpx 0 0;
  background: currentColor;
}
.app-icon__camera-lens {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 28%;
  height: 38%;
  border: 4rpx solid currentColor;
  border-radius: 50%;
  transform: translate(-50%, -50%);
}
.app-icon__edit {
  position: relative;
  width: 64%;
  height: 64%;
  transform: rotate(-42deg);
}
.app-icon__edit-line {
  position: absolute;
  left: 20%;
  top: 0;
  width: 18%;
  height: 80%;
  border-radius: 999rpx 999rpx 4rpx 4rpx;
  background: currentColor;
}
.app-icon__edit-tip {
  position: absolute;
  left: 20%;
  bottom: -8rpx;
  width: 18%;
  height: 9rpx;
  border-radius: 0 0 999rpx 999rpx;
  background: currentColor;
}
.app-icon__close {
  position: relative;
  width: 62%;
  height: 62%;
}
.app-icon__close-line {
  position: absolute;
  top: 50%;
  left: 0;
  width: 100%;
  height: 5rpx;
  border-radius: 999rpx;
  background: currentColor;
}
.app-icon__close-line--one { transform: rotate(45deg); }
.app-icon__close-line--two { transform: rotate(-45deg); }
.app-icon__check {
  position: relative;
  width: 64%;
  height: 64%;
  transform: rotate(-6deg);
}
.app-icon__check-arm {
  position: absolute;
  border-radius: 999rpx;
  background: currentColor;
  transform-origin: left center;
}
.app-icon__check-arm--short {
  left: 14%;
  top: 56%;
  width: 28%;
  height: 5rpx;
  transform: rotate(42deg);
}
.app-icon__check-arm--long {
  left: 34%;
  top: 46%;
  width: 42%;
  height: 5rpx;
  transform: rotate(-45deg);
}
.app-icon__calendar {
  position: relative;
  width: 74%;
  height: 72%;
  border: 4rpx solid currentColor;
  border-radius: 12rpx;
  overflow: hidden;
}
.app-icon__calendar-top {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 24%;
  background: currentColor;
}
.app-icon__calendar-ring {
  position: absolute;
  top: 8%;
  width: 8rpx;
  height: 12rpx;
  border-radius: 999rpx;
  background: #fff;
}
.app-icon__calendar-ring--left { left: 24%; }
.app-icon__calendar-ring--right { right: 24%; }
.app-icon__calendar-grid {
  position: absolute;
  left: 18%;
  right: 18%;
  top: 42%;
  height: 24%;
  border-top: 4rpx solid currentColor;
  border-left: 4rpx solid currentColor;
  box-shadow:
    0 0 0 0 currentColor,
    18rpx 0 0 0 transparent,
    36rpx 0 0 0 transparent;
}
.app-icon__notification {
  position: relative;
  width: 72%;
  height: 72%;
}
.app-icon__notification-bell {
  position: absolute;
  left: 18%;
  top: 12%;
  width: 64%;
  height: 62%;
  border: 4rpx solid currentColor;
  border-bottom-width: 5rpx;
  border-radius: 50% 50% 38% 38%;
}
.app-icon__notification-clapper {
  position: absolute;
  left: 42%;
  bottom: 10%;
  width: 16%;
  height: 10%;
  border-radius: 999rpx;
  background: currentColor;
}
.app-icon__notification-dot {
  position: absolute;
  right: 8%;
  top: 8%;
  width: 12%;
  height: 12%;
  border-radius: 50%;
  background: #FF6B6B;
  box-shadow: 0 0 0 3rpx #fff;
}
.app-icon__trophy {
  position: relative;
  width: 76%;
  height: 74%;
}
.app-icon__trophy-cup {
  position: absolute;
  left: 20%;
  top: 14%;
  width: 60%;
  height: 40%;
  border: 4rpx solid currentColor;
  border-bottom: 0;
  border-radius: 16rpx 16rpx 8rpx 8rpx;
}
.app-icon__trophy-handle {
  position: absolute;
  top: 22%;
  width: 18%;
  height: 14%;
  border: 4rpx solid currentColor;
  border-top: 0;
  border-bottom: 0;
}
.app-icon__trophy-handle--left {
  left: 4%;
  border-right: 0;
  border-radius: 999rpx 0 0 999rpx;
}
.app-icon__trophy-handle--right {
  right: 4%;
  border-left: 0;
  border-radius: 0 999rpx 999rpx 0;
}
.app-icon__trophy-stand {
  position: absolute;
  left: 42%;
  top: 54%;
  width: 16%;
  height: 18%;
  border-radius: 0 0 8rpx 8rpx;
  background: currentColor;
}
.app-icon__trophy-base {
  position: absolute;
  left: 28%;
  bottom: 8%;
  width: 44%;
  height: 10%;
  border-radius: 999rpx;
  background: currentColor;
}
.app-icon__bar {
  position: absolute;
  top: 16%;
  width: 72%;
  height: 5rpx;
  border-radius: 999rpx;
  background: currentColor;
}
.app-icon__figure-head {
  position: absolute;
  top: 34%;
  width: 16%;
  height: 16%;
  border-radius: 50%;
  background: currentColor;
}
.app-icon__figure-body {
  position: absolute;
  top: 50%;
  width: 6rpx;
  height: 30%;
  border-radius: 999rpx;
  background: currentColor;
}
.app-icon__figure-arm {
  position: absolute;
  top: 30%;
  width: 30%;
  height: 5rpx;
  border-radius: 999rpx;
  background: currentColor;
}
.app-icon__figure-arm--left { left: 22%; transform: rotate(-38deg); }
.app-icon__figure-arm--right { right: 22%; transform: rotate(38deg); }
.app-icon__push-body,
.app-icon__push-arm {
  position: absolute;
  height: 6rpx;
  border-radius: 999rpx;
  background: currentColor;
}
.app-icon__push-body { top: 48%; width: 72%; transform: rotate(7deg); }
.app-icon__push-arm--left { top: 58%; left: 28%; width: 26%; transform: rotate(75deg); }
.app-icon__push-arm--right { top: 58%; right: 20%; width: 24%; transform: rotate(75deg); }
.app-icon__sit-body,
.app-icon__sit-leg {
  position: absolute;
  height: 6rpx;
  border-radius: 999rpx;
  background: currentColor;
}
.app-icon__sit-body { top: 48%; left: 25%; width: 40%; transform: rotate(-42deg); }
.app-icon__sit-leg { top: 66%; left: 42%; width: 42%; transform: rotate(10deg); }
.app-icon__sit-head {
  position: absolute;
  top: 25%;
  left: 23%;
  width: 16%;
  height: 16%;
  border-radius: 50%;
  background: currentColor;
}
.app-icon__default {
  width: 52%;
  height: 52%;
  border-radius: 50%;
  background: currentColor;
}
</style>
