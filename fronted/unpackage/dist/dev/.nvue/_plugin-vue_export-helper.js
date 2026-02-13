import { isInSSRComponentSetup, injectHook, getCurrentInstance } from "vue";
const ON_SHOW = "onShow";
const ON_HIDE = "onHide";
const ON_LOAD = "onLoad";
function formatAppLog(type, filename, ...args) {
  if (uni.__log__) {
    uni.__log__(type, filename, ...args);
  } else {
    console[type].apply(console, [...args, filename]);
  }
}
const createLifeCycleHook = (lifecycle, flag = 0) => (hook, target = getCurrentInstance()) => {
  !isInSSRComponentSetup && injectHook(lifecycle, hook, target);
};
const onShow = /* @__PURE__ */ createLifeCycleHook(
  ON_SHOW,
  1 | 2
  /* HookFlags.PAGE */
);
const onHide = /* @__PURE__ */ createLifeCycleHook(
  ON_HIDE,
  1 | 2
  /* HookFlags.PAGE */
);
const onLoad = /* @__PURE__ */ createLifeCycleHook(
  ON_LOAD,
  2
  /* HookFlags.PAGE */
);
let baseUrl = "http://127.0.0.1:8000";
baseUrl = "http://192.168.0.210:8000";
const BASE_URL = baseUrl;
const request = (...args) => {
  let options = {};
  if (typeof args[0] === "string") {
    options = { url: args[0], ...args[1] };
  } else {
    options = args[0] || {};
  }
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync("token");
    const header = {
      "Content-Type": "application/json",
      ...options.header || {}
    };
    if (token) {
      header["Authorization"] = `Bearer ${token}`;
    }
    uni.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || "GET",
      data: options.data || {},
      header,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          uni.removeStorageSync("token");
          uni.removeStorageSync("userInfo");
          uni.showToast({
            title: "登录已过期，请重新登录",
            icon: "none"
          });
          setTimeout(() => {
            uni.reLaunch({
              url: "/pages/login/login"
            });
          }, 1500);
          reject(res.data);
        } else {
          uni.showToast({
            title: res.data.detail || "请求失败",
            icon: "none"
          });
          reject(res.data);
        }
      },
      fail: (err) => {
        formatAppLog("error", "at utils/request.js:83", "Request fail:", err);
        uni.showModal({
          title: "网络请求失败",
          content: err.errMsg || JSON.stringify(err),
          showCancel: false
        });
        reject(err);
      }
    });
  });
};
const _export_sfc = (sfc, props) => {
  const target = sfc.__vccOpts || sfc;
  for (const [key, val] of props) {
    target[key] = val;
  }
  return target;
};
export {
  BASE_URL as B,
  _export_sfc as _,
  onShow as a,
  onHide as b,
  formatAppLog as f,
  onLoad as o,
  request as r
};
