"use strict";
const common_vendor = require("../../common/vendor.js");
const _sfc_main = {
  __name: "result",
  setup(__props) {
    const currentMode = common_vendor.ref("normal");
    const duration = common_vendor.ref(0);
    const distance = common_vendor.ref(0);
    const isReach = common_vendor.ref(false);
    const isPoliceFinish = common_vendor.ref(false);
    const policePace = common_vendor.ref(0);
    const testProject = common_vendor.ref("");
    common_vendor.ref("");
    const testCount = common_vendor.ref(0);
    const testQualified = common_vendor.ref(false);
    const standardReq = common_vendor.ref(0);
    const userScorePercent = common_vendor.ref(0);
    const standardScorePercent = common_vendor.ref(0);
    const suggestionText = common_vendor.ref("");
    const modeTitle = common_vendor.computed(() => {
      switch (currentMode.value) {
        case "police":
          return "🎯 2000米专项体能结算";
        case "campus":
          return "🏫 校园打卡跑步结算";
        case "test":
          return "💪 体能测试结算";
        default:
          return "🏃 普通跑步结算";
      }
    });
    const modeBgColor = common_vendor.computed(() => {
      switch (currentMode.value) {
        case "police":
          return "#fdf2f0";
        case "campus":
          return "#e8f4f8";
        case "test":
          return "#f3f7ff";
        default:
          return "#f5f5f5";
      }
    });
    const isPaceQualified = common_vendor.computed(() => {
      return policePace.value <= 6.5;
    });
    common_vendor.onLoad((options) => {
      if (options.data) {
        try {
          const data = JSON.parse(decodeURIComponent(options.data));
          currentMode.value = data.type === "test" ? "test" : "normal";
          if (data.metrics) {
            duration.value = data.metrics.duration || 0;
            distance.value = (data.metrics.distance || 0) * 1e3;
            testCount.value = data.metrics.count || 0;
            testQualified.value = data.metrics.qualified;
            policePace.value = Number(data.metrics.pace) || 0;
          }
          if (currentMode.value === "test") {
            testProject.value = "体测项目";
            testQualified.value = data.metrics.qualified;
            if (testQualified.value) {
              suggestionText.value = "恭喜达标！";
            } else {
              suggestionText.value = "继续加油！";
            }
          }
        } catch (e) {
          common_vendor.index.__f__("error", "at pages/result/result.vue:191", "Failed to parse result data", e);
        }
      } else {
        currentMode.value = options.mode || "normal";
        duration.value = Number(options.duration) || 0;
        distance.value = Number(options.distance) || 0;
        isReach.value = options.isReach === "true";
        isPoliceFinish.value = options.isPoliceFinish === "true";
        policePace.value = Number(options.policePace) || 0;
      }
    });
    const formatDuration = (seconds) => {
      const min = Math.floor(seconds / 60);
      const sec = seconds % 60;
      return `${min.toString().padStart(2, "0")}:${sec.toString().padStart(2, "0")}`;
    };
    const backToHome = () => {
      common_vendor.index.reLaunch({ url: "/pages/home/home" });
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.t(modeTitle.value),
        b: modeBgColor.value,
        c: currentMode.value === "test"
      }, currentMode.value === "test" ? {
        d: common_vendor.t(testProject.value),
        e: common_vendor.t(testCount.value),
        f: common_vendor.t(formatDuration(duration.value)),
        g: common_vendor.t(testQualified.value ? "✅ 合格" : "❌ 未合格"),
        h: common_vendor.n(testQualified.value ? "success" : "fail")
      } : {}, {
        i: currentMode.value === "test"
      }, currentMode.value === "test" ? common_vendor.e({
        j: userScorePercent.value + "%",
        k: userScorePercent.value > 15
      }, userScorePercent.value > 15 ? {
        l: common_vendor.t(testCount.value)
      } : {}, {
        m: userScorePercent.value <= 15
      }, userScorePercent.value <= 15 ? {
        n: common_vendor.t(testCount.value)
      } : {}, {
        o: standardScorePercent.value + "%",
        p: standardScorePercent.value > 15
      }, standardScorePercent.value > 15 ? {
        q: common_vendor.t(standardReq.value)
      } : {}, {
        r: standardScorePercent.value <= 15
      }, standardScorePercent.value <= 15 ? {
        s: common_vendor.t(standardReq.value)
      } : {}, {
        t: common_vendor.t(suggestionText.value)
      }) : {
        v: common_vendor.t(formatDuration(duration.value)),
        w: common_vendor.t((distance.value / 1e3).toFixed(2))
      }, {
        x: currentMode.value === "police"
      }, currentMode.value === "police" ? {
        y: common_vendor.t(isPoliceFinish.value ? "✅ 已完成" : "❌ 未完成"),
        z: common_vendor.n(isPoliceFinish.value ? "success" : "fail"),
        A: common_vendor.t(isPaceQualified.value ? `✅ 达标（${policePace.value.toFixed(1)} 分/公里）` : `❌ 未达标（${policePace.value.toFixed(1)} 分/公里）`),
        B: common_vendor.n(isPaceQualified.value ? "success" : "fail")
      } : {}, {
        C: currentMode.value === "campus"
      }, currentMode.value === "campus" ? {
        D: common_vendor.t(isReach.value ? "✅ 已到达" : "❌ 未到达"),
        E: common_vendor.n(isReach.value ? "success" : "fail")
      } : {}, {
        F: currentMode.value === "normal"
      }, currentMode.value === "normal" ? {} : {}, {
        G: common_vendor.o(backToHome)
      });
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-b615976f"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/result/result.js.map
