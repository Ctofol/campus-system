"use strict";
const common_vendor = require("../../../common/vendor.js");
if (!Math) {
  CustomTabBar();
}
const CustomTabBar = () => "../../../components/CustomTabBar/CustomTabBar.js";
const _sfc_main = {
  __name: "mine",
  setup(__props) {
    const userInfo = common_vendor.ref({});
    common_vendor.onShow(() => {
      common_vendor.index.hideHomeButton && common_vendor.index.hideHomeButton();
      const storedUser = common_vendor.index.getStorageSync("userInfo");
      if (storedUser) {
        try {
          userInfo.value = typeof storedUser === "string" ? JSON.parse(storedUser) : storedUser;
        } catch (e) {
          userInfo.value = {};
        }
      }
    });
    const handleLogout = () => {
      common_vendor.index.removeStorageSync("userInfo");
      common_vendor.index.removeStorageSync("userRole");
      common_vendor.index.reLaunch({
        url: "/pages/login/login"
      });
    };
    return (_ctx, _cache) => {
      return {
        a: common_vendor.t(userInfo.value.name || "教官"),
        b: common_vendor.o(($event) => common_vendor.index.showToast({
          title: "设置功能开发中",
          icon: "none"
        })),
        c: common_vendor.o(($event) => common_vendor.index.showToast({
          title: "安全中心开发中",
          icon: "none"
        })),
        d: common_vendor.o(($event) => common_vendor.index.showToast({
          title: "暂无新通知",
          icon: "none"
        })),
        e: common_vendor.o(($event) => common_vendor.index.showToast({
          title: "请联系管理员",
          icon: "none"
        })),
        f: common_vendor.o(handleLogout),
        g: common_vendor.p({
          current: "/pages/teacher/mine/mine"
        })
      };
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-f7dece31"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../../.sourcemap/mp-weixin/pages/teacher/mine/mine.js.map
