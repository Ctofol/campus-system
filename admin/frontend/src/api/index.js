import axios from 'axios'

// 管理端独立路由
// 生产环境通过 8090 端口访问，Nginx 代理 /admin-api/ 到 8001
const BASE_URL = 'http://101.33.210.169:8002'

const api = axios.create({ baseURL: BASE_URL })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('admin_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res.data,
  err => {
    if (err.response?.status === 401 || err.response?.status === 403) {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_info')
      window.location.hash = '#/login'
    }
    return Promise.reject(err.response?.data || err)
  }
)

export const login = (data) => api.post('/auth/login', data)
export const getDashboardStats = () => api.get('/admin/dashboard/stats')
export const getMajors = () => api.get('/common/majors')
export const getClasses = () => api.get('/admin/classes')
export const createClass = (data) => api.post('/admin/classes', data)
export const deleteClass = (id) => api.delete(`/admin/classes/${id}`)
export const getUsers = (params) => api.get('/admin/users', { params })
export const createUser = (data, p) => api.post('/admin/users', data, { params: p })
export const importStudents = (file) => {
  const f = new FormData(); f.append('file', file)
  return api.post('/admin/import/students', f, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export const importTeachers = (file) => {
  const f = new FormData(); f.append('file', file)
  return api.post('/admin/import/teachers', f, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export const importProfiles = (file) => {
  const f = new FormData(); f.append('file', file)
  return api.post('/admin/import/profiles', f, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export const getSunshineClassStats = () => api.get('/admin/sunshine/class-stats')
export const getUserMajors = () => api.get('/admin/users/majors')
export const deleteUser = (id) => api.delete(`/admin/users/${id}`)
export const resetPassword = (id) => api.post(`/admin/users/${id}/reset-password`)
export const getTeacherSubjects = (id) => api.get(`/admin/teacher-subjects/${id}`)
export const updateTeacherSubjects = (id, data) => api.post(`/admin/teacher-subjects/${id}`, data)
export const downloadProfilesTemplate = () => window.open(`${BASE_URL}/import/template/profiles`)
export const downloadStudentTemplate = () => window.open(`${BASE_URL}/import/template/students`)
export const downloadTeacherTemplate = () => window.open(`${BASE_URL}/import/template/teachers`)

export default api
