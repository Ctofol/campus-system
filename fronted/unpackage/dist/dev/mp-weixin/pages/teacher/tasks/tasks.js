"use strict";
const common_vendor = require("../../../common/vendor.js");
const utils_request = require("../../../utils/request.js");
const _sfc_main = {
  __name: "tasks",
  setup(__props) {
    const currentTab = common_vendor.ref(0);
    const tasks = common_vendor.ref([]);
    const page = common_vendor.ref(1);
    const size = common_vendor.ref(20);
    const total = common_vendor.ref(0);
    const loading = common_vendor.ref(false);
    const loadTasks = async () => {
      if (loading.value)
        return;
      loading.value = true;
      try {
        const res = await utils_request.getTeacherTasks({ page: page.value, size: size.value });
        if (res.items) {
          const now = /* @__PURE__ */ new Date();
          const newTasks = res.items.map((item) => {
            const deadlineDate = new Date(item.deadline);
            const isExpired = deadlineDate < now;
            let displayType = "训练";
            if (item.type === "test")
              displayType = "考核";
            else if (item.type === "run")
              displayType = "日常";
            const completed = item.completed_count || 0;
            const totalCount = item.total_students || 0;
            const percent = totalCount > 0 ? Math.round(completed / totalCount * 100) : 0;
            return {
              id: item.id,
              title: item.title,
              type: displayType,
              desc: item.description || (item.min_distance ? `目标距离: ${item.min_distance}km` : "无具体描述"),
              status: isExpired ? "已结束" : "进行中",
              completed,
              total: totalCount,
              percent,
              deadline: item.deadline ? item.deadline.split("T")[0] : "无"
            };
          });
          if (page.value === 1) {
            tasks.value = newTasks;
          } else {
            tasks.value = [...tasks.value, ...newTasks];
          }
          total.value = res.total;
        }
      } catch (e) {
        common_vendor.index.__f__("error", "at pages/teacher/tasks/tasks.vue:162", e);
        common_vendor.index.showToast({ title: "加载任务失败", icon: "none" });
      } finally {
        loading.value = false;
      }
    };
    common_vendor.onShow(() => {
      page.value = 1;
      loadTasks();
    });
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
      if (!deadline || deadline === "无")
        return false;
      const d = new Date(deadline);
      const now = /* @__PURE__ */ new Date();
      const diffTime = Math.abs(d - now);
      const diffDays = Math.ceil(diffTime / (1e3 * 60 * 60 * 24));
      return diffDays <= 3 && d > now;
    };
    const goToDetail = (task) => {
      common_vendor.index.navigateTo({ url: `/pages/teacher/tasks/detail?id=${task.id}` });
    };
    const remindUnfinished = (task) => {
      common_vendor.index.showToast({ title: "提醒已发送", icon: "success" });
    };
    const showActionSheet = (task) => {
      common_vendor.index.showActionSheet({
        itemList: ["编辑任务", "删除任务"],
        itemColor: "#000000",
        success: async (res) => {
          if (res.tapIndex === 0) {
            common_vendor.index.showToast({ title: "编辑功能开发中", icon: "none" });
          } else if (res.tapIndex === 1) {
            handleDelete(task);
          }
        }
      });
    };
    const handleDelete = (task) => {
      common_vendor.index.showModal({
        title: "确认删除",
        content: `确定要删除任务"${task.title}"吗？`,
        success: async (res) => {
          if (res.confirm) {
            try {
              await utils_request.deleteTask(task.id);
              common_vendor.index.showToast({ title: "删除成功" });
              page.value = 1;
              loadTasks();
            } catch (e) {
              common_vendor.index.__f__("error", "at pages/teacher/tasks/tasks.vue:245", e);
              common_vendor.index.showToast({ title: "删除失败", icon: "none" });
            }
          }
        }
      });
    };
    const createTask = () => {
      common_vendor.index.navigateTo({
        url: "/pages/teacher/tasks/create"
      });
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
            e: common_vendor.o(($event) => showActionSheet(task), index),
            f: common_vendor.t(task.title),
            g: common_vendor.t(task.desc),
            h: common_vendor.t(task.percent),
            i: common_vendor.t(task.completed),
            j: common_vendor.t(task.total),
            k: task.percent + "%",
            l: common_vendor.f(3, (n, k1, i1) => {
              return {
                a: n,
                b: (n - 1) * 20 + "rpx",
                c: 4 - n
              };
            }),
            m: task.status === "进行中"
          }, task.status === "进行中" ? {
            n: common_vendor.o(($event) => remindUnfinished(), index)
          } : {}, {
            o: common_vendor.o(() => {
            }, index),
            p: index,
            q: common_vendor.o(($event) => goToDetail(task), index)
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
