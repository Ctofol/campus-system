"use strict";
const common_vendor = require("../../../common/vendor.js");
const utils_request = require("../../../utils/request.js");
const _sfc_main = {
  __name: "create",
  setup(__props) {
    const taskTypes = ["run", "test"];
    const taskTypeLabels = ["跑步任务", "体能测试"];
    const groupOptions = ["all", "group_a", "group_b"];
    const groupLabels = ["全员", "体能A组", "体能B组"];
    const form = common_vendor.ref({
      title: "",
      type: "",
      typeLabel: "",
      distance: "",
      deadline: "",
      target: "all",
      targetLabel: "全员",
      description: ""
    });
    const onTypeChange = (e) => {
      const index = e.detail.value;
      form.value.type = taskTypes[index];
      form.value.typeLabel = taskTypeLabels[index];
    };
    const onDateChange = (e) => {
      form.value.deadline = e.detail.value;
    };
    const onGroupChange = (e) => {
      const index = e.detail.value;
      form.value.target = groupOptions[index];
      form.value.targetLabel = groupLabels[index];
    };
    const submitTask = async () => {
      if (!form.value.title || !form.value.type || !form.value.deadline) {
        return common_vendor.index.showToast({ title: "请完善任务信息", icon: "none" });
      }
      common_vendor.index.showLoading({ title: "发布中..." });
      try {
        const payload = {
          title: form.value.title,
          type: form.value.type,
          min_distance: form.value.type === "run" ? Number(form.value.distance) : 0,
          min_duration: 0,
          min_count: 0,
          deadline: new Date(form.value.deadline).toISOString(),
          description: form.value.description,
          target_group: form.value.target
        };
        await utils_request.createTeacherTask(payload);
        common_vendor.index.hideLoading();
        common_vendor.index.showToast({ title: "任务发布成功", icon: "success" });
        setTimeout(() => {
          common_vendor.index.navigateBack();
        }, 1500);
      } catch (e) {
        common_vendor.index.hideLoading();
        common_vendor.index.__f__("error", "at pages/teacher/tasks/create.vue:121", e);
      }
    };
    return (_ctx, _cache) => {
      return {
        a: form.value.title,
        b: common_vendor.o(($event) => form.value.title = $event.detail.value),
        c: common_vendor.t(form.value.typeLabel || "请选择任务类型"),
        d: taskTypeLabels,
        e: common_vendor.o(onTypeChange),
        f: form.value.distance,
        g: common_vendor.o(($event) => form.value.distance = $event.detail.value),
        h: common_vendor.t(form.value.deadline || "请选择截止日期"),
        i: common_vendor.o(onDateChange),
        j: common_vendor.t(form.value.targetLabel || "全员"),
        k: groupLabels,
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
