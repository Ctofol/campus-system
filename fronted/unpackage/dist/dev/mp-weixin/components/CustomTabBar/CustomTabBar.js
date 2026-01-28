"use strict";
const common_vendor = require("../../common/vendor.js");
const color = "#666666";
const selectedColor = "#20C997";
const _sfc_main = {
  __name: "CustomTabBar",
  props: {
    current: {
      type: String,
      default: ""
    }
  },
  setup(__props) {
    const props = __props;
    const role = common_vendor.ref("student");
    const studentList = [
      { pagePath: "/pages/home/home", text: "首页", iconPath: "/static/tab/home.png", selectedIconPath: "/static/tab/home-active.png" },
      { pagePath: "/pages/run/run", text: "跑步", iconPath: "/static/tab/run.png", selectedIconPath: "/static/tab/run-active.png" },
      { pagePath: "/pages/test/test", text: "体测", iconPath: "/static/tab/test.png", selectedIconPath: "/static/tab/test-active.png" },
      { pagePath: "/pages/mine/mine", text: "我的", iconPath: "/static/tab/mine.png", selectedIconPath: "/static/tab/mine-active.png" }
    ];
    const teacherList = [
      { pagePath: "/pages/teacher/home/home", text: "主页", iconPath: "/static/tab/home.png", selectedIconPath: "/static/tab/home-active.png" },
      { pagePath: "/pages/teacher/manage/manage", text: "管理", iconPath: "/static/tab/run.png", selectedIconPath: "/static/tab/run-active.png" },
      // 暂用 run 图标
      { pagePath: "/pages/teacher/mine/mine", text: "我的", iconPath: "/static/tab/mine.png", selectedIconPath: "/static/tab/mine-active.png" }
    ];
    common_vendor.onMounted(() => {
      const userRole = common_vendor.index.getStorageSync("userRole") || "student";
      role.value = userRole;
    });
    const list = common_vendor.computed(() => {
      return role.value === "teacher" ? teacherList : studentList;
    });
    const selected = common_vendor.computed(() => {
      return list.value.findIndex((item) => item.pagePath === props.current || props.current.startsWith(item.pagePath));
    });
    const switchTab = (item) => {
      const url = item.pagePath;
      if (url === props.current)
        return;
      common_vendor.index.redirectTo({
        url
      });
    };
    return (_ctx, _cache) => {
      return {
        a: common_vendor.f(list.value, (item, index, i0) => {
          return {
            a: selected.value === index ? item.selectedIconPath : item.iconPath,
            b: common_vendor.t(item.text),
            c: selected.value === index ? selectedColor : color,
            d: index,
            e: common_vendor.o(($event) => switchTab(item), index)
          };
        })
      };
    };
  }
};
const Component = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-208a9ade"]]);
wx.createComponent(Component);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/components/CustomTabBar/CustomTabBar.js.map
