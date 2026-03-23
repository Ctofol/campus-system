<template>
  <div class="dashboard-container">
    <!-- 顶部四项核心指标 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6" v-for="item in stats" :key="item.label">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" :color="item.color"><component :is="item.icon" /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ item.value || 0 }}</div>
              <div class="stat-label">{{ item.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 中间图表层 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="14">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>班级达标率排行 (≥20次)</span>
              <el-tag size="small">阳光跑</el-tag>
            </div>
          </template>
          <div ref="barRef" style="height:320px"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card>
          <template #header>专业活跃度分布</template>
          <div ref="pieRef" style="height:320px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部详情与快捷操作 -->
    <el-row :gutter="16">
      <el-col :span="18">
        <el-card>
          <template #header>班级管理明细</template>
          <el-table :data="classStats" stripe height="300">
            <el-table-column prop="class_name" label="班级" width="150" />
            <el-table-column prop="total_count" label="人数" width="80" align="right" />
            <el-table-column prop="total_valid_runs" label="累计跑步" width="110" align="right" />
            <el-table-column prop="avg_score" label="平均分" width="100" align="right" />
            <el-table-column prop="pass_rate" label="达标率" align="right">
              <template #default="{ row }">
                <el-progress :percentage="row.pass_rate" :color="row.pass_rate > 80 ? '#67c23a' : '#409eff'" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card title="快捷操作">
          <template #header>快捷入口</template>
          <div class="shortcut-buttons">
            <el-button class="w-100" type="primary" plain @click="$router.push('/classes')">班级管理</el-button>
            <el-button class="w-100" type="success" plain @click="$router.push('/users')">账号管理</el-button>
            <el-button class="w-100" type="warning" plain @click="$router.push('/import')">数据导入</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getDashboardStats, getSunshineClassStats } from '../api/index.js'

// 核心指标
const stats = ref([
  { label: '学生总数', value: 0, icon: 'UserFilled', color: '#409eff' },
  { label: '教师总数', value: 0, icon: 'Avatar', color: '#67c23a' },
  { label: '班级总数', value: 0, icon: 'School', color: '#e6a23c' },
  { label: '待审批事项', value: 0, icon: 'Bell', color: '#f56c6c' },
])

// 阳光跑数据
const classStats = ref([])
const majorActivity = ref([])
const barRef = ref(null)
const pieRef = ref(null)
let barChart = null
let pieChart = null

const initCharts = () => {
  if (barRef.value) {
    barChart = echarts.init(barRef.value)
    const names = classStats.value.map(c => c.class_name)
    const rates = classStats.value.map(c => c.pass_rate)
    barChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: { type: 'category', data: names, axisLabel: { rotate: 25, fontSize: 10 } },
      yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
      series: [{ name: '达标率', type: 'bar', data: rates, itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] } }]
    })
  }

  if (pieRef.value) {
    pieChart = echarts.init(pieRef.value)
    const list = majorActivity.value.filter(m => m.valid_runs > 0)
    pieChart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        name: '活跃度',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        data: list.map(m => ({ value: m.valid_runs, name: m.major }))
      }]
    })
  }
}

onMounted(async () => {
  try {
    // 1. 获取基础统计
    const basicData = await getDashboardStats()
    stats.value[0].value = basicData.total_students
    stats.value[1].value = basicData.total_teachers
    stats.value[2].value = basicData.total_classes
    stats.value[3].value = basicData.pending_approvals

    // 2. 获取阳光跑统计
    const sunshineData = await getSunshineClassStats()
    classStats.value = sunshineData.class_stats || []
    majorActivity.value = sunshineData.major_activity || []

    // 渲染图表
    await nextTick()
    initCharts()
  } catch (e) {
    console.error('Fetch dashboard data failed', e)
  }
})
</script>

<style scoped>
.dashboard-container { padding: 4px; }
.stat-card { border: none; transition: transform 0.3s; }
.stat-card:hover { transform: translateY(-5px); }
.stat-content { display: flex; align-items: center; gap: 20px; }
.stat-value { font-size: 30px; font-weight: 800; line-height: 1.2; color: #303133; }
.stat-label { font-size: 14px; color: #909399; margin-top: 4px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.shortcut-buttons { display: flex; flex-direction: column; gap: 12px; }
.w-100 { width: 100%; margin-left: 0 !important; }
</style>
