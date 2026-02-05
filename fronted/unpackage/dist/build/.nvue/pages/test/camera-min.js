import { _ as _export_sfc, f as formatAppLog } from "../../_plugin-vue_export-helper.js";
import { resolveComponent, openBlock, createElementBlock, createElementVNode, normalizeStyle, toDisplayString, createVNode, withCtx, createTextVNode } from "vue";
const _style_0 = { "camera-min-page": { "": { "flex": 1, "backgroundColor": "#f5f5f5", "flexDirection": "column" } }, "status-bar": { "": { "backgroundColor": "#ffffff" } }, "header": { "": { "paddingTop": 20, "paddingRight": 20, "paddingBottom": 20, "paddingLeft": 20, "backgroundColor": "#ffffff", "borderBottomWidth": 1, "borderBottomColor": "#eeeeee" } }, "title": { "": { "fontSize": 18, "fontWeight": "bold", "color": "#333333" } }, "subtitle": { "": { "fontSize": 12, "color": "#999999", "marginTop": 5 } }, "camera-container": { "": { "width": "750rpx", "height": "500rpx", "backgroundColor": "#000000", "marginTop": 20, "position": "relative" } }, "live-camera": { "": { "width": "750rpx", "height": "500rpx" } }, "camera-overlay": { "": { "position": "absolute", "bottom": "20rpx", "left": "20rpx", "backgroundColor": "rgba(0,0,0,0.5)", "paddingTop": 5, "paddingRight": 10, "paddingBottom": 5, "paddingLeft": 10, "borderRadius": 4 } }, "overlay-text": { "": { "color": "#ffffff", "fontSize": 12 } }, "debug-info": { "": { "paddingTop": 20, "paddingRight": 20, "paddingBottom": 20, "paddingLeft": 20, "marginTop": 10, "backgroundColor": "#ffffff" } }, "info-item": { "": { "fontSize": 14, "color": "#666666", "marginBottom": 5 } }, "action-btn": { "": { "marginTop": 10, "marginRight": 20, "marginBottom": 10, "marginLeft": 20, "backgroundColor": "#20C997", "borderRadius": 8, "height": 44, "justifyContent": "center", "alignItems": "center" } }, "secondary": { "": { "backgroundColor": "#dddddd" } } };
const _sfc_main = {
  data() {
    return {
      statusBarHeight: 20,
      statusMsg: "初始化...",
      authStatus: "未知"
    };
  },
  onLoad() {
    const sys = uni.getSystemInfoSync();
    this.statusBarHeight = sys.statusBarHeight || 20;
    this.statusMsg = "页面已加载";
    this.checkAuth();
  },
  methods: {
    handleCameraError(e) {
      formatAppLog("error", "at pages/test/camera-min.nvue:62", "Camera Error:", e);
      this.statusMsg = "摄像头错误: " + (e.detail.errMsg || "未知");
      uni.showToast({
        title: "摄像头启动失败",
        icon: "none"
      });
    },
    checkAuth() {
      const permission = uni.getAppAuthorizeSetting();
      this.authStatus = permission.cameraAuthorized || "未检测到";
      if (permission.cameraAuthorized === "denied") {
        this.statusMsg = "权限被拒绝";
        uni.showModal({
          title: "权限提示",
          content: "摄像头权限已被拒绝，请前往系统设置开启",
          confirmText: "去设置",
          success: (res) => {
            if (res.confirm)
              uni.openAppAuthorizeSetting();
          }
        });
      } else {
        this.statusMsg = "权限正常";
      }
    },
    back() {
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
    createElementVNode("view", { class: "camera-min-page" }, [
      createElementVNode("view", {
        class: "status-bar",
        style: normalizeStyle({ height: $data.statusBarHeight + "px" })
      }, null, 4),
      createElementVNode("view", { class: "header" }, [
        createElementVNode("u-text", { class: "title" }, "摄像头最小可用测试"),
        createElementVNode("u-text", { class: "subtitle" }, "仅用于检测 App 端摄像头画面是否正常")
      ]),
      createElementVNode("view", { class: "camera-container" }, [
        createElementVNode("camera", {
          class: "live-camera",
          devicePosition: "back",
          flash: "off",
          onError: _cache[0] || (_cache[0] = (...args) => $options.handleCameraError && $options.handleCameraError(...args))
        }, [
          createElementVNode("cover-view", { class: "camera-overlay" }, [
            createElementVNode("u-text", { class: "overlay-text" }, "原生组件运行中")
          ])
        ], 32)
      ]),
      createElementVNode("view", { class: "debug-info" }, [
        createElementVNode("u-text", { class: "info-item" }, "状态：" + toDisplayString($data.statusMsg), 1),
        createElementVNode("u-text", { class: "info-item" }, "权限：" + toDisplayString($data.authStatus), 1)
      ]),
      createVNode(_component_button, {
        class: "action-btn",
        onClick: $options.checkAuth
      }, {
        default: withCtx(() => [
          createTextVNode("检查权限")
        ]),
        _: 1
      }, 8, ["onClick"]),
      createVNode(_component_button, {
        class: "action-btn secondary",
        onClick: $options.back
      }, {
        default: withCtx(() => [
          createTextVNode("返回")
        ]),
        _: 1
      }, 8, ["onClick"])
    ])
  ]);
}
const cameraMin = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render], ["styles", [_style_0]]]);
export {
  cameraMin as default
};
