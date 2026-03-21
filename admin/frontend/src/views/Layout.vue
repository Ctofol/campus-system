<template>
  <el-container style="height:100vh">
    <el-aside width="200px" style="background:#001529">
      <div class="logo">🏫 管理端</div>
      <el-menu router background-color="#001529" text-color="#ccc" active-text-color="#fff" :default-active="$route.path">
        <el-menu-item index="/dashboard"><el-icon><Odometer /></el-icon>控制台</el-menu-item>
        <el-menu-item index="/classes"><el-icon><School /></el-icon>班级管理</el-menu-item>
        <el-menu-item index="/users"><el-icon><User /></el-icon>账号管理</el-menu-item>
        <el-menu-item index="/sunshine"><el-icon><PieChart /></el-icon>阳光跑看板</el-menu-item>
        <el-menu-item index="/import"><el-icon><Upload /></el-icon>批量导入</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background:#fff;border-bottom:1px solid #eee;display:flex;align-items:center;justify-content:space-between;padding:0 20px">
        <span style="font-size:16px;font-weight:600">{{ $route.meta.title }}</span>
        <div style="display:flex;align-items:center;gap:12px">
          <span style="color:#666">{{ adminInfo.name }}</span>
          <el-button size="small" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main style="background:#f0f2f5">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const adminInfo = ref(JSON.parse(localStorage.getItem('admin_info') || '{"name":"管理员"}'))

const logout = () => {
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_info')
  router.push('/login')
}
</script>

<style scoped>
.logo { color:#fff; text-align:center; padding:20px 0; font-size:16px; font-weight:bold; border-bottom:1px solid #333; }
</style>
