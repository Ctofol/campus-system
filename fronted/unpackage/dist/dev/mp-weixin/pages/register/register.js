"use strict";
const common_vendor = require("../../common/vendor.js");
const _sfc_main = {
  __name: "register",
  setup(__props) {
    const step = common_vendor.ref(1);
    const loading = common_vendor.ref(false);
    const registerForm = common_vendor.ref({
      role: "student",
      // student | teacher
      name: "",
      phone: "",
      code: "",
      password: "",
      confirmPwd: "",
      // 扩展
      school: "",
      college: "",
      major: "",
      class: "",
      empId: "",
      department: "",
      isPoliceSchool: false
    });
    const selectRole = (role) => {
      registerForm.value.role = role;
    };
    const nextStep = () => {
      step.value = 2;
    };
    const togglePolice = (e) => {
      registerForm.value.isPoliceSchool = e.detail.value;
    };
    const goToLogin = () => {
      common_vendor.index.navigateBack();
    };
    const getCode = () => {
      if (!registerForm.value.phone) {
        common_vendor.index.showToast({ title: "请先输入手机号", icon: "none" });
        return;
      }
      const phoneRegex = /^1[3-9]\d{9}$/;
      if (!phoneRegex.test(registerForm.value.phone)) {
        common_vendor.index.showToast({ title: "手机号格式不正确", icon: "none" });
        return;
      }
      common_vendor.index.showToast({ title: "验证码已发送", icon: "success" });
    };
    const handleRegister = () => {
      const form = registerForm.value;
      if (!form.name || !form.phone || !form.password) {
        common_vendor.index.showToast({ title: "请完善基础信息", icon: "none" });
        return;
      }
      const phoneRegex = /^1[3-9]\d{9}$/;
      if (!phoneRegex.test(form.phone)) {
        common_vendor.index.showToast({ title: "请输入正确的手机号", icon: "none" });
        return;
      }
      if (form.password.length < 6) {
        common_vendor.index.showToast({ title: "密码长度不能少于6位", icon: "none" });
        return;
      }
      if (form.password !== form.confirmPwd) {
        common_vendor.index.showToast({ title: "两次密码不一致", icon: "none" });
        return;
      }
      if (form.role === "student" && (!form.school || !form.class)) {
        common_vendor.index.showToast({ title: "请完善学生信息", icon: "none" });
        return;
      }
      if (form.role === "teacher" && (!form.empId || !form.department)) {
        common_vendor.index.showToast({ title: "请完善教师信息", icon: "none" });
        return;
      }
      loading.value = true;
      setTimeout(() => {
        loading.value = false;
        const newUser = {
          userId: form.role === "student" ? form.phone : form.empId,
          // 简化的ID
          role: form.role,
          name: form.name,
          schoolId: "10001",
          // 模拟
          isPoliceSchool: form.isPoliceSchool,
          ...form
        };
        common_vendor.index.setStorageSync("token", "mock_token_register_123");
        common_vendor.index.setStorageSync("userInfo", newUser);
        common_vendor.index.setStorageSync("role", form.role);
        common_vendor.index.showToast({
          title: "注册成功",
          icon: "success"
        });
        setTimeout(() => {
          common_vendor.index.redirectTo({ url: "/pages/home/home" });
        }, 1500);
      }, 1500);
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: step.value === 1
      }, step.value === 1 ? {
        b: registerForm.value.role === "student" ? 1 : "",
        c: common_vendor.o(($event) => selectRole("student")),
        d: registerForm.value.role === "teacher" ? 1 : "",
        e: common_vendor.o(($event) => selectRole("teacher")),
        f: common_vendor.o(nextStep)
      } : common_vendor.e({
        g: common_vendor.o(($event) => step.value = 1),
        h: common_vendor.t(registerForm.value.role === "student" ? "学生" : "教师"),
        i: registerForm.value.name,
        j: common_vendor.o(($event) => registerForm.value.name = $event.detail.value),
        k: registerForm.value.phone,
        l: common_vendor.o(($event) => registerForm.value.phone = $event.detail.value),
        m: registerForm.value.code,
        n: common_vendor.o(($event) => registerForm.value.code = $event.detail.value),
        o: common_vendor.o(getCode),
        p: registerForm.value.password,
        q: common_vendor.o(($event) => registerForm.value.password = $event.detail.value),
        r: registerForm.value.confirmPwd,
        s: common_vendor.o(($event) => registerForm.value.confirmPwd = $event.detail.value),
        t: registerForm.value.role === "student"
      }, registerForm.value.role === "student" ? {
        v: registerForm.value.school,
        w: common_vendor.o(($event) => registerForm.value.school = $event.detail.value),
        x: registerForm.value.college,
        y: common_vendor.o(($event) => registerForm.value.college = $event.detail.value),
        z: registerForm.value.major,
        A: common_vendor.o(($event) => registerForm.value.major = $event.detail.value),
        B: registerForm.value.class,
        C: common_vendor.o(($event) => registerForm.value.class = $event.detail.value)
      } : {}, {
        D: registerForm.value.role === "teacher"
      }, registerForm.value.role === "teacher" ? {
        E: registerForm.value.school,
        F: common_vendor.o(($event) => registerForm.value.school = $event.detail.value),
        G: registerForm.value.empId,
        H: common_vendor.o(($event) => registerForm.value.empId = $event.detail.value),
        I: registerForm.value.department,
        J: common_vendor.o(($event) => registerForm.value.department = $event.detail.value)
      } : {}, {
        K: registerForm.value.isPoliceSchool,
        L: common_vendor.o(togglePolice),
        M: registerForm.value.isPoliceSchool
      }, registerForm.value.isPoliceSchool ? {} : {}, {
        N: common_vendor.o(handleRegister),
        O: loading.value
      }), {
        P: common_vendor.o(goToLogin)
      });
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-bac4a35d"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/register/register.js.map
