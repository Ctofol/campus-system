"use strict";
const common_vendor = require("../../../common/vendor.js");
const utils_request = require("../../../utils/request.js");
const _sfc_main = {
  __name: "approve",
  setup(__props) {
    const activities = common_vendor.ref([]);
    const loadData = async () => {
      try {
        const res = await utils_request.getTeacherActivities({ page: 1, size: 20 });
        if (res && res.items) {
          activities.value = res.items;
        }
      } catch (e) {
        common_vendor.index.__f__("error", "at pages/teacher/approve/approve.vue:36", e);
        common_vendor.index.showToast({ title: "加载待审批活动失败", icon: "none" });
      }
    };
    const handleApprove = async (id) => {
      try {
        await utils_request.approveActivity(id);
        common_vendor.index.showToast({ title: "审批成功" });
        loadData();
      } catch (e) {
        common_vendor.index.__f__("error", "at pages/teacher/approve/approve.vue:47", e);
        common_vendor.index.showToast({ title: "审批失败，请稍后重试", icon: "none" });
      }
    };
    const goToDetail = (item) => {
      common_vendor.index.navigateTo({
        url: `/pages/teacher/approve/student-detail?studentId=${item.user_id}&studentName=${item.student_name}`
      });
    };
    common_vendor.onShow(() => {
      loadData();
    });
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.f(activities.value, (item, k0, i0) => {
          var _a;
          return {
            a: common_vendor.t(item.student_name),
            b: common_vendor.t(item.type === "run" ? "跑步" : "体测"),
            c: common_vendor.t(((_a = item.metrics) == null ? void 0 : _a.distance) ? Number(item.metrics.distance).toFixed(2) : 0),
            d: common_vendor.t(new Date(item.started_at).toLocaleString()),
            e: common_vendor.t(item.status === "approved" || item.status === "completed" ? "已通过" : "通过"),
            f: common_vendor.o(($event) => handleApprove(item.id), item.id),
            g: item.status === "approved" || item.status === "completed",
            h: item.status === "approved" || item.status === "completed" ? "#ccc" : "#20C997",
            i: item.id,
            j: common_vendor.o(($event) => goToDetail(item), item.id)
          };
        }),
        b: activities.value.length === 0
      }, activities.value.length === 0 ? {} : {});
    };
  }
};
wx.createPage(_sfc_main);
//# sourceMappingURL=../../../../.sourcemap/mp-weixin/pages/teacher/approve/approve.js.map
