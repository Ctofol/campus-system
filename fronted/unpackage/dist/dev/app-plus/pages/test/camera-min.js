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
  var _style_0 = { "page": { "": { "flex": 1, "backgroundColor": "#f5f7fa", "flexDirection": "column" } }, "status-bar": { "": { "backgroundColor": "#ffffff" } }, "header": { "": { "paddingTop": 20, "paddingRight": 20, "paddingBottom": 20, "paddingLeft": 20, "backgroundColor": "#ffffff", "borderBottomWidth": 1, "borderBottomColor": "#eeeeee", "marginBottom": 15 } }, "title": { "": { "fontSize": 20, "fontWeight": "bold", "color": "#333333" } }, "subtitle": { "": { "fontSize": 14, "color": "#999999", "marginTop": 5 } }, "action-card": { "": { "marginTop": 0, "marginRight": 15, "marginBottom": 15, "marginLeft": 15, "paddingTop": 20, "paddingRight": 20, "paddingBottom": 20, "paddingLeft": 20, "backgroundColor": "#ffffff", "borderRadius": 12 } }, "card-title": { "": { "fontSize": 16, "fontWeight": "bold", "color": "#333333", "marginBottom": 15, "borderLeftWidth": 4, "borderLeftColor": "#20C997", "paddingLeft": 10 } }, "btn-group": { "": { "flexDirection": "row", "justifyContent": "space-between" } }, "action-btn": { "": { "flex": 1, "height": 50, "backgroundColor": "#f0f0f0", "borderRadius": 8, "justifyContent": "center", "alignItems": "center", "marginTop": 0, "marginRight": 5, "marginBottom": 0, "marginLeft": 5, "borderWidth": 0 } }, "primary": { "": { "backgroundColor": "#20C997" } }, "btn-text": { "": { "fontSize": 14, "color": "#333333" } }, "result-card": { "": { "marginTop": 0, "marginRight": 15, "marginBottom": 15, "marginLeft": 15, "paddingTop": 20, "paddingRight": 20, "paddingBottom": 20, "paddingLeft": 20, "backgroundColor": "#ffffff", "borderRadius": 12 } }, "preview-img": { "": { "width": "650rpx", "height": "400rpx", "backgroundColor": "#000000", "borderRadius": 8, "marginBottom": 10 } }, "preview-video": { "": { "width": "650rpx", "height": "400rpx", "backgroundColor": "#000000", "borderRadius": 8, "marginBottom": 10 } }, "path-text": { "": { "fontSize": 12, "color": "#999999", "wordWrap": "break-word" } }, "ai-card": { "": { "marginTop": 0, "marginRight": 15, "marginBottom": 15, "marginLeft": 15, "paddingTop": 20, "paddingRight": 20, "paddingBottom": 20, "paddingLeft": 20, "backgroundColor": "#e8f5e9", "borderRadius": 12, "borderWidth": 1, "borderColor": "#c8e6c9" } }, "ai-header": { "": { "flexDirection": "row", "justifyContent": "space-between", "alignItems": "center", "marginBottom": 15, "paddingBottom": 10, "borderBottomWidth": 1, "borderBottomColor": "#c8e6c9" } }, "ai-title": { "": { "fontSize": 16, "fontWeight": "bold", "color": "#2e7d32" } }, "ai-tag": { "": { "fontSize": 10, "color": "#ffffff", "backgroundColor": "#4caf50", "paddingTop": 2, "paddingRight": 6, "paddingBottom": 2, "paddingLeft": 6, "borderRadius": 4 } }, "ai-row": { "": { "flexDirection": "row", "justifyContent": "space-between", "marginBottom": 8 } }, "ai-label": { "": { "fontSize": 14, "color": "#555555" } }, "ai-value": { "": { "fontSize": 14, "color": "#333333", "fontWeight": "bold" } }, "score": { "": { "color": "#ff9800", "fontSize": 18 } }, "footer": { "": { "marginTop": 20, "marginRight": 15, "marginBottom": 20, "marginLeft": 15 } }, "back-btn": { "": { "backgroundColor": "#ffffff", "borderWidth": 1, "borderColor": "#dddddd", "color": "#666666" } } };
  var _sfc_main = {
    data() {
      return {
        statusBarHeight: 20,
        result: {
          type: "",
          // 'image' | 'video'
          path: ""
        },
        aiReport: null
      };
    },
    onLoad() {
      const sys = uni.getSystemInfoSync();
      this.statusBarHeight = sys.statusBarHeight || 20;
    },
    methods: {
      // 拍照功能
      takePhoto() {
        const cmr = plus.camera.getCamera();
        cmr.captureImage((p) => {
          plus.io.resolveLocalFileSystemURL(p, (entry) => {
            this.result = {
              type: "image",
              path: entry.toLocalURL()
            };
            this.aiReport = null;
            uni.showToast({ title: "\u62CD\u7167\u6210\u529F", icon: "success" });
          });
        }, (e) => {
          formatAppLog("error", "at pages/test/camera-min.nvue:105", "\u62CD\u7167\u5931\u8D25: " + e.message);
        }, {
          filename: "_doc/camera/",
          index: 1
        });
      },
      // 录像功能
      recordVideo() {
        const cmr = plus.camera.getCamera();
        cmr.startVideoCapture((p) => {
          plus.io.resolveLocalFileSystemURL(p, (entry) => {
            this.result = {
              type: "video",
              path: entry.toLocalURL()
            };
            this.simulateAIAnalysis();
          });
        }, (e) => {
          formatAppLog("error", "at pages/test/camera-min.nvue:131", "\u5F55\u50CF\u5931\u8D25: " + e.message);
        }, {
          filename: "_doc/camera/",
          index: 1,
          videoMaximumDuration: 10
          // 限制10秒
        });
      },
      // 模拟 AI 分析
      simulateAIAnalysis() {
        uni.showLoading({ title: "AI \u6B63\u5728\u5206\u6790..." });
        setTimeout(() => {
          uni.hideLoading();
          this.aiReport = {
            duration: (Math.random() * 5 + 5).toFixed(1),
            score: Math.floor(Math.random() * 10 + 85),
            comment: "\u52A8\u4F5C\u6807\u51C6\uFF0C\u8282\u594F\u63A7\u5236\u826F\u597D\uFF0C\u672A\u53D1\u73B0\u660E\u663E\u8FDD\u89C4\u3002"
          };
          uni.showToast({ title: "\u5206\u6790\u5B8C\u6210", icon: "success" });
        }, 2e3);
      },
      goBack() {
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
      (0, import_vue2.createElementVNode)("view", { class: "page" }, [
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
          (0, import_vue2.createElementVNode)("u-text", { class: "title" }, "\u6444\u50CF\u5934\u529F\u80FD\u6D4B\u8BD5"),
          (0, import_vue2.createElementVNode)("u-text", { class: "subtitle" }, "\u57FA\u4E8E\u7CFB\u7EDF\u539F\u751F\u63A5\u53E3 (Plus API)")
        ]),
        (0, import_vue2.createElementVNode)("view", { class: "action-card" }, [
          (0, import_vue2.createElementVNode)("u-text", { class: "card-title" }, "\u529F\u80FD\u9009\u62E9"),
          (0, import_vue2.createElementVNode)("view", { class: "btn-group" }, [
            (0, import_vue2.createVNode)(_component_button, {
              class: "action-btn",
              onClick: $options.takePhoto
            }, {
              default: (0, import_vue2.withCtx)(() => [
                (0, import_vue2.createElementVNode)("u-text", { class: "btn-text" }, "\u{1F4F7} \u62CD\u7167\u6D4B\u8BD5")
              ]),
              _: 1
              /* STABLE */
            }, 8, ["onClick"]),
            (0, import_vue2.createVNode)(_component_button, {
              class: "action-btn primary",
              onClick: $options.recordVideo
            }, {
              default: (0, import_vue2.withCtx)(() => [
                (0, import_vue2.createElementVNode)("u-text", {
                  class: "btn-text",
                  style: { "color": "#fff" }
                }, "\u{1F4F9} \u5F55\u50CF\u6D4B\u8BD5 (\u6A21\u62DFAI\u5206\u6790)")
              ]),
              _: 1
              /* STABLE */
            }, 8, ["onClick"])
          ])
        ]),
        $data.result.path ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
          key: 0,
          class: "result-card"
        }, [
          (0, import_vue2.createElementVNode)("u-text", { class: "card-title" }, "\u6267\u884C\u7ED3\u679C"),
          $data.result.type === "image" ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("u-image", {
            key: 0,
            src: $data.result.path,
            mode: "aspectFit",
            class: "preview-img"
          }, null, 8, ["src"])) : (0, import_vue2.createCommentVNode)("v-if", true),
          $data.result.type === "video" ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("u-video", {
            key: 1,
            src: $data.result.path,
            controls: "",
            class: "preview-video"
          }, null, 8, ["src"])) : (0, import_vue2.createCommentVNode)("v-if", true),
          (0, import_vue2.createElementVNode)(
            "u-text",
            { class: "path-text" },
            "\u6587\u4EF6\u8DEF\u5F84: " + (0, import_vue2.toDisplayString)($data.result.path),
            1
            /* TEXT */
          )
        ])) : (0, import_vue2.createCommentVNode)("v-if", true),
        $data.aiReport ? ((0, import_vue2.openBlock)(), (0, import_vue2.createElementBlock)("view", {
          key: 1,
          class: "ai-card"
        }, [
          (0, import_vue2.createElementVNode)("view", { class: "ai-header" }, [
            (0, import_vue2.createElementVNode)("u-text", { class: "ai-title" }, "\u{1F916} AI \u667A\u80FD\u5206\u6790\u62A5\u544A"),
            (0, import_vue2.createElementVNode)("u-text", { class: "ai-tag" }, "\u6A21\u62DF\u6570\u636E")
          ]),
          (0, import_vue2.createElementVNode)("view", { class: "ai-content" }, [
            (0, import_vue2.createElementVNode)("view", { class: "ai-row" }, [
              (0, import_vue2.createElementVNode)("u-text", { class: "ai-label" }, "\u89C6\u9891\u65F6\u957F"),
              (0, import_vue2.createElementVNode)(
                "u-text",
                { class: "ai-value" },
                (0, import_vue2.toDisplayString)($data.aiReport.duration) + " \u79D2",
                1
                /* TEXT */
              )
            ]),
            (0, import_vue2.createElementVNode)("view", { class: "ai-row" }, [
              (0, import_vue2.createElementVNode)("u-text", { class: "ai-label" }, "\u52A8\u4F5C\u8BC4\u5206"),
              (0, import_vue2.createElementVNode)(
                "u-text",
                { class: "ai-value score" },
                (0, import_vue2.toDisplayString)($data.aiReport.score),
                1
                /* TEXT */
              )
            ]),
            (0, import_vue2.createElementVNode)("view", { class: "ai-row" }, [
              (0, import_vue2.createElementVNode)("u-text", { class: "ai-label" }, "\u7EFC\u5408\u8BC4\u4EF7"),
              (0, import_vue2.createElementVNode)(
                "u-text",
                { class: "ai-value" },
                (0, import_vue2.toDisplayString)($data.aiReport.comment),
                1
                /* TEXT */
              )
            ])
          ])
        ])) : (0, import_vue2.createCommentVNode)("v-if", true),
        (0, import_vue2.createElementVNode)("view", { class: "footer" }, [
          (0, import_vue2.createVNode)(_component_button, {
            class: "back-btn",
            onClick: $options.goBack
          }, {
            default: (0, import_vue2.withCtx)(() => [
              (0, import_vue2.createTextVNode)("\u8FD4\u56DE\u9996\u9875")
            ]),
            _: 1
            /* STABLE */
          }, 8, ["onClick"])
        ])
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
