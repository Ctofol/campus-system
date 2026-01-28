"use strict";
const common_vendor = require("../../common/vendor.js");
if (!Math) {
  CustomTabBar();
}
const CustomTabBar = () => "../../components/CustomTabBar/CustomTabBar.js";
const _sfc_main = {
  __name: "home",
  setup(__props) {
    const role = common_vendor.ref("student");
    const userInfo = common_vendor.ref({});
    common_vendor.onShow(() => {
      const userRole = common_vendor.index.getStorageSync("userRole") || common_vendor.index.getStorageSync("role");
      if (userRole)
        role.value = userRole;
      const storedUser = common_vendor.index.getStorageSync("userInfo");
      if (storedUser) {
        try {
          userInfo.value = typeof storedUser === "string" ? JSON.parse(storedUser) : storedUser;
        } catch (e) {
          common_vendor.index.__f__("error", "at pages/home/home.vue:139", "JSON parse error", e);
          userInfo.value = {};
        }
      }
    });
    const showTrainingPlans = common_vendor.ref(true);
    const showRankModal = common_vendor.ref(false);
    const teacherTask = common_vendor.ref({ id: 101, title: `本周五前完成一次3000米拉练，配速要求6'00"`, type: "urgent" });
    const testProjects = common_vendor.ref([
      { name: "引体向上", tag: "警务考核", tagClass: "tag-police", status: "未完成", type: "pull-up" },
      { name: "仰卧起坐", tag: "日常测评", tagClass: "tag-daily", status: "进行中", type: "sit-up" },
      { name: "俯卧撑", tag: "基础训练", tagClass: "tag-base", status: "未开始", type: "push-up" }
    ]);
    const trainingPlans = common_vendor.ref([
      { id: 1, name: "警务体能综合测试", type: "考核", typeClass: "tag-red", duration: 45, difficulty: "高强度", isCompleted: false },
      { id: 2, name: "1000米爆发力训练", type: "专项", typeClass: "tag-blue", duration: 20, difficulty: "中强度", isCompleted: true },
      { id: 3, name: "核心力量强化课程", type: "日常", typeClass: "tag-green", duration: 30, difficulty: "低强度", isCompleted: false }
    ]);
    const myClub = common_vendor.ref({ name: "刑侦先锋跑团", rank: 3, members: 42, totalDistance: 1205.8, activityCount: 5 });
    const activities = common_vendor.ref([
      { name: "五四青年节环校跑", time: "5月4日 07:00", status: "报名中", statusClass: "status-active", joined: 128 },
      { name: "周末夜跑打卡赛", time: "本周六 19:00", status: "进行中", statusClass: "status-ing", joined: 56 },
      { name: "警务技能交流会", time: "下周三 14:00", status: "预告", statusClass: "status-future", joined: 30 }
    ]);
    common_vendor.ref([
      { user: "张伟", time: "10分钟前", action: "完成了", result: "5公里晨跑", likes: 12, avatarColor: "#FF6B6B" },
      { user: "李娜", time: "35分钟前", action: "打卡了", result: "核心力量训练", likes: 8, avatarColor: "#4ECDC4" },
      { user: "王强", time: "1小时前", action: "刷新了", result: "3000米个人记录", likes: 25, avatarColor: "#45B7D1" }
    ]);
    const rankList = common_vendor.ref([
      { name: "特警突击队", members: 56, distance: 2300, heat: 9800 },
      { name: "交警铁骑团", members: 48, distance: 1800, heat: 8500 },
      { name: "刑侦先锋跑团", members: 42, distance: 1205, heat: 7200 },
      { name: "治安巡逻队", members: 35, distance: 980, heat: 6e3 }
    ]);
    const getRandomColor = () => {
      const colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD"];
      return colors[Math.floor(Math.random() * colors.length)];
    };
    const handleTaskClick = () => {
      common_vendor.index.showToast({ title: "任务详情", icon: "none" });
    };
    const gotoAiPolice = () => {
      common_vendor.index.navigateTo({ url: "/pages/ai-police/ai-police" });
    };
    const browseActivities = () => {
      common_vendor.index.navigateTo({ url: "/pages/activity/list" });
    };
    const createClub = () => {
      common_vendor.index.showToast({ title: "创建功能即将上线", icon: "none" });
    };
    const joinClub = () => {
      common_vendor.index.showToast({ title: "加入功能即将上线", icon: "none" });
    };
    const enterClubDetail = () => {
      common_vendor.index.showToast({ title: "跑团详情", icon: "none" });
    };
    const showRank = () => {
      showRankModal.value = true;
    };
    const closeRank = () => {
      showRankModal.value = false;
    };
    const showActivityDetail = (act) => {
      common_vendor.index.navigateTo({
        url: `/pages/activity/detail?name=${act.name}`
      });
    };
    const startTestProject = (item) => {
      common_vendor.index.redirectTo({ url: "/pages/test/test?project=" + item.name + "&type=" + item.type });
    };
    const startTraining = (item) => {
      common_vendor.index.navigateTo({
        url: `/pages/run/run?mode=training&planId=${item.id}&name=${item.name}`
      });
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: teacherTask.value
      }, teacherTask.value ? {
        b: common_vendor.t(teacherTask.value.title),
        c: common_vendor.o(handleTaskClick)
      } : {}, {
        d: common_vendor.o(gotoAiPolice),
        e: common_vendor.o(browseActivities),
        f: common_vendor.o(($event) => common_vendor.index.redirectTo({
          url: "/pages/test/test"
        })),
        g: common_vendor.o(($event) => common_vendor.index.redirectTo({
          url: "/pages/mine/mine"
        })),
        h: common_vendor.f(testProjects.value, (item, index, i0) => {
          return {
            a: common_vendor.t(item.type === "pull-up" ? "💪" : item.type === "sit-up" ? "🧘" : "🏋️"),
            b: common_vendor.t(item.name),
            c: common_vendor.t(item.tag),
            d: common_vendor.n(item.tagClass),
            e: common_vendor.t(item.status),
            f: index,
            g: common_vendor.o(($event) => startTestProject(item), index)
          };
        }),
        i: common_vendor.t(showTrainingPlans.value ? "收起" : "展开"),
        j: common_vendor.o(($event) => showTrainingPlans.value = !showTrainingPlans.value),
        k: showTrainingPlans.value
      }, showTrainingPlans.value ? {
        l: common_vendor.f(trainingPlans.value, (item, index, i0) => {
          return common_vendor.e({
            a: common_vendor.t(item.type),
            b: common_vendor.n(item.typeClass),
            c: common_vendor.t(item.name),
            d: common_vendor.t(item.duration),
            e: common_vendor.t(item.difficulty),
            f: item.isCompleted
          }, item.isCompleted ? {} : {}, {
            g: index,
            h: common_vendor.o(($event) => startTraining(item), index)
          });
        })
      } : {}, {
        m: common_vendor.o(createClub),
        n: common_vendor.o(joinClub),
        o: common_vendor.o(browseActivities),
        p: common_vendor.t(myClub.value.name),
        q: common_vendor.t(myClub.value.rank),
        r: common_vendor.t(myClub.value.members),
        s: common_vendor.t(myClub.value.totalDistance),
        t: common_vendor.t(myClub.value.activityCount),
        v: common_vendor.o(showRank),
        w: common_vendor.o(enterClubDetail),
        x: common_vendor.f(activities.value, (act, idx, i0) => {
          return {
            a: common_vendor.t(act.status),
            b: common_vendor.n(act.statusClass),
            c: common_vendor.t(act.name),
            d: common_vendor.t(act.time),
            e: common_vendor.f(3, (n, k1, i1) => {
              return {
                a: n
              };
            }),
            f: common_vendor.t(act.joined),
            g: idx,
            h: common_vendor.o(($event) => showActivityDetail(act), idx)
          };
        }),
        y: getRandomColor(),
        z: common_vendor.p({
          current: "/pages/home/home"
        }),
        A: showRankModal.value
      }, showRankModal.value ? {
        B: common_vendor.o(closeRank),
        C: common_vendor.f(rankList.value, (item, idx, i0) => {
          return {
            a: common_vendor.t(idx + 1),
            b: common_vendor.n("rank-" + (idx + 1)),
            c: common_vendor.t(item.name),
            d: common_vendor.t(item.members),
            e: common_vendor.t(item.distance),
            f: common_vendor.t(item.heat),
            g: idx
          };
        }),
        D: common_vendor.o(() => {
        }),
        E: common_vendor.o(closeRank)
      } : {});
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-07e72d3c"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/home/home.js.map
