import axios from 'axios'

const BASE_URL = ''

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
export const getDashboardStats = () => api.get('/manage/dashboard/stats')
export const getMajors = () => api.get('/common/majors')
export const getClasses = () => api.get('/manage/classes')
export const createClass = (data) => api.post('/manage/classes', data)
export const patchClass = (id, data) => api.patch(`/manage/classes/${id}`, data)
export const deleteClass = (id) => api.delete(`/manage/classes/${id}`)
export const getUsers = (params) => api.get('/manage/users', { params })
export const getStudentActivities = (userId, params) =>
  api.get(`/manage/users/${userId}/activities`, { params })
export const createUser = (data, p) => api.post('/manage/users', data, { params: p })
export const importStudents = (file) => {
  const f = new FormData(); f.append('file', file)
  return api.post('/manage/import/students', f, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export const importTeachers = (file) => {
  const f = new FormData(); f.append('file', file)
  return api.post('/manage/import/teachers', f, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export const importProfiles = (file) => {
  const f = new FormData(); f.append('file', file)
  return api.post('/manage/import/profiles', f, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export const getSunshineClassStats = () => api.get('/manage/sunshine/class-stats')
export const getUserMajors = () => api.get('/manage/users/majors')
export const deleteUser = (id) => api.delete(`/manage/users/${id}`)
export const resetPassword = (id) => api.post(`/manage/users/${id}/reset-password`)
export const getTeacherSubjects = (id) => api.get(`/manage/teacher-subjects/${id}`)
export const updateTeacherSubjects = (id, data) => api.post(`/manage/teacher-subjects/${id}`, data)
export const getTeacherBoundStudents = (teacherId) =>
  api.get(`/manage/teachers/${teacherId}/bound-students`)
export const addTeacherBoundStudents = (teacherId, data) =>
  api.post(`/manage/teachers/${teacherId}/bound-students`, data)
export const removeTeacherBoundStudent = (teacherId, studentUserId) =>
  api.delete(`/manage/teachers/${teacherId}/bound-students/${studentUserId}`)

export const getSubjects = () => api.get('/manage/subjects')
export const createSubject = (data) => api.post('/manage/subjects', data)
export const deleteSubject = (id) => api.delete(`/manage/subjects/${id}`)

export default api
