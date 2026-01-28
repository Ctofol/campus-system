"use strict";
const common_vendor = require("../../../common/vendor.js");
const _sfc_main = {
  __name: "detail",
  setup(__props) {
    const task = common_vendor.ref({
      id: 1,
      title: "本周5公里耐力跑",
      status: "ongoing",
      statusText: "进行中",
      dueDate: "2026-01-25",
      requirements: [
        "单次跑步距离不少于5公里",
        `配速要求在4'00" - 7'00"之间`,
        "需上传跑步轨迹和心率数据"
      ],
      completedCount: 32,
      totalCount: 45
    });
    const students = common_vendor.ref([
      { id: 1, name: "张三", studentId: "2023001", status: "completed", statusText: "已完成", avatar: "" },
      { id: 2, name: "李四", studentId: "2023002", status: "uncompleted", statusText: "未完成", avatar: "" },
      { id: 3, name: "王五", studentId: "2023003", status: "completed", statusText: "已完成", avatar: "" },
      { id: 4, name: "赵六", studentId: "2023004", status: "uncompleted", statusText: "未完成", avatar: "" }
      // Mock data...
    ]);
    const currentFilter = common_vendor.ref("all");
    const completionPercentage = common_vendor.computed(() => {
      if (task.value.totalCount === 0)
        return 0;
      return Math.round(task.value.completedCount / task.value.totalCount * 100);
    });
    const filteredStudents = common_vendor.computed(() => {
      if (currentFilter.value === "all")
        return students.value;
      return students.value.filter((s) => s.status === currentFilter.value);
    });
    const remindStudent = (student) => {
      common_vendor.index.showToast({
        title: `已发送提醒给 ${student.name}`,
        icon: "success"
      });
    };
    common_vendor.onMounted(() => {
    });
    return (_ctx, _cache) => {
      return {
        a: common_vendor.t(task.value.title),
        b: common_vendor.t(task.value.statusText),
        c: common_vendor.n(task.value.status),
        d: common_vendor.t(task.value.dueDate),
        e: common_vendor.f(task.value.requirements, (req, index, i0) => {
          return {
            a: common_vendor.t(req),
            b: index
          };
        }),
        f: common_vendor.t(task.value.completedCount),
        g: common_vendor.t(task.value.totalCount),
        h: completionPercentage.value + "%",
        i: common_vendor.t(completionPercentage.value),
        j: currentFilter.value === "all" ? 1 : "",
        k: common_vendor.o(($event) => currentFilter.value = "all"),
        l: currentFilter.value === "uncompleted" ? 1 : "",
        m: common_vendor.o(($event) => currentFilter.value = "uncompleted"),
        n: common_vendor.f(filteredStudents.value, (student, k0, i0) => {
          return common_vendor.e({
            a: student.avatar || "/static/avatar.png",
            b: common_vendor.t(student.name),
            c: common_vendor.t(student.studentId),
            d: common_vendor.t(student.statusText),
            e: common_vendor.n(student.status),
            f: student.status === "uncompleted"
          }, student.status === "uncompleted" ? {
            g: common_vendor.o(($event) => remindStudent(student), student.id)
          } : {}, {
            h: student.id
          });
        })
      };
    };
  }
};
wx.createPage(_sfc_main);
//# sourceMappingURL=../../../../.sourcemap/mp-weixin/pages/teacher/tasks/detail.js.map
