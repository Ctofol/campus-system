"use strict";
const common_vendor = require("../../../common/vendor.js");
const _sfc_main = {
  __name: "create",
  setup(__props) {
    const taskTypes = ["普通跑步", "配速跑", "间歇跑", "体能测试"];
    const groupOptions = ["全员", "体能A组", "体能B组", "康复组"];
    const form = common_vendor.ref({
      title: "",
      type: "",
      distance: "",
      deadline: "",
      target: "全员",
      description: ""
    });
    const onTypeChange = (e) => {
      form.value.type = taskTypes[e.detail.value];
    };
    const onDateChange = (e) => {
      form.value.deadline = e.detail.value;
    };
    const onGroupChange = (e) => {
      form.value.target = groupOptions[e.detail.value];
    };
    const submitTask = () => {
      if (!form.value.title || !form.value.type || !form.value.deadline) {
        return common_vendor.index.showToast({ title: "请完善任务信息", icon: "none" });
      }
      common_vendor.index.showLoading({ title: "发布中..." });
      setTimeout(() => {
        common_vendor.index.hideLoading();
        common_vendor.index.showToast({ title: "任务发布成功", icon: "success" });
        ({
          id: "T" + Date.now(),
          title: form.value.title,
          type: form.value.type,
          deadline: form.value.deadline,
          progress: 0,
          total: 128,
          // Mock total
          completed: 0
        });
        setTimeout(() => {
          common_vendor.index.navigateBack();
        }, 1500);
      }, 1e3);
    };
    return (_ctx, _cache) => {
      return {
        a: form.value.title,
        b: common_vendor.o(($event) => form.value.title = $event.detail.value),
        c: common_vendor.t(form.value.type || "请选择任务类型"),
        d: taskTypes,
        e: common_vendor.o(onTypeChange),
        f: form.value.distance,
        g: common_vendor.o(($event) => form.value.distance = $event.detail.value),
        h: common_vendor.t(form.value.deadline || "请选择截止日期"),
        i: common_vendor.o(onDateChange),
        j: common_vendor.t(form.value.target || "全员"),
        k: groupOptions,
        l: common_vendor.o(onGroupChange),
        m: form.value.description,
        n: common_vendor.o(($event) => form.value.description = $event.detail.value),
        o: common_vendor.o(submitTask)
      };
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-ddf6333b"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../../.sourcemap/mp-weixin/pages/teacher/tasks/create.js.map
