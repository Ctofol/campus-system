import axios from 'axios'

const BASE_URL = 'http://101.37.24.171:8001'

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
      window.location.href = '/#/login'
    }
    return Promise.reject(err.response?.data || err)
  }
)

export const login = (data) => api.post('/auth/login', data)
export const refreshToken = () => api.post('/auth/refresh')
export const getDashboardStats = () => api.get('/admin/dashboard/stats')
export const getClasses = () => api.get('/admin/classes')
export const createClass = (data) => api.post('/admin/classes', data)
export const deleteClass = (id) => api.delete(`/admin/classes/${id}`)
export const getUsers = (params) => api.get('/admin/users', { params })
export const createUser = (data, params) => api.post('/admin/users', data, { params })
export const deleteUser = (id) => api.delete(`/admin/users/${id}`)
export const resetPassword = (id) => api.post(`/admin/users/${id}/reset-password`)
export const importStudents = (file) => {
  const form = new FormData(); form.append('file', file)
  return api.post('/admin/import/students', form, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export const importTeachers = (file) => {
  const form = new FormData(); form.append('file', file)
  return api.post('/admin/import/teachers', form, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export const downloadStudentTemplate = () => `${BASE_URL}/admin/import/template/students`
export const downloadTeacherTemplate = () => `${BASE_URL}/admin/import/template/teachers`
