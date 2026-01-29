"use strict";
const common_vendor = require("../../../common/vendor.js");
const utils_request = require("../../../utils/request.js");
const _sfc_main = {
  __name: "student-detail",
  setup(__props) {
    const studentId = common_vendor.ref(null);
    const studentName = common_vendor.ref("");
    const activities = common_vendor.ref([]);
    const totalDistance = common_vendor.computed(() => {
      const dist = activities.value.reduce((acc, cur) => {
        var _a;
        return acc + (((_a = cur.metrics) == null ? void 0 : _a.distance) || 0);
      }, 0);
      return dist.toFixed(2);
    });
    const totalDuration = common_vendor.computed(() => {
      const dur = activities.value.reduce((acc, cur) => {
        var _a;
        return acc + (((_a = cur.metrics) == null ? void 0 : _a.duration) || 0);
      }, 0);
      return Math.floor(dur / 60);
    });
    const getStatusText = (status) => {
      const map = {
        "pending": "待审批",
        "approved": "已通过",
        "rejected": "已驳回",
        "completed": "已完成",
        "finished": "已完成"
        // Default backend status
      };
      return map[status] || status;
    };
    const loadStudentData = async () => {
      if (!studentId.value)
        return;
      try {
        const res = await utils_request.getTeacherStudentActivities(studentId.value, { page: 1, size: 100 });
        if (res && res.items) {
          activities.value = res.items;
        }
      } catch (e) {
        common_vendor.index.__f__("error", "at pages/teacher/approve/student-detail.vue:81", e);
        common_vendor.index.showToast({ title: "加载失败", icon: "none" });
      }
    };
    common_vendor.onLoad((options) => {
      if (options.studentId) {
        studentId.value = options.studentId;
        studentName.value = options.studentName || "学生";
        loadStudentData();
      }
    });
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.t(studentName.value),
        b: common_vendor.t(totalDistance.value),
        c: common_vendor.t(totalDuration.value),
        d: common_vendor.t(activities.value.length),
        e: common_vendor.f(activities.value, (item, k0, i0) => {
          var _a, _b;
          return {
            a: common_vendor.t(item.type === "run" ? "跑步" : "体测"),
            b: common_vendor.t(((_a = item.metrics) == null ? void 0 : _a.distance) ? Number(item.metrics.distance).toFixed(2) : 0),
            c: common_vendor.t(((_b = item.metrics) == null ? void 0 : _b.duration) ? Math.floor(item.metrics.duration / 60) : 0),
            d: common_vendor.t(new Date(item.started_at).toLocaleString()),
            e: common_vendor.t(getStatusText(item.status)),
            f: common_vendor.n(item.status),
            g: item.id
          };
        }),
        f: activities.value.length === 0
      }, activities.value.length === 0 ? {} : {});
    };
  }
};
wx.createPage(_sfc_main);
//# sourceMappingURL=../../../../.sourcemap/mp-weixin/pages/teacher/approve/student-detail.js.map
