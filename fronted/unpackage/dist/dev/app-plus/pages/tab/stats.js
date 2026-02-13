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

  // D:/PC/Document/HBuilderProjects/campus-system/fronted/unpackage/dist/dev/.nvue/pages/tab/stats.js
  var import_vue2 = __toESM(require_vue());

  // D:/PC/Document/HBuilderProjects/campus-system/fronted/unpackage/dist/dev/.nvue/_plugin-vue_export-helper.js
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
          formatAppLog("error", "at utils/request.js:83", "Request fail:", err);
          uni.showModal({
            title: "\u7F51\u7EDC\u8BF7\u6C42\u5931\u8D25",
            content: err.errMsg || JSON.stringify(err),
            showCancel: false
          });
          reject(err);
        }
      });
    });
  };
  var _export_sfc = (sfc, props) => {
    const target = sfc.__vccOpts || sfc;
    for (const [key, val] of props) {
      target[key] = val;
    }
    return target;
  };

  // D:/PC/Document/HBuilderProjects/campus-system/fronted/unpackage/dist/dev/.nvue/pages/tab/stats.js
  var _style_0$2 = { "test-page-root": { "": { "flex": 1, "backgroundColor": "#1a1a1a", "flexDirection": "column" } }, "custom-navbar": { "": { "position": "fixed", "top": 0, "left": 0, "width": "750rpx", "backgroundColor": "#1a1a1a" } }, "navbar-content": { "": { "height": 44, "flexDirection": "row", "alignItems": "center", "justifyContent": "center" } }, "navbar-title": { "": { "color": "#ffffff", "fontSize": 16, "fontWeight": "bold" } }, "content-wrapper": { "": { "flex": 1, "flexDirection": "column", "alignItems": "center", "width": "750rpx", "paddingBottom": "20rpx" } }, "teacher-tools": { "": { "width": "750rpx", "paddingTop": "40rpx", "paddingRight": "30rpx", "paddingBottom": "40rpx", "paddingLeft": "30rpx" } }, "teacher-card": { "": { "backgroundColor": "#ffffff", "borderRadius": "12rpx", "paddingTop": "20rpx", "paddingRight": "20rpx", "paddingBottom": "20rpx", "paddingLeft": "20rpx" } }, "teacher-title": { "": { "fontSize": "34rpx", "fontWeight": "bold", "marginBottom": "10rpx", "color": "#333333" } }, "teacher-actions": { "": { "flexDirection": "row" } }, "teacher-btn": { "": { "backgroundColor": "#20C997", "paddingTop": "10rpx", "paddingRight": "20rpx", "paddingBottom": "10rpx", "paddingLeft": "20rpx", "borderRadius": "8rpx" } }, "teacher-btn-text": { "": { "color": "#ffffff", "fontSize": "28rpx" } }, "student-container": { "": { "flexDirection": "column", "width": "750rpx", "alignItems": "center" } }, "header-info": { "": { "paddingTop": "40rpx", "paddingRight": "30rpx", "paddingBottom": "20rpx", "paddingLeft": "30rpx", "alignItems": "center" } }, "project-name": { "": { "fontSize": "36rpx", "fontWeight": "bold", "marginBottom": "10rpx", "color": "#ffffff" } }, "standard-badge": { "": { "backgroundColor": "rgba(32,201,151,0.2)", "paddingTop": "8rpx", "paddingRight": "20rpx", "paddingBottom": "8rpx", "paddingLeft": "20rpx", "borderRadius": "12rpx", "marginBottom": "16rpx" } }, "badge-text": { "": { "color": "#20C997", "fontSize": "24rpx", "fontWeight": "bold" } }, "standard-desc": { "": { "fontSize": "28rpx", "color": "#aaaaaa", "marginTop": "10rpx" } }, "test-type-switch": { "": { "marginTop": "20rpx", "flexDirection": "column", "alignItems": "center" } }, "switch-btn": { "": { "backgroundColor": "rgba(255,255,255,0.1)", "paddingTop": "12rpx", "paddingRight": "36rpx", "paddingBottom": "12rpx", "paddingLeft": "36rpx", "borderRadius": "30rpx", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(32,201,151,0.3)" } }, "switch-btn-text": { "": { "color": "#20C997", "fontSize": "28rpx" } }, "type-selector": { "": { "backgroundColor": "rgba(0,0,0,0.4)", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.1)", "borderRadius": "16rpx", "marginTop": "10rpx" } }, "type-item": { "": { "paddingTop": "16rpx", "paddingRight": "40rpx", "paddingBottom": "16rpx", "paddingLeft": "40rpx", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "rgba(255,255,255,0.08)" } }, "type-item-text": { "": { "color": "#ffffff", "fontSize": "28rpx", "textAlign": "center" } }, "camera-area": { "": { "width": "750rpx", "height": "562.5rpx", "backgroundColor": "#000000", "position": "relative", "justifyContent": "center", "alignItems": "center", "borderTopWidth": 1, "borderTopStyle": "solid", "borderTopColor": "#333333", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "#333333" } }, "real-camera": { "": { "width": "750rpx", "height": "562.5rpx" } }, "camera-error-view": { "": { "width": "750rpx", "height": "562.5rpx", "backgroundColor": "#222222", "justifyContent": "center", "alignItems": "center" } }, "error-text": { "": { "color": "#ff6b6b", "fontSize": "30rpx", "marginBottom": "20rpx" } }, "retry-btn": { "": { "backgroundColor": "#333333", "paddingTop": "10rpx", "paddingRight": "30rpx", "paddingBottom": "10rpx", "paddingLeft": "30rpx", "borderRadius": "8rpx", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#444444" } }, "retry-text": { "": { "color": "#ffffff", "fontSize": "28rpx" } }, "camera-overlay-content": { "": { "position": "absolute", "top": 0, "left": 0, "width": "750rpx", "height": "562.5rpx" } }, "count-overlay": { "": { "position": "absolute", "top": "200rpx", "left": "375rpx", "transform": "translateX(-50%)", "flexDirection": "row", "alignItems": "flex-end", "justifyContent": "center" } }, "count-val": { "": { "fontSize": "100rpx", "fontWeight": "800", "color": "#20C997", "lineHeight": "100rpx" } }, "count-label": { "": { "fontSize": "30rpx", "color": "rgba(255,255,255,0.8)", "marginLeft": "12rpx", "fontWeight": "bold", "marginBottom": "10rpx" } }, "progress-bar-container": { "": { "position": "absolute", "bottom": 0, "left": 0, "width": "750rpx", "height": "10rpx", "backgroundColor": "rgba(255,255,255,0.1)" } }, "progress-fill": { "": { "height": "10rpx", "backgroundColor": "#20C997" } }, "status-tips": { "": { "position": "absolute", "bottom": "60rpx", "left": 0, "width": "750rpx", "flexDirection": "row", "justifyContent": "center" } }, "status-text": { "": { "backgroundColor": "rgba(0,0,0,0.7)", "paddingTop": "16rpx", "paddingRight": "48rpx", "paddingBottom": "16rpx", "paddingLeft": "48rpx", "borderRadius": "50rpx", "fontSize": "32rpx", "color": "#ffffff", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.1)" } }, "valid-text": { "": { "color": "#20C997", "backgroundColor": "rgba(32,201,151,0.15)", "borderColor": "rgba(32,201,151,0.4)" } }, "action-area": { "": { "width": "750rpx", "paddingTop": "20rpx", "paddingRight": "40rpx", "paddingBottom": "60rpx", "paddingLeft": "40rpx", "alignItems": "center" } }, "timer-box": { "": { "marginBottom": "40rpx", "backgroundColor": "rgba(255,255,255,0.05)", "paddingTop": "16rpx", "paddingRight": "40rpx", "paddingBottom": "16rpx", "paddingLeft": "40rpx", "borderRadius": "20rpx", "alignItems": "center", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.05)" } }, "timer-label": { "": { "fontSize": "24rpx", "color": "#888888", "marginBottom": "4rpx" } }, "timer-text": { "": { "fontSize": "60rpx", "fontWeight": "bold", "color": "#ffffff" } }, "last-result-box": { "": { "marginTop": 20, "backgroundColor": "#2a2a2a", "borderRadius": 12, "paddingTop": 15, "paddingRight": 15, "paddingBottom": 15, "paddingLeft": 15, "width": "600rpx", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#333333" } }, "result-title": { "": { "color": "#ffffff", "fontSize": "32rpx", "fontWeight": "bold", "marginBottom": "20rpx", "textAlign": "center" } }, "result-row": { "": { "flexDirection": "row", "justifyContent": "space-between", "marginBottom": "10rpx" } }, "result-label": { "": { "color": "#888888", "fontSize": "28rpx" } }, "result-value": { "": { "color": "#20C997", "fontSize": "32rpx", "fontWeight": "bold" } }, "btn-group": { "": { "flexDirection": "row", "width": "600rpx", "justifyContent": "center" } }, "testing-btns": { "": { "flexDirection": "row", "flex": 1, "justifyContent": "space-between" } }, "main-btn": { "": { "flex": 1, "backgroundImage": "linear-gradient(to bottom right, #20C997, #17a077)", "height": "110rpx", "alignItems": "center", "justifyContent": "center", "borderRadius": "60rpx" } }, "sub-btn": { "": { "flex": 1, "height": "110rpx", "alignItems": "center", "justifyContent": "center", "borderRadius": "60rpx", "marginTop": 0, "marginRight": "10rpx", "marginBottom": 0, "marginLeft": "10rpx" } }, "stop-btn": { "": { "backgroundImage": "linear-gradient(to bottom right, #ff6b6b, #ee5253)" } }, "mock-btn": { "": { "backgroundColor": "rgba(255,255,255,0.1)", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.1)" } }, "btn-text": { "": { "color": "#ffffff", "fontSize": "36rpx", "fontWeight": "bold" } }, "mock-text": { "": { "color": "#cccccc", "fontSize": "32rpx" } }, "guide-modal": { "": { "position": "fixed", "top": 0, "left": 0, "bottom": 0, "right": 0, "backgroundColor": "rgba(0,0,0,0.8)", "justifyContent": "center", "alignItems": "center" } }, "guide-content": { "": { "backgroundColor": "#ffffff", "width": "600rpx", "borderRadius": "20rpx", "paddingTop": "40rpx", "paddingRight": "40rpx", "paddingBottom": "40rpx", "paddingLeft": "40rpx", "alignItems": "center" } }, "guide-title": { "": { "fontSize": "36rpx", "fontWeight": "bold", "marginBottom": "30rpx", "color": "#333333" } }, "guide-visual": { "": { "width": "200rpx", "height": "200rpx", "backgroundColor": "#f5f5f5", "borderRadius": "20rpx", "alignItems": "center", "justifyContent": "center", "marginBottom": "30rpx" } }, "guide-emoji": { "": { "fontSize": "80rpx" } }, "guide-desc": { "": { "fontSize": "28rpx", "color": "#666666", "textAlign": "center", "marginBottom": "40rpx" } }, "guide-btn": { "": { "backgroundColor": "#20C997", "paddingTop": "10rpx", "paddingRight": "60rpx", "paddingBottom": "10rpx", "paddingLeft": "60rpx", "borderRadius": "40rpx" } }, "guide-btn-text": { "": { "color": "#ffffff", "fontSize": "30rpx" } }, "h5-camera-wrapper": { "": { "width": "750rpx", "height": "562.5rpx", "justifyContent": "center", "alignItems": "center", "backgroundColor": "#333333" } } };
  var _sfc_main$2 = {
    __name: "student-test",
    setup(__props, { expose: __expose }) {
      const statusBarHeight = (0, import_vue2.ref)(20);
      const cameraContext = (0, import_vue2.ref)(null);
      const captureTimer = (0, import_vue2.ref)(null);
      const isTesting = (0, import_vue2.ref)(false);
      const count = (0, import_vue2.ref)(0);
      const duration = (0, import_vue2.ref)(0);
      const timer = (0, import_vue2.ref)(null);
      const lastResult = (0, import_vue2.ref)(null);
      const pendingVideoUrl = (0, import_vue2.ref)("");
      const progressPercent = (0, import_vue2.computed)(() => Math.min(count.value / 20 * 100, 100));
      const isStandard = (0, import_vue2.ref)(false);
      const statusText = (0, import_vue2.ref)("\u8BF7\u505A\u597D\u51C6\u5907");
      const showSelector = (0, import_vue2.ref)(false);
      const showGuide = (0, import_vue2.ref)(false);
      const role = (0, import_vue2.ref)("student");
      const showCamera = (0, import_vue2.ref)(true);
      const cameraPosition = (0, import_vue2.ref)("back");
      const projectName = (0, import_vue2.ref)("\u5F15\u4F53\u5411\u4E0A");
      const standardDesc = (0, import_vue2.ref)("\u4E0B\u988C\u8FC7\u6760\uFF0C\u53CC\u81C2\u4F38\u76F4");
      const testType = (0, import_vue2.ref)("pull-up");
      const projectEmoji = (0, import_vue2.computed)(() => {
        const map = { "pull-up": "\u{1F4AA}", "sit-up": "\u{1F9D8}", "push-up": "\u{1F647}" };
        return map[testType.value] || "\u{1F3C3}";
      });
      const onPageShow = () => {
        const userRole = uni.getStorageSync("userRole") || "student";
        role.value = userRole;
        if (!cameraContext.value && uni.createCameraContext) {
          cameraContext.value = uni.createCameraContext();
        }
      };
      const onPageHide = () => {
        if (isTesting.value) {
          clearInterval(timer.value);
          clearInterval(captureTimer.value);
          isTesting.value = false;
        }
      };
      (0, import_vue2.onMounted)(() => {
        onPageShow();
      });
      __expose({
        onPageShow,
        onPageHide
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
        if (cameraContext.value) {
          cameraContext.value.startRecord({
            success: () => formatAppLog("log", "at components/student-test/student-test.nvue:235", "Start record success"),
            fail: (e) => {
              formatAppLog("error", "at components/student-test/student-test.nvue:237", "Start record fail", e);
            }
          });
        }
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
        uni.showLoading({ title: "\u6B63\u5728\u5904\u7406\u89C6\u9891..." });
        if (cameraContext.value) {
          cameraContext.value.stopRecord({
            success: (res) => __async(this, null, function* () {
              const videoPath = res.tempVideoPath;
              try {
                uni.showLoading({ title: "\u6B63\u5728\u4E0A\u4F20\u89C6\u9891..." });
                const uploadRes = yield uploadFile(videoPath);
                let evidenceUrl = "";
                if (uploadRes && uploadRes.url) {
                  evidenceUrl = uploadRes.url;
                }
                yield submitResult(evidenceUrl);
                uni.hideLoading();
                showCompletionModal();
              } catch (e) {
                uni.hideLoading();
                uni.showToast({ title: "\u89C6\u9891\u4E0A\u4F20\u5931\u8D25", icon: "none" });
              }
            }),
            fail: (e) => {
              formatAppLog("error", "at components/student-test/student-test.nvue:295", "Stop record fail", e);
              fallbackToSnapshot();
            }
          });
          return;
        }
        fallbackToSnapshot();
      });
      const fallbackToSnapshot = () => __async(this, null, function* () {
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
          showCompletionModal();
        } catch (e) {
          uni.hideLoading();
          uni.showToast({ title: "\u6570\u636E\u63D0\u4EA4\u5931\u8D25", icon: "none" });
          formatAppLog("error", "at components/student-test/student-test.nvue:322", e);
        }
      });
      const showCompletionModal = () => {
        uni.showModal({
          title: "\u6D4B\u8BD5\u5B8C\u6210",
          content: `\u9879\u76EE\uFF1A${projectName.value}
\u672C\u6B21\u6210\u7EE9\uFF1A${count.value}\u6B21
\u7528\u65F6\uFF1A${formatTime(duration.value)}`,
          showCancel: false
        });
      };
      const takeSnapshot = () => {
        return new Promise((resolve, reject) => {
          if (cameraContext.value && cameraContext.value.takePhoto) {
            cameraContext.value.takePhoto({
              quality: "normal",
              success: (res) => {
                resolve(res.tempImagePath);
              },
              fail: (err) => {
                formatAppLog("error", "at components/student-test/student-test.nvue:344", "App snapshot failed", err);
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
      const submitResult = (evidenceUrlArg) => {
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
              ...evidenceUrlArg ? [{ evidence_type: "video", data_ref: evidenceUrlArg }] : []
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
      const toggleCamera = () => {
        cameraPosition.value = cameraPosition.value === "back" ? "front" : "back";
      };
      const retryCamera = () => {
        showCamera.value = false;
        setTimeout(() => {
          showCamera.value = true;
        }, 100);
      };
      const openSysSettings = () => {
        uni.openAppAuthorizeSetting();
      };
      const handleCameraError = (e) => {
        formatAppLog("error", "at components/student-test/student-test.nvue:453", "Camera Error:", e);
        showCamera.value = false;
        uni.showModal({
          title: "\u6444\u50CF\u5934\u6743\u9650\u53D7\u9650",
          content: "\u8BF7\u5728\u8BBE\u7F6E\u4E2D\u5F00\u542F\u6444\u50CF\u5934\u6743\u9650\u4EE5\u8FDB\u884C\u62CD\u6444",
          confirmText: "\u53BB\u8BBE\u7F6E",
          success: (res) => {
            if (res.confirm)
              openSysSettings();
          }
        });
      };
      const __returned__ = { statusBarHeight, cameraContext, captureTimer, isTesting, count, duration, timer, lastResult, pendingVideoUrl, progressPercent, isStandard, statusText, showSelector, showGuide, role, showCamera, cameraPosition, projectName, standardDesc, testType, projectEmoji, onPageShow, onPageHide, showTypeSelector, switchTestType, formatTime, mockCount, startTest, endTest, fallbackToSnapshot, showCompletionModal, takeSnapshot, uploadFile, submitResult, handleOptions, gotoStudents, toggleCamera, retryCamera, openSysSettings, handleCameraError, ref: import_vue2.ref, computed: import_vue2.computed, onMounted: import_vue2.onMounted, onUnmounted: import_vue2.onUnmounted, get onLoad() {
        return onLoad;
      }, get request() {
        return request;
      }, get BASE_URL() {
        return BASE_URL;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$2(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_button = (0, import_vue2.resolveComponent)("button");
    return (0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
      class: "test-page-root",
      renderWhole: true
    }, [
      (0, import_vue2.createElementVNode)(
        "view",
        {
          class: "custom-navbar",
          style: (0, import_vue2.normalizeStyle)({ paddingTop: $setup.statusBarHeight + "px" })
        },
        [
          (0, import_vue2.createElementVNode)("view", { class: "navbar-content" }, [
            (0, import_vue2.createElementVNode)("u-text", { class: "navbar-title" }, "\u4F53\u80FD\u6D4B\u8BD5")
          ])
        ],
        4
        /* STYLE */
      ),
      (0, import_vue2.createElementVNode)(
        "scroll-view",
        {
          scrollY: "true",
          class: "content-wrapper",
          style: (0, import_vue2.normalizeStyle)({ paddingTop: $setup.statusBarHeight + 44 + "px" })
        },
        [
          $setup.role === "teacher" ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
            key: 0,
            class: "teacher-tools"
          }, [
            (0, import_vue2.createElementVNode)("view", { class: "teacher-card" }, [
              (0, import_vue2.createElementVNode)("u-text", { class: "teacher-title" }, "\u6559\u5E08\u5DE5\u5177"),
              (0, import_vue2.createElementVNode)("view", { class: "teacher-actions" }, [
                (0, import_vue2.createVNode)(_component_button, {
                  class: "teacher-btn",
                  onClick: $setup.gotoStudents
                }, {
                  default: (0, import_vue2.withCtx)(() => [
                    (0, import_vue2.createElementVNode)("u-text", { class: "teacher-btn-text" }, "\u5B66\u5458\u7BA1\u7406")
                  ]),
                  _: 1
                  /* STABLE */
                })
              ])
            ])
          ])) : ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
            key: 1,
            class: "student-container"
          }, [
            (0, import_vue2.createElementVNode)("view", { class: "header-info" }, [
              (0, import_vue2.createElementVNode)(
                "u-text",
                { class: "project-name" },
                (0, import_vue2.toDisplayString)($setup.projectName),
                1
                /* TEXT */
              ),
              (0, import_vue2.createElementVNode)("view", { class: "standard-badge" }, [
                (0, import_vue2.createElementVNode)("u-text", { class: "badge-text" }, "\u56FD\u5BB6\u5B66\u751F\u4F53\u8D28\u5065\u5EB7\u6807\u51C6")
              ]),
              (0, import_vue2.createElementVNode)(
                "u-text",
                { class: "standard-desc" },
                "\u52A8\u4F5C\u6807\u51C6\uFF1A" + (0, import_vue2.toDisplayString)($setup.standardDesc),
                1
                /* TEXT */
              ),
              (0, import_vue2.createElementVNode)("view", { class: "test-type-switch" }, [
                (0, import_vue2.createVNode)(_component_button, {
                  class: "switch-btn",
                  onClick: $setup.showTypeSelector
                }, {
                  default: (0, import_vue2.withCtx)(() => [
                    (0, import_vue2.createElementVNode)("u-text", { class: "switch-btn-text" }, "\u5207\u6362\u6D4B\u8BD5\u7C7B\u578B")
                  ]),
                  _: 1
                  /* STABLE */
                }),
                $setup.showSelector ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
                  key: 0,
                  class: "type-selector"
                }, [
                  (0, import_vue2.createElementVNode)("view", {
                    class: "type-item",
                    onClick: _cache[0] || (_cache[0] = ($event) => $setup.switchTestType("\u5F15\u4F53\u5411\u4E0A", "pull-up"))
                  }, [
                    (0, import_vue2.createElementVNode)("u-text", { class: "type-item-text" }, "\u5F15\u4F53\u5411\u4E0A")
                  ]),
                  (0, import_vue2.createElementVNode)("view", {
                    class: "type-item",
                    onClick: _cache[1] || (_cache[1] = ($event) => $setup.switchTestType("\u4EF0\u5367\u8D77\u5750", "sit-up"))
                  }, [
                    (0, import_vue2.createElementVNode)("u-text", { class: "type-item-text" }, "\u4EF0\u5367\u8D77\u5750")
                  ]),
                  (0, import_vue2.createElementVNode)("view", {
                    class: "type-item",
                    onClick: _cache[2] || (_cache[2] = ($event) => $setup.switchTestType("\u4FEF\u5367\u6491", "push-up"))
                  }, [
                    (0, import_vue2.createElementVNode)("u-text", { class: "type-item-text" }, "\u4FEF\u5367\u6491")
                  ])
                ])) : (0, import_vue2.createCommentVNode)("v-if", true)
              ])
            ]),
            (0, import_vue2.createElementVNode)("view", { class: "camera-area" }, [
              $setup.showCamera ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("camera", {
                key: 0,
                class: "real-camera",
                devicePosition: $setup.cameraPosition,
                flash: "off",
                onError: $setup.handleCameraError
              }, null, 40, ["devicePosition"])) : (0, import_vue2.createCommentVNode)("v-if", true),
              $setup.showCamera ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
                key: 1,
                class: "camera-controls"
              }, [
                (0, import_vue2.createVNode)(_component_button, {
                  class: "switch-cam-btn",
                  onClick: $setup.toggleCamera
                }, {
                  default: (0, import_vue2.withCtx)(() => [
                    (0, import_vue2.createElementVNode)("u-text", { class: "switch-text" }, "\u{1F4F7} \u5207\u6362")
                  ]),
                  _: 1
                  /* STABLE */
                })
              ])) : (0, import_vue2.createCommentVNode)("v-if", true),
              !$setup.showCamera ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
                key: 2,
                class: "camera-error-view"
              }, [
                (0, import_vue2.createElementVNode)("u-text", { class: "error-text" }, "\u65E0\u6CD5\u8BBF\u95EE\u6444\u50CF\u5934"),
                (0, import_vue2.createVNode)(_component_button, {
                  class: "retry-btn",
                  onClick: $setup.retryCamera
                }, {
                  default: (0, import_vue2.withCtx)(() => [
                    (0, import_vue2.createElementVNode)("u-text", { class: "retry-text" }, "\u91CD\u8BD5")
                  ]),
                  _: 1
                  /* STABLE */
                }),
                (0, import_vue2.createVNode)(_component_button, {
                  class: "retry-btn setting-btn",
                  onClick: $setup.openSysSettings,
                  style: { "margin-top": "20rpx", "background-color": "#555" }
                }, {
                  default: (0, import_vue2.withCtx)(() => [
                    (0, import_vue2.createElementVNode)("u-text", { class: "retry-text" }, "\u53BB\u8BBE\u7F6E\u5F00\u542F\u6743\u9650")
                  ]),
                  _: 1
                  /* STABLE */
                })
              ])) : (0, import_vue2.createCommentVNode)("v-if", true),
              $setup.isTesting ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
                key: 3,
                class: "camera-overlay-content"
              }, [
                (0, import_vue2.createElementVNode)("view", { class: "count-overlay" }, [
                  (0, import_vue2.createElementVNode)(
                    "u-text",
                    { class: "count-val" },
                    (0, import_vue2.toDisplayString)($setup.count),
                    1
                    /* TEXT */
                  ),
                  (0, import_vue2.createElementVNode)("u-text", { class: "count-label" }, "\u6B21")
                ]),
                (0, import_vue2.createElementVNode)("view", { class: "progress-bar-container" }, [
                  (0, import_vue2.createElementVNode)(
                    "view",
                    {
                      class: "progress-fill",
                      style: (0, import_vue2.normalizeStyle)({ width: $setup.progressPercent + "%" })
                    },
                    null,
                    4
                    /* STYLE */
                  )
                ]),
                (0, import_vue2.createElementVNode)("view", { class: "status-tips" }, [
                  (0, import_vue2.createElementVNode)(
                    "u-text",
                    {
                      class: (0, import_vue2.normalizeClass)(["status-text", [$setup.isStandard ? "valid-text" : ""]])
                    },
                    (0, import_vue2.toDisplayString)($setup.statusText),
                    3
                    /* TEXT, CLASS */
                  )
                ])
              ])) : (0, import_vue2.createCommentVNode)("v-if", true)
            ]),
            (0, import_vue2.createElementVNode)("view", { class: "action-area" }, [
              (0, import_vue2.createElementVNode)("view", { class: "timer-box" }, [
                (0, import_vue2.createElementVNode)(
                  "u-text",
                  { class: "timer-label" },
                  (0, import_vue2.toDisplayString)($setup.isTesting ? "\u6D4B\u8BD5\u7528\u65F6" : $setup.lastResult ? "\u4E0A\u6B21\u7528\u65F6" : "\u6D4B\u8BD5\u7528\u65F6"),
                  1
                  /* TEXT */
                ),
                (0, import_vue2.createElementVNode)(
                  "u-text",
                  { class: "timer-text" },
                  (0, import_vue2.toDisplayString)($setup.isTesting ? $setup.formatTime($setup.duration) : $setup.lastResult ? $setup.lastResult.duration : "00:00"),
                  1
                  /* TEXT */
                )
              ]),
              !$setup.isTesting && $setup.lastResult ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
                key: 0,
                class: "last-result-box"
              }, [
                (0, import_vue2.createElementVNode)(
                  "u-text",
                  { class: "result-title" },
                  "\u4E0A\u6B21\u6210\u7EE9 (" + (0, import_vue2.toDisplayString)($setup.projectName) + ")",
                  1
                  /* TEXT */
                ),
                (0, import_vue2.createElementVNode)("view", { class: "result-row" }, [
                  (0, import_vue2.createElementVNode)("u-text", { class: "result-label" }, "\u6570\u91CF\uFF1A"),
                  (0, import_vue2.createElementVNode)(
                    "u-text",
                    { class: "result-value" },
                    (0, import_vue2.toDisplayString)($setup.lastResult.count) + " \u6B21",
                    1
                    /* TEXT */
                  )
                ]),
                (0, import_vue2.createElementVNode)("view", { class: "result-row" }, [
                  (0, import_vue2.createElementVNode)("u-text", { class: "result-label" }, "\u7528\u65F6\uFF1A"),
                  (0, import_vue2.createElementVNode)(
                    "u-text",
                    { class: "result-value" },
                    (0, import_vue2.toDisplayString)($setup.lastResult.duration),
                    1
                    /* TEXT */
                  )
                ])
              ])) : (0, import_vue2.createCommentVNode)("v-if", true),
              (0, import_vue2.createElementVNode)("view", { class: "btn-group" }, [
                !$setup.isTesting ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
                  key: 0,
                  class: "main-btn start-btn",
                  onClick: $setup.startTest
                }, [
                  (0, import_vue2.createElementVNode)(
                    "u-text",
                    { class: "btn-text" },
                    (0, import_vue2.toDisplayString)($setup.lastResult ? "\u518D\u6B21\u6D4B\u8BD5" : "\u5F00\u59CB\u6D4B\u8BD5"),
                    1
                    /* TEXT */
                  )
                ])) : ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
                  key: 1,
                  class: "testing-btns"
                }, [
                  (0, import_vue2.createElementVNode)("view", {
                    class: "sub-btn stop-btn",
                    onClick: $setup.endTest
                  }, [
                    (0, import_vue2.createElementVNode)("u-text", { class: "btn-text" }, "\u7ED3\u675F\u6D4B\u8BD5")
                  ]),
                  (0, import_vue2.createElementVNode)("view", {
                    class: "sub-btn mock-btn",
                    onClick: $setup.mockCount
                  }, [
                    (0, import_vue2.createElementVNode)("u-text", { class: "btn-text mock-text" }, "+1 \u6A21\u62DF")
                  ])
                ]))
              ])
            ])
          ])),
          $setup.showGuide ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
            key: 2,
            class: "guide-modal",
            onClick: _cache[5] || (_cache[5] = ($event) => $setup.showGuide = false)
          }, [
            (0, import_vue2.createElementVNode)("view", {
              class: "guide-content",
              onClick: _cache[4] || (_cache[4] = (0, import_vue2.withModifiers)(() => {
              }, ["stop"]))
            }, [
              (0, import_vue2.createElementVNode)("u-text", { class: "guide-title" }, "\u52A8\u4F5C\u6307\u5357"),
              (0, import_vue2.createElementVNode)("view", { class: "guide-visual" }, [
                (0, import_vue2.createElementVNode)(
                  "u-text",
                  { class: "guide-emoji" },
                  (0, import_vue2.toDisplayString)($setup.projectEmoji),
                  1
                  /* TEXT */
                )
              ]),
              (0, import_vue2.createElementVNode)(
                "u-text",
                { class: "guide-desc" },
                (0, import_vue2.toDisplayString)($setup.standardDesc),
                1
                /* TEXT */
              ),
              (0, import_vue2.createVNode)(_component_button, {
                class: "guide-btn",
                onClick: _cache[3] || (_cache[3] = ($event) => $setup.showGuide = false)
              }, {
                default: (0, import_vue2.withCtx)(() => [
                  (0, import_vue2.createElementVNode)("u-text", { class: "guide-btn-text" }, "\u6211\u77E5\u9053\u4E86")
                ]),
                _: 1
                /* STABLE */
              })
            ])
          ])) : (0, import_vue2.createCommentVNode)("v-if", true)
        ],
        4
        /* STYLE */
      )
    ]);
  }
  var StudentTest = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["render", _sfc_render$2], ["styles", [_style_0$2]], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/components/student-test/student-test.nvue"]]);
  var _style_0$1 = { "teacher-test-page": { "": { "flex": 1, "backgroundColor": "#f8f9fa", "display": "flex", "flexDirection": "column" } }, "header-tabs": { "": { "backgroundColor": "#ffffff", "display": "flex", "paddingTop": 0, "paddingRight": "20rpx", "paddingBottom": 0, "paddingLeft": "20rpx", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "#eeeeee" } }, "tab-item": { "": { "flex": 1, "textAlign": "center", "paddingTop": "30rpx", "paddingRight": 0, "paddingBottom": "30rpx", "paddingLeft": 0, "position": "relative", "fontSize": "30rpx", "color": "#666666" }, ".active": { "color": "#20C997", "fontWeight": "bold" } }, "tab-indicator": { "": { "position": "absolute", "bottom": 0, "left": 50, "transform": "translateX(-50%)", "width": "40rpx", "height": "6rpx", "backgroundColor": "#20C997", "borderRadius": "4rpx" } }, "content-area": { "": { "flex": 1, "paddingTop": "20rpx", "paddingRight": "20rpx", "paddingBottom": "20rpx", "paddingLeft": "20rpx" } }, "live-header": { "": { "display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "20rpx" } }, "live-title": { "": { "fontSize": "32rpx", "fontWeight": "bold", "color": "#333333" } }, "live-badge": { "": { "backgroundColor": "rgba(32,201,151,0.1)", "color": "#20C997", "fontSize": "24rpx", "paddingTop": "4rpx", "paddingRight": "12rpx", "paddingBottom": "4rpx", "paddingLeft": "12rpx", "borderRadius": "8rpx" } }, "student-live-grid": { "": { "display": "flex", "flexDirection": "row", "flexWrap": "wrap", "justifyContent": "space-between" } }, "student-monitor-card": { "": { "width": "345rpx", "backgroundColor": "#ffffff", "borderRadius": "12rpx", "overflow": "hidden", "boxShadow": "0 2rpx 8rpx rgba(0,0,0,0.05)", "marginBottom": "20rpx" } }, "monitor-video-placeholder": { "": { "height": "200rpx", "backgroundColor": "#000000", "position": "relative", "display": "flex", "alignItems": "center", "justifyContent": "center" } }, "ai-overlay": { "": { "position": "absolute", "top": "10rpx", "left": "10rpx", "color": "#00ff00", "fontSize": "20rpx", "fontFamily": "monospace" } }, "live-score": { "": { "position": "absolute", "bottom": "10rpx", "right": "10rpx", "color": "#ffffff", "fontWeight": "bold", "fontSize": "36rpx" } }, "pose-skeleton": { "": { "width": "60rpx", "height": "100rpx", "position": "relative" } }, "bone": { "": { "backgroundColor": "#00ff00", "position": "absolute" }, ".head": { "width": "16rpx", "height": "16rpx", "borderRadius": 50, "top": 0, "left": "22rpx" }, ".body": { "width": "4rpx", "height": "40rpx", "top": "16rpx", "left": "28rpx" }, ".arm-l": { "width": "20rpx", "height": "4rpx", "top": "24rpx", "left": "8rpx", "transform": "rotate(20deg)" }, ".arm-r": { "width": "20rpx", "height": "4rpx", "top": "24rpx", "right": "8rpx", "transform": "rotate(-20deg)" }, ".leg-l": { "width": "4rpx", "height": "30rpx", "top": "56rpx", "left": "24rpx", "transform": "rotate(10deg)" }, ".leg-r": { "width": "4rpx", "height": "30rpx", "top": "56rpx", "left": "34rpx", "transform": "rotate(-10deg)" } }, "ai-bbox": { "": { "position": "absolute", "top": "20rpx", "left": 20, "width": 60, "height": 80, "borderWidth": "2rpx", "borderStyle": "dashed", "borderColor": "#00ff00", "borderRadius": "8rpx" } }, "bbox-label": { "": { "position": "absolute", "top": "-24rpx", "left": 0, "backgroundColor": "#00ff00", "color": "#000000", "fontSize": "18rpx", "paddingTop": 0, "paddingRight": "4rpx", "paddingBottom": 0, "paddingLeft": "4rpx" } }, "monitor-info": { "": { "paddingTop": "16rpx", "paddingRight": "16rpx", "paddingBottom": "16rpx", "paddingLeft": "16rpx" } }, "skills-matrix": { "": { "display": "flex", "flexDirection": "column" } }, "skill-row": { "": { "display": "flex", "alignItems": "center", "marginBottom": "16rpx" } }, "skill-name": { "": { "fontSize": "24rpx", "color": "#666666", "width": "100rpx", "marginRight": "20rpx" } }, "skill-track": { "": { "flex": 1, "height": "16rpx", "backgroundColor": "#f0f0f0", "borderRadius": "8rpx", "overflow": "hidden" } }, "skill-bar": { "": { "height": 100, "borderRadius": "8rpx" } }, "skill-val": { "": { "fontSize": "24rpx", "fontWeight": "bold", "color": "#333333", "width": "50rpx", "textAlign": "right" } }, "analysis-summary": { "": { "marginTop": "20rpx", "paddingTop": "16rpx", "paddingRight": "16rpx", "paddingBottom": "16rpx", "paddingLeft": "16rpx", "backgroundColor": "#f8f9fa", "borderRadius": "8rpx" } }, "summary-text": { "": { "fontSize": "26rpx", "color": "#666666" } }, "highlight": { "": { "color": "#ff6b6b", "fontWeight": "bold" } }, "s-name": { "": { "fontSize": "28rpx", "fontWeight": "bold" } }, "s-action": { "": { "fontSize": "24rpx", "color": "#666666", "marginTop": "4rpx", "marginRight": 0, "marginBottom": "4rpx", "marginLeft": 0 } }, "s-status": { "": { "fontSize": "22rpx", "paddingTop": "2rpx", "paddingRight": "8rpx", "paddingBottom": "2rpx", "paddingLeft": "8rpx", "borderRadius": "4rpx" }, ".good": { "backgroundColor": "#e6fffa", "color": "#20C997" }, ".warning": { "backgroundColor": "#fff5f5", "color": "#ff6b6b" } }, "chart-card": { "": { "backgroundColor": "#ffffff", "borderRadius": "16rpx", "paddingTop": "30rpx", "paddingRight": "30rpx", "paddingBottom": "30rpx", "paddingLeft": "30rpx", "marginBottom": "20rpx" } }, "card-title": { "": { "fontSize": "30rpx", "fontWeight": "bold", "marginBottom": "30rpx", "borderLeftWidth": "8rpx", "borderLeftStyle": "solid", "borderLeftColor": "#20C997", "paddingLeft": "16rpx" } }, "bar-chart": { "": { "display": "flex", "justifyContent": "space-around", "alignItems": "flex-end", "height": "300rpx", "paddingBottom": "20rpx", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "#eeeeee" } }, "bar-group": { "": { "display": "flex", "flexDirection": "column", "alignItems": "center", "height": 100, "justifyContent": "flex-end" } }, "bar-col": { "": { "width": "40rpx", "height": 80, "backgroundColor": "#f0f0f0", "borderRadius": "20rpx", "position": "relative", "display": "flex", "alignItems": "flex-end" } }, "bar-fill": { "": { "width": 100, "borderRadius": "20rpx", "transitionProperty": "height", "transitionDuration": 1e3 } }, "bar-val": { "": { "position": "absolute", "top": "-30rpx", "left": 50, "transform": "translateX(-50%)", "fontSize": "22rpx", "color": "#666666" } }, "bar-label": { "": { "marginTop": "10rpx", "fontSize": "24rpx", "color": "#666666" } }, "progress-list": { "": { "display": "flex", "flexDirection": "column" } }, "prog-item": { "": { "width": 100, "marginBottom": "24rpx" } }, "prog-header": { "": { "display": "flex", "justifyContent": "space-between", "marginBottom": "8rpx" } }, "prog-name": { "": { "fontSize": "26rpx", "color": "#333333" } }, "prog-val": { "": { "fontSize": "26rpx", "fontWeight": "bold", "color": "#20C997" } }, "prog-track": { "": { "height": "12rpx", "backgroundColor": "#f0f0f0", "borderRadius": "6rpx", "overflow": "hidden" } }, "prog-bar": { "": { "height": 100, "backgroundColor": "#20C997", "borderRadius": "6rpx" } }, "history-list": { "": { "backgroundColor": "#ffffff", "borderRadius": "16rpx" } }, "history-item": { "": { "display": "flex", "justifyContent": "space-between", "alignItems": "center", "paddingTop": "30rpx", "paddingRight": "30rpx", "paddingBottom": "30rpx", "paddingLeft": "30rpx", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "#f5f5f5", "borderBottomWidth:last-child": 0 } }, "h-left": { "": { "display": "flex", "flexDirection": "column" } }, "h-date": { "": { "fontSize": "24rpx", "color": "#999999", "marginBottom": "8rpx" } }, "h-name": { "": { "fontSize": "30rpx", "fontWeight": "bold", "color": "#333333" } }, "h-right": { "": { "display": "flex", "alignItems": "center" } }, "h-stat": { "": { "fontSize": "24rpx", "color": "#666666", "marginRight": "20rpx" } }, "arrow": { "": { "color": "#cccccc", "fontSize": "24rpx" } }, "@TRANSITION": { "bar-fill": { "property": "height", "duration": 1e3 } } };
  var _sfc_main$1 = {
    __name: "teacher-tests",
    setup(__props, { expose: __expose }) {
      const currentTab = (0, import_vue2.ref)("live");
      const liveStudents = (0, import_vue2.ref)([
        { name: "\u5F20\u4F1F", action: "\u5F15\u4F53\u5411\u4E0A", currentScore: 8, isAbnormal: false, confidence: 98 },
        { name: "\u674E\u5F3A", action: "\u4EF0\u5367\u8D77\u5750", currentScore: 24, isAbnormal: true, confidence: 85 },
        { name: "\u738B\u82B3", action: "\u6DF1\u8E72", currentScore: 15, isAbnormal: false, confidence: 96 },
        { name: "\u8D75\u6770", action: "\u4FEF\u5367\u6491", currentScore: 12, isAbnormal: false, confidence: 99 }
      ]);
      const classSkills = (0, import_vue2.ref)([
        { name: "\u7206\u53D1\u529B", val: 85, color: "#ff6b6b" },
        { name: "\u8010\u529B", val: 72, color: "#4dabf7" },
        { name: "\u67D4\u97E7\u6027", val: 68, color: "#ffd43b" },
        { name: "\u534F\u8C03\u6027", val: 90, color: "#20C997" },
        { name: "\u6838\u5FC3\u529B\u91CF", val: 78, color: "#a55eea" }
      ]);
      const classComparison = (0, import_vue2.ref)([
        { label: "\u4F18\u79C0", value: 15, percent: 30, color: "#20C997" },
        { label: "\u826F\u597D", value: 45, percent: 60, color: "#4dabf7" },
        { label: "\u53CA\u683C", value: 30, percent: 45, color: "#ffd43b" },
        { label: "\u4E0D\u53CA\u683C", value: 10, percent: 20, color: "#ff6b6b" }
      ]);
      const passRates = (0, import_vue2.ref)([
        { name: "1000\u7C73\u8DD1", rate: 85 },
        { name: "\u5F15\u4F53\u5411\u4E0A", rate: 62 },
        { name: "\u7ACB\u5B9A\u8DF3\u8FDC", rate: 94 },
        { name: "\u5750\u4F4D\u4F53\u524D\u5C48", rate: 78 }
      ]);
      const historyList = (0, import_vue2.ref)([
        { date: "2026-05-18", testName: "\u5168\u5458\u4F53\u80FD\u6478\u5E95\u6D4B\u8BD5", count: 128, passRate: 92 },
        { date: "2026-05-10", testName: "\u529B\u91CF\u4E13\u9879\u8003\u6838", count: 45, passRate: 88 },
        { date: "2026-04-28", testName: "\u8010\u529B\u8DD1\u6D4B\u8BD5", count: 128, passRate: 76 }
      ]);
      const onPageShow = () => {
        formatAppLog("log", "at components/teacher-tests/teacher-tests.vue:178", "teacher-tests onPageShow");
      };
      const onPageHide = () => {
      };
      __expose({
        onPageShow,
        onPageHide
      });
      const __returned__ = { currentTab, liveStudents, classSkills, classComparison, passRates, historyList, onPageShow, onPageHide, ref: import_vue2.ref };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$1(_ctx, _cache, $props, $setup, $data, $options) {
    return (0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
      class: "teacher-test-page",
      renderWhole: true
    }, [
      (0, import_vue2.createElementVNode)("view", { class: "header-tabs" }, [
        (0, import_vue2.createElementVNode)(
          "view",
          {
            class: (0, import_vue2.normalizeClass)(["tab-item", { active: $setup.currentTab === "live" }]),
            onClick: _cache[0] || (_cache[0] = ($event) => $setup.currentTab = "live")
          },
          [
            (0, import_vue2.createElementVNode)("u-text", { class: "tab-title" }, "\u5B9E\u65F6\u76D1\u63A7"),
            $setup.currentTab === "live" ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
              key: 0,
              class: "tab-indicator"
            })) : (0, import_vue2.createCommentVNode)("v-if", true)
          ],
          2
          /* CLASS */
        ),
        (0, import_vue2.createElementVNode)(
          "view",
          {
            class: (0, import_vue2.normalizeClass)(["tab-item", { active: $setup.currentTab === "analysis" }]),
            onClick: _cache[1] || (_cache[1] = ($event) => $setup.currentTab = "analysis")
          },
          [
            (0, import_vue2.createElementVNode)("u-text", { class: "tab-title" }, "\u6570\u636E\u5206\u6790"),
            $setup.currentTab === "analysis" ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
              key: 0,
              class: "tab-indicator"
            })) : (0, import_vue2.createCommentVNode)("v-if", true)
          ],
          2
          /* CLASS */
        ),
        (0, import_vue2.createElementVNode)(
          "view",
          {
            class: (0, import_vue2.normalizeClass)(["tab-item", { active: $setup.currentTab === "history" }]),
            onClick: _cache[2] || (_cache[2] = ($event) => $setup.currentTab = "history")
          },
          [
            (0, import_vue2.createElementVNode)("u-text", { class: "tab-title" }, "\u5386\u53F2\u56DE\u987E"),
            $setup.currentTab === "history" ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
              key: 0,
              class: "tab-indicator"
            })) : (0, import_vue2.createCommentVNode)("v-if", true)
          ],
          2
          /* CLASS */
        )
      ]),
      $setup.currentTab === "live" ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("scroll-view", {
        key: 0,
        scrollY: "",
        class: "content-area"
      }, [
        (0, import_vue2.createElementVNode)("view", { class: "live-card" }, [
          (0, import_vue2.createElementVNode)("view", { class: "live-header" }, [
            (0, import_vue2.createElementVNode)("u-text", { class: "live-title" }, "\u5F53\u524D\u6B63\u5728\u8FDB\u884C\u7684\u6D4B\u8BD5"),
            (0, import_vue2.createElementVNode)("view", { class: "live-badge" }, [
              (0, import_vue2.createElementVNode)("u-text", null, "AI \u8BC4\u5206\u63A5\u5165\u4E2D")
            ])
          ]),
          (0, import_vue2.createElementVNode)("view", { class: "student-live-grid" }, [
            ((0, import_vue2.openBlock)(true), (0, import_vue2.createElementBlock)(
              import_vue2.Fragment,
              null,
              (0, import_vue2.renderList)($setup.liveStudents, (stu, idx) => {
                return (0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
                  class: "student-monitor-card",
                  key: idx
                }, [
                  (0, import_vue2.createElementVNode)("view", { class: "monitor-video-placeholder" }, [
                    (0, import_vue2.createElementVNode)("u-text", { class: "ai-overlay" }, "AI Analyzing..."),
                    (0, import_vue2.createElementVNode)(
                      "view",
                      {
                        class: "ai-bbox",
                        style: (0, import_vue2.normalizeStyle)({ borderColor: stu.isAbnormal ? "#ff6b6b" : "#0f0" })
                      },
                      [
                        (0, import_vue2.createElementVNode)(
                          "u-text",
                          { class: "bbox-label" },
                          (0, import_vue2.toDisplayString)(stu.confidence) + "%",
                          1
                          /* TEXT */
                        )
                      ],
                      4
                      /* STYLE */
                    ),
                    (0, import_vue2.createElementVNode)("view", { class: "pose-skeleton" }, [
                      (0, import_vue2.createElementVNode)("view", { class: "bone head" }),
                      (0, import_vue2.createElementVNode)("view", { class: "bone body" }),
                      (0, import_vue2.createElementVNode)("view", { class: "bone arm-l" }),
                      (0, import_vue2.createElementVNode)("view", { class: "bone arm-r" }),
                      (0, import_vue2.createElementVNode)("view", { class: "bone leg-l" }),
                      (0, import_vue2.createElementVNode)("view", { class: "bone leg-r" })
                    ]),
                    (0, import_vue2.createElementVNode)(
                      "u-text",
                      { class: "live-score" },
                      (0, import_vue2.toDisplayString)(stu.currentScore),
                      1
                      /* TEXT */
                    )
                  ]),
                  (0, import_vue2.createElementVNode)("view", { class: "monitor-info" }, [
                    (0, import_vue2.createElementVNode)(
                      "u-text",
                      { class: "s-name" },
                      (0, import_vue2.toDisplayString)(stu.name),
                      1
                      /* TEXT */
                    ),
                    (0, import_vue2.createElementVNode)(
                      "u-text",
                      { class: "s-action" },
                      (0, import_vue2.toDisplayString)(stu.action),
                      1
                      /* TEXT */
                    ),
                    stu.isAbnormal ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("u-text", {
                      key: 0,
                      class: "s-status warning"
                    }, "\u52A8\u4F5C\u4E0D\u6807\u51C6")) : ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("u-text", {
                      key: 1,
                      class: "s-status good"
                    }, "\u52A8\u4F5C\u6807\u51C6"))
                  ])
                ]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ])
        ])
      ])) : (0, import_vue2.createCommentVNode)("v-if", true),
      $setup.currentTab === "analysis" ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("scroll-view", {
        key: 1,
        scrollY: "",
        class: "content-area"
      }, [
        (0, import_vue2.createElementVNode)("view", { class: "chart-card" }, [
          (0, import_vue2.createElementVNode)("view", { class: "card-title" }, [
            (0, import_vue2.createElementVNode)("u-text", null, "\u73ED\u7EA7\u4F53\u80FD\u7EFC\u5408\u6A21\u578B")
          ]),
          (0, import_vue2.createElementVNode)("view", { class: "skills-matrix" }, [
            ((0, import_vue2.openBlock)(true), (0, import_vue2.createElementBlock)(
              import_vue2.Fragment,
              null,
              (0, import_vue2.renderList)($setup.classSkills, (skill, idx) => {
                return (0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
                  class: "skill-row",
                  key: idx
                }, [
                  (0, import_vue2.createElementVNode)(
                    "u-text",
                    { class: "skill-name" },
                    (0, import_vue2.toDisplayString)(skill.name),
                    1
                    /* TEXT */
                  ),
                  (0, import_vue2.createElementVNode)("view", { class: "skill-track" }, [
                    (0, import_vue2.createElementVNode)(
                      "view",
                      {
                        class: "skill-bar",
                        style: (0, import_vue2.normalizeStyle)({ width: skill.val + "%", background: skill.color })
                      },
                      null,
                      4
                      /* STYLE */
                    )
                  ]),
                  (0, import_vue2.createElementVNode)(
                    "u-text",
                    { class: "skill-val" },
                    (0, import_vue2.toDisplayString)(skill.val),
                    1
                    /* TEXT */
                  )
                ]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ]),
          (0, import_vue2.createElementVNode)("view", { class: "analysis-summary" }, [
            (0, import_vue2.createElementVNode)("u-text", { class: "summary-text" }, "\u{1F4A1} \u5EFA\u8BAE\u52A0\u5F3A  \u4E13\u9879\u8BAD\u7EC3")
          ])
        ]),
        (0, import_vue2.createElementVNode)("view", { class: "chart-card" }, [
          (0, import_vue2.createElementVNode)("view", { class: "card-title" }, [
            (0, import_vue2.createElementVNode)("u-text", null, "\u73ED\u7EA7\u6210\u7EE9\u5206\u5E03\u5BF9\u6BD4")
          ]),
          (0, import_vue2.createElementVNode)("view", { class: "bar-chart" }, [
            ((0, import_vue2.openBlock)(true), (0, import_vue2.createElementBlock)(
              import_vue2.Fragment,
              null,
              (0, import_vue2.renderList)($setup.classComparison, (item, idx) => {
                return (0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
                  class: "bar-group",
                  key: idx
                }, [
                  (0, import_vue2.createElementVNode)("view", { class: "bar-col" }, [
                    (0, import_vue2.createElementVNode)(
                      "view",
                      {
                        class: "bar-fill",
                        style: (0, import_vue2.normalizeStyle)({ height: item.percent + "%", background: item.color })
                      },
                      null,
                      4
                      /* STYLE */
                    ),
                    (0, import_vue2.createElementVNode)(
                      "u-text",
                      { class: "bar-val" },
                      (0, import_vue2.toDisplayString)(item.value),
                      1
                      /* TEXT */
                    )
                  ]),
                  (0, import_vue2.createElementVNode)(
                    "u-text",
                    { class: "bar-label" },
                    (0, import_vue2.toDisplayString)(item.label),
                    1
                    /* TEXT */
                  )
                ]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ])
        ]),
        (0, import_vue2.createElementVNode)("view", { class: "chart-card" }, [
          (0, import_vue2.createElementVNode)("view", { class: "card-title" }, [
            (0, import_vue2.createElementVNode)("u-text", null, "\u5404\u9879\u4F53\u80FD\u5408\u683C\u7387")
          ]),
          (0, import_vue2.createElementVNode)("view", { class: "progress-list" }, [
            ((0, import_vue2.openBlock)(true), (0, import_vue2.createElementBlock)(
              import_vue2.Fragment,
              null,
              (0, import_vue2.renderList)($setup.passRates, (p, idx) => {
                return (0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
                  class: "prog-item",
                  key: idx
                }, [
                  (0, import_vue2.createElementVNode)("view", { class: "prog-header" }, [
                    (0, import_vue2.createElementVNode)(
                      "u-text",
                      { class: "prog-name" },
                      (0, import_vue2.toDisplayString)(p.name),
                      1
                      /* TEXT */
                    ),
                    (0, import_vue2.createElementVNode)(
                      "u-text",
                      { class: "prog-val" },
                      (0, import_vue2.toDisplayString)(p.rate) + "%",
                      1
                      /* TEXT */
                    )
                  ]),
                  (0, import_vue2.createElementVNode)("view", { class: "prog-track" }, [
                    (0, import_vue2.createElementVNode)(
                      "view",
                      {
                        class: "prog-bar",
                        style: (0, import_vue2.normalizeStyle)({ width: p.rate + "%" })
                      },
                      null,
                      4
                      /* STYLE */
                    )
                  ])
                ]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ])
        ])
      ])) : (0, import_vue2.createCommentVNode)("v-if", true),
      $setup.currentTab === "history" ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("scroll-view", {
        key: 2,
        scrollY: "",
        class: "content-area"
      }, [
        (0, import_vue2.createElementVNode)("view", { class: "history-list" }, [
          ((0, import_vue2.openBlock)(true), (0, import_vue2.createElementBlock)(
            import_vue2.Fragment,
            null,
            (0, import_vue2.renderList)($setup.historyList, (h, idx) => {
              return (0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
                class: "history-item",
                key: idx
              }, [
                (0, import_vue2.createElementVNode)("view", { class: "h-left" }, [
                  (0, import_vue2.createElementVNode)(
                    "u-text",
                    { class: "h-date" },
                    (0, import_vue2.toDisplayString)(h.date),
                    1
                    /* TEXT */
                  ),
                  (0, import_vue2.createElementVNode)(
                    "u-text",
                    { class: "h-name" },
                    (0, import_vue2.toDisplayString)(h.testName),
                    1
                    /* TEXT */
                  )
                ]),
                (0, import_vue2.createElementVNode)("view", { class: "h-right" }, [
                  (0, import_vue2.createElementVNode)(
                    "u-text",
                    { class: "h-stat" },
                    "\u53C2\u4E0E: " + (0, import_vue2.toDisplayString)(h.count) + "\u4EBA",
                    1
                    /* TEXT */
                  ),
                  (0, import_vue2.createElementVNode)(
                    "u-text",
                    { class: "h-stat" },
                    "\u5408\u683C: " + (0, import_vue2.toDisplayString)(h.passRate) + "%",
                    1
                    /* TEXT */
                  ),
                  (0, import_vue2.createElementVNode)("u-text", { class: "arrow" }, ">")
                ])
              ]);
            }),
            128
            /* KEYED_FRAGMENT */
          ))
        ])
      ])) : (0, import_vue2.createCommentVNode)("v-if", true)
    ]);
  }
  var TeacherTests = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["render", _sfc_render$1], ["styles", [_style_0$1]], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/components/teacher-tests/teacher-tests.vue"]]);
  var _style_0 = { "container": { "": { "flex": 1 } } };
  var _sfc_main = {
    __name: "stats",
    setup(__props, { expose: __expose }) {
      __expose();
      const role = (0, import_vue2.ref)(uni.getStorageSync("userRole") || "student");
      const studentTestRef = (0, import_vue2.ref)(null);
      const teacherTestsRef = (0, import_vue2.ref)(null);
      onShow(() => {
        role.value = uni.getStorageSync("userRole") || "student";
        (0, import_vue2.nextTick)(() => {
          if (role.value === "student" && studentTestRef.value && studentTestRef.value.onPageShow) {
            studentTestRef.value.onPageShow();
          } else if (role.value === "teacher" && teacherTestsRef.value && teacherTestsRef.value.onPageShow) {
            teacherTestsRef.value.onPageShow();
          }
        });
      });
      onHide(() => {
        if (role.value === "student" && studentTestRef.value && studentTestRef.value.onPageHide) {
          studentTestRef.value.onPageHide();
        } else if (role.value === "teacher" && teacherTestsRef.value && teacherTestsRef.value.onPageHide) {
          teacherTestsRef.value.onPageHide();
        }
      });
      const __returned__ = { role, studentTestRef, teacherTestsRef, ref: import_vue2.ref, nextTick: import_vue2.nextTick, get onShow() {
        return onShow;
      }, get onHide() {
        return onHide;
      }, get StudentTest() {
        return StudentTest;
      }, TeacherTests };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
    return (0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("scroll-view", {
      scrollY: true,
      showScrollbar: true,
      enableBackToTop: true,
      bubble: "true",
      style: { flexDirection: "column" }
    }, [
      (0, import_vue2.createElementVNode)("view", { class: "container" }, [
        $setup.role === "student" ? ((0, import_vue2.openBlock)(), (0, import_vue2.createBlock)(
          $setup["StudentTest"],
          {
            key: 0,
            ref: "studentTestRef"
          },
          null,
          512
          /* NEED_PATCH */
        )) : ((0, import_vue2.openBlock)(), (0, import_vue2.createBlock)(
          $setup["TeacherTests"],
          {
            key: 1,
            ref: "teacherTestsRef"
          },
          null,
          512
          /* NEED_PATCH */
        ))
      ])
    ]);
  }
  var stats = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render], ["styles", [_style_0]], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/tab/stats.nvue"]]);

  // <stdin>
  var webview = plus.webview.currentWebview();
  if (webview) {
    const __pageId = parseInt(webview.id);
    const __pagePath = "pages/tab/stats";
    let __pageQuery = {};
    try {
      __pageQuery = JSON.parse(webview.__query__);
    } catch (e) {
    }
    stats.mpType = "page";
    const app = Vue.createPageApp(stats, { $store: getApp({ allowDefault: true }).$store, __pageId, __pagePath, __pageQuery });
    app.provide("__globalStyles", Vue.useCssStyles([...__uniConfig.styles, ...stats.styles || []]));
    app.mount("#root");
  }
})();
