<template>
  <cover-view class="tab-bar">
    <cover-view class="tab-bar-border"></cover-view>
    <cover-view v-for="(item, index) in list" :key="index" class="tab-bar-item" @click="switchTab(item)">
      <cover-image class="tab-icon" :src="selected === index ? item.selectedIconPath : item.iconPath"></cover-image>
      <cover-view class="tab-text" :style="{ color: selected === index ? selectedColor : color }">{{ item.text }}</cover-view>
    </cover-view>
  </cover-view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const props = defineProps({
  current: {
    type: String,
    default: ''
  }
});

const color = "#666666";
const selectedColor = "#20C997";
const role = ref('student');

const studentList = [
  { pagePath: "/pages/home/home", text: "首页", iconPath: "/static/tab/home.png", selectedIconPath: "/static/tab/home-active.png" },
  { pagePath: "/pages/run/run", text: "跑步", iconPath: "/static/tab/run.png", selectedIconPath: "/static/tab/run-active.png" },
  { pagePath: "/pages/test/test", text: "体测", iconPath: "/static/tab/test.png", selectedIconPath: "/static/tab/test-active.png" },
  { pagePath: "/pages/mine/mine", text: "我的", iconPath: "/static/tab/mine.png", selectedIconPath: "/static/tab/mine-active.png" }
];

const teacherList = [
  { pagePath: "/pages/teacher/home/home", text: "主页", iconPath: "/static/tab/home.png", selectedIconPath: "/static/tab/home-active.png" },
  { pagePath: "/pages/teacher/manage/manage", text: "管理", iconPath: "/static/tab/run.png", selectedIconPath: "/static/tab/run-active.png" }, // 暂用 run 图标
  { pagePath: "/pages/teacher/mine/mine", text: "我的", iconPath: "/static/tab/mine.png", selectedIconPath: "/static/tab/mine-active.png" }
];

onMounted(() => {
  const userRole = uni.getStorageSync('userRole') || 'student';
  role.value = userRole;
});

const list = computed(() => {
  return role.value === 'teacher' ? teacherList : studentList;
});

const selected = computed(() => {
  return list.value.findIndex(item => item.pagePath === props.current || props.current.startsWith(item.pagePath));
});

const switchTab = (item) => {
  const url = item.pagePath;
  if (url === props.current) return;
  
  uni.redirectTo({
    url
  });
};
</script>

<style scoped>
.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100rpx; /* Standard tab bar height */
  background: white;
  display: flex;
  padding-bottom: env(safe-area-inset-bottom);
  z-index: 99999;
}

.tab-bar-border {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 1px;
  background-color: rgba(0, 0, 0, 0.1);
  transform: scaleY(0.5);
}

.tab-bar-item {
  flex: 1;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}

.tab-icon {
  width: 50rpx;
  height: 50rpx;
  margin-bottom: 4rpx;
}

.tab-text {
  font-size: 20rpx;
}
</style>