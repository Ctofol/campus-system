"use strict";
const common_vendor = require("../../common/vendor.js");
const _sfc_main = {
  __name: "login",
  setup(__props) {
    const currentRole = common_vendor.ref("student");
    const loading = common_vendor.ref(false);
    const loginForm = common_vendor.ref({
      account: "",
      password: ""
    });
    const canSubmit = common_vendor.computed(() => {
      return loginForm.value.account.length > 0 && loginForm.value.password.length > 0;
    });
    const validateForm = () => {
      const { account, password } = loginForm.value;
      if (password.length < 6) {
        common_vendor.index.showToast({ title: "密码长度不能少于6位", icon: "none" });
        return false;
      }
      const phoneRegex = /^1[3-9]\d{9}$/;
      if (/^\d{11}$/.test(account)) {
        if (!phoneRegex.test(account)) {
          common_vendor.index.showToast({ title: "请输入正确的手机号", icon: "none" });
          return false;
        }
      }
      return true;
    };
    const handleLogin = () => {
      if (!canSubmit.value)
        return;
      if (!validateForm())
        return;
      loading.value = true;
      setTimeout(() => {
        loading.value = false;
        const { account, password } = loginForm.value;
        let isValid = false;
        if (currentRole.value === "student") {
          if (account === "2024001" && password === "123456") {
            isValid = true;
          }
        } else if (currentRole.value === "teacher") {
          if (account === "2024888" && password === "123456") {
            isValid = true;
          }
        }
        if (!isValid) {
          common_vendor.index.showToast({
            title: "账号或密码错误",
            icon: "none"
          });
          return;
        }
        const mockUser = {
          userId: loginForm.value.account,
          role: currentRole.value,
          name: currentRole.value === "student" ? "张三" : "李老师",
          schoolId: "10001",
          isPoliceSchool: true
          // 假设是公安院校
        };
        common_vendor.index.setStorageSync("token", "mock_token_123456");
        common_vendor.index.setStorageSync("userInfo", mockUser);
        common_vendor.index.setStorageSync("userRole", currentRole.value);
        common_vendor.index.showToast({
          title: "登录成功",
          icon: "success"
        });
        setTimeout(() => {
          if (currentRole.value === "student") {
            common_vendor.index.redirectTo({ url: "/pages/home/home" });
          } else {
            common_vendor.index.redirectTo({ url: "/pages/teacher/home/home" });
          }
        }, 1e3);
      }, 1e3);
    };
    const goToRegister = () => {
      common_vendor.index.navigateTo({ url: "/pages/register/register" });
    };
    const forgotPassword = () => {
      common_vendor.index.showToast({ title: "请联系管理员重置密码", icon: "none" });
    };
    return (_ctx, _cache) => {
      return {
        a: currentRole.value === "student" ? 1 : "",
        b: common_vendor.o(($event) => currentRole.value = "student"),
        c: currentRole.value === "teacher" ? 1 : "",
        d: common_vendor.o(($event) => currentRole.value = "teacher"),
        e: common_vendor.t(currentRole.value === "student" ? "学号 / 手机号" : "工号 / 手机号"),
        f: currentRole.value === "student" ? "请输入学号/手机号" : "请输入工号/手机号",
        g: loginForm.value.account,
        h: common_vendor.o(($event) => loginForm.value.account = $event.detail.value),
        i: loginForm.value.password,
        j: common_vendor.o(($event) => loginForm.value.password = $event.detail.value),
        k: !canSubmit.value ? 1 : "",
        l: common_vendor.o(handleLogin),
        m: loading.value,
        n: common_vendor.o(goToRegister),
        o: common_vendor.o(forgotPassword)
      };
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-e4e4508d"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/login/login.js.map
