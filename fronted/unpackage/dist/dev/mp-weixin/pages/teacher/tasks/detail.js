"use strict";
const common_vendor = require("../../../common/vendor.js");
const utils_request = require("../../../utils/request.js");
const _sfc_main = {
  __name: "detail",
  setup(__props) {
    const taskId = common_vendor.ref(null);
    const loading = common_vendor.ref(true);
    const task = common_vendor.ref({
      id: 0,
      title: "",
      status: "",
      statusText: "",
      dueDate: "",
      requirements: [],
      completedCount: 0,
      totalCount: 0
    });
    const students = common_vendor.ref([]);
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
    const goToStudentDetail = (student) => {
      common_vendor.index.navigateTo({
        url: `/pages/teacher/approve/student-detail?studentId=${student.id}&studentName=${student.name}`
      });
    };
    const fetchTaskDetail = async () => {
      if (!taskId.value)
        return;
      loading.value = true;
      try {
        const res = await utils_request.getTeacherTaskDetail(taskId.value);
        const reqs = [];
        if (res.type === "run") {
          reqs.push("任务类型: 跑步任务");
          if (res.min_distance)
            reqs.push(`最低距离: ${res.min_distance} km`);
          if (res.min_duration)
            reqs.push(`最低时长: ${res.min_duration} 分钟`);
        } else {
          reqs.push("任务类型: 体测任务");
          if (res.min_count)
            reqs.push(`最低次数: ${res.min_count} 次`);
        }
        if (res.description)
          reqs.push(`备注: ${res.description}`);
        const now = /* @__PURE__ */ new Date();
        const deadline = res.deadline ? new Date(res.deadline) : null;
        let status = "ongoing";
        let statusText = "进行中";
        if (deadline && deadline < now) {
          status = "ended";
          statusText = "已结束";
        }
        task.value = {
          id: res.id,
          title: res.title,
          status,
          statusText,
          dueDate: res.deadline ? res.deadline.replace("T", " ") : "无限制",
          requirements: reqs,
          completedCount: res.completed_count,
          totalCount: res.total_students
        };
        students.value = res.student_statuses.map((s) => ({
          id: s.student_id,
          name: s.student_name,
          studentId: `ID:${s.student_id}`,
          // Mock student ID if not available
          status: s.status === "completed" ? "completed" : "uncompleted",
          statusText: s.status === "completed" ? "已完成" : "未完成",
          metricValue: s.metric_value,
          avatar: ""
        }));
      } catch (e) {
        common_vendor.index.__f__("error", "at pages/teacher/tasks/detail.vue:178", e);
        common_vendor.index.showToast({ title: "加载失败", icon: "none" });
      } finally {
        loading.value = false;
      }
    };
    common_vendor.onLoad((options) => {
      if (options.id) {
        taskId.value = options.id;
        fetchTaskDetail();
      }
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
            d: student.metricValue && student.metricValue !== "-"
          }, student.metricValue && student.metricValue !== "-" ? {
            e: common_vendor.t(student.metricValue)
          } : {}, {
            f: common_vendor.t(student.statusText),
            g: common_vendor.n(student.status),
            h: student.status === "uncompleted"
          }, student.status === "uncompleted" ? {
            i: common_vendor.o(($event) => remindStudent(student), student.id)
          } : {}, {
            j: student.id,
            k: common_vendor.o(($event) => goToStudentDetail(student), student.id)
          });
        })
      };
    };
  }
};
wx.createPage(_sfc_main);
//# sourceMappingURL=../../../../.sourcemap/mp-weixin/pages/teacher/tasks/detail.js.map
