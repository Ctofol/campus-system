"use strict";
const common_vendor = require("../../common/vendor.js");
if (!Array) {
  const _easycom_CustomTabBar2 = common_vendor.resolveComponent("CustomTabBar");
  _easycom_CustomTabBar2();
}
const _easycom_CustomTabBar = () => "../../components/CustomTabBar/CustomTabBar.js";
if (!Math) {
  _easycom_CustomTabBar();
}
const _sfc_main = {
  __name: "test",
  setup(__props) {
    const projectName = common_vendor.ref("引体向上");
    const standardDesc = common_vendor.ref("下颌过杠，双臂伸直");
    const testType = common_vendor.ref("pull-up");
    const role = common_vendor.ref("student");
    const isTesting = common_vendor.ref(false);
    const count = common_vendor.ref(0);
    const duration = common_vendor.ref(0);
    const timer = common_vendor.ref(null);
    const isStandard = common_vendor.ref(true);
    const statusText = common_vendor.ref("准备就绪");
    common_vendor.ref(false);
    const targetCount = common_vendor.ref(10);
    const projectEmoji = common_vendor.computed(() => {
      const map = {
        "pull-up": "💪",
        "sit-up": "🧘",
        "push-up": "🤸",
        "run-1000": "🏃",
        "run-800": "🏃‍♀️"
      };
      return map[testType.value] || "🏋️";
    });
    const progressPercent = common_vendor.computed(() => {
      return Math.min(count.value / targetCount.value * 100, 100);
    });
    const handleOptions = (options) => {
      if (options.project)
        projectName.value = options.project;
      if (options.type)
        testType.value = options.type;
      const standards = {
        "引体向上": "下颌过杠，双臂伸直",
        "仰卧起坐": "双手抱头，肘部触膝",
        "俯卧撑": "身体平直，屈臂90度"
      };
      const targets = {
        "引体向上": 10,
        "仰卧起坐": 40,
        "俯卧撑": 30
      };
      if (standards[projectName.value]) {
        standardDesc.value = standards[projectName.value];
      }
      if (targets[projectName.value]) {
        targetCount.value = targets[projectName.value];
      }
    };
    common_vendor.onLoad((options) => {
      handleOptions(options);
    });
    common_vendor.onShow(() => {
      const r = common_vendor.index.getStorageSync("userRole") || common_vendor.index.getStorageSync("role");
      if (r)
        role.value = r;
      const storedProject = common_vendor.index.getStorageSync("testProject");
      const storedType = common_vendor.index.getStorageSync("testType");
      if (storedProject) {
        handleOptions({ project: storedProject, type: storedType });
        common_vendor.index.removeStorageSync("testProject");
        common_vendor.index.removeStorageSync("testType");
        common_vendor.index.showToast({ title: "已清理传参缓存", icon: "none" });
      }
    });
    const showSelector = common_vendor.ref(false);
    const showTypeSelector = () => {
      showSelector.value = !showSelector.value;
    };
    const switchTestType = (project, type) => {
      handleOptions({ project, type });
      showSelector.value = false;
    };
    const formatTime = (seconds) => {
      const m = Math.floor(seconds / 60);
      const s = seconds % 60;
      return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
    };
    const startTest = () => {
      isTesting.value = true;
      count.value = 0;
      duration.value = 0;
      statusText.value = "正在识别动作...";
      timer.value = setInterval(() => {
        duration.value++;
      }, 1e3);
    };
    const mockCount = () => {
      count.value++;
      statusText.value = "动作标准 ✅";
      setTimeout(() => {
        statusText.value = "正在识别动作...";
      }, 800);
    };
    const endTest = () => {
      clearInterval(timer.value);
      isTesting.value = false;
      common_vendor.index.showModal({
        title: "测试结束",
        content: `共完成 ${count.value} 次，用时 ${formatTime(duration.value)}，是否提交成绩？`,
        confirmText: "提交结果",
        cancelText: "放弃",
        success: (res) => {
          if (res.confirm) {
            submitResult();
          } else {
            count.value = 0;
            duration.value = 0;
            statusText.value = "准备就绪";
          }
        }
      });
    };
    const submitResult = () => {
      common_vendor.index.showLoading({ title: "正在提交成绩..." });
      ({
        mode: "test",
        testProject: projectName.value,
        count: count.value,
        duration: duration.value,
        isStandard: true,
        testDate: (/* @__PURE__ */ new Date()).getTime()
      });
      setTimeout(() => {
        common_vendor.index.hideLoading();
        common_vendor.index.navigateTo({
          url: `/pages/result/result?mode=test&project=${projectName.value}&count=${count.value}&duration=${duration.value}`
        });
      }, 1e3);
    };
    const gotoStudents = () => {
      common_vendor.index.navigateTo({ url: "/pages/teacher/students/students" });
    };
    const handleCameraError = (e) => {
      common_vendor.index.__f__("error", "at pages/test/test.vue:325", "Camera Error:", e);
      let msg = "无法访问摄像头";
      if (e.name === "NotAllowedError" || e.message === "Permission denied") {
        msg = "权限被拒绝，请允许摄像头访问";
      } else if (e.name === "NotFoundError") {
        msg = "未检测到摄像头";
      }
      common_vendor.index.showToast({
        title: msg,
        icon: "none",
        duration: 3e3
      });
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: role.value === "teacher"
      }, role.value === "teacher" ? {
        b: common_vendor.o(gotoStudents)
      } : common_vendor.e({
        c: common_vendor.t(projectName.value),
        d: common_vendor.t(standardDesc.value),
        e: common_vendor.t(projectEmoji.value),
        f: common_vendor.o(showTypeSelector),
        g: showSelector.value
      }, showSelector.value ? {
        h: common_vendor.o(($event) => switchTestType("引体向上", "pull-up")),
        i: common_vendor.o(($event) => switchTestType("仰卧起坐", "sit-up")),
        j: common_vendor.o(($event) => switchTestType("俯卧撑", "push-up"))
      } : {}, {
        k: common_vendor.t(count.value),
        l: progressPercent.value + "%",
        m: common_vendor.t(statusText.value),
        n: isStandard.value ? 1 : "",
        o: common_vendor.o(handleCameraError),
        p: common_vendor.t(formatTime(duration.value)),
        q: !isTesting.value
      }, !isTesting.value ? {
        r: common_vendor.o(startTest)
      } : {
        s: common_vendor.o(endTest),
        t: common_vendor.o(mockCount)
      }), {
        v: common_vendor.p({
          current: "/pages/test/test"
        })
      });
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-727d09f0"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/test/test.js.map
