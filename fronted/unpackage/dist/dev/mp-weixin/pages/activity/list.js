"use strict";
const common_vendor = require("../../common/vendor.js");
const _sfc_main = {
  __name: "list",
  setup(__props) {
    const activities = common_vendor.ref([
      { id: 1, name: "五四青年节环校跑", time: "5月4日 07:00", location: "南操场", status: "报名中", statusClass: "status-active", joined: 128, image: "" },
      { id: 2, name: "周末夜跑打卡赛", time: "本周六 19:00", location: "北田径场", status: "进行中", statusClass: "status-ing", joined: 56, image: "" },
      { id: 3, name: "警务技能交流会", time: "下周三 14:00", location: "体育馆", status: "预告", statusClass: "status-future", joined: 30, image: "" }
    ]);
    const goDetail = (item) => {
      common_vendor.index.navigateTo({
        url: `/pages/activity/detail?id=${item.id}&name=${item.name}`
      });
    };
    return (_ctx, _cache) => {
      return {
        a: common_vendor.f(activities.value, (item, index, i0) => {
          return {
            a: item.image || "/static/activity-placeholder.png",
            b: common_vendor.t(item.name),
            c: common_vendor.t(item.time),
            d: common_vendor.t(item.location),
            e: common_vendor.t(item.status),
            f: common_vendor.t(item.joined),
            g: common_vendor.n(item.statusClass),
            h: index,
            i: common_vendor.o(($event) => goDetail(item), index)
          };
        })
      };
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-e2466d57"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/activity/list.js.map
