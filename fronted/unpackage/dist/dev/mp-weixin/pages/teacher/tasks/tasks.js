"use strict";
const common_vendor = require("../../../common/vendor.js");
const _sfc_main = {
  __name: "tasks",
  setup(__props) {
    const currentTab = common_vendor.ref(0);
    const tasks = common_vendor.ref([
      {
        id: 1,
        title: "3000米摸底测试",
        type: "考核",
        desc: "全员必须参加，记录成绩，作为期末考核参考。",
        status: "进行中",
        completed: 98,
        total: 128,
        percent: 76,
        deadline: "2026-05-20"
      },
      {
        id: 2,
        title: "周末晨跑打卡",
        type: "日常",
        desc: "不少于3公里，配速不低于7分，保持良好的体能状态。",
        status: "进行中",
        completed: 45,
        total: 128,
        percent: 35,
        deadline: "2026-05-21"
      },
      {
        id: 3,
        title: "核心力量专项训练",
        type: "训练",
        desc: "完成3组平板支撑，每组2分钟，强化核心肌群。",
        status: "已结束",
        completed: 120,
        total: 128,
        percent: 93,
        deadline: "2026-05-18"
      },
      {
        id: 4,
        title: "5公里耐力跑",
        type: "训练",
        desc: "为下月运动会做准备，提升耐力。",
        status: "已结束",
        completed: 110,
        total: 128,
        percent: 85,
        deadline: "2026-05-15"
      }
    ]);
    const ongoingCount = common_vendor.computed(() => tasks.value.filter((t) => t.status === "进行中").length);
    const totalTasks = common_vendor.computed(() => tasks.value.length);
    const avgCompletion = common_vendor.computed(() => {
      if (tasks.value.length === 0)
        return 0;
      const sum = tasks.value.reduce((acc, cur) => acc + cur.percent, 0);
      return Math.round(sum / tasks.value.length);
    });
    const filteredTasks = common_vendor.computed(() => {
      if (currentTab.value === 0) {
        return tasks.value.filter((t) => t.status === "进行中");
      } else {
        return tasks.value.filter((t) => t.status !== "进行中");
      }
    });
    const getTypeClass = (type) => {
      const map = {
        "考核": "tag-red",
        "日常": "tag-green",
        "训练": "tag-blue"
      };
      return map[type] || "tag-gray";
    };
    const isUrgent = (deadline) => {
      return deadline === "2026-05-20";
    };
    const createTask = () => {
      common_vendor.index.navigateTo({
        url: "/pages/teacher/tasks/create"
      });
    };
    const goToDetail = (task) => {
      common_vendor.index.navigateTo({
        url: `/pages/teacher/tasks/detail?id=${task.id}&title=${task.title}`
      });
    };
    const remindUnfinished = (task) => {
      common_vendor.index.showToast({ title: `已发送提醒给${task.total - task.completed}名未完成学生`, icon: "none" });
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.t(ongoingCount.value),
        b: common_vendor.t(avgCompletion.value),
        c: common_vendor.t(totalTasks.value),
        d: currentTab.value === 0
      }, currentTab.value === 0 ? {} : {}, {
        e: currentTab.value === 0 ? 1 : "",
        f: common_vendor.o(($event) => currentTab.value = 0),
        g: currentTab.value === 1
      }, currentTab.value === 1 ? {} : {}, {
        h: currentTab.value === 1 ? 1 : "",
        i: common_vendor.o(($event) => currentTab.value = 1),
        j: common_vendor.f(filteredTasks.value, (task, index, i0) => {
          return common_vendor.e({
            a: common_vendor.t(task.type),
            b: common_vendor.n(getTypeClass(task.type)),
            c: common_vendor.t(task.deadline),
            d: isUrgent(task.deadline) ? 1 : "",
            e: common_vendor.t(task.title),
            f: common_vendor.t(task.desc),
            g: common_vendor.t(task.percent),
            h: common_vendor.t(task.completed),
            i: common_vendor.t(task.total),
            j: task.percent + "%",
            k: common_vendor.f(3, (n, k1, i1) => {
              return {
                a: n,
                b: (n - 1) * 20 + "rpx",
                c: 4 - n
              };
            }),
            l: task.status === "进行中"
          }, task.status === "进行中" ? {
            m: common_vendor.o(($event) => remindUnfinished(task), index)
          } : {}, {
            n: common_vendor.o(() => {
            }, index),
            o: index,
            p: common_vendor.o(($event) => goToDetail(task), index)
          });
        }),
        k: "60rpx",
        l: filteredTasks.value.length === 0
      }, filteredTasks.value.length === 0 ? {} : {}, {
        m: common_vendor.o(createTask)
      });
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-6877fe60"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../../.sourcemap/mp-weixin/pages/teacher/tasks/tasks.js.map
