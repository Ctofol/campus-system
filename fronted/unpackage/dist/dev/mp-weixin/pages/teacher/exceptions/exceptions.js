"use strict";
const common_vendor = require("../../../common/vendor.js");
const _sfc_main = {
  __name: "exceptions",
  setup(__props) {
    const currentFilter = common_vendor.ref("all");
    const alerts = common_vendor.ref([
      {
        id: 1,
        type: "heart_rate",
        typeText: "心率过高",
        typeClass: "tag-red",
        studentName: "张三",
        studentId: "2023001",
        time: "10:30",
        value: "195 bpm",
        standard: "60-180 bpm",
        description: "跑步过程中持续3分钟心率超过安全阈值，建议暂停训练并检查身体状况。",
        level: "urgent"
      },
      {
        id: 2,
        type: "pace",
        typeText: "配速异常",
        typeClass: "tag-orange",
        studentName: "李四",
        studentId: "2023002",
        time: "10:45",
        value: `2'30"/km`,
        standard: `4'00"-8'00"/km`,
        description: "短时间内配速极快，疑似骑车或数据漂移。",
        level: "normal"
      },
      {
        id: 3,
        type: "location",
        typeText: "轨迹异常",
        typeClass: "tag-blue",
        studentName: "王五",
        studentId: "2023003",
        time: "09:15",
        value: "直线穿越",
        standard: "连续轨迹",
        description: "轨迹点之间距离过大，且无中间路径，疑似GPS信号丢失或作弊。",
        level: "normal"
      }
    ]);
    const pendingCount = common_vendor.computed(() => alerts.value.length);
    const todayCount = common_vendor.ref(5);
    const filteredAlerts = common_vendor.computed(() => {
      if (currentFilter.value === "all")
        return alerts.value;
      return alerts.value.filter((a) => a.level === currentFilter.value);
    });
    const ignoreAlert = (id) => {
      common_vendor.index.showModal({
        title: "确认忽略",
        content: "忽略后该异常将不再提醒，确认操作？",
        success: (res) => {
          if (res.confirm) {
            alerts.value = alerts.value.filter((a) => a.id !== id);
            common_vendor.index.showToast({ title: "已忽略", icon: "none" });
          }
        }
      });
    };
    const notifyStudent = (alert) => {
      common_vendor.index.showToast({
        title: `已发送通知给 ${alert.studentName}`,
        icon: "success"
      });
    };
    const handleAlert = (alert) => {
      common_vendor.index.showActionSheet({
        itemList: ["标记为无效成绩", "标记为设备故障", "要求重测"],
        success: (res) => {
          const actions = ["无效成绩", "设备故障", "重测"];
          common_vendor.index.showToast({
            title: `已标记为：${actions[res.tapIndex]}`,
            icon: "success"
          });
          alerts.value = alerts.value.filter((a) => a.id !== alert.id);
        }
      });
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.t(pendingCount.value),
        b: common_vendor.t(todayCount.value),
        c: currentFilter.value === "all" ? 1 : "",
        d: common_vendor.o(($event) => currentFilter.value = "all"),
        e: currentFilter.value === "urgent" ? 1 : "",
        f: common_vendor.o(($event) => currentFilter.value = "urgent"),
        g: currentFilter.value === "normal" ? 1 : "",
        h: common_vendor.o(($event) => currentFilter.value = "normal"),
        i: common_vendor.f(filteredAlerts.value, (alert, index, i0) => {
          return {
            a: common_vendor.t(alert.typeText),
            b: common_vendor.n(alert.typeClass),
            c: common_vendor.t(alert.studentName),
            d: common_vendor.t(alert.studentId),
            e: common_vendor.t(alert.time),
            f: common_vendor.t(alert.value),
            g: common_vendor.t(alert.standard),
            h: common_vendor.t(alert.description),
            i: common_vendor.o(($event) => ignoreAlert(alert.id), alert.id),
            j: common_vendor.o(($event) => notifyStudent(alert), alert.id),
            k: common_vendor.o(($event) => handleAlert(alert), alert.id),
            l: alert.id
          };
        }),
        j: filteredAlerts.value.length === 0
      }, filteredAlerts.value.length === 0 ? {} : {});
    };
  }
};
wx.createPage(_sfc_main);
//# sourceMappingURL=../../../../.sourcemap/mp-weixin/pages/teacher/exceptions/exceptions.js.map
