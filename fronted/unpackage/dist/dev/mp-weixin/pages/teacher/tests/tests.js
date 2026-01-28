"use strict";
const common_vendor = require("../../../common/vendor.js");
const _sfc_main = {
  __name: "tests",
  setup(__props) {
    const currentTab = common_vendor.ref("live");
    const liveStudents = common_vendor.ref([
      { name: "张伟", action: "引体向上", currentScore: 8, isAbnormal: false, confidence: 98 },
      { name: "李强", action: "仰卧起坐", currentScore: 24, isAbnormal: true, confidence: 85 },
      { name: "王芳", action: "深蹲", currentScore: 15, isAbnormal: false, confidence: 96 },
      { name: "赵杰", action: "俯卧撑", currentScore: 12, isAbnormal: false, confidence: 99 }
    ]);
    const classSkills = common_vendor.ref([
      { name: "爆发力", val: 85, color: "#ff6b6b" },
      { name: "耐力", val: 72, color: "#4dabf7" },
      { name: "柔韧性", val: 68, color: "#ffd43b" },
      { name: "协调性", val: 90, color: "#20C997" },
      { name: "核心力量", val: 78, color: "#a55eea" }
    ]);
    const classComparison = common_vendor.ref([
      { label: "优秀", value: 15, percent: 30, color: "#20C997" },
      { label: "良好", value: 45, percent: 60, color: "#4dabf7" },
      { label: "及格", value: 30, percent: 45, color: "#ffd43b" },
      { label: "不及格", value: 10, percent: 20, color: "#ff6b6b" }
    ]);
    const passRates = common_vendor.ref([
      { name: "1000米跑", rate: 85 },
      { name: "引体向上", rate: 62 },
      { name: "立定跳远", rate: 94 },
      { name: "坐位体前屈", rate: 78 }
    ]);
    const historyList = common_vendor.ref([
      { date: "2026-05-18", testName: "全员体能摸底测试", count: 128, passRate: 92 },
      { date: "2026-05-10", testName: "力量专项考核", count: 45, passRate: 88 },
      { date: "2026-04-28", testName: "耐力跑测试", count: 128, passRate: 76 }
    ]);
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: currentTab.value === "live"
      }, currentTab.value === "live" ? {} : {}, {
        b: currentTab.value === "live" ? 1 : "",
        c: common_vendor.o(($event) => currentTab.value = "live"),
        d: currentTab.value === "analysis"
      }, currentTab.value === "analysis" ? {} : {}, {
        e: currentTab.value === "analysis" ? 1 : "",
        f: common_vendor.o(($event) => currentTab.value = "analysis"),
        g: currentTab.value === "history"
      }, currentTab.value === "history" ? {} : {}, {
        h: currentTab.value === "history" ? 1 : "",
        i: common_vendor.o(($event) => currentTab.value = "history"),
        j: currentTab.value === "live"
      }, currentTab.value === "live" ? {
        k: common_vendor.f(liveStudents.value, (stu, idx, i0) => {
          return common_vendor.e({
            a: common_vendor.t(stu.confidence),
            b: stu.isAbnormal ? "#ff6b6b" : "#0f0",
            c: common_vendor.t(stu.currentScore),
            d: common_vendor.t(stu.name),
            e: common_vendor.t(stu.action),
            f: stu.isAbnormal
          }, stu.isAbnormal ? {} : {}, {
            g: idx
          });
        })
      } : {}, {
        l: currentTab.value === "analysis"
      }, currentTab.value === "analysis" ? {
        m: common_vendor.f(classSkills.value, (skill, idx, i0) => {
          return {
            a: common_vendor.t(skill.name),
            b: skill.val + "%",
            c: skill.color,
            d: common_vendor.t(skill.val),
            e: idx
          };
        }),
        n: common_vendor.f(classComparison.value, (item, idx, i0) => {
          return {
            a: item.percent + "%",
            b: item.color,
            c: common_vendor.t(item.value),
            d: common_vendor.t(item.label),
            e: idx
          };
        }),
        o: common_vendor.f(passRates.value, (p, idx, i0) => {
          return {
            a: common_vendor.t(p.name),
            b: common_vendor.t(p.rate),
            c: p.rate + "%",
            d: idx
          };
        })
      } : {}, {
        p: currentTab.value === "history"
      }, currentTab.value === "history" ? {
        q: common_vendor.f(historyList.value, (h, idx, i0) => {
          return {
            a: common_vendor.t(h.date),
            b: common_vendor.t(h.testName),
            c: common_vendor.t(h.count),
            d: common_vendor.t(h.passRate),
            e: idx
          };
        })
      } : {});
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-20d5ebe7"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../../.sourcemap/mp-weixin/pages/teacher/tests/tests.js.map
