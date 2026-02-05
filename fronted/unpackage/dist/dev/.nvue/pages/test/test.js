import { _ as _export_sfc, o as onShow, a as onLoad, b as onHide, f as formatAppLog } from "../../_plugin-vue_export-helper.js";
import { ref, computed, resolveComponent, openBlock, createElementBlock, createElementVNode, normalizeStyle, createVNode, withCtx, toDisplayString, createCommentVNode, normalizeClass, withModifiers, Fragment, renderList, onMounted, onUnmounted } from "vue";
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
        uni.showToast({
          title: "网络请求失败",
          icon: "none"
        });
        reject(err);
      }
    });
  });
};
const _style_0 = { "test-page-root": { "": { "flex": 1, "backgroundColor": "#1a1a1a", "flexDirection": "column" } }, "custom-navbar": { "": { "position": "fixed", "top": 0, "left": 0, "width": "750rpx", "backgroundColor": "#1a1a1a" } }, "navbar-content": { "": { "height": 44, "flexDirection": "row", "alignItems": "center", "justifyContent": "center" } }, "navbar-title": { "": { "color": "#ffffff", "fontSize": 16, "fontWeight": "bold" } }, "content-wrapper": { "": { "flex": 1, "flexDirection": "column", "alignItems": "center", "width": "750rpx", "paddingBottom": "120rpx" } }, "teacher-tools": { "": { "width": "750rpx", "paddingTop": "40rpx", "paddingRight": "30rpx", "paddingBottom": "40rpx", "paddingLeft": "30rpx" } }, "teacher-card": { "": { "backgroundColor": "#ffffff", "borderRadius": "12rpx", "paddingTop": "20rpx", "paddingRight": "20rpx", "paddingBottom": "20rpx", "paddingLeft": "20rpx" } }, "teacher-title": { "": { "fontSize": "34rpx", "fontWeight": "bold", "marginBottom": "10rpx", "color": "#333333" } }, "teacher-actions": { "": { "flexDirection": "row" } }, "teacher-btn": { "": { "backgroundColor": "#20C997", "paddingTop": "10rpx", "paddingRight": "20rpx", "paddingBottom": "10rpx", "paddingLeft": "20rpx", "borderRadius": "8rpx" } }, "teacher-btn-text": { "": { "color": "#ffffff", "fontSize": "28rpx" } }, "student-container": { "": { "flexDirection": "column", "width": "750rpx", "alignItems": "center" } }, "header-info": { "": { "paddingTop": "40rpx", "paddingRight": "30rpx", "paddingBottom": "20rpx", "paddingLeft": "30rpx", "alignItems": "center" } }, "project-name": { "": { "fontSize": "36rpx", "fontWeight": "bold", "marginBottom": "10rpx", "color": "#ffffff" } }, "standard-badge": { "": { "backgroundColor": "rgba(32,201,151,0.2)", "paddingTop": "8rpx", "paddingRight": "20rpx", "paddingBottom": "8rpx", "paddingLeft": "20rpx", "borderRadius": "12rpx", "marginBottom": "16rpx" } }, "badge-text": { "": { "color": "#20C997", "fontSize": "24rpx", "fontWeight": "bold" } }, "standard-desc": { "": { "fontSize": "28rpx", "color": "#aaaaaa", "marginTop": "10rpx" } }, "test-type-switch": { "": { "marginTop": "20rpx", "flexDirection": "column", "alignItems": "center" } }, "switch-btn": { "": { "backgroundColor": "rgba(255,255,255,0.1)", "paddingTop": "12rpx", "paddingRight": "36rpx", "paddingBottom": "12rpx", "paddingLeft": "36rpx", "borderRadius": "30rpx", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(32,201,151,0.3)" } }, "switch-btn-text": { "": { "color": "#20C997", "fontSize": "28rpx" } }, "type-selector": { "": { "backgroundColor": "rgba(0,0,0,0.4)", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.1)", "borderRadius": "16rpx", "marginTop": "10rpx" } }, "type-item": { "": { "paddingTop": "16rpx", "paddingRight": "40rpx", "paddingBottom": "16rpx", "paddingLeft": "40rpx", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "rgba(255,255,255,0.08)" } }, "type-item-text": { "": { "color": "#ffffff", "fontSize": "28rpx", "textAlign": "center" } }, "camera-area": { "": { "width": "750rpx", "height": "562.5rpx", "backgroundColor": "#000000", "position": "relative", "justifyContent": "center", "alignItems": "center", "borderTopWidth": 1, "borderTopStyle": "solid", "borderTopColor": "#333333", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "#333333" } }, "real-camera": { "": { "width": "750rpx", "height": "562.5rpx" } }, "camera-error-view": { "": { "width": "750rpx", "height": "562.5rpx", "backgroundColor": "#222222", "justifyContent": "center", "alignItems": "center" } }, "error-text": { "": { "color": "#aaaaaa", "fontSize": "28rpx", "marginBottom": "20rpx" } }, "retry-btn": { "": { "backgroundColor": "#333333", "paddingTop": "10rpx", "paddingRight": "30rpx", "paddingBottom": "10rpx", "paddingLeft": "30rpx", "borderRadius": "8rpx", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#444444" } }, "retry-text": { "": { "color": "#ffffff", "fontSize": "28rpx" } }, "camera-overlay-content": { "": { "position": "absolute", "top": 0, "left": 0, "width": "750rpx", "height": "562.5rpx" } }, "count-overlay": { "": { "position": "absolute", "top": "200rpx", "left": "375rpx", "transform": "translateX(-50%)", "flexDirection": "row", "alignItems": "flex-end", "justifyContent": "center" } }, "count-val": { "": { "fontSize": "100rpx", "fontWeight": "800", "color": "#20C997", "lineHeight": "100rpx" } }, "count-label": { "": { "fontSize": "30rpx", "color": "rgba(255,255,255,0.8)", "marginLeft": "12rpx", "fontWeight": "bold", "marginBottom": "10rpx" } }, "progress-bar-container": { "": { "position": "absolute", "bottom": 0, "left": 0, "width": "750rpx", "height": "10rpx", "backgroundColor": "rgba(255,255,255,0.1)" } }, "progress-fill": { "": { "height": "10rpx", "backgroundColor": "#20C997" } }, "status-tips": { "": { "position": "absolute", "bottom": "60rpx", "left": 0, "width": "750rpx", "flexDirection": "row", "justifyContent": "center" } }, "status-text": { "": { "backgroundColor": "rgba(0,0,0,0.7)", "paddingTop": "16rpx", "paddingRight": "48rpx", "paddingBottom": "16rpx", "paddingLeft": "48rpx", "borderRadius": "50rpx", "fontSize": "32rpx", "color": "#ffffff", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.1)" } }, "valid-text": { "": { "color": "#20C997", "backgroundColor": "rgba(32,201,151,0.15)", "borderColor": "rgba(32,201,151,0.4)" } }, "action-area": { "": { "width": "750rpx", "paddingTop": "20rpx", "paddingRight": "40rpx", "paddingBottom": "60rpx", "paddingLeft": "40rpx", "alignItems": "center" } }, "timer-box": { "": { "marginBottom": "40rpx", "backgroundColor": "rgba(255,255,255,0.05)", "paddingTop": "16rpx", "paddingRight": "40rpx", "paddingBottom": "16rpx", "paddingLeft": "40rpx", "borderRadius": "20rpx", "alignItems": "center", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.05)" } }, "timer-label": { "": { "fontSize": "24rpx", "color": "#888888", "marginBottom": "4rpx" } }, "timer-text": { "": { "fontSize": "60rpx", "fontWeight": "bold", "color": "#ffffff" } }, "last-result-box": { "": { "marginTop": 20, "backgroundColor": "#2a2a2a", "borderRadius": 12, "paddingTop": 15, "paddingRight": 15, "paddingBottom": 15, "paddingLeft": 15, "width": "600rpx", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#333333" } }, "result-title": { "": { "color": "#ffffff", "fontSize": "32rpx", "fontWeight": "bold", "marginBottom": "20rpx", "textAlign": "center" } }, "result-row": { "": { "flexDirection": "row", "justifyContent": "space-between", "marginBottom": "10rpx" } }, "result-label": { "": { "color": "#888888", "fontSize": "28rpx" } }, "result-value": { "": { "color": "#20C997", "fontSize": "32rpx", "fontWeight": "bold" } }, "btn-group": { "": { "flexDirection": "row", "width": "600rpx", "justifyContent": "center" } }, "testing-btns": { "": { "flexDirection": "row", "flex": 1, "justifyContent": "space-between" } }, "main-btn": { "": { "flex": 1, "backgroundImage": "linear-gradient(to bottom right, #20C997, #17a077)", "height": "110rpx", "alignItems": "center", "justifyContent": "center", "borderRadius": "60rpx" } }, "sub-btn": { "": { "flex": 1, "height": "110rpx", "alignItems": "center", "justifyContent": "center", "borderRadius": "60rpx", "marginTop": 0, "marginRight": "10rpx", "marginBottom": 0, "marginLeft": "10rpx" } }, "stop-btn": { "": { "backgroundImage": "linear-gradient(to bottom right, #ff6b6b, #ee5253)" } }, "mock-btn": { "": { "backgroundColor": "rgba(255,255,255,0.1)", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.1)" } }, "btn-text": { "": { "color": "#ffffff", "fontSize": "36rpx", "fontWeight": "bold" } }, "mock-text": { "": { "color": "#cccccc", "fontSize": "32rpx" } }, "tab-bar": { "": { "position": "fixed", "bottom": 0, "left": 0, "width": "750rpx", "height": "100rpx", "backgroundColor": "#ffffff", "flexDirection": "row", "borderTopWidth": 1, "borderTopStyle": "solid", "borderTopColor": "rgba(0,0,0,0.1)" } }, "tab-bar-item": { "": { "flex": 1, "alignItems": "center", "justifyContent": "center" } }, "tab-icon": { "": { "width": "50rpx", "height": "50rpx", "marginBottom": "4rpx" } }, "tab-text": { "": { "fontSize": "20rpx" } }, "guide-modal": { "": { "position": "fixed", "top": 0, "left": 0, "bottom": 0, "right": 0, "backgroundColor": "rgba(0,0,0,0.8)", "justifyContent": "center", "alignItems": "center" } }, "guide-content": { "": { "backgroundColor": "#ffffff", "width": "600rpx", "borderRadius": "20rpx", "paddingTop": "40rpx", "paddingRight": "40rpx", "paddingBottom": "40rpx", "paddingLeft": "40rpx", "alignItems": "center" } }, "guide-title": { "": { "fontSize": "36rpx", "fontWeight": "bold", "marginBottom": "30rpx", "color": "#333333" } }, "guide-visual": { "": { "width": "200rpx", "height": "200rpx", "backgroundColor": "#f5f5f5", "borderRadius": "20rpx", "alignItems": "center", "justifyContent": "center", "marginBottom": "30rpx" } }, "guide-emoji": { "": { "fontSize": "80rpx" } }, "guide-desc": { "": { "fontSize": "28rpx", "color": "#666666", "textAlign": "center", "marginBottom": "40rpx" } }, "guide-btn": { "": { "backgroundColor": "#20C997", "paddingTop": "10rpx", "paddingRight": "60rpx", "paddingBottom": "10rpx", "paddingLeft": "60rpx", "borderRadius": "40rpx" } }, "guide-btn-text": { "": { "color": "#ffffff", "fontSize": "30rpx" } }, "h5-camera-wrapper": { "": { "width": "750rpx", "height": "562.5rpx", "justifyContent": "center", "alignItems": "center", "backgroundColor": "#333333" } } };
const currentTab = "/pages/test/test";
const _sfc_main = {
  __name: "test",
  setup(__props, { expose: __expose }) {
    __expose();
    const statusBarHeight = ref(20);
    const cameraContext = ref(null);
    const captureTimer = ref(null);
    const isTesting = ref(false);
    const count = ref(0);
    const duration = ref(0);
    const timer = ref(null);
    const lastResult = ref(null);
    const pendingVideoUrl = ref("");
    const progressPercent = computed(() => Math.min(count.value / 20 * 100, 100));
    const isStandard = ref(false);
    const statusText = ref("请做好准备");
    const showSelector = ref(false);
    const showGuide = ref(false);
    const role = ref("student");
    const showCamera = ref(true);
    const cameraPosition = ref("back");
    const projectName = ref("引体向上");
    const standardDesc = ref("下颌过杠，双臂伸直");
    const testType = ref("pull-up");
    const projectEmoji = computed(() => {
      const map = { "pull-up": "💪", "sit-up": "🧘", "push-up": "🙇" };
      return map[testType.value] || "🏃";
    });
    const tabList = computed(() => {
      return role.value === "teacher" ? [
        { pagePath: "/pages/teacher/home/home", text: "主页", iconPath: "/static/tab/home.png", selectedIconPath: "/static/tab/home-active.png" },
        { pagePath: "/pages/teacher/manage/manage", text: "管理", iconPath: "/static/tab/run.png", selectedIconPath: "/static/tab/run-active.png" },
        { pagePath: "/pages/teacher/mine/mine", text: "我的", iconPath: "/static/tab/mine.png", selectedIconPath: "/static/tab/mine-active.png" }
      ] : [
        { pagePath: "/pages/home/home", text: "首页", iconPath: "/static/tab/home.png", selectedIconPath: "/static/tab/home-active.png" },
        { pagePath: "/pages/run/run", text: "跑步", iconPath: "/static/tab/run.png", selectedIconPath: "/static/tab/run-active.png" },
        { pagePath: "/pages/test/test", text: "体测", iconPath: "/static/tab/test.png", selectedIconPath: "/static/tab/test-active.png" },
        { pagePath: "/pages/mine/mine", text: "我的", iconPath: "/static/tab/mine.png", selectedIconPath: "/static/tab/mine-active.png" }
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
        standardDesc.value = "下颌过杠，双臂伸直";
      else if (type === "sit-up")
        standardDesc.value = "双手抱头，肘部触膝";
      else if (type === "push-up")
        standardDesc.value = "身体平直，屈臂90度";
      count.value = 0;
      duration.value = 0;
      isTesting.value = false;
      statusText.value = "请做好准备";
    };
    const formatTime = (seconds) => {
      const m = Math.floor(seconds / 60);
      const s = seconds % 60;
      return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
    };
    const mockCount = () => {
      count.value++;
      isStandard.value = true;
      statusText.value = "动作标准";
      setTimeout(() => {
        isStandard.value = false;
        statusText.value = "保持动作";
      }, 1e3);
    };
    const startTest = () => {
      if (isTesting.value)
        return;
      if (cameraContext.value) {
        cameraContext.value.startRecord({
          success: () => formatAppLog("log", "at pages/test/test.nvue:247", "Start record success"),
          fail: (e) => {
            formatAppLog("error", "at pages/test/test.nvue:249", "Start record fail", e);
          }
        });
      }
      isTesting.value = true;
      count.value = 0;
      duration.value = 0;
      statusText.value = "正在识别...";
      pendingVideoUrl.value = "";
      timer.value = setInterval(() => {
        duration.value++;
      }, 1e3);
      captureTimer.value = setInterval(() => {
        mockCount();
      }, 3e3);
    };
    const endTest = async () => {
      if (!isTesting.value)
        return;
      clearInterval(timer.value);
      clearInterval(captureTimer.value);
      isTesting.value = false;
      statusText.value = "测试结束";
      lastResult.value = {
        count: count.value,
        duration: formatTime(duration.value),
        date: (/* @__PURE__ */ new Date()).toLocaleString()
      };
      uni.showLoading({ title: "正在处理视频..." });
      if (cameraContext.value) {
        cameraContext.value.stopRecord({
          success: async (res) => {
            const videoPath = res.tempVideoPath;
            try {
              uni.showLoading({ title: "正在上传视频..." });
              const uploadRes = await uploadFile(videoPath);
              let evidenceUrl = "";
              if (uploadRes && uploadRes.url) {
                evidenceUrl = uploadRes.url;
              }
              await submitResult(evidenceUrl);
              uni.hideLoading();
              showCompletionModal();
            } catch (e) {
              uni.hideLoading();
              uni.showToast({ title: "视频上传失败", icon: "none" });
            }
          },
          fail: (e) => {
            formatAppLog("error", "at pages/test/test.nvue:307", "Stop record fail", e);
            fallbackToSnapshot();
          }
        });
        return;
      }
      fallbackToSnapshot();
    };
    const fallbackToSnapshot = async () => {
      try {
        const snapshotPath = await takeSnapshot();
        let evidenceUrl = "";
        if (snapshotPath) {
          const uploadRes = await uploadFile(snapshotPath);
          if (uploadRes && uploadRes.url) {
            evidenceUrl = uploadRes.url;
          }
        }
        await submitResult(evidenceUrl);
        uni.hideLoading();
        showCompletionModal();
      } catch (e) {
        uni.hideLoading();
        uni.showToast({ title: "数据提交失败", icon: "none" });
        formatAppLog("error", "at pages/test/test.nvue:334", e);
      }
    };
    const showCompletionModal = () => {
      uni.showModal({
        title: "测试完成",
        content: `项目：${projectName.value}
本次成绩：${count.value}次
用时：${formatTime(duration.value)}`,
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
              formatAppLog("error", "at pages/test/test.nvue:356", "App snapshot failed", err);
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
        "引体向上": "下颌过杠，双臂伸直",
        "仰卧起坐": "双手抱头，肘部触膝",
        "俯卧撑": "身体平直，屈臂90度"
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
      formatAppLog("error", "at pages/test/test.nvue:465", "Camera Error:", e);
      showCamera.value = false;
      uni.showModal({
        title: "摄像头权限受限",
        content: "请在设置中开启摄像头权限以进行拍摄",
        confirmText: "去设置",
        success: (res) => {
          if (res.confirm)
            openSysSettings();
        }
      });
    };
    onHide(() => {
      if (isTesting.value) {
        clearInterval(timer.value);
        clearInterval(captureTimer.value);
        isTesting.value = false;
      }
    });
    const __returned__ = { statusBarHeight, cameraContext, captureTimer, isTesting, count, duration, timer, lastResult, pendingVideoUrl, progressPercent, isStandard, statusText, showSelector, showGuide, role, showCamera, cameraPosition, projectName, standardDesc, testType, projectEmoji, currentTab, tabList, switchTab, showTypeSelector, switchTestType, formatTime, mockCount, startTest, endTest, fallbackToSnapshot, showCompletionModal, takeSnapshot, uploadFile, submitResult, handleOptions, gotoStudents, toggleCamera, retryCamera, openSysSettings, handleCameraError, ref, computed, onMounted, onUnmounted, get onLoad() {
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
  const _component_button = resolveComponent("button");
  return openBlock(), createElementBlock("scroll-view", {
    scrollY: true,
    showScrollbar: true,
    enableBackToTop: true,
    bubble: "true",
    style: { flexDirection: "column" }
  }, [
    createElementVNode("view", { class: "test-page-root" }, [
      createElementVNode(
        "view",
        {
          class: "custom-navbar",
          style: normalizeStyle({ paddingTop: $setup.statusBarHeight + "px" })
        },
        [
          createElementVNode("view", { class: "navbar-content" }, [
            createElementVNode("u-text", { class: "navbar-title" }, "体能测试")
          ])
        ],
        4
        /* STYLE */
      ),
      createElementVNode(
        "scroll-view",
        {
          scrollY: "true",
          class: "content-wrapper",
          style: normalizeStyle({ paddingTop: $setup.statusBarHeight + 44 + "px" })
        },
        [
          $setup.role === "teacher" ? (openBlock(), createElementBlock("view", {
            key: 0,
            class: "teacher-tools"
          }, [
            createElementVNode("view", { class: "teacher-card" }, [
              createElementVNode("u-text", { class: "teacher-title" }, "教师工具"),
              createElementVNode("view", { class: "teacher-actions" }, [
                createVNode(_component_button, {
                  class: "teacher-btn",
                  onClick: $setup.gotoStudents
                }, {
                  default: withCtx(() => [
                    createElementVNode("u-text", { class: "teacher-btn-text" }, "学员管理")
                  ]),
                  _: 1
                  /* STABLE */
                })
              ])
            ])
          ])) : (openBlock(), createElementBlock("view", {
            key: 1,
            class: "student-container"
          }, [
            createElementVNode("view", { class: "header-info" }, [
              createElementVNode(
                "u-text",
                { class: "project-name" },
                toDisplayString($setup.projectName),
                1
                /* TEXT */
              ),
              createElementVNode("view", { class: "standard-badge" }, [
                createElementVNode("u-text", { class: "badge-text" }, "国家学生体质健康标准")
              ]),
              createElementVNode(
                "u-text",
                { class: "standard-desc" },
                "动作标准：" + toDisplayString($setup.standardDesc),
                1
                /* TEXT */
              ),
              createElementVNode("view", { class: "test-type-switch" }, [
                createVNode(_component_button, {
                  class: "switch-btn",
                  onClick: $setup.showTypeSelector
                }, {
                  default: withCtx(() => [
                    createElementVNode("u-text", { class: "switch-btn-text" }, "切换测试类型")
                  ]),
                  _: 1
                  /* STABLE */
                }),
                $setup.showSelector ? (openBlock(), createElementBlock("view", {
                  key: 0,
                  class: "type-selector"
                }, [
                  createElementVNode("view", {
                    class: "type-item",
                    onClick: _cache[0] || (_cache[0] = ($event) => $setup.switchTestType("引体向上", "pull-up"))
                  }, [
                    createElementVNode("u-text", { class: "type-item-text" }, "引体向上")
                  ]),
                  createElementVNode("view", {
                    class: "type-item",
                    onClick: _cache[1] || (_cache[1] = ($event) => $setup.switchTestType("仰卧起坐", "sit-up"))
                  }, [
                    createElementVNode("u-text", { class: "type-item-text" }, "仰卧起坐")
                  ]),
                  createElementVNode("view", {
                    class: "type-item",
                    onClick: _cache[2] || (_cache[2] = ($event) => $setup.switchTestType("俯卧撑", "push-up"))
                  }, [
                    createElementVNode("u-text", { class: "type-item-text" }, "俯卧撑")
                  ])
                ])) : createCommentVNode("v-if", true)
              ])
            ]),
            createElementVNode("view", { class: "camera-area" }, [
              $setup.showCamera ? (openBlock(), createElementBlock("camera", {
                key: 0,
                class: "real-camera",
                devicePosition: $setup.cameraPosition,
                flash: "off",
                onError: $setup.handleCameraError
              }, null, 40, ["devicePosition"])) : createCommentVNode("v-if", true),
              $setup.showCamera ? (openBlock(), createElementBlock("view", {
                key: 1,
                class: "camera-controls"
              }, [
                createVNode(_component_button, {
                  class: "switch-cam-btn",
                  onClick: $setup.toggleCamera
                }, {
                  default: withCtx(() => [
                    createElementVNode("u-text", { class: "switch-text" }, "📷 切换")
                  ]),
                  _: 1
                  /* STABLE */
                })
              ])) : createCommentVNode("v-if", true),
              !$setup.showCamera ? (openBlock(), createElementBlock("view", {
                key: 2,
                class: "camera-error-view"
              }, [
                createElementVNode("u-text", { class: "error-text" }, "无法访问摄像头"),
                createVNode(_component_button, {
                  class: "retry-btn",
                  onClick: $setup.retryCamera
                }, {
                  default: withCtx(() => [
                    createElementVNode("u-text", { class: "retry-text" }, "重试")
                  ]),
                  _: 1
                  /* STABLE */
                }),
                createVNode(_component_button, {
                  class: "retry-btn setting-btn",
                  onClick: $setup.openSysSettings,
                  style: { "margin-top": "20rpx", "background-color": "#555" }
                }, {
                  default: withCtx(() => [
                    createElementVNode("u-text", { class: "retry-text" }, "去设置开启权限")
                  ]),
                  _: 1
                  /* STABLE */
                })
              ])) : createCommentVNode("v-if", true),
              $setup.isTesting ? (openBlock(), createElementBlock("view", {
                key: 3,
                class: "camera-overlay-content"
              }, [
                createElementVNode("view", { class: "count-overlay" }, [
                  createElementVNode(
                    "u-text",
                    { class: "count-val" },
                    toDisplayString($setup.count),
                    1
                    /* TEXT */
                  ),
                  createElementVNode("u-text", { class: "count-label" }, "次")
                ]),
                createElementVNode("view", { class: "progress-bar-container" }, [
                  createElementVNode(
                    "view",
                    {
                      class: "progress-fill",
                      style: normalizeStyle({ width: $setup.progressPercent + "%" })
                    },
                    null,
                    4
                    /* STYLE */
                  )
                ]),
                createElementVNode("view", { class: "status-tips" }, [
                  createElementVNode(
                    "u-text",
                    {
                      class: normalizeClass(["status-text", [$setup.isStandard ? "valid-text" : ""]])
                    },
                    toDisplayString($setup.statusText),
                    3
                    /* TEXT, CLASS */
                  )
                ])
              ])) : createCommentVNode("v-if", true)
            ]),
            createElementVNode("view", { class: "action-area" }, [
              createElementVNode("view", { class: "timer-box" }, [
                createElementVNode(
                  "u-text",
                  { class: "timer-label" },
                  toDisplayString($setup.isTesting ? "测试用时" : $setup.lastResult ? "上次用时" : "测试用时"),
                  1
                  /* TEXT */
                ),
                createElementVNode(
                  "u-text",
                  { class: "timer-text" },
                  toDisplayString($setup.isTesting ? $setup.formatTime($setup.duration) : $setup.lastResult ? $setup.lastResult.duration : "00:00"),
                  1
                  /* TEXT */
                )
              ]),
              !$setup.isTesting && $setup.lastResult ? (openBlock(), createElementBlock("view", {
                key: 0,
                class: "last-result-box"
              }, [
                createElementVNode(
                  "u-text",
                  { class: "result-title" },
                  "上次成绩 (" + toDisplayString($setup.projectName) + ")",
                  1
                  /* TEXT */
                ),
                createElementVNode("view", { class: "result-row" }, [
                  createElementVNode("u-text", { class: "result-label" }, "数量："),
                  createElementVNode(
                    "u-text",
                    { class: "result-value" },
                    toDisplayString($setup.lastResult.count) + " 次",
                    1
                    /* TEXT */
                  )
                ]),
                createElementVNode("view", { class: "result-row" }, [
                  createElementVNode("u-text", { class: "result-label" }, "用时："),
                  createElementVNode(
                    "u-text",
                    { class: "result-value" },
                    toDisplayString($setup.lastResult.duration),
                    1
                    /* TEXT */
                  )
                ])
              ])) : createCommentVNode("v-if", true),
              createElementVNode("view", { class: "btn-group" }, [
                !$setup.isTesting ? (openBlock(), createElementBlock("view", {
                  key: 0,
                  class: "main-btn start-btn",
                  onClick: $setup.startTest
                }, [
                  createElementVNode(
                    "u-text",
                    { class: "btn-text" },
                    toDisplayString($setup.lastResult ? "再次测试" : "开始测试"),
                    1
                    /* TEXT */
                  )
                ])) : (openBlock(), createElementBlock("view", {
                  key: 1,
                  class: "testing-btns"
                }, [
                  createElementVNode("view", {
                    class: "sub-btn stop-btn",
                    onClick: $setup.endTest
                  }, [
                    createElementVNode("u-text", { class: "btn-text" }, "结束测试")
                  ]),
                  createElementVNode("view", {
                    class: "sub-btn mock-btn",
                    onClick: $setup.mockCount
                  }, [
                    createElementVNode("u-text", { class: "btn-text mock-text" }, "+1 模拟")
                  ])
                ]))
              ])
            ])
          ])),
          $setup.showGuide ? (openBlock(), createElementBlock("view", {
            key: 2,
            class: "guide-modal",
            onClick: _cache[5] || (_cache[5] = ($event) => $setup.showGuide = false)
          }, [
            createElementVNode("view", {
              class: "guide-content",
              onClick: _cache[4] || (_cache[4] = withModifiers(() => {
              }, ["stop"]))
            }, [
              createElementVNode("u-text", { class: "guide-title" }, "动作指南"),
              createElementVNode("view", { class: "guide-visual" }, [
                createElementVNode(
                  "u-text",
                  { class: "guide-emoji" },
                  toDisplayString($setup.projectEmoji),
                  1
                  /* TEXT */
                )
              ]),
              createElementVNode(
                "u-text",
                { class: "guide-desc" },
                toDisplayString($setup.standardDesc),
                1
                /* TEXT */
              ),
              createVNode(_component_button, {
                class: "guide-btn",
                onClick: _cache[3] || (_cache[3] = ($event) => $setup.showGuide = false)
              }, {
                default: withCtx(() => [
                  createElementVNode("u-text", { class: "guide-btn-text" }, "我知道了")
                ]),
                _: 1
                /* STABLE */
              })
            ])
          ])) : createCommentVNode("v-if", true)
        ],
        4
        /* STYLE */
      ),
      createElementVNode("view", { class: "tab-bar" }, [
        createElementVNode("view", { class: "tab-bar-border" }),
        (openBlock(true), createElementBlock(
          Fragment,
          null,
          renderList($setup.tabList, (item, index) => {
            return openBlock(), createElementBlock("view", {
              key: index,
              class: "tab-bar-item",
              onClick: ($event) => $setup.switchTab(item)
            }, [
              createElementVNode("u-image", {
                class: "tab-icon",
                src: $setup.currentTab === item.pagePath ? item.selectedIconPath : item.iconPath
              }, null, 8, ["src"]),
              createElementVNode(
                "u-text",
                {
                  class: "tab-text",
                  style: normalizeStyle({ color: $setup.currentTab === item.pagePath ? "#20C997" : "#666666" })
                },
                toDisplayString(item.text),
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
const test = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render], ["styles", [_style_0]], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/test/test.nvue"]]);
export {
  test as default
};
