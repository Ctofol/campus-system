"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const common_vendor = require("./common/vendor.js");
if (!Math) {
  "./pages/home/home.js";
  "./pages/run/run.js";
  "./pages/mine/mine.js";
  "./pages/result/result.js";
  "./pages/login/login.js";
  "./pages/register/register.js";
  "./pages/test/test.js";
  "./pages/student/tasks/list.js";
  "./pages/teacher/home/home.js";
  "./pages/teacher/manage/manage.js";
  "./pages/teacher/mine/mine.js";
  "./pages/teacher/students/students.js";
  "./pages/teacher/students/detail.js";
  "./pages/teacher/tasks/tasks.js";
  "./pages/teacher/tasks/detail.js";
  "./pages/teacher/tasks/create.js";
  "./pages/teacher/exceptions/exceptions.js";
  "./pages/teacher/tests/tests.js";
  "./pages/teacher/approve/approve.js";
  "./pages/teacher/approve/student-detail.js";
  "./pages/activity/list.js";
  "./pages/activity/detail.js";
  "./pages/ai-police/ai-police.js";
}
const _sfc_main = {
  onLaunch: function() {
    try {
      const userInfo = common_vendor.index.getStorageSync("userInfo");
      if (!userInfo) {
        common_vendor.index.reLaunch({
          url: "/pages/login/login",
          success: () => {
          },
          fail: (err) => {
            common_vendor.index.__f__("error", "at App.vue:20", "跳转登录页失败:", err);
          }
        });
      } else {
      }
    } catch (e) {
      common_vendor.index.__f__("error", "at App.vue:27", "读取缓存失败:", e);
      common_vendor.index.reLaunch({ url: "/pages/login/login" });
    }
  },
  onShow: function() {
  },
  onHide: function() {
  }
};
function createApp() {
  const app = common_vendor.createSSRApp(_sfc_main);
  return {
    app
  };
}
createApp().app.mount("#app");
exports.createApp = createApp;
//# sourceMappingURL=../.sourcemap/mp-weixin/app.js.map
