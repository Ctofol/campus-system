"use strict";
const common_vendor = require("../../../common/vendor.js");
const utils_request = require("../../../utils/request.js");
const _sfc_main = {
  __name: "list",
  setup(__props) {
    const currentTab = common_vendor.ref(0);
    const tasks = common_vendor.ref([]);
    const page = common_vendor.ref(1);
    const size = common_vendor.ref(20);
    const loading = common_vendor.ref(false);
    const loadTasks = async () => {
      if (loading.value)
        return;
      loading.value = true;
      try {
        const res = await utils_request.getStudentTasks({ page: page.value, size: size.value });
        if (res.items) {
          const newTasks = res.items.map((t) => ({
            ...t,
            statusText: t.status === "completed" ? "已完成" : t.status === "expired" ? "已过期" : "进行中",
            desc: t.description || (t.min_distance ? `目标: ${t.min_distance}km` : "无具体描述"),
            deadline: t.deadline ? t.deadline.split("T")[0] : "无限制"
          }));
          if (page.value === 1)
            tasks.value = newTasks;
          else
            tasks.value = [...tasks.value, ...newTasks];
        }
      } catch (e) {
        common_vendor.index.__f__("error", "at pages/student/tasks/list.vue:66", e);
        common_vendor.index.showToast({ title: "加载任务失败", icon: "none" });
      } finally {
        loading.value = false;
      }
    };
    const loadMore = () => {
    };
    common_vendor.onShow(() => {
      page.value = 1;
      loadTasks();
    });
    const filteredTasks = common_vendor.computed(() => {
      if (currentTab.value === 0) {
        return tasks.value.filter((t) => t.status === "pending");
      } else {
        return tasks.value.filter((t) => t.status !== "pending");
      }
    });
    const getTypeClass = (type) => {
      return type === "test" ? "tag-red" : "tag-blue";
    };
    const getStatusClass = (status) => {
      if (status === "completed")
        return "text-green";
      if (status === "expired")
        return "text-gray";
      return "text-orange";
    };
    const doTask = (item) => {
      if (item.type === "run") {
        common_vendor.index.navigateTo({ url: "/pages/run/run" });
      } else {
        common_vendor.index.navigateTo({ url: "/pages/test/test" });
      }
    };
    const goToDetail = (item) => {
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: currentTab.value === 0 ? 1 : "",
        b: common_vendor.o(($event) => currentTab.value = 0),
        c: currentTab.value === 1 ? 1 : "",
        d: common_vendor.o(($event) => currentTab.value = 1),
        e: common_vendor.f(filteredTasks.value, (item, k0, i0) => {
          return common_vendor.e({
            a: common_vendor.t(item.type === "run" ? "跑步" : "体测"),
            b: common_vendor.n(getTypeClass(item.type)),
            c: common_vendor.t(item.title),
            d: common_vendor.t(item.statusText),
            e: common_vendor.n(getStatusClass(item.status)),
            f: common_vendor.t(item.desc),
            g: common_vendor.t(item.deadline),
            h: item.status === "pending"
          }, item.status === "pending" ? {
            i: common_vendor.o(($event) => doTask(item), item.id)
          } : item.status === "completed" ? {} : {}, {
            j: item.status === "completed",
            k: item.id,
            l: common_vendor.o(($event) => goToDetail(), item.id)
          });
        }),
        f: loading.value
      }, loading.value ? {} : {}, {
        g: !loading.value && filteredTasks.value.length === 0
      }, !loading.value && filteredTasks.value.length === 0 ? {} : {}, {
        h: common_vendor.o(loadMore)
      });
    };
  }
};
wx.createPage(_sfc_main);
//# sourceMappingURL=../../../../.sourcemap/mp-weixin/pages/student/tasks/list.js.map
