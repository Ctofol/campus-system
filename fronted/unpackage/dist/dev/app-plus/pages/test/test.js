"use weex:vue";

if (typeof Promise !== 'undefined' && !Promise.prototype.finally) {
  Promise.prototype.finally = function(callback) {
    const promise = this.constructor
    return this.then(
      value => promise.resolve(callback()).then(() => value),
      reason => promise.resolve(callback()).then(() => {
        throw reason
      })
    )
  }
};

if (typeof uni !== 'undefined' && uni && uni.requireGlobal) {
  const global = uni.requireGlobal()
  ArrayBuffer = global.ArrayBuffer
  Int8Array = global.Int8Array
  Uint8Array = global.Uint8Array
  Uint8ClampedArray = global.Uint8ClampedArray
  Int16Array = global.Int16Array
  Uint16Array = global.Uint16Array
  Int32Array = global.Int32Array
  Uint32Array = global.Uint32Array
  Float32Array = global.Float32Array
  Float64Array = global.Float64Array
  BigInt64Array = global.BigInt64Array
  BigUint64Array = global.BigUint64Array
};


(() => {
  var __create = Object.create;
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __getOwnPropSymbols = Object.getOwnPropertySymbols;
  var __getProtoOf = Object.getPrototypeOf;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __propIsEnum = Object.prototype.propertyIsEnumerable;
  var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
  var __spreadValues = (a, b) => {
    for (var prop in b || (b = {}))
      if (__hasOwnProp.call(b, prop))
        __defNormalProp(a, prop, b[prop]);
    if (__getOwnPropSymbols)
      for (var prop of __getOwnPropSymbols(b)) {
        if (__propIsEnum.call(b, prop))
          __defNormalProp(a, prop, b[prop]);
      }
    return a;
  };
  var __commonJS = (cb, mod) => function __require() {
    return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
    // If the importer is in node compatibility mode or this is not an ESM
    // file that has been converted to a CommonJS file using a Babel-
    // compatible transform (i.e. "__esModule" has not been set), then set
    // "default" to the CommonJS "module.exports" for node compatibility.
    isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
    mod
  ));
  var __async = (__this, __arguments, generator) => {
    return new Promise((resolve, reject) => {
      var fulfilled = (value) => {
        try {
          step(generator.next(value));
        } catch (e) {
          reject(e);
        }
      };
      var rejected = (value) => {
        try {
          step(generator.throw(value));
        } catch (e) {
          reject(e);
        }
      };
      var step = (x) => x.done ? resolve(x.value) : Promise.resolve(x.value).then(fulfilled, rejected);
      step((generator = generator.apply(__this, __arguments)).next());
    });
  };

  // vue-ns:vue
  var require_vue = __commonJS({
    "vue-ns:vue"(exports, module) {
      module.exports = Vue;
    }
  });

  // D:/PC/Document/HBuilderProjects/campus-system/fronted/unpackage/dist/dev/.nvue/pages/test/test.js
  var import_vue = __toESM(require_vue());
  var ON_SHOW = "onShow";
  var ON_HIDE = "onHide";
  var ON_LOAD = "onLoad";
  function formatAppLog(type, filename, ...args) {
    if (uni.__log__) {
      uni.__log__(type, filename, ...args);
    } else {
      console[type].apply(console, [...args, filename]);
    }
  }
  var createLifeCycleHook = (lifecycle, flag = 0) => (hook, target = (0, import_vue.getCurrentInstance)()) => {
    !import_vue.isInSSRComponentSetup && (0, import_vue.injectHook)(lifecycle, hook, target);
  };
  var onShow = /* @__PURE__ */ createLifeCycleHook(
    ON_SHOW,
    1 | 2
    /* HookFlags.PAGE */
  );
  var onHide = /* @__PURE__ */ createLifeCycleHook(
    ON_HIDE,
    1 | 2
    /* HookFlags.PAGE */
  );
  var onLoad = /* @__PURE__ */ createLifeCycleHook(
    ON_LOAD,
    2
    /* HookFlags.PAGE */
  );
  var baseUrl = "http://127.0.0.1:8000";
  baseUrl = "http://192.168.0.210:8000";
  var BASE_URL = baseUrl;
  var request = (...args) => {
    let options = {};
    if (typeof args[0] === "string") {
      options = __spreadValues({ url: args[0] }, args[1]);
    } else {
      options = args[0] || {};
    }
    return new Promise((resolve, reject) => {
      const token = uni.getStorageSync("token");
      const header = __spreadValues({
        "Content-Type": "application/json"
      }, options.header || {});
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
              title: "\u767B\u5F55\u5DF2\u8FC7\u671F\uFF0C\u8BF7\u91CD\u65B0\u767B\u5F55",
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
              title: res.data.detail || "\u8BF7\u6C42\u5931\u8D25",
              icon: "none"
            });
            reject(res.data);
          }
        },
        fail: (err) => {
          uni.showToast({
            title: "\u7F51\u7EDC\u8BF7\u6C42\u5931\u8D25",
            icon: "none"
          });
          reject(err);
        }
      });
    });
  };
  var _style_0 = { "test-page-root": { "": { "flex": 1, "backgroundColor": "#1a1a1a", "flexDirection": "column" } }, "custom-navbar": { "": { "position": "fixed", "top": 0, "left": 0, "width": "750rpx", "backgroundColor": "#1a1a1a" } }, "navbar-content": { "": { "height": 44, "flexDirection": "row", "alignItems": "center", "justifyContent": "center" } }, "navbar-title": { "": { "color": "#ffffff", "fontSize": 16, "fontWeight": "bold" } }, "content-wrapper": { "": { "flex": 1, "flexDirection": "column", "alignItems": "center", "width": "750rpx", "paddingBottom": "120rpx" } }, "teacher-tools": { "": { "width": "750rpx", "paddingTop": "40rpx", "paddingRight": "30rpx", "paddingBottom": "40rpx", "paddingLeft": "30rpx" } }, "teacher-card": { "": { "backgroundColor": "#ffffff", "borderRadius": "12rpx", "paddingTop": "20rpx", "paddingRight": "20rpx", "paddingBottom": "20rpx", "paddingLeft": "20rpx" } }, "teacher-title": { "": { "fontSize": "34rpx", "fontWeight": "bold", "marginBottom": "10rpx", "color": "#333333" } }, "teacher-actions": { "": { "flexDirection": "row" } }, "teacher-btn": { "": { "backgroundColor": "#20C997", "paddingTop": "10rpx", "paddingRight": "20rpx", "paddingBottom": "10rpx", "paddingLeft": "20rpx", "borderRadius": "8rpx" } }, "teacher-btn-text": { "": { "color": "#ffffff", "fontSize": "28rpx" } }, "student-container": { "": { "flexDirection": "column", "width": "750rpx", "alignItems": "center" } }, "header-info": { "": { "paddingTop": "40rpx", "paddingRight": "30rpx", "paddingBottom": "20rpx", "paddingLeft": "30rpx", "alignItems": "center" } }, "project-name": { "": { "fontSize": "36rpx", "fontWeight": "bold", "marginBottom": "10rpx", "color": "#ffffff" } }, "standard-badge": { "": { "backgroundColor": "rgba(32,201,151,0.2)", "paddingTop": "8rpx", "paddingRight": "20rpx", "paddingBottom": "8rpx", "paddingLeft": "20rpx", "borderRadius": "12rpx", "marginBottom": "16rpx" } }, "badge-text": { "": { "color": "#20C997", "fontSize": "24rpx", "fontWeight": "bold" } }, "standard-desc": { "": { "fontSize": "28rpx", "color": "#aaaaaa", "marginTop": "10rpx" } }, "test-type-switch": { "": { "marginTop": "20rpx", "flexDirection": "column", "alignItems": "center" } }, "switch-btn": { "": { "backgroundColor": "rgba(255,255,255,0.1)", "paddingTop": "12rpx", "paddingRight": "36rpx", "paddingBottom": "12rpx", "paddingLeft": "36rpx", "borderRadius": "30rpx", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(32,201,151,0.3)" } }, "switch-btn-text": { "": { "color": "#20C997", "fontSize": "28rpx" } }, "type-selector": { "": { "backgroundColor": "rgba(0,0,0,0.4)", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.1)", "borderRadius": "16rpx", "marginTop": "10rpx" } }, "type-item": { "": { "paddingTop": "16rpx", "paddingRight": "40rpx", "paddingBottom": "16rpx", "paddingLeft": "40rpx", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "rgba(255,255,255,0.08)" } }, "type-item-text": { "": { "color": "#ffffff", "fontSize": "28rpx", "textAlign": "center" } }, "camera-area": { "": { "width": "750rpx", "height": "562.5rpx", "backgroundColor": "#000000", "position": "relative", "justifyContent": "center", "alignItems": "center", "borderTopWidth": 1, "borderTopStyle": "solid", "borderTopColor": "#333333", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "#333333" } }, "real-camera": { "": { "width": "750rpx", "height": "562.5rpx" } }, "camera-overlay-content": { "": { "position": "absolute", "top": 0, "left": 0, "width": "750rpx", "height": "562.5rpx" } }, "count-overlay": { "": { "position": "absolute", "top": "200rpx", "left": "375rpx", "transform": "translateX(-50%)", "flexDirection": "row", "alignItems": "flex-end", "justifyContent": "center" } }, "count-val": { "": { "fontSize": "100rpx", "fontWeight": "800", "color": "#20C997", "lineHeight": "100rpx" } }, "count-label": { "": { "fontSize": "30rpx", "color": "rgba(255,255,255,0.8)", "marginLeft": "12rpx", "fontWeight": "bold", "marginBottom": "10rpx" } }, "progress-bar-container": { "": { "position": "absolute", "bottom": 0, "left": 0, "width": "750rpx", "height": "10rpx", "backgroundColor": "rgba(255,255,255,0.1)" } }, "progress-fill": { "": { "height": "10rpx", "backgroundColor": "#20C997" } }, "status-tips": { "": { "position": "absolute", "bottom": "60rpx", "left": 0, "width": "750rpx", "flexDirection": "row", "justifyContent": "center" } }, "status-text": { "": { "backgroundColor": "rgba(0,0,0,0.7)", "paddingTop": "16rpx", "paddingRight": "48rpx", "paddingBottom": "16rpx", "paddingLeft": "48rpx", "borderRadius": "50rpx", "fontSize": "32rpx", "color": "#ffffff", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.1)" } }, "valid-text": { "": { "color": "#20C997", "backgroundColor": "rgba(32,201,151,0.15)", "borderColor": "rgba(32,201,151,0.4)" } }, "action-area": { "": { "width": "750rpx", "paddingTop": "20rpx", "paddingRight": "40rpx", "paddingBottom": "60rpx", "paddingLeft": "40rpx", "alignItems": "center" } }, "timer-box": { "": { "marginBottom": "40rpx", "backgroundColor": "rgba(255,255,255,0.05)", "paddingTop": "16rpx", "paddingRight": "40rpx", "paddingBottom": "16rpx", "paddingLeft": "40rpx", "borderRadius": "20rpx", "alignItems": "center", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.05)" } }, "timer-label": { "": { "fontSize": "24rpx", "color": "#888888", "marginBottom": "4rpx" } }, "timer-text": { "": { "fontSize": "60rpx", "fontWeight": "bold", "color": "#ffffff" } }, "last-result-box": { "": { "marginTop": 20, "backgroundColor": "#2a2a2a", "borderRadius": 12, "paddingTop": 15, "paddingRight": 15, "paddingBottom": 15, "paddingLeft": 15, "width": "600rpx", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#333333" } }, "result-title": { "": { "color": "#ffffff", "fontSize": "32rpx", "fontWeight": "bold", "marginBottom": "20rpx", "textAlign": "center" } }, "result-row": { "": { "flexDirection": "row", "justifyContent": "space-between", "marginBottom": "10rpx" } }, "result-label": { "": { "color": "#888888", "fontSize": "28rpx" } }, "result-value": { "": { "color": "#20C997", "fontSize": "32rpx", "fontWeight": "bold" } }, "btn-group": { "": { "flexDirection": "row", "width": "600rpx", "justifyContent": "center" } }, "testing-btns": { "": { "flexDirection": "row", "flex": 1, "justifyContent": "space-between" } }, "main-btn": { "": { "flex": 1, "backgroundImage": "linear-gradient(to bottom right, #20C997, #17a077)", "height": "110rpx", "alignItems": "center", "justifyContent": "center", "borderRadius": "60rpx" } }, "sub-btn": { "": { "flex": 1, "height": "110rpx", "alignItems": "center", "justifyContent": "center", "borderRadius": "60rpx", "marginTop": 0, "marginRight": "10rpx", "marginBottom": 0, "marginLeft": "10rpx" } }, "stop-btn": { "": { "backgroundImage": "linear-gradient(to bottom right, #ff6b6b, #ee5253)" } }, "mock-btn": { "": { "backgroundColor": "rgba(255,255,255,0.1)", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.1)" } }, "btn-text": { "": { "color": "#ffffff", "fontSize": "36rpx", "fontWeight": "bold" } }, "mock-text": { "": { "color": "#cccccc", "fontSize": "32rpx" } }, "tab-bar": { "": { "position": "fixed", "bottom": 0, "left": 0, "width": "750rpx", "height": "100rpx", "backgroundColor": "#ffffff", "flexDirection": "row", "borderTopWidth": 1, "borderTopStyle": "solid", "borderTopColor": "rgba(0,0,0,0.1)" } }, "tab-bar-item": { "": { "flex": 1, "alignItems": "center", "justifyContent": "center" } }, "tab-icon": { "": { "width": "50rpx", "height": "50rpx", "marginBottom": "4rpx" } }, "tab-text": { "": { "fontSize": "20rpx" } }, "guide-modal": { "": { "position": "fixed", "top": 0, "left": 0, "bottom": 0, "right": 0, "backgroundColor": "rgba(0,0,0,0.8)", "justifyContent": "center", "alignItems": "center" } }, "guide-content": { "": { "backgroundColor": "#ffffff", "width": "600rpx", "borderRadius": "20rpx", "paddingTop": "40rpx", "paddingRight": "40rpx", "paddingBottom": "40rpx", "paddingLeft": "40rpx", "alignItems": "center" } }, "guide-title": { "": { "fontSize": "36rpx", "fontWeight": "bold", "marginBottom": "30rpx", "color": "#333333" } }, "guide-visual": { "": { "width": "200rpx", "height": "200rpx", "backgroundColor": "#f5f5f5", "borderRadius": "20rpx", "alignItems": "center", "justifyContent": "center", "marginBottom": "30rpx" } }, "guide-emoji": { "": { "fontSize": "80rpx" } }, "guide-desc": { "": { "fontSize": "28rpx", "color": "#666666", "textAlign": "center", "marginBottom": "40rpx" } }, "guide-btn": { "": { "backgroundColor": "#20C997", "paddingTop": "10rpx", "paddingRight": "60rpx", "paddingBottom": "10rpx", "paddingLeft": "60rpx", "borderRadius": "40rpx" } }, "guide-btn-text": { "": { "color": "#ffffff", "fontSize": "30rpx" } }, "h5-camera-wrapper": { "": { "width": "750rpx", "height": "562.5rpx", "justifyContent": "center", "alignItems": "center", "backgroundColor": "#333333" } }, "error-text": { "": { "color": "#aaaaaa", "fontSize": "28rpx" } } };
  var _export_sfc = (sfc, props) => {
    const target = sfc.__vccOpts || sfc;
    for (const [key, val] of props) {
      target[key] = val;
    }
    return target;
  };
  var currentTab = "/pages/test/test";
  var _sfc_main = {
    __name: "test",
    setup(__props, { expose: __expose }) {
      __expose();
      const statusBarHeight = (0, import_vue.ref)(20);
      const cameraContext = (0, import_vue.ref)(null);
      const captureTimer = (0, import_vue.ref)(null);
      const isTesting = (0, import_vue.ref)(false);
      const count = (0, import_vue.ref)(0);
      const duration = (0, import_vue.ref)(0);
      const timer = (0, import_vue.ref)(null);
      const lastResult = (0, import_vue.ref)(null);
      const pendingVideoUrl = (0, import_vue.ref)("");
      const progressPercent = (0, import_vue.computed)(() => Math.min(count.value / 20 * 100, 100));
      const isStandard = (0, import_vue.ref)(false);
      const statusText = (0, import_vue.ref)("\u8BF7\u505A\u597D\u51C6\u5907");
      const showSelector = (0, import_vue.ref)(false);
      const showGuide = (0, import_vue.ref)(false);
      const role = (0, import_vue.ref)("student");
      const projectName = (0, import_vue.ref)("\u5F15\u4F53\u5411\u4E0A");
      const standardDesc = (0, import_vue.ref)("\u4E0B\u988C\u8FC7\u6760\uFF0C\u53CC\u81C2\u4F38\u76F4");
      const testType = (0, import_vue.ref)("pull-up");
      const projectEmoji = (0, import_vue.computed)(() => {
        const map = { "pull-up": "\u{1F4AA}", "sit-up": "\u{1F9D8}", "push-up": "\u{1F647}" };
        return map[testType.value] || "\u{1F3C3}";
      });
      const tabList = (0, import_vue.computed)(() => {
        return role.value === "teacher" ? [
          { pagePath: "/pages/teacher/home/home", text: "\u4E3B\u9875", iconPath: "/static/tab/home.png", selectedIconPath: "/static/tab/home-active.png" },
          { pagePath: "/pages/teacher/manage/manage", text: "\u7BA1\u7406", iconPath: "/static/tab/run.png", selectedIconPath: "/static/tab/run-active.png" },
          { pagePath: "/pages/teacher/mine/mine", text: "\u6211\u7684", iconPath: "/static/tab/mine.png", selectedIconPath: "/static/tab/mine-active.png" }
        ] : [
          { pagePath: "/pages/home/home", text: "\u9996\u9875", iconPath: "/static/tab/home.png", selectedIconPath: "/static/tab/home-active.png" },
          { pagePath: "/pages/run/run", text: "\u8DD1\u6B65", iconPath: "/static/tab/run.png", selectedIconPath: "/static/tab/run-active.png" },
          { pagePath: "/pages/test/test", text: "\u4F53\u6D4B", iconPath: "/static/tab/test.png", selectedIconPath: "/static/tab/test-active.png" },
          { pagePath: "/pages/mine/mine", text: "\u6211\u7684", iconPath: "/static/tab/mine.png", selectedIconPath: "/static/tab/mine-active.png" }
        ];
      });
      const switchTab = (item) => {
        if (item.pagePath === currentTab)
          return;
        uni.redirectTo({ url: item.pagePath });
      };
      onShow(() => {
        const userRole = uni.getStorageSync("userRole") || "student";
        role.value = userRole;
        if (!cameraContext.value && uni.createCameraContext) {
          cameraContext.value = uni.createCameraContext();
        }
      });
      const showTypeSelector = () => {
        showSelector.value = !showSelector.value;
      };
      const switchTestType = (name, type) => {
        projectName.value = name;
        testType.value = type;
        showSelector.value = false;
        if (type === "pull-up")
          standardDesc.value = "\u4E0B\u988C\u8FC7\u6760\uFF0C\u53CC\u81C2\u4F38\u76F4";
        else if (type === "sit-up")
          standardDesc.value = "\u53CC\u624B\u62B1\u5934\uFF0C\u8098\u90E8\u89E6\u819D";
        else if (type === "push-up")
          standardDesc.value = "\u8EAB\u4F53\u5E73\u76F4\uFF0C\u5C48\u81C290\u5EA6";
        count.value = 0;
        duration.value = 0;
        isTesting.value = false;
        statusText.value = "\u8BF7\u505A\u597D\u51C6\u5907";
      };
      const formatTime = (seconds) => {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
      };
      const mockCount = () => {
        count.value++;
        isStandard.value = true;
        statusText.value = "\u52A8\u4F5C\u6807\u51C6";
        setTimeout(() => {
          isStandard.value = false;
          statusText.value = "\u4FDD\u6301\u52A8\u4F5C";
        }, 1e3);
      };
      const startTest = () => {
        if (isTesting.value)
          return;
        isTesting.value = true;
        count.value = 0;
        duration.value = 0;
        statusText.value = "\u6B63\u5728\u8BC6\u522B...";
        pendingVideoUrl.value = "";
        timer.value = setInterval(() => {
          duration.value++;
        }, 1e3);
        captureTimer.value = setInterval(() => {
          mockCount();
        }, 3e3);
      };
      const endTest = () => __async(this, null, function* () {
        if (!isTesting.value)
          return;
        clearInterval(timer.value);
        clearInterval(captureTimer.value);
        isTesting.value = false;
        statusText.value = "\u6D4B\u8BD5\u7ED3\u675F";
        lastResult.value = {
          count: count.value,
          duration: formatTime(duration.value),
          date: (/* @__PURE__ */ new Date()).toLocaleString()
        };
        uni.showLoading({ title: "\u6B63\u5728\u4E0A\u4F20\u6570\u636E..." });
        try {
          const snapshotPath = yield takeSnapshot();
          let evidenceUrl = "";
          if (snapshotPath) {
            const uploadRes = yield uploadFile(snapshotPath);
            if (uploadRes && uploadRes.url) {
              evidenceUrl = uploadRes.url;
            }
          }
          yield submitResult(evidenceUrl);
          uni.hideLoading();
          uni.showModal({
            title: "\u6D4B\u8BD5\u5B8C\u6210",
            content: `\u9879\u76EE\uFF1A${projectName.value}
\u672C\u6B21\u6210\u7EE9\uFF1A${count.value}\u6B21
\u7528\u65F6\uFF1A${formatTime(duration.value)}`,
            showCancel: false
          });
        } catch (e) {
          uni.hideLoading();
          uni.showToast({ title: "\u6570\u636E\u63D0\u4EA4\u5931\u8D25", icon: "none" });
          formatAppLog("error", "at pages/test/test.nvue:282", e);
        }
      });
      const takeSnapshot = () => {
        return new Promise((resolve, reject) => {
          if (cameraContext.value && cameraContext.value.takePhoto) {
            cameraContext.value.takePhoto({
              quality: "normal",
              success: (res) => {
                resolve(res.tempImagePath);
              },
              fail: (err) => {
                formatAppLog("error", "at pages/test/test.nvue:296", "App snapshot failed", err);
                resolve(null);
              }
            });
          } else {
            resolve(null);
          }
        });
      };
      const uploadFile = (filePath) => {
        return new Promise((resolve, reject) => {
          const token = uni.getStorageSync("token");
          uni.uploadFile({
            url: `${BASE_URL}/upload`,
            filePath,
            name: "file",
            header: {
              "Authorization": `Bearer ${token}`
            },
            success: (uploadFileRes) => {
              try {
                const data = JSON.parse(uploadFileRes.data);
                resolve(data);
              } catch (e) {
                reject(e);
              }
            },
            fail: (err) => {
              reject(err);
            }
          });
        });
      };
      const submitResult = () => {
        return request({
          url: "/activity/finish",
          method: "POST",
          data: {
            type: "test",
            source: "free",
            started_at: new Date(Date.now() - duration.value * 1e3).toISOString(),
            ended_at: (/* @__PURE__ */ new Date()).toISOString(),
            metrics: {
              count: count.value,
              duration: duration.value,
              qualified: count.value >= 10,
              checkpoints: JSON.stringify([])
            },
            evidence: [
              ...pendingVideoUrl.value ? [{ evidence_type: "video", data_ref: pendingVideoUrl.value }] : []
            ]
          }
        });
      };
      const handleOptions = (options) => {
        if (options.project)
          projectName.value = options.project;
        if (options.type)
          testType.value = options.type;
        const standards = {
          "\u5F15\u4F53\u5411\u4E0A": "\u4E0B\u988C\u8FC7\u6760\uFF0C\u53CC\u81C2\u4F38\u76F4",
          "\u4EF0\u5367\u8D77\u5750": "\u53CC\u624B\u62B1\u5934\uFF0C\u8098\u90E8\u89E6\u819D",
          "\u4FEF\u5367\u6491": "\u8EAB\u4F53\u5E73\u76F4\uFF0C\u5C48\u81C290\u5EA6"
        };
        if (standards[projectName.value]) {
          standardDesc.value = standards[projectName.value];
        }
      };
      onLoad((options) => {
        const sys = uni.getSystemInfoSync();
        statusBarHeight.value = sys.statusBarHeight || 20;
        if (options) {
          handleOptions(options);
        }
      });
      const gotoStudents = () => {
        uni.navigateTo({ url: "/pages/teacher/students/students" });
      };
      const handleCameraError = (e) => {
        formatAppLog("error", "at pages/test/test.nvue:385", "Camera Error:", e);
        uni.showToast({
          title: "\u65E0\u6CD5\u8BBF\u95EE\u6444\u50CF\u5934",
          icon: "none",
          duration: 3e3
        });
      };
      onHide(() => {
        if (isTesting.value) {
          clearInterval(timer.value);
          clearInterval(captureTimer.value);
          isTesting.value = false;
        }
      });
      const __returned__ = { statusBarHeight, cameraContext, captureTimer, isTesting, count, duration, timer, lastResult, pendingVideoUrl, progressPercent, isStandard, statusText, showSelector, showGuide, role, projectName, standardDesc, testType, projectEmoji, currentTab, tabList, switchTab, showTypeSelector, switchTestType, formatTime, mockCount, startTest, endTest, takeSnapshot, uploadFile, submitResult, handleOptions, gotoStudents, handleCameraError, ref: import_vue.ref, computed: import_vue.computed, onMounted: import_vue.onMounted, onUnmounted: import_vue.onUnmounted, get onLoad() {
        return onLoad;
      }, get onShow() {
        return onShow;
      }, get onHide() {
        return onHide;
      }, get request() {
        return request;
      }, get BASE_URL() {
        return BASE_URL;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_button = (0, import_vue.resolveComponent)("button");
    return (0, import_vue.openBlock)(), (0, import_vue.createElementBlock)("scroll-view", {
      scrollY: true,
      showScrollbar: true,
      enableBackToTop: true,
      bubble: "true",
      style: { flexDirection: "column" }
    }, [
      (0, import_vue.createElementVNode)("view", { class: "test-page-root" }, [
        (0, import_vue.createElementVNode)(
          "view",
          {
            class: "custom-navbar",
            style: (0, import_vue.normalizeStyle)({ paddingTop: $setup.statusBarHeight + "px" })
          },
          [
            (0, import_vue.createElementVNode)("view", { class: "navbar-content" }, [
              (0, import_vue.createElementVNode)("u-text", { class: "navbar-title" }, "\u4F53\u80FD\u6D4B\u8BD5")
            ])
          ],
          4
          /* STYLE */
        ),
        (0, import_vue.createElementVNode)(
          "scroll-view",
          {
            scrollY: "true",
            class: "content-wrapper",
            style: (0, import_vue.normalizeStyle)({ paddingTop: $setup.statusBarHeight + 44 + "px" })
          },
          [
            $setup.role === "teacher" ? ((0, import_vue.openBlock)(), (0, import_vue.createElementBlock)("view", {
              key: 0,
              class: "teacher-tools"
            }, [
              (0, import_vue.createElementVNode)("view", { class: "teacher-card" }, [
                (0, import_vue.createElementVNode)("u-text", { class: "teacher-title" }, "\u6559\u5E08\u5DE5\u5177"),
                (0, import_vue.createElementVNode)("view", { class: "teacher-actions" }, [
                  (0, import_vue.createVNode)(_component_button, {
                    class: "teacher-btn",
                    onClick: $setup.gotoStudents
                  }, {
                    default: (0, import_vue.withCtx)(() => [
                      (0, import_vue.createElementVNode)("u-text", { class: "teacher-btn-text" }, "\u5B66\u5458\u7BA1\u7406")
                    ]),
                    _: 1
                    /* STABLE */
                  })
                ])
              ])
            ])) : ((0, import_vue.openBlock)(), (0, import_vue.createElementBlock)("view", {
              key: 1,
              class: "student-container"
            }, [
              (0, import_vue.createElementVNode)("view", { class: "header-info" }, [
                (0, import_vue.createElementVNode)(
                  "u-text",
                  { class: "project-name" },
                  (0, import_vue.toDisplayString)($setup.projectName),
                  1
                  /* TEXT */
                ),
                (0, import_vue.createElementVNode)("view", { class: "standard-badge" }, [
                  (0, import_vue.createElementVNode)("u-text", { class: "badge-text" }, "\u56FD\u5BB6\u5B66\u751F\u4F53\u8D28\u5065\u5EB7\u6807\u51C6")
                ]),
                (0, import_vue.createElementVNode)(
                  "u-text",
                  { class: "standard-desc" },
                  "\u52A8\u4F5C\u6807\u51C6\uFF1A" + (0, import_vue.toDisplayString)($setup.standardDesc),
                  1
                  /* TEXT */
                ),
                (0, import_vue.createElementVNode)("view", { class: "test-type-switch" }, [
                  (0, import_vue.createVNode)(_component_button, {
                    class: "switch-btn",
                    onClick: $setup.showTypeSelector
                  }, {
                    default: (0, import_vue.withCtx)(() => [
                      (0, import_vue.createElementVNode)("u-text", { class: "switch-btn-text" }, "\u5207\u6362\u6D4B\u8BD5\u7C7B\u578B")
                    ]),
                    _: 1
                    /* STABLE */
                  }),
                  $setup.showSelector ? ((0, import_vue.openBlock)(), (0, import_vue.createElementBlock)("view", {
                    key: 0,
                    class: "type-selector"
                  }, [
                    (0, import_vue.createElementVNode)("view", {
                      class: "type-item",
                      onClick: _cache[0] || (_cache[0] = ($event) => $setup.switchTestType("\u5F15\u4F53\u5411\u4E0A", "pull-up"))
                    }, [
                      (0, import_vue.createElementVNode)("u-text", { class: "type-item-text" }, "\u5F15\u4F53\u5411\u4E0A")
                    ]),
                    (0, import_vue.createElementVNode)("view", {
                      class: "type-item",
                      onClick: _cache[1] || (_cache[1] = ($event) => $setup.switchTestType("\u4EF0\u5367\u8D77\u5750", "sit-up"))
                    }, [
                      (0, import_vue.createElementVNode)("u-text", { class: "type-item-text" }, "\u4EF0\u5367\u8D77\u5750")
                    ]),
                    (0, import_vue.createElementVNode)("view", {
                      class: "type-item",
                      onClick: _cache[2] || (_cache[2] = ($event) => $setup.switchTestType("\u4FEF\u5367\u6491", "push-up"))
                    }, [
                      (0, import_vue.createElementVNode)("u-text", { class: "type-item-text" }, "\u4FEF\u5367\u6491")
                    ])
                  ])) : (0, import_vue.createCommentVNode)("v-if", true)
                ])
              ]),
              (0, import_vue.createElementVNode)("view", { class: "camera-area" }, [
                (0, import_vue.createElementVNode)(
                  "camera",
                  {
                    class: "real-camera",
                    devicePosition: "front",
                    flash: "off",
                    onError: $setup.handleCameraError
                  },
                  null,
                  32
                  /* NEED_HYDRATION */
                ),
                $setup.isTesting ? ((0, import_vue.openBlock)(), (0, import_vue.createElementBlock)("view", {
                  key: 0,
                  class: "camera-overlay-content"
                }, [
                  (0, import_vue.createElementVNode)("view", { class: "count-overlay" }, [
                    (0, import_vue.createElementVNode)(
                      "u-text",
                      { class: "count-val" },
                      (0, import_vue.toDisplayString)($setup.count),
                      1
                      /* TEXT */
                    ),
                    (0, import_vue.createElementVNode)("u-text", { class: "count-label" }, "\u6B21")
                  ]),
                  (0, import_vue.createElementVNode)("view", { class: "progress-bar-container" }, [
                    (0, import_vue.createElementVNode)(
                      "view",
                      {
                        class: "progress-fill",
                        style: (0, import_vue.normalizeStyle)({ width: $setup.progressPercent + "%" })
                      },
                      null,
                      4
                      /* STYLE */
                    )
                  ]),
                  (0, import_vue.createElementVNode)("view", { class: "status-tips" }, [
                    (0, import_vue.createElementVNode)(
                      "u-text",
                      {
                        class: (0, import_vue.normalizeClass)(["status-text", [$setup.isStandard ? "valid-text" : ""]])
                      },
                      (0, import_vue.toDisplayString)($setup.statusText),
                      3
                      /* TEXT, CLASS */
                    )
                  ])
                ])) : (0, import_vue.createCommentVNode)("v-if", true)
              ]),
              (0, import_vue.createElementVNode)("view", { class: "action-area" }, [
                (0, import_vue.createElementVNode)("view", { class: "timer-box" }, [
                  (0, import_vue.createElementVNode)(
                    "u-text",
                    { class: "timer-label" },
                    (0, import_vue.toDisplayString)($setup.isTesting ? "\u6D4B\u8BD5\u7528\u65F6" : $setup.lastResult ? "\u4E0A\u6B21\u7528\u65F6" : "\u6D4B\u8BD5\u7528\u65F6"),
                    1
                    /* TEXT */
                  ),
                  (0, import_vue.createElementVNode)(
                    "u-text",
                    { class: "timer-text" },
                    (0, import_vue.toDisplayString)($setup.isTesting ? $setup.formatTime($setup.duration) : $setup.lastResult ? $setup.lastResult.duration : "00:00"),
                    1
                    /* TEXT */
                  )
                ]),
                !$setup.isTesting && $setup.lastResult ? ((0, import_vue.openBlock)(), (0, import_vue.createElementBlock)("view", {
                  key: 0,
                  class: "last-result-box"
                }, [
                  (0, import_vue.createElementVNode)(
                    "u-text",
                    { class: "result-title" },
                    "\u4E0A\u6B21\u6210\u7EE9 (" + (0, import_vue.toDisplayString)($setup.projectName) + ")",
                    1
                    /* TEXT */
                  ),
                  (0, import_vue.createElementVNode)("view", { class: "result-row" }, [
                    (0, import_vue.createElementVNode)("u-text", { class: "result-label" }, "\u6570\u91CF\uFF1A"),
                    (0, import_vue.createElementVNode)(
                      "u-text",
                      { class: "result-value" },
                      (0, import_vue.toDisplayString)($setup.lastResult.count) + " \u6B21",
                      1
                      /* TEXT */
                    )
                  ]),
                  (0, import_vue.createElementVNode)("view", { class: "result-row" }, [
                    (0, import_vue.createElementVNode)("u-text", { class: "result-label" }, "\u7528\u65F6\uFF1A"),
                    (0, import_vue.createElementVNode)(
                      "u-text",
                      { class: "result-value" },
                      (0, import_vue.toDisplayString)($setup.lastResult.duration),
                      1
                      /* TEXT */
                    )
                  ])
                ])) : (0, import_vue.createCommentVNode)("v-if", true),
                (0, import_vue.createElementVNode)("view", { class: "btn-group" }, [
                  !$setup.isTesting ? ((0, import_vue.openBlock)(), (0, import_vue.createElementBlock)("view", {
                    key: 0,
                    class: "main-btn start-btn",
                    onClick: $setup.startTest
                  }, [
                    (0, import_vue.createElementVNode)(
                      "u-text",
                      { class: "btn-text" },
                      (0, import_vue.toDisplayString)($setup.lastResult ? "\u518D\u6B21\u6D4B\u8BD5" : "\u5F00\u59CB\u6D4B\u8BD5"),
                      1
                      /* TEXT */
                    )
                  ])) : ((0, import_vue.openBlock)(), (0, import_vue.createElementBlock)("view", {
                    key: 1,
                    class: "testing-btns"
                  }, [
                    (0, import_vue.createElementVNode)("view", {
                      class: "sub-btn stop-btn",
                      onClick: $setup.endTest
                    }, [
                      (0, import_vue.createElementVNode)("u-text", { class: "btn-text" }, "\u7ED3\u675F\u6D4B\u8BD5")
                    ]),
                    (0, import_vue.createElementVNode)("view", {
                      class: "sub-btn mock-btn",
                      onClick: $setup.mockCount
                    }, [
                      (0, import_vue.createElementVNode)("u-text", { class: "btn-text mock-text" }, "+1 \u6A21\u62DF")
                    ])
                  ]))
                ])
              ])
            ])),
            $setup.showGuide ? ((0, import_vue.openBlock)(), (0, import_vue.createElementBlock)("view", {
              key: 2,
              class: "guide-modal",
              onClick: _cache[5] || (_cache[5] = ($event) => $setup.showGuide = false)
            }, [
              (0, import_vue.createElementVNode)("view", {
                class: "guide-content",
                onClick: _cache[4] || (_cache[4] = (0, import_vue.withModifiers)(() => {
                }, ["stop"]))
              }, [
                (0, import_vue.createElementVNode)("u-text", { class: "guide-title" }, "\u52A8\u4F5C\u6307\u5357"),
                (0, import_vue.createElementVNode)("view", { class: "guide-visual" }, [
                  (0, import_vue.createElementVNode)(
                    "u-text",
                    { class: "guide-emoji" },
                    (0, import_vue.toDisplayString)($setup.projectEmoji),
                    1
                    /* TEXT */
                  )
                ]),
                (0, import_vue.createElementVNode)(
                  "u-text",
                  { class: "guide-desc" },
                  (0, import_vue.toDisplayString)($setup.standardDesc),
                  1
                  /* TEXT */
                ),
                (0, import_vue.createVNode)(_component_button, {
                  class: "guide-btn",
                  onClick: _cache[3] || (_cache[3] = ($event) => $setup.showGuide = false)
                }, {
                  default: (0, import_vue.withCtx)(() => [
                    (0, import_vue.createElementVNode)("u-text", { class: "guide-btn-text" }, "\u6211\u77E5\u9053\u4E86")
                  ]),
                  _: 1
                  /* STABLE */
                })
              ])
            ])) : (0, import_vue.createCommentVNode)("v-if", true)
          ],
          4
          /* STYLE */
        ),
        (0, import_vue.createElementVNode)("view", { class: "tab-bar" }, [
          (0, import_vue.createElementVNode)("view", { class: "tab-bar-border" }),
          ((0, import_vue.openBlock)(true), (0, import_vue.createElementBlock)(
            import_vue.Fragment,
            null,
            (0, import_vue.renderList)($setup.tabList, (item, index) => {
              return (0, import_vue.openBlock)(), (0, import_vue.createElementBlock)("view", {
                key: index,
                class: "tab-bar-item",
                onClick: ($event) => $setup.switchTab(item)
              }, [
                (0, import_vue.createElementVNode)("u-image", {
                  class: "tab-icon",
                  src: $setup.currentTab === item.pagePath ? item.selectedIconPath : item.iconPath
                }, null, 8, ["src"]),
                (0, import_vue.createElementVNode)(
                  "u-text",
                  {
                    class: "tab-text",
                    style: (0, import_vue.normalizeStyle)({ color: $setup.currentTab === item.pagePath ? "#20C997" : "#666666" })
                  },
                  (0, import_vue.toDisplayString)(item.text),
                  5
                  /* TEXT, STYLE */
                )
              ], 8, ["onClick"]);
            }),
            128
            /* KEYED_FRAGMENT */
          ))
        ])
      ])
    ]);
  }
  var test = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render], ["styles", [_style_0]], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/test/test.nvue"]]);

  // <stdin>
  var webview = plus.webview.currentWebview();
  if (webview) {
    const __pageId = parseInt(webview.id);
    const __pagePath = "pages/test/test";
    let __pageQuery = {};
    try {
      __pageQuery = JSON.parse(webview.__query__);
    } catch (e) {
    }
    test.mpType = "page";
    const app = Vue.createPageApp(test, { $store: getApp({ allowDefault: true }).$store, __pageId, __pagePath, __pageQuery });
    app.provide("__globalStyles", Vue.useCssStyles([...__uniConfig.styles, ...test.styles || []]));
    app.mount("#root");
  }
})();
