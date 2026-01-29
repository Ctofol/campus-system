"use strict";
const common_vendor = require("../common/vendor.js");
const BASE_URL = "http://127.0.0.1:8000";
const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = common_vendor.index.getStorageSync("token");
    const header = {
      "Content-Type": "application/json",
      ...options.header
    };
    if (token) {
      header["Authorization"] = `Bearer ${token}`;
    }
    common_vendor.index.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || "GET",
      data: options.data || {},
      header,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          common_vendor.index.removeStorageSync("token");
          common_vendor.index.removeStorageSync("userInfo");
          common_vendor.index.showToast({
            title: "登录已过期，请重新登录",
            icon: "none"
          });
          setTimeout(() => {
            common_vendor.index.reLaunch({
              url: "/pages/login/login"
            });
          }, 1500);
          reject(res.data);
        } else {
          common_vendor.index.showToast({
            title: res.data.detail || "请求失败",
            icon: "none"
          });
          reject(res.data);
        }
      },
      fail: (err) => {
        common_vendor.index.showToast({
          title: "网络请求失败",
          icon: "none"
        });
        reject(err);
      }
    });
  });
};
const login = (data) => {
  return request({
    url: "/auth/login",
    method: "POST",
    data
  });
};
const register = (data) => {
  return request({
    url: "/auth/register",
    method: "POST",
    data
  });
};
const submitActivity = (data) => {
  return request({
    url: "/activity/finish",
    method: "POST",
    data
  });
};
const getActivityHistory = (params) => {
  let queryString = "";
  if (params) {
    queryString = `?page=${params.page}&size=${params.size}`;
  }
  return request({
    url: `/activity/history${queryString}`,
    method: "GET"
  });
};
const getTeacherActivities = (params) => {
  let queryString = "";
  if (params) {
    queryString = `?page=${params.page}&size=${params.size}`;
  }
  return request({
    url: `/teacher/activities${queryString}`,
    method: "GET"
  });
};
const approveActivity = (activityId) => {
  return request({
    url: `/teacher/activity/${activityId}/approve`,
    method: "POST"
  });
};
const createTeacherTask = (data) => {
  return request({
    url: "/teacher/tasks",
    method: "POST",
    data
  });
};
const deleteTask = (taskId) => {
  return request({
    url: `/teacher/tasks/${taskId}`,
    method: "DELETE"
  });
};
const getTeacherTasks = (params) => {
  let queryString = "";
  if (params) {
    queryString = `?page=${params.page}&size=${params.size}`;
  }
  return request({
    url: `/teacher/tasks${queryString}`,
    method: "GET"
  });
};
const getStudentTasks = (params) => {
  let queryString = "";
  if (params) {
    queryString = `?page=${params.page}&size=${params.size}`;
  }
  return request({
    url: `/student/tasks${queryString}`,
    method: "GET"
  });
};
const getTeacherStudentActivities = (studentId, params) => {
  return request({
    url: `/teacher/student/${studentId}/activities`,
    method: "GET",
    data: params
  });
};
const getTeacherTaskDetail = (taskId) => {
  return request({
    url: `/teacher/tasks/${taskId}`,
    method: "GET"
  });
};
const checkIn = (data) => {
  return request({
    url: "/activity/checkin",
    method: "POST",
    data
  });
};
exports.approveActivity = approveActivity;
exports.checkIn = checkIn;
exports.createTeacherTask = createTeacherTask;
exports.deleteTask = deleteTask;
exports.getActivityHistory = getActivityHistory;
exports.getStudentTasks = getStudentTasks;
exports.getTeacherActivities = getTeacherActivities;
exports.getTeacherStudentActivities = getTeacherStudentActivities;
exports.getTeacherTaskDetail = getTeacherTaskDetail;
exports.getTeacherTasks = getTeacherTasks;
exports.login = login;
exports.register = register;
exports.submitActivity = submitActivity;
//# sourceMappingURL=../../.sourcemap/mp-weixin/utils/request.js.map
