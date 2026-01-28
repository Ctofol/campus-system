"use strict";
const common_vendor = require("../../../common/vendor.js");
const _sfc_main = {
  __name: "detail",
  setup(__props) {
    const id = common_vendor.ref("");
    const name = common_vendor.ref("");
    const no = common_vendor.ref("");
    const className = common_vendor.ref("");
    const group = common_vendor.ref("体能A组");
    const healthStatus = common_vendor.ref("良好");
    const activeTab = common_vendor.ref("run");
    const runList = common_vendor.ref([
      { date: "05-10 07:20", distance: 3.2, duration: "00:22", modeText: "普通跑步", pace: `6'52"` },
      { date: "05-12 18:05", distance: 2, duration: "00:13", modeText: "警务专项", pace: `6'30"` },
      { date: "05-15 06:40", distance: 5, duration: "00:30", modeText: "耐力跑", pace: `6'00"` }
    ]);
    const testList = common_vendor.ref([
      { date: "05-08 09:30", testName: "引体向上", testCount: 12, result: "合格" },
      { date: "05-14 15:10", testName: "仰卧起坐", testCount: 35, result: "未合格" }
    ]);
    const totalDistance = common_vendor.computed(() => {
      return runList.value.reduce((acc, cur) => acc + cur.distance, 0).toFixed(1);
    });
    const healthClass = common_vendor.computed(() => {
      return healthStatus.value === "良好" ? "good" : "bad";
    });
    common_vendor.onLoad((opt) => {
      id.value = opt.id || "";
      name.value = opt.name || "";
      no.value = opt.no || "";
      className.value = opt.class || "";
    });
    common_vendor.onShow(() => {
      common_vendor.index.getStorageSync("userRole") || common_vendor.index.getStorageSync("role");
    });
    const contactStudent = () => {
      common_vendor.index.showActionSheet({
        itemList: ["拨打电话", "发送消息"],
        success: (res) => {
          common_vendor.index.showToast({ title: "操作已模拟", icon: "none" });
        }
      });
    };
    const exportReport = () => {
      common_vendor.index.showToast({ title: "正在生成PDF档案...", icon: "loading" });
      setTimeout(() => {
        common_vendor.index.showToast({ title: "导出成功", icon: "success" });
      }, 1500);
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.t(name.value.slice(0, 1)),
        b: common_vendor.t(name.value),
        c: common_vendor.t(healthStatus.value),
        d: common_vendor.n(healthClass.value),
        e: common_vendor.t(no.value),
        f: common_vendor.t(className.value),
        g: common_vendor.t(group.value || "未分组"),
        h: common_vendor.t(runList.value.length),
        i: common_vendor.t(totalDistance.value),
        j: common_vendor.t(testList.value.length),
        k: activeTab.value === "run" ? 1 : "",
        l: common_vendor.o(($event) => activeTab.value = "run"),
        m: activeTab.value === "test" ? 1 : "",
        n: common_vendor.o(($event) => activeTab.value = "test"),
        o: activeTab.value === "run"
      }, activeTab.value === "run" ? common_vendor.e({
        p: common_vendor.f(runList.value, (r, i, i0) => {
          return {
            a: common_vendor.t(r.date),
            b: common_vendor.t(r.modeText),
            c: common_vendor.t(r.distance),
            d: common_vendor.t(r.duration),
            e: common_vendor.t(r.pace || `5'30"`),
            f: "r" + i
          };
        }),
        q: runList.value.length === 0
      }, runList.value.length === 0 ? {} : {}) : common_vendor.e({
        r: common_vendor.f(testList.value, (t, i, i0) => {
          return {
            a: common_vendor.t(t.date),
            b: common_vendor.t(t.testName),
            c: common_vendor.t(t.result),
            d: common_vendor.n(t.result === "合格" ? "pass" : "fail"),
            e: common_vendor.t(t.testCount),
            f: "t" + i
          };
        }),
        s: testList.value.length === 0
      }, testList.value.length === 0 ? {} : {}), {
        t: common_vendor.o(contactStudent),
        v: common_vendor.o(exportReport)
      });
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-c1f3574c"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../../.sourcemap/mp-weixin/pages/teacher/students/detail.js.map
