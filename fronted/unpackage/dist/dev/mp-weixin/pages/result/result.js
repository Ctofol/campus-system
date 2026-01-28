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
    const testType = common_vendor.ref("");
    const testCount = common_vendor.ref(0);
    const testQualified = common_vendor.ref(false);
    const standardReq = common_vendor.ref(0);
    const userScorePercent = common_vendor.ref(0);
    const standardScorePercent = common_vendor.ref(0);
    const suggestionText = common_vendor.ref("");
    const isSaved = common_vendor.ref(false);
    const isSaving = common_vendor.ref(false);
    const modeTitle = common_vendor.computed(() => {
      switch (currentMode.value) {
        case "police":
          return "🚨 警务专项2000米训练结算";
        case "campus":
          return "🏫 校园打卡跑步结算";
        case "test":
          return "💪 警务体能测试结算";
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
      currentMode.value = options.mode || "normal";
      duration.value = Number(options.duration) || 0;
      distance.value = Number(options.distance) || 0;
      isReach.value = options.isReach === "true";
      isPoliceFinish.value = options.isPoliceFinish === "true";
      policePace.value = Number(options.policePace) || 0;
      if (currentMode.value === "test") {
        testProject.value = options.project || "";
        testCount.value = Number(options.count) || 0;
        const map = { "引体向上": "pull_up", "仰卧起坐": "sit_up", "俯卧撑": "push_up" };
        testType.value = map[testProject.value] || "";
        const threshold = { pull_up: 10, sit_up: 40, push_up: 30 };
        const req = threshold[testType.value] || 0;
        standardReq.value = req;
        testQualified.value = testCount.value >= req;
        const maxVal = Math.max(req * 1.5, testCount.value * 1.2, 1);
        userScorePercent.value = Math.min(testCount.value / maxVal * 100, 100);
        standardScorePercent.value = Math.min(req / maxVal * 100, 100);
        if (testQualified.value) {
          suggestionText.value = "恭喜达标！建议保持当前的训练频率，适当增加核心力量训练以进一步提升稳定性。";
        } else {
          const diff = req - testCount.value;
          suggestionText.value = `距离达标还差 ${diff} 次。建议加强上肢力量训练，每天进行3组辅助练习，注意动作规范。`;
        }
      }
    });
    const formatDuration = (seconds) => {
      const min = Math.floor(seconds / 60);
      const sec = seconds % 60;
      return `${min.toString().padStart(2, "0")}:${sec.toString().padStart(2, "0")}`;
    };
    const saveRunRecord = () => {
      if (isSaved.value || isSaving.value)
        return;
      isSaving.value = true;
      common_vendor.index.showLoading({ title: "保存中..." });
      if (currentMode.value !== "test") {
        const totalCount = Number(common_vendor.index.getStorageSync("totalRunCount")) || 0;
        common_vendor.index.setStorageSync("totalRunCount", totalCount + 1);
        const totalDistance = Number(common_vendor.index.getStorageSync("totalRunDistance")) || 0;
        common_vendor.index.setStorageSync("totalRunDistance", totalDistance + distance.value / 1e3);
        if (currentMode.value === "campus" && isReach.value) {
          const successCount = Number(common_vendor.index.getStorageSync("successCampusCount")) || 0;
          common_vendor.index.setStorageSync("successCampusCount", successCount + 1);
        }
        if (currentMode.value === "police" && isPoliceFinish.value && isPaceQualified.value) {
          const policeSuccessCount = Number(common_vendor.index.getStorageSync("policeSuccessCount")) || 0;
          common_vendor.index.setStorageSync("policeSuccessCount", policeSuccessCount + 1);
        }
      }
      const runRecordsList = common_vendor.index.getStorageSync("runRecordsList") || [];
      if (currentMode.value === "test") {
        runRecordsList.push({
          type: "police_test",
          testType: testType.value,
          testName: testProject.value,
          testCount: testCount.value,
          result: testQualified.value ? "合格" : "未合格",
          duration: duration.value,
          createTime: (/* @__PURE__ */ new Date()).getTime()
        });
      } else {
        const km = distance.value / 1e3;
        const min = duration.value / 60;
        const pace = km === 0 ? 0 : min / km;
        runRecordsList.push({
          type: "run",
          mode: currentMode.value,
          duration: duration.value,
          distance: distance.value / 1e3,
          pace,
          isReach: isReach.value,
          isPoliceFinish: isPoliceFinish.value,
          policePace: policePace.value,
          isPaceQualified: isPaceQualified.value,
          createTime: (/* @__PURE__ */ new Date()).getTime()
        });
      }
      common_vendor.index.setStorageSync("runRecordsList", runRecordsList);
      const db = common_vendor.tr.database();
      const runRecords = db.collection("run_records");
      const basePayload = { userId: common_vendor.index.getStorageSync("bindDeviceId") || "test_user", duration: duration.value, createTime: (/* @__PURE__ */ new Date()).getTime() };
      const payload = currentMode.value === "test" ? { ...basePayload, type: "police_test", testType: testType.value, testName: testProject.value, testCount: testCount.value, result: testQualified.value ? "合格" : "未合格" } : { ...basePayload, type: "run", mode: currentMode.value, distance: distance.value / 1e3, isReach: isReach.value, isPoliceFinish: isPoliceFinish.value, policePace: policePace.value, isPaceQualified: isPaceQualified.value };
      runRecords.add(payload).then(() => {
        isSaved.value = true;
        common_vendor.index.showToast({ title: "✅ 数据保存成功", icon: "success" });
      }).catch((err) => {
        common_vendor.index.__f__("error", "at pages/result/result.vue:276", "云端保存失败：", err);
        isSaved.value = true;
        common_vendor.index.showToast({ title: "⚠️ 本地保存成功，云端同步失败", icon: "none" });
      }).finally(() => {
        isSaving.value = false;
        common_vendor.index.hideLoading();
      });
    };
    const backToHome = () => {
      common_vendor.index.redirectTo({ url: "/pages/home/home" });
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
        G: common_vendor.t(isSaved.value ? "✅ 数据已保存" : isSaving.value ? "正在保存..." : "保存运动数据"),
        H: common_vendor.o(saveRunRecord),
        I: isSaved.value || isSaving.value,
        J: common_vendor.o(backToHome)
      });
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-b615976f"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/result/result.js.map
