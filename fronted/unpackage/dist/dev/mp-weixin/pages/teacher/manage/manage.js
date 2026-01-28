"use strict";
const common_vendor = require("../../../common/vendor.js");
if (!Math) {
  CustomTabBar();
}
const CustomTabBar = () => "../../../components/CustomTabBar/CustomTabBar.js";
const _sfc_main = {
  __name: "manage",
  setup(__props) {
    common_vendor.onShow(() => {
      common_vendor.index.hideHomeButton && common_vendor.index.hideHomeButton();
    });
    const navTo = (url) => {
      common_vendor.index.navigateTo({ url });
    };
    const showToast = (title) => {
      common_vendor.index.showToast({
        title: `${title}功能开发中`,
        icon: "none"
      });
    };
    return (_ctx, _cache) => {
      return {
        a: common_vendor.o(($event) => navTo("/pages/teacher/students/students")),
        b: common_vendor.o(($event) => showToast("班级管理")),
        c: common_vendor.o(($event) => navTo("/pages/teacher/tasks/tasks")),
        d: common_vendor.o(($event) => showToast("教学资源")),
        e: common_vendor.o(($event) => navTo("/pages/teacher/tests/tests")),
        f: common_vendor.o(($event) => showToast("数据导出")),
        g: common_vendor.o(($event) => navTo("/pages/teacher/exceptions/exceptions")),
        h: common_vendor.o(($event) => showToast("通知公告")),
        i: common_vendor.p({
          current: "/pages/teacher/manage/manage"
        })
      };
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-b30bafb4"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../../.sourcemap/mp-weixin/pages/teacher/manage/manage.js.map
