<template>
  <view class="page">
    <!-- 顶部班级选择与统计概览 -->
    <view class="header">
      <view class="role-badge">教师端 · 班级排行</view>
      <picker
        mode="selector"
        :range="classOptions"
        range-key="label"
        @change="onClassChange"
      >
        <view class="picker">
          <text class="picker-label">当前范围：</text>
          <text class="picker-value">
            {{ currentClassLabel }}
          </text>
        </view>
      </picker>
      <view class="meta">
        <text>本页展示已绑定班级内学生的阳光跑积分排行。</text>
      </view>
    </view>

    <!-- 排行列表 -->
    <scroll-view class="list" scroll-y>
      <view
        v-for="(item, index) in rankedItems"
        :key="item.user_id || item.student_id || index"
        class="row"
        @click="goToStudentDetail(item)"
      >
        <view class="rank" :class="{ top: index < 3 }">
          <text v-if="index === 0">①</text>
          <text v-else-if="index === 1">②</text>
          <text v-else-if="index === 2">③</text>
          <text v-else>{{ index + 1 }}</text>
        </view>
        <view class="info">
          <view class="name-line">
            <text class="name">{{ item.name || '未命名' }}</text>
            <text class="id" v-if="item.student_id">学号 {{ item.student_id }}</text>
          </view>
          <view class="meta-line">
            <text class="class-name">{{ item.class_name || '未分班' }}</text>
            <text class="weekly">本周 {{ item.weekly_count || 0 }} 次</text>
          </view>
        </view>
        <view class="score-block">
          <text class="score">{{ item.total_score || 0 }}</text>
          <text class="score-label">积分</text>
        </view>
      </view>

      <view v-if="!loading && rankedItems.length === 0" class="empty">
        <text>暂无数据，请先为班级分配学生并完成阳光跑。</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { request } from '@/utils/request.js'

const loading = ref(false)
const items = ref([])

// 班级筛选（目前接口返回的是所有绑定班级学生，这里预留班级筛选能力）
const classOptions = ref([{ label: '全部班级', value: 'all' }])
const currentClassValue = ref('all')

const currentClassLabel = computed(() => {
  const found = classOptions.value.find(c => c.value === currentClassValue.value)
  return found ? found.label : '全部班级'
})

const rankedItems = computed(() => {
  let list = items.value || []
  if (currentClassValue.value !== 'all') {
    list = list.filter(i => i.class_name === currentClassValue.value)
  }
  // 后端已按 total_score 排序，这里兜底再排一次
  return [...list].sort((a, b) => (b.total_score || 0) - (a.total_score || 0))
})

const fetchData = async () => {
  if (!uni.getStorageSync('token')) {
    return
  }
  loading.value = true
  try {
    const res = await request({
      url: '/teacher/class-member-details',
      method: 'GET'
    })
    const list = Array.isArray(res?.items) ? res.items : []
    items.value = list

    // 构造班级选项
    const classSet = Array.from(
      new Set(list.map(i => i.class_name).filter(Boolean))
    )
    classOptions.value = [
      { label: '全部班级', value: 'all' },
      ...classSet.map(name => ({ label: name, value: name }))
    ]
    if (!classSet.includes(currentClassValue.value)) {
      currentClassValue.value = 'all'
    }
  } catch (e) {
    console.error('Failed to fetch class member details:', e)
    uni.showToast({
      title: '加载班级排行失败',
      icon: 'none'
    })
  } finally {
    loading.value = false
  }
}

const onClassChange = e => {
  const idx = Number(e.detail.value)
  const opt = classOptions.value[idx]
  if (opt) {
    currentClassValue.value = opt.value
  }
}

const goToStudentDetail = item => {
  // 仅 teacher 角色可访问，复用教师端学生详情
  const userRole = uni.getStorageSync('userRole')
  if (userRole !== 'teacher') {
    uni.showToast({ title: '仅教师可查看详情', icon: 'none' })
    return
  }
  const userId = item.user_id
  if (!userId) return
  uni.navigateTo({
    url: `/pages/teacher/students/detail?studentId=${userId}`
  })
}

onShow(() => {
  const role = uni.getStorageSync('userRole')
  if (role !== 'teacher') {
    uni.showToast({
      title: '仅教师可访问该页面',
      icon: 'none'
    })
    setTimeout(() => {
      uni.reLaunch({ url: '/pages/tab/home' })
    }, 1000)
    return
  }
  fetchData()
})
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fb;
}

.header {
  padding: 24rpx 32rpx 16rpx;
  background: #ffffff;
  box-shadow: 0 4rpx 12rpx rgba(15, 23, 42, 0.06);
}

.role-badge {
  display: inline-flex;
  padding: 4rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(32, 201, 151, 0.08);
  color: #20c997;
  font-size: 22rpx;
  margin-bottom: 12rpx;
}

.picker {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx 20rpx;
  border-radius: 999rpx;
  background: #f3f5f9;
}

.picker-label {
  font-size: 26rpx;
  color: #64748b;
}

.picker-value {
  font-size: 26rpx;
  color: #111827;
  font-weight: 600;
}

.meta {
  margin-top: 10rpx;
  font-size: 22rpx;
  color: #94a3b8;
}

.list {
  flex: 1;
  padding: 16rpx 24rpx 32rpx;
}

.row {
  display: flex;
  align-items: center;
  padding: 18rpx 20rpx;
  margin-bottom: 12rpx;
  border-radius: 20rpx;
  background: #ffffff;
  box-shadow: 0 4rpx 10rpx rgba(15, 23, 42, 0.04);
}

.rank {
  width: 60rpx;
  text-align: center;
  font-size: 28rpx;
  color: #64748b;
}

.rank.top {
  font-weight: 700;
  color: #f97316;
}

.info {
  flex: 1;
  margin: 0 12rpx;
}

.name-line {
  display: flex;
  align-items: baseline;
  gap: 12rpx;
}

.name {
  font-size: 30rpx;
  color: #0f172a;
  font-weight: 600;
}

.id {
  font-size: 22rpx;
  color: #94a3b8;
}

.meta-line {
  margin-top: 6rpx;
  display: flex;
  justify-content: space-between;
  font-size: 24rpx;
  color: #6b7280;
}

.class-name {
  max-width: 280rpx;
}

.weekly {
  color: #20c997;
}

.score-block {
  width: 120rpx;
  align-items: flex-end;
  justify-content: center;
  text-align: right;
}

.score {
  font-size: 34rpx;
  font-weight: 700;
  color: #111827;
}

.score-label {
  font-size: 22rpx;
  color: #9ca3af;
}

.empty {
  margin-top: 40rpx;
  text-align: center;
  font-size: 24rpx;
  color: #9ca3af;
}
</style>

