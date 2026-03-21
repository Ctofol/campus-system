<template>
  <div class="sunshine-dashboard">
    <el-card class="title-card">
      <template #header>阳光跑 · 班级统计看板</template>
      <p style="color:#666;font-size:14px;margin:0">
        按班级聚合：总人数、总有效跑步次数、班级平均分（10-20-40 阶梯）；达标率 = 达到 20 次及格线人数/班级人数。
      </p>
    </el-card>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="14">
        <el-card>
          <template #header>班级达标率排行（20 次及格线人数占比）</template>
          <div ref="barRef" style="height:360px"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card>
          <template #header>专业活跃度对比（有效跑步次数）</template>
          <div ref="pieRef" style="height:360px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top:16px">
      <template #header>班级明细</template>
      <el-table :data="classStats" stripe border>
        <el-table-column prop="class_name" label="班级" width="160" />
        <el-table-column prop="total_count" label="总人数" width="100" align="right" />
        <el-table-column prop="total_valid_runs" label="总有效跑步次数" width="140" align="right" />
        <el-table-column prop="avg_score" label="班级平均分" width="120" align="right" />
        <el-table-column prop="passed_20_count" label="达标(≥20次)人数" width="130" align="right" />
        <el-table-column prop="pass_rate" label="达标率 %" width="100" align="right">
          <template #default="{ row }">{{ row.pass_rate }}%</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { getSunshineClassStats } from '../api/index.js'

const classStats = ref([])
const majorActivity = ref([])
const barRef = ref(null)
const pieRef = ref(null)
let barChart = null
let pieChart = null

const load = async () => {
  const data = await getSunshineClassStats()
  classStats.value = data.class_stats || []
  majorActivity.value = data.major_activity || []
  drawBar()
  drawPie()
}

function drawBar() {
  if (!barRef.value || !classStats.value.length) return
  if (barChart) barChart.dispose()
  barChart = echarts.init(barRef.value)
  const names = classStats.value.map((c) => c.class_name)
  const rates = classStats.value.map((c) => c.pass_rate)
  barChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '12%', right: '8%', bottom: '15%', top: '10%', containLabel: true },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: '达标率 %', max: 100, axisLabel: { formatter: '{value}%' } },
    series: [{ name: '达标率', type: 'bar', data: rates, itemStyle: { color: '#409eff' } }],
  })
}

function drawPie() {
  if (!pieRef.value) return
  const list = majorActivity.value.filter((m) => m.valid_runs > 0)
  if (!list.length) {
    if (pieChart) pieChart.dispose()
    pieChart = echarts.init(pieRef.value)
    pieChart.setOption({ title: { text: '暂无数据', left: 'center', top: 'center' } })
    return
  }
  if (pieChart) pieChart.dispose()
  pieChart = echarts.init(pieRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', right: 10, top: 'center' },
    series: [
      {
        name: '有效跑步次数',
        type: 'pie',
        radius: ['40%', '70%'],
        data: list.map((m) => ({ value: m.valid_runs, name: m.major })),
        emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.2)' } },
      },
    ],
  })
}

onMounted(load)
watch(classStats, drawBar, { deep: true })
watch(majorActivity, drawPie, { deep: true })
</script>

<style scoped>
.sunshine-dashboard .title-card { margin-bottom: 0; }
</style>
