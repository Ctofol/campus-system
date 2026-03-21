<template>
  <div>
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6" v-for="item in stats" :key="item.label">
        <el-card shadow="hover">
          <div style="display:flex;align-items:center;gap:16px">
            <el-icon :size="40" :color="item.color"><component :is="item.icon" /></el-icon>
            <div>
              <div style="font-size:28px;font-weight:bold">{{ item.value }}</div>
              <div style="color:#666;font-size:14px">{{ item.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-card>
      <template #header>快捷操作</template>
      <el-space>
        <el-button type="primary" @click="$router.push('/classes')">班级管理</el-button>
        <el-button type="primary" @click="$router.push('/users')">账号管理</el-button>
        <el-button type="primary" @click="$router.push('/import')">批量导入</el-button>
      </el-space>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDashboardStats } from '../api/index.js'

const stats = ref([
  { label: '学生总数', value: 0, icon: 'UserFilled', color: '#409eff' },
  { label: '教师总数', value: 0, icon: 'Avatar', color: '#67c23a' },
  { label: '班级总数', value: 0, icon: 'School', color: '#e6a23c' },
  { label: '待审批', value: 0, icon: 'Bell', color: '#f56c6c' },
])

onMounted(async () => {
  try {
    const data = await getDashboardStats()
    stats.value[0].value = data.total_students
    stats.value[1].value = data.total_teachers
    stats.value[2].value = data.total_classes
    stats.value[3].value = data.pending_approvals
  } catch(e) {}
})
</script>
