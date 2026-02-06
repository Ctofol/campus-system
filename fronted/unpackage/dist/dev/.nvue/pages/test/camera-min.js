import { _ as _export_sfc, f as formatAppLog } from "../../_plugin-vue_export-helper.js";
import { resolveComponent, openBlock, createElementBlock, createElementVNode, normalizeStyle, createVNode, withCtx, createCommentVNode, toDisplayString, createTextVNode } from "vue";
const _style_0 = { "page": { "": { "flex": 1, "backgroundColor": "#f5f7fa", "flexDirection": "column" } }, "status-bar": { "": { "backgroundColor": "#ffffff" } }, "header": { "": { "paddingTop": 20, "paddingRight": 20, "paddingBottom": 20, "paddingLeft": 20, "backgroundColor": "#ffffff", "borderBottomWidth": 1, "borderBottomColor": "#eeeeee", "marginBottom": 15 } }, "title": { "": { "fontSize": 20, "fontWeight": "bold", "color": "#333333" } }, "subtitle": { "": { "fontSize": 14, "color": "#999999", "marginTop": 5 } }, "action-card": { "": { "marginTop": 0, "marginRight": 15, "marginBottom": 15, "marginLeft": 15, "paddingTop": 20, "paddingRight": 20, "paddingBottom": 20, "paddingLeft": 20, "backgroundColor": "#ffffff", "borderRadius": 12 } }, "card-title": { "": { "fontSize": 16, "fontWeight": "bold", "color": "#333333", "marginBottom": 15, "borderLeftWidth": 4, "borderLeftColor": "#20C997", "paddingLeft": 10 } }, "btn-group": { "": { "flexDirection": "row", "justifyContent": "space-between" } }, "action-btn": { "": { "flex": 1, "height": 50, "backgroundColor": "#f0f0f0", "borderRadius": 8, "justifyContent": "center", "alignItems": "center", "marginTop": 0, "marginRight": 5, "marginBottom": 0, "marginLeft": 5, "borderWidth": 0 } }, "primary": { "": { "backgroundColor": "#20C997" } }, "btn-text": { "": { "fontSize": 14, "color": "#333333" } }, "result-card": { "": { "marginTop": 0, "marginRight": 15, "marginBottom": 15, "marginLeft": 15, "paddingTop": 20, "paddingRight": 20, "paddingBottom": 20, "paddingLeft": 20, "backgroundColor": "#ffffff", "borderRadius": 12 } }, "preview-img": { "": { "width": "650rpx", "height": "400rpx", "backgroundColor": "#000000", "borderRadius": 8, "marginBottom": 10 } }, "preview-video": { "": { "width": "650rpx", "height": "400rpx", "backgroundColor": "#000000", "borderRadius": 8, "marginBottom": 10 } }, "path-text": { "": { "fontSize": 12, "color": "#999999", "wordWrap": "break-word" } }, "ai-card": { "": { "marginTop": 0, "marginRight": 15, "marginBottom": 15, "marginLeft": 15, "paddingTop": 20, "paddingRight": 20, "paddingBottom": 20, "paddingLeft": 20, "backgroundColor": "#e8f5e9", "borderRadius": 12, "borderWidth": 1, "borderColor": "#c8e6c9" } }, "ai-header": { "": { "flexDirection": "row", "justifyContent": "space-between", "alignItems": "center", "marginBottom": 15, "paddingBottom": 10, "borderBottomWidth": 1, "borderBottomColor": "#c8e6c9" } }, "ai-title": { "": { "fontSize": 16, "fontWeight": "bold", "color": "#2e7d32" } }, "ai-tag": { "": { "fontSize": 10, "color": "#ffffff", "backgroundColor": "#4caf50", "paddingTop": 2, "paddingRight": 6, "paddingBottom": 2, "paddingLeft": 6, "borderRadius": 4 } }, "ai-row": { "": { "flexDirection": "row", "justifyContent": "space-between", "marginBottom": 8 } }, "ai-label": { "": { "fontSize": 14, "color": "#555555" } }, "ai-value": { "": { "fontSize": 14, "color": "#333333", "fontWeight": "bold" } }, "score": { "": { "color": "#ff9800", "fontSize": 18 } }, "footer": { "": { "marginTop": 20, "marginRight": 15, "marginBottom": 20, "marginLeft": 15 } }, "back-btn": { "": { "backgroundColor": "#ffffff", "borderWidth": 1, "borderColor": "#dddddd", "color": "#666666" } } };
const _sfc_main = {
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
          uni.showToast({ title: "拍照成功", icon: "success" });
        });
      }, (e) => {
        formatAppLog("error", "at pages/test/camera-min.nvue:105", "拍照失败: " + e.message);
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
        formatAppLog("error", "at pages/test/camera-min.nvue:131", "录像失败: " + e.message);
      }, {
        filename: "_doc/camera/",
        index: 1,
        videoMaximumDuration: 10
        // 限制10秒
      });
    },
    // 模拟 AI 分析
    simulateAIAnalysis() {
      uni.showLoading({ title: "AI 正在分析..." });
      setTimeout(() => {
        uni.hideLoading();
        this.aiReport = {
          duration: (Math.random() * 5 + 5).toFixed(1),
          score: Math.floor(Math.random() * 10 + 85),
          comment: "动作标准，节奏控制良好，未发现明显违规。"
        };
        uni.showToast({ title: "分析完成", icon: "success" });
      }, 2e3);
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
      createElementVNode(
        "view",
        {
          class: "status-bar",
          style: normalizeStyle({ height: $data.statusBarHeight + "px" })
        },
        null,
        4
        /* STYLE */
      ),
      createElementVNode("view", { class: "header" }, [
        createElementVNode("u-text", { class: "title" }, "摄像头功能测试"),
        createElementVNode("u-text", { class: "subtitle" }, "基于系统原生接口 (Plus API)")
      ]),
      createElementVNode("view", { class: "action-card" }, [
        createElementVNode("u-text", { class: "card-title" }, "功能选择"),
        createElementVNode("view", { class: "btn-group" }, [
          createVNode(_component_button, {
            class: "action-btn",
            onClick: $options.takePhoto
          }, {
            default: withCtx(() => [
              createElementVNode("u-text", { class: "btn-text" }, "📷 拍照测试")
            ]),
            _: 1
            /* STABLE */
          }, 8, ["onClick"]),
          createVNode(_component_button, {
            class: "action-btn primary",
            onClick: $options.recordVideo
          }, {
            default: withCtx(() => [
              createElementVNode("u-text", {
                class: "btn-text",
                style: { "color": "#fff" }
              }, "📹 录像测试 (模拟AI分析)")
            ]),
            _: 1
            /* STABLE */
          }, 8, ["onClick"])
        ])
      ]),
      $data.result.path ? (openBlock(), createElementBlock("view", {
        key: 0,
        class: "result-card"
      }, [
        createElementVNode("u-text", { class: "card-title" }, "执行结果"),
        $data.result.type === "image" ? (openBlock(), createElementBlock("u-image", {
          key: 0,
          src: $data.result.path,
          mode: "aspectFit",
          class: "preview-img"
        }, null, 8, ["src"])) : createCommentVNode("v-if", true),
        $data.result.type === "video" ? (openBlock(), createElementBlock("u-video", {
          key: 1,
          src: $data.result.path,
          controls: "",
          class: "preview-video"
        }, null, 8, ["src"])) : createCommentVNode("v-if", true),
        createElementVNode(
          "u-text",
          { class: "path-text" },
          "文件路径: " + toDisplayString($data.result.path),
          1
          /* TEXT */
        )
      ])) : createCommentVNode("v-if", true),
      $data.aiReport ? (openBlock(), createElementBlock("view", {
        key: 1,
        class: "ai-card"
      }, [
        createElementVNode("view", { class: "ai-header" }, [
          createElementVNode("u-text", { class: "ai-title" }, "🤖 AI 智能分析报告"),
          createElementVNode("u-text", { class: "ai-tag" }, "模拟数据")
        ]),
        createElementVNode("view", { class: "ai-content" }, [
          createElementVNode("view", { class: "ai-row" }, [
            createElementVNode("u-text", { class: "ai-label" }, "视频时长"),
            createElementVNode(
              "u-text",
              { class: "ai-value" },
              toDisplayString($data.aiReport.duration) + " 秒",
              1
              /* TEXT */
            )
          ]),
          createElementVNode("view", { class: "ai-row" }, [
            createElementVNode("u-text", { class: "ai-label" }, "动作评分"),
            createElementVNode(
              "u-text",
              { class: "ai-value score" },
              toDisplayString($data.aiReport.score),
              1
              /* TEXT */
            )
          ]),
          createElementVNode("view", { class: "ai-row" }, [
            createElementVNode("u-text", { class: "ai-label" }, "综合评价"),
            createElementVNode(
              "u-text",
              { class: "ai-value" },
              toDisplayString($data.aiReport.comment),
              1
              /* TEXT */
            )
          ])
        ])
      ])) : createCommentVNode("v-if", true),
      createElementVNode("view", { class: "footer" }, [
        createVNode(_component_button, {
          class: "back-btn",
          onClick: $options.goBack
        }, {
          default: withCtx(() => [
            createTextVNode("返回首页")
          ]),
          _: 1
          /* STABLE */
        }, 8, ["onClick"])
      ])
    ])
  ]);
}
const cameraMin = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render], ["styles", [_style_0]], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/test/camera-min.nvue"]]);
export {
  cameraMin as default
};
