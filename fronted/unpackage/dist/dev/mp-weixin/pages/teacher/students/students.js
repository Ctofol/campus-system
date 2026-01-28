"use strict";
const common_vendor = require("../../../common/vendor.js");
const _sfc_main = {
  __name: "students",
  setup(__props) {
    const isBatchMode = common_vendor.ref(false);
    const selectedIds = common_vendor.ref([]);
    const sharedReports = common_vendor.ref([]);
    const showReportsModal = common_vendor.ref(false);
    const students = common_vendor.ref([
      { id: "S1001", name: "张三", no: "20240001", className: "侦查一班", group: "体能A组", status: "正常", statusClass: "ok", health: "良好", expanded: false, recent3km: `12'45"`, weeklyDistance: 15.5, attendance: "100%" },
      { id: "S1002", name: "李四", no: "20240002", className: "侦查二班", group: "体能B组", status: "异常", statusClass: "warn", health: "需关注", expanded: false, recent3km: `15'30"`, weeklyDistance: 5, attendance: "80%" },
      { id: "S1003", name: "王五", no: "20240003", className: "治安一班", group: "体能A组", status: "正常", statusClass: "ok", health: "良好", expanded: false, recent3km: `13'10"`, weeklyDistance: 12, attendance: "95%" }
    ]);
    const keyword = common_vendor.ref("");
    const classOptions = common_vendor.ref(["侦查一班", "侦查二班", "治安一班"]);
    const currentClass = common_vendor.ref("");
    const groupOptions = common_vendor.ref(["体能A组", "体能B组", "康复组"]);
    const currentGroup = common_vendor.ref("");
    const filteredStudents = common_vendor.computed(() => {
      return students.value.filter((s) => {
        const k = keyword.value.trim();
        const matchK = k ? s.name.includes(k) || s.no.includes(k) : true;
        const matchC = currentClass.value ? s.className === currentClass.value : true;
        const matchG = currentGroup.value ? s.group === currentGroup.value : true;
        return matchK && matchC && matchG;
      });
    });
    const total = common_vendor.computed(() => students.value.length);
    const abnormal = common_vendor.computed(() => students.value.filter((s) => s.status === "异常").length);
    const normal = common_vendor.computed(() => students.value.filter((s) => s.status === "正常").length);
    const onClassChange = (e) => {
      const idx = e.detail.value;
      currentClass.value = classOptions.value[idx];
    };
    const onGroupChange = (e) => {
      const idx = e.detail.value;
      currentGroup.value = groupOptions.value[idx];
    };
    const isAllSelected = common_vendor.computed(() => {
      return filteredStudents.value.length > 0 && selectedIds.value.length === filteredStudents.value.length;
    });
    const toggleBatchMode = () => {
      isBatchMode.value = !isBatchMode.value;
      selectedIds.value = [];
      if (isBatchMode.value) {
        students.value.forEach((s) => s.expanded = false);
      }
    };
    const handleCardClick = (stu) => {
      if (isBatchMode.value) {
        toggleSelect(stu);
      } else {
        stu.expanded = !stu.expanded;
      }
    };
    const toggleSelect = (stu) => {
      const idx = selectedIds.value.indexOf(stu.id);
      if (idx > -1) {
        selectedIds.value.splice(idx, 1);
      } else {
        selectedIds.value.push(stu.id);
      }
    };
    const toggleSelectAll = () => {
      if (isAllSelected.value) {
        selectedIds.value = [];
      } else {
        selectedIds.value = filteredStudents.value.map((s) => s.id);
      }
    };
    const batchRemind = () => {
      if (selectedIds.value.length === 0)
        return common_vendor.index.showToast({ title: "请先选择学员", icon: "none" });
      common_vendor.index.showModal({
        title: "批量提醒",
        content: `确定向选中的 ${selectedIds.value.length} 位学员发送跑步提醒吗？`,
        success: (res) => {
          if (res.confirm) {
            common_vendor.index.showToast({ title: "发送成功", icon: "success" });
            toggleBatchMode();
          }
        }
      });
    };
    const batchExport = () => {
      if (selectedIds.value.length === 0)
        return common_vendor.index.showToast({ title: "请先选择学员", icon: "none" });
      common_vendor.index.showLoading({ title: "生成报表中..." });
      setTimeout(() => {
        common_vendor.index.hideLoading();
        common_vendor.index.showToast({ title: "导出成功，已发送至邮箱", icon: "success" });
        toggleBatchMode();
      }, 1500);
    };
    const batchGroup = () => {
      if (selectedIds.value.length === 0)
        return common_vendor.index.showToast({ title: "请先选择学员", icon: "none" });
      common_vendor.index.showActionSheet({
        itemList: groupOptions.value,
        success: (res) => {
          const groupName = groupOptions.value[res.tapIndex];
          students.value.forEach((s) => {
            if (selectedIds.value.includes(s.id)) {
              s.group = groupName;
            }
          });
          common_vendor.index.showToast({ title: "批量分组成功", icon: "success" });
          toggleBatchMode();
        }
      });
    };
    const editGroup = (stu) => {
      common_vendor.index.showActionSheet({
        itemList: groupOptions.value,
        success: (res) => {
          stu.group = groupOptions.value[res.tapIndex];
          common_vendor.index.showToast({ title: "已调整分组", icon: "none" });
        }
      });
    };
    common_vendor.onShow(() => {
      const role = common_vendor.index.getStorageSync("userRole") || common_vendor.index.getStorageSync("role");
      if (role !== "teacher") {
        common_vendor.index.showToast({ title: "请使用教师账号登录", icon: "none" });
        common_vendor.index.redirectTo({ url: "/pages/login/login" });
      }
      sharedReports.value = common_vendor.index.getStorageSync("mockSharedReports") || [];
    });
    const replyStudent = (report) => {
      common_vendor.index.showModal({
        title: "回复指导",
        editable: true,
        placeholderText: "请输入指导建议...",
        success: (res) => {
          if (res.confirm && res.content) {
            common_vendor.index.showToast({ title: "已发送指导", icon: "success" });
          }
        }
      });
    };
    const openDetail = (stu) => {
      common_vendor.index.navigateTo({
        url: `/pages/teacher/students/detail?id=${stu.id}&name=${stu.name}&no=${stu.no}&class=${stu.className}`
      });
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.t(isBatchMode.value ? "取消批量" : "批量管理"),
        b: common_vendor.o(toggleBatchMode),
        c: keyword.value,
        d: common_vendor.o(($event) => keyword.value = $event.detail.value),
        e: common_vendor.t(currentClass.value || "全部班级"),
        f: classOptions.value,
        g: common_vendor.o(onClassChange),
        h: common_vendor.t(currentGroup.value || "全部小组"),
        i: groupOptions.value,
        j: common_vendor.o(onGroupChange),
        k: common_vendor.t(total.value),
        l: common_vendor.t(abnormal.value),
        m: common_vendor.t(normal.value),
        n: sharedReports.value.length > 0
      }, sharedReports.value.length > 0 ? {
        o: common_vendor.t(sharedReports.value.length),
        p: common_vendor.o(($event) => showReportsModal.value = true)
      } : {}, {
        q: common_vendor.f(filteredStudents.value, (stu, idx, i0) => {
          return common_vendor.e(isBatchMode.value ? {
            a: selectedIds.value.includes(stu.id),
            b: common_vendor.o(($event) => toggleSelect(stu), idx)
          } : {}, {
            c: common_vendor.t(stu.name.slice(0, 1)),
            d: common_vendor.t(stu.name),
            e: stu.group
          }, stu.group ? {
            f: common_vendor.t(stu.group)
          } : {}, {
            g: common_vendor.t(stu.no),
            h: common_vendor.t(stu.className),
            i: common_vendor.t(stu.health),
            j: common_vendor.t(stu.status),
            k: common_vendor.n(stu.statusClass)
          }, !isBatchMode.value ? {
            l: common_vendor.t(stu.expanded ? "▲" : "▼")
          } : {}, {
            m: stu.expanded && !isBatchMode.value
          }, stu.expanded && !isBatchMode.value ? {
            n: common_vendor.t(stu.recent3km || "无记录"),
            o: common_vendor.t(stu.weeklyDistance || "0"),
            p: common_vendor.t(stu.attendance || "100%"),
            q: common_vendor.o(($event) => openDetail(stu), idx),
            r: common_vendor.o(($event) => editGroup(stu), idx)
          } : {}, {
            s: idx,
            t: common_vendor.o(($event) => handleCardClick(stu), idx)
          });
        }),
        r: isBatchMode.value,
        s: !isBatchMode.value,
        t: filteredStudents.value.length === 0
      }, filteredStudents.value.length === 0 ? {} : {}, {
        v: isBatchMode.value ? 1 : "",
        w: isBatchMode.value
      }, isBatchMode.value ? {
        x: isAllSelected.value,
        y: common_vendor.o(toggleSelectAll),
        z: common_vendor.t(selectedIds.value.length),
        A: common_vendor.o(batchGroup),
        B: common_vendor.o(batchRemind),
        C: common_vendor.o(batchExport)
      } : {}, {
        D: showReportsModal.value
      }, showReportsModal.value ? {
        E: common_vendor.o(($event) => showReportsModal.value = false),
        F: common_vendor.f(sharedReports.value, (report, idx, i0) => {
          return common_vendor.e({
            a: common_vendor.t(report.studentName),
            b: common_vendor.t(report.time),
            c: common_vendor.t(report.card.title),
            d: report.card.suggestion
          }, report.card.suggestion ? {
            e: common_vendor.t(report.card.suggestion)
          } : {}, {
            f: report.card.chartData
          }, report.card.chartData ? {
            g: common_vendor.f(report.card.chartData, (d, i, i1) => {
              return {
                a: common_vendor.t(d.label),
                b: d.value + "%",
                c: d.color,
                d: common_vendor.t(d.valText),
                e: i
              };
            })
          } : {}, {
            h: common_vendor.o(($event) => replyStudent(), idx),
            i: idx
          });
        }),
        G: common_vendor.o(() => {
        }),
        H: common_vendor.o(($event) => showReportsModal.value = false)
      } : {});
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-87e02a48"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../../.sourcemap/mp-weixin/pages/teacher/students/students.js.map
