<template>
  <div class="login-wrap">
    <el-card class="login-card">
      <div class="logo">🏫 校园管理系统</div>
      <div class="subtitle">管理员登录</div>
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="form.phone" placeholder="手机号" prefix-icon="Phone" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" size="large" show-password />
        </el-form-item>
        <el-button type="primary" native-type="submit" size="large" style="width:100%" :loading="loading">登录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/index.js'
import { ElMessage } from 'element-plus'

const router = useRouter()
const form = ref({ phone: '', password: '' })
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  try {
    const res = await login(form.value)
    localStorage.setItem('admin_token', res.access_token)
    localStorage.setItem('admin_info', JSON.stringify({ name: res.name, role: res.role }))
    router.push('/')
  } catch (e) {
    ElMessage.error(e?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap { display:flex; justify-content:center; align-items:center; height:100vh; background:#f0f2f5; }
.login-card { width:400px; padding:20px; }
.logo { font-size:28px; text-align:center; margin-bottom:8px; }
.subtitle { text-align:center; color:#666; margin-bottom:24px; font-size:16px; }
</style>
