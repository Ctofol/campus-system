"use strict";
const common_vendor = require("../../common/vendor.js");
const _sfc_main = {
  __name: "ai-police",
  setup(__props) {
    const isDetecting = common_vendor.ref(false);
    const count = common_vendor.ref(0);
    const statusText = common_vendor.ref("准备就绪");
    const statusClass = common_vendor.ref("normal");
    const confidence = common_vendor.ref(0);
    const posture = common_vendor.ref("Standing");
    let timer = null;
    const startDetect = () => {
      isDetecting.value = true;
      statusText.value = "正在检测...";
      statusClass.value = "normal";
      count.value = 0;
      startSimulationLoop();
    };
    const stopDetect = () => {
      isDetecting.value = false;
      statusText.value = "训练结束";
      clearInterval(timer);
      common_vendor.index.showModal({
        title: "训练结束",
        content: `本次训练共完成 ${count.value} 次，是否查看结果？`,
        confirmText: "查看结果",
        cancelText: "取消",
        success: (res) => {
          if (res.confirm) {
            common_vendor.index.showLoading({ title: "正在保存..." });
            setTimeout(() => {
              common_vendor.index.hideLoading();
              common_vendor.index.navigateTo({
                url: `/pages/result/result?mode=test&project=AI智能训练&count=${count.value}&duration=0`
              });
            }, 800);
          }
        }
      });
    };
    const startSimulationLoop = () => {
      timer = setInterval(() => {
        confidence.value = (95 + Math.random() * 5).toFixed(1);
      }, 1e3);
    };
    const simValidAction = () => {
      if (!isDetecting)
        return;
      statusText.value = "动作标准";
      statusClass.value = "success";
      posture.value = "Squat Down";
      setTimeout(() => {
        count.value++;
        posture.value = "Standing";
        statusText.value = "正在检测...";
        statusClass.value = "normal";
      }, 800);
    };
    const simCheat = (type) => {
      if (!isDetecting)
        return;
      statusText.value = `警告：${type}`;
      statusClass.value = "warn";
      confidence.value = (Math.random() * 40).toFixed(1);
      common_vendor.index.vibrateLong();
      common_vendor.index.showToast({
        title: `检测到异常：${type}`,
        icon: "none",
        duration: 2e3
      });
      setTimeout(() => {
        statusText.value = "正在检测...";
        statusClass.value = "normal";
        confidence.value = 98.5;
      }, 2e3);
    };
    const handleCameraError = (e) => {
      common_vendor.index.__f__("error", "at pages/ai-police/ai-police.vue:209", "Camera Error:", e);
      let msg = "无法访问摄像头";
      if (e.name === "NotAllowedError" || e.message === "Permission denied") {
        msg = "权限被拒绝，请在设置中允许摄像头访问";
      } else if (e.name === "NotFoundError") {
        msg = "未检测到摄像头设备";
      } else if (e.name === "NotSupportedError") {
        msg = "浏览器不支持该摄像头配置";
      }
      common_vendor.index.showToast({
        title: msg,
        icon: "none",
        duration: 3e3
      });
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: !isDetecting.value
      }, !isDetecting.value ? {} : {}, {
        b: isDetecting.value
      }, isDetecting.value ? {
        c: common_vendor.t(confidence.value),
        d: common_vendor.t(posture.value)
      } : {}, {
        e: common_vendor.o(handleCameraError),
        f: common_vendor.t(count.value),
        g: common_vendor.t(statusText.value),
        h: common_vendor.n(statusClass.value),
        i: !isDetecting.value
      }, !isDetecting.value ? {
        j: common_vendor.o(startDetect)
      } : {
        k: common_vendor.o(stopDetect)
      }, {
        l: common_vendor.o(simValidAction),
        m: common_vendor.o(($event) => simCheat("遮挡")),
        n: common_vendor.o(($event) => simCheat("多人")),
        o: common_vendor.o(($event) => simCheat("非活体"))
      });
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-97c40662"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/ai-police/ai-police.js.map
