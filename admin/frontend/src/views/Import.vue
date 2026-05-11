<template>
  <el-row :gutter="16">
    <el-col :span="8">
      <el-card>
        <template #header>仅导入学生档案</template>
        <p style="color:#666;font-size:14px;margin-bottom:16px">
          Excel 列：学号、姓名、性别、班级、专业；<b>选科</b>可选（体育专项）。「班级」为行政班名称；「专业」须与系统专业库一致或便于导入建库。仅建档案，不创建登录账号。
        </p>
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
        <p style="color:#666;font-size:14px;margin-bottom:16px">
          Excel 列：姓名、手机号、密码、学号、所属班级名称、专业/课程。「专业/课程」会创建或匹配一条 Major，并与「所属班级名称」组成唯一班级（同班名不同专业会分成两条班级记录）。
        </p>
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
import api, { importProfiles, importStudents, importTeachers } from '../api/index.js'
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

const TEMPLATE_PATHS = {
  profiles: '/manage/import/template/profiles',
  student: '/manage/import/template/students',
  teacher: '/manage/import/template/teachers'
}
const TEMPLATE_FILES = {
  profiles: 'profiles_import_template.xlsx',
  student: 'student_import_template.xlsx',
  teacher: 'teacher_import_template.xlsx'
}

const downloadTpl = async (type) => {
  try {
    const blob = await api.get(TEMPLATE_PATHS[type], { responseType: 'blob' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = TEMPLATE_FILES[type]
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error(e?.detail || '下载失败（请确认已登录）')
  }
}
</script>
