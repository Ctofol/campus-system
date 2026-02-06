import { _ as _export_sfc, f as formatAppLog } from "../../_plugin-vue_export-helper.js";
import { resolveComponent, openBlock, createElementBlock, createElementVNode, createCommentVNode, toDisplayString, createVNode, withCtx, createTextVNode } from "vue";
const _style_0 = { "page": { "": { "flex": 1, "backgroundColor": "#f8f8f8", "flexDirection": "column" } }, "header": { "": { "paddingTop": 60, "paddingRight": 20, "paddingBottom": 20, "paddingLeft": 20, "backgroundColor": "#ffffff" } }, "title": { "": { "fontSize": 20, "fontWeight": "bold" } }, "subtitle": { "": { "fontSize": 12, "color": "#666666", "marginTop": 5 } }, "camera-box": { "": { "width": "750rpx", "height": "500rpx", "backgroundColor": "#333333", "marginTop": 10, "position": "relative", "justifyContent": "center", "alignItems": "center" } }, "camera-placeholder": { "": { "position": "absolute", "top": "200rpx", "left": 0, "width": "750rpx", "alignItems": "center" } }, "camera-view": { "": { "width": "750rpx", "height": "500rpx", "position": "absolute", "top": 0, "left": 0 } }, "error-overlay": { "": { "position": "absolute", "top": 0, "left": 0, "width": "750rpx", "height": "500rpx", "backgroundColor": "rgba(0,0,0,0.8)", "justifyContent": "center", "alignItems": "center" } }, "error-text": { "": { "color": "#ff0000", "fontSize": 18, "fontWeight": "bold", "marginBottom": 10 } }, "error-desc": { "": { "color": "#ffffff", "fontSize": 14, "marginBottom": 5 } }, "log-box": { "": { "flex": 1, "backgroundColor": "#333333", "marginTop": 10, "marginRight": 10, "marginBottom": 10, "marginLeft": 10, "paddingTop": 10, "paddingRight": 10, "paddingBottom": 10, "paddingLeft": 10, "borderRadius": 5 } }, "log-text": { "": { "color": "#00ff00", "fontSize": 12, "fontFamily": "monospace" } }, "btn-group": { "": { "paddingTop": 10, "paddingRight": 10, "paddingBottom": 10, "paddingLeft": 10, "backgroundColor": "#ffffff" } }, "btn": { "": { "marginBottom": 10, "backgroundColor": "#007aff", "borderRadius": 5, "height": 44, "justifyContent": "center", "alignItems": "center" } }, "secondary": { "": { "backgroundColor": "#999999" } } };
const _sfc_main = {
  data() {
    return {
      logs: "Ready...\n",
      ctx: null,
      devicePosition: "back",
      isAPIMissing: false,
      isCustomBase: false
    };
  },
  onLoad() {
    this.addLog("Page onLoad");
    this.checkRuntime();
  },
  onReady() {
    this.addLog("Page onReady");
    if (typeof uni.createCameraContext === "function") {
      this.ctx = uni.createCameraContext();
      this.addLog("Camera Context Created");
    } else {
      this.addLog("Error: uni.createCameraContext is not a function");
      this.isAPIMissing = true;
      uni.showModal({
        title: "环境异常",
        content: "检测到 uni.createCameraContext 方法缺失。\n\n这通常是因为“自定义基座”未包含 Camera 模块。\n\n请在 HBuilderX 菜单中选择：\n运行 -> 运行到手机 -> 制作自定义调试基座\n(确保 manifest 已勾选 Camera 模块)",
        showCancel: false
      });
    }
  },
  methods: {
    addLog(msg) {
      const time = (/* @__PURE__ */ new Date()).toTimeString().split(" ")[0];
      this.logs = `[${time}] ${msg}
` + this.logs;
      formatAppLog("log", "at pages/test/camera-min.nvue:91", msg);
    },
    onError(e) {
      this.addLog("Camera Error Event: " + JSON.stringify(e.detail));
    },
    onInitDone(e) {
      this.addLog("Camera InitDone Event: " + JSON.stringify(e.detail));
    },
    checkRuntime() {
      this.isCustomBase = plus.runtime.isCustomRuntime;
      const info = uni.getSystemInfoSync();
      this.addLog("SysInfo: " + info.platform + " / " + info.system);
      this.addLog("AppID: " + info.appId);
      this.addLog("Runtime CustomBase: " + this.isCustomBase);
      if (!this.isCustomBase) {
        this.addLog("WARNING: Running on Standard Base!");
        uni.showToast({
          title: "请切换到自定义基座",
          icon: "none",
          duration: 3e3
        });
      }
    },
    testSystemCamera() {
      this.addLog("尝试调用系统相机...");
      const cmr = plus.camera.getCamera();
      cmr.captureImage((p) => {
        this.addLog("系统相机拍照成功: " + p);
        uni.showToast({ title: "硬件正常", icon: "success" });
      }, (e) => {
        this.addLog("系统相机失败: " + e.message);
        uni.showModal({ title: "相机启动失败", content: "错误: " + e.message });
      }, {
        filename: "_doc/camera/",
        index: 1
      });
    },
    testPlusCamera() {
      try {
        const cmr = plus.camera.getCamera();
        this.addLog("Plus Camera Obj: " + (cmr ? "OK" : "NULL"));
        if (cmr) {
          const res = cmr.supportedImageResolutions;
          this.addLog("Supported Res: " + JSON.stringify(res));
        }
      } catch (e) {
        this.addLog("Plus Error: " + e.message);
      }
    },
    startPreviewManual() {
      if (this.ctx) {
        this.addLog("Calling startPreview...");
        this.ctx.startPreview({
          success: () => this.addLog("startPreview Success"),
          fail: (e) => this.addLog("startPreview Fail: " + e.errMsg)
        });
      } else {
        this.addLog("No Camera Context");
      }
    },
    toggleCamera() {
      this.devicePosition = this.devicePosition === "back" ? "front" : "back";
      this.addLog("Switched to: " + this.devicePosition);
    },
    goBack() {
      uni.navigateBack();
    }
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
    createElementVNode("view", { class: "page" }, [
      createElementVNode("view", { class: "header" }, [
        createElementVNode("u-text", { class: "title" }, "Camera Debug V3"),
        createElementVNode("u-text", { class: "subtitle" }, "红底=容器, 绿底=组件, 画面=正常")
      ]),
      createElementVNode("view", { class: "camera-box" }, [
        createElementVNode("view", { class: "camera-placeholder" }, [
          createElementVNode("u-text", { style: { "color": "#666", "font-size": "14px" } }, "摄像头区域")
        ]),
        createElementVNode("camera", {
          id: "myCamera",
          class: "camera-view",
          devicePosition: $data.devicePosition,
          flash: "off",
          onError: _cache[0] || (_cache[0] = (...args) => $options.onError && $options.onError(...args)),
          onInitdone: _cache[1] || (_cache[1] = (...args) => $options.onInitDone && $options.onInitDone(...args)),
          style: { "width": "750rpx", "height": "500rpx", "background-color": "transparent" }
        }, null, 40, ["devicePosition"]),
        $data.isAPIMissing ? (openBlock(), createElementBlock("view", {
          key: 0,
          class: "error-overlay",
          style: { "background-color": "rgba(0,0,0,0.5)", "pointer-events": "none" }
        }, [
          createElementVNode("u-text", {
            class: "error-text",
            style: { "font-size": "14px", "color": "#ff9900" }
          }, "⚠️ Camera API 未就绪"),
          createElementVNode("u-text", {
            class: "error-desc",
            style: { "font-size": "12px" }
          }, "请尝试卸载 App 后重装")
        ])) : createCommentVNode("", true)
      ]),
      createElementVNode("scroll-view", {
        class: "log-box",
        scrollY: "true"
      }, [
        createElementVNode("u-text", { class: "log-text" }, toDisplayString($data.logs), 1)
      ]),
      createElementVNode("view", { class: "btn-group" }, [
        createVNode(_component_button, {
          class: "btn",
          onClick: $options.testSystemCamera
        }, {
          default: withCtx(() => [
            createTextVNode("1. 调用系统相机 (验证硬件)")
          ]),
          _: 1
        }, 8, ["onClick"]),
        createVNode(_component_button, {
          class: "btn",
          onClick: $options.startPreviewManual
        }, {
          default: withCtx(() => [
            createTextVNode("2. 强制启动预览")
          ]),
          _: 1
        }, 8, ["onClick"]),
        createVNode(_component_button, {
          class: "btn",
          onClick: $options.toggleCamera
        }, {
          default: withCtx(() => [
            createTextVNode("3. 切换摄像头")
          ]),
          _: 1
        }, 8, ["onClick"]),
        createVNode(_component_button, {
          class: "btn secondary",
          onClick: $options.goBack
        }, {
          default: withCtx(() => [
            createTextVNode("返回")
          ]),
          _: 1
        }, 8, ["onClick"])
      ])
    ])
  ]);
}
const cameraMin = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render], ["styles", [_style_0]]]);
export {
  cameraMin as default
};
