// 基础配置
// 开发环境地址
let baseUrl = 'http://127.0.0.1:8000';

// #ifdef H5
try {
  const proto = location && location.protocol ? location.protocol : 'http:';
  const host = location && location.hostname ? location.hostname : 'localhost';
  baseUrl = `${proto}//${host}:8000`;
} catch (e) {
  baseUrl = 'http://127.0.0.1:8000';
}
// #endif

// #ifndef H5
// 真机调试地址（请修改为你电脑/服务器的真实IP）
baseUrl = 'http://192.168.0.210:8000'; 
// 改为远程服务器地址，以便在不启动本地后端时也能使用
// baseUrl = 'http://120.26.17.147:8000';
// #endif

// --- 服务器生产环境配置 ---
baseUrl = 'http://120.26.17.147:8000';
// --------------------------------------------------------

export const BASE_URL = baseUrl;

// 请求封装
export const request = (...args) => {
  let options = {};
  if (typeof args[0] === 'string') {
    options = { url: args[0], ...args[1] };
  } else {
    options = args[0] || {};
  }
  
  return new Promise((resolve, reject) => {
    // 获取 Token
    const token = uni.getStorageSync('token');
    
    // 组装 Header
    const header = {
      'Content-Type': 'application/json',
      ...(options.header || {})
    };
    
    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }

    uni.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data || {},
      header: header,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          // Token 失效，跳转登录
          uni.removeStorageSync('token');
          uni.removeStorageSync('userInfo');
          uni.showToast({
            title: '登录已过期，请重新登录',
            icon: 'none'
          });
          setTimeout(() => {
            uni.reLaunch({
              url: '/pages/login/login'
            });
          }, 1500);
          reject(res.data);
        } else {
          // 其他错误
          uni.showToast({
            title: res.data.detail || '请求失败',
            icon: 'none'
          });
          reject(res.data);
        }
      },
      fail: (err) => {
        console.error('Request fail:', err);
        uni.showModal({
            title: '网络请求失败',
            content: err.errMsg || JSON.stringify(err),
            showCancel: false
        });
        reject(err);
      }
    });
  });
};

// API 接口定义

// Auth
export const login = (data) => {
  return request({
    url: '/auth/login',
    method: 'POST',
    data
  });
};

export const register = (data) => {
  return request({
    url: '/auth/register',
    method: 'POST',
    data
  });
};

// Activity
export const submitActivity = (data) => {
  return request({
    url: '/activity/finish',
    method: 'POST',
    data
  });
};

export const getActivityHistory = (params) => {
  // params: { page, size }
  let queryString = '';
  if (params) {
    queryString = `?page=${params.page}&size=${params.size}`;
  }
  return request({
    url: `/activity/history${queryString}`,
    method: 'GET'
  });
};

// Teacher
export const getTeacherActivities = (params) => {
  let queryString = '';
  if (params) {
    queryString = `?page=${params.page}&size=${params.size}`;
  }
  return request({
    url: `/teacher/activities${queryString}`,
    method: 'GET'
  });
};

export const approveActivity = (activityId) => {
  return request({
    url: `/teacher/activity/${activityId}/approve`,
    method: 'POST'
  });
};

export const createTeacherTask = (data) => {
  return request({
    url: '/teacher/tasks',
    method: 'POST',
    data
  });
};

export const deleteTask = (taskId) => {
  return request({
    url: `/teacher/tasks/${taskId}`,
    method: 'DELETE'
  });
};

export const getTeacherTasks = (params) => {
  let queryString = '';
  if (params) {
    const queryParts = [];
    if (params.page) queryParts.push(`page=${params.page}`);
    if (params.size) queryParts.push(`size=${params.size}`);
    if (params.status) queryParts.push(`status=${params.status}`);
    if (queryParts.length > 0) queryString = `?${queryParts.join('&')}`;
  }
  return request({
    url: `/teacher/tasks${queryString}`,
    method: 'GET'
  });
};

export const getStudentTasks = (params) => {
  let queryString = '';
  if (params) {
    const queryParts = [];
    if (params.page) queryParts.push(`page=${params.page}`);
    if (params.size) queryParts.push(`size=${params.size}`);
    if (params.status) queryParts.push(`status=${params.status}`);
    if (queryParts.length > 0) queryString = `?${queryParts.join('&')}`;
  }
  return request({
    url: `/student/tasks${queryString}`,
    method: 'GET'
  });
};

export const getTeacherStudentActivities = (studentId, params) => {
  return request({
    url: `/teacher/student/${studentId}/activities`,
    method: 'GET',
    data: params
  });
};

export const getTeacherTaskDetail = (taskId) => {
  return request({
    url: `/teacher/tasks/${taskId}`,
    method: 'GET'
  });
};

export const getCheckpoints = () => {
  return request({
    url: '/checkpoints',
    method: 'GET'
  });
};

export const checkIn = (data) => {
  return request({
    url: '/activity/checkin',
    method: 'POST',
    data
  });
};

export const getTeacherDashboardStats = () => {
  return request({
    url: '/teacher/dashboard/stats',
    method: 'GET'
  });
};

export default {
  login,
  register,
  submitActivity,
  getActivityHistory,
  getTeacherActivities,
  getTeacherDashboardStats,
  approveActivity,
  createTeacherTask,
  getTeacherTasks,
  getStudentTasks,
  getTeacherTaskDetail,
  getCheckpoints,
  checkIn
};
