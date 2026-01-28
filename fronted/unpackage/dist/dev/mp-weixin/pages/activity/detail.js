"use strict";
const common_vendor = require("../../common/vendor.js");
const common_assets = require("../../common/assets.js");
const _sfc_main = {
  __name: "detail",
  setup(__props) {
    const activity = common_vendor.ref({
      name: "加载中...",
      time: "待定",
      location: "待定",
      status: "报名中",
      joined: 0,
      limit: 100
    });
    common_vendor.onLoad((options) => {
      if (options.name) {
        activity.value.name = options.name;
        activity.value.time = "2026年5月4日 07:00";
        activity.value.location = "南操场主席台前";
        activity.value.joined = 128;
        activity.value.limit = 200;
      }
    });
    const handleJoin = () => {
      common_vendor.index.showToast({ title: "报名成功！", icon: "success" });
    };
    return (_ctx, _cache) => {
      return {
        a: common_assets._imports_0$1,
        b: common_vendor.t(activity.value.name),
        c: common_vendor.t(activity.value.status),
        d: common_vendor.t(activity.value.time),
        e: common_vendor.t(activity.value.location),
        f: common_vendor.t(activity.value.joined),
        g: common_vendor.t(activity.value.limit),
        h: common_vendor.o(handleJoin)
      };
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-19f90eeb"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/activity/detail.js.map
