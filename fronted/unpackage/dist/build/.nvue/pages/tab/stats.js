import { ref, computed, onMounted, resolveComponent, openBlock, createElementBlock, createElementVNode, normalizeStyle, createVNode, withCtx, toDisplayString, createCommentVNode, normalizeClass, withModifiers, onUnmounted, Fragment, renderList, createTextVNode, nextTick, createBlock, unref } from "vue";
import { _ as _export_sfc, o as onLoad, f as formatAppLog, B as BASE_URL, r as request, a as onShow, b as onHide } from "../../_plugin-vue_export-helper.js";
const _style_0$2 = { "test-page-root": { "": { "flex": 1, "backgroundColor": "#1a1a1a", "flexDirection": "column" } }, "custom-navbar": { "": { "position": "fixed", "top": 0, "left": 0, "width": "750rpx", "backgroundColor": "#1a1a1a" } }, "navbar-content": { "": { "height": 44, "flexDirection": "row", "alignItems": "center", "justifyContent": "center" } }, "navbar-title": { "": { "color": "#ffffff", "fontSize": 16, "fontWeight": "bold" } }, "content-wrapper": { "": { "flex": 1, "flexDirection": "column", "alignItems": "center", "width": "750rpx", "paddingBottom": "20rpx" } }, "teacher-tools": { "": { "width": "750rpx", "paddingTop": "40rpx", "paddingRight": "30rpx", "paddingBottom": "40rpx", "paddingLeft": "30rpx" } }, "teacher-card": { "": { "backgroundColor": "#ffffff", "borderRadius": "12rpx", "paddingTop": "20rpx", "paddingRight": "20rpx", "paddingBottom": "20rpx", "paddingLeft": "20rpx" } }, "teacher-title": { "": { "fontSize": "34rpx", "fontWeight": "bold", "marginBottom": "10rpx", "color": "#333333" } }, "teacher-actions": { "": { "flexDirection": "row" } }, "teacher-btn": { "": { "backgroundColor": "#20C997", "paddingTop": "10rpx", "paddingRight": "20rpx", "paddingBottom": "10rpx", "paddingLeft": "20rpx", "borderRadius": "8rpx" } }, "teacher-btn-text": { "": { "color": "#ffffff", "fontSize": "28rpx" } }, "student-container": { "": { "flexDirection": "column", "width": "750rpx", "alignItems": "center" } }, "header-info": { "": { "paddingTop": "40rpx", "paddingRight": "30rpx", "paddingBottom": "20rpx", "paddingLeft": "30rpx", "alignItems": "center" } }, "project-name": { "": { "fontSize": "36rpx", "fontWeight": "bold", "marginBottom": "10rpx", "color": "#ffffff" } }, "standard-badge": { "": { "backgroundColor": "rgba(32,201,151,0.2)", "paddingTop": "8rpx", "paddingRight": "20rpx", "paddingBottom": "8rpx", "paddingLeft": "20rpx", "borderRadius": "12rpx", "marginBottom": "16rpx" } }, "badge-text": { "": { "color": "#20C997", "fontSize": "24rpx", "fontWeight": "bold" } }, "standard-desc": { "": { "fontSize": "28rpx", "color": "#aaaaaa", "marginTop": "10rpx" } }, "test-type-switch": { "": { "marginTop": "20rpx", "flexDirection": "column", "alignItems": "center" } }, "switch-btn": { "": { "backgroundColor": "rgba(255,255,255,0.1)", "paddingTop": "12rpx", "paddingRight": "36rpx", "paddingBottom": "12rpx", "paddingLeft": "36rpx", "borderRadius": "30rpx", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(32,201,151,0.3)" } }, "switch-btn-text": { "": { "color": "#20C997", "fontSize": "28rpx" } }, "type-selector": { "": { "backgroundColor": "rgba(0,0,0,0.4)", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.1)", "borderRadius": "16rpx", "marginTop": "10rpx" } }, "type-item": { "": { "paddingTop": "16rpx", "paddingRight": "40rpx", "paddingBottom": "16rpx", "paddingLeft": "40rpx", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "rgba(255,255,255,0.08)" } }, "type-item-text": { "": { "color": "#ffffff", "fontSize": "28rpx", "textAlign": "center" } }, "camera-area": { "": { "width": "750rpx", "height": "562.5rpx", "backgroundColor": "#000000", "position": "relative", "justifyContent": "center", "alignItems": "center", "borderTopWidth": 1, "borderTopStyle": "solid", "borderTopColor": "#333333", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "#333333" } }, "real-camera": { "": { "width": "750rpx", "height": "562.5rpx" } }, "camera-error-view": { "": { "width": "750rpx", "height": "562.5rpx", "backgroundColor": "#222222", "justifyContent": "center", "alignItems": "center" } }, "error-text": { "": { "color": "#ff6b6b", "fontSize": "30rpx", "marginBottom": "20rpx" } }, "retry-btn": { "": { "backgroundColor": "#333333", "paddingTop": "10rpx", "paddingRight": "30rpx", "paddingBottom": "10rpx", "paddingLeft": "30rpx", "borderRadius": "8rpx", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#444444" } }, "retry-text": { "": { "color": "#ffffff", "fontSize": "28rpx" } }, "camera-overlay-content": { "": { "position": "absolute", "top": 0, "left": 0, "width": "750rpx", "height": "562.5rpx" } }, "count-overlay": { "": { "position": "absolute", "top": "200rpx", "left": "375rpx", "transform": "translateX(-50%)", "flexDirection": "row", "alignItems": "flex-end", "justifyContent": "center" } }, "count-val": { "": { "fontSize": "100rpx", "fontWeight": "800", "color": "#20C997", "lineHeight": "100rpx" } }, "count-label": { "": { "fontSize": "30rpx", "color": "rgba(255,255,255,0.8)", "marginLeft": "12rpx", "fontWeight": "bold", "marginBottom": "10rpx" } }, "progress-bar-container": { "": { "position": "absolute", "bottom": 0, "left": 0, "width": "750rpx", "height": "10rpx", "backgroundColor": "rgba(255,255,255,0.1)" } }, "progress-fill": { "": { "height": "10rpx", "backgroundColor": "#20C997" } }, "status-tips": { "": { "position": "absolute", "bottom": "60rpx", "left": 0, "width": "750rpx", "flexDirection": "row", "justifyContent": "center" } }, "status-text": { "": { "backgroundColor": "rgba(0,0,0,0.7)", "paddingTop": "16rpx", "paddingRight": "48rpx", "paddingBottom": "16rpx", "paddingLeft": "48rpx", "borderRadius": "50rpx", "fontSize": "32rpx", "color": "#ffffff", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.1)" } }, "valid-text": { "": { "color": "#20C997", "backgroundColor": "rgba(32,201,151,0.15)", "borderColor": "rgba(32,201,151,0.4)" } }, "action-area": { "": { "width": "750rpx", "paddingTop": "20rpx", "paddingRight": "40rpx", "paddingBottom": "60rpx", "paddingLeft": "40rpx", "alignItems": "center" } }, "timer-box": { "": { "marginBottom": "40rpx", "backgroundColor": "rgba(255,255,255,0.05)", "paddingTop": "16rpx", "paddingRight": "40rpx", "paddingBottom": "16rpx", "paddingLeft": "40rpx", "borderRadius": "20rpx", "alignItems": "center", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.05)" } }, "timer-label": { "": { "fontSize": "24rpx", "color": "#888888", "marginBottom": "4rpx" } }, "timer-text": { "": { "fontSize": "60rpx", "fontWeight": "bold", "color": "#ffffff" } }, "last-result-box": { "": { "marginTop": 20, "backgroundColor": "#2a2a2a", "borderRadius": 12, "paddingTop": 15, "paddingRight": 15, "paddingBottom": 15, "paddingLeft": 15, "width": "600rpx", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#333333" } }, "result-title": { "": { "color": "#ffffff", "fontSize": "32rpx", "fontWeight": "bold", "marginBottom": "20rpx", "textAlign": "center" } }, "result-row": { "": { "flexDirection": "row", "justifyContent": "space-between", "marginBottom": "10rpx" } }, "result-label": { "": { "color": "#888888", "fontSize": "28rpx" } }, "result-value": { "": { "color": "#20C997", "fontSize": "32rpx", "fontWeight": "bold" } }, "btn-group": { "": { "flexDirection": "row", "width": "600rpx", "justifyContent": "center" } }, "testing-btns": { "": { "flexDirection": "row", "flex": 1, "justifyContent": "space-between" } }, "main-btn": { "": { "flex": 1, "backgroundImage": "linear-gradient(to bottom right, #20C997, #17a077)", "height": "110rpx", "alignItems": "center", "justifyContent": "center", "borderRadius": "60rpx" } }, "sub-btn": { "": { "flex": 1, "height": "110rpx", "alignItems": "center", "justifyContent": "center", "borderRadius": "60rpx", "marginTop": 0, "marginRight": "10rpx", "marginBottom": 0, "marginLeft": "10rpx" } }, "stop-btn": { "": { "backgroundImage": "linear-gradient(to bottom right, #ff6b6b, #ee5253)" } }, "mock-btn": { "": { "backgroundColor": "rgba(255,255,255,0.1)", "borderWidth": 1, "borderStyle": "solid", "borderColor": "rgba(255,255,255,0.1)" } }, "btn-text": { "": { "color": "#ffffff", "fontSize": "36rpx", "fontWeight": "bold" } }, "mock-text": { "": { "color": "#cccccc", "fontSize": "32rpx" } }, "guide-modal": { "": { "position": "fixed", "top": 0, "left": 0, "bottom": 0, "right": 0, "backgroundColor": "rgba(0,0,0,0.8)", "justifyContent": "center", "alignItems": "center" } }, "guide-content": { "": { "backgroundColor": "#ffffff", "width": "600rpx", "borderRadius": "20rpx", "paddingTop": "40rpx", "paddingRight": "40rpx", "paddingBottom": "40rpx", "paddingLeft": "40rpx", "alignItems": "center" } }, "guide-title": { "": { "fontSize": "36rpx", "fontWeight": "bold", "marginBottom": "30rpx", "color": "#333333" } }, "guide-visual": { "": { "width": "200rpx", "height": "200rpx", "backgroundColor": "#f5f5f5", "borderRadius": "20rpx", "alignItems": "center", "justifyContent": "center", "marginBottom": "30rpx" } }, "guide-emoji": { "": { "fontSize": "80rpx" } }, "guide-desc": { "": { "fontSize": "28rpx", "color": "#666666", "textAlign": "center", "marginBottom": "40rpx" } }, "guide-btn": { "": { "backgroundColor": "#20C997", "paddingTop": "10rpx", "paddingRight": "60rpx", "paddingBottom": "10rpx", "paddingLeft": "60rpx", "borderRadius": "40rpx" } }, "guide-btn-text": { "": { "color": "#ffffff", "fontSize": "30rpx" } }, "h5-camera-wrapper": { "": { "width": "750rpx", "height": "562.5rpx", "justifyContent": "center", "alignItems": "center", "backgroundColor": "#333333" } } };
const _sfc_main$2 = {
  __name: "student-test",
  setup(__props, { expose: __expose }) {
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
    onMounted(() => {
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
          success: () => formatAppLog("log", "at components/student-test/student-test.nvue:235", "Start record success"),
          fail: (e) => {
            formatAppLog("error", "at components/student-test/student-test.nvue:237", "Start record fail", e);
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
            formatAppLog("error", "at components/student-test/student-test.nvue:295", "Stop record fail", e);
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
        formatAppLog("error", "at components/student-test/student-test.nvue:322", e);
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
      formatAppLog("error", "at components/student-test/student-test.nvue:453", "Camera Error:", e);
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
    return (_ctx, _cache) => {
      const _component_button = resolveComponent("button");
      return openBlock(), createElementBlock("view", {
        class: "test-page-root",
        renderWhole: true
      }, [
        createElementVNode("view", {
          class: "custom-navbar",
          style: normalizeStyle({ paddingTop: statusBarHeight.value + "px" })
        }, [
          createElementVNode("view", { class: "navbar-content" }, [
            createElementVNode("u-text", { class: "navbar-title" }, "体能测试")
          ])
        ], 4),
        createElementVNode("scroll-view", {
          scrollY: "true",
          class: "content-wrapper",
          style: normalizeStyle({ paddingTop: statusBarHeight.value + 44 + "px" })
        }, [
          role.value === "teacher" ? (openBlock(), createElementBlock("view", {
            key: 0,
            class: "teacher-tools"
          }, [
            createElementVNode("view", { class: "teacher-card" }, [
              createElementVNode("u-text", { class: "teacher-title" }, "教师工具"),
              createElementVNode("view", { class: "teacher-actions" }, [
                createVNode(_component_button, {
                  class: "teacher-btn",
                  onClick: gotoStudents
                }, {
                  default: withCtx(() => [
                    createElementVNode("u-text", { class: "teacher-btn-text" }, "学员管理")
                  ]),
                  _: 1
                })
              ])
            ])
          ])) : (openBlock(), createElementBlock("view", {
            key: 1,
            class: "student-container"
          }, [
            createElementVNode("view", { class: "header-info" }, [
              createElementVNode("u-text", { class: "project-name" }, toDisplayString(projectName.value), 1),
              createElementVNode("view", { class: "standard-badge" }, [
                createElementVNode("u-text", { class: "badge-text" }, "国家学生体质健康标准")
              ]),
              createElementVNode("u-text", { class: "standard-desc" }, "动作标准：" + toDisplayString(standardDesc.value), 1),
              createElementVNode("view", { class: "test-type-switch" }, [
                createVNode(_component_button, {
                  class: "switch-btn",
                  onClick: showTypeSelector
                }, {
                  default: withCtx(() => [
                    createElementVNode("u-text", { class: "switch-btn-text" }, "切换测试类型")
                  ]),
                  _: 1
                }),
                showSelector.value ? (openBlock(), createElementBlock("view", {
                  key: 0,
                  class: "type-selector"
                }, [
                  createElementVNode("view", {
                    class: "type-item",
                    onClick: _cache[0] || (_cache[0] = ($event) => switchTestType("引体向上", "pull-up"))
                  }, [
                    createElementVNode("u-text", { class: "type-item-text" }, "引体向上")
                  ]),
                  createElementVNode("view", {
                    class: "type-item",
                    onClick: _cache[1] || (_cache[1] = ($event) => switchTestType("仰卧起坐", "sit-up"))
                  }, [
                    createElementVNode("u-text", { class: "type-item-text" }, "仰卧起坐")
                  ]),
                  createElementVNode("view", {
                    class: "type-item",
                    onClick: _cache[2] || (_cache[2] = ($event) => switchTestType("俯卧撑", "push-up"))
                  }, [
                    createElementVNode("u-text", { class: "type-item-text" }, "俯卧撑")
                  ])
                ])) : createCommentVNode("", true)
              ])
            ]),
            createElementVNode("view", { class: "camera-area" }, [
              showCamera.value ? (openBlock(), createElementBlock("camera", {
                key: 0,
                class: "real-camera",
                devicePosition: cameraPosition.value,
                flash: "off",
                onError: handleCameraError
              }, null, 40, ["devicePosition"])) : createCommentVNode("", true),
              showCamera.value ? (openBlock(), createElementBlock("view", {
                key: 1,
                class: "camera-controls"
              }, [
                createVNode(_component_button, {
                  class: "switch-cam-btn",
                  onClick: toggleCamera
                }, {
                  default: withCtx(() => [
                    createElementVNode("u-text", { class: "switch-text" }, "📷 切换")
                  ]),
                  _: 1
                })
              ])) : createCommentVNode("", true),
              !showCamera.value ? (openBlock(), createElementBlock("view", {
                key: 2,
                class: "camera-error-view"
              }, [
                createElementVNode("u-text", { class: "error-text" }, "无法访问摄像头"),
                createVNode(_component_button, {
                  class: "retry-btn",
                  onClick: retryCamera
                }, {
                  default: withCtx(() => [
                    createElementVNode("u-text", { class: "retry-text" }, "重试")
                  ]),
                  _: 1
                }),
                createVNode(_component_button, {
                  class: "retry-btn setting-btn",
                  onClick: openSysSettings,
                  style: { "margin-top": "20rpx", "background-color": "#555" }
                }, {
                  default: withCtx(() => [
                    createElementVNode("u-text", { class: "retry-text" }, "去设置开启权限")
                  ]),
                  _: 1
                })
              ])) : createCommentVNode("", true),
              isTesting.value ? (openBlock(), createElementBlock("view", {
                key: 3,
                class: "camera-overlay-content"
              }, [
                createElementVNode("view", { class: "count-overlay" }, [
                  createElementVNode("u-text", { class: "count-val" }, toDisplayString(count.value), 1),
                  createElementVNode("u-text", { class: "count-label" }, "次")
                ]),
                createElementVNode("view", { class: "progress-bar-container" }, [
                  createElementVNode("view", {
                    class: "progress-fill",
                    style: normalizeStyle({ width: progressPercent.value + "%" })
                  }, null, 4)
                ]),
                createElementVNode("view", { class: "status-tips" }, [
                  createElementVNode("u-text", {
                    class: normalizeClass(["status-text", [isStandard.value ? "valid-text" : ""]])
                  }, toDisplayString(statusText.value), 3)
                ])
              ])) : createCommentVNode("", true)
            ]),
            createElementVNode("view", { class: "action-area" }, [
              createElementVNode("view", { class: "timer-box" }, [
                createElementVNode("u-text", { class: "timer-label" }, toDisplayString(isTesting.value ? "测试用时" : lastResult.value ? "上次用时" : "测试用时"), 1),
                createElementVNode("u-text", { class: "timer-text" }, toDisplayString(isTesting.value ? formatTime(duration.value) : lastResult.value ? lastResult.value.duration : "00:00"), 1)
              ]),
              !isTesting.value && lastResult.value ? (openBlock(), createElementBlock("view", {
                key: 0,
                class: "last-result-box"
              }, [
                createElementVNode("u-text", { class: "result-title" }, "上次成绩 (" + toDisplayString(projectName.value) + ")", 1),
                createElementVNode("view", { class: "result-row" }, [
                  createElementVNode("u-text", { class: "result-label" }, "数量："),
                  createElementVNode("u-text", { class: "result-value" }, toDisplayString(lastResult.value.count) + " 次", 1)
                ]),
                createElementVNode("view", { class: "result-row" }, [
                  createElementVNode("u-text", { class: "result-label" }, "用时："),
                  createElementVNode("u-text", { class: "result-value" }, toDisplayString(lastResult.value.duration), 1)
                ])
              ])) : createCommentVNode("", true),
              createElementVNode("view", { class: "btn-group" }, [
                !isTesting.value ? (openBlock(), createElementBlock("view", {
                  key: 0,
                  class: "main-btn start-btn",
                  onClick: startTest
                }, [
                  createElementVNode("u-text", { class: "btn-text" }, toDisplayString(lastResult.value ? "再次测试" : "开始测试"), 1)
                ])) : (openBlock(), createElementBlock("view", {
                  key: 1,
                  class: "testing-btns"
                }, [
                  createElementVNode("view", {
                    class: "sub-btn stop-btn",
                    onClick: endTest
                  }, [
                    createElementVNode("u-text", { class: "btn-text" }, "结束测试")
                  ]),
                  createElementVNode("view", {
                    class: "sub-btn mock-btn",
                    onClick: mockCount
                  }, [
                    createElementVNode("u-text", { class: "btn-text mock-text" }, "+1 模拟")
                  ])
                ]))
              ])
            ])
          ])),
          showGuide.value ? (openBlock(), createElementBlock("view", {
            key: 2,
            class: "guide-modal",
            onClick: _cache[5] || (_cache[5] = ($event) => showGuide.value = false)
          }, [
            createElementVNode("view", {
              class: "guide-content",
              onClick: _cache[4] || (_cache[4] = withModifiers(() => {
              }, ["stop"]))
            }, [
              createElementVNode("u-text", { class: "guide-title" }, "动作指南"),
              createElementVNode("view", { class: "guide-visual" }, [
                createElementVNode("u-text", { class: "guide-emoji" }, toDisplayString(projectEmoji.value), 1)
              ]),
              createElementVNode("u-text", { class: "guide-desc" }, toDisplayString(standardDesc.value), 1),
              createVNode(_component_button, {
                class: "guide-btn",
                onClick: _cache[3] || (_cache[3] = ($event) => showGuide.value = false)
              }, {
                default: withCtx(() => [
                  createElementVNode("u-text", { class: "guide-btn-text" }, "我知道了")
                ]),
                _: 1
              })
            ])
          ])) : createCommentVNode("", true)
        ], 4)
      ]);
    };
  }
};
const StudentTest = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["styles", [_style_0$2]]]);
const _style_0$1 = { "teacher-test-page": { "": { "flex": 1, "backgroundColor": "#f8f9fa", "display": "flex", "flexDirection": "column", "height": 100 } }, "custom-nav-bar": { "": { "backgroundColor": "#ffffff", "width": "750rpx", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "#eeeeee" } }, "nav-status-bar": { "": { "height": 20, "width": "750rpx" } }, "nav-content": { "": { "height": 44, "width": "750rpx", "display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "center", "position": "relative" } }, "nav-title": { "": { "color": "#333333", "fontSize": "32rpx", "fontWeight": "bold" } }, "header-tabs": { "": { "backgroundColor": "#ffffff", "display": "flex", "flexDirection": "row", "paddingTop": 0, "paddingRight": "20rpx", "paddingBottom": 0, "paddingLeft": "20rpx", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "#eeeeee", "zIndex": 99 } }, "tab-item": { "": { "flex": 1, "textAlign": "center", "paddingTop": "30rpx", "paddingRight": 0, "paddingBottom": "30rpx", "paddingLeft": 0, "position": "relative", "fontSize": "30rpx", "color": "#666666" }, ".active": { "color": "#20C997", "fontWeight": "bold" } }, "tab-indicator": { "": { "position": "absolute", "bottom": 0, "left": 50, "transform": "translateX(-50%)", "width": "40rpx", "height": "6rpx", "backgroundColor": "#20C997", "borderRadius": "4rpx" } }, "content-area": { "": { "flex": 1, "paddingTop": "20rpx", "paddingRight": "20rpx", "paddingBottom": "20rpx", "paddingLeft": "20rpx" } }, "live-header": { "": { "display": "flex", "flexDirection": "row", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "20rpx" } }, "live-title": { "": { "fontSize": "32rpx", "fontWeight": "bold", "color": "#333333" } }, "live-badge": { "": { "backgroundColor": "rgba(32,201,151,0.1)", "paddingTop": "4rpx", "paddingRight": "12rpx", "paddingBottom": "4rpx", "paddingLeft": "12rpx", "borderRadius": "8rpx" } }, "live-badge-text": { "": { "color": "#20C997", "fontSize": "24rpx" } }, "student-live-grid": { "": { "display": "flex", "flexDirection": "row", "flexWrap": "wrap", "justifyContent": "space-between" } }, "student-monitor-card": { "": { "width": "340rpx", "backgroundColor": "#ffffff", "borderRadius": "12rpx", "overflow": "hidden", "boxShadow": "0 2rpx 8rpx rgba(0,0,0,0.05)", "marginBottom": "20rpx" } }, "monitor-video-placeholder": { "": { "height": "200rpx", "backgroundColor": "#1a1a1a", "position": "relative", "display": "flex", "alignItems": "center", "justifyContent": "center" } }, "ai-overlay": { "": { "position": "absolute", "top": "10rpx", "left": "10rpx", "color": "#00ff00", "fontSize": "20rpx", "backgroundColor": "rgba(0,0,0,0.5)", "paddingTop": "2rpx", "paddingRight": "6rpx", "paddingBottom": "2rpx", "paddingLeft": "6rpx", "borderRadius": "4rpx" } }, "live-score": { "": { "position": "absolute", "bottom": "10rpx", "right": "10rpx", "color": "#ffffff", "fontWeight": "bold", "fontSize": "36rpx" } }, "pose-skeleton": { "": { "width": "60rpx", "height": "100rpx", "position": "relative", "opacity": 0.8 } }, "bone": { "": { "backgroundColor": "#00ff00", "position": "absolute" }, ".head": { "width": "16rpx", "height": "16rpx", "borderRadius": 50, "top": 0, "left": "22rpx" }, ".body": { "width": "4rpx", "height": "40rpx", "top": "16rpx", "left": "28rpx" }, ".arm-l": { "width": "20rpx", "height": "4rpx", "top": "24rpx", "left": "8rpx", "transform": "rotate(20deg)" }, ".arm-r": { "width": "20rpx", "height": "4rpx", "top": "24rpx", "right": "8rpx", "transform": "rotate(-20deg)" }, ".leg-l": { "width": "4rpx", "height": "30rpx", "top": "56rpx", "left": "24rpx", "transform": "rotate(10deg)" }, ".leg-r": { "width": "4rpx", "height": "30rpx", "top": "56rpx", "left": "34rpx", "transform": "rotate(-10deg)" } }, "ai-bbox": { "": { "position": "absolute", "top": "20rpx", "left": 20, "width": 60, "height": 80, "borderWidth": "2rpx", "borderStyle": "dashed", "borderRadius": "8rpx" } }, "bbox-label": { "": { "position": "absolute", "top": "-24rpx", "left": "-2rpx", "color": "#000000", "fontSize": "18rpx", "paddingTop": "2rpx", "paddingRight": "6rpx", "paddingBottom": "2rpx", "paddingLeft": "6rpx", "borderRadius": "4rpx", "fontWeight": "bold" } }, "monitor-info": { "": { "paddingTop": "16rpx", "paddingRight": "16rpx", "paddingBottom": "16rpx", "paddingLeft": "16rpx" } }, "s-name": { "": { "fontSize": "28rpx", "fontWeight": "bold", "color": "#333333" } }, "s-action": { "": { "fontSize": "24rpx", "color": "#666666", "marginTop": "4rpx", "marginRight": 0, "marginBottom": "4rpx", "marginLeft": 0 } }, "s-status": { "": { "fontSize": "22rpx", "paddingTop": "4rpx", "paddingRight": "10rpx", "paddingBottom": "4rpx", "paddingLeft": "10rpx", "borderRadius": "6rpx", "marginTop": "8rpx", "textAlign": "center" }, ".good": { "backgroundColor": "#e6fffa", "color": "#20C997" }, ".warning": { "backgroundColor": "#fff5f5", "color": "#ff6b6b" } }, "chart-card": { "": { "backgroundColor": "#ffffff", "borderRadius": "20rpx", "paddingTop": "30rpx", "paddingRight": "30rpx", "paddingBottom": "30rpx", "paddingLeft": "30rpx", "marginBottom": "24rpx", "boxShadow": "0 4rpx 12rpx rgba(0,0,0,0.03)" } }, "card-title": { "": { "marginBottom": "30rpx", "borderLeftWidth": "8rpx", "borderLeftStyle": "solid", "borderLeftColor": "#20C997", "paddingLeft": "20rpx" } }, "card-title-text": { "": { "fontSize": "32rpx", "fontWeight": "bold", "color": "#333333" } }, "skills-matrix": { "": { "display": "flex", "flexDirection": "column" } }, "skill-row": { "": { "display": "flex", "flexDirection": "row", "alignItems": "center", "marginBottom": "20rpx" } }, "skill-name": { "": { "fontSize": "26rpx", "color": "#555555", "width": "120rpx", "marginRight": "20rpx" } }, "skill-track": { "": { "flex": 1, "height": "20rpx", "backgroundColor": "#f0f0f0", "borderRadius": "10rpx", "overflow": "hidden" } }, "skill-bar": { "": { "height": 100, "borderRadius": "10rpx", "transitionProperty": "width", "transitionDuration": 1e3 } }, "skill-val": { "": { "fontSize": "26rpx", "fontWeight": "bold", "color": "#333333", "width": "60rpx", "textAlign": "right" } }, "analysis-summary": { "": { "marginTop": "20rpx", "paddingTop": "20rpx", "paddingRight": "20rpx", "paddingBottom": "20rpx", "paddingLeft": "20rpx", "backgroundColor": "#e6fffa", "borderRadius": "12rpx", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#b2f5ea" } }, "summary-text": { "": { "fontSize": "28rpx", "color": "#234e52" } }, "highlight": { "": { "color": "#d53f8c", "fontWeight": "bold" } }, "bar-chart": { "": { "display": "flex", "flexDirection": "row", "justifyContent": "space-around", "alignItems": "flex-end", "height": "320rpx", "paddingBottom": "20rpx", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "#eeeeee" } }, "bar-group": { "": { "display": "flex", "flexDirection": "column", "alignItems": "center", "height": 100, "justifyContent": "flex-end", "flex": 1, "position": "relative" } }, "bar-col": { "": { "width": "60rpx", "height": 85, "backgroundColor": "#f5f5f5", "borderRadius": "20rpx", "position": "relative", "display": "flex", "alignItems": "flex-end" } }, "bar-fill": { "": { "width": 100, "borderRadius": "20rpx", "position": "absolute", "bottom": 0, "left": 0, "transitionProperty": "height", "transitionDuration": 1e3 } }, "bar-val": { "": { "position": "absolute", "top": "-40rpx", "left": 50, "transform": "translateX(-50%)", "fontSize": "22rpx", "color": "#666666", "fontWeight": "bold", "lines": 1, "textOverflow": "clip", "zIndex": 10 } }, "bar-label": { "": { "marginTop": "16rpx", "fontSize": "26rpx", "color": "#666666" } }, "progress-list": { "": { "display": "flex", "flexDirection": "column" } }, "prog-item": { "": { "width": 100, "marginBottom": "30rpx" } }, "prog-header": { "": { "display": "flex", "flexDirection": "row", "justifyContent": "space-between", "marginBottom": "12rpx" } }, "prog-name": { "": { "fontSize": "28rpx", "color": "#444444" } }, "prog-val": { "": { "fontSize": "28rpx", "fontWeight": "bold" } }, "prog-track": { "": { "height": "16rpx", "backgroundColor": "#f0f0f0", "borderRadius": "8rpx", "overflow": "hidden" } }, "prog-bar": { "": { "height": 100, "borderRadius": "8rpx", "transitionProperty": "width", "transitionDuration": 1e3 } }, "history-list": { "": { "backgroundColor": "#ffffff", "borderRadius": "20rpx", "boxShadow": "0 4rpx 12rpx rgba(0,0,0,0.03)" } }, "history-item": { "": { "display": "flex", "flexDirection": "row", "justifyContent": "space-between", "alignItems": "center", "paddingTop": "32rpx", "paddingRight": "32rpx", "paddingBottom": "32rpx", "paddingLeft": "32rpx", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "#f5f5f5" } }, "h-left": { "": { "display": "flex", "flexDirection": "column" } }, "h-date": { "": { "fontSize": "24rpx", "color": "#999999", "marginBottom": "8rpx" } }, "h-name": { "": { "fontSize": "32rpx", "fontWeight": "bold", "color": "#333333" } }, "h-right": { "": { "display": "flex", "flexDirection": "row", "alignItems": "center" } }, "h-stat": { "": { "fontSize": "26rpx", "color": "#666666", "marginRight": "20rpx" }, ".high-pass": { "color": "#20C997", "fontWeight": "bold" } }, "arrow": { "": { "color": "#cccccc", "fontSize": "24rpx" } }, "exception-header": { "": { "backgroundColor": "#ffffff", "paddingTop": "30rpx", "paddingRight": "30rpx", "paddingBottom": "30rpx", "paddingLeft": "30rpx", "borderRadius": "16rpx", "marginBottom": "20rpx", "boxShadow": "0 2rpx 10rpx rgba(0,0,0,0.05)" } }, "ex-stats-row": { "": { "display": "flex", "flexDirection": "row", "justifyContent": "space-around" } }, "ex-stat-item": { "": { "display": "flex", "flexDirection": "column", "alignItems": "center" } }, "ex-stat-num": { "": { "fontSize": "36rpx", "fontWeight": "bold", "color": "#ff6b6b" } }, "ex-stat-desc": { "": { "fontSize": "24rpx", "color": "#999999" } }, "filter-bar": { "": { "display": "flex", "flexDirection": "row", "marginBottom": "20rpx", "backgroundColor": "#ffffff", "paddingTop": "10rpx", "paddingRight": "10rpx", "paddingBottom": "10rpx", "paddingLeft": "10rpx", "borderRadius": "12rpx" } }, "filter-item": { "": { "flex": 1, "textAlign": "center", "paddingTop": "16rpx", "paddingRight": 0, "paddingBottom": "16rpx", "paddingLeft": 0, "fontSize": "28rpx", "color": "#666666", "borderRadius": "8rpx" }, ".active": { "backgroundColor": "#e6f7ff", "color": "#1890ff", "fontWeight": "500" } }, "alert-list": { "": { "paddingBottom": "40rpx" } }, "alert-card": { "": { "backgroundColor": "#ffffff", "borderRadius": "16rpx", "paddingTop": "30rpx", "paddingRight": "30rpx", "paddingBottom": "30rpx", "paddingLeft": "30rpx", "marginBottom": "20rpx", "boxShadow": "0 2rpx 8rpx rgba(0,0,0,0.05)" } }, "alert-header": { "": { "display": "flex", "flexDirection": "row", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "24rpx", "paddingBottom": "20rpx", "borderBottomWidth": 1, "borderBottomStyle": "solid", "borderBottomColor": "#f0f0f0" } }, "alert-header-left": { "": { "display": "flex", "flexDirection": "row", "alignItems": "center" } }, "type-tag": { "": { "fontSize": "22rpx", "paddingTop": "4rpx", "paddingRight": "12rpx", "paddingBottom": "4rpx", "paddingLeft": "12rpx", "borderRadius": "6rpx", "color": "#ffffff", "marginRight": "16rpx" } }, "tag-red": { "": { "backgroundColor": "#ff4d4f" } }, "tag-orange": { "": { "backgroundColor": "#faad14" } }, "tag-blue": { "": { "backgroundColor": "#1890ff" } }, "student-name": { "": { "fontSize": "30rpx", "fontWeight": "500", "color": "#333333", "marginRight": "16rpx" } }, "student-id": { "": { "fontSize": "24rpx", "color": "#999999" } }, "time": { "": { "fontSize": "24rpx", "color": "#999999" } }, "alert-body": { "": { "marginBottom": "24rpx" } }, "data-row": { "": { "display": "flex", "flexDirection": "row", "marginBottom": "16rpx", "fontSize": "28rpx", "alignItems": "center" } }, "label": { "": { "color": "#666666" } }, "value": { "": { "color": "#333333", "fontWeight": "500", "marginRight": "10rpx" }, ".highlight": { "color": "#ff4d4f" } }, "standard": { "": { "color": "#999999", "fontSize": "24rpx" } }, "desc-box": { "": { "backgroundColor": "#f9f9f9", "paddingTop": "16rpx", "paddingRight": "16rpx", "paddingBottom": "16rpx", "paddingLeft": "16rpx", "borderRadius": "8rpx" } }, "desc-title": { "": { "fontSize": "26rpx", "color": "#333333", "fontWeight": "500", "marginBottom": "8rpx" } }, "desc-content": { "": { "fontSize": "26rpx", "color": "#666666" } }, "alert-footer": { "": { "display": "flex", "flexDirection": "row", "justifyContent": "flex-end" } }, "action-btn": { "": { "marginLeft": "20rpx", "marginRight": 0, "fontSize": "24rpx" }, ".ignore": { "color": "#999999", "backgroundColor": "#ffffff", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#dddddd" }, ".notify": { "color": "#1890ff", "backgroundColor": "#ffffff", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#1890ff" }, ".handle": { "backgroundColor": "#20C997", "color": "#ffffff" } }, "empty-state": { "": { "paddingTop": "60rpx", "paddingRight": "60rpx", "paddingBottom": "60rpx", "paddingLeft": "60rpx", "textAlign": "center", "color": "#999999", "fontSize": "28rpx" } }, "@TRANSITION": { "skill-bar": { "property": "width", "duration": 1e3 }, "bar-fill": { "property": "height", "duration": 1e3 }, "prog-bar": { "property": "width", "duration": 1e3 } } };
const _sfc_main$1 = {
  __name: "teacher-tests",
  setup(__props, { expose: __expose }) {
    const currentTab = ref("live");
    const timer = ref(null);
    const statusBarHeight = ref(20);
    onMounted(() => {
      const info = uni.getSystemInfoSync();
      statusBarHeight.value = info.statusBarHeight || 20;
    });
    const liveStudents = ref([
      { name: "张伟", action: "引体向上", currentScore: 8, isAbnormal: false, confidence: 98 },
      { name: "李强", action: "仰卧起坐", currentScore: 24, isAbnormal: true, confidence: 85 },
      { name: "王芳", action: "深蹲", currentScore: 15, isAbnormal: false, confidence: 96 },
      { name: "赵杰", action: "俯卧撑", currentScore: 12, isAbnormal: false, confidence: 99 }
    ]);
    const classSkills = ref([
      { name: "爆发力", val: 85, color: "#ff6b6b" },
      { name: "耐力", val: 72, color: "#4dabf7" },
      { name: "柔韧性", val: 68, color: "#ffd43b" },
      { name: "协调性", val: 90, color: "#20C997" },
      { name: "核心力量", val: 78, color: "#a55eea" }
    ]);
    const classComparison = ref([
      { label: "优秀", value: 15, percent: 30, color: "#20C997" },
      { label: "良好", value: 45, percent: 60, color: "#4dabf7" },
      { label: "及格", value: 30, percent: 45, color: "#ffd43b" },
      { label: "不及格", value: 10, percent: 20, color: "#ff6b6b" }
    ]);
    const passRates = ref([
      { name: "1000米跑", rate: 85 },
      { name: "引体向上", rate: 62 },
      { name: "立定跳远", rate: 94 },
      { name: "坐位体前屈", rate: 78 }
    ]);
    const historyList = ref([
      { date: "2026-05-18", testName: "全员体能摸底测试", count: 128, passRate: 92 },
      { date: "2026-05-10", testName: "力量专项考核", count: 45, passRate: 88 },
      { date: "2026-04-28", testName: "耐力跑测试", count: 128, passRate: 76 }
    ]);
    const currentFilter = ref("all");
    const todayCount = ref(5);
    const alerts = ref([
      {
        id: 1,
        type: "heart_rate",
        typeText: "心率过高",
        typeClass: "tag-red",
        studentName: "张三",
        studentId: "2023001",
        time: "10:30",
        value: "195 bpm",
        standard: "60-180 bpm",
        description: "跑步过程中持续3分钟心率超过安全阈值。",
        level: "urgent"
      },
      {
        id: 2,
        type: "pace",
        typeText: "配速异常",
        typeClass: "tag-orange",
        studentName: "李四",
        studentId: "2023002",
        time: "10:45",
        value: `2'30"/km`,
        standard: `4'00"-8'00"/km`,
        description: "短时间内配速极快，疑似骑车或数据漂移。",
        level: "normal"
      },
      {
        id: 3,
        type: "location",
        typeText: "轨迹异常",
        typeClass: "tag-blue",
        studentName: "王五",
        studentId: "2023003",
        time: "09:15",
        value: "直线穿越",
        standard: "连续轨迹",
        description: "轨迹点之间距离过大，且无中间路径。",
        level: "normal"
      }
    ]);
    const pendingCount = computed(() => alerts.value.length);
    const filteredAlerts = computed(() => {
      if (currentFilter.value === "all")
        return alerts.value;
      return alerts.value.filter((a) => a.level === currentFilter.value);
    });
    const ignoreAlert = (id) => {
      uni.showModal({
        title: "确认忽略",
        content: "忽略后该异常将不再提醒，确认操作？",
        success: (res) => {
          if (res.confirm) {
            alerts.value = alerts.value.filter((a) => a.id !== id);
            uni.showToast({ title: "已忽略", icon: "none" });
          }
        }
      });
    };
    const notifyStudent = (alert) => {
      uni.showToast({ title: `已发送通知给 ${alert.studentName}`, icon: "success" });
    };
    const handleAlert = (alert) => {
      uni.showActionSheet({
        itemList: ["标记为无效成绩", "标记为设备故障", "要求重测"],
        success: (res) => {
          const actions = ["无效成绩", "设备故障", "重测"];
          uni.showToast({ title: `已标记为：${actions[res.tapIndex]}`, icon: "success" });
          alerts.value = alerts.value.filter((a) => a.id !== alert.id);
        }
      });
    };
    const simulateLiveUpdate = () => {
      liveStudents.value.forEach((stu) => {
        if (Math.random() > 0.7)
          stu.currentScore += 1;
        const change = Math.floor(Math.random() * 5) - 2;
        stu.confidence = Math.min(100, Math.max(80, stu.confidence + change));
      });
    };
    const startLiveUpdate = () => {
      if (timer.value)
        clearInterval(timer.value);
      timer.value = setInterval(simulateLiveUpdate, 2e3);
    };
    const stopLiveUpdate = () => {
      if (timer.value) {
        clearInterval(timer.value);
        timer.value = null;
      }
    };
    const onPageShow = () => {
      if (currentTab.value === "live") {
        startLiveUpdate();
      }
    };
    const onPageHide = () => {
      stopLiveUpdate();
    };
    onMounted(() => {
    });
    onUnmounted(() => {
      stopLiveUpdate();
    });
    __expose({
      onPageShow,
      onPageHide
    });
    return (_ctx, _cache) => {
      const _component_button = resolveComponent("button");
      return openBlock(), createElementBlock("view", {
        class: "teacher-test-page",
        renderWhole: true
      }, [
        createElementVNode("view", { class: "custom-nav-bar" }, [
          createElementVNode("view", {
            class: "nav-status-bar",
            style: normalizeStyle({ height: statusBarHeight.value + "px" })
          }, null, 4),
          createElementVNode("view", { class: "nav-content" }, [
            createElementVNode("u-text", { class: "nav-title" }, "测试监控")
          ])
        ]),
        createElementVNode("view", { class: "header-tabs" }, [
          createElementVNode("view", {
            class: normalizeClass(["tab-item", { active: currentTab.value === "live" }]),
            onClick: _cache[0] || (_cache[0] = ($event) => currentTab.value = "live")
          }, [
            createElementVNode("u-text", { class: "tab-title" }, "实时监控"),
            currentTab.value === "live" ? (openBlock(), createElementBlock("view", {
              key: 0,
              class: "tab-indicator"
            })) : createCommentVNode("", true)
          ], 2),
          createElementVNode("view", {
            class: normalizeClass(["tab-item", { active: currentTab.value === "analysis" }]),
            onClick: _cache[1] || (_cache[1] = ($event) => currentTab.value = "analysis")
          }, [
            createElementVNode("u-text", { class: "tab-title" }, "数据分析"),
            currentTab.value === "analysis" ? (openBlock(), createElementBlock("view", {
              key: 0,
              class: "tab-indicator"
            })) : createCommentVNode("", true)
          ], 2),
          createElementVNode("view", {
            class: normalizeClass(["tab-item", { active: currentTab.value === "history" }]),
            onClick: _cache[2] || (_cache[2] = ($event) => currentTab.value = "history")
          }, [
            createElementVNode("u-text", { class: "tab-title" }, "历史回顾"),
            currentTab.value === "history" ? (openBlock(), createElementBlock("view", {
              key: 0,
              class: "tab-indicator"
            })) : createCommentVNode("", true)
          ], 2),
          createElementVNode("view", {
            class: normalizeClass(["tab-item", { active: currentTab.value === "exception" }]),
            onClick: _cache[3] || (_cache[3] = ($event) => currentTab.value = "exception")
          }, [
            createElementVNode("u-text", { class: "tab-title" }, "异常处理"),
            currentTab.value === "exception" ? (openBlock(), createElementBlock("view", {
              key: 0,
              class: "tab-indicator"
            })) : createCommentVNode("", true)
          ], 2)
        ]),
        currentTab.value === "live" ? (openBlock(), createElementBlock("scroll-view", {
          key: 0,
          scrollY: "",
          class: "content-area"
        }, [
          createElementVNode("view", { class: "live-card" }, [
            createElementVNode("view", { class: "live-header" }, [
              createElementVNode("u-text", { class: "live-title" }, "当前正在进行的测试"),
              createElementVNode("view", { class: "live-badge" }, [
                createElementVNode("u-text", { class: "live-badge-text" }, "AI 评分接入中")
              ])
            ]),
            createElementVNode("view", { class: "student-live-grid" }, [
              (openBlock(true), createElementBlock(Fragment, null, renderList(liveStudents.value, (stu, idx) => {
                return openBlock(), createElementBlock("view", {
                  class: "student-monitor-card",
                  key: idx
                }, [
                  createElementVNode("view", { class: "monitor-video-placeholder" }, [
                    createElementVNode("u-text", { class: "ai-overlay" }, "AI Analyzing..."),
                    createElementVNode("view", {
                      class: "ai-bbox",
                      style: normalizeStyle({ borderColor: stu.isAbnormal ? "#ff6b6b" : "#0f0" })
                    }, [
                      createElementVNode("u-text", {
                        class: "bbox-label",
                        style: normalizeStyle({ background: stu.isAbnormal ? "#ff6b6b" : "#0f0" })
                      }, toDisplayString(stu.confidence) + "%", 5)
                    ], 4),
                    createElementVNode("view", { class: "pose-skeleton" }, [
                      createElementVNode("view", { class: "bone head" }),
                      createElementVNode("view", { class: "bone body" }),
                      createElementVNode("view", { class: "bone arm-l" }),
                      createElementVNode("view", { class: "bone arm-r" }),
                      createElementVNode("view", { class: "bone leg-l" }),
                      createElementVNode("view", { class: "bone leg-r" })
                    ]),
                    createElementVNode("u-text", { class: "live-score" }, toDisplayString(stu.currentScore), 1)
                  ]),
                  createElementVNode("view", { class: "monitor-info" }, [
                    createElementVNode("u-text", { class: "s-name" }, toDisplayString(stu.name), 1),
                    createElementVNode("u-text", { class: "s-action" }, toDisplayString(stu.action), 1),
                    stu.isAbnormal ? (openBlock(), createElementBlock("u-text", {
                      key: 0,
                      class: "s-status warning"
                    }, "动作不标准")) : (openBlock(), createElementBlock("u-text", {
                      key: 1,
                      class: "s-status good"
                    }, "动作标准"))
                  ])
                ]);
              }), 128))
            ])
          ])
        ])) : createCommentVNode("", true),
        currentTab.value === "analysis" ? (openBlock(), createElementBlock("scroll-view", {
          key: 1,
          scrollY: "",
          class: "content-area"
        }, [
          createElementVNode("view", { class: "chart-card" }, [
            createElementVNode("view", { class: "card-title" }, [
              createElementVNode("u-text", { class: "card-title-text" }, "班级体能综合模型")
            ]),
            createElementVNode("view", { class: "skills-matrix" }, [
              (openBlock(true), createElementBlock(Fragment, null, renderList(classSkills.value, (skill, idx) => {
                return openBlock(), createElementBlock("view", {
                  class: "skill-row",
                  key: idx
                }, [
                  createElementVNode("u-text", { class: "skill-name" }, toDisplayString(skill.name), 1),
                  createElementVNode("view", { class: "skill-track" }, [
                    createElementVNode("view", {
                      class: "skill-bar",
                      style: normalizeStyle({ width: skill.val + "%", background: skill.color })
                    }, null, 4)
                  ]),
                  createElementVNode("u-text", { class: "skill-val" }, toDisplayString(skill.val), 1)
                ]);
              }), 128))
            ]),
            createElementVNode("view", { class: "analysis-summary" }, [
              createElementVNode("u-text", { class: "summary-text" }, "💡 建议加强  专项训练")
            ])
          ]),
          createElementVNode("view", { class: "chart-card" }, [
            createElementVNode("view", { class: "card-title" }, [
              createElementVNode("u-text", { class: "card-title-text" }, "班级成绩分布对比")
            ]),
            createElementVNode("view", { class: "bar-chart" }, [
              (openBlock(true), createElementBlock(Fragment, null, renderList(classComparison.value, (item, idx) => {
                return openBlock(), createElementBlock("view", {
                  class: "bar-group",
                  key: idx
                }, [
                  createElementVNode("view", { class: "bar-col" }, [
                    createElementVNode("view", {
                      class: "bar-fill",
                      style: normalizeStyle({ height: item.percent + "%", background: item.color })
                    }, [
                      createElementVNode("u-text", { class: "bar-val" }, toDisplayString(item.value) + "人", 1)
                    ], 4)
                  ]),
                  createElementVNode("u-text", { class: "bar-label" }, toDisplayString(item.label), 1)
                ]);
              }), 128))
            ])
          ]),
          createElementVNode("view", { class: "chart-card" }, [
            createElementVNode("view", { class: "card-title" }, [
              createElementVNode("u-text", { class: "card-title-text" }, "各项体能合格率")
            ]),
            createElementVNode("view", { class: "progress-list" }, [
              (openBlock(true), createElementBlock(Fragment, null, renderList(passRates.value, (p, idx) => {
                return openBlock(), createElementBlock("view", {
                  class: "prog-item",
                  key: idx
                }, [
                  createElementVNode("view", { class: "prog-header" }, [
                    createElementVNode("u-text", { class: "prog-name" }, toDisplayString(p.name), 1),
                    createElementVNode("u-text", {
                      class: "prog-val",
                      style: normalizeStyle({ color: p.rate >= 80 ? "#20C997" : "#ff9f43" })
                    }, toDisplayString(p.rate) + "%", 5)
                  ]),
                  createElementVNode("view", { class: "prog-track" }, [
                    createElementVNode("view", {
                      class: "prog-bar",
                      style: normalizeStyle({ width: p.rate + "%", background: p.rate >= 80 ? "#20C997" : "#ff9f43" })
                    }, null, 4)
                  ])
                ]);
              }), 128))
            ])
          ])
        ])) : createCommentVNode("", true),
        currentTab.value === "history" ? (openBlock(), createElementBlock("scroll-view", {
          key: 2,
          scrollY: "",
          class: "content-area"
        }, [
          createElementVNode("view", { class: "history-list" }, [
            (openBlock(true), createElementBlock(Fragment, null, renderList(historyList.value, (h, idx) => {
              return openBlock(), createElementBlock("view", {
                class: "history-item",
                key: idx
              }, [
                createElementVNode("view", { class: "h-left" }, [
                  createElementVNode("u-text", { class: "h-date" }, toDisplayString(h.date), 1),
                  createElementVNode("u-text", { class: "h-name" }, toDisplayString(h.testName), 1)
                ]),
                createElementVNode("view", { class: "h-right" }, [
                  createElementVNode("u-text", { class: "h-stat" }, "参与: " + toDisplayString(h.count) + "人", 1),
                  createElementVNode("u-text", {
                    class: normalizeClass(["h-stat", { "high-pass": h.passRate >= 90 }])
                  }, "合格: " + toDisplayString(h.passRate) + "%", 3),
                  createElementVNode("u-text", { class: "arrow" }, ">")
                ])
              ]);
            }), 128))
          ])
        ])) : createCommentVNode("", true),
        currentTab.value === "exception" ? (openBlock(), createElementBlock("scroll-view", {
          key: 3,
          scrollY: "",
          class: "content-area"
        }, [
          createElementVNode("view", { class: "exception-header" }, [
            createElementVNode("view", { class: "ex-stats-row" }, [
              createElementVNode("view", { class: "ex-stat-item" }, [
                createElementVNode("u-text", { class: "ex-stat-num" }, toDisplayString(pendingCount.value), 1),
                createElementVNode("u-text", { class: "ex-stat-desc" }, "待处理")
              ]),
              createElementVNode("view", { class: "ex-stat-item" }, [
                createElementVNode("u-text", { class: "ex-stat-num" }, toDisplayString(todayCount.value), 1),
                createElementVNode("u-text", { class: "ex-stat-desc" }, "今日新增")
              ])
            ])
          ]),
          createElementVNode("view", { class: "filter-bar" }, [
            createElementVNode("u-text", {
              class: normalizeClass(["filter-item", { active: currentFilter.value === "all" }]),
              onClick: _cache[4] || (_cache[4] = ($event) => currentFilter.value = "all")
            }, "全部", 2),
            createElementVNode("u-text", {
              class: normalizeClass(["filter-item", { active: currentFilter.value === "urgent" }]),
              onClick: _cache[5] || (_cache[5] = ($event) => currentFilter.value = "urgent")
            }, "紧急", 2),
            createElementVNode("u-text", {
              class: normalizeClass(["filter-item", { active: currentFilter.value === "normal" }]),
              onClick: _cache[6] || (_cache[6] = ($event) => currentFilter.value = "normal")
            }, "一般", 2)
          ]),
          createElementVNode("view", { class: "alert-list" }, [
            (openBlock(true), createElementBlock(Fragment, null, renderList(filteredAlerts.value, (alert, index) => {
              return openBlock(), createElementBlock("view", {
                class: "alert-card",
                key: alert.id
              }, [
                createElementVNode("view", { class: "alert-header" }, [
                  createElementVNode("view", { class: "alert-header-left" }, [
                    createElementVNode("u-text", {
                      class: normalizeClass(["type-tag", alert.typeClass])
                    }, toDisplayString(alert.typeText), 3),
                    createElementVNode("u-text", { class: "student-name" }, toDisplayString(alert.studentName), 1),
                    createElementVNode("u-text", { class: "student-id" }, toDisplayString(alert.studentId), 1)
                  ]),
                  createElementVNode("u-text", { class: "time" }, toDisplayString(alert.time), 1)
                ]),
                createElementVNode("view", { class: "alert-body" }, [
                  createElementVNode("view", { class: "data-row" }, [
                    createElementVNode("u-text", { class: "label" }, "异常数据："),
                    createElementVNode("u-text", { class: "value highlight" }, toDisplayString(alert.value), 1),
                    createElementVNode("u-text", { class: "standard" }, "（标准: " + toDisplayString(alert.standard) + "）", 1)
                  ]),
                  createElementVNode("view", { class: "desc-box" }, [
                    createElementVNode("u-text", { class: "desc-title" }, "说明："),
                    createElementVNode("u-text", { class: "desc-content" }, toDisplayString(alert.description), 1)
                  ])
                ]),
                createElementVNode("view", { class: "alert-footer" }, [
                  createVNode(_component_button, {
                    class: "action-btn ignore",
                    size: "mini",
                    onClick: ($event) => ignoreAlert(alert.id)
                  }, {
                    default: withCtx(() => [
                      createTextVNode("忽略")
                    ]),
                    _: 2
                  }, 1032, ["onClick"]),
                  createVNode(_component_button, {
                    class: "action-btn notify",
                    size: "mini",
                    onClick: ($event) => notifyStudent(alert)
                  }, {
                    default: withCtx(() => [
                      createTextVNode("通知")
                    ]),
                    _: 2
                  }, 1032, ["onClick"]),
                  createVNode(_component_button, {
                    class: "action-btn handle",
                    size: "mini",
                    onClick: ($event) => handleAlert(alert)
                  }, {
                    default: withCtx(() => [
                      createTextVNode("处理")
                    ]),
                    _: 2
                  }, 1032, ["onClick"])
                ])
              ]);
            }), 128)),
            filteredAlerts.value.length === 0 ? (openBlock(), createElementBlock("view", {
              key: 0,
              class: "empty-state"
            }, [
              createElementVNode("u-text", { class: "empty-text" }, "暂无异常数据")
            ])) : createCommentVNode("", true)
          ])
        ])) : createCommentVNode("", true)
      ]);
    };
  }
};
const TeacherTests = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["styles", [_style_0$1]]]);
const _style_0 = { "container": { "": { "flex": 1 } } };
const _sfc_main = {
  __name: "stats",
  setup(__props) {
    const role = ref(uni.getStorageSync("userRole") || "student");
    const studentTestRef = ref(null);
    const teacherTestsRef = ref(null);
    onShow(() => {
      role.value = uni.getStorageSync("userRole") || "student";
      nextTick(() => {
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
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("scroll-view", {
        scrollY: true,
        showScrollbar: true,
        enableBackToTop: true,
        bubble: "true",
        style: { flexDirection: "column" }
      }, [
        createElementVNode("view", { class: "container" }, [
          role.value === "student" ? (openBlock(), createBlock(unref(StudentTest), {
            key: 0,
            ref_key: "studentTestRef",
            ref: studentTestRef
          }, null, 512)) : (openBlock(), createBlock(TeacherTests, {
            key: 1,
            ref_key: "teacherTestsRef",
            ref: teacherTestsRef
          }, null, 512))
        ])
      ]);
    };
  }
};
const stats = /* @__PURE__ */ _export_sfc(_sfc_main, [["styles", [_style_0]]]);
export {
  stats as default
};
