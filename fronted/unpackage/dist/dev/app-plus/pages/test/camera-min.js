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
  var __getProtoOf = Object.getPrototypeOf;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
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

  // vue-ns:vue
  var require_vue = __commonJS({
    "vue-ns:vue"(exports, module) {
      module.exports = Vue;
    }
  });

  // D:/PC/Document/HBuilderProjects/campus-system/fronted/unpackage/dist/dev/.nvue/_plugin-vue_export-helper.js
  var import_vue = __toESM(require_vue());
  var ON_SHOW = "onShow";
  var ON_HIDE = "onHide";
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
  var _export_sfc = (sfc, props) => {
    const target = sfc.__vccOpts || sfc;
    for (const [key, val] of props) {
      target[key] = val;
    }
    return target;
  };

  // D:/PC/Document/HBuilderProjects/campus-system/fronted/unpackage/dist/dev/.nvue/pages/test/camera-min.js
  var import_vue2 = __toESM(require_vue());
  var _style_0 = { "camera-min-page": { "": { "flex": 1, "backgroundColor": "#f5f5f5", "flexDirection": "column" } }, "status-bar": { "": { "backgroundColor": "#ffffff" } }, "header": { "": { "paddingTop": 20, "paddingRight": 20, "paddingBottom": 20, "paddingLeft": 20, "backgroundColor": "#ffffff", "borderBottomWidth": 1, "borderBottomColor": "#eeeeee" } }, "title": { "": { "fontSize": 18, "fontWeight": "bold", "color": "#333333" } }, "subtitle": { "": { "fontSize": 12, "color": "#999999", "marginTop": 5 } }, "camera-container": { "": { "width": "750rpx", "height": "500rpx", "backgroundColor": "#000000", "marginTop": 20, "position": "relative" } }, "live-camera": { "": { "width": "750rpx", "height": "500rpx" } }, "camera-overlay": { "": { "position": "absolute", "bottom": "20rpx", "left": "20rpx", "backgroundColor": "rgba(0,0,0,0.5)", "paddingTop": 5, "paddingRight": 10, "paddingBottom": 5, "paddingLeft": 10, "borderRadius": 4 } }, "overlay-text": { "": { "color": "#ffffff", "fontSize": 12 } }, "debug-info": { "": { "paddingTop": 20, "paddingRight": 20, "paddingBottom": 20, "paddingLeft": 20, "marginTop": 10, "backgroundColor": "#ffffff" } }, "info-item": { "": { "fontSize": 14, "color": "#666666", "marginBottom": 5 } }, "action-btn": { "": { "marginTop": 10, "marginRight": 20, "marginBottom": 10, "marginLeft": 20, "backgroundColor": "#20C997", "borderRadius": 8, "height": 44, "justifyContent": "center", "alignItems": "center" } }, "secondary": { "": { "backgroundColor": "#dddddd" } } };
  var _sfc_main = {
    data() {
      return {
        statusBarHeight: 20,
        statusMsg: "\u521D\u59CB\u5316...",
        authStatus: "\u672A\u77E5"
      };
    },
    onLoad() {
      const sys = uni.getSystemInfoSync();
      this.statusBarHeight = sys.statusBarHeight || 20;
      this.statusMsg = "\u9875\u9762\u5DF2\u52A0\u8F7D";
      this.checkAuth();
    },
    methods: {
      handleCameraError(e) {
        formatAppLog("error", "at pages/test/camera-min.nvue:62", "Camera Error:", e);
        this.statusMsg = "\u6444\u50CF\u5934\u9519\u8BEF: " + (e.detail.errMsg || "\u672A\u77E5");
        uni.showToast({
          title: "\u6444\u50CF\u5934\u542F\u52A8\u5931\u8D25",
          icon: "none"
        });
      },
      checkAuth() {
        const permission = uni.getAppAuthorizeSetting();
        this.authStatus = permission.cameraAuthorized || "\u672A\u68C0\u6D4B\u5230";
        if (permission.cameraAuthorized === "denied") {
          this.statusMsg = "\u6743\u9650\u88AB\u62D2\u7EDD";
          uni.showModal({
            title: "\u6743\u9650\u63D0\u793A",
            content: "\u6444\u50CF\u5934\u6743\u9650\u5DF2\u88AB\u62D2\u7EDD\uFF0C\u8BF7\u524D\u5F80\u7CFB\u7EDF\u8BBE\u7F6E\u5F00\u542F",
            confirmText: "\u53BB\u8BBE\u7F6E",
            success: (res) => {
              if (res.confirm)
                uni.openAppAuthorizeSetting();
            }
          });
        } else {
          this.statusMsg = "\u6743\u9650\u6B63\u5E38";
        }
      },
      back() {
        uni.navigateBack();
      }
    }
  };
  function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_button = (0, import_vue2.resolveComponent)("button");
    return (0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("scroll-view", {
      scrollY: true,
      showScrollbar: true,
      enableBackToTop: true,
      bubble: "true",
      style: { flexDirection: "column" }
    }, [
      (0, import_vue2.createElementVNode)("view", { class: "camera-min-page" }, [
        (0, import_vue2.createElementVNode)(
          "view",
          {
            class: "status-bar",
            style: (0, import_vue2.normalizeStyle)({ height: $data.statusBarHeight + "px" })
          },
          null,
          4
          /* STYLE */
        ),
        (0, import_vue2.createElementVNode)("view", { class: "header" }, [
          (0, import_vue2.createElementVNode)("u-text", { class: "title" }, "\u6444\u50CF\u5934\u6700\u5C0F\u53EF\u7528\u6D4B\u8BD5"),
          (0, import_vue2.createElementVNode)("u-text", { class: "subtitle" }, "\u4EC5\u7528\u4E8E\u68C0\u6D4B App \u7AEF\u6444\u50CF\u5934\u753B\u9762\u662F\u5426\u6B63\u5E38")
        ]),
        (0, import_vue2.createElementVNode)("view", { class: "camera-container" }, [
          (0, import_vue2.createElementVNode)(
            "camera",
            {
              class: "live-camera",
              devicePosition: "back",
              flash: "off",
              onError: _cache[0] || (_cache[0] = (...args) => $options.handleCameraError && $options.handleCameraError(...args))
            },
            [
              (0, import_vue2.createElementVNode)("cover-view", { class: "camera-overlay" }, [
                (0, import_vue2.createElementVNode)("u-text", { class: "overlay-text" }, "\u539F\u751F\u7EC4\u4EF6\u8FD0\u884C\u4E2D")
              ])
            ],
            32
            /* NEED_HYDRATION */
          )
        ]),
        (0, import_vue2.createElementVNode)("view", { class: "debug-info" }, [
          (0, import_vue2.createElementVNode)(
            "u-text",
            { class: "info-item" },
            "\u72B6\u6001\uFF1A" + (0, import_vue2.toDisplayString)($data.statusMsg),
            1
            /* TEXT */
          ),
          (0, import_vue2.createElementVNode)(
            "u-text",
            { class: "info-item" },
            "\u6743\u9650\uFF1A" + (0, import_vue2.toDisplayString)($data.authStatus),
            1
            /* TEXT */
          )
        ]),
        (0, import_vue2.createVNode)(_component_button, {
          class: "action-btn",
          onClick: $options.checkAuth
        }, {
          default: (0, import_vue2.withCtx)(() => [
            (0, import_vue2.createTextVNode)("\u68C0\u67E5\u6743\u9650")
          ]),
          _: 1
          /* STABLE */
        }, 8, ["onClick"]),
        (0, import_vue2.createVNode)(_component_button, {
          class: "action-btn secondary",
          onClick: $options.back
        }, {
          default: (0, import_vue2.withCtx)(() => [
            (0, import_vue2.createTextVNode)("\u8FD4\u56DE")
          ]),
          _: 1
          /* STABLE */
        }, 8, ["onClick"])
      ])
    ]);
  }
  var cameraMin = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render], ["styles", [_style_0]], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/test/camera-min.nvue"]]);

  // <stdin>
  var webview = plus.webview.currentWebview();
  if (webview) {
    const __pageId = parseInt(webview.id);
    const __pagePath = "pages/test/camera-min";
    let __pageQuery = {};
    try {
      __pageQuery = JSON.parse(webview.__query__);
    } catch (e) {
    }
    cameraMin.mpType = "page";
    const app = Vue.createPageApp(cameraMin, { $store: getApp({ allowDefault: true }).$store, __pageId, __pagePath, __pageQuery });
    app.provide("__globalStyles", Vue.useCssStyles([...__uniConfig.styles, ...cameraMin.styles || []]));
    app.mount("#root");
  }
})();
