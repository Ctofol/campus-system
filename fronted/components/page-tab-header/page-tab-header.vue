<template>
  <view>
    <view
      class="page-tab-header"
      :class="[
        `page-tab-header--${theme}`,
        { 'page-tab-header--fixed': fixed }
      ]"
      :style="headerStyle"
    >
      <view class="page-tab-header__status" :style="statusBarStyle"></view>
      <view class="page-tab-header__bar" :style="barStyle">
        <view class="page-tab-header__side page-tab-header__side--left">
          <view v-if="showBack" class="page-tab-header__back" @click="handleBack">
            <text class="page-tab-header__back-icon">‹</text>
          </view>
        </view>
        <view class="page-tab-header__center">
          <text class="page-tab-header__title">{{ title }}</text>
        </view>
        <view class="page-tab-header__side page-tab-header__side--right">
          <view v-if="hasRightSlot" class="page-tab-header__right">
            <slot name="right" />
          </view>
        </view>
      </view>
    </view>
    <view
      v-if="fixed && placeholder"
      class="page-tab-header__placeholder"
      :style="placeholderStyle"
    ></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, useSlots } from 'vue';

const props = defineProps({
  title: { type: String, default: '' },
  /** light | brand | white | transparent | dark */
  theme: { type: String, default: 'light' },
  showBack: { type: Boolean, default: false },
  /** 自定义返回逻辑（设置后不再自动 navigateBack） */
  backHandler: { type: Function, default: null },
  fixed: { type: Boolean, default: true },
  placeholder: { type: Boolean, default: true }
});

const emit = defineEmits(['back']);
const slots = useSlots();
const hasRightSlot = computed(() => !!slots.right);

const statusBarHeight = ref(20);
const navBarHeight = ref(44);
/** 右侧留白，避免与微信小程序胶囊重叠 */
const capsuleSafeRightPx = ref(12);

const initNavLayout = () => {
  try {
    const sys = uni.getSystemInfoSync();
    const sb = sys.statusBarHeight || 20;
    statusBarHeight.value = sb;
    let barH = 44;
    let safeRight = 12;

    // #ifdef MP-WEIXIN
    const menu = typeof uni.getMenuButtonBoundingClientRect === 'function'
      ? uni.getMenuButtonBoundingClientRect()
      : null;
    if (menu && menu.width && menu.top != null) {
      barH = Math.max(44, (menu.top - sb) * 2 + menu.height);
      safeRight = Math.max(12, (sys.windowWidth || 375) - menu.left + 8);
    }
    // #endif

    navBarHeight.value = barH;
    capsuleSafeRightPx.value = safeRight;
  } catch (e) {
    statusBarHeight.value = 20;
    navBarHeight.value = 44;
    capsuleSafeRightPx.value = 12;
  }
};

initNavLayout();

const statusBarStyle = computed(() => ({
  height: `${statusBarHeight.value}px`
}));

const headerStyle = computed(() => ({
  '--nav-bar-height-px': `${navBarHeight.value}px`,
  '--capsule-safe-right': `${capsuleSafeRightPx.value}px`
}));

const barStyle = computed(() => ({
  height: `${navBarHeight.value}px`,
  paddingRight: `${capsuleSafeRightPx.value}px`,
  paddingLeft: 'var(--page-padding-x, 30rpx)'
}));

const placeholderStyle = computed(() => ({
  height: `${statusBarHeight.value + navBarHeight.value}px`
}));

const handleBack = () => {
  emit('back');
  if (props.backHandler) {
    props.backHandler();
    return;
  }
  uni.navigateBack({
    fail: () => {
      uni.switchTab({ url: '/pages/tab/home' });
    }
  });
};

onMounted(() => {
  initNavLayout();
});
</script>

<style lang="scss" scoped>
.page-tab-header {
  width: 100%;
  box-sizing: border-box;
}

.page-tab-header--fixed {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.page-tab-header--light {
  background-color: var(--page-bg, #f5f7fa);
}

.page-tab-header--brand {
  background-color: var(--color-brand, #20c997);
}

.page-tab-header--white {
  background-color: #fff;
  border-bottom: 1rpx solid #eee;
}

.page-tab-header--transparent {
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.45) 0%, rgba(0, 0, 0, 0) 100%);
}

.page-tab-header--transparent .page-tab-header__title,
.page-tab-header--transparent .page-tab-header__back-icon {
  color: #fff;
}

.page-tab-header--dark {
  background-color: #1a1a1a;
}

.page-tab-header--dark .page-tab-header__title,
.page-tab-header--dark .page-tab-header__back-icon {
  color: #fff;
}

.page-tab-header__bar {
  position: relative;
  height: var(--nav-bar-height-px, var(--nav-bar-height, 44px));
  display: grid;
  grid-template-columns: 1fr minmax(0, auto) 1fr;
  align-items: center;
  column-gap: 12rpx;
  box-sizing: border-box;
}

.page-tab-header__side {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  min-width: 0;
  height: 100%;
}

.page-tab-header__side--left {
  justify-content: flex-start;
  padding-right: 8rpx;
}

.page-tab-header__side--right {
  justify-content: flex-end;
  padding-left: 8rpx;
}

.page-tab-header__center {
  grid-column: 2;
  min-width: 0;
  max-width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.page-tab-header__back {
  width: 64rpx;
  height: 64rpx;
  margin-left: -16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
}

.page-tab-header__back-icon {
  font-size: 48rpx;
  line-height: 1;
  font-weight: 300;
}

.page-tab-header--light .page-tab-header__back-icon,
.page-tab-header--white .page-tab-header__back-icon {
  color: #333;
}

.page-tab-header--brand .page-tab-header__back-icon {
  color: #fff;
}

.page-tab-header__title {
  max-width: 100%;
  font-size: var(--nav-title-size, 34rpx);
  font-weight: bold;
  line-height: 1.2;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.page-tab-header--light .page-tab-header__title,
.page-tab-header--white .page-tab-header__title {
  color: #333;
}

.page-tab-header--brand .page-tab-header__title {
  color: #fff;
}

.page-tab-header__right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-shrink: 0;
  pointer-events: auto;
  max-width: 100%;
}

.page-tab-header__placeholder {
  width: 100%;
}
</style>
