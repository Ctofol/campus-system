<template>
  <el-row :gutter="16">
    <el-col :span="8">
      <el-card>
        <template #header>仅导入学生档案</template>
        <p style="color:#666;font-size:14px;margin-bottom:16px">Excel 列：学号、姓名、性别、班级、专业。仅建档案，不创建账号，用于「档案激活」注册。</p>
        <el-space direction="vertical" style="width:100%">
          <el-upload :before-upload="(f) => handleImport(f, 'profiles')" :show-file-list="false" accept=".xls,.xlsx">
            <el-button type="primary" :loading="loading.profiles">选择文件并导入档案</el-button>
          </el-upload>
          <el-button @click="downloadTpl('profiles')">下载档案模板</el-button>
        </el-space>
      </el-card>
    </el-col>
    <el-col :span="8">
      <el-card>
        <template #header>批量导入学生</template>
        <p style="color:#666;font-size:14px;margin-bottom:16px">Excel 列：姓名、手机号、密码、学号、所属班级名称、专业/课程</p>
        <el-space direction="vertical" style="width:100%">
          <el-upload :before-upload="(f) => handleImport(f, 'student')" :show-file-list="false" accept=".xls,.xlsx">
            <el-button type="primary" :loading="loading.student">选择文件并导入</el-button>
          </el-upload>
          <el-button @click="downloadTpl('student')">下载学生模板</el-button>
        </el-space>
      </el-card>
    </el-col>
    <el-col :span="8">
      <el-card>
        <template #header>批量导入教师</template>
        <p style="color:#666;font-size:14px;margin-bottom:16px">Excel 列：姓名、手机号、密码、工号</p>
        <el-space direction="vertical" style="width:100%">
          <el-upload :before-upload="(f) => handleImport(f, 'teacher')" :show-file-list="false" accept=".xls,.xlsx">
            <el-button type="primary" :loading="loading.teacher">选择文件并导入</el-button>
          </el-upload>
          <el-button @click="downloadTpl('teacher')">下载教师模板</el-button>
        </el-space>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref } from 'vue'
import { importProfiles, importStudents, importTeachers, downloadProfilesTemplate, downloadStudentTemplate, downloadTeacherTemplate } from '../api/index.js'
import { ElMessage } from 'element-plus'

const loading = ref({ student: false, teacher: false, profiles: false })

const handleImport = async (file, type) => {
  loading.value[type] = true
  try {
    const fn = type === 'profiles' ? importProfiles : type === 'student' ? importStudents : importTeachers
    const data = await fn(file)
    ElMessage.success(`导入完成：成功 ${data.success} 条，失败 ${data.failed} 条`)
  } catch (e) {
    ElMessage.error(e?.detail || '导入失败')
  } finally {
    loading.value[type] = false
  }
  return false
}

const downloadTpl = (type) => {
  const token = localStorage.getItem('admin_token')
  const url = type === 'profiles' ? downloadProfilesTemplate() : type === 'student' ? downloadStudentTemplate() : downloadTeacherTemplate()
  const a = document.createElement('a')
  a.href = url + (token ? '?token=' + token : '')
  a.click()
}
</script>
