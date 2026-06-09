// 生产：须与 nginx `location /api/` 一致（BASE_URL 含 /api，请求 path 为 /student/...）。
// 本地直连 uvicorn：无 /api 前缀，见下方 DEV_FALLBACK。
const PROD_FALLBACK = 'https://campus.gzyichenai.com/api';
const DEV_FALLBACK = 'http://127.0.0.1:8000';

let baseUrl = PROD_FALLBACK;
try {
  const env = import.meta?.env;
  const envBase = env?.VITE_API_BASE_URL;
  if (envBase && String(envBase).trim()) {
    baseUrl = String(envBase).trim();
  } else if (env && (env.DEV === true || env.MODE === 'development')) {
    // 开发构建未注入 .env 时，避免误连生产 HTTPS（易出现 ERR_CONNECTION_CLOSED，代码无法修复 TLS）
    baseUrl = DEV_FALLBACK;
  }
} catch (e) {
  console.warn('env load failed', e);
}

export const BASE_URL = baseUrl;

/** 避免多个接口同时 401 时重复弹 Toast、重复 reLaunch */
let sessionRedirecting = false;

export function getStoredToken() {
  const t = uni.getStorageSync('token');
  return t ? String(t).trim() : '';
}

export function isAuthError(err) {
  return !!(err && (err.type === 'auth' || err.statusCode === 401));
}

/** 登录过期或未登录：清缓存并跳转登录页（全局只处理一次） */
export function handleSessionExpired(message = '登录已过期，请重新登录') {
  if (sessionRedirecting) return;
  sessionRedirecting = true;
  uni.removeStorageSync('token');
  uni.removeStorageSync('userInfo');
  uni.removeStorageSync('userRole');
  uni.showToast({ title: message, icon: 'none', duration: 2000 });
  setTimeout(() => {
    uni.reLaunch({
      url: '/pages/login/login',
      complete: () => {
        sessionRedirecting = false;
      }
    });
  }, 600);
}

/** 静态资源（/uploads 等）在站点根路径，不在 /api 下；勿用 BASE_URL 直接拼接 */
export function resolveMediaUrl(pathOrUrl) {
  if (pathOrUrl == null || pathOrUrl === '') return '';
  const u = String(pathOrUrl).trim();
  if (/^https?:\/\//i.test(u) || u.startsWith('wxfile:') || u.startsWith('blob:')) return u;
  const origin = BASE_URL.replace(/\/api\/?$/i, '');
  const path = u.startsWith('/') ? u : `/${u}`;
  return `${origin}${path}`;
}

export function getStoredUserInfo() {
  const raw = uni.getStorageSync('userInfo');
  if (!raw) return {};
  if (typeof raw === 'string') {
    try {
      return JSON.parse(raw);
    } catch (e) {
      return {};
    }
  }
  return raw;
}

export function patchStoredUserInfo(patch) {
  const userInfo = { ...getStoredUserInfo(), ...patch };
  uni.setStorageSync('userInfo', userInfo);
  return userInfo;
}

/** 头像展示 URL，附带版本参数避免微信 image 缓存旧图 */
export function avatarImageSrc(avatarPathOrUrl) {
  if (!avatarPathOrUrl) return '/static/avatar.png';
  const base = resolveMediaUrl(avatarPathOrUrl);
  const token = encodeURIComponent(String(avatarPathOrUrl));
  return `${base}${base.includes('?') ? '&' : '?'}v=${token}`;
}

export async function persistAvatarUrl(avatarUrl) {
  if (!avatarUrl) return;
  await request({
    url: '/users/profile',
    method: 'PUT',
    data: { avatar_url: avatarUrl }
  });
  patchStoredUserInfo({ avatar_url: avatarUrl });
}

// 请求封装
export const request = (...args) => {
  let options = {};
  if (typeof args[0] === 'string') {
    options = { url: args[0], ...args[1] };
  } else {
    options = args[0] || {};
  }
  
  return new Promise((resolve, reject) => {
    const url = options.url || '';
    const isLoginRequest = url.indexOf('/auth/login') !== -1;
    const isRegisterRequest = url.indexOf('/auth/register') !== -1;
    const isPublicAuth = isLoginRequest || isRegisterRequest;
    const token = getStoredToken();

    if (!isPublicAuth && !token) {
      handleSessionExpired('请先登录');
      reject({ type: 'auth', message: '未登录' });
      return;
    }

    // 组装 Header
    const header = {
      'Content-Type': 'application/json',
      ...(options.header || {})
    };

    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }

    uni.request({
      url: `${BASE_URL}${url}`,
      method: options.method || 'GET',
      data: options.data || {},
      header: header,
      timeout: typeof options.timeout === 'number' ? options.timeout : 60000,
      success: (res) => {
        if (res.statusCode === 204) {
          resolve(null);
          return;
        }
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          if (isLoginRequest) {
            const msg = (res.data && res.data.detail) ? res.data.detail : '用户名或密码错误';
            reject({ type: 'server', statusCode: 401, message: msg, data: res.data });
          } else {
            handleSessionExpired();
            reject({ type: 'auth', message: '登录已过期', data: res.data });
          }
        } else {
          let errorMessage = '请求失败';
          try {
            const d = res.data;
            if (d && typeof d === 'object' && !Array.isArray(d)) {
              const det = d.detail;
              if (typeof det === 'string') {
                errorMessage = det;
              } else if (Array.isArray(det)) {
                errorMessage = det
                  .map((x) => (x && (x.msg || x.message)) || JSON.stringify(x))
                  .join('; ');
              } else if (typeof d.message === 'string') {
                errorMessage = d.message;
              }
            } else if (typeof d === 'string' && d.length < 240) {
              errorMessage = d;
            }
          } catch (_) {}
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
  const payload = {
    ...data
  };
  const normalizedAccount = payload.account != null ? String(payload.account).trim() : '';
  if (normalizedAccount) {
    payload.account = normalizedAccount;
    if (!payload.phone) {
      payload.phone = normalizedAccount;
    }
  }
  return request({
    url: '/auth/login',
    method: 'POST',
    data: payload
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

export const getTestAnalysisStatus = (activityId) => {
  return request({
    url: `/activity/${activityId}/analysis-status`,
    method: 'GET'
  });
};

export const reanalyzeTestActivity = (activityId) => {
  return request({
    url: `/activity/${activityId}/reanalyze`,
    method: 'POST'
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

export const getStudentTaskDetail = (taskId) => {
  return request({
    url: `/student/tasks/${taskId}`,
    method: 'GET'
  });
};

export const getStudentTaskRunHistory = (params) => {
  let queryString = '';
  if (params) {
    const queryParts = [];
    if (params.page) queryParts.push(`page=${params.page}`);
    if (params.size) queryParts.push(`size=${params.size}`);
    if (queryParts.length > 0) queryString = `?${queryParts.join('&')}`;
  }
  return request({
    url: `/student/task-runs/history${queryString}`,
    method: 'GET'
  });
};

export const getTeacherTaskRunDetail = (activityId) => {
  return request({
    url: `/teacher/task-runs/${activityId}`,
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
    url: '/common/checkpoints',
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
    const opts = {
      url: `${BASE_URL}/upload/file`,
      filePath: filePath,
      name: 'file',
      timeout: 120000,
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
          handleSessionExpired();
          reject({ type: 'auth', statusCode: 401, message: '登录已过期' });
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
    };
    // 微信小程序 multipart 常无 .mp4 后缀，需显式 fileName（基础库 2.10.0+）
    if (fileType === 'video') {
      opts.fileName = 'upload.mp4';
    }
    uni.uploadFile(opts);
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
  getTeacherDashboardStats,
  getTeacherWeeklyTrend,
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

export const updateRunGroup = (groupId, data) => {
  return request({
    url: `/run-group/${groupId}`,
    method: 'PUT',
    data
  });
};

export const joinRunGroup = (groupId) => {
  return request({
    url: `/run-group/join?group_id=${groupId}`,
    method: 'POST'
  });
};

export const leaveRunGroup = (groupId) => {
  const query = groupId ? `?group_id=${groupId}` : '';
  return request({
    url: `/run-group/leave${query}`,
    method: 'POST'
  });
};

export const deleteRunGroup = (groupId) => {
  const query = groupId ? `?group_id=${groupId}` : '';
  return request({
    url: `/run-group/current${query}`,
    method: 'DELETE'
  });
};

export const getMyRunGroup = () => {
  return request({
    url: '/run-group/my',
    method: 'GET'
  });
};

export const getMyRunGroups = () => {
  return request({
    url: '/run-group/my-groups',
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
