"use strict";
const common_vendor = require("../../common/vendor.js");
const _sfc_main = {
  __name: "ai-chat-robot",
  props: {
    visible: Boolean,
    runData: {
      type: Object,
      default: () => ({ distance: 0, pace: 0, heartRate: 0 })
    }
  },
  emits: ["update:visible", "share"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const messages = common_vendor.ref([
      { type: "robot", text: "你好！我是你的专属运动小助手。我正在实时分析你的跑步数据，有什么可以帮你的吗？" }
    ]);
    const inputText = common_vendor.ref("");
    const scrollTop = common_vendor.ref(0);
    const close = () => {
      emit("update:visible", false);
    };
    const scrollToBottom = () => {
      common_vendor.nextTick$1(() => {
        scrollTop.value = 99999;
      });
    };
    const sendText = () => {
      if (!inputText.value.trim())
        return;
      ask(inputText.value);
      inputText.value = "";
    };
    const ask = (text) => {
      messages.value.push({ type: "user", text });
      scrollToBottom();
      setTimeout(() => {
        analyzeAndReply(text);
      }, 800);
    };
    const analyzeAndReply = (question) => {
      let reply = { type: "robot", text: "", card: null };
      const { distance, pace, heartRate } = props.runData;
      if (question.includes("配速")) {
        reply.text = `当前配速 ${pace.toFixed(2)} 分钟/公里。`;
        let suggestion = "";
        let color = "#20C997";
        if (pace < 4) {
          suggestion = "速度很快，请注意保持心率稳定！";
          color = "#FF6B6B";
        } else if (pace > 8) {
          suggestion = "速度稍慢，建议加快摆臂频率来提升速度。";
          color = "#FF9F43";
        } else {
          suggestion = "配速保持得很好，继续加油！";
        }
        reply.card = {
          title: "🏃 配速分析",
          chartData: [
            { label: "当前", value: Math.min(100, 10 / pace * 50), valText: `${pace.toFixed(1)}`, color },
            { label: "目标", value: 70, valText: "6.0", color: "#3A7BD5" }
            // Assume target 6.0
          ],
          suggestion,
          shareable: true
        };
      } else if (question.includes("运动量") || question.includes("够吗")) {
        const km = (distance / 1e3).toFixed(2);
        reply.text = `你今天已经跑了 ${km} 公里。`;
        let suggestion = "";
        if (km < 2) {
          suggestion = "建议今天至少完成 3 公里，加油！";
        } else if (km > 10) {
          suggestion = "运动量非常充足，注意跑后拉伸。";
        } else {
          suggestion = "运动量适中，保持这个节奏。";
        }
        reply.card = {
          title: "📊 运动量评估",
          chartData: [
            { label: "今日", value: Math.min(100, km / 5 * 100), valText: `${km}km`, color: "#20C997" },
            { label: "目标", value: 100, valText: "5.0km", color: "#eee" }
          ],
          suggestion,
          shareable: true
        };
      } else if (question.includes("建议") || question.includes("分析")) {
        reply.text = "基于你的实时数据，我生成了一份简报：";
        reply.card = {
          title: "💡 综合改进建议",
          suggestion: heartRate > 160 ? "心率偏高，建议适当放慢速度，调整呼吸。" : "心率控制良好，可以尝试进行间歇跑训练提升耐力。",
          chartData: [
            { label: "心率", value: Math.min(100, heartRate / 200 * 100), valText: `${heartRate}bpm`, color: heartRate > 160 ? "#FF4757" : "#20C997" },
            { label: "配速", value: Math.min(100, 10 / pace * 50), valText: `${pace.toFixed(1)}`, color: "#3A7BD5" }
          ],
          shareable: true
        };
      } else {
        reply.text = "抱歉，我还在学习中，暂时只能回答关于配速、运动量和改进建议的问题。";
      }
      messages.value.push(reply);
      scrollToBottom();
    };
    const shareToTeacher = (card) => {
      common_vendor.index.showToast({ title: "已发送给教官", icon: "success" });
      emit("share", card);
    };
    common_vendor.watch(() => props.visible, (val) => {
      if (val && messages.value.length === 0) {
        messages.value.push({ type: "robot", text: "你好！我是你的专属运动小助手。" });
      }
    });
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: __props.visible
      }, __props.visible ? {
        b: common_vendor.o(close),
        c: common_vendor.o(close),
        d: common_vendor.f(messages.value, (msg, index, i0) => {
          return common_vendor.e({
            a: msg.type === "robot"
          }, msg.type === "robot" ? {} : {}, {
            b: common_vendor.t(msg.text),
            c: msg.card
          }, msg.card ? common_vendor.e({
            d: common_vendor.t(msg.card.title),
            e: msg.card.chartData
          }, msg.card.chartData ? {
            f: common_vendor.f(msg.card.chartData, (item, idx, i1) => {
              return {
                a: common_vendor.t(item.label),
                b: item.value + "%",
                c: item.color,
                d: common_vendor.t(item.valText),
                e: idx
              };
            })
          } : {}, {
            g: msg.card.suggestion
          }, msg.card.suggestion ? {
            h: common_vendor.t(msg.card.suggestion)
          } : {}, {
            i: msg.card.shareable
          }, msg.card.shareable ? {
            j: common_vendor.o(($event) => shareToTeacher(msg.card), index)
          } : {}) : {}, {
            k: msg.type === "user"
          }, msg.type === "user" ? {} : {}, {
            l: index,
            m: common_vendor.n(msg.type)
          });
        }),
        e: scrollTop.value,
        f: common_vendor.o(($event) => ask("我的配速怎么样？")),
        g: common_vendor.o(($event) => ask("今天运动量够吗？")),
        h: common_vendor.o(($event) => ask("给点建议")),
        i: common_vendor.o(sendText),
        j: inputText.value,
        k: common_vendor.o(($event) => inputText.value = $event.detail.value),
        l: common_vendor.o(sendText)
      } : {});
    };
  }
};
const Component = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-b77ff380"]]);
wx.createComponent(Component);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/components/ai-chat-robot/ai-chat-robot.js.map
