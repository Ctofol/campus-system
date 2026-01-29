"use strict";
const common_vendor = require("../../common/vendor.js");
const utils_request = require("../../utils/request.js");
if (!Math) {
  (AiChatRobot + CustomTabBar)();
}
const AiChatRobot = () => "../../components/ai-chat-robot/ai-chat-robot.js";
const CustomTabBar = () => "../../components/CustomTabBar/CustomTabBar.js";
const _sfc_main = {
  __name: "run",
  setup(__props) {
    common_vendor.onUnmounted(() => {
      if (timer)
        clearInterval(timer);
      stopStepCount();
    });
    const showAiRobot = common_vendor.ref(false);
    const currentRunData = common_vendor.computed(() => ({
      distance: distance.value,
      pace: currentPace.value || (distance.value > 0 ? duration.value / 60 / (distance.value / 1e3) : 0),
      heartRate: heartRate.value,
      stepCount: stepCount.value
    }));
    const openAiRobot = () => {
      showAiRobot.value = true;
    };
    const handleShareToTeacher = (card) => {
      var _a;
      const report = {
        studentName: ((_a = common_vendor.index.getStorageSync("userInfo")) == null ? void 0 : _a.name) || "学员",
        time: (/* @__PURE__ */ new Date()).toLocaleString(),
        card
      };
      let sharedReports = common_vendor.index.getStorageSync("mockSharedReports") || [];
      sharedReports.unshift(report);
      common_vendor.index.setStorageSync("mockSharedReports", sharedReports);
    };
    const todayRunCount = common_vendor.ref(0);
    const todayRunDistance = common_vendor.ref(0);
    const teacherRunTask = common_vendor.ref("");
    const dailyTarget = common_vendor.ref(5);
    const normalProgress = common_vendor.ref(0);
    const policeProgress = common_vendor.ref(0);
    const historyList = common_vendor.ref([]);
    const achievements = common_vendor.ref([
      { name: "初次开跑", icon: "🏅" },
      { name: "五公里达人", icon: "🏃‍♂️" },
      { name: "全勤周", icon: "🔥" },
      { name: "早起鸟", icon: "🐦" }
    ]);
    const showRoutes = common_vendor.ref(false);
    const recommendRoutes = common_vendor.ref([
      { name: "环校外圈跑", distance: 5.2, difficulty: "中等" },
      { name: "湖畔林荫道", distance: 3, difficulty: "简单" },
      { name: "体育场冲刺", distance: 1.5, difficulty: "困难" }
    ]);
    const toggleRoutes = () => showRoutes.value = !showRoutes.value;
    const useRoute = (route) => {
      common_vendor.index.showToast({ title: `已加载路线：${route.name}`, icon: "none" });
      dailyTarget.value = route.distance;
    };
    const checkpointName = common_vendor.ref("");
    const lat = common_vendor.ref(39.909);
    const lng = common_vendor.ref(116.397);
    const markers = common_vendor.ref([]);
    const polyline = common_vendor.ref([{ points: [], color: "#007AFF", width: 4 }]);
    const checkpoint = common_vendor.ref({});
    const trajectoryPoints = common_vendor.ref([]);
    const checkinRecords = common_vendor.ref([]);
    const getDistance = (lat1, lng1, lat2, lng2) => {
      const R = 6371e3;
      const dLat = (lat2 - lat1) * Math.PI / 180;
      const dLng = (lng2 - lng1) * Math.PI / 180;
      const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      return R * c;
    };
    const startRealLocationTracking = () => {
      common_vendor.index.startLocationUpdate({
        success: () => {
          common_vendor.index.onLocationChange((res) => {
            const newLat = res.latitude;
            const newLng = res.longitude;
            lat.value = newLat;
            lng.value = newLng;
            if (res.speed && res.speed >= 0) {
              currentSpeed.value = res.speed;
            }
            markers.value[0] = {
              id: 0,
              latitude: newLat,
              longitude: newLng,
              title: "我的位置",
              iconPath: "/static/location.png",
              width: 30,
              height: 30
            };
            if (isRunning.value) {
              if (trajectoryPoints.value.length > 0) {
                const lastPoint = trajectoryPoints.value[trajectoryPoints.value.length - 1];
                const d = getDistance(lastPoint.latitude, lastPoint.longitude, newLat, newLng);
                if (d > 2 && d < 100) {
                  distance.value += d;
                }
              }
              const point = { latitude: newLat, longitude: newLng, timestamp: Date.now(), speed: currentSpeed.value };
              trajectoryPoints.value.push(point);
              polyline.value[0].points.push({ latitude: newLat, longitude: newLng });
              if (currentMode.value === "campus" && checkpoint.value.lat) {
                distanceToCheckpoint.value = Math.floor(getDistance(newLat, newLng, checkpoint.value.lat, checkpoint.value.lng));
                if (distanceToCheckpoint.value <= (checkpoint.value.radius || 50)) {
                  isReach.value = true;
                  if (!common_vendor.index.getStorageSync("checkpointReached")) {
                    if (checkpoint.value.id) {
                      utils_request.checkIn({ lat: newLat, lng: newLng, checkpoint_id: checkpoint.value.id }).then((res2) => {
                        if (res2.success) {
                          common_vendor.index.showToast({ title: "打卡成功！", icon: "success" });
                          checkinRecords.value.push({ checkpoint_id: checkpoint.value.id, time: (/* @__PURE__ */ new Date()).toISOString(), lat: newLat, lng: newLng });
                        }
                      }).catch(() => {
                      });
                    } else {
                      common_vendor.index.showToast({ title: "已到达打卡点范围！", icon: "success" });
                    }
                    common_vendor.index.setStorageSync("checkpointReached", "1");
                  }
                } else {
                  isReach.value = false;
                }
              }
              if (currentMode.value === "normal") {
                normalProgress.value = Math.min(100, distance.value / 1e3 / dailyTarget.value * 100);
              } else if (currentMode.value === "police") {
                policeProgress.value = Math.min(100, distance.value / policeTargetDistance.value * 100);
              }
            }
          });
        },
        fail: () => {
          common_vendor.index.showToast({ title: "无法获取实时位置，请检查权限", icon: "none" });
        }
      });
    };
    const stopRealLocationTracking = () => {
      common_vendor.index.stopLocationUpdate();
      common_vendor.index.offLocationChange();
    };
    const currentMode = common_vendor.ref("normal");
    const isRunning = common_vendor.ref(false);
    const duration = common_vendor.ref(0);
    const distance = common_vendor.ref(0);
    const distanceToCheckpoint = common_vendor.ref(0);
    const isReach = common_vendor.ref(false);
    const stepCount = common_vendor.ref(0);
    const heartRate = common_vendor.ref(80);
    const currentSpeed = common_vendor.ref(0);
    common_vendor.ref(0);
    let timer = null;
    let accelerometerCallback = null;
    const policeTargetDistance = common_vendor.ref(2e3);
    const policeTargetPace = common_vendor.ref(6.5);
    const currentPace = common_vendor.computed(() => {
      const km = distance.value / 1e3;
      const min = duration.value / 60;
      return km === 0 ? 0 : min / km;
    });
    const currentSpeedKmh = common_vendor.computed(() => (currentSpeed.value * 3.6).toFixed(1));
    const avgSpeedKmh = common_vendor.computed(() => {
      if (duration.value === 0)
        return 0;
      return (distance.value / 1e3 / (duration.value / 3600)).toFixed(1);
    });
    common_vendor.onLoad((options) => {
      if (options.mode) {
        currentMode.value = options.mode;
      }
      if (options.target) {
        policeTargetDistance.value = parseInt(options.target);
      }
      if (options.course) {
        common_vendor.index.showToast({ title: `开始课程：${options.course}`, icon: "none" });
      }
    });
    common_vendor.onShow(() => {
      const role = common_vendor.index.getStorageSync("userRole") || common_vendor.index.getStorageSync("role");
      if (role === "teacher") {
        common_vendor.index.showToast({ title: "该功能仅对学生开放", icon: "none" });
        setTimeout(() => {
          common_vendor.index.redirectTo({ url: "/pages/teacher/home/home" });
        }, 800);
        return;
      }
      const targetMode = common_vendor.index.getStorageSync("runMode");
      if (targetMode) {
        switchMode(targetMode);
        common_vendor.index.removeStorageSync("runMode");
      }
      getLocation();
      checkpoint.value = common_vendor.index.getStorageSync("checkpoint") || {};
      if (checkpoint.value.name) {
        addCheckpointMarker(checkpoint.value.lat, checkpoint.value.lng, checkpoint.value.name);
      }
      const records = common_vendor.index.getStorageSync("runRecordsList") || [];
      const now = /* @__PURE__ */ new Date();
      const dayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
      const dayEnd = dayStart + 24 * 60 * 60 * 1e3;
      let c = 0;
      let d = 0;
      records.forEach((r) => {
        const t = new Date(r.createTime).getTime();
        const isRunType = r.type ? r.type === "run" : true;
        if (isRunType && t >= dayStart && t < dayEnd) {
          c += 1;
          d += Number(r.distance) || 0;
        }
      });
      todayRunCount.value = c;
      todayRunDistance.value = Number(d.toFixed(2));
      historyList.value = buildHistory(records);
      const taskStr = common_vendor.index.getStorageSync("teacherTask");
      if (taskStr) {
        try {
          const obj = typeof taskStr === "string" ? JSON.parse(taskStr) : taskStr;
          teacherRunTask.value = obj.title || "";
        } catch (e) {
          teacherRunTask.value = "";
        }
      }
    });
    const getLocation = () => {
      common_vendor.index.authorize({
        scope: "scope.userLocation",
        success: () => {
          doGetLocation();
        },
        fail: () => {
          common_vendor.index.showModal({
            title: "权限申请",
            content: "需要定位权限才能使用打卡/跑步功能，请前往设置开启",
            confirmText: "去设置",
            success: (res) => {
              if (res.confirm)
                common_vendor.index.openSetting();
            }
          });
        }
      });
    };
    const doGetLocation = () => {
      const lastLoc = common_vendor.index.getStorageSync("lastLocation");
      if (lastLoc) {
        lat.value = lastLoc.lat;
        lng.value = lastLoc.lng;
        markers.value = [{
          id: 0,
          latitude: lastLoc.lat,
          longitude: lastLoc.lng,
          title: "我的位置",
          iconPath: "/static/location.png",
          width: 30,
          height: 30
        }];
      }
      common_vendor.index.getLocation({
        type: "gcj02",
        accuracy: "high",
        success: (res) => {
          lat.value = res.latitude;
          lng.value = res.longitude;
          markers.value = [{
            id: 0,
            latitude: res.latitude,
            longitude: res.longitude,
            title: "我的位置",
            iconPath: "/static/location.png",
            width: 30,
            height: 30
          }];
          const campusLatMin = 39.9;
          const campusLatMax = 39.92;
          const campusLngMin = 116.39;
          const campusLngMax = 116.41;
          const isInCampus = res.latitude >= campusLatMin && res.latitude <= campusLatMax && res.longitude >= campusLngMin && res.longitude <= campusLngMax;
          if (!isInCampus && currentMode.value === "campus") {
            common_vendor.index.showToast({ title: "仅校园内可进行打卡", icon: "none" });
          }
        },
        fail: (err) => {
          common_vendor.index.__f__("error", "at pages/run/run.vue:570", "Location failed:", err);
          let msg = "定位失败，已使用模拟位置";
          common_vendor.index.showToast({ title: msg, icon: "none", duration: 3e3 });
          lat.value = 39.908823;
          lng.value = 116.39747;
          markers.value = [{
            id: 0,
            latitude: 39.908823,
            longitude: 116.39747,
            title: "我的位置 (模拟)",
            iconPath: "/static/location.png",
            width: 30,
            height: 30
          }];
        }
      });
    };
    const searchCheckpoint = () => {
      if (!checkpointName.value) {
        common_vendor.index.showToast({ title: "请输入打卡点名称", icon: "none" });
        return;
      }
      const newCheckpoint = {
        name: checkpointName.value,
        lat: lat.value + 1e-3,
        lng: lng.value + 1e-3
      };
      common_vendor.index.setStorageSync("checkpoint", newCheckpoint);
      checkpoint.value = newCheckpoint;
      addCheckpointMarker(newCheckpoint.lat, newCheckpoint.lng, newCheckpoint.name);
      polyline.value = [{
        points: [
          { latitude: lat.value, longitude: lng.value },
          { latitude: newCheckpoint.lat, longitude: newCheckpoint.lng }
        ],
        color: "#FF0000",
        width: 5
      }];
      common_vendor.index.showToast({ title: `找到${newCheckpoint.name}`, icon: "success" });
    };
    const addCheckpointMarker = (lat2, lng2, name) => {
      markers.value.push({
        id: 1,
        latitude: lat2,
        longitude: lng2,
        title: name,
        iconPath: "/static/checkpoint.png",
        width: 40,
        height: 40
      });
    };
    const switchMode = (mode) => {
      isRunning.value = false;
      clearInterval(timer);
      stopStepCount();
      duration.value = 0;
      distance.value = 0;
      stepCount.value = 0;
      heartRate.value = 80;
      currentMode.value = mode;
    };
    const startStepCount = () => {
      accelerometerCallback = (res) => {
        const acceleration = Math.sqrt(res.x * res.x + res.y * res.y + res.z * res.z);
        if (acceleration > 15)
          stepCount.value += 1;
      };
      common_vendor.index.onAccelerometerChange(accelerometerCallback);
    };
    const stopStepCount = () => {
      if (accelerometerCallback) {
        common_vendor.index.offAccelerometerChange(accelerometerCallback);
        accelerometerCallback = null;
      }
    };
    const updateHeartRate = () => {
      heartRate.value = 80 + Math.floor(duration.value / 10);
      if (heartRate.value > 180) {
        common_vendor.index.showModal({
          title: "健康预警",
          content: `当前心率过高（${heartRate.value}次/分），建议降速休息`,
          showCancel: false
        });
      }
    };
    const startNormalRun = () => {
      isRunning.value = true;
      duration.value = 0;
      distance.value = 0;
      stepCount.value = 0;
      heartRate.value = 80;
      common_vendor.index.removeStorageSync("checkpointReached");
      startRealLocationTracking();
      startStepCount();
      timer = setInterval(() => {
        duration.value += 1;
        updateHeartRate();
      }, 1e3);
    };
    const startPoliceRun = () => {
      isRunning.value = true;
      duration.value = 0;
      distance.value = 0;
      stepCount.value = 0;
      heartRate.value = 80;
      common_vendor.index.removeStorageSync("policeFinishTip");
      startRealLocationTracking();
      startStepCount();
      timer = setInterval(() => {
        duration.value += 1;
        updateHeartRate();
        if (distance.value >= policeTargetDistance.value && !common_vendor.index.getStorageSync("policeFinishTip")) {
          common_vendor.index.showToast({ title: "已完成2000米目标！", icon: "success" });
          common_vendor.index.setStorageSync("policeFinishTip", "1");
        }
      }, 1e3);
    };
    const startCampusRun = () => {
      isRunning.value = true;
      duration.value = 0;
      isReach.value = false;
      stepCount.value = 0;
      heartRate.value = 80;
      common_vendor.index.removeStorageSync("checkpointReached");
      startRealLocationTracking();
      startStepCount();
      timer = setInterval(() => {
        duration.value += 1;
        updateHeartRate();
      }, 1e3);
    };
    const stopRun = async () => {
      if (!isRunning.value)
        return;
      isRunning.value = false;
      clearInterval(timer);
      stopStepCount();
      stopRealLocationTracking();
      const token = common_vendor.index.getStorageSync("token");
      if (!token) {
        common_vendor.index.showToast({ title: "请先登录", icon: "none" });
        setTimeout(() => {
          common_vendor.index.reLaunch({ url: "/pages/login/login" });
        }, 800);
        return;
      }
      const runData = {
        type: currentMode.value === "police" ? "test" : "run",
        source: "free",
        started_at: new Date(Date.now() - duration.value * 1e3).toISOString(),
        ended_at: (/* @__PURE__ */ new Date()).toISOString(),
        metrics: {
          distance: distance.value / 1e3,
          // Convert meters to km
          duration: duration.value,
          pace: currentPace.value.toFixed(1),
          count: currentMode.value === "police" ? 1 : null,
          qualified: currentMode.value === "police" ? currentPace.value <= policeTargetPace.value : false,
          trajectory: JSON.stringify(trajectoryPoints.value),
          checkpoints: JSON.stringify(checkinRecords.value)
        },
        evidence: []
      };
      try {
        common_vendor.index.showLoading({ title: "提交中..." });
        const res = await utils_request.submitActivity(runData);
        common_vendor.index.hideLoading();
        common_vendor.index.navigateTo({
          url: `/pages/result/result?data=${encodeURIComponent(JSON.stringify(runData))}`
        });
      } catch (error) {
        common_vendor.index.hideLoading();
        common_vendor.index.__f__("error", "at pages/run/run.vue:777", "Submit failed:", error);
        common_vendor.index.showToast({
          title: error && error.detail ? `提交失败：${error.detail}` : "提交失败，请重试",
          icon: "none",
          duration: 2e3
        });
      }
    };
    const buildHistory = (records) => {
      const days = 7;
      const now = /* @__PURE__ */ new Date();
      const arr = [];
      for (let i = 0; i < days; i++) {
        const day = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i);
        const start = new Date(day.getFullYear(), day.getMonth(), day.getDate()).getTime();
        const end = start + 24 * 60 * 60 * 1e3;
        const runRecs = records.filter((r) => {
          const t = new Date(r.createTime).getTime();
          const isRunType = r.type ? r.type === "run" : true;
          return isRunType && t >= start && t < end;
        });
        const count = runRecs.length;
        const distanceSum = runRecs.reduce((s, x) => s + Number(x.distance || 0), 0);
        arr.push({ date: `${day.getMonth() + 1}/${day.getDate()}`, count, distance: Number(distanceSum.toFixed(2)) });
      }
      return arr.reverse();
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.o(handleShareToTeacher),
        b: common_vendor.o(($event) => showAiRobot.value = $event),
        c: common_vendor.p({
          ["run-data"]: currentRunData.value,
          visible: showAiRobot.value
        }),
        d: isRunning.value || distance.value > 0
      }, isRunning.value || distance.value > 0 ? {
        e: common_vendor.o(openAiRobot)
      } : {}, {
        f: common_vendor.f(achievements.value, (badge, idx, i0) => {
          return {
            a: common_vendor.t(badge.icon),
            b: common_vendor.t(badge.name),
            c: idx
          };
        }),
        g: currentMode.value === "campus"
      }, currentMode.value === "campus" ? {
        h: checkpointName.value,
        i: common_vendor.o(($event) => checkpointName.value = $event.detail.value),
        j: common_vendor.o(searchCheckpoint)
      } : {}, {
        k: common_vendor.t(todayRunCount.value),
        l: common_vendor.t(todayRunDistance.value),
        m: teacherRunTask.value
      }, teacherRunTask.value ? {
        n: common_vendor.t(teacherRunTask.value)
      } : {}, {
        o: lat.value,
        p: lng.value,
        q: markers.value,
        r: polyline.value,
        s: currentMode.value === "normal"
      }, currentMode.value === "normal" ? common_vendor.e({
        t: common_vendor.t(showRoutes.value ? "收起" : "展开"),
        v: common_vendor.o(toggleRoutes),
        w: showRoutes.value
      }, showRoutes.value ? {
        x: common_vendor.f(recommendRoutes.value, (route, idx, i0) => {
          return {
            a: common_vendor.t(route.name),
            b: common_vendor.t(route.distance),
            c: common_vendor.t(route.difficulty),
            d: idx,
            e: common_vendor.o(($event) => useRoute(route), idx)
          };
        })
      } : {}) : {}, {
        y: currentMode.value === "normal" ? 1 : "",
        z: common_vendor.o(($event) => switchMode("normal")),
        A: currentMode.value === "police" ? 1 : "",
        B: common_vendor.o(($event) => switchMode("police")),
        C: currentMode.value === "campus" ? 1 : "",
        D: common_vendor.o(($event) => switchMode("campus")),
        E: currentMode.value === "police"
      }, currentMode.value === "police" ? {
        F: common_vendor.t(policeTargetDistance.value / 1e3),
        G: common_vendor.t(policeTargetPace.value)
      } : {}, {
        H: currentMode.value === "normal"
      }, currentMode.value === "normal" ? common_vendor.e({
        I: !isRunning.value
      }, !isRunning.value ? {
        J: common_vendor.o(startNormalRun)
      } : {
        K: common_vendor.t(duration.value),
        L: common_vendor.t((distance.value / 1e3).toFixed(2)),
        M: common_vendor.t(currentSpeedKmh.value),
        N: common_vendor.t(stepCount.value),
        O: common_vendor.t(heartRate.value),
        P: common_vendor.t(avgSpeedKmh.value),
        Q: normalProgress.value + "%",
        R: common_vendor.t(dailyTarget.value),
        S: common_vendor.t((distance.value / 1e3).toFixed(2)),
        T: common_vendor.o(stopRun)
      }) : {}, {
        U: currentMode.value === "police"
      }, currentMode.value === "police" ? common_vendor.e({
        V: !isRunning.value
      }, !isRunning.value ? {
        W: common_vendor.o(startPoliceRun)
      } : common_vendor.e({
        X: common_vendor.t(duration.value),
        Y: common_vendor.t((distance.value / 1e3).toFixed(2)),
        Z: common_vendor.t(((policeTargetDistance.value - distance.value) / 1e3).toFixed(2)),
        aa: common_vendor.t(currentPace.value.toFixed(1)),
        ab: common_vendor.t(heartRate.value),
        ac: common_vendor.t(stepCount.value),
        ad: common_vendor.t(currentPace.value <= policeTargetPace.value ? "✅ 配速达标" : "❌ 配速未达标"),
        ae: currentPace.value <= policeTargetPace.value ? "green" : "red",
        af: distance.value >= policeTargetDistance.value
      }, distance.value >= policeTargetDistance.value ? {} : {}, {
        ag: policeProgress.value + "%",
        ah: common_vendor.t((distance.value / 1e3).toFixed(2)),
        ai: common_vendor.o(stopRun)
      })) : {}, {
        aj: currentMode.value === "campus"
      }, currentMode.value === "campus" ? common_vendor.e({
        ak: !checkpoint.value.name
      }, !checkpoint.value.name ? {} : common_vendor.e({
        al: !isRunning.value
      }, !isRunning.value ? {
        am: common_vendor.t(checkpoint.value.name),
        an: common_vendor.o(startCampusRun)
      } : {
        ao: common_vendor.t(duration.value),
        ap: common_vendor.t(distanceToCheckpoint.value),
        aq: common_vendor.t(stepCount.value),
        ar: common_vendor.t(heartRate.value),
        as: common_vendor.t(isReach.value ? "✅ 已到达打卡点" : "❌ 未到达打卡点"),
        at: isReach.value ? "green" : "red",
        av: common_vendor.o(stopRun)
      })) : {}, {
        aw: common_vendor.p({
          current: "/pages/run/run"
        })
      });
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-8ae35d30"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/run/run.js.map
