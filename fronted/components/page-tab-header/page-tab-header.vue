<template>
  <view>
    <view
      class="page-tab-header"
      :class="[
        `page-tab-header--${theme}`,
        { 'page-tab-header--fixed': fixed }
      ]"
    >
      <view class="page-tab-header__status" :style="statusBarStyle"></view>
      <view class="page-tab-header__bar">
        <view v-if="showBack" class="page-tab-header__back" @click="handleBack">
          <text class="page-tab-header__back-icon">‹</text>
        </view>
        <text
          class="page-tab-header__title"
          :class="{ 'page-tab-header__title--with-back': showBack }"
        >{{ title }}</text>
        <view v-if="$slots.right" class="page-tab-header__right">
          <slot name="right" />
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
import { ref, computed, onMounted } from 'vue';

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

const statusBarHeight = ref(20);

const statusBarStyle = computed(() => ({
  height: `${statusBarHeight.value}px`
}));

const placeholderStyle = computed(() => ({
  height: `${statusBarHeight.value + 44}px`
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
  try {
    const sys = uni.getSystemInfoSync();
    statusBarHeight.value = sys.statusBarHeight || 20;
  } catch (e) {
    statusBarHeight.value = 20;
  }
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
  height: var(--nav-bar-height, 44px);
  display: flex;
  align-items: center;
  padding: 0 var(--page-padding-x, 30rpx);
  box-sizing: border-box;
}

.page-tab-header__back {
  width: 64rpx;
  height: 64rpx;
  margin-left: -16rpx;
  margin-right: 4rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
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
  font-size: var(--nav-title-size, 34rpx);
  font-weight: bold;
  line-height: 1.2;
  flex: 1;
  min-width: 0;
}

.page-tab-header__title--with-back {
  flex: 1;
}

.page-tab-header--light .page-tab-header__title,
.page-tab-header--white .page-tab-header__title {
  color: #333;
}

.page-tab-header--brand .page-tab-header__title {
  color: #fff;
}

.page-tab-header__right {
  margin-left: auto;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.page-tab-header__placeholder {
  width: 100%;
}
</style>
