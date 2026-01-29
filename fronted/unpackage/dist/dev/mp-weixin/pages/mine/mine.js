"use strict";
const common_vendor = require("../../common/vendor.js");
const common_assets = require("../../common/assets.js");
const utils_request = require("../../utils/request.js");
if (!Math) {
  CustomTabBar();
}
const CustomTabBar = () => "../../components/CustomTabBar/CustomTabBar.js";
const _sfc_main = {
  __name: "mine",
  setup(__props) {
    const userName = common_vendor.ref("运动先锋");
    const userType = common_vendor.ref("2024级侦查系");
    const deviceId = common_vendor.ref("");
    const totalRunCount = common_vendor.ref(0);
    const totalRunDistance = common_vendor.ref(0);
    const policeSuccessCount = common_vendor.ref(0);
    const weekRunCount = common_vendor.ref(0);
    const weekRunDistance = common_vendor.ref(0);
    const weekPoliceSuccess = common_vendor.ref(0);
    const weekDateRange = common_vendor.ref("");
    const progressPercent = common_vendor.ref(0);
    const runRecords = common_vendor.ref([]);
    const showRecords = common_vendor.ref([]);
    common_vendor.onLoad(() => {
      common_vendor.index.startPullDownRefresh();
    });
    common_vendor.onShow(() => {
      loadUserStats();
      loadWeekData();
      loadRunRecords();
      loadDeviceInfo();
    });
    common_vendor.onPullDownRefresh(() => {
      loadUserStats();
      loadWeekData();
      loadRunRecords();
      setTimeout(() => {
        common_vendor.index.stopPullDownRefresh();
        common_vendor.index.showToast({ title: "数据已刷新", icon: "success" });
      }, 500);
    });
    const loadUserStats = () => {
      totalRunCount.value = Number(common_vendor.index.getStorageSync("totalRunCount")) || 0;
      totalRunDistance.value = (Number(common_vendor.index.getStorageSync("totalRunDistance")) || 0).toFixed(1);
      policeSuccessCount.value = Number(common_vendor.index.getStorageSync("policeSuccessCount")) || 0;
    };
    const loadWeekData = () => {
      const now = /* @__PURE__ */ new Date();
      const weekStart = new Date(now.setDate(now.getDate() - now.getDay() + 1));
      const weekEnd = new Date(now.setDate(now.getDate() + 6));
      weekDateRange.value = `${weekStart.getMonth() + 1}月${weekStart.getDate()}日 - ${weekEnd.getMonth() + 1}月${weekEnd.getDate()}日`;
      const allRecords = common_vendor.index.getStorageSync("runRecordsList") || [];
      let weekCount = 0;
      let weekDistance = 0;
      let weekPolice = 0;
      allRecords.forEach((record) => {
        const recordTime = new Date(record.createTime);
        if (recordTime >= weekStart && recordTime <= weekEnd) {
          const isRunType = record.type ? record.type === "run" : true;
          if (isRunType) {
            weekCount++;
            weekDistance += record.distance;
            if (record.mode === "police" && record.isPaceQualified) {
              weekPolice++;
            }
          }
        }
      });
      weekRunCount.value = weekCount;
      weekRunDistance.value = weekDistance.toFixed(1);
      weekPoliceSuccess.value = weekPolice;
      progressPercent.value = Math.min(weekCount / 3 * 100, 100);
    };
    const loadRunRecords = async () => {
      try {
        const res = await utils_request.getActivityHistory({ page: 1, size: 5 });
        if (res && res.items) {
          runRecords.value = res.items.map((item) => {
            var _a, _b, _c, _d, _e;
            const isRun = item.type === "run";
            return {
              id: item.id,
              type: item.type,
              modeText: isRun ? "跑步" : "体测",
              modeBg: isRun ? "#4CAF50" : "#2196F3",
              createTime: new Date(item.started_at).toLocaleString(),
              distance: ((_b = (_a = item.metrics) == null ? void 0 : _a.distance) == null ? void 0 : _b.toFixed(2)) || "0.00",
              duration: formatDuration(((_c = item.metrics) == null ? void 0 : _c.duration) || 0),
              pace: ((_d = item.metrics) == null ? void 0 : _d.pace) || "--",
              testName: isRun ? "" : "专项测试",
              testCount: ((_e = item.metrics) == null ? void 0 : _e.count) || 0,
              result: item.status === "approved" || item.status === "completed" ? "已完成" : item.status,
              statusText: item.status === "approved" || item.status === "completed" ? "已完成" : "审核中",
              statusColor: item.status === "approved" || item.status === "completed" ? "#4CAF50" : "#FF9800"
            };
          });
          showRecords.value = runRecords.value;
        }
      } catch (error) {
        common_vendor.index.__f__("error", "at pages/mine/mine.vue:243", "Failed to load history:", error);
        common_vendor.index.showToast({
          title: "加载历史记录失败",
          icon: "none"
        });
      }
    };
    const formatDuration = (seconds) => {
      const m = Math.floor(seconds / 60);
      const s = seconds % 60;
      return `${m}:${s < 10 ? "0" + s : s}`;
    };
    const loadDeviceInfo = () => {
      deviceId.value = common_vendor.index.getStorageSync("bindDeviceId") || "";
    };
    const gotoUserProfile = () => {
      common_vendor.index.showToast({ title: "暂未开放，敬请期待", icon: "none" });
    };
    const viewAllRecords = () => {
      if (runRecords.value.length === 0) {
        common_vendor.index.showToast({ title: "暂无运动记录", icon: "none" });
        return;
      }
      common_vendor.index.showToast({ title: "已展示全部记录", icon: "success" });
    };
    const gotoRecordDetail = (item) => {
      common_vendor.index.showModal({
        title: "记录详情",
        content: item.type === "run" ? `模式：${item.modeText}
时间：${item.createTime}
距离：${item.distance}km
时长：${item.duration}
状态：${item.statusText}` : `类型：体能测试
项目：${item.testName}
次数：${item.testCount}
判定：${item.result}
时长：${item.duration}`,
        showCancel: false
      });
    };
    const gotoDeviceBind = () => {
      if (deviceId.value) {
        common_vendor.index.showModal({
          title: "设备绑定",
          content: "是否解除当前设备绑定？",
          success: (res) => {
            if (res.confirm) {
              common_vendor.index.removeStorageSync("bindDeviceId");
              deviceId.value = "";
              common_vendor.index.showToast({ title: "已解除绑定", icon: "success" });
            }
          }
        });
      } else {
        common_vendor.index.getSystemInfo({
          success: (res) => {
            const uniqueId = res.deviceId || `${res.platform}_${res.model}`;
            common_vendor.index.setStorageSync("bindDeviceId", uniqueId);
            deviceId.value = uniqueId;
            common_vendor.index.showToast({ title: "设备绑定成功", icon: "success" });
          },
          fail: () => {
            common_vendor.index.showToast({ title: "获取设备信息失败", icon: "none" });
          }
        });
      }
    };
    const clearCache = () => {
      common_vendor.index.showModal({
        title: "清除缓存",
        content: "确定要清除本地缓存吗？运动记录不会被删除",
        success: (res) => {
          if (res.confirm) {
            common_vendor.index.removeStorageSync("checkpoint");
            common_vendor.index.removeStorageSync("policeFinishTip");
            common_vendor.index.showToast({ title: "缓存已清除", icon: "success" });
          }
        }
      });
    };
    const gotoAbout = () => {
      common_vendor.index.showModal({
        title: "关于我们",
        content: "大学生运动健康管理系统 v1.0.0\n专为公安院校定制的跑步打卡工具",
        showCancel: false
      });
    };
    const logout = () => {
      common_vendor.index.showModal({
        title: "退出登录",
        content: "确定要退出当前账号吗？",
        success: (res) => {
          if (res.confirm) {
            common_vendor.index.clearStorageSync();
            common_vendor.index.reLaunch({ url: "/pages/login/login" });
          }
        }
      });
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_assets._imports_0,
        b: common_vendor.o(gotoUserProfile),
        c: common_vendor.t(userName.value),
        d: common_vendor.t(userType.value),
        e: common_vendor.t(totalRunCount.value),
        f: common_vendor.t(totalRunDistance.value),
        g: common_vendor.t(policeSuccessCount.value),
        h: common_vendor.t(weekDateRange.value),
        i: common_vendor.t(weekRunCount.value),
        j: common_vendor.t(weekRunDistance.value),
        k: common_vendor.t(weekPoliceSuccess.value),
        l: common_vendor.t(weekRunCount.value),
        m: progressPercent.value + "%",
        n: common_vendor.o(viewAllRecords),
        o: runRecords.value.length > 0
      }, runRecords.value.length > 0 ? {
        p: common_vendor.f(showRecords.value, (item, index, i0) => {
          return common_vendor.e({
            a: common_vendor.t(item.modeText),
            b: item.modeBg,
            c: common_vendor.t(item.createTime),
            d: item.type === "run"
          }, item.type === "run" ? common_vendor.e({
            e: common_vendor.t(item.distance),
            f: common_vendor.t(item.duration),
            g: item.pace
          }, item.pace ? {
            h: common_vendor.t(Number(item.pace).toFixed(1))
          } : {}) : {
            i: common_vendor.t(item.testName),
            j: common_vendor.t(item.testCount),
            k: common_vendor.t(item.result)
          }, {
            l: common_vendor.t(item.statusText),
            m: item.statusColor,
            n: index,
            o: common_vendor.o(($event) => gotoRecordDetail(item), index)
          });
        })
      } : {}, {
        q: common_vendor.t(deviceId.value || "未绑定"),
        r: common_vendor.o(gotoDeviceBind),
        s: common_vendor.o(clearCache),
        t: common_vendor.o(gotoAbout),
        v: common_vendor.o(logout),
        w: common_vendor.p({
          current: "/pages/mine/mine"
        })
      });
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-7c2ebfa5"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/mine/mine.js.map
