// 基础配置
// 默认指向服务器后端；可通过 fronted/.env.* 的 VITE_API_BASE_URL 覆盖
const FALLBACK_BASE_URL = 'http://localhost:8080';
let baseUrl = FALLBACK_BASE_URL;

// uni-app(vite) 会在构建期注入 import.meta.env
try {
  // eslint-disable-next-line no-undef
  const envBase = import.meta?.env?.VITE_API_BASE_URL;
  if (envBase) baseUrl = envBase;
} catch (e) {
  // ignore
}

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
          const isLoginRequest = (options.url || '').indexOf('/auth/login') !== -1;
          if (isLoginRequest) {
            // 登录接口 401 = 账号或密码错误，交给登录页显示
            const msg = (res.data && res.data.detail) ? res.data.detail : '用户名或密码错误';
            reject({ type: 'server', statusCode: 401, message: msg, data: res.data });
          } else {
            // 其他接口 401 = Token 失效
            uni.removeStorageSync('token');
            uni.removeStorageSync('userInfo');
            uni.removeStorageSync('userRole');
            uni.showToast({
              title: '登录已过期，请重新登录',
              icon: 'none'
            });
            setTimeout(() => {
              uni.reLaunch({
                url: '/pages/login/login'
              });
            }, 1500);
            reject({ type: 'auth', message: '登录已过期', data: res.data });
          }
        } else {
          // 其他错误 - 不在这里显示toast，让调用方处理
          const errorMessage = res.data.detail || res.data.message || '请求失败';
          reject({ type: 'server', statusCode: res.statusCode, message: errorMessage, data: res.data });
        }
      },
      fail: (err) => {
        console.error('Request fail:', err);
        reject({ type: 'network', message: '网络连接失败', error: err });
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

// 文件上传
export const uploadFile = (filePath, fileType = 'image') => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token');
    
    uni.uploadFile({
      url: `${BASE_URL}/upload/file`,
      filePath: filePath,
      name: 'file',
      header: {
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            const data = JSON.parse(res.data);
            resolve(data);
          } catch (e) {
            resolve(res.data);
          }
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
          reject(res);
        } else {
          let errorMsg = '上传失败';
          try {
            const errorData = JSON.parse(res.data);
            errorMsg = errorData.detail || errorMsg;
          } catch (e) {
            // 解析失败，使用默认错误信息
          }
          uni.showToast({
            title: errorMsg,
            icon: 'none'
          });
          reject(res);
        }
      },
      fail: (err) => {
        console.error('Upload fail:', err);
        uni.showToast({
          title: '上传失败',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
};

// 重新计算活动评分
export const recalculateScore = (data) => {
  return request({
    url: '/activity/score/recalc',
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

export const getTeacherWeeklyTrend = () => {
  return request({
    url: '/teacher/weekly-trend',
    method: 'GET'
  });
};

// Sunshine run stats
export const getSunshineStats = () => {
  return request({
    url: '/student/sunshine-stats',
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
  getTeacherWeeklyTrend,
  approveActivity,
  createTeacherTask,
  getTeacherTasks,
  getStudentTasks,
  getTeacherTaskDetail,
  getCheckpoints,
  checkIn
};


// Courses (Phase 4.2)
export const getCourses = (params) => {
  let queryString = '';
  if (params) {
    const queryParts = [];
    if (params.page) queryParts.push(`page=${params.page}`);
    if (params.size) queryParts.push(`size=${params.size}`);
    if (params.category) queryParts.push(`category=${params.category}`);
    if (queryParts.length > 0) queryString = `?${queryParts.join('&')}`;
  }
  return request({
    url: `/courses/${queryString}`,
    method: 'GET'
  });
};

export const getCourseDetail = (courseId) => {
  return request({
    url: `/courses/${courseId}`,
    method: 'GET'
  });
};

export const enrollCourse = (courseId) => {
  return request({
    url: `/courses/${courseId}/enroll`,
    method: 'POST'
  });
};

export const getMyCourses = () => {
  return request({
    url: '/courses/my/enrollments',
    method: 'GET'
  });
};

export const createCourse = (data) => {
  return request({
    url: '/courses/',
    method: 'POST',
    data
  });
};

export const updateCourse = (id, data) => {
  return request({
    url: `/courses/${id}`,
    method: 'PUT',
    data
  });
};

// Run Group APIs (跑团联盟)
export const createRunGroup = (data) => {
  return request({
    url: '/run-group/create',
    method: 'POST',
    data
  });
};

export const joinRunGroup = (groupId) => {
  return request({
    url: `/run-group/join?group_id=${groupId}`,
    method: 'POST'
  });
};

export const leaveRunGroup = () => {
  return request({
    url: '/run-group/leave',
    method: 'POST'
  });
};

export const getMyRunGroup = () => {
  return request({
    url: '/run-group/my',
    method: 'GET'
  });
};

export const getRunGroups = (params) => {
  let queryString = '';
  if (params) {
    const queryParts = [];
    if (params.page) queryParts.push(`page=${params.page}`);
    if (params.size) queryParts.push(`size=${params.size}`);
    if (queryParts.length > 0) queryString = `?${queryParts.join('&')}`;
  }
  return request({
    url: `/run-group/list${queryString}`,
    method: 'GET'
  });
};

export const getGroupMembers = (groupId, params) => {
  let queryString = '';
  if (params) {
    const queryParts = [];
    if (params.page) queryParts.push(`page=${params.page}`);
    if (params.size) queryParts.push(`size=${params.size}`);
    if (queryParts.length > 0) queryString = `?${queryParts.join('&')}`;
  }
  return request({
    url: `/run-group/members/${groupId}${queryString}`,
    method: 'GET'
  });
};

export const getGroupActivities = (groupId, params) => {
  let queryString = '';
  if (params) {
    const queryParts = [];
    if (params.page) queryParts.push(`page=${params.page}`);
    if (params.size) queryParts.push(`size=${params.size}`);
    if (params.status) queryParts.push(`status=${params.status}`);
    if (queryParts.length > 0) queryString = `?${queryParts.join('&')}`;
  }
  return request({
    url: `/run-group/activities/${groupId}${queryString}`,
    method: 'GET'
  });
};

export const createGroupActivity = (data) => {
  return request({
    url: '/run-group/activity/create',
    method: 'POST',
    data
  });
};

export const applyActivity = (activityId) => {
  return request({
    url: `/run-group/activity/apply?activity_id=${activityId}`,
    method: 'POST'
  });
};

export const cancelActivity = (activityId) => {
  return request({
    url: `/run-group/activity/cancel?activity_id=${activityId}`,
    method: 'POST'
  });
};

export const getActivityDetail = (activityId) => {
  return request({
    url: `/run-group/activity/${activityId}`,
    method: 'GET'
  });
};

export const getRunGroupRank = () => {
  return request({
    url: '/run-group/rank',
    method: 'GET'
  });
};

export const getRunGroupActivities = (params) => {
  let queryString = '';
  if (params) {
    const queryParts = [];
    if (params.page) queryParts.push(`page=${params.page}`);
    if (params.size) queryParts.push(`size=${params.size}`);
    if (params.status) queryParts.push(`status=${params.status}`);
    if (queryParts.length > 0) queryString = `?${queryParts.join('&')}`;
  }
  return request({
    url: `/run-group/activity/list${queryString}`,
    method: 'GET'
  });
};
