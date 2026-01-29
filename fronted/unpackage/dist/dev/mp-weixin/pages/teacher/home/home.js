"use strict";
const common_vendor = require("../../../common/vendor.js");
const common_assets = require("../../../common/assets.js");
if (!Math) {
  CustomTabBar();
}
const CustomTabBar = () => "../../../components/CustomTabBar/CustomTabBar.js";
const _sfc_main = {
  __name: "home",
  setup(__props) {
    const userInfo = common_vendor.ref({});
    const goToApprove = () => {
      common_vendor.index.navigateTo({ url: "/pages/teacher/approve/approve" });
    };
    common_vendor.onShow(() => {
      common_vendor.index.hideHomeButton && common_vendor.index.hideHomeButton();
      const storedUser = common_vendor.index.getStorageSync("userInfo");
      if (storedUser) {
        try {
          userInfo.value = typeof storedUser === "string" ? JSON.parse(storedUser) : storedUser;
        } catch (e) {
          common_vendor.index.__f__("error", "at pages/teacher/home/home.vue:198", "JSON parse error", e);
          userInfo.value = {};
        }
      }
    });
    const teacherStats = common_vendor.ref({
      studentCount: 128,
      todayCheckin: 105,
      abnormalCount: 3,
      avgPace: `5'45"`,
      taskCount: 5,
      complianceRate: 92
    });
    const weeklyTrend = common_vendor.ref([
      { day: "周一", val: 60, color: "#e0e0e0" },
      { day: "周二", val: 80, color: "#e0e0e0" },
      { day: "周三", val: 45, color: "#e0e0e0" },
      { day: "周四", val: 90, color: "#20C997" },
      { day: "周五", val: 70, color: "#e0e0e0" },
      { day: "周六", val: 30, color: "#e0e0e0" },
      { day: "周日", val: 50, color: "#e0e0e0" }
    ]);
    const showTaskModal = common_vendor.ref(false);
    const isEditing = common_vendor.ref(false);
    const currentTask = common_vendor.ref({ title: "", type: "日常", desc: "" });
    const quickTasks = common_vendor.ref([
      { title: "3000米摸底测试", type: "考核", typeClass: "tag-red", status: "进行中", percent: 76 },
      { title: "周末晨跑打卡", type: "日常", typeClass: "tag-green", status: "进行中", percent: 35 },
      { title: "核心力量专项", type: "训练", typeClass: "tag-blue", status: "即将截止", percent: 88 }
    ]);
    const abnormalAlerts = common_vendor.ref([
      { id: 1, student: "张三", type: "心率过高", value: "195 bpm", time: "10:30" },
      { id: 2, student: "李四", type: "配速异常", value: "过快", time: "10:45" },
      { id: 3, student: "王五", type: "动作不达标", value: "引体向上", time: "10:50" }
    ]);
    const openTaskModal = () => {
      isEditing.value = false;
      currentTask.value = { title: "", type: "日常", desc: "" };
      showTaskModal.value = true;
    };
    const editTask = (task) => {
      isEditing.value = true;
      currentTask.value = { ...task, desc: "任务描述..." };
      showTaskModal.value = true;
    };
    const saveTask = () => {
      if (!currentTask.value.title)
        return common_vendor.index.showToast({ title: "请输入标题", icon: "none" });
      common_vendor.index.showToast({ title: isEditing.value ? "修改成功" : "发布成功", icon: "success" });
      showTaskModal.value = false;
    };
    const remindTask = (task) => {
      common_vendor.index.showToast({ title: `已催办任务: ${task.title}`, icon: "none" });
    };
    const handleQuickTask = (task) => {
      common_vendor.index.navigateTo({
        url: `/pages/teacher/tasks/detail?id=999&title=${task.title}`
      });
    };
    const handleResolveAlert = (index) => {
      common_vendor.index.showActionSheet({
        itemList: ["联系学生", "标记已处理", "查看详情"],
        success: (res) => {
          if (res.tapIndex === 1) {
            abnormalAlerts.value.splice(index, 1);
            teacherStats.value.abnormalCount = Math.max(0, teacherStats.value.abnormalCount - 1);
            common_vendor.index.showToast({ title: "已处理", icon: "success" });
          } else if (res.tapIndex === 0) {
            common_vendor.index.showToast({ title: "已发送通知", icon: "none" });
          } else {
            common_vendor.index.navigateTo({ url: "/pages/teacher/exceptions/exceptions" });
          }
        }
      });
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.t(userInfo.value.name || "老师"),
        b: common_assets._imports_0,
        c: common_vendor.t(teacherStats.value.todayCheckin),
        d: common_vendor.t(teacherStats.value.abnormalCount),
        e: common_vendor.t(teacherStats.value.pendingApprovals || 12),
        f: common_vendor.o(goToApprove),
        g: common_vendor.f(weeklyTrend.value, (d, i, i0) => {
          return {
            a: d.val + "%",
            b: d.color,
            c: common_vendor.t(d.day),
            d: i
          };
        }),
        h: common_vendor.o(openTaskModal),
        i: common_vendor.f(quickTasks.value, (task, idx, i0) => {
          return common_vendor.e({
            a: common_vendor.t(task.type),
            b: common_vendor.n(task.typeClass),
            c: common_vendor.t(task.status),
            d: common_vendor.t(task.title),
            e: task.percent + "%",
            f: common_vendor.t(task.percent),
            g: common_vendor.o(($event) => editTask(task), idx),
            h: task.percent < 100
          }, task.percent < 100 ? {
            i: common_vendor.o(($event) => remindTask(task), idx)
          } : {}, {
            j: common_vendor.o(() => {
            }, idx),
            k: idx,
            l: common_vendor.o(($event) => handleQuickTask(task), idx)
          });
        }),
        j: abnormalAlerts.value.length > 0
      }, abnormalAlerts.value.length > 0 ? {
        k: common_vendor.f(abnormalAlerts.value, (alert, idx, i0) => {
          return {
            a: common_vendor.t(alert.student),
            b: common_vendor.t(alert.type),
            c: common_vendor.t(alert.value),
            d: common_vendor.t(alert.time),
            e: common_vendor.o(($event) => handleResolveAlert(idx), idx),
            f: idx
          };
        })
      } : {}, {
        l: showTaskModal.value
      }, showTaskModal.value ? {
        m: common_vendor.t(isEditing.value ? "编辑任务" : "快速发布任务"),
        n: common_vendor.o(($event) => showTaskModal.value = false),
        o: currentTask.value.title,
        p: common_vendor.o(($event) => currentTask.value.title = $event.detail.value),
        q: currentTask.value.type === "考核" ? 1 : "",
        r: common_vendor.o(($event) => currentTask.value.type = "考核"),
        s: currentTask.value.type === "日常" ? 1 : "",
        t: common_vendor.o(($event) => currentTask.value.type = "日常"),
        v: currentTask.value.type === "训练" ? 1 : "",
        w: common_vendor.o(($event) => currentTask.value.type = "训练"),
        x: currentTask.value.desc,
        y: common_vendor.o(($event) => currentTask.value.desc = $event.detail.value),
        z: common_vendor.o(saveTask),
        A: common_vendor.o(() => {
        }),
        B: common_vendor.o(($event) => showTaskModal.value = false)
      } : {}, {
        C: common_vendor.p({
          current: "/pages/teacher/home/home"
        })
      });
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-c5a4d262"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../../.sourcemap/mp-weixin/pages/teacher/home/home.js.map
