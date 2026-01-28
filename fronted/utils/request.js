// 基础配置
const BASE_URL = 'http://127.0.0.1:8000'; // 开发环境地址，真机调试请换成局域网IP

// 请求封装
const request = (options) => {
  return new Promise((resolve, reject) => {
    // 获取 Token
    const token = uni.getStorageSync('token');
    
    // 组装 Header
    const header = {
      'Content-Type': 'application/json',
      ...options.header
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
        uni.showToast({
          title: '网络请求失败',
          icon: 'none'
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
    queryString = `?page=${params.page}&size=${params.size}`;
  }
  return request({
    url: `/teacher/tasks${queryString}`,
    method: 'GET'
  });
};

export const getStudentTasks = (params) => {
  let queryString = '';
  if (params) {
    queryString = `?page=${params.page}&size=${params.size}`;
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

export default {
  login,
  register,
  submitActivity,
  getActivityHistory,
  getTeacherActivities,
  approveActivity,
  createTeacherTask,
  getTeacherTasks,
  getStudentTasks,
  getTeacherTaskDetail
};
