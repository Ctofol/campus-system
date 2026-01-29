if (typeof Promise !== "undefined" && !Promise.prototype.finally) {
  Promise.prototype.finally = function(callback) {
    const promise = this.constructor;
    return this.then(
      (value) => promise.resolve(callback()).then(() => value),
      (reason) => promise.resolve(callback()).then(() => {
        throw reason;
      })
    );
  };
}
;
if (typeof uni !== "undefined" && uni && uni.requireGlobal) {
  const global = uni.requireGlobal();
  ArrayBuffer = global.ArrayBuffer;
  Int8Array = global.Int8Array;
  Uint8Array = global.Uint8Array;
  Uint8ClampedArray = global.Uint8ClampedArray;
  Int16Array = global.Int16Array;
  Uint16Array = global.Uint16Array;
  Int32Array = global.Int32Array;
  Uint32Array = global.Uint32Array;
  Float32Array = global.Float32Array;
  Float64Array = global.Float64Array;
  BigInt64Array = global.BigInt64Array;
  BigUint64Array = global.BigUint64Array;
}
;
if (uni.restoreGlobal) {
  uni.restoreGlobal(Vue, weex, plus, setTimeout, clearTimeout, setInterval, clearInterval);
}
(function(vue) {
  "use strict";
  const ON_SHOW = "onShow";
  const ON_LOAD = "onLoad";
  function formatAppLog(type, filename, ...args) {
    if (uni.__log__) {
      uni.__log__(type, filename, ...args);
    } else {
      console[type].apply(console, [...args, filename]);
    }
  }
  const createLifeCycleHook = (lifecycle, flag = 0) => (hook, target = vue.getCurrentInstance()) => {
    !vue.isInSSRComponentSetup && vue.injectHook(lifecycle, hook, target);
  };
  const onShow = /* @__PURE__ */ createLifeCycleHook(
    ON_SHOW,
    1 | 2
    /* HookFlags.PAGE */
  );
  const onLoad = /* @__PURE__ */ createLifeCycleHook(
    ON_LOAD,
    2
    /* HookFlags.PAGE */
  );
  const _export_sfc = (sfc, props) => {
    const target = sfc.__vccOpts || sfc;
    for (const [key, val] of props) {
      target[key] = val;
    }
    return target;
  };
  const color = "#666666";
  const selectedColor = "#20C997";
  const _sfc_main$p = {
    __name: "CustomTabBar",
    props: {
      current: {
        type: String,
        default: ""
      }
    },
    setup(__props, { expose: __expose }) {
      __expose();
      const props = __props;
      const role = vue.ref("student");
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
      vue.onMounted(() => {
        const userRole = uni.getStorageSync("userRole") || "student";
        role.value = userRole;
      });
      const list = vue.computed(() => {
        return role.value === "teacher" ? teacherList : studentList;
      });
      const selected = vue.computed(() => {
        return list.value.findIndex((item) => item.pagePath === props.current || props.current.startsWith(item.pagePath));
      });
      const switchTab = (item) => {
        const url = item.pagePath;
        if (url === props.current)
          return;
        uni.redirectTo({
          url
        });
      };
      const __returned__ = { props, color, selectedColor, role, studentList, teacherList, list, selected, switchTab, ref: vue.ref, computed: vue.computed, onMounted: vue.onMounted };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$o(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("cover-view", { class: "tab-bar" }, [
      vue.createElementVNode("cover-view", { class: "tab-bar-border" }),
      (vue.openBlock(true), vue.createElementBlock(
        vue.Fragment,
        null,
        vue.renderList($setup.list, (item, index) => {
          return vue.openBlock(), vue.createElementBlock("cover-view", {
            key: index,
            class: "tab-bar-item",
            onClick: ($event) => $setup.switchTab(item)
          }, [
            vue.createElementVNode("cover-image", {
              class: "tab-icon",
              src: $setup.selected === index ? item.selectedIconPath : item.iconPath
            }, null, 8, ["src"]),
            vue.createElementVNode(
              "cover-view",
              {
                class: "tab-text",
                style: vue.normalizeStyle({ color: $setup.selected === index ? $setup.selectedColor : $setup.color })
              },
              vue.toDisplayString(item.text),
              5
              /* TEXT, STYLE */
            )
          ], 8, ["onClick"]);
        }),
        128
        /* KEYED_FRAGMENT */
      ))
    ]);
  }
  const CustomTabBar = /* @__PURE__ */ _export_sfc(_sfc_main$p, [["render", _sfc_render$o], ["__scopeId", "data-v-208a9ade"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/components/CustomTabBar/CustomTabBar.vue"]]);
  const BASE_URL = "http://192.168.1.119:8000";
  const request = (options) => {
    return new Promise((resolve, reject) => {
      const token = uni.getStorageSync("token");
      const header = {
        "Content-Type": "application/json",
        ...options.header
      };
      if (token) {
        header["Authorization"] = `Bearer ${token}`;
      }
      uni.request({
        url: `${BASE_URL}${options.url}`,
        method: options.method || "GET",
        data: options.data || {},
        header,
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data);
          } else if (res.statusCode === 401) {
            uni.removeStorageSync("token");
            uni.removeStorageSync("userInfo");
            uni.showToast({
              title: "登录已过期，请重新登录",
              icon: "none"
            });
            setTimeout(() => {
              uni.reLaunch({
                url: "/pages/login/login"
              });
            }, 1500);
            reject(res.data);
          } else {
            uni.showToast({
              title: res.data.detail || "请求失败",
              icon: "none"
            });
            reject(res.data);
          }
        },
        fail: (err) => {
          uni.showToast({
            title: "网络请求失败",
            icon: "none"
          });
          reject(err);
        }
      });
    });
  };
  const login = (data) => {
    return request({
      url: "/auth/login",
      method: "POST",
      data
    });
  };
  const register = (data) => {
    return request({
      url: "/auth/register",
      method: "POST",
      data
    });
  };
  const submitActivity = (data) => {
    return request({
      url: "/activity/finish",
      method: "POST",
      data
    });
  };
  const getTeacherActivities = (params) => {
    let queryString = "";
    if (params) {
      queryString = `?page=${params.page}&size=${params.size}`;
    }
    return request({
      url: `/teacher/activities${queryString}`,
      method: "GET"
    });
  };
  const approveActivity = (activityId) => {
    return request({
      url: `/teacher/activity/${activityId}/approve`,
      method: "POST"
    });
  };
  const createTeacherTask = (data) => {
    return request({
      url: "/teacher/tasks",
      method: "POST",
      data
    });
  };
  const deleteTask = (taskId) => {
    return request({
      url: `/teacher/tasks/${taskId}`,
      method: "DELETE"
    });
  };
  const getTeacherTasks = (params) => {
    let queryString = "";
    if (params) {
      queryString = `?page=${params.page}&size=${params.size}`;
    }
    return request({
      url: `/teacher/tasks${queryString}`,
      method: "GET"
    });
  };
  const getStudentTasks = (params) => {
    let queryString = "";
    if (params) {
      queryString = `?page=${params.page}&size=${params.size}`;
    }
    return request({
      url: `/student/tasks${queryString}`,
      method: "GET"
    });
  };
  const getTeacherStudentActivities = (studentId, params) => {
    return request({
      url: `/teacher/student/${studentId}/activities`,
      method: "GET",
      data: params
    });
  };
  const getTeacherTaskDetail = (taskId) => {
    return request({
      url: `/teacher/tasks/${taskId}`,
      method: "GET"
    });
  };
  const getCheckpoints = () => {
    return request({
      url: "/checkpoints",
      method: "GET"
    });
  };
  const checkIn = (data) => {
    return request({
      url: "/activity/checkin",
      method: "POST",
      data
    });
  };
  const _sfc_main$o = {
    __name: "home",
    setup(__props, { expose: __expose }) {
      __expose();
      const statusBarHeight = vue.ref(20);
      const role = vue.ref("student");
      const userInfo = vue.ref({});
      const teacherTask = vue.ref(null);
      const fetchLatestTask = async () => {
        try {
          const res = await getStudentTasks({ page: 1, size: 1 });
          if (res.items && res.items.length > 0) {
            const task = res.items[0];
            teacherTask.value = {
              id: task.id,
              title: task.title,
              desc: task.description || (task.min_distance ? `目标: ${task.min_distance}km` : "请查看详情")
            };
          } else {
            teacherTask.value = null;
          }
        } catch (e) {
          formatAppLog("error", "at pages/home/home.vue:163", "Fetch task failed", e);
        }
      };
      onShow(() => {
        statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 20;
        const token = uni.getStorageSync("token");
        if (!token) {
          uni.reLaunch({ url: "/pages/login/login" });
          return;
        }
        const userRole = uni.getStorageSync("userRole") || uni.getStorageSync("role");
        if (userRole)
          role.value = userRole;
        const storedUser = uni.getStorageSync("userInfo");
        if (storedUser) {
          try {
            userInfo.value = typeof storedUser === "string" ? JSON.parse(storedUser) : storedUser;
          } catch (e) {
            formatAppLog("error", "at pages/home/home.vue:186", "JSON parse error", e);
            userInfo.value = {};
          }
        }
        fetchLatestTask();
      });
      const showTrainingPlans = vue.ref(true);
      const showRankModal = vue.ref(false);
      const testProjects = vue.ref([
        { name: "引体向上", tag: "体测项目", tagClass: "tag-police", status: "未完成", type: "pull-up" },
        { name: "仰卧起坐", tag: "日常测评", tagClass: "tag-daily", status: "进行中", type: "sit-up" },
        { name: "俯卧撑", tag: "基础训练", tagClass: "tag-base", status: "未开始", type: "push-up" }
      ]);
      const trainingPlans = vue.ref([
        { id: 1, name: "综合体能测试", type: "考核", typeClass: "tag-red", duration: 45, difficulty: "高强度", isCompleted: false },
        { id: 2, name: "1000米爆发力训练", type: "专项", typeClass: "tag-blue", duration: 20, difficulty: "中强度", isCompleted: true },
        { id: 3, name: "核心力量强化课程", type: "日常", typeClass: "tag-green", duration: 30, difficulty: "低强度", isCompleted: false }
      ]);
      const myClub = vue.ref({ name: "刑侦先锋跑团", rank: 3, members: 42, totalDistance: 1205.8, activityCount: 5 });
      const activities = vue.ref([
        { name: "五四青年节环校跑", time: "5月4日 07:00", status: "报名中", statusClass: "status-active", joined: 128 },
        { name: "周末夜跑打卡赛", time: "本周六 19:00", status: "进行中", statusClass: "status-ing", joined: 56 },
        { name: "运动技能交流会", time: "下周三 14:00", status: "预告", statusClass: "status-future", joined: 30 }
      ]);
      const memberUpdates = vue.ref([
        { user: "张伟", time: "10分钟前", action: "完成了", result: "5公里晨跑", likes: 12, avatarColor: "#FF6B6B" },
        { user: "李娜", time: "35分钟前", action: "打卡了", result: "核心力量训练", likes: 8, avatarColor: "#4ECDC4" },
        { user: "王强", time: "1小时前", action: "刷新了", result: "3000米个人记录", likes: 25, avatarColor: "#45B7D1" }
      ]);
      const rankList = vue.ref([
        { name: "晨跑先锋队", members: 56, distance: 2300, heat: 9800 },
        { name: "长跑菁英团", members: 48, distance: 1800, heat: 8500 },
        { name: "校园马拉松社", members: 42, distance: 1205, heat: 7200 },
        { name: "阳光运动队", members: 35, distance: 980, heat: 6e3 }
      ]);
      const getRandomColor = () => {
        const colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD"];
        return colors[Math.floor(Math.random() * colors.length)];
      };
      const handleTaskClick = () => {
        uni.navigateTo({
          url: "/pages/student/tasks/list"
        });
      };
      const gotoAiPolice = () => {
        uni.navigateTo({ url: "/pages/ai-police/ai-police" });
      };
      const browseActivities = () => {
        uni.navigateTo({ url: "/pages/activity/list" });
      };
      const createClub = () => {
        uni.showToast({ title: "创建功能即将上线", icon: "none" });
      };
      const joinClub = () => {
        uni.showToast({ title: "加入功能即将上线", icon: "none" });
      };
      const enterClubDetail = () => {
        uni.showToast({ title: "跑团详情", icon: "none" });
      };
      const showRank = () => {
        showRankModal.value = true;
      };
      const closeRank = () => {
        showRankModal.value = false;
      };
      const showActivityDetail = (act) => {
        uni.navigateTo({
          url: `/pages/activity/detail?name=${act.name}`
        });
      };
      const startTestProject = (item) => {
        uni.redirectTo({ url: "/pages/test/test?project=" + item.name + "&type=" + item.type });
      };
      const startTraining = (item) => {
        uni.navigateTo({
          url: `/pages/run/run?mode=training&planId=${item.id}&name=${item.name}`
        });
      };
      const __returned__ = { statusBarHeight, role, userInfo, teacherTask, fetchLatestTask, showTrainingPlans, showRankModal, testProjects, trainingPlans, myClub, activities, memberUpdates, rankList, getRandomColor, handleTaskClick, gotoAiPolice, browseActivities, createClub, joinClub, enterClubDetail, showRank, closeRank, showActivityDetail, startTestProject, startTraining, ref: vue.ref, get onShow() {
        return onShow;
      }, get onLoad() {
        return onLoad;
      }, CustomTabBar, get getStudentTasks() {
        return getStudentTasks;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$n(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "home-container" }, [
      vue.createElementVNode(
        "view",
        {
          class: "custom-navbar",
          style: vue.normalizeStyle({ paddingTop: $setup.statusBarHeight + "px" })
        },
        [
          vue.createElementVNode("view", { class: "navbar-content" }, [
            vue.createElementVNode("text", { class: "navbar-title" }, "首页")
          ])
        ],
        4
        /* STYLE */
      ),
      vue.createElementVNode(
        "view",
        {
          class: "content-wrapper",
          style: vue.normalizeStyle({ paddingTop: $setup.statusBarHeight + 44 + "px" })
        },
        [
          vue.createElementVNode("view", { class: "student-dashboard" }, [
            vue.createElementVNode("view", { class: "header-section" }, [
              $setup.teacherTask ? (vue.openBlock(), vue.createElementBlock("view", {
                key: 0,
                class: "teacher-task-box",
                onClick: $setup.handleTaskClick
              }, [
                vue.createElementVNode("view", { class: "task-icon-box" }, [
                  vue.createElementVNode("text", { class: "task-icon" }, "📢")
                ]),
                vue.createElementVNode("view", { class: "task-content" }, [
                  vue.createElementVNode("text", { class: "task-title" }, "老师发布了新任务"),
                  vue.createElementVNode(
                    "text",
                    { class: "task-desc" },
                    vue.toDisplayString($setup.teacherTask.title),
                    1
                    /* TEXT */
                  )
                ]),
                vue.createElementVNode("view", { class: "task-action" }, [
                  vue.createElementVNode("text", { class: "btn-text" }, "去完成")
                ])
              ])) : vue.createCommentVNode("v-if", true),
              vue.createElementVNode("view", { class: "student-func-grid" }, [
                vue.createElementVNode("view", {
                  class: "stu-func-item",
                  onClick: $setup.gotoAiPolice
                }, [
                  vue.createElementVNode("view", { class: "stu-func-icon" }, "🤖"),
                  vue.createElementVNode("text", { class: "stu-func-name" }, "AI计数")
                ]),
                vue.createElementVNode("view", {
                  class: "stu-func-item",
                  onClick: $setup.browseActivities
                }, [
                  vue.createElementVNode("view", { class: "stu-func-icon" }, "🚩"),
                  vue.createElementVNode("text", { class: "stu-func-name" }, "跑团活动")
                ]),
                vue.createElementVNode("view", {
                  class: "stu-func-item",
                  onClick: _cache[0] || (_cache[0] = ($event) => uni.redirectTo({ url: "/pages/test/test" }))
                }, [
                  vue.createElementVNode("view", { class: "stu-func-icon" }, "📊"),
                  vue.createElementVNode("text", { class: "stu-func-name" }, "体测成绩")
                ]),
                vue.createElementVNode("view", {
                  class: "stu-func-item",
                  onClick: _cache[1] || (_cache[1] = ($event) => uni.redirectTo({ url: "/pages/mine/mine" }))
                }, [
                  vue.createElementVNode("view", { class: "stu-func-icon" }, "👤"),
                  vue.createElementVNode("text", { class: "stu-func-name" }, "个人中心")
                ])
              ])
            ]),
            vue.createElementVNode("view", { class: "section-container module-card" }, [
              vue.createElementVNode("view", { class: "section-header" }, [
                vue.createElementVNode("text", { class: "section-title" }, "体能考核项目")
              ]),
              vue.createElementVNode("view", { class: "test-project-list" }, [
                (vue.openBlock(true), vue.createElementBlock(
                  vue.Fragment,
                  null,
                  vue.renderList($setup.testProjects, (item, index) => {
                    return vue.openBlock(), vue.createElementBlock("view", {
                      class: "test-card",
                      key: index,
                      onClick: ($event) => $setup.startTestProject(item)
                    }, [
                      vue.createElementVNode(
                        "view",
                        { class: "test-icon" },
                        vue.toDisplayString(item.type === "pull-up" ? "💪" : item.type === "sit-up" ? "🧘" : "🏋️"),
                        1
                        /* TEXT */
                      ),
                      vue.createElementVNode("view", { class: "test-info" }, [
                        vue.createElementVNode(
                          "text",
                          { class: "test-name" },
                          vue.toDisplayString(item.name),
                          1
                          /* TEXT */
                        ),
                        vue.createElementVNode("view", { class: "test-tags" }, [
                          vue.createElementVNode(
                            "text",
                            {
                              class: vue.normalizeClass(["tag-small", item.tagClass])
                            },
                            vue.toDisplayString(item.tag),
                            3
                            /* TEXT, CLASS */
                          )
                        ])
                      ]),
                      vue.createElementVNode(
                        "text",
                        { class: "test-status" },
                        vue.toDisplayString(item.status),
                        1
                        /* TEXT */
                      )
                    ], 8, ["onClick"]);
                  }),
                  128
                  /* KEYED_FRAGMENT */
                ))
              ])
            ]),
            vue.createElementVNode("view", { class: "section-container module-card" }, [
              vue.createElementVNode("view", {
                class: "section-header",
                onClick: _cache[2] || (_cache[2] = ($event) => $setup.showTrainingPlans = !$setup.showTrainingPlans)
              }, [
                vue.createElementVNode("text", { class: "section-title" }, "专项训练计划"),
                vue.createElementVNode(
                  "text",
                  { class: "section-more" },
                  vue.toDisplayString($setup.showTrainingPlans ? "收起" : "展开"),
                  1
                  /* TEXT */
                )
              ]),
              $setup.showTrainingPlans ? (vue.openBlock(), vue.createElementBlock("view", {
                key: 0,
                class: "training-list"
              }, [
                (vue.openBlock(true), vue.createElementBlock(
                  vue.Fragment,
                  null,
                  vue.renderList($setup.trainingPlans, (item, index) => {
                    return vue.openBlock(), vue.createElementBlock("view", {
                      class: "training-card",
                      key: index,
                      onClick: ($event) => $setup.startTraining(item)
                    }, [
                      vue.createElementVNode("view", { class: "card-left" }, [
                        vue.createElementVNode(
                          "view",
                          {
                            class: vue.normalizeClass(["tag-box", item.typeClass])
                          },
                          [
                            vue.createElementVNode(
                              "text",
                              { class: "tag-text" },
                              vue.toDisplayString(item.type),
                              1
                              /* TEXT */
                            )
                          ],
                          2
                          /* CLASS */
                        ),
                        vue.createElementVNode("view", { class: "training-info" }, [
                          vue.createElementVNode(
                            "text",
                            { class: "training-name" },
                            vue.toDisplayString(item.name),
                            1
                            /* TEXT */
                          ),
                          vue.createElementVNode(
                            "text",
                            { class: "training-meta" },
                            vue.toDisplayString(item.duration) + "分钟 · " + vue.toDisplayString(item.difficulty),
                            1
                            /* TEXT */
                          )
                        ])
                      ]),
                      vue.createElementVNode("view", { class: "card-right" }, [
                        item.isCompleted ? (vue.openBlock(), vue.createElementBlock("view", {
                          key: 0,
                          class: "status-icon"
                        }, [
                          vue.createElementVNode("text", null, "✅")
                        ])) : (vue.openBlock(), vue.createElementBlock("view", {
                          key: 1,
                          class: "start-btn-small"
                        }, [
                          vue.createElementVNode("text", null, "开始")
                        ]))
                      ])
                    ], 8, ["onClick"]);
                  }),
                  128
                  /* KEYED_FRAGMENT */
                ))
              ])) : vue.createCommentVNode("v-if", true)
            ]),
            vue.createElementVNode("view", { class: "section-container module-card" }, [
              vue.createElementVNode("view", { class: "section-header" }, [
                vue.createElementVNode("text", { class: "section-title" }, "跑团联盟"),
                vue.createElementVNode("view", { class: "header-actions" }, [
                  vue.createElementVNode("text", {
                    class: "action-link",
                    onClick: $setup.createClub
                  }, "创建"),
                  vue.createElementVNode("text", { class: "divider" }, "|"),
                  vue.createElementVNode("text", {
                    class: "action-link",
                    onClick: $setup.joinClub
                  }, "加入"),
                  vue.createElementVNode("text", { class: "divider" }, "|"),
                  vue.createElementVNode("text", {
                    class: "action-link",
                    onClick: $setup.browseActivities
                  }, "活动浏览")
                ])
              ]),
              vue.createElementVNode("view", {
                class: "my-club-card",
                onClick: $setup.enterClubDetail
              }, [
                vue.createElementVNode("view", { class: "club-bg-overlay" }),
                vue.createElementVNode("view", { class: "club-info" }, [
                  vue.createElementVNode("view", { class: "club-header" }, [
                    vue.createElementVNode(
                      "text",
                      { class: "club-name" },
                      vue.toDisplayString($setup.myClub.name),
                      1
                      /* TEXT */
                    ),
                    vue.createElementVNode(
                      "text",
                      { class: "club-rank" },
                      "No." + vue.toDisplayString($setup.myClub.rank),
                      1
                      /* TEXT */
                    )
                  ]),
                  vue.createElementVNode("view", { class: "club-stats" }, [
                    vue.createElementVNode("view", { class: "stat-box" }, [
                      vue.createElementVNode(
                        "text",
                        { class: "val" },
                        vue.toDisplayString($setup.myClub.members),
                        1
                        /* TEXT */
                      ),
                      vue.createElementVNode("text", { class: "label" }, "成员")
                    ]),
                    vue.createElementVNode("view", { class: "stat-box" }, [
                      vue.createElementVNode(
                        "text",
                        { class: "val" },
                        vue.toDisplayString($setup.myClub.totalDistance),
                        1
                        /* TEXT */
                      ),
                      vue.createElementVNode("text", { class: "label" }, "总里程(km)")
                    ]),
                    vue.createElementVNode("view", { class: "stat-box" }, [
                      vue.createElementVNode(
                        "text",
                        { class: "val" },
                        vue.toDisplayString($setup.myClub.activityCount),
                        1
                        /* TEXT */
                      ),
                      vue.createElementVNode("text", { class: "label" }, "本月活动")
                    ])
                  ])
                ]),
                vue.createElementVNode("view", {
                  class: "rank-entry",
                  onClick: vue.withModifiers($setup.showRank, ["stop"])
                }, [
                  vue.createElementVNode("text", { class: "rank-icon" }, "🏆"),
                  vue.createElementVNode("text", { class: "rank-text" }, "排行榜")
                ])
              ]),
              vue.createElementVNode("view", { class: "community-feed" }, [
                vue.createElementVNode("text", { class: "feed-title" }, "最新动态"),
                vue.createElementVNode("scroll-view", {
                  "scroll-x": "",
                  class: "activity-scroll"
                }, [
                  (vue.openBlock(true), vue.createElementBlock(
                    vue.Fragment,
                    null,
                    vue.renderList($setup.activities, (act, idx) => {
                      return vue.openBlock(), vue.createElementBlock("view", {
                        class: "activity-card",
                        key: idx,
                        onClick: ($event) => $setup.showActivityDetail(act)
                      }, [
                        vue.createElementVNode(
                          "view",
                          {
                            class: vue.normalizeClass(["act-tag", act.statusClass])
                          },
                          vue.toDisplayString(act.status),
                          3
                          /* TEXT, CLASS */
                        ),
                        vue.createElementVNode(
                          "text",
                          { class: "act-name" },
                          vue.toDisplayString(act.name),
                          1
                          /* TEXT */
                        ),
                        vue.createElementVNode(
                          "text",
                          { class: "act-time" },
                          "🕒 " + vue.toDisplayString(act.time),
                          1
                          /* TEXT */
                        ),
                        vue.createElementVNode("view", { class: "act-users" }, [
                          vue.createElementVNode("view", { class: "avatar-group" }, [
                            (vue.openBlock(), vue.createElementBlock(
                              vue.Fragment,
                              null,
                              vue.renderList(3, (n) => {
                                return vue.createElementVNode(
                                  "view",
                                  {
                                    class: "avatar-circle",
                                    key: n,
                                    style: vue.normalizeStyle({ backgroundColor: $setup.getRandomColor() })
                                  },
                                  null,
                                  4
                                  /* STYLE */
                                );
                              }),
                              64
                              /* STABLE_FRAGMENT */
                            ))
                          ]),
                          vue.createElementVNode(
                            "text",
                            { class: "act-count" },
                            vue.toDisplayString(act.joined) + "人已报名",
                            1
                            /* TEXT */
                          )
                        ])
                      ], 8, ["onClick"]);
                    }),
                    128
                    /* KEYED_FRAGMENT */
                  ))
                ])
              ])
            ])
          ]),
          vue.createElementVNode("view", { style: { "height": "120rpx" } }),
          vue.createVNode($setup["CustomTabBar"], { current: "/pages/home/home" }),
          $setup.showRankModal ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 0,
            class: "modal-overlay",
            onClick: $setup.closeRank
          }, [
            vue.createElementVNode("view", {
              class: "rank-modal",
              onClick: _cache[3] || (_cache[3] = vue.withModifiers(() => {
              }, ["stop"]))
            }, [
              vue.createElementVNode("view", { class: "modal-header" }, [
                vue.createElementVNode("text", { class: "modal-title" }, "🏆 跑团排行榜"),
                vue.createElementVNode("text", {
                  class: "close-btn",
                  onClick: $setup.closeRank
                }, "×")
              ]),
              vue.createElementVNode("view", { class: "rank-list" }, [
                (vue.openBlock(true), vue.createElementBlock(
                  vue.Fragment,
                  null,
                  vue.renderList($setup.rankList, (item, idx) => {
                    return vue.openBlock(), vue.createElementBlock("view", {
                      class: "rank-item",
                      key: idx
                    }, [
                      vue.createElementVNode(
                        "view",
                        {
                          class: vue.normalizeClass(["rank-num", "rank-" + (idx + 1)])
                        },
                        vue.toDisplayString(idx + 1),
                        3
                        /* TEXT, CLASS */
                      ),
                      vue.createElementVNode("view", { class: "rank-info" }, [
                        vue.createElementVNode(
                          "text",
                          { class: "rank-name" },
                          vue.toDisplayString(item.name),
                          1
                          /* TEXT */
                        ),
                        vue.createElementVNode(
                          "text",
                          { class: "rank-detail" },
                          vue.toDisplayString(item.members) + "人 / " + vue.toDisplayString(item.distance) + "km",
                          1
                          /* TEXT */
                        )
                      ]),
                      vue.createElementVNode("view", { class: "rank-trend" }, [
                        vue.createElementVNode(
                          "text",
                          null,
                          "🔥 " + vue.toDisplayString(item.heat),
                          1
                          /* TEXT */
                        )
                      ])
                    ]);
                  }),
                  128
                  /* KEYED_FRAGMENT */
                ))
              ])
            ])
          ])) : vue.createCommentVNode("v-if", true)
        ],
        4
        /* STYLE */
      )
    ]);
  }
  const PagesHomeHome = /* @__PURE__ */ _export_sfc(_sfc_main$o, [["render", _sfc_render$n], ["__scopeId", "data-v-07e72d3c"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/home/home.vue"]]);
  const _sfc_main$n = {
    __name: "ai-chat-robot",
    props: {
      visible: Boolean,
      runData: {
        type: Object,
        default: () => ({ distance: 0, pace: 0, heartRate: 0 })
      }
    },
    emits: ["update:visible", "share"],
    setup(__props, { expose: __expose, emit: __emit }) {
      __expose();
      const props = __props;
      const emit = __emit;
      const messages = vue.ref([
        { type: "robot", text: "你好！我是你的专属运动小助手。我正在实时分析你的跑步数据，有什么可以帮你的吗？" }
      ]);
      const inputText = vue.ref("");
      const scrollTop = vue.ref(0);
      const close = () => {
        emit("update:visible", false);
      };
      const scrollToBottom = () => {
        vue.nextTick(() => {
          scrollTop.value = 99999;
        });
      };
      const sendText = () => {
        if (!inputText.value.trim())
          return;
        ask(inputText.value);
        inputText.value = "";
      };
      const ask = (text) => {
        messages.value.push({ type: "user", text });
        scrollToBottom();
        setTimeout(() => {
          analyzeAndReply(text);
        }, 800);
      };
      const analyzeAndReply = (question) => {
        let reply = { type: "robot", text: "", card: null };
        const { distance, pace, heartRate } = props.runData;
        if (question.includes("配速")) {
          reply.text = `当前配速 ${pace.toFixed(2)} 分钟/公里。`;
          let suggestion = "";
          let color2 = "#20C997";
          if (pace < 4) {
            suggestion = "速度很快，请注意保持心率稳定！";
            color2 = "#FF6B6B";
          } else if (pace > 8) {
            suggestion = "速度稍慢，建议加快摆臂频率来提升速度。";
            color2 = "#FF9F43";
          } else {
            suggestion = "配速保持得很好，继续加油！";
          }
          reply.card = {
            title: "🏃 配速分析",
            chartData: [
              { label: "当前", value: Math.min(100, 10 / pace * 50), valText: `${pace.toFixed(1)}`, color: color2 },
              { label: "目标", value: 70, valText: "6.0", color: "#3A7BD5" }
              // Assume target 6.0
            ],
            suggestion,
            shareable: true
          };
        } else if (question.includes("运动量") || question.includes("够吗")) {
          const km = (distance / 1e3).toFixed(2);
          reply.text = `你今天已经跑了 ${km} 公里。`;
          let suggestion = "";
          if (km < 2) {
            suggestion = "建议今天至少完成 3 公里，加油！";
          } else if (km > 10) {
            suggestion = "运动量非常充足，注意跑后拉伸。";
          } else {
            suggestion = "运动量适中，保持这个节奏。";
          }
          reply.card = {
            title: "📊 运动量评估",
            chartData: [
              { label: "今日", value: Math.min(100, km / 5 * 100), valText: `${km}km`, color: "#20C997" },
              { label: "目标", value: 100, valText: "5.0km", color: "#eee" }
            ],
            suggestion,
            shareable: true
          };
        } else if (question.includes("建议") || question.includes("分析")) {
          reply.text = "基于你的实时数据，我生成了一份简报：";
          reply.card = {
            title: "💡 综合改进建议",
            suggestion: heartRate > 160 ? "心率偏高，建议适当放慢速度，调整呼吸。" : "心率控制良好，可以尝试进行间歇跑训练提升耐力。",
            chartData: [
              { label: "心率", value: Math.min(100, heartRate / 200 * 100), valText: `${heartRate}bpm`, color: heartRate > 160 ? "#FF4757" : "#20C997" },
              { label: "配速", value: Math.min(100, 10 / pace * 50), valText: `${pace.toFixed(1)}`, color: "#3A7BD5" }
            ],
            shareable: true
          };
        } else {
          reply.text = "抱歉，我还在学习中，暂时只能回答关于配速、运动量和改进建议的问题。";
        }
        messages.value.push(reply);
        scrollToBottom();
      };
      const shareToTeacher = (card) => {
        uni.showToast({ title: "已发送给教官", icon: "success" });
        emit("share", card);
      };
      vue.watch(() => props.visible, (val) => {
        if (val && messages.value.length === 0) {
          messages.value.push({ type: "robot", text: "你好！我是你的专属运动小助手。" });
        }
      });
      const __returned__ = { props, emit, messages, inputText, scrollTop, close, scrollToBottom, sendText, ask, analyzeAndReply, shareToTeacher, ref: vue.ref, watch: vue.watch, nextTick: vue.nextTick };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$m(_ctx, _cache, $props, $setup, $data, $options) {
    return $props.visible ? (vue.openBlock(), vue.createElementBlock("view", {
      key: 0,
      class: "ai-robot-container"
    }, [
      vue.createElementVNode("view", {
        class: "robot-mask",
        onClick: $setup.close
      }),
      vue.createElementVNode("view", { class: "robot-window" }, [
        vue.createElementVNode("view", { class: "robot-header" }, [
          vue.createElementVNode("view", { class: "header-left" }, [
            vue.createElementVNode("view", { class: "robot-avatar" }, "🤖"),
            vue.createElementVNode("view", { class: "robot-info" }, [
              vue.createElementVNode("text", { class: "robot-name" }, "运动小助手"),
              vue.createElementVNode("text", { class: "robot-status" }, "在线分析中...")
            ])
          ]),
          vue.createElementVNode("view", { class: "header-right" }, [
            vue.createElementVNode("text", {
              class: "close-btn",
              onClick: $setup.close
            }, "×")
          ])
        ]),
        vue.createElementVNode("scroll-view", {
          "scroll-y": "",
          class: "chat-area",
          "scroll-top": $setup.scrollTop
        }, [
          vue.createElementVNode("view", { class: "message-list" }, [
            (vue.openBlock(true), vue.createElementBlock(
              vue.Fragment,
              null,
              vue.renderList($setup.messages, (msg, index) => {
                return vue.openBlock(), vue.createElementBlock(
                  "view",
                  {
                    key: index,
                    class: vue.normalizeClass(["message-item", msg.type])
                  },
                  [
                    msg.type === "robot" ? (vue.openBlock(), vue.createElementBlock("view", {
                      key: 0,
                      class: "msg-avatar"
                    }, "🤖")) : vue.createCommentVNode("v-if", true),
                    vue.createElementVNode("view", { class: "msg-content-box" }, [
                      vue.createElementVNode("view", { class: "msg-content" }, [
                        vue.createElementVNode(
                          "text",
                          null,
                          vue.toDisplayString(msg.text),
                          1
                          /* TEXT */
                        )
                      ]),
                      msg.card ? (vue.openBlock(), vue.createElementBlock("view", {
                        key: 0,
                        class: "msg-card"
                      }, [
                        vue.createElementVNode(
                          "view",
                          { class: "card-title" },
                          vue.toDisplayString(msg.card.title),
                          1
                          /* TEXT */
                        ),
                        msg.card.chartData ? (vue.openBlock(), vue.createElementBlock("view", {
                          key: 0,
                          class: "card-chart"
                        }, [
                          (vue.openBlock(true), vue.createElementBlock(
                            vue.Fragment,
                            null,
                            vue.renderList(msg.card.chartData, (item, idx) => {
                              return vue.openBlock(), vue.createElementBlock("view", {
                                class: "chart-bar-item",
                                key: idx
                              }, [
                                vue.createElementVNode(
                                  "text",
                                  { class: "bar-label" },
                                  vue.toDisplayString(item.label),
                                  1
                                  /* TEXT */
                                ),
                                vue.createElementVNode("view", { class: "bar-track" }, [
                                  vue.createElementVNode(
                                    "view",
                                    {
                                      class: "bar-fill",
                                      style: vue.normalizeStyle({ width: item.value + "%", background: item.color })
                                    },
                                    null,
                                    4
                                    /* STYLE */
                                  )
                                ]),
                                vue.createElementVNode(
                                  "text",
                                  { class: "bar-val" },
                                  vue.toDisplayString(item.valText),
                                  1
                                  /* TEXT */
                                )
                              ]);
                            }),
                            128
                            /* KEYED_FRAGMENT */
                          ))
                        ])) : vue.createCommentVNode("v-if", true),
                        msg.card.suggestion ? (vue.openBlock(), vue.createElementBlock("view", {
                          key: 1,
                          class: "card-suggestion"
                        }, [
                          vue.createElementVNode("text", { class: "suggestion-icon" }, "💡"),
                          vue.createElementVNode(
                            "text",
                            null,
                            vue.toDisplayString(msg.card.suggestion),
                            1
                            /* TEXT */
                          )
                        ])) : vue.createCommentVNode("v-if", true),
                        msg.card.shareable ? (vue.openBlock(), vue.createElementBlock("button", {
                          key: 2,
                          class: "share-btn",
                          size: "mini",
                          onClick: ($event) => $setup.shareToTeacher(msg.card)
                        }, "分享给教官", 8, ["onClick"])) : vue.createCommentVNode("v-if", true)
                      ])) : vue.createCommentVNode("v-if", true)
                    ]),
                    msg.type === "user" ? (vue.openBlock(), vue.createElementBlock("view", {
                      key: 1,
                      class: "msg-avatar"
                    }, "👤")) : vue.createCommentVNode("v-if", true)
                  ],
                  2
                  /* CLASS */
                );
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ])
        ], 8, ["scroll-top"]),
        vue.createElementVNode("view", { class: "input-area" }, [
          vue.createElementVNode("scroll-view", {
            "scroll-x": "",
            class: "quick-replies",
            "show-scrollbar": false
          }, [
            vue.createElementVNode("view", {
              class: "chip",
              onClick: _cache[0] || (_cache[0] = ($event) => $setup.ask("我的配速怎么样？"))
            }, "配速分析"),
            vue.createElementVNode("view", {
              class: "chip",
              onClick: _cache[1] || (_cache[1] = ($event) => $setup.ask("今天运动量够吗？"))
            }, "运动量评估"),
            vue.createElementVNode("view", {
              class: "chip",
              onClick: _cache[2] || (_cache[2] = ($event) => $setup.ask("给点建议"))
            }, "改进建议")
          ]),
          vue.createElementVNode("view", { class: "input-box" }, [
            vue.withDirectives(vue.createElementVNode(
              "input",
              {
                class: "text-input",
                "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $setup.inputText = $event),
                placeholder: "输入问题...",
                "confirm-type": "send",
                onConfirm: $setup.sendText
              },
              null,
              544
              /* NEED_HYDRATION, NEED_PATCH */
            ), [
              [vue.vModelText, $setup.inputText]
            ]),
            vue.createElementVNode("view", {
              class: "send-btn",
              onClick: $setup.sendText
            }, "发送")
          ])
        ])
      ])
    ])) : vue.createCommentVNode("v-if", true);
  }
  const AiChatRobot = /* @__PURE__ */ _export_sfc(_sfc_main$n, [["render", _sfc_render$m], ["__scopeId", "data-v-b77ff380"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/components/ai-chat-robot/ai-chat-robot.vue"]]);
  const STEP_THRESHOLD_UP = 1.25;
  const STEP_THRESHOLD_DOWN = 1.05;
  const MIN_STEP_INTERVAL = 300;
  const RESET_TIMEOUT = 1500;
  const _sfc_main$m = {
    __name: "run",
    setup(__props, { expose: __expose }) {
      __expose();
      const statusBarHeight = vue.ref(20);
      onLoad(() => {
        const sys = uni.getSystemInfoSync();
        statusBarHeight.value = sys.statusBarHeight || 20;
      });
      vue.onUnmounted(() => {
        if (timer)
          clearInterval(timer);
        stopStepCount();
      });
      const showAiRobot = vue.ref(false);
      const currentRunData = vue.computed(() => ({
        distance: distance.value,
        pace: currentPace.value || (distance.value > 0 ? duration.value / 60 / (distance.value / 1e3) : 0),
        heartRate: heartRate.value,
        stepCount: stepCount.value
      }));
      const openAiRobot = () => {
        showAiRobot.value = true;
      };
      onShow(() => {
        formatAppLog("log", "at pages/run/run.vue:205", "run.vue onShow triggered");
        uni.setNavigationBarTitle({
          title: "跑步"
        });
        uni.setNavigationBarColor({
          frontColor: "#ffffff",
          backgroundColor: "#20C997"
        });
        const role = uni.getStorageSync("userRole") || uni.getStorageSync("role");
        if (role === "teacher") {
          uni.showToast({ title: "该功能仅对学生开放", icon: "none" });
          setTimeout(() => {
            uni.redirectTo({ url: "/pages/teacher/home/home" });
          }, 800);
          return;
        }
        const targetMode = uni.getStorageSync("runMode");
        if (targetMode) {
          switchMode(targetMode);
          uni.removeStorageSync("runMode");
        }
        getLocation();
        checkpoint.value = uni.getStorageSync("checkpoint") || {};
        if (checkpoint.value.name) {
          addCheckpointMarker(checkpoint.value.lat, checkpoint.value.lng, checkpoint.value.name);
        }
        const records = uni.getStorageSync("runRecordsList") || [];
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
        const taskStr = uni.getStorageSync("teacherTask");
        if (taskStr) {
          try {
            const obj = typeof taskStr === "string" ? JSON.parse(taskStr) : taskStr;
            teacherRunTask.value = obj.title || "";
          } catch (e) {
            teacherRunTask.value = "";
          }
        }
      });
      const handleShareToTeacher = (card) => {
        var _a;
        const report = {
          studentName: ((_a = uni.getStorageSync("userInfo")) == null ? void 0 : _a.name) || "学员",
          time: (/* @__PURE__ */ new Date()).toLocaleString(),
          card
        };
        let sharedReports = uni.getStorageSync("mockSharedReports") || [];
        sharedReports.unshift(report);
        uni.setStorageSync("mockSharedReports", sharedReports);
      };
      const todayRunCount = vue.ref(0);
      const todayRunDistance = vue.ref(0);
      const teacherRunTask = vue.ref("");
      const dailyTarget = vue.ref(5);
      const normalProgress = vue.ref(0);
      const policeProgress = vue.ref(0);
      const historyList = vue.ref([]);
      const achievements = vue.ref([
        { name: "初次开跑", icon: "🏅" },
        { name: "五公里达人", icon: "🏃‍♂️" },
        { name: "全勤周", icon: "🔥" },
        { name: "早起鸟", icon: "🐦" }
      ]);
      const showRoutes = vue.ref(false);
      const recommendRoutes = vue.ref([
        { name: "环校外圈跑", distance: 5.2, difficulty: "中等" },
        { name: "湖畔林荫道", distance: 3, difficulty: "简单" },
        { name: "体育场冲刺", distance: 1.5, difficulty: "困难" }
      ]);
      const toggleRoutes = () => showRoutes.value = !showRoutes.value;
      const useRoute = (route) => {
        uni.showToast({ title: `已加载路线：${route.name}`, icon: "none" });
        dailyTarget.value = route.distance;
      };
      const checkpointName = vue.ref("");
      const lat = vue.ref(39.909);
      const lng = vue.ref(116.397);
      const markers = vue.ref([]);
      const polyline = vue.ref([{ points: [], color: "#007AFF", width: 4 }]);
      const checkpoint = vue.ref({});
      const trajectoryPoints = vue.ref([]);
      const checkinRecords = vue.ref([]);
      const getDistance = (lat1, lng1, lat2, lng2) => {
        const R = 6371e3;
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLng = (lng2 - lng1) * Math.PI / 180;
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c;
      };
      const startRealLocationTracking = () => {
        uni.startLocationUpdate({
          success: () => {
            locationCallback = (res) => {
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
                    if (!uni.getStorageSync("checkpointReached")) {
                      if (checkpoint.value.id) {
                        checkIn({ lat: newLat, lng: newLng, checkpoint_id: checkpoint.value.id }).then((res2) => {
                          if (res2.success) {
                            uni.showToast({ title: "打卡成功！", icon: "success" });
                            checkinRecords.value.push({ checkpoint_id: checkpoint.value.id, time: (/* @__PURE__ */ new Date()).toISOString(), lat: newLat, lng: newLng });
                          }
                        }).catch(() => {
                        });
                      } else {
                        uni.showToast({ title: "已到达打卡点范围！", icon: "success" });
                      }
                      uni.setStorageSync("checkpointReached", "1");
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
            };
            uni.onLocationChange(locationCallback);
          },
          fail: () => {
            uni.showToast({ title: "无法获取实时位置，请检查权限", icon: "none" });
          }
        });
      };
      const stopRealLocationTracking = () => {
        uni.stopLocationUpdate();
        if (locationCallback) {
          uni.offLocationChange(locationCallback);
          locationCallback = null;
        }
      };
      const currentMode = vue.ref("normal");
      const isRunning = vue.ref(false);
      const duration = vue.ref(0);
      const distance = vue.ref(0);
      const distanceToCheckpoint = vue.ref(0);
      const isReach = vue.ref(false);
      const stepCount = vue.ref(0);
      const heartRate = vue.ref(80);
      const currentSpeed = vue.ref(0);
      const maxSpeed = vue.ref(0);
      let timer = null;
      let accelerometerCallback = null;
      let locationCallback = null;
      let h5LocationTimer = null;
      const policeTargetDistance = vue.ref(2e3);
      const policeTargetPace = vue.ref(6.5);
      const currentPace = vue.computed(() => {
        const km = distance.value / 1e3;
        const min = duration.value / 60;
        if (km === 0)
          return 0;
        const p = min / km;
        return p > 999 ? 999 : p;
      });
      const currentSpeedKmh = vue.computed(() => (currentSpeed.value * 3.6).toFixed(1));
      const avgSpeedKmh = vue.computed(() => {
        if (duration.value === 0)
          return 0;
        return (distance.value / 1e3 / (duration.value / 3600)).toFixed(1);
      });
      onLoad((options) => {
        if (options.mode) {
          currentMode.value = options.mode;
        }
        if (options.target) {
          policeTargetDistance.value = parseInt(options.target);
        }
        if (options.course) {
          uni.showToast({ title: `开始课程：${options.course}`, icon: "none" });
        }
      });
      const getLocation = () => {
        doGetLocation();
      };
      const doGetLocation = () => {
        const lastLoc = uni.getStorageSync("lastLocation");
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
        uni.getLocation({
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
              uni.showToast({ title: "仅校园内可进行打卡", icon: "none" });
            }
          },
          fail: (err) => {
            formatAppLog("error", "at pages/run/run.vue:606", "Location failed:", err);
            let msg = "定位失败，已使用模拟位置";
            uni.showToast({ title: msg, icon: "none", duration: 3e3 });
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
          uni.showToast({ title: "请输入打卡点名称", icon: "none" });
          return;
        }
        const newCheckpoint = {
          name: checkpointName.value,
          lat: lat.value + 1e-3,
          lng: lng.value + 1e-3
        };
        uni.setStorageSync("checkpoint", newCheckpoint);
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
        uni.showToast({ title: `找到${newCheckpoint.name}`, icon: "success" });
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
      let isStepActive = false;
      let lastStepTime = 0;
      const startStepCount = () => {
        uni.stopAccelerometer();
        uni.startAccelerometer({
          interval: "game",
          // 使用 game (20ms) 频率，采样更密集，捕捉波峰更准
          success: () => {
            formatAppLog("log", "at pages/run/run.vue:703", "Accelerometer started");
            isStepActive = false;
            lastStepTime = Date.now();
          },
          fail: (err) => {
            formatAppLog("error", "at pages/run/run.vue:708", "Start Accelerometer failed:", err);
          }
        });
        accelerometerCallback = (res) => {
          let acceleration = Math.sqrt(res.x * res.x + res.y * res.y + res.z * res.z);
          if (acceleration > 5) {
            acceleration = acceleration / 9.8;
          }
          const now = Date.now();
          if (isStepActive && now - lastStepTime > RESET_TIMEOUT) {
            isStepActive = false;
          }
          if (!isStepActive && acceleration > STEP_THRESHOLD_UP) {
            if (now - lastStepTime > MIN_STEP_INTERVAL) {
              stepCount.value += 1;
              lastStepTime = now;
              isStepActive = true;
            }
          } else if (isStepActive && acceleration < STEP_THRESHOLD_DOWN) {
            isStepActive = false;
          }
        };
        uni.onAccelerometerChange(accelerometerCallback);
      };
      const stopStepCount = () => {
        if (accelerometerCallback) {
          uni.stopAccelerometer();
          uni.offAccelerometerChange(accelerometerCallback);
          accelerometerCallback = null;
        }
      };
      const updateHeartRate = () => {
        heartRate.value = 80 + Math.floor(duration.value / 10);
        if (heartRate.value > 180) {
          uni.showModal({
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
        uni.removeStorageSync("checkpointReached");
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
        uni.removeStorageSync("policeFinishTip");
        startRealLocationTracking();
        startStepCount();
        timer = setInterval(() => {
          duration.value += 1;
          updateHeartRate();
          if (distance.value >= policeTargetDistance.value && !uni.getStorageSync("policeFinishTip")) {
            uni.showToast({ title: "已完成2000米目标！", icon: "success" });
            uni.setStorageSync("policeFinishTip", "1");
          }
        }, 1e3);
      };
      const startCampusRun = () => {
        isRunning.value = true;
        duration.value = 0;
        isReach.value = false;
        stepCount.value = 0;
        heartRate.value = 80;
        uni.removeStorageSync("checkpointReached");
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
        const token = uni.getStorageSync("token");
        if (!token) {
          uni.showToast({ title: "请先登录", icon: "none" });
          setTimeout(() => {
            uni.reLaunch({ url: "/pages/login/login" });
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
          uni.showLoading({ title: "提交中..." });
          const res = await submitActivity(runData);
          uni.hideLoading();
          formatAppLog("log", "at pages/run/run.vue:851", "Submit success:", res);
          uni.setStorageSync("tempRunResult", runData);
          uni.redirectTo({
            url: "/pages/result/result?useStorage=true",
            fail: (err) => {
              formatAppLog("error", "at pages/run/run.vue:861", "Navigate failed:", err);
              uni.showToast({ title: "页面跳转失败", icon: "none" });
            }
          });
        } catch (error) {
          uni.hideLoading();
          formatAppLog("error", "at pages/run/run.vue:867", "Submit failed:", error);
          uni.showModal({
            title: "提交失败",
            content: error && error.detail ? error.detail : "网络或服务器错误，请重试",
            confirmText: "重试",
            cancelText: "强制结束",
            success: (modalRes) => {
              if (modalRes.confirm)
                ;
              else if (modalRes.cancel) {
                uni.showToast({ title: "已强制结束", icon: "none" });
                setTimeout(() => {
                  uni.reLaunch({ url: "/pages/home/home" });
                }, 800);
              }
            }
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
      const __returned__ = { statusBarHeight, showAiRobot, currentRunData, openAiRobot, handleShareToTeacher, todayRunCount, todayRunDistance, teacherRunTask, dailyTarget, normalProgress, policeProgress, historyList, achievements, showRoutes, recommendRoutes, toggleRoutes, useRoute, checkpointName, lat, lng, markers, polyline, checkpoint, trajectoryPoints, checkinRecords, getDistance, startRealLocationTracking, stopRealLocationTracking, currentMode, isRunning, duration, distance, distanceToCheckpoint, isReach, stepCount, heartRate, currentSpeed, maxSpeed, get timer() {
        return timer;
      }, set timer(v) {
        timer = v;
      }, get accelerometerCallback() {
        return accelerometerCallback;
      }, set accelerometerCallback(v) {
        accelerometerCallback = v;
      }, get locationCallback() {
        return locationCallback;
      }, set locationCallback(v) {
        locationCallback = v;
      }, get h5LocationTimer() {
        return h5LocationTimer;
      }, set h5LocationTimer(v) {
        h5LocationTimer = v;
      }, policeTargetDistance, policeTargetPace, currentPace, currentSpeedKmh, avgSpeedKmh, getLocation, doGetLocation, searchCheckpoint, addCheckpointMarker, switchMode, get isStepActive() {
        return isStepActive;
      }, set isStepActive(v) {
        isStepActive = v;
      }, get lastStepTime() {
        return lastStepTime;
      }, set lastStepTime(v) {
        lastStepTime = v;
      }, STEP_THRESHOLD_UP, STEP_THRESHOLD_DOWN, MIN_STEP_INTERVAL, RESET_TIMEOUT, startStepCount, stopStepCount, updateHeartRate, startNormalRun, startPoliceRun, startCampusRun, stopRun, buildHistory, ref: vue.ref, computed: vue.computed, onUnmounted: vue.onUnmounted, get onShow() {
        return onShow;
      }, get onLoad() {
        return onLoad;
      }, AiChatRobot, CustomTabBar, get submitActivity() {
        return submitActivity;
      }, get getCheckpoints() {
        return getCheckpoints;
      }, get checkIn() {
        return checkIn;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$l(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "run" }, [
      vue.createElementVNode(
        "view",
        {
          class: "custom-navbar",
          style: vue.normalizeStyle({ paddingTop: $setup.statusBarHeight + "px" })
        },
        [
          vue.createElementVNode("view", { class: "navbar-content" }, [
            vue.createElementVNode("text", { class: "navbar-title" }, "跑步")
          ])
        ],
        4
        /* STYLE */
      ),
      vue.createElementVNode(
        "view",
        {
          class: "content-spacer",
          style: vue.normalizeStyle({ height: $setup.statusBarHeight + 44 + "px" })
        },
        null,
        4
        /* STYLE */
      ),
      vue.createVNode($setup["AiChatRobot"], {
        visible: $setup.showAiRobot,
        "onUpdate:visible": _cache[0] || (_cache[0] = ($event) => $setup.showAiRobot = $event),
        "run-data": $setup.currentRunData,
        onShare: $setup.handleShareToTeacher
      }, null, 8, ["visible", "run-data"]),
      $setup.isRunning || $setup.distance > 0 ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 0,
        class: "ai-float-btn",
        onClick: $setup.openAiRobot
      }, [
        vue.createElementVNode("text", { class: "ai-btn-icon" }, "🤖"),
        vue.createElementVNode("text", { class: "ai-btn-text" }, "AI助手")
      ])) : vue.createCommentVNode("v-if", true),
      vue.createElementVNode("view", { class: "top-widgets" }, [
        vue.createElementVNode("view", { class: "weather-widget" }, [
          vue.createElementVNode("view", { class: "weather-left" }, [
            vue.createElementVNode("text", { class: "weather-temp" }, "24°C"),
            vue.createElementVNode("text", { class: "weather-status" }, "☀️ 晴朗")
          ]),
          vue.createElementVNode("view", { class: "weather-right" }, [
            vue.createElementVNode("text", { class: "weather-tips" }, "空气优 · 适宜跑步")
          ])
        ]),
        vue.createElementVNode("scroll-view", {
          "scroll-x": "",
          class: "achievements-scroll",
          "show-scrollbar": false
        }, [
          (vue.openBlock(true), vue.createElementBlock(
            vue.Fragment,
            null,
            vue.renderList($setup.achievements, (badge, idx) => {
              return vue.openBlock(), vue.createElementBlock("view", {
                class: "badge-item",
                key: idx
              }, [
                vue.createElementVNode(
                  "text",
                  { class: "badge-icon" },
                  vue.toDisplayString(badge.icon),
                  1
                  /* TEXT */
                ),
                vue.createElementVNode(
                  "text",
                  { class: "badge-name" },
                  vue.toDisplayString(badge.name),
                  1
                  /* TEXT */
                )
              ]);
            }),
            128
            /* KEYED_FRAGMENT */
          ))
        ])
      ]),
      $setup.currentMode === "campus" ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 1,
        class: "search-bar"
      }, [
        vue.withDirectives(vue.createElementVNode(
          "input",
          {
            "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => $setup.checkpointName = $event),
            placeholder: "输入校园打卡点（如：操场/跑道）",
            class: "search-input"
          },
          null,
          512
          /* NEED_PATCH */
        ), [
          [vue.vModelText, $setup.checkpointName]
        ]),
        vue.createElementVNode("button", {
          onClick: $setup.searchCheckpoint,
          class: "search-btn"
        }, "搜索")
      ])) : vue.createCommentVNode("v-if", true),
      vue.createElementVNode("view", { class: "overview-card" }, [
        vue.createElementVNode("text", { class: "overview-title" }, "今日跑步概览"),
        vue.createElementVNode("view", { class: "overview-meta" }, [
          vue.createElementVNode(
            "text",
            null,
            "次数：" + vue.toDisplayString($setup.todayRunCount),
            1
            /* TEXT */
          ),
          vue.createElementVNode(
            "text",
            null,
            "里程：" + vue.toDisplayString($setup.todayRunDistance) + " km",
            1
            /* TEXT */
          )
        ]),
        $setup.teacherRunTask ? (vue.openBlock(), vue.createElementBlock(
          "text",
          {
            key: 0,
            class: "task-tip"
          },
          "教师任务：" + vue.toDisplayString($setup.teacherRunTask),
          1
          /* TEXT */
        )) : vue.createCommentVNode("v-if", true)
      ]),
      vue.createElementVNode("map", {
        class: "map",
        latitude: $setup.lat,
        longitude: $setup.lng,
        markers: $setup.markers,
        polyline: $setup.polyline
      }, null, 8, ["latitude", "longitude", "markers", "polyline"]),
      $setup.currentMode === "normal" ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 2,
        class: "routes-card"
      }, [
        vue.createElementVNode("view", {
          class: "card-header",
          onClick: $setup.toggleRoutes
        }, [
          vue.createElementVNode("text", { class: "card-title" }, "🏃 推荐路线"),
          vue.createElementVNode(
            "text",
            { class: "card-toggle" },
            vue.toDisplayString($setup.showRoutes ? "收起" : "展开"),
            1
            /* TEXT */
          )
        ]),
        $setup.showRoutes ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "routes-list"
        }, [
          (vue.openBlock(true), vue.createElementBlock(
            vue.Fragment,
            null,
            vue.renderList($setup.recommendRoutes, (route, idx) => {
              return vue.openBlock(), vue.createElementBlock("view", {
                class: "route-item",
                key: idx,
                onClick: ($event) => $setup.useRoute(route)
              }, [
                vue.createElementVNode("view", { class: "route-info" }, [
                  vue.createElementVNode(
                    "text",
                    { class: "route-name" },
                    vue.toDisplayString(route.name),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "route-meta" },
                    vue.toDisplayString(route.distance) + "km · " + vue.toDisplayString(route.difficulty),
                    1
                    /* TEXT */
                  )
                ]),
                vue.createElementVNode("text", { class: "route-action" }, "去跑步 >")
              ], 8, ["onClick"]);
            }),
            128
            /* KEYED_FRAGMENT */
          ))
        ])) : vue.createCommentVNode("v-if", true)
      ])) : vue.createCommentVNode("v-if", true),
      vue.createElementVNode("view", { class: "mode-switch" }, [
        vue.createElementVNode(
          "text",
          {
            class: vue.normalizeClass(["mode-item", { active: $setup.currentMode === "normal" }]),
            onClick: _cache[2] || (_cache[2] = ($event) => $setup.switchMode("normal"))
          },
          "普通跑步",
          2
          /* CLASS */
        ),
        vue.createElementVNode(
          "text",
          {
            class: vue.normalizeClass(["mode-item", { active: $setup.currentMode === "police" }]),
            onClick: _cache[3] || (_cache[3] = ($event) => $setup.switchMode("police"))
          },
          "专项测试",
          2
          /* CLASS */
        ),
        vue.createElementVNode(
          "text",
          {
            class: vue.normalizeClass(["mode-item", { active: $setup.currentMode === "campus" }]),
            onClick: _cache[4] || (_cache[4] = ($event) => $setup.switchMode("campus"))
          },
          "校园打卡",
          2
          /* CLASS */
        )
      ]),
      $setup.currentMode === "police" ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 3,
        class: "police-plan"
      }, [
        vue.createElementVNode("text", { class: "plan-title" }, "🎯 2000米体能专项训练"),
        vue.createElementVNode("view", { class: "plan-info" }, [
          vue.createElementVNode("text", { class: "info-item" }, [
            vue.createTextVNode("目标距离："),
            vue.createElementVNode(
              "span",
              { class: "highlight" },
              vue.toDisplayString($setup.policeTargetDistance / 1e3) + "公里",
              1
              /* TEXT */
            )
          ]),
          vue.createElementVNode("text", { class: "info-item" }, [
            vue.createTextVNode("达标配速："),
            vue.createElementVNode(
              "span",
              { class: "highlight" },
              vue.toDisplayString($setup.policeTargetPace) + "分钟/公里",
              1
              /* TEXT */
            )
          ]),
          vue.createElementVNode("text", { class: "info-item" }, [
            vue.createTextVNode("建议标准："),
            vue.createElementVNode("span", { class: "highlight" }, "可按学校或课程要求配置")
          ])
        ])
      ])) : vue.createCommentVNode("v-if", true),
      $setup.currentMode === "normal" ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 4,
        class: "run-mode-box"
      }, [
        !$setup.isRunning ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "start-box"
        }, [
          vue.createElementVNode("text", { class: "tip" }, "无地点/距离限制，自由记录跑步轨迹"),
          vue.createElementVNode("button", {
            onClick: $setup.startNormalRun,
            class: "start-btn"
          }, "开始跑步")
        ])) : (vue.openBlock(), vue.createElementBlock("view", {
          key: 1,
          class: "running-box"
        }, [
          vue.createElementVNode(
            "text",
            { class: "data" },
            "时长：" + vue.toDisplayString($setup.duration) + "秒 | 已跑：" + vue.toDisplayString((($setup.distance || 0) / 1e3).toFixed(2)) + "km | 速度：" + vue.toDisplayString($setup.currentSpeedKmh) + "km/h",
            1
            /* TEXT */
          ),
          vue.createElementVNode(
            "text",
            { class: "data" },
            "步数：" + vue.toDisplayString($setup.stepCount) + " | 心率：" + vue.toDisplayString($setup.heartRate) + "次/分 | 平均速度：" + vue.toDisplayString($setup.avgSpeedKmh) + "km/h",
            1
            /* TEXT */
          ),
          vue.createElementVNode("view", { class: "progress-wrap" }, [
            vue.createElementVNode("view", { class: "progress-bar" }, [
              vue.createElementVNode(
                "view",
                {
                  class: "progress-fill",
                  style: vue.normalizeStyle({ width: $setup.normalProgress + "%" })
                },
                null,
                4
                /* STYLE */
              )
            ]),
            vue.createElementVNode(
              "text",
              { class: "progress-text" },
              "今日目标 " + vue.toDisplayString($setup.dailyTarget) + " km · 完成 " + vue.toDisplayString((($setup.distance || 0) / 1e3).toFixed(2)) + " km",
              1
              /* TEXT */
            )
          ]),
          vue.createElementVNode("button", {
            onClick: $setup.stopRun,
            class: "stop-btn"
          }, "结束跑步")
        ]))
      ])) : vue.createCommentVNode("v-if", true),
      $setup.currentMode === "police" ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 5,
        class: "run-mode-box"
      }, [
        !$setup.isRunning ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "start-box"
        }, [
          vue.createElementVNode("text", { class: "tip" }, "按课程要求完成2000米跑，自动校验配速是否达标"),
          vue.createElementVNode("button", {
            onClick: $setup.startPoliceRun,
            class: "start-btn"
          }, "开始专项训练")
        ])) : (vue.openBlock(), vue.createElementBlock("view", {
          key: 1,
          class: "running-box"
        }, [
          vue.createElementVNode(
            "text",
            { class: "data" },
            "时长：" + vue.toDisplayString($setup.duration) + "秒 | 已跑：" + vue.toDisplayString(($setup.distance / 1e3).toFixed(2)) + "km / 目标：2km",
            1
            /* TEXT */
          ),
          vue.createElementVNode(
            "text",
            { class: "data" },
            "剩余：" + vue.toDisplayString((($setup.policeTargetDistance - $setup.distance) / 1e3).toFixed(2)) + "km | 配速：" + vue.toDisplayString($setup.currentPace.toFixed(1)) + "分钟/公里",
            1
            /* TEXT */
          ),
          vue.createElementVNode(
            "text",
            { class: "data" },
            "心率：" + vue.toDisplayString($setup.heartRate) + "次/分 | 步数：" + vue.toDisplayString($setup.stepCount),
            1
            /* TEXT */
          ),
          vue.createElementVNode(
            "text",
            {
              class: "pace-status",
              style: vue.normalizeStyle({ color: $setup.currentPace <= $setup.policeTargetPace ? "green" : "red" })
            },
            vue.toDisplayString($setup.currentPace <= $setup.policeTargetPace ? "✅ 配速达标" : "❌ 配速未达标"),
            5
            /* TEXT, STYLE */
          ),
          $setup.distance >= $setup.policeTargetDistance ? (vue.openBlock(), vue.createElementBlock("text", {
            key: 0,
            class: "finish-tip"
          }, "🎉 已完成2000米目标！")) : vue.createCommentVNode("v-if", true),
          vue.createElementVNode("view", { class: "progress-wrap" }, [
            vue.createElementVNode("view", { class: "progress-bar" }, [
              vue.createElementVNode(
                "view",
                {
                  class: "progress-fill",
                  style: vue.normalizeStyle({ width: $setup.policeProgress + "%" })
                },
                null,
                4
                /* STYLE */
              )
            ]),
            vue.createElementVNode(
              "text",
              { class: "progress-text" },
              "专项目标 2 km · 完成 " + vue.toDisplayString(($setup.distance / 1e3).toFixed(2)) + " km",
              1
              /* TEXT */
            )
          ]),
          vue.createElementVNode("button", {
            onClick: $setup.stopRun,
            class: "stop-btn"
          }, "结束训练")
        ]))
      ])) : vue.createCommentVNode("v-if", true),
      $setup.currentMode === "campus" ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 6,
        class: "run-mode-box"
      }, [
        !$setup.checkpoint.name ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "no-checkpoint"
        }, [
          vue.createElementVNode("text", { class: "tip" }, "请先搜索校园打卡点")
        ])) : (vue.openBlock(), vue.createElementBlock("view", { key: 1 }, [
          !$setup.isRunning ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 0,
            class: "start-box"
          }, [
            vue.createElementVNode(
              "text",
              { class: "checkpoint-info" },
              "打卡点：" + vue.toDisplayString($setup.checkpoint.name) + "（需到达10米内）",
              1
              /* TEXT */
            ),
            vue.createElementVNode("button", {
              onClick: $setup.startCampusRun,
              class: "start-btn"
            }, "开始打卡")
          ])) : (vue.openBlock(), vue.createElementBlock("view", {
            key: 1,
            class: "running-box"
          }, [
            vue.createElementVNode(
              "text",
              { class: "data" },
              "时长：" + vue.toDisplayString($setup.duration) + "秒 | 距打卡点：" + vue.toDisplayString($setup.distanceToCheckpoint) + "米 | 步数：" + vue.toDisplayString($setup.stepCount) + " | 心率：" + vue.toDisplayString($setup.heartRate) + "次/分",
              1
              /* TEXT */
            ),
            vue.createElementVNode(
              "text",
              {
                class: "reach-status",
                style: vue.normalizeStyle({ color: $setup.isReach ? "green" : "red" })
              },
              vue.toDisplayString($setup.isReach ? "✅ 已到达打卡点" : "❌ 未到达打卡点"),
              5
              /* TEXT, STYLE */
            ),
            vue.createElementVNode("button", {
              onClick: $setup.stopRun,
              class: "stop-btn"
            }, "结束打卡")
          ]))
        ]))
      ])) : vue.createCommentVNode("v-if", true),
      vue.createVNode($setup["CustomTabBar"], { current: "/pages/run/run" })
    ]);
  }
  const PagesRunRun = /* @__PURE__ */ _export_sfc(_sfc_main$m, [["render", _sfc_render$l], ["__scopeId", "data-v-8ae35d30"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue"]]);
  const _imports_0$1 = "/static/avatar.png";
  const _sfc_main$l = {
    __name: "mine",
    setup(__props, { expose: __expose }) {
      __expose();
      const statusBarHeight = vue.ref(20);
      const userName = vue.ref("同学");
      const userType = vue.ref("学生");
      const totalRunCount = vue.ref(12);
      const totalRunDistance = vue.ref(36.5);
      const policeSuccessCount = vue.ref(5);
      const weekDateRange = vue.ref("本周");
      const weekRunCount = vue.ref(1);
      const weekRunDistance = vue.ref(3);
      const weekPoliceSuccess = vue.ref(0);
      const progressPercent = vue.ref(33);
      const runRecords = vue.ref([
        {
          type: "run",
          modeBg: "#20C997",
          modeText: "跑步",
          createTime: "2023-10-25 18:30",
          distance: 3.02,
          duration: "00:18:45",
          pace: 6.2,
          statusText: "有效",
          statusColor: "#20C997"
        },
        {
          type: "test",
          modeBg: "#FF9F43",
          modeText: "体测",
          testName: "引体向上",
          createTime: "2023-10-24 16:20",
          testCount: 12,
          result: "优秀",
          statusText: "已上传",
          statusColor: "#20C997"
        }
      ]);
      const showRecords = vue.computed(() => runRecords.value.slice(0, 3));
      const deviceId = vue.ref("");
      onShow(() => {
        statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 20;
        const user = uni.getStorageSync("userInfo");
        if (user) {
          if (typeof user === "string") {
            try {
              const u = JSON.parse(user);
              if (u.name)
                userName.value = u.name;
            } catch (e) {
            }
          } else if (user.name) {
            userName.value = user.name;
          }
        }
      });
      const gotoUserProfile = () => {
        uni.showToast({ title: "编辑资料功能待开发", icon: "none" });
      };
      const viewAllRecords = () => {
        uni.showToast({ title: "查看全部记录待开发", icon: "none" });
      };
      const gotoRecordDetail = (item) => {
      };
      const gotoDeviceBind = () => {
        uni.showToast({ title: "设备绑定功能开发中", icon: "none" });
      };
      const clearCache = () => {
        uni.showModal({
          title: "提示",
          content: "确定要清除缓存吗？",
          success: (res) => {
            if (res.confirm) {
              uni.showToast({ title: "清理完成" });
            }
          }
        });
      };
      const gotoAbout = () => {
        uni.showToast({ title: "当前版本 v1.0.0", icon: "none" });
      };
      const logout = () => {
        uni.showModal({
          title: "提示",
          content: "确定要退出登录吗？",
          success: (res) => {
            if (res.confirm) {
              uni.removeStorageSync("token");
              uni.removeStorageSync("userInfo");
              uni.removeStorageSync("userRole");
              uni.reLaunch({ url: "/pages/login/login" });
            }
          }
        });
      };
      const __returned__ = { statusBarHeight, userName, userType, totalRunCount, totalRunDistance, policeSuccessCount, weekDateRange, weekRunCount, weekRunDistance, weekPoliceSuccess, progressPercent, runRecords, showRecords, deviceId, gotoUserProfile, viewAllRecords, gotoRecordDetail, gotoDeviceBind, clearCache, gotoAbout, logout, ref: vue.ref, computed: vue.computed, get onShow() {
        return onShow;
      }, CustomTabBar };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$k(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "mine-page" }, [
      vue.createElementVNode(
        "view",
        {
          class: "custom-navbar",
          style: vue.normalizeStyle({ paddingTop: $setup.statusBarHeight + "px" })
        },
        [
          vue.createElementVNode("view", { class: "navbar-content" }, [
            vue.createElementVNode("text", { class: "navbar-title" }, "个人中心")
          ])
        ],
        4
        /* STYLE */
      ),
      vue.createElementVNode(
        "view",
        {
          class: "content-wrapper",
          style: vue.normalizeStyle({ paddingTop: $setup.statusBarHeight + 44 + "px" })
        },
        [
          vue.createElementVNode("view", { class: "user-header" }, [
            vue.createElementVNode("view", { class: "avatar-box" }, [
              vue.createElementVNode("image", {
                class: "avatar",
                src: _imports_0$1,
                mode: "aspectFill"
              }),
              vue.createElementVNode("button", {
                class: "edit-avatar",
                onClick: $setup.gotoUserProfile
              }, "编辑资料")
            ]),
            vue.createElementVNode("view", { class: "user-info" }, [
              vue.createElementVNode(
                "text",
                { class: "username" },
                vue.toDisplayString($setup.userName),
                1
                /* TEXT */
              ),
              vue.createElementVNode(
                "text",
                { class: "user-desc" },
                "校园运动打卡 · " + vue.toDisplayString($setup.userType),
                1
                /* TEXT */
              )
            ]),
            vue.createElementVNode("view", { class: "user-stats" }, [
              vue.createElementVNode("view", { class: "stats-item" }, [
                vue.createElementVNode(
                  "text",
                  { class: "stats-num" },
                  vue.toDisplayString($setup.totalRunCount),
                  1
                  /* TEXT */
                ),
                vue.createElementVNode("text", { class: "stats-text" }, "总次数")
              ]),
              vue.createElementVNode("view", { class: "stats-item" }, [
                vue.createElementVNode(
                  "text",
                  { class: "stats-num" },
                  vue.toDisplayString($setup.totalRunDistance) + "km",
                  1
                  /* TEXT */
                ),
                vue.createElementVNode("text", { class: "stats-text" }, "总距离")
              ]),
              vue.createElementVNode("view", { class: "stats-item" }, [
                vue.createElementVNode(
                  "text",
                  { class: "stats-num" },
                  vue.toDisplayString($setup.policeSuccessCount),
                  1
                  /* TEXT */
                ),
                vue.createElementVNode("text", { class: "stats-text" }, "体测达标")
              ])
            ])
          ]),
          vue.createElementVNode("view", { class: "week-run-card" }, [
            vue.createElementVNode("view", { class: "card-header" }, [
              vue.createElementVNode("text", { class: "card-title" }, "本周跑步"),
              vue.createElementVNode(
                "text",
                { class: "date-range" },
                vue.toDisplayString($setup.weekDateRange),
                1
                /* TEXT */
              )
            ]),
            vue.createElementVNode("view", { class: "week-stats" }, [
              vue.createElementVNode("view", { class: "week-item" }, [
                vue.createElementVNode(
                  "text",
                  { class: "week-num" },
                  vue.toDisplayString($setup.weekRunCount),
                  1
                  /* TEXT */
                ),
                vue.createElementVNode("text", { class: "week-text" }, "跑步次数")
              ]),
              vue.createElementVNode("view", { class: "week-item" }, [
                vue.createElementVNode(
                  "text",
                  { class: "week-num" },
                  vue.toDisplayString($setup.weekRunDistance) + "km",
                  1
                  /* TEXT */
                ),
                vue.createElementVNode("text", { class: "week-text" }, "总距离")
              ]),
              vue.createElementVNode("view", { class: "week-item" }, [
                vue.createElementVNode(
                  "text",
                  { class: "week-num" },
                  vue.toDisplayString($setup.weekPoliceSuccess) + "次",
                  1
                  /* TEXT */
                ),
                vue.createElementVNode("text", { class: "week-text" }, "体测达标")
              ])
            ]),
            vue.createElementVNode("view", { class: "progress-box" }, [
              vue.createElementVNode(
                "text",
                { class: "progress-title" },
                "本周目标：跑步3次（完成" + vue.toDisplayString($setup.weekRunCount) + "/3）",
                1
                /* TEXT */
              ),
              vue.createElementVNode("view", { class: "progress-bar" }, [
                vue.createElementVNode(
                  "view",
                  {
                    class: "progress-fill",
                    style: vue.normalizeStyle({ width: $setup.progressPercent + "%" })
                  },
                  null,
                  4
                  /* STYLE */
                )
              ])
            ])
          ]),
          vue.createElementVNode("view", { class: "record-card" }, [
            vue.createElementVNode("view", { class: "card-header" }, [
              vue.createElementVNode("text", { class: "card-title" }, "运动记录"),
              vue.createElementVNode("button", {
                class: "view-all",
                onClick: $setup.viewAllRecords
              }, "查看全部")
            ]),
            $setup.runRecords.length > 0 ? (vue.openBlock(), vue.createElementBlock("view", {
              key: 0,
              class: "record-list"
            }, [
              (vue.openBlock(true), vue.createElementBlock(
                vue.Fragment,
                null,
                vue.renderList($setup.showRecords, (item, index) => {
                  return vue.openBlock(), vue.createElementBlock("view", {
                    class: "record-item",
                    key: index,
                    onClick: ($event) => $setup.gotoRecordDetail(item)
                  }, [
                    vue.createElementVNode(
                      "view",
                      {
                        class: "record-type",
                        style: vue.normalizeStyle({ backgroundColor: item.modeBg })
                      },
                      [
                        vue.createElementVNode(
                          "text",
                          { class: "type-text" },
                          vue.toDisplayString(item.modeText),
                          1
                          /* TEXT */
                        )
                      ],
                      4
                      /* STYLE */
                    ),
                    vue.createElementVNode("view", { class: "record-info" }, [
                      vue.createElementVNode(
                        "text",
                        { class: "record-date" },
                        vue.toDisplayString(item.createTime),
                        1
                        /* TEXT */
                      ),
                      item.type === "run" ? (vue.openBlock(), vue.createElementBlock("text", {
                        key: 0,
                        class: "record-data"
                      }, [
                        vue.createTextVNode(
                          vue.toDisplayString(item.distance) + "km | " + vue.toDisplayString(item.duration),
                          1
                          /* TEXT */
                        ),
                        item.pace ? (vue.openBlock(), vue.createElementBlock(
                          "text",
                          { key: 0 },
                          " | 配速：" + vue.toDisplayString(Number(item.pace).toFixed(1)) + " 分/公里",
                          1
                          /* TEXT */
                        )) : vue.createCommentVNode("v-if", true)
                      ])) : (vue.openBlock(), vue.createElementBlock(
                        "text",
                        {
                          key: 1,
                          class: "record-data"
                        },
                        vue.toDisplayString(item.testName) + " | 次数：" + vue.toDisplayString(item.testCount) + " | " + vue.toDisplayString(item.result),
                        1
                        /* TEXT */
                      ))
                    ]),
                    vue.createElementVNode("view", { class: "record-status" }, [
                      vue.createElementVNode(
                        "text",
                        {
                          class: "status-text",
                          style: vue.normalizeStyle({ color: item.statusColor })
                        },
                        vue.toDisplayString(item.statusText),
                        5
                        /* TEXT, STYLE */
                      )
                    ])
                  ], 8, ["onClick"]);
                }),
                128
                /* KEYED_FRAGMENT */
              ))
            ])) : (vue.openBlock(), vue.createElementBlock("view", {
              key: 1,
              class: "empty-record"
            }, [
              vue.createElementVNode("text", { class: "empty-icon" }, "🏃"),
              vue.createElementVNode("text", { class: "empty-text" }, "暂无运动记录，快去跑步打卡吧～")
            ]))
          ]),
          vue.createElementVNode("view", { class: "setting-card" }, [
            vue.createElementVNode("view", {
              class: "setting-item",
              onClick: $setup.gotoDeviceBind
            }, [
              vue.createElementVNode("text", { class: "setting-icon" }, "📱"),
              vue.createElementVNode("text", { class: "setting-text" }, "设备绑定（防代跑）"),
              vue.createElementVNode(
                "text",
                { class: "setting-desc" },
                vue.toDisplayString($setup.deviceId || "未绑定"),
                1
                /* TEXT */
              ),
              vue.createElementVNode("text", { class: "arrow" }, "＞")
            ]),
            vue.createElementVNode("view", {
              class: "setting-item",
              onClick: $setup.clearCache
            }, [
              vue.createElementVNode("text", { class: "setting-icon" }, "🗑️"),
              vue.createElementVNode("text", { class: "setting-text" }, "清除缓存"),
              vue.createElementVNode("text", { class: "setting-desc" }, "释放本地存储空间"),
              vue.createElementVNode("text", { class: "arrow" }, "＞")
            ]),
            vue.createElementVNode("view", {
              class: "setting-item",
              onClick: $setup.gotoAbout
            }, [
              vue.createElementVNode("text", { class: "setting-icon" }, "ℹ️"),
              vue.createElementVNode("text", { class: "setting-text" }, "关于我们"),
              vue.createElementVNode("text", { class: "setting-desc" }, "版本 v1.0.0"),
              vue.createElementVNode("text", { class: "arrow" }, "＞")
            ]),
            vue.createElementVNode("view", {
              class: "setting-item logout",
              onClick: $setup.logout
            }, [
              vue.createElementVNode("text", { class: "setting-icon" }, "🚪"),
              vue.createElementVNode("text", { class: "setting-text" }, "退出登录"),
              vue.createElementVNode("text", { class: "arrow" }, "＞")
            ])
          ])
        ],
        4
        /* STYLE */
      ),
      vue.createVNode($setup["CustomTabBar"], { current: "/pages/mine/mine" })
    ]);
  }
  const PagesMineMine = /* @__PURE__ */ _export_sfc(_sfc_main$l, [["render", _sfc_render$k], ["__scopeId", "data-v-7c2ebfa5"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/mine/mine.vue"]]);
  const _sfc_main$k = {
    __name: "result",
    setup(__props, { expose: __expose }) {
      __expose();
      const currentMode = vue.ref("normal");
      const duration = vue.ref(0);
      const distance = vue.ref(0);
      const isReach = vue.ref(false);
      const isPoliceFinish = vue.ref(false);
      const policePace = vue.ref(0);
      const testProject = vue.ref("");
      const testType = vue.ref("");
      const testCount = vue.ref(0);
      const testQualified = vue.ref(false);
      const standardReq = vue.ref(0);
      const userScorePercent = vue.ref(0);
      const standardScorePercent = vue.ref(0);
      const suggestionText = vue.ref("");
      const modeTitle = vue.computed(() => {
        switch (currentMode.value) {
          case "police":
            return "🎯 2000米专项体能结算";
          case "campus":
            return "🏫 校园打卡跑步结算";
          case "test":
            return "💪 体能测试结算";
          default:
            return "🏃 普通跑步结算";
        }
      });
      const modeBgColor = vue.computed(() => {
        switch (currentMode.value) {
          case "police":
            return "#fdf2f0";
          case "campus":
            return "#e8f4f8";
          case "test":
            return "#f3f7ff";
          default:
            return "#f5f5f5";
        }
      });
      const isPaceQualified = vue.computed(() => {
        return policePace.value <= 6.5;
      });
      onLoad((options) => {
        let data = null;
        if (options.useStorage === "true") {
          data = uni.getStorageSync("tempRunResult");
        } else if (options.data) {
          try {
            data = JSON.parse(decodeURIComponent(options.data));
          } catch (e) {
            formatAppLog("error", "at pages/result/result.vue:177", "Failed to parse result data", e);
          }
        }
        if (data) {
          currentMode.value = data.type === "test" ? "test" : "normal";
          if (data.metrics) {
            duration.value = data.metrics.duration || 0;
            distance.value = (data.metrics.distance || 0) * 1e3;
            testCount.value = data.metrics.count || 0;
            testQualified.value = data.metrics.qualified;
            policePace.value = Number(data.metrics.pace) || 0;
          }
          if (currentMode.value === "test") {
            testProject.value = "体测项目";
            testQualified.value = data.metrics.qualified;
            if (testQualified.value) {
              suggestionText.value = "恭喜达标！";
            } else {
              suggestionText.value = "继续加油！";
            }
          }
        } else {
          currentMode.value = options.mode || "normal";
          duration.value = Number(options.duration) || 0;
          distance.value = Number(options.distance) || 0;
          isReach.value = options.isReach === "true";
          isPoliceFinish.value = options.isPoliceFinish === "true";
          policePace.value = Number(options.policePace) || 0;
        }
      });
      const formatDuration = (seconds) => {
        const min = Math.floor(seconds / 60);
        const sec = seconds % 60;
        return `${min.toString().padStart(2, "0")}:${sec.toString().padStart(2, "0")}`;
      };
      const backToHome = () => {
        uni.reLaunch({ url: "/pages/home/home" });
      };
      const __returned__ = { currentMode, duration, distance, isReach, isPoliceFinish, policePace, testProject, testType, testCount, testQualified, standardReq, userScorePercent, standardScorePercent, suggestionText, modeTitle, modeBgColor, isPaceQualified, formatDuration, backToHome, ref: vue.ref, computed: vue.computed, get onShow() {
        return onShow;
      }, get onLoad() {
        return onLoad;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$j(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "result-page" }, [
      vue.createElementVNode(
        "view",
        {
          class: "mode-header",
          style: vue.normalizeStyle({ backgroundColor: $setup.modeBgColor })
        },
        [
          vue.createElementVNode(
            "text",
            { class: "mode-title" },
            vue.toDisplayString($setup.modeTitle),
            1
            /* TEXT */
          )
        ],
        4
        /* STYLE */
      ),
      vue.createElementVNode("view", { class: "result-card" }, [
        $setup.currentMode === "test" ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "base-data"
        }, [
          vue.createElementVNode(
            "text",
            { class: "base-title" },
            "测试项目：" + vue.toDisplayString($setup.testProject),
            1
            /* TEXT */
          ),
          vue.createElementVNode("view", { class: "data-item" }, [
            vue.createElementVNode("text", { class: "item-label" }, "完成数量"),
            vue.createElementVNode(
              "text",
              { class: "item-value count-text" },
              vue.toDisplayString($setup.testCount) + " 次",
              1
              /* TEXT */
            )
          ]),
          vue.createElementVNode("view", { class: "data-item" }, [
            vue.createElementVNode("text", { class: "item-label" }, "测试用时"),
            vue.createElementVNode(
              "text",
              { class: "item-value" },
              vue.toDisplayString($setup.formatDuration($setup.duration)),
              1
              /* TEXT */
            )
          ]),
          vue.createElementVNode("view", { class: "data-item" }, [
            vue.createElementVNode("text", { class: "item-label" }, "动作判定"),
            vue.createElementVNode(
              "text",
              {
                class: vue.normalizeClass(["item-value", $setup.testQualified ? "success" : "fail"])
              },
              vue.toDisplayString($setup.testQualified ? "✅ 合格" : "❌ 未合格"),
              3
              /* TEXT, CLASS */
            )
          ])
        ])) : vue.createCommentVNode("v-if", true),
        $setup.currentMode === "test" ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 1,
          class: "mode-data"
        }, [
          vue.createElementVNode("text", { class: "mode-data-title" }, "成绩分析"),
          vue.createElementVNode("view", { class: "bar-chart" }, [
            vue.createElementVNode("view", { class: "bar-row" }, [
              vue.createElementVNode("text", { class: "bar-label" }, "我的"),
              vue.createElementVNode("view", { class: "bar-track" }, [
                vue.createElementVNode(
                  "view",
                  {
                    class: "bar-fill user-fill",
                    style: vue.normalizeStyle({ width: $setup.userScorePercent + "%" })
                  },
                  null,
                  4
                  /* STYLE */
                ),
                $setup.userScorePercent > 15 ? (vue.openBlock(), vue.createElementBlock(
                  "text",
                  {
                    key: 0,
                    class: "bar-val-in"
                  },
                  vue.toDisplayString($setup.testCount),
                  1
                  /* TEXT */
                )) : vue.createCommentVNode("v-if", true)
              ]),
              $setup.userScorePercent <= 15 ? (vue.openBlock(), vue.createElementBlock(
                "text",
                {
                  key: 0,
                  class: "bar-val-out"
                },
                vue.toDisplayString($setup.testCount),
                1
                /* TEXT */
              )) : vue.createCommentVNode("v-if", true)
            ]),
            vue.createElementVNode("view", { class: "bar-row" }, [
              vue.createElementVNode("text", { class: "bar-label" }, "合格"),
              vue.createElementVNode("view", { class: "bar-track" }, [
                vue.createElementVNode(
                  "view",
                  {
                    class: "bar-fill standard-fill",
                    style: vue.normalizeStyle({ width: $setup.standardScorePercent + "%" })
                  },
                  null,
                  4
                  /* STYLE */
                ),
                $setup.standardScorePercent > 15 ? (vue.openBlock(), vue.createElementBlock(
                  "text",
                  {
                    key: 0,
                    class: "bar-val-in"
                  },
                  vue.toDisplayString($setup.standardReq),
                  1
                  /* TEXT */
                )) : vue.createCommentVNode("v-if", true)
              ]),
              $setup.standardScorePercent <= 15 ? (vue.openBlock(), vue.createElementBlock(
                "text",
                {
                  key: 0,
                  class: "bar-val-out"
                },
                vue.toDisplayString($setup.standardReq),
                1
                /* TEXT */
              )) : vue.createCommentVNode("v-if", true)
            ])
          ]),
          vue.createElementVNode("view", { class: "suggestion-box" }, [
            vue.createElementVNode("text", { class: "sugg-title" }, "💡 智能反馈"),
            vue.createElementVNode(
              "text",
              { class: "sugg-text" },
              vue.toDisplayString($setup.suggestionText),
              1
              /* TEXT */
            )
          ])
        ])) : (vue.openBlock(), vue.createElementBlock("view", {
          key: 2,
          class: "base-data"
        }, [
          vue.createElementVNode("text", { class: "base-title" }, "运动基础数据"),
          vue.createElementVNode("view", { class: "data-item" }, [
            vue.createElementVNode("text", { class: "item-label" }, "运动时长"),
            vue.createElementVNode(
              "text",
              { class: "item-value" },
              vue.toDisplayString($setup.formatDuration($setup.duration)),
              1
              /* TEXT */
            )
          ]),
          vue.createElementVNode("view", { class: "data-item" }, [
            vue.createElementVNode("text", { class: "item-label" }, "运动距离"),
            vue.createElementVNode(
              "text",
              { class: "item-value" },
              vue.toDisplayString(($setup.distance / 1e3).toFixed(2)) + " 公里",
              1
              /* TEXT */
            )
          ])
        ])),
        $setup.currentMode === "police" ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 3,
          class: "mode-data"
        }, [
          vue.createElementVNode("text", { class: "mode-data-title" }, "专项体能测试数据"),
          vue.createElementVNode("view", { class: "data-item" }, [
            vue.createElementVNode("text", { class: "item-label" }, "2000米目标完成"),
            vue.createElementVNode(
              "text",
              {
                class: vue.normalizeClass(["item-value", $setup.isPoliceFinish ? "success" : "fail"])
              },
              vue.toDisplayString($setup.isPoliceFinish ? "✅ 已完成" : "❌ 未完成"),
              3
              /* TEXT, CLASS */
            )
          ]),
          vue.createElementVNode("view", { class: "data-item" }, [
            vue.createElementVNode("text", { class: "item-label" }, "配速是否达标"),
            vue.createElementVNode(
              "text",
              {
                class: vue.normalizeClass(["item-value", $setup.isPaceQualified ? "success" : "fail"])
              },
              vue.toDisplayString($setup.isPaceQualified ? `✅ 达标（${$setup.policePace.toFixed(1)} 分/公里）` : `❌ 未达标（${$setup.policePace.toFixed(1)} 分/公里）`),
              3
              /* TEXT, CLASS */
            )
          ]),
          vue.createElementVNode("view", { class: "data-item tips" }, [
            vue.createElementVNode("text", { class: "item-label" }, "参考标准"),
            vue.createElementVNode("text", { class: "item-value" }, "可根据学校或课程体测标准配置")
          ])
        ])) : vue.createCommentVNode("v-if", true),
        $setup.currentMode === "campus" ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 4,
          class: "mode-data"
        }, [
          vue.createElementVNode("text", { class: "mode-data-title" }, "校园打卡数据"),
          vue.createElementVNode("view", { class: "data-item" }, [
            vue.createElementVNode("text", { class: "item-label" }, "打卡点到达状态"),
            vue.createElementVNode(
              "text",
              {
                class: vue.normalizeClass(["item-value", $setup.isReach ? "success" : "fail"])
              },
              vue.toDisplayString($setup.isReach ? "✅ 已到达" : "❌ 未到达"),
              3
              /* TEXT, CLASS */
            )
          ])
        ])) : vue.createCommentVNode("v-if", true),
        $setup.currentMode === "normal" ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 5,
          class: "mode-data"
        }, [
          vue.createElementVNode("text", { class: "mode-data-title" }, "普通跑步数据"),
          vue.createElementVNode("view", { class: "data-item tips" }, [
            vue.createElementVNode("text", { class: "item-label" }, "温馨提示"),
            vue.createElementVNode("text", { class: "item-value" }, "数据已自动记录，可在「我的」页面查看汇总")
          ])
        ])) : vue.createCommentVNode("v-if", true)
      ]),
      vue.createElementVNode("view", { class: "btn-group" }, [
        vue.createElementVNode("button", {
          class: "save-btn",
          disabled: ""
        }, " ✅ 数据已保存 "),
        vue.createElementVNode("button", {
          onClick: $setup.backToHome,
          class: "back-btn"
        }, "返回首页")
      ])
    ]);
  }
  const PagesResultResult = /* @__PURE__ */ _export_sfc(_sfc_main$k, [["render", _sfc_render$j], ["__scopeId", "data-v-b615976f"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/result/result.vue"]]);
  const _sfc_main$j = {
    __name: "login",
    setup(__props, { expose: __expose }) {
      __expose();
      const currentRole = vue.ref("student");
      const loading = vue.ref(false);
      const loginForm = vue.ref({
        account: "",
        password: ""
      });
      const canSubmit = vue.computed(() => {
        return loginForm.value.account.length > 0 && loginForm.value.password.length > 0;
      });
      const validateForm = () => {
        const { account, password } = loginForm.value;
        if (password.length < 6) {
          uni.showToast({ title: "密码长度不能少于6位", icon: "none" });
          return false;
        }
        return true;
      };
      const handleLogin = async () => {
        if (!canSubmit.value)
          return;
        if (!validateForm())
          return;
        loading.value = true;
        try {
          const res = await login({
            phone: loginForm.value.account,
            password: loginForm.value.password
          });
          if (res.role !== currentRole.value) {
            uni.showToast({
              title: "角色不匹配，请切换角色登录",
              icon: "none"
            });
            loading.value = false;
            return;
          }
          const userInfo = {
            userId: res.user_id,
            role: res.role,
            name: res.name,
            phone: loginForm.value.account,
            // 兼容字段
            schoolId: "10001",
            isPoliceSchool: false
          };
          uni.setStorageSync("token", res.access_token);
          uni.setStorageSync("userInfo", userInfo);
          uni.setStorageSync("userRole", res.role);
          uni.showToast({
            title: "登录成功",
            icon: "success"
          });
          setTimeout(() => {
            if (currentRole.value === "student") {
              uni.redirectTo({ url: "/pages/home/home" });
            } else {
              uni.redirectTo({ url: "/pages/teacher/home/home" });
            }
          }, 1e3);
        } catch (error) {
          formatAppLog("error", "at pages/login/login.vue:162", "Login failed:", error);
        } finally {
          loading.value = false;
        }
      };
      const goToRegister = () => {
        uni.navigateTo({ url: "/pages/register/register" });
      };
      const forgotPassword = () => {
        uni.showToast({ title: "请联系管理员重置密码", icon: "none" });
      };
      const __returned__ = { currentRole, loading, loginForm, canSubmit, validateForm, handleLogin, goToRegister, forgotPassword, ref: vue.ref, computed: vue.computed, get login() {
        return login;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$i(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "login-container" }, [
      vue.createElementVNode("view", { class: "header-section" }, [
        vue.createElementVNode("view", { class: "logo-circle" }, [
          vue.createElementVNode("text", { class: "logo-text" }, "校")
        ]),
        vue.createElementVNode("text", { class: "app-name" }, "大学生运动健康管理平台"),
        vue.createElementVNode("text", { class: "app-sub-name" }, "Professional Sports Management System")
      ]),
      vue.createElementVNode("view", { class: "login-card" }, [
        vue.createElementVNode("view", { class: "role-tabs" }, [
          vue.createElementVNode(
            "view",
            {
              class: vue.normalizeClass(["role-tab", { active: $setup.currentRole === "student" }]),
              onClick: _cache[0] || (_cache[0] = ($event) => $setup.currentRole = "student")
            },
            [
              vue.createElementVNode("text", null, "学生端")
            ],
            2
            /* CLASS */
          ),
          vue.createElementVNode(
            "view",
            {
              class: vue.normalizeClass(["role-tab", { active: $setup.currentRole === "teacher" }]),
              onClick: _cache[1] || (_cache[1] = ($event) => $setup.currentRole = "teacher")
            },
            [
              vue.createElementVNode("text", null, "教师端")
            ],
            2
            /* CLASS */
          )
        ]),
        vue.createElementVNode("view", { class: "form-area" }, [
          vue.createElementVNode("view", { class: "input-group" }, [
            vue.createElementVNode(
              "text",
              { class: "input-label" },
              vue.toDisplayString($setup.currentRole === "student" ? "学号 / 手机号" : "工号 / 手机号"),
              1
              /* TEXT */
            ),
            vue.withDirectives(vue.createElementVNode("input", {
              class: "input-field",
              "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $setup.loginForm.account = $event),
              placeholder: $setup.currentRole === "student" ? "请输入学号/手机号" : "请输入工号/手机号",
              "placeholder-class": "placeholder-style"
            }, null, 8, ["placeholder"]), [
              [vue.vModelText, $setup.loginForm.account]
            ])
          ]),
          vue.createElementVNode("view", { class: "input-group" }, [
            vue.createElementVNode("text", { class: "input-label" }, "密码"),
            vue.withDirectives(vue.createElementVNode(
              "input",
              {
                class: "input-field",
                "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $setup.loginForm.password = $event),
                type: "password",
                placeholder: "请输入密码",
                "placeholder-class": "placeholder-style"
              },
              null,
              512
              /* NEED_PATCH */
            ), [
              [vue.vModelText, $setup.loginForm.password]
            ])
          ]),
          vue.createElementVNode("button", {
            class: vue.normalizeClass(["submit-btn", { disabled: !$setup.canSubmit }]),
            onClick: $setup.handleLogin,
            loading: $setup.loading
          }, " 登录 ", 10, ["loading"]),
          vue.createElementVNode("view", { class: "footer-links" }, [
            vue.createElementVNode("text", {
              class: "link-text",
              onClick: $setup.goToRegister
            }, "注册新账号"),
            vue.createElementVNode("text", { class: "divider" }, "|"),
            vue.createElementVNode("text", {
              class: "link-text",
              onClick: $setup.forgotPassword
            }, "忘记密码？")
          ])
        ])
      ]),
      vue.createElementVNode("view", { class: "copyright" }, [
        vue.createElementVNode("text", null, "Copyright © 2026 Campus Sports System")
      ])
    ]);
  }
  const PagesLoginLogin = /* @__PURE__ */ _export_sfc(_sfc_main$j, [["render", _sfc_render$i], ["__scopeId", "data-v-e4e4508d"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/login/login.vue"]]);
  const _sfc_main$i = {
    __name: "register",
    setup(__props, { expose: __expose }) {
      __expose();
      const step = vue.ref(1);
      const loading = vue.ref(false);
      const registerForm = vue.ref({
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
        uni.navigateBack();
      };
      const getCode = () => {
        if (!registerForm.value.phone) {
          uni.showToast({ title: "请先输入手机号", icon: "none" });
          return;
        }
        const phoneRegex = /^1[3-9]\d{9}$/;
        if (!phoneRegex.test(registerForm.value.phone)) {
          uni.showToast({ title: "手机号格式不正确", icon: "none" });
          return;
        }
        uni.showToast({ title: "验证码已发送", icon: "success" });
      };
      const handleRegister = async () => {
        const form = registerForm.value;
        if (!form.name || !form.phone || !form.password) {
          uni.showToast({ title: "请完善基础信息", icon: "none" });
          return;
        }
        const phoneRegex = /^1[3-9]\d{9}$/;
        if (!phoneRegex.test(form.phone)) {
          uni.showToast({ title: "请输入正确的手机号", icon: "none" });
          return;
        }
        if (form.password.length < 6) {
          uni.showToast({ title: "密码长度不能少于6位", icon: "none" });
          return;
        }
        if (form.password !== form.confirmPwd) {
          uni.showToast({ title: "两次密码不一致", icon: "none" });
          return;
        }
        if (form.role === "student" && (!form.school || !form.class)) {
          uni.showToast({ title: "请完善学生信息", icon: "none" });
          return;
        }
        if (form.role === "teacher" && (!form.empId || !form.department)) {
          uni.showToast({ title: "请完善教师信息", icon: "none" });
          return;
        }
        loading.value = true;
        try {
          await register({
            phone: form.phone,
            name: form.name,
            role: form.role,
            password: form.password
          });
          uni.showToast({
            title: "注册成功",
            icon: "success"
          });
          setTimeout(() => {
            uni.navigateBack();
          }, 1500);
        } catch (error) {
          formatAppLog("error", "at pages/register/register.vue:228", "Register failed:", error);
        } finally {
          loading.value = false;
        }
      };
      const __returned__ = { step, loading, registerForm, selectRole, nextStep, togglePolice, goToLogin, getCode, handleRegister, ref: vue.ref, get register() {
        return register;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$h(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "register-container" }, [
      vue.createElementVNode("view", { class: "header-section" }, [
        vue.createElementVNode("text", { class: "title" }, "注册新账号"),
        vue.createElementVNode("text", { class: "sub-title" }, "加入校园运动健康平台")
      ]),
      vue.createElementVNode("view", { class: "register-card" }, [
        $setup.step === 1 ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "role-select-box"
        }, [
          vue.createElementVNode("text", { class: "step-title" }, "请选择您的身份"),
          vue.createElementVNode("view", { class: "role-options" }, [
            vue.createElementVNode(
              "view",
              {
                class: vue.normalizeClass(["role-option", { active: $setup.registerForm.role === "student" }]),
                onClick: _cache[0] || (_cache[0] = ($event) => $setup.selectRole("student"))
              },
              [
                vue.createElementVNode("text", { class: "role-icon" }, "👨‍🎓"),
                vue.createElementVNode("text", { class: "role-name" }, "我是学生")
              ],
              2
              /* CLASS */
            ),
            vue.createElementVNode(
              "view",
              {
                class: vue.normalizeClass(["role-option", { active: $setup.registerForm.role === "teacher" }]),
                onClick: _cache[1] || (_cache[1] = ($event) => $setup.selectRole("teacher"))
              },
              [
                vue.createElementVNode("text", { class: "role-icon" }, "👨‍🏫"),
                vue.createElementVNode("text", { class: "role-name" }, "我是教师")
              ],
              2
              /* CLASS */
            )
          ]),
          vue.createElementVNode("button", {
            class: "next-btn",
            onClick: $setup.nextStep
          }, "下一步")
        ])) : (vue.openBlock(), vue.createElementBlock("view", {
          key: 1,
          class: "form-box"
        }, [
          vue.createElementVNode("view", { class: "form-header" }, [
            vue.createElementVNode("text", {
              class: "back-text",
              onClick: _cache[2] || (_cache[2] = ($event) => $setup.step = 1)
            }, "返回修改身份"),
            vue.createElementVNode(
              "text",
              { class: "current-role" },
              "当前身份：" + vue.toDisplayString($setup.registerForm.role === "student" ? "学生" : "教师"),
              1
              /* TEXT */
            )
          ]),
          vue.createElementVNode("view", { class: "section-title" }, "基础信息"),
          vue.createElementVNode("view", { class: "input-item" }, [
            vue.withDirectives(vue.createElementVNode(
              "input",
              {
                class: "input",
                "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $setup.registerForm.name = $event),
                placeholder: "真实姓名"
              },
              null,
              512
              /* NEED_PATCH */
            ), [
              [vue.vModelText, $setup.registerForm.name]
            ])
          ]),
          vue.createElementVNode("view", { class: "input-item" }, [
            vue.withDirectives(vue.createElementVNode(
              "input",
              {
                class: "input",
                "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $setup.registerForm.phone = $event),
                type: "number",
                placeholder: "手机号码"
              },
              null,
              512
              /* NEED_PATCH */
            ), [
              [vue.vModelText, $setup.registerForm.phone]
            ])
          ]),
          vue.createElementVNode("view", { class: "input-item code-box" }, [
            vue.withDirectives(vue.createElementVNode(
              "input",
              {
                class: "input",
                "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => $setup.registerForm.code = $event),
                type: "number",
                placeholder: "验证码"
              },
              null,
              512
              /* NEED_PATCH */
            ), [
              [vue.vModelText, $setup.registerForm.code]
            ]),
            vue.createElementVNode("text", {
              class: "get-code",
              onClick: $setup.getCode
            }, "获取验证码")
          ]),
          vue.createElementVNode("view", { class: "input-item" }, [
            vue.withDirectives(vue.createElementVNode(
              "input",
              {
                class: "input",
                "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $setup.registerForm.password = $event),
                type: "password",
                placeholder: "设置密码 (6-16位)"
              },
              null,
              512
              /* NEED_PATCH */
            ), [
              [vue.vModelText, $setup.registerForm.password]
            ])
          ]),
          vue.createElementVNode("view", { class: "input-item" }, [
            vue.withDirectives(vue.createElementVNode(
              "input",
              {
                class: "input",
                "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => $setup.registerForm.confirmPwd = $event),
                type: "password",
                placeholder: "确认密码"
              },
              null,
              512
              /* NEED_PATCH */
            ), [
              [vue.vModelText, $setup.registerForm.confirmPwd]
            ])
          ]),
          vue.createElementVNode("view", { class: "section-title" }, "身份信息"),
          $setup.registerForm.role === "student" ? (vue.openBlock(), vue.createElementBlock(
            vue.Fragment,
            { key: 0 },
            [
              vue.createElementVNode("view", { class: "input-item" }, [
                vue.withDirectives(vue.createElementVNode(
                  "input",
                  {
                    class: "input",
                    "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => $setup.registerForm.school = $event),
                    placeholder: "学校名称"
                  },
                  null,
                  512
                  /* NEED_PATCH */
                ), [
                  [vue.vModelText, $setup.registerForm.school]
                ])
              ]),
              vue.createElementVNode("view", { class: "input-item" }, [
                vue.withDirectives(vue.createElementVNode(
                  "input",
                  {
                    class: "input",
                    "onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => $setup.registerForm.college = $event),
                    placeholder: "所属学院"
                  },
                  null,
                  512
                  /* NEED_PATCH */
                ), [
                  [vue.vModelText, $setup.registerForm.college]
                ])
              ]),
              vue.createElementVNode("view", { class: "input-item" }, [
                vue.withDirectives(vue.createElementVNode(
                  "input",
                  {
                    class: "input",
                    "onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => $setup.registerForm.major = $event),
                    placeholder: "专业"
                  },
                  null,
                  512
                  /* NEED_PATCH */
                ), [
                  [vue.vModelText, $setup.registerForm.major]
                ])
              ]),
              vue.createElementVNode("view", { class: "input-item" }, [
                vue.withDirectives(vue.createElementVNode(
                  "input",
                  {
                    class: "input",
                    "onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => $setup.registerForm.class = $event),
                    placeholder: "班级 (如: 22级3班)"
                  },
                  null,
                  512
                  /* NEED_PATCH */
                ), [
                  [vue.vModelText, $setup.registerForm.class]
                ])
              ])
            ],
            64
            /* STABLE_FRAGMENT */
          )) : vue.createCommentVNode("v-if", true),
          $setup.registerForm.role === "teacher" ? (vue.openBlock(), vue.createElementBlock(
            vue.Fragment,
            { key: 1 },
            [
              vue.createElementVNode("view", { class: "input-item" }, [
                vue.withDirectives(vue.createElementVNode(
                  "input",
                  {
                    class: "input",
                    "onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => $setup.registerForm.school = $event),
                    placeholder: "学校名称"
                  },
                  null,
                  512
                  /* NEED_PATCH */
                ), [
                  [vue.vModelText, $setup.registerForm.school]
                ])
              ]),
              vue.createElementVNode("view", { class: "input-item" }, [
                vue.withDirectives(vue.createElementVNode(
                  "input",
                  {
                    class: "input",
                    "onUpdate:modelValue": _cache[13] || (_cache[13] = ($event) => $setup.registerForm.empId = $event),
                    placeholder: "教师工号"
                  },
                  null,
                  512
                  /* NEED_PATCH */
                ), [
                  [vue.vModelText, $setup.registerForm.empId]
                ])
              ]),
              vue.createElementVNode("view", { class: "input-item" }, [
                vue.withDirectives(vue.createElementVNode(
                  "input",
                  {
                    class: "input",
                    "onUpdate:modelValue": _cache[14] || (_cache[14] = ($event) => $setup.registerForm.department = $event),
                    placeholder: "所属部门 (如: 警体教研室)"
                  },
                  null,
                  512
                  /* NEED_PATCH */
                ), [
                  [vue.vModelText, $setup.registerForm.department]
                ])
              ])
            ],
            64
            /* STABLE_FRAGMENT */
          )) : vue.createCommentVNode("v-if", true),
          vue.createElementVNode("view", { class: "police-switch-box" }, [
            vue.createElementVNode("view", { class: "switch-header" }, [
              vue.createElementVNode("text", { class: "switch-label" }, "警校/军校用户"),
              vue.createElementVNode("switch", {
                checked: $setup.registerForm.isPoliceSchool,
                onChange: $setup.togglePolice,
                color: "#20C997",
                style: { "transform": "scale(0.8)" }
              }, null, 40, ["checked"])
            ]),
            $setup.registerForm.isPoliceSchool ? (vue.openBlock(), vue.createElementBlock("text", {
              key: 0,
              class: "switch-tip"
            }, " * 勾选后，系统将开启适配警校/军校体测标准的专项训练模块 ")) : vue.createCommentVNode("v-if", true)
          ]),
          vue.createElementVNode("button", {
            class: "submit-btn",
            onClick: $setup.handleRegister,
            loading: $setup.loading
          }, "立即注册", 8, ["loading"])
        ])),
        vue.createElementVNode("view", { class: "footer-link" }, [
          vue.createElementVNode("text", {
            class: "link-text",
            onClick: $setup.goToLogin
          }, "已有账号？返回登录")
        ])
      ])
    ]);
  }
  const PagesRegisterRegister = /* @__PURE__ */ _export_sfc(_sfc_main$i, [["render", _sfc_render$h], ["__scopeId", "data-v-bac4a35d"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/register/register.vue"]]);
  const currentTab = "/pages/test/test";
  const _sfc_main$h = {
    __name: "test",
    setup(__props, { expose: __expose }) {
      __expose();
      const statusBarHeight = vue.ref(20);
      const cameraContext = vue.ref(null);
      const captureTimer = vue.ref(null);
      const tabList = vue.computed(() => {
        return role.value === "teacher" ? [
          { pagePath: "/pages/teacher/home/home", text: "主页", iconPath: "/static/tab/home.png", selectedIconPath: "/static/tab/home-active.png" },
          { pagePath: "/pages/teacher/manage/manage", text: "管理", iconPath: "/static/tab/run.png", selectedIconPath: "/static/tab/run-active.png" },
          { pagePath: "/pages/teacher/mine/mine", text: "我的", iconPath: "/static/tab/mine.png", selectedIconPath: "/static/tab/mine-active.png" }
        ] : [
          { pagePath: "/pages/home/home", text: "首页", iconPath: "/static/tab/home.png", selectedIconPath: "/static/tab/home-active.png" },
          { pagePath: "/pages/run/run", text: "跑步", iconPath: "/static/tab/run.png", selectedIconPath: "/static/tab/run-active.png" },
          { pagePath: "/pages/test/test", text: "体测", iconPath: "/static/tab/test.png", selectedIconPath: "/static/tab/test-active.png" },
          { pagePath: "/pages/mine/mine", text: "我的", iconPath: "/static/tab/mine.png", selectedIconPath: "/static/tab/mine-active.png" }
        ];
      });
      const switchTab = (item) => {
        if (item.pagePath === currentTab)
          return;
        uni.redirectTo({ url: item.pagePath });
      };
      const projectName = vue.ref("引体向上");
      const standardDesc = vue.ref("下颌过杠，双臂伸直");
      const testType = vue.ref("pull-up");
      const role = vue.ref("student");
      onShow(() => {
        const userRole = uni.getStorageSync("userRole") || "student";
        role.value = userRole;
      });
      const isTesting = vue.ref(false);
      const count = vue.ref(0);
      const duration = vue.ref(0);
      const timer = vue.ref(null);
      const isStandard = vue.ref(true);
      const statusText = vue.ref("准备就绪");
      const showGuide = vue.ref(false);
      const targetCount = vue.ref(10);
      const projectEmoji = vue.computed(() => {
        const map = {
          "pull-up": "💪",
          "sit-up": "🧘",
          "push-up": "🤸",
          "run-1000": "🏃",
          "run-800": "🏃‍♀️"
        };
        return map[testType.value] || "🏋️";
      });
      const progressPercent = vue.computed(() => {
        return Math.min(count.value / targetCount.value * 100, 100);
      });
      const handleOptions = (options) => {
        if (options.project)
          projectName.value = options.project;
        if (options.type)
          testType.value = options.type;
        const standards = {
          "引体向上": "下颌过杠，双臂伸直",
          "仰卧起坐": "双手抱头，肘部触膝",
          "俯卧撑": "身体平直，屈臂90度"
        };
        const targets = {
          "引体向上": 10,
          "仰卧起坐": 40,
          "俯卧撑": 30
        };
        if (standards[projectName.value]) {
          standardDesc.value = standards[projectName.value];
        }
        if (targets[projectName.value]) {
          targetCount.value = targets[projectName.value];
        }
      };
      onLoad((options) => {
        const sys = uni.getSystemInfoSync();
        statusBarHeight.value = sys.statusBarHeight || 20;
        if (options) {
          handleOptions(options);
        }
      });
      onShow(() => {
        const r = uni.getStorageSync("userRole") || uni.getStorageSync("role");
        if (r)
          role.value = r;
        const storedProject = uni.getStorageSync("testProject");
        const storedType = uni.getStorageSync("testType");
        if (storedProject) {
          handleOptions({ project: storedProject, type: storedType });
          uni.removeStorageSync("testProject");
          uni.removeStorageSync("testType");
          uni.showToast({ title: "已清理传参缓存", icon: "none" });
        }
      });
      const showSelector = vue.ref(false);
      const showTypeSelector = () => {
        showSelector.value = !showSelector.value;
      };
      const switchTestType = (project, type) => {
        handleOptions({ project, type });
        showSelector.value = false;
      };
      const formatTime = (seconds) => {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
      };
      const startTest = () => {
        isTesting.value = true;
        count.value = 0;
        duration.value = 0;
        statusText.value = "正在识别动作...";
        timer.value = setInterval(() => {
          duration.value++;
        }, 1e3);
        const ctx = uni.createCameraContext();
        cameraContext.value = ctx;
        captureTimer.value = setInterval(() => {
          ctx.takePhoto({
            quality: "low",
            success: (res) => {
              formatAppLog("log", "at pages/test/test.vue:341", "Capture success:", res.tempImagePath);
              uploadSnapshot(res.tempImagePath);
            },
            fail: (err) => {
              formatAppLog("error", "at pages/test/test.vue:347", "Capture failed:", err);
            }
          });
        }, 3e3);
      };
      const uploadSnapshot = (filePath) => {
        uni.uploadFile({
          url: `${BASE_URL}/upload`,
          filePath,
          name: "file",
          header: {
            "Authorization": `Bearer ${uni.getStorageSync("token")}`
          },
          success: (uploadRes) => {
            formatAppLog("log", "at pages/test/test.vue:363", "Upload result:", uploadRes.data);
            try {
              const data = JSON.parse(uploadRes.data);
              if (data.url) {
                formatAppLog("log", "at pages/test/test.vue:367", "Uploaded successfully:", data.url);
              }
            } catch (e) {
              formatAppLog("error", "at pages/test/test.vue:370", "Parse error", e);
            }
          },
          fail: (err) => {
            formatAppLog("error", "at pages/test/test.vue:374", "Upload failed:", err);
          }
        });
      };
      const mockCount = () => {
        count.value++;
        statusText.value = "动作标准 ✅";
        setTimeout(() => {
          statusText.value = "正在识别动作...";
        }, 800);
      };
      const endTest = () => {
        clearInterval(timer.value);
        if (captureTimer.value) {
          clearInterval(captureTimer.value);
          captureTimer.value = null;
        }
        isTesting.value = false;
        uni.showModal({
          title: "测试结束",
          content: `共完成 ${count.value} 次，用时 ${formatTime(duration.value)}，是否提交成绩？`,
          confirmText: "提交结果",
          cancelText: "放弃",
          success: (res) => {
            if (res.confirm) {
              submitResult();
            } else {
              count.value = 0;
              duration.value = 0;
              statusText.value = "准备就绪";
            }
          }
        });
      };
      const submitResult = () => {
        uni.showLoading({ title: "正在提交成绩..." });
        ({
          mode: "test",
          testProject: projectName.value,
          count: count.value,
          duration: duration.value,
          isStandard: true,
          testDate: (/* @__PURE__ */ new Date()).getTime()
        });
        setTimeout(() => {
          uni.hideLoading();
          uni.navigateTo({
            url: `/pages/result/result?mode=test&project=${projectName.value}&count=${count.value}&duration=${duration.value}`
          });
        }, 1e3);
      };
      const gotoStudents = () => {
        uni.navigateTo({ url: "/pages/teacher/students/students" });
      };
      const handleCameraError = (e) => {
        formatAppLog("error", "at pages/test/test.vue:444", "Camera Error:", e);
        let msg = "无法访问摄像头";
        if (e.name === "NotAllowedError" || e.message === "Permission denied") {
          msg = "权限被拒绝，请允许摄像头访问";
        } else if (e.name === "NotFoundError") {
          msg = "未检测到摄像头";
        }
        uni.showToast({
          title: msg,
          icon: "none",
          duration: 3e3
        });
      };
      const __returned__ = { statusBarHeight, cameraContext, captureTimer, currentTab, tabList, switchTab, projectName, standardDesc, testType, role, isTesting, count, duration, timer, isStandard, statusText, showGuide, targetCount, projectEmoji, progressPercent, handleOptions, showSelector, showTypeSelector, switchTestType, formatTime, startTest, uploadSnapshot, mockCount, endTest, submitResult, gotoStudents, handleCameraError, ref: vue.ref, computed: vue.computed, onMounted: vue.onMounted, onUnmounted: vue.onUnmounted, get onLoad() {
        return onLoad;
      }, get onShow() {
        return onShow;
      }, get BASE_URL() {
        return BASE_URL;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$g(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "test-page-root" }, [
      vue.createElementVNode(
        "view",
        {
          class: "custom-navbar",
          style: vue.normalizeStyle({ paddingTop: $setup.statusBarHeight + "px" })
        },
        [
          vue.createElementVNode("view", { class: "navbar-content" }, [
            vue.createElementVNode("text", { class: "navbar-title" }, "体能测试")
          ])
        ],
        4
        /* STYLE */
      ),
      vue.createElementVNode(
        "view",
        {
          class: "content-wrapper",
          style: vue.normalizeStyle({ paddingTop: $setup.statusBarHeight + 44 + "px" })
        },
        [
          $setup.role === "teacher" ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 0,
            class: "teacher-tools"
          }, [
            vue.createElementVNode("view", { class: "teacher-card" }, [
              vue.createElementVNode("text", { class: "teacher-title" }, "教师工具"),
              vue.createElementVNode("view", { class: "teacher-actions" }, [
                vue.createElementVNode("button", {
                  class: "teacher-btn",
                  onClick: $setup.gotoStudents
                }, "学员管理")
              ])
            ])
          ])) : (vue.openBlock(), vue.createElementBlock("view", {
            key: 1,
            class: "student-container"
          }, [
            vue.createElementVNode("view", { class: "header-info" }, [
              vue.createElementVNode(
                "text",
                { class: "project-name" },
                vue.toDisplayString($setup.projectName),
                1
                /* TEXT */
              ),
              vue.createElementVNode("view", { class: "standard-badge" }, [
                vue.createElementVNode("text", { class: "badge-text" }, "国家学生体质健康标准")
              ]),
              vue.createElementVNode(
                "text",
                { class: "standard-desc" },
                "动作标准：" + vue.toDisplayString($setup.standardDesc),
                1
                /* TEXT */
              ),
              vue.createElementVNode("view", { class: "project-icon-wrapper" }, [
                vue.createElementVNode(
                  "text",
                  { class: "project-emoji" },
                  vue.toDisplayString($setup.projectEmoji),
                  1
                  /* TEXT */
                )
              ]),
              vue.createElementVNode("view", { class: "test-type-switch" }, [
                vue.createElementVNode("button", {
                  class: "switch-btn",
                  onClick: $setup.showTypeSelector
                }, "切换测试类型"),
                $setup.showSelector ? (vue.openBlock(), vue.createElementBlock("view", {
                  key: 0,
                  class: "type-selector"
                }, [
                  vue.createElementVNode("view", {
                    class: "type-item",
                    onClick: _cache[0] || (_cache[0] = ($event) => $setup.switchTestType("引体向上", "pull-up"))
                  }, "引体向上"),
                  vue.createElementVNode("view", {
                    class: "type-item",
                    onClick: _cache[1] || (_cache[1] = ($event) => $setup.switchTestType("仰卧起坐", "sit-up"))
                  }, "仰卧起坐"),
                  vue.createElementVNode("view", {
                    class: "type-item",
                    onClick: _cache[2] || (_cache[2] = ($event) => $setup.switchTestType("俯卧撑", "push-up"))
                  }, "俯卧撑")
                ])) : vue.createCommentVNode("v-if", true)
              ])
            ]),
            vue.createElementVNode("view", { class: "camera-area" }, [
              vue.createElementVNode(
                "camera",
                {
                  class: "real-camera",
                  "device-position": "front",
                  flash: "off",
                  onError: $setup.handleCameraError
                },
                null,
                32
                /* NEED_HYDRATION */
              ),
              vue.createElementVNode("view", {
                class: "camera-overlay-content",
                style: { "z-index": "999" }
              }, [
                vue.createElementVNode("view", { class: "count-overlay" }, [
                  vue.createElementVNode(
                    "view",
                    { class: "count-val" },
                    vue.toDisplayString($setup.count),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode("view", { class: "count-label" }, "次")
                ]),
                vue.createElementVNode("view", { class: "progress-bar-container" }, [
                  vue.createElementVNode(
                    "view",
                    {
                      class: "progress-fill",
                      style: vue.normalizeStyle({ width: $setup.progressPercent + "%" })
                    },
                    null,
                    4
                    /* STYLE */
                  )
                ]),
                vue.createElementVNode("view", { class: "status-tips" }, [
                  vue.createElementVNode(
                    "view",
                    {
                      class: vue.normalizeClass(["status-text", { "valid-text": $setup.isStandard }])
                    },
                    vue.toDisplayString($setup.statusText),
                    3
                    /* TEXT, CLASS */
                  )
                ])
              ])
            ]),
            vue.createElementVNode("view", { class: "action-area" }, [
              vue.createElementVNode("view", { class: "timer-box" }, [
                vue.createElementVNode("text", { class: "timer-label" }, "测试用时"),
                vue.createElementVNode(
                  "text",
                  { class: "timer-text" },
                  vue.toDisplayString($setup.formatTime($setup.duration)),
                  1
                  /* TEXT */
                )
              ]),
              vue.createElementVNode("view", { class: "btn-group" }, [
                !$setup.isTesting ? (vue.openBlock(), vue.createElementBlock("button", {
                  key: 0,
                  class: "main-btn start-btn",
                  "hover-class": "btn-hover",
                  onClick: $setup.startTest
                }, "开始测试")) : (vue.openBlock(), vue.createElementBlock(
                  vue.Fragment,
                  { key: 1 },
                  [
                    vue.createElementVNode("button", {
                      class: "sub-btn stop-btn",
                      "hover-class": "btn-hover",
                      onClick: $setup.endTest
                    }, "结束测试"),
                    vue.createElementVNode("button", {
                      class: "sub-btn mock-btn",
                      "hover-class": "btn-hover",
                      onClick: $setup.mockCount
                    }, "+1 (模拟)")
                  ],
                  64
                  /* STABLE_FRAGMENT */
                ))
              ])
            ])
          ])),
          $setup.showGuide ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 2,
            class: "guide-modal",
            onClick: _cache[5] || (_cache[5] = ($event) => $setup.showGuide = false)
          }, [
            vue.createElementVNode("view", {
              class: "guide-content",
              onClick: _cache[4] || (_cache[4] = vue.withModifiers(() => {
              }, ["stop"]))
            }, [
              vue.createElementVNode("text", { class: "guide-title" }, "动作指南"),
              vue.createElementVNode("view", { class: "guide-visual" }, [
                vue.createElementVNode(
                  "text",
                  { class: "guide-emoji" },
                  vue.toDisplayString($setup.projectEmoji),
                  1
                  /* TEXT */
                )
              ]),
              vue.createElementVNode(
                "text",
                { class: "guide-desc" },
                vue.toDisplayString($setup.standardDesc),
                1
                /* TEXT */
              ),
              vue.createElementVNode("button", {
                class: "guide-btn",
                onClick: _cache[3] || (_cache[3] = ($event) => $setup.showGuide = false)
              }, "我知道了")
            ])
          ])) : vue.createCommentVNode("v-if", true)
        ],
        4
        /* STYLE */
      ),
      vue.createElementVNode("view", { class: "tab-bar" }, [
        vue.createElementVNode("view", { class: "tab-bar-border" }),
        (vue.openBlock(true), vue.createElementBlock(
          vue.Fragment,
          null,
          vue.renderList($setup.tabList, (item, index) => {
            return vue.openBlock(), vue.createElementBlock("view", {
              key: index,
              class: "tab-bar-item",
              onClick: ($event) => $setup.switchTab(item)
            }, [
              vue.createElementVNode("image", {
                class: "tab-icon",
                src: $setup.currentTab === item.pagePath ? item.selectedIconPath : item.iconPath
              }, null, 8, ["src"]),
              vue.createElementVNode(
                "view",
                {
                  class: "tab-text",
                  style: vue.normalizeStyle({ color: $setup.currentTab === item.pagePath ? "#20C997" : "#666666" })
                },
                vue.toDisplayString(item.text),
                5
                /* TEXT, STYLE */
              )
            ], 8, ["onClick"]);
          }),
          128
          /* KEYED_FRAGMENT */
        ))
      ])
    ]);
  }
  const PagesTestTest = /* @__PURE__ */ _export_sfc(_sfc_main$h, [["render", _sfc_render$g], ["__scopeId", "data-v-727d09f0"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/test/test.vue"]]);
  const _sfc_main$g = {
    __name: "list",
    setup(__props, { expose: __expose }) {
      __expose();
      const currentTab2 = vue.ref(0);
      const tasks = vue.ref([]);
      const page = vue.ref(1);
      const size = vue.ref(20);
      const loading = vue.ref(false);
      const loadTasks = async () => {
        if (loading.value)
          return;
        loading.value = true;
        try {
          const res = await getStudentTasks({ page: page.value, size: size.value });
          if (res.items) {
            const newTasks = res.items.map((t) => ({
              ...t,
              statusText: t.status === "completed" ? "已完成" : t.status === "expired" ? "已过期" : "进行中",
              desc: t.description || (t.min_distance ? `目标: ${t.min_distance}km` : "无具体描述"),
              deadline: t.deadline ? t.deadline.split("T")[0] : "无限制"
            }));
            if (page.value === 1)
              tasks.value = newTasks;
            else
              tasks.value = [...tasks.value, ...newTasks];
          }
        } catch (e) {
          formatAppLog("error", "at pages/student/tasks/list.vue:66", e);
          uni.showToast({ title: "加载任务失败", icon: "none" });
        } finally {
          loading.value = false;
        }
      };
      const loadMore = () => {
      };
      onShow(() => {
        page.value = 1;
        loadTasks();
      });
      const filteredTasks = vue.computed(() => {
        if (currentTab2.value === 0) {
          return tasks.value.filter((t) => t.status === "pending");
        } else {
          return tasks.value.filter((t) => t.status !== "pending");
        }
      });
      const getTypeClass = (type) => {
        return type === "test" ? "tag-red" : "tag-blue";
      };
      const getStatusClass = (status) => {
        if (status === "completed")
          return "text-green";
        if (status === "expired")
          return "text-gray";
        return "text-orange";
      };
      const doTask = (item) => {
        if (item.type === "run") {
          uni.navigateTo({ url: "/pages/run/run" });
        } else {
          uni.navigateTo({ url: "/pages/test/test" });
        }
      };
      const goToDetail = (item) => {
      };
      const __returned__ = { currentTab: currentTab2, tasks, page, size, loading, loadTasks, loadMore, filteredTasks, getTypeClass, getStatusClass, doTask, goToDetail, ref: vue.ref, computed: vue.computed, get onShow() {
        return onShow;
      }, get getStudentTasks() {
        return getStudentTasks;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$f(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "container" }, [
      vue.createElementVNode("view", { class: "tabs" }, [
        vue.createElementVNode(
          "view",
          {
            class: vue.normalizeClass(["tab-item", { active: $setup.currentTab === 0 }]),
            onClick: _cache[0] || (_cache[0] = ($event) => $setup.currentTab = 0)
          },
          "进行中",
          2
          /* CLASS */
        ),
        vue.createElementVNode(
          "view",
          {
            class: vue.normalizeClass(["tab-item", { active: $setup.currentTab === 1 }]),
            onClick: _cache[1] || (_cache[1] = ($event) => $setup.currentTab = 1)
          },
          "已结束",
          2
          /* CLASS */
        )
      ]),
      vue.createElementVNode(
        "scroll-view",
        {
          "scroll-y": "",
          class: "task-list",
          onScrolltolower: $setup.loadMore
        },
        [
          (vue.openBlock(true), vue.createElementBlock(
            vue.Fragment,
            null,
            vue.renderList($setup.filteredTasks, (item) => {
              return vue.openBlock(), vue.createElementBlock("view", {
                class: "task-card",
                key: item.id,
                onClick: ($event) => $setup.goToDetail(item)
              }, [
                vue.createElementVNode("view", { class: "card-header" }, [
                  vue.createElementVNode("view", { class: "title-row" }, [
                    vue.createElementVNode(
                      "text",
                      {
                        class: vue.normalizeClass(["tag", $setup.getTypeClass(item.type)])
                      },
                      vue.toDisplayString(item.type === "run" ? "跑步" : "体测"),
                      3
                      /* TEXT, CLASS */
                    ),
                    vue.createElementVNode(
                      "text",
                      { class: "title" },
                      vue.toDisplayString(item.title),
                      1
                      /* TEXT */
                    )
                  ]),
                  vue.createElementVNode(
                    "text",
                    {
                      class: vue.normalizeClass(["status", $setup.getStatusClass(item.status)])
                    },
                    vue.toDisplayString(item.statusText),
                    3
                    /* TEXT, CLASS */
                  )
                ]),
                vue.createElementVNode("view", { class: "card-body" }, [
                  vue.createElementVNode(
                    "text",
                    { class: "desc" },
                    vue.toDisplayString(item.desc),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode("view", { class: "meta-row" }, [
                    vue.createElementVNode(
                      "text",
                      { class: "deadline" },
                      "截止: " + vue.toDisplayString(item.deadline),
                      1
                      /* TEXT */
                    )
                  ])
                ]),
                vue.createElementVNode("view", { class: "card-footer" }, [
                  item.status === "pending" ? (vue.openBlock(), vue.createElementBlock("button", {
                    key: 0,
                    class: "action-btn",
                    onClick: vue.withModifiers(($event) => $setup.doTask(item), ["stop"])
                  }, "去完成", 8, ["onClick"])) : item.status === "completed" ? (vue.openBlock(), vue.createElementBlock("text", {
                    key: 1,
                    class: "completed-text"
                  }, "✅ 已完成")) : (vue.openBlock(), vue.createElementBlock("text", {
                    key: 2,
                    class: "expired-text"
                  }, "已过期"))
                ])
              ], 8, ["onClick"]);
            }),
            128
            /* KEYED_FRAGMENT */
          )),
          $setup.loading ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 0,
            class: "loading-more"
          }, "加载中...")) : vue.createCommentVNode("v-if", true),
          !$setup.loading && $setup.filteredTasks.length === 0 ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 1,
            class: "no-more"
          }, "暂无任务")) : vue.createCommentVNode("v-if", true)
        ],
        32
        /* NEED_HYDRATION */
      )
    ]);
  }
  const PagesStudentTasksList = /* @__PURE__ */ _export_sfc(_sfc_main$g, [["render", _sfc_render$f], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/student/tasks/list.vue"]]);
  const _sfc_main$f = {
    __name: "home",
    setup(__props, { expose: __expose }) {
      __expose();
      const userInfo = vue.ref({});
      const goToApprove = () => {
        uni.navigateTo({ url: "/pages/teacher/approve/approve" });
      };
      onShow(() => {
        uni.hideHomeButton && uni.hideHomeButton();
        const storedUser = uni.getStorageSync("userInfo");
        if (storedUser) {
          try {
            userInfo.value = typeof storedUser === "string" ? JSON.parse(storedUser) : storedUser;
          } catch (e) {
            formatAppLog("error", "at pages/teacher/home/home.vue:198", "JSON parse error", e);
            userInfo.value = {};
          }
        }
      });
      const teacherStats = vue.ref({
        studentCount: 128,
        todayCheckin: 105,
        abnormalCount: 3,
        avgPace: `5'45"`,
        taskCount: 5,
        complianceRate: 92
      });
      const weeklyTrend = vue.ref([
        { day: "周一", val: 60, color: "#e0e0e0" },
        { day: "周二", val: 80, color: "#e0e0e0" },
        { day: "周三", val: 45, color: "#e0e0e0" },
        { day: "周四", val: 90, color: "#20C997" },
        { day: "周五", val: 70, color: "#e0e0e0" },
        { day: "周六", val: 30, color: "#e0e0e0" },
        { day: "周日", val: 50, color: "#e0e0e0" }
      ]);
      const showTaskModal = vue.ref(false);
      const isEditing = vue.ref(false);
      const currentTask = vue.ref({ title: "", type: "日常", desc: "" });
      const quickTasks = vue.ref([
        { title: "3000米摸底测试", type: "考核", typeClass: "tag-red", status: "进行中", percent: 76 },
        { title: "周末晨跑打卡", type: "日常", typeClass: "tag-green", status: "进行中", percent: 35 },
        { title: "核心力量专项", type: "训练", typeClass: "tag-blue", status: "即将截止", percent: 88 }
      ]);
      const abnormalAlerts = vue.ref([
        { id: 1, student: "张三", type: "心率过高", value: "195 bpm", time: "10:30" },
        { id: 2, student: "李四", type: "配速异常", value: "过快", time: "10:45" },
        { id: 3, student: "王五", type: "动作不达标", value: "引体向上", time: "10:50" }
      ]);
      const handleTeacherAction = (action) => {
        if (action === "学员管理") {
          uni.navigateTo({ url: "/pages/teacher/students/students" });
        } else if (action === "任务管理") {
          uni.navigateTo({ url: "/pages/teacher/tasks/tasks" });
        } else if (action === "发布任务") {
          uni.navigateTo({ url: "/pages/teacher/tasks/create" });
        } else if (action === "异常处理") {
          uni.navigateTo({ url: "/pages/teacher/exceptions/exceptions" });
        } else if (action === "测试监控") {
          uni.navigateTo({ url: "/pages/teacher/tests/tests" });
        } else {
          uni.showToast({ title: `${action}功能即将上线`, icon: "none" });
        }
      };
      const openTaskModal = () => {
        isEditing.value = false;
        currentTask.value = { title: "", type: "日常", desc: "" };
        showTaskModal.value = true;
      };
      const editTask = (task) => {
        isEditing.value = true;
        currentTask.value = { ...task, desc: "任务描述..." };
        showTaskModal.value = true;
      };
      const saveTask = () => {
        if (!currentTask.value.title)
          return uni.showToast({ title: "请输入标题", icon: "none" });
        uni.showToast({ title: isEditing.value ? "修改成功" : "发布成功", icon: "success" });
        showTaskModal.value = false;
      };
      const remindTask = (task) => {
        uni.showToast({ title: `已催办任务: ${task.title}`, icon: "none" });
      };
      const handleQuickTask = (task) => {
        uni.navigateTo({
          url: `/pages/teacher/tasks/detail?id=999&title=${task.title}`
        });
      };
      const handleResolveAlert = (index) => {
        uni.showActionSheet({
          itemList: ["联系学生", "标记已处理", "查看详情"],
          success: (res) => {
            if (res.tapIndex === 1) {
              abnormalAlerts.value.splice(index, 1);
              teacherStats.value.abnormalCount = Math.max(0, teacherStats.value.abnormalCount - 1);
              uni.showToast({ title: "已处理", icon: "success" });
            } else if (res.tapIndex === 0) {
              uni.showToast({ title: "已发送通知", icon: "none" });
            } else {
              uni.navigateTo({ url: "/pages/teacher/exceptions/exceptions" });
            }
          }
        });
      };
      const __returned__ = { userInfo, goToApprove, teacherStats, weeklyTrend, showTaskModal, isEditing, currentTask, quickTasks, abnormalAlerts, handleTeacherAction, openTaskModal, editTask, saveTask, remindTask, handleQuickTask, handleResolveAlert, ref: vue.ref, get onShow() {
        return onShow;
      }, CustomTabBar };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$e(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "home-container" }, [
      vue.createElementVNode("view", { class: "teacher-dashboard" }, [
        vue.createElementVNode("view", { class: "custom-nav-bar" }, [
          vue.createElementVNode("view", { class: "nav-status-bar" }),
          vue.createElementVNode("view", { class: "nav-content" }, [
            vue.createElementVNode("text", { class: "nav-title" }, "教师工作台")
          ])
        ]),
        vue.createElementVNode("view", { class: "teacher-header" }, [
          vue.createElementVNode("view", { class: "teacher-info" }, [
            vue.createElementVNode(
              "text",
              { class: "teacher-name" },
              vue.toDisplayString($setup.userInfo.name || "老师"),
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "teacher-title" }, "体育教研室")
          ]),
          vue.createElementVNode("view", { class: "teacher-avatar" }, [
            vue.createElementVNode("image", {
              class: "avatar-img",
              src: _imports_0$1,
              mode: "aspectFill"
            })
          ])
        ]),
        vue.createElementVNode("view", { class: "dashboard-stats" }, [
          vue.createElementVNode("view", { class: "stat-card" }, [
            vue.createElementVNode(
              "text",
              { class: "stat-num" },
              vue.toDisplayString($setup.teacherStats.todayCheckin),
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "stat-label" }, "今日打卡")
          ]),
          vue.createElementVNode("view", { class: "stat-card" }, [
            vue.createElementVNode(
              "text",
              { class: "stat-num" },
              vue.toDisplayString($setup.teacherStats.abnormalCount),
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "stat-label" }, "异常待处理")
          ]),
          vue.createElementVNode("view", {
            class: "stat-card",
            onClick: $setup.goToApprove
          }, [
            vue.createElementVNode(
              "text",
              { class: "stat-num" },
              vue.toDisplayString($setup.teacherStats.pendingApprovals || 12),
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "stat-label" }, "待审批")
          ])
        ]),
        vue.createElementVNode("view", { class: "section-card todo-section" }, [
          vue.createElementVNode("view", { class: "section-header" }, [
            vue.createElementVNode("text", { class: "section-title" }, "今日待办"),
            vue.createElementVNode("text", { class: "section-more" }, "全部 >")
          ]),
          vue.createElementVNode("view", { class: "todo-list" }, [
            vue.createElementVNode("view", { class: "todo-item" }, [
              vue.createElementVNode("view", { class: "todo-check" }),
              vue.createElementVNode("view", { class: "todo-content" }, [
                vue.createElementVNode("text", { class: "todo-text" }, "审批 2023级体测成绩"),
                vue.createElementVNode("text", { class: "todo-time" }, "截止: 17:00")
              ])
            ]),
            vue.createElementVNode("view", { class: "todo-item" }, [
              vue.createElementVNode("view", { class: "todo-check" }),
              vue.createElementVNode("view", { class: "todo-content" }, [
                vue.createElementVNode("text", { class: "todo-text" }, "发布本周训练计划"),
                vue.createElementVNode("text", { class: "todo-time" }, "待处理")
              ])
            ])
          ])
        ]),
        vue.createElementVNode("view", { class: "section-card chart-section" }, [
          vue.createElementVNode("view", { class: "section-header" }, [
            vue.createElementVNode("text", { class: "section-title" }, "学员体能概览"),
            vue.createElementVNode("text", { class: "section-more" }, "更多 >")
          ]),
          vue.createElementVNode("view", { class: "overview-chart" }, [
            vue.createElementVNode("view", { class: "chart-col" }, [
              vue.createElementVNode("view", { class: "chart-ring ring-green" }, [
                vue.createElementVNode("text", { class: "ring-val" }, "92%"),
                vue.createElementVNode("text", { class: "ring-label" }, "达标率")
              ]),
              vue.createElementVNode("text", { class: "chart-name" }, "体能达标")
            ]),
            vue.createElementVNode("view", { class: "chart-col" }, [
              vue.createElementVNode("view", { class: "chart-ring ring-blue" }, [
                vue.createElementVNode("text", { class: "ring-val" }, "85%"),
                vue.createElementVNode("text", { class: "ring-label" }, "完成率")
              ]),
              vue.createElementVNode("text", { class: "chart-name" }, "本周任务")
            ]),
            vue.createElementVNode("view", { class: "chart-col" }, [
              vue.createElementVNode("view", { class: "chart-ring ring-red" }, [
                vue.createElementVNode("text", { class: "ring-val" }, `5'45"`),
                vue.createElementVNode("text", { class: "ring-label" }, "平均配速")
              ]),
              vue.createElementVNode("text", { class: "chart-name" }, "跑步状态")
            ])
          ]),
          vue.createElementVNode("view", { class: "trend-chart" }, [
            vue.createElementVNode("text", { class: "trend-title" }, "本周运动趋势"),
            vue.createElementVNode("view", { class: "trend-bars" }, [
              (vue.openBlock(true), vue.createElementBlock(
                vue.Fragment,
                null,
                vue.renderList($setup.weeklyTrend, (d, i) => {
                  return vue.openBlock(), vue.createElementBlock("view", {
                    class: "t-bar-group",
                    key: i
                  }, [
                    vue.createElementVNode(
                      "view",
                      {
                        class: "t-bar",
                        style: vue.normalizeStyle({ height: d.val + "%", background: d.color })
                      },
                      null,
                      4
                      /* STYLE */
                    ),
                    vue.createElementVNode(
                      "text",
                      { class: "t-day" },
                      vue.toDisplayString(d.day),
                      1
                      /* TEXT */
                    )
                  ]);
                }),
                128
                /* KEYED_FRAGMENT */
              ))
            ])
          ])
        ]),
        vue.createElementVNode("view", { class: "section-card task-widget" }, [
          vue.createElementVNode("view", { class: "section-header" }, [
            vue.createElementVNode("text", { class: "section-title" }, "快速任务管理"),
            vue.createElementVNode("view", { class: "header-actions" }, [
              vue.createElementVNode("text", {
                class: "section-action",
                onClick: $setup.openTaskModal
              }, "+ 发布")
            ])
          ]),
          vue.createElementVNode("scroll-view", {
            "scroll-x": "",
            class: "quick-task-scroll"
          }, [
            (vue.openBlock(true), vue.createElementBlock(
              vue.Fragment,
              null,
              vue.renderList($setup.quickTasks, (task, idx) => {
                return vue.openBlock(), vue.createElementBlock("view", {
                  class: "quick-task-item",
                  key: idx,
                  onClick: ($event) => $setup.handleQuickTask(task)
                }, [
                  vue.createElementVNode("view", { class: "qt-header" }, [
                    vue.createElementVNode(
                      "text",
                      {
                        class: vue.normalizeClass(["qt-type", task.typeClass])
                      },
                      vue.toDisplayString(task.type),
                      3
                      /* TEXT, CLASS */
                    ),
                    vue.createElementVNode(
                      "text",
                      { class: "qt-status" },
                      vue.toDisplayString(task.status),
                      1
                      /* TEXT */
                    )
                  ]),
                  vue.createElementVNode(
                    "text",
                    { class: "qt-title" },
                    vue.toDisplayString(task.title),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode("view", { class: "qt-progress" }, [
                    vue.createElementVNode("view", { class: "qt-bar-bg" }, [
                      vue.createElementVNode(
                        "view",
                        {
                          class: "qt-bar-fill",
                          style: vue.normalizeStyle({ width: task.percent + "%" })
                        },
                        null,
                        4
                        /* STYLE */
                      )
                    ]),
                    vue.createElementVNode(
                      "text",
                      { class: "qt-val" },
                      vue.toDisplayString(task.percent) + "%",
                      1
                      /* TEXT */
                    )
                  ]),
                  vue.createElementVNode("view", {
                    class: "qt-actions",
                    onClick: _cache[0] || (_cache[0] = vue.withModifiers(() => {
                    }, ["stop"]))
                  }, [
                    vue.createElementVNode("text", {
                      class: "qt-btn",
                      onClick: ($event) => $setup.editTask(task)
                    }, "编辑", 8, ["onClick"]),
                    task.percent < 100 ? (vue.openBlock(), vue.createElementBlock("text", {
                      key: 0,
                      class: "qt-btn warn",
                      onClick: ($event) => $setup.remindTask(task)
                    }, "催办", 8, ["onClick"])) : vue.createCommentVNode("v-if", true)
                  ])
                ], 8, ["onClick"]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ])
        ]),
        $setup.abnormalAlerts.length > 0 ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "section-card alert-widget"
        }, [
          vue.createElementVNode("view", { class: "section-header" }, [
            vue.createElementVNode("text", { class: "section-title red-dot" }, "⚠️ 实时警报")
          ]),
          vue.createElementVNode("view", { class: "alert-feed" }, [
            (vue.openBlock(true), vue.createElementBlock(
              vue.Fragment,
              null,
              vue.renderList($setup.abnormalAlerts, (alert, idx) => {
                return vue.openBlock(), vue.createElementBlock("view", {
                  class: "feed-item",
                  key: idx
                }, [
                  vue.createElementVNode("view", { class: "feed-content" }, [
                    vue.createElementVNode("text", { class: "feed-msg" }, [
                      vue.createElementVNode(
                        "text",
                        { class: "feed-name" },
                        vue.toDisplayString(alert.student),
                        1
                        /* TEXT */
                      ),
                      vue.createTextVNode(
                        " " + vue.toDisplayString(alert.type) + " (" + vue.toDisplayString(alert.value) + ")",
                        1
                        /* TEXT */
                      )
                    ]),
                    vue.createElementVNode(
                      "text",
                      { class: "feed-time" },
                      vue.toDisplayString(alert.time),
                      1
                      /* TEXT */
                    )
                  ]),
                  vue.createElementVNode("button", {
                    class: "feed-btn",
                    size: "mini",
                    onClick: ($event) => $setup.handleResolveAlert(idx)
                  }, "干预", 8, ["onClick"])
                ]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ])
        ])) : vue.createCommentVNode("v-if", true),
        $setup.showTaskModal ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 1,
          class: "modal-overlay",
          onClick: _cache[8] || (_cache[8] = ($event) => $setup.showTaskModal = false)
        }, [
          vue.createElementVNode("view", {
            class: "task-modal",
            onClick: _cache[7] || (_cache[7] = vue.withModifiers(() => {
            }, ["stop"]))
          }, [
            vue.createElementVNode("view", { class: "modal-header" }, [
              vue.createElementVNode(
                "text",
                { class: "modal-title" },
                vue.toDisplayString($setup.isEditing ? "编辑任务" : "快速发布任务"),
                1
                /* TEXT */
              ),
              vue.createElementVNode("text", {
                class: "close-btn",
                onClick: _cache[1] || (_cache[1] = ($event) => $setup.showTaskModal = false)
              }, "×")
            ]),
            vue.createElementVNode("view", { class: "modal-body" }, [
              vue.withDirectives(vue.createElementVNode(
                "input",
                {
                  class: "modal-input",
                  placeholder: "任务标题",
                  "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $setup.currentTask.title = $event)
                },
                null,
                512
                /* NEED_PATCH */
              ), [
                [vue.vModelText, $setup.currentTask.title]
              ]),
              vue.createElementVNode("view", { class: "modal-types" }, [
                vue.createElementVNode(
                  "view",
                  {
                    class: vue.normalizeClass(["type-chip", { active: $setup.currentTask.type === "考核" }]),
                    onClick: _cache[3] || (_cache[3] = ($event) => $setup.currentTask.type = "考核")
                  },
                  "考核",
                  2
                  /* CLASS */
                ),
                vue.createElementVNode(
                  "view",
                  {
                    class: vue.normalizeClass(["type-chip", { active: $setup.currentTask.type === "日常" }]),
                    onClick: _cache[4] || (_cache[4] = ($event) => $setup.currentTask.type = "日常")
                  },
                  "日常",
                  2
                  /* CLASS */
                ),
                vue.createElementVNode(
                  "view",
                  {
                    class: vue.normalizeClass(["type-chip", { active: $setup.currentTask.type === "训练" }]),
                    onClick: _cache[5] || (_cache[5] = ($event) => $setup.currentTask.type = "训练")
                  },
                  "训练",
                  2
                  /* CLASS */
                )
              ]),
              vue.withDirectives(vue.createElementVNode(
                "textarea",
                {
                  class: "modal-textarea",
                  placeholder: "任务描述",
                  "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $setup.currentTask.desc = $event)
                },
                null,
                512
                /* NEED_PATCH */
              ), [
                [vue.vModelText, $setup.currentTask.desc]
              ])
            ]),
            vue.createElementVNode("button", {
              class: "modal-submit-btn",
              onClick: $setup.saveTask
            }, "确认发布")
          ])
        ])) : vue.createCommentVNode("v-if", true),
        vue.createElementVNode("view", { style: { "height": "120rpx" } }),
        vue.createVNode($setup["CustomTabBar"], { current: "/pages/teacher/home/home" })
      ])
    ]);
  }
  const PagesTeacherHomeHome = /* @__PURE__ */ _export_sfc(_sfc_main$f, [["render", _sfc_render$e], ["__scopeId", "data-v-c5a4d262"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/home/home.vue"]]);
  const _sfc_main$e = {
    __name: "manage",
    setup(__props, { expose: __expose }) {
      __expose();
      onShow(() => {
        uni.hideHomeButton && uni.hideHomeButton();
      });
      const navTo = (url) => {
        uni.navigateTo({ url });
      };
      const showToast = (title) => {
        uni.showToast({
          title: `${title}功能开发中`,
          icon: "none"
        });
      };
      const __returned__ = { navTo, showToast, get onShow() {
        return onShow;
      }, CustomTabBar };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$d(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "manage-container" }, [
      vue.createElementVNode("view", { class: "custom-nav-bar" }, [
        vue.createElementVNode("view", { class: "nav-status-bar" }),
        vue.createElementVNode("view", { class: "nav-content" }, [
          vue.createElementVNode("text", { class: "nav-title" }, "综合管理")
        ])
      ]),
      vue.createElementVNode("view", { class: "content-wrapper" }, [
        vue.createElementVNode("view", { class: "grid-container" }, [
          vue.createElementVNode("view", {
            class: "grid-item",
            onClick: _cache[0] || (_cache[0] = ($event) => $setup.navTo("/pages/teacher/students/students"))
          }, [
            vue.createElementVNode("view", { class: "icon-box purple" }, "👥"),
            vue.createElementVNode("text", { class: "grid-label" }, "学员管理"),
            vue.createElementVNode("text", { class: "grid-desc" }, "分组、档案")
          ]),
          vue.createElementVNode("view", {
            class: "grid-item",
            onClick: _cache[1] || (_cache[1] = ($event) => $setup.showToast("班级管理"))
          }, [
            vue.createElementVNode("view", { class: "icon-box cyan" }, "🏫"),
            vue.createElementVNode("text", { class: "grid-label" }, "班级管理"),
            vue.createElementVNode("text", { class: "grid-desc" }, "排课、考勤")
          ]),
          vue.createElementVNode("view", {
            class: "grid-item",
            onClick: _cache[2] || (_cache[2] = ($event) => $setup.navTo("/pages/teacher/tasks/tasks"))
          }, [
            vue.createElementVNode("view", { class: "icon-box green" }, "📢"),
            vue.createElementVNode("text", { class: "grid-label" }, "任务管理"),
            vue.createElementVNode("text", { class: "grid-desc" }, "发布、审批")
          ]),
          vue.createElementVNode("view", {
            class: "grid-item",
            onClick: _cache[3] || (_cache[3] = ($event) => $setup.showToast("教学资源"))
          }, [
            vue.createElementVNode("view", { class: "icon-box pink" }, "📚"),
            vue.createElementVNode("text", { class: "grid-label" }, "教学资源"),
            vue.createElementVNode("text", { class: "grid-desc" }, "课件、视频")
          ]),
          vue.createElementVNode("view", {
            class: "grid-item",
            onClick: _cache[4] || (_cache[4] = ($event) => $setup.navTo("/pages/teacher/tests/tests"))
          }, [
            vue.createElementVNode("view", { class: "icon-box blue" }, "📊"),
            vue.createElementVNode("text", { class: "grid-label" }, "测试监控"),
            vue.createElementVNode("text", { class: "grid-desc" }, "实时数据")
          ]),
          vue.createElementVNode("view", {
            class: "grid-item",
            onClick: _cache[5] || (_cache[5] = ($event) => $setup.showToast("数据导出"))
          }, [
            vue.createElementVNode("view", { class: "icon-box indigo" }, "📥"),
            vue.createElementVNode("text", { class: "grid-label" }, "数据导出"),
            vue.createElementVNode("text", { class: "grid-desc" }, "报表下载")
          ]),
          vue.createElementVNode("view", {
            class: "grid-item",
            onClick: _cache[6] || (_cache[6] = ($event) => $setup.navTo("/pages/teacher/exceptions/exceptions"))
          }, [
            vue.createElementVNode("view", { class: "icon-box orange" }, "⚠️"),
            vue.createElementVNode("text", { class: "grid-label" }, "异常处理"),
            vue.createElementVNode("text", { class: "grid-desc" }, "预警干预")
          ]),
          vue.createElementVNode("view", {
            class: "grid-item",
            onClick: _cache[7] || (_cache[7] = ($event) => $setup.showToast("通知公告"))
          }, [
            vue.createElementVNode("view", { class: "icon-box teal" }, "🔔"),
            vue.createElementVNode("text", { class: "grid-label" }, "通知公告"),
            vue.createElementVNode("text", { class: "grid-desc" }, "消息推送")
          ])
        ]),
        vue.createElementVNode("view", { class: "stats-card" }, [
          vue.createElementVNode("view", { class: "card-header" }, [
            vue.createElementVNode("text", { class: "card-title" }, "数据概览")
          ]),
          vue.createElementVNode("view", { class: "stats-row" }, [
            vue.createElementVNode("view", { class: "stat-item" }, [
              vue.createElementVNode("text", { class: "stat-val" }, "128"),
              vue.createElementVNode("text", { class: "stat-label" }, "总学员")
            ]),
            vue.createElementVNode("view", { class: "stat-item" }, [
              vue.createElementVNode("text", { class: "stat-val" }, "92%"),
              vue.createElementVNode("text", { class: "stat-label" }, "达标率")
            ]),
            vue.createElementVNode("view", { class: "stat-item" }, [
              vue.createElementVNode("text", { class: "stat-val" }, "5"),
              vue.createElementVNode("text", { class: "stat-label" }, "进行中任务")
            ])
          ])
        ]),
        vue.createElementVNode("view", { style: { "height": "120rpx" } }),
        vue.createVNode($setup["CustomTabBar"], { current: "/pages/teacher/manage/manage" })
      ])
    ]);
  }
  const PagesTeacherManageManage = /* @__PURE__ */ _export_sfc(_sfc_main$e, [["render", _sfc_render$d], ["__scopeId", "data-v-b30bafb4"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/manage/manage.vue"]]);
  const _sfc_main$d = {
    __name: "mine",
    setup(__props, { expose: __expose }) {
      __expose();
      const userInfo = vue.ref({});
      onShow(() => {
        uni.hideHomeButton && uni.hideHomeButton();
        const storedUser = uni.getStorageSync("userInfo");
        if (storedUser) {
          try {
            userInfo.value = typeof storedUser === "string" ? JSON.parse(storedUser) : storedUser;
          } catch (e) {
            userInfo.value = {};
          }
        }
      });
      const handleLogout = () => {
        uni.removeStorageSync("userInfo");
        uni.removeStorageSync("userRole");
        uni.reLaunch({
          url: "/pages/login/login"
        });
      };
      const __returned__ = { userInfo, handleLogout, ref: vue.ref, get onShow() {
        return onShow;
      }, CustomTabBar };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$c(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "mine-container" }, [
      vue.createElementVNode("view", { class: "custom-nav-bar" }, [
        vue.createElementVNode("view", { class: "nav-status-bar" }),
        vue.createElementVNode("view", { class: "nav-content" }, [
          vue.createElementVNode("text", { class: "nav-title" }, "个人中心")
        ])
      ]),
      vue.createElementVNode("view", { class: "content-wrapper" }, [
        vue.createElementVNode("view", { class: "user-card" }, [
          vue.createElementVNode("view", { class: "avatar" }, "👮‍♂️"),
          vue.createElementVNode("view", { class: "info" }, [
            vue.createElementVNode(
              "text",
              { class: "name" },
              vue.toDisplayString($setup.userInfo.name || "教官"),
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "role" }, "警务体能教研室")
          ])
        ]),
        vue.createElementVNode("view", { class: "menu-list" }, [
          vue.createElementVNode("view", {
            class: "menu-item",
            onClick: _cache[0] || (_cache[0] = ($event) => uni.showToast({ title: "设置功能开发中", icon: "none" }))
          }, [
            vue.createElementVNode("text", null, "个人信息设置"),
            vue.createElementVNode("text", { class: "arrow" }, ">")
          ]),
          vue.createElementVNode("view", {
            class: "menu-item",
            onClick: _cache[1] || (_cache[1] = ($event) => uni.showToast({ title: "安全中心开发中", icon: "none" }))
          }, [
            vue.createElementVNode("text", null, "账号安全"),
            vue.createElementVNode("text", { class: "arrow" }, ">")
          ]),
          vue.createElementVNode("view", {
            class: "menu-item",
            onClick: _cache[2] || (_cache[2] = ($event) => uni.showToast({ title: "暂无新通知", icon: "none" }))
          }, [
            vue.createElementVNode("text", null, "系统通知"),
            vue.createElementVNode("text", { class: "arrow" }, ">")
          ]),
          vue.createElementVNode("view", {
            class: "menu-item",
            onClick: _cache[3] || (_cache[3] = ($event) => uni.showToast({ title: "请联系管理员", icon: "none" }))
          }, [
            vue.createElementVNode("text", null, "帮助与反馈"),
            vue.createElementVNode("text", { class: "arrow" }, ">")
          ])
        ]),
        vue.createElementVNode("button", {
          class: "logout-btn",
          onClick: $setup.handleLogout
        }, "退出登录"),
        vue.createElementVNode("view", { style: { "height": "120rpx" } }),
        vue.createVNode($setup["CustomTabBar"], { current: "/pages/teacher/mine/mine" })
      ])
    ]);
  }
  const PagesTeacherMineMine = /* @__PURE__ */ _export_sfc(_sfc_main$d, [["render", _sfc_render$c], ["__scopeId", "data-v-f7dece31"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/mine/mine.vue"]]);
  const _sfc_main$c = {
    __name: "students",
    setup(__props, { expose: __expose }) {
      __expose();
      const isBatchMode = vue.ref(false);
      const selectedIds = vue.ref([]);
      const sharedReports = vue.ref([]);
      const showReportsModal = vue.ref(false);
      const students = vue.ref([
        { id: "S1001", name: "张三", no: "20240001", className: "侦查一班", group: "体能A组", status: "正常", statusClass: "ok", health: "良好", expanded: false, recent3km: `12'45"`, weeklyDistance: 15.5, attendance: "100%" },
        { id: "S1002", name: "李四", no: "20240002", className: "侦查二班", group: "体能B组", status: "异常", statusClass: "warn", health: "需关注", expanded: false, recent3km: `15'30"`, weeklyDistance: 5, attendance: "80%" },
        { id: "S1003", name: "王五", no: "20240003", className: "治安一班", group: "体能A组", status: "正常", statusClass: "ok", health: "良好", expanded: false, recent3km: `13'10"`, weeklyDistance: 12, attendance: "95%" }
      ]);
      const keyword = vue.ref("");
      const classOptions = vue.ref(["侦查一班", "侦查二班", "治安一班"]);
      const currentClass = vue.ref("");
      const groupOptions = vue.ref(["体能A组", "体能B组", "康复组"]);
      const currentGroup = vue.ref("");
      const filteredStudents = vue.computed(() => {
        return students.value.filter((s) => {
          const k = keyword.value.trim();
          const matchK = k ? s.name.includes(k) || s.no.includes(k) : true;
          const matchC = currentClass.value ? s.className === currentClass.value : true;
          const matchG = currentGroup.value ? s.group === currentGroup.value : true;
          return matchK && matchC && matchG;
        });
      });
      const total = vue.computed(() => students.value.length);
      const abnormal = vue.computed(() => students.value.filter((s) => s.status === "异常").length);
      const normal = vue.computed(() => students.value.filter((s) => s.status === "正常").length);
      const onClassChange = (e) => {
        const idx = e.detail.value;
        currentClass.value = classOptions.value[idx];
      };
      const onGroupChange = (e) => {
        const idx = e.detail.value;
        currentGroup.value = groupOptions.value[idx];
      };
      const isAllSelected = vue.computed(() => {
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
          return uni.showToast({ title: "请先选择学员", icon: "none" });
        uni.showModal({
          title: "批量提醒",
          content: `确定向选中的 ${selectedIds.value.length} 位学员发送跑步提醒吗？`,
          success: (res) => {
            if (res.confirm) {
              uni.showToast({ title: "发送成功", icon: "success" });
              toggleBatchMode();
            }
          }
        });
      };
      const batchExport = () => {
        if (selectedIds.value.length === 0)
          return uni.showToast({ title: "请先选择学员", icon: "none" });
        uni.showLoading({ title: "生成报表中..." });
        setTimeout(() => {
          uni.hideLoading();
          uni.showToast({ title: "导出成功，已发送至邮箱", icon: "success" });
          toggleBatchMode();
        }, 1500);
      };
      const batchGroup = () => {
        if (selectedIds.value.length === 0)
          return uni.showToast({ title: "请先选择学员", icon: "none" });
        uni.showActionSheet({
          itemList: groupOptions.value,
          success: (res) => {
            const groupName = groupOptions.value[res.tapIndex];
            students.value.forEach((s) => {
              if (selectedIds.value.includes(s.id)) {
                s.group = groupName;
              }
            });
            uni.showToast({ title: "批量分组成功", icon: "success" });
            toggleBatchMode();
          }
        });
      };
      const editGroup = (stu) => {
        uni.showActionSheet({
          itemList: groupOptions.value,
          success: (res) => {
            stu.group = groupOptions.value[res.tapIndex];
            uni.showToast({ title: "已调整分组", icon: "none" });
          }
        });
      };
      onShow(() => {
        const role = uni.getStorageSync("userRole") || uni.getStorageSync("role");
        if (role !== "teacher") {
          uni.showToast({ title: "请使用教师账号登录", icon: "none" });
          uni.redirectTo({ url: "/pages/login/login" });
        }
        sharedReports.value = uni.getStorageSync("mockSharedReports") || [];
      });
      const replyStudent = (report) => {
        uni.showModal({
          title: "回复指导",
          editable: true,
          placeholderText: "请输入指导建议...",
          success: (res) => {
            if (res.confirm && res.content) {
              uni.showToast({ title: "已发送指导", icon: "success" });
            }
          }
        });
      };
      const openDetail = (stu) => {
        uni.navigateTo({
          url: `/pages/teacher/students/detail?id=${stu.id}&name=${stu.name}&no=${stu.no}&class=${stu.className}`
        });
      };
      const __returned__ = { isBatchMode, selectedIds, sharedReports, showReportsModal, students, keyword, classOptions, currentClass, groupOptions, currentGroup, filteredStudents, total, abnormal, normal, onClassChange, onGroupChange, isAllSelected, toggleBatchMode, handleCardClick, toggleSelect, toggleSelectAll, batchRemind, batchExport, batchGroup, editGroup, replyStudent, openDetail, ref: vue.ref, computed: vue.computed, get onShow() {
        return onShow;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$b(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "students-page" }, [
      vue.createElementVNode("view", { class: "header" }, [
        vue.createElementVNode("view", { class: "title-row" }, [
          vue.createElementVNode("text", { class: "title" }, "学员管理"),
          vue.createElementVNode("view", {
            class: "batch-toggle",
            onClick: $setup.toggleBatchMode
          }, [
            vue.createElementVNode(
              "text",
              null,
              vue.toDisplayString($setup.isBatchMode ? "取消批量" : "批量管理"),
              1
              /* TEXT */
            )
          ])
        ]),
        vue.createElementVNode("view", { class: "toolbar" }, [
          vue.withDirectives(vue.createElementVNode(
            "input",
            {
              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => $setup.keyword = $event),
              class: "search",
              placeholder: "输入姓名或学号"
            },
            null,
            512
            /* NEED_PATCH */
          ), [
            [vue.vModelText, $setup.keyword]
          ]),
          vue.createElementVNode("picker", {
            mode: "selector",
            range: $setup.classOptions,
            onChange: $setup.onClassChange
          }, [
            vue.createElementVNode(
              "view",
              { class: "picker" },
              vue.toDisplayString($setup.currentClass || "全部班级") + " ▾",
              1
              /* TEXT */
            )
          ], 40, ["range"]),
          vue.createElementVNode("picker", {
            mode: "selector",
            range: $setup.groupOptions,
            onChange: $setup.onGroupChange
          }, [
            vue.createElementVNode(
              "view",
              { class: "picker" },
              vue.toDisplayString($setup.currentGroup || "全部小组") + " ▾",
              1
              /* TEXT */
            )
          ], 40, ["range"])
        ]),
        vue.createElementVNode("view", { class: "summary" }, [
          vue.createElementVNode("view", { class: "sum-item" }, [
            vue.createElementVNode(
              "text",
              { class: "sum-val" },
              vue.toDisplayString($setup.total),
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "sum-label" }, "总人数")
          ]),
          vue.createElementVNode("view", { class: "sum-item" }, [
            vue.createElementVNode(
              "text",
              { class: "sum-val" },
              vue.toDisplayString($setup.abnormal),
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "sum-label" }, "异常")
          ]),
          vue.createElementVNode("view", { class: "sum-item" }, [
            vue.createElementVNode(
              "text",
              { class: "sum-val" },
              vue.toDisplayString($setup.normal),
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "sum-label" }, "正常")
          ])
        ])
      ]),
      $setup.sharedReports.length > 0 ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 0,
        class: "report-notice",
        onClick: _cache[1] || (_cache[1] = ($event) => $setup.showReportsModal = true)
      }, [
        vue.createElementVNode("view", { class: "notice-left" }, [
          vue.createElementVNode("text", { class: "notice-icon" }, "🤖"),
          vue.createElementVNode(
            "text",
            { class: "notice-text" },
            "收到 " + vue.toDisplayString($setup.sharedReports.length) + " 份新的运动分析报告",
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("text", { class: "notice-arrow" }, "查看 >")
      ])) : vue.createCommentVNode("v-if", true),
      vue.createElementVNode(
        "view",
        {
          class: vue.normalizeClass(["card-list", { "has-bottom-bar": $setup.isBatchMode }])
        },
        [
          (vue.openBlock(true), vue.createElementBlock(
            vue.Fragment,
            null,
            vue.renderList($setup.filteredStudents, (stu, idx) => {
              return vue.openBlock(), vue.createElementBlock("view", {
                class: "student-card",
                key: idx,
                onClick: ($event) => $setup.handleCardClick(stu)
              }, [
                vue.createElementVNode("view", { class: "card-main" }, [
                  vue.createElementVNode("view", { class: "card-left" }, [
                    $setup.isBatchMode ? (vue.openBlock(), vue.createElementBlock("checkbox", {
                      key: 0,
                      checked: $setup.selectedIds.includes(stu.id),
                      onClick: vue.withModifiers(($event) => $setup.toggleSelect(stu), ["stop"]),
                      color: "#20C997",
                      style: { "transform": "scale(0.8)" }
                    }, null, 8, ["checked", "onClick"])) : vue.createCommentVNode("v-if", true),
                    vue.createElementVNode(
                      "view",
                      { class: "avatar" },
                      vue.toDisplayString(stu.name.slice(0, 1)),
                      1
                      /* TEXT */
                    ),
                    vue.createElementVNode("view", { class: "info" }, [
                      vue.createElementVNode("text", { class: "name" }, [
                        vue.createTextVNode(
                          vue.toDisplayString(stu.name) + " ",
                          1
                          /* TEXT */
                        ),
                        stu.group ? (vue.openBlock(), vue.createElementBlock(
                          "text",
                          {
                            key: 0,
                            class: "group-tag"
                          },
                          "(" + vue.toDisplayString(stu.group) + ")",
                          1
                          /* TEXT */
                        )) : vue.createCommentVNode("v-if", true)
                      ]),
                      vue.createElementVNode(
                        "text",
                        { class: "meta" },
                        "学号：" + vue.toDisplayString(stu.no),
                        1
                        /* TEXT */
                      ),
                      vue.createElementVNode(
                        "text",
                        { class: "meta" },
                        "班级：" + vue.toDisplayString(stu.className),
                        1
                        /* TEXT */
                      ),
                      vue.createElementVNode(
                        "text",
                        { class: "meta" },
                        "健康：" + vue.toDisplayString(stu.health),
                        1
                        /* TEXT */
                      )
                    ])
                  ]),
                  vue.createElementVNode("view", { class: "card-right" }, [
                    vue.createElementVNode(
                      "text",
                      {
                        class: vue.normalizeClass(["status", stu.statusClass])
                      },
                      vue.toDisplayString(stu.status),
                      3
                      /* TEXT, CLASS */
                    ),
                    !$setup.isBatchMode ? (vue.openBlock(), vue.createElementBlock(
                      "text",
                      {
                        key: 0,
                        class: "expand-icon"
                      },
                      vue.toDisplayString(stu.expanded ? "▲" : "▼"),
                      1
                      /* TEXT */
                    )) : vue.createCommentVNode("v-if", true)
                  ])
                ]),
                stu.expanded && !$setup.isBatchMode ? (vue.openBlock(), vue.createElementBlock("view", {
                  key: 0,
                  class: "card-expanded"
                }, [
                  vue.createElementVNode("view", { class: "exp-grid" }, [
                    vue.createElementVNode("view", { class: "exp-item" }, [
                      vue.createElementVNode("text", { class: "exp-label" }, "最近3km"),
                      vue.createElementVNode(
                        "text",
                        { class: "exp-val" },
                        vue.toDisplayString(stu.recent3km || "无记录"),
                        1
                        /* TEXT */
                      )
                    ]),
                    vue.createElementVNode("view", { class: "exp-item" }, [
                      vue.createElementVNode("text", { class: "exp-label" }, "本周跑量"),
                      vue.createElementVNode(
                        "text",
                        { class: "exp-val" },
                        vue.toDisplayString(stu.weeklyDistance || "0") + "km",
                        1
                        /* TEXT */
                      )
                    ]),
                    vue.createElementVNode("view", { class: "exp-item" }, [
                      vue.createElementVNode("text", { class: "exp-label" }, "出勤率"),
                      vue.createElementVNode(
                        "text",
                        { class: "exp-val" },
                        vue.toDisplayString(stu.attendance || "100%"),
                        1
                        /* TEXT */
                      )
                    ])
                  ]),
                  vue.createElementVNode("view", { class: "exp-actions" }, [
                    vue.createElementVNode("button", {
                      size: "mini",
                      class: "exp-btn",
                      onClick: vue.withModifiers(($event) => $setup.openDetail(stu), ["stop"])
                    }, "完整档案", 8, ["onClick"]),
                    vue.createElementVNode("button", {
                      size: "mini",
                      class: "exp-btn outline",
                      onClick: vue.withModifiers(($event) => $setup.editGroup(stu), ["stop"])
                    }, "调整分组", 8, ["onClick"])
                  ])
                ])) : vue.createCommentVNode("v-if", true)
              ], 8, ["onClick"]);
            }),
            128
            /* KEYED_FRAGMENT */
          )),
          $setup.filteredStudents.length === 0 ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 0,
            class: "empty"
          }, [
            vue.createElementVNode("text", null, "暂无符合条件的学员")
          ])) : vue.createCommentVNode("v-if", true)
        ],
        2
        /* CLASS */
      ),
      $setup.isBatchMode ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 1,
        class: "batch-bar"
      }, [
        vue.createElementVNode("view", { class: "batch-info" }, [
          vue.createElementVNode("checkbox", {
            checked: $setup.isAllSelected,
            onClick: $setup.toggleSelectAll,
            color: "#20C997",
            style: { "transform": "scale(0.8)" }
          }, null, 8, ["checked"]),
          vue.createElementVNode(
            "text",
            null,
            "已选 " + vue.toDisplayString($setup.selectedIds.length) + " 人",
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "batch-actions" }, [
          vue.createElementVNode("button", {
            size: "mini",
            class: "action-btn outline",
            onClick: $setup.batchGroup
          }, "批量分组"),
          vue.createElementVNode("button", {
            size: "mini",
            class: "action-btn warn",
            onClick: $setup.batchRemind
          }, "一键提醒"),
          vue.createElementVNode("button", {
            size: "mini",
            class: "action-btn",
            onClick: $setup.batchExport
          }, "导出数据")
        ])
      ])) : vue.createCommentVNode("v-if", true),
      $setup.showReportsModal ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 2,
        class: "modal-overlay",
        onClick: _cache[4] || (_cache[4] = ($event) => $setup.showReportsModal = false)
      }, [
        vue.createElementVNode("view", {
          class: "report-modal",
          onClick: _cache[3] || (_cache[3] = vue.withModifiers(() => {
          }, ["stop"]))
        }, [
          vue.createElementVNode("view", { class: "modal-header" }, [
            vue.createElementVNode("text", { class: "modal-title" }, "📄 学员运动分析报告"),
            vue.createElementVNode("text", {
              class: "close-btn",
              onClick: _cache[2] || (_cache[2] = ($event) => $setup.showReportsModal = false)
            }, "×")
          ]),
          vue.createElementVNode("scroll-view", {
            "scroll-y": "",
            class: "report-list"
          }, [
            (vue.openBlock(true), vue.createElementBlock(
              vue.Fragment,
              null,
              vue.renderList($setup.sharedReports, (report, idx) => {
                return vue.openBlock(), vue.createElementBlock("view", {
                  class: "report-item",
                  key: idx
                }, [
                  vue.createElementVNode("view", { class: "report-meta" }, [
                    vue.createElementVNode(
                      "text",
                      { class: "report-stu" },
                      vue.toDisplayString(report.studentName),
                      1
                      /* TEXT */
                    ),
                    vue.createElementVNode(
                      "text",
                      { class: "report-time" },
                      vue.toDisplayString(report.time),
                      1
                      /* TEXT */
                    )
                  ]),
                  vue.createElementVNode("view", { class: "report-card" }, [
                    vue.createElementVNode(
                      "text",
                      { class: "report-title" },
                      vue.toDisplayString(report.card.title),
                      1
                      /* TEXT */
                    ),
                    report.card.suggestion ? (vue.openBlock(), vue.createElementBlock(
                      "text",
                      {
                        key: 0,
                        class: "report-suggestion"
                      },
                      "💡 " + vue.toDisplayString(report.card.suggestion),
                      1
                      /* TEXT */
                    )) : vue.createCommentVNode("v-if", true),
                    report.card.chartData ? (vue.openBlock(), vue.createElementBlock("view", {
                      key: 1,
                      class: "report-chart"
                    }, [
                      (vue.openBlock(true), vue.createElementBlock(
                        vue.Fragment,
                        null,
                        vue.renderList(report.card.chartData, (d, i) => {
                          return vue.openBlock(), vue.createElementBlock("view", {
                            class: "mini-bar",
                            key: i
                          }, [
                            vue.createElementVNode(
                              "text",
                              { class: "mini-label" },
                              vue.toDisplayString(d.label),
                              1
                              /* TEXT */
                            ),
                            vue.createElementVNode("view", { class: "mini-track" }, [
                              vue.createElementVNode(
                                "view",
                                {
                                  class: "mini-fill",
                                  style: vue.normalizeStyle({ width: d.value + "%", background: d.color })
                                },
                                null,
                                4
                                /* STYLE */
                              )
                            ]),
                            vue.createElementVNode(
                              "text",
                              { class: "mini-val" },
                              vue.toDisplayString(d.valText),
                              1
                              /* TEXT */
                            )
                          ]);
                        }),
                        128
                        /* KEYED_FRAGMENT */
                      ))
                    ])) : vue.createCommentVNode("v-if", true)
                  ]),
                  vue.createElementVNode("view", { class: "report-actions" }, [
                    vue.createElementVNode("button", {
                      size: "mini",
                      class: "reply-btn",
                      onClick: ($event) => $setup.replyStudent(report)
                    }, "回复指导", 8, ["onClick"])
                  ])
                ]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ])
        ])
      ])) : vue.createCommentVNode("v-if", true)
    ]);
  }
  const PagesTeacherStudentsStudents = /* @__PURE__ */ _export_sfc(_sfc_main$c, [["render", _sfc_render$b], ["__scopeId", "data-v-87e02a48"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/students/students.vue"]]);
  const _sfc_main$b = {
    __name: "detail",
    setup(__props, { expose: __expose }) {
      __expose();
      const id = vue.ref("");
      const name = vue.ref("");
      const no = vue.ref("");
      const className = vue.ref("");
      const group = vue.ref("体能A组");
      const healthStatus = vue.ref("良好");
      const activeTab = vue.ref("run");
      const runList = vue.ref([
        { date: "05-10 07:20", distance: 3.2, duration: "00:22", modeText: "普通跑步", pace: `6'52"` },
        { date: "05-12 18:05", distance: 2, duration: "00:13", modeText: "警务专项", pace: `6'30"` },
        { date: "05-15 06:40", distance: 5, duration: "00:30", modeText: "耐力跑", pace: `6'00"` }
      ]);
      const testList = vue.ref([
        { date: "05-08 09:30", testName: "引体向上", testCount: 12, result: "合格" },
        { date: "05-14 15:10", testName: "仰卧起坐", testCount: 35, result: "未合格" }
      ]);
      const totalDistance = vue.computed(() => {
        return runList.value.reduce((acc, cur) => acc + cur.distance, 0).toFixed(1);
      });
      const healthClass = vue.computed(() => {
        return healthStatus.value === "良好" ? "good" : "bad";
      });
      onLoad((opt) => {
        id.value = opt.id || "";
        name.value = opt.name || "";
        no.value = opt.no || "";
        className.value = opt.class || "";
      });
      onShow(() => {
        uni.getStorageSync("userRole") || uni.getStorageSync("role");
      });
      const contactStudent = () => {
        uni.showActionSheet({
          itemList: ["拨打电话", "发送消息"],
          success: (res) => {
            uni.showToast({ title: "操作已模拟", icon: "none" });
          }
        });
      };
      const exportReport = () => {
        uni.showToast({ title: "正在生成PDF档案...", icon: "loading" });
        setTimeout(() => {
          uni.showToast({ title: "导出成功", icon: "success" });
        }, 1500);
      };
      const __returned__ = { id, name, no, className, group, healthStatus, activeTab, runList, testList, totalDistance, healthClass, contactStudent, exportReport, ref: vue.ref, computed: vue.computed, get onShow() {
        return onShow;
      }, get onLoad() {
        return onLoad;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$a(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "detail-page" }, [
      vue.createElementVNode("view", { class: "header-card" }, [
        vue.createElementVNode("view", { class: "user-info" }, [
          vue.createElementVNode(
            "view",
            { class: "avatar" },
            vue.toDisplayString($setup.name.slice(0, 1)),
            1
            /* TEXT */
          ),
          vue.createElementVNode("view", { class: "info-content" }, [
            vue.createElementVNode("view", { class: "name-row" }, [
              vue.createElementVNode(
                "text",
                { class: "name" },
                vue.toDisplayString($setup.name),
                1
                /* TEXT */
              ),
              vue.createElementVNode(
                "text",
                {
                  class: vue.normalizeClass(["status-badge", $setup.healthClass])
                },
                vue.toDisplayString($setup.healthStatus),
                3
                /* TEXT, CLASS */
              )
            ]),
            vue.createElementVNode(
              "text",
              { class: "sub-text" },
              "学号：" + vue.toDisplayString($setup.no) + " | " + vue.toDisplayString($setup.className),
              1
              /* TEXT */
            ),
            vue.createElementVNode(
              "text",
              { class: "sub-text" },
              "分组：" + vue.toDisplayString($setup.group || "未分组"),
              1
              /* TEXT */
            )
          ])
        ]),
        vue.createElementVNode("view", { class: "stats-grid" }, [
          vue.createElementVNode("view", { class: "stat-item" }, [
            vue.createElementVNode(
              "text",
              { class: "stat-val" },
              vue.toDisplayString($setup.runList.length),
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "stat-label" }, "总跑次")
          ]),
          vue.createElementVNode("view", { class: "stat-item" }, [
            vue.createElementVNode(
              "text",
              { class: "stat-val" },
              vue.toDisplayString($setup.totalDistance),
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "stat-label" }, "总里程(km)")
          ]),
          vue.createElementVNode("view", { class: "stat-item" }, [
            vue.createElementVNode(
              "text",
              { class: "stat-val" },
              vue.toDisplayString($setup.testList.length),
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "stat-label" }, "测试次数")
          ])
        ])
      ]),
      vue.createElementVNode("view", { class: "tabs-container" }, [
        vue.createElementVNode("view", { class: "tabs" }, [
          vue.createElementVNode(
            "view",
            {
              class: vue.normalizeClass(["tab-item", { active: $setup.activeTab === "run" }]),
              onClick: _cache[0] || (_cache[0] = ($event) => $setup.activeTab = "run")
            },
            "跑步记录",
            2
            /* CLASS */
          ),
          vue.createElementVNode(
            "view",
            {
              class: vue.normalizeClass(["tab-item", { active: $setup.activeTab === "test" }]),
              onClick: _cache[1] || (_cache[1] = ($event) => $setup.activeTab = "test")
            },
            "体能测试",
            2
            /* CLASS */
          )
        ])
      ]),
      vue.createElementVNode("scroll-view", {
        "scroll-y": "",
        class: "content-area"
      }, [
        $setup.activeTab === "run" ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "list-container"
        }, [
          (vue.openBlock(true), vue.createElementBlock(
            vue.Fragment,
            null,
            vue.renderList($setup.runList, (r, i) => {
              return vue.openBlock(), vue.createElementBlock("view", {
                class: "record-card",
                key: "r" + i
              }, [
                vue.createElementVNode("view", { class: "card-left" }, [
                  vue.createElementVNode(
                    "text",
                    { class: "card-date" },
                    vue.toDisplayString(r.date),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "card-tag" },
                    vue.toDisplayString(r.modeText),
                    1
                    /* TEXT */
                  )
                ]),
                vue.createElementVNode("view", { class: "card-right" }, [
                  vue.createElementVNode("view", { class: "data-row" }, [
                    vue.createElementVNode("text", { class: "data-val" }, [
                      vue.createTextVNode(
                        vue.toDisplayString(r.distance),
                        1
                        /* TEXT */
                      ),
                      vue.createElementVNode("text", { class: "unit" }, "km")
                    ]),
                    vue.createElementVNode(
                      "text",
                      { class: "data-val" },
                      vue.toDisplayString(r.duration),
                      1
                      /* TEXT */
                    )
                  ]),
                  vue.createElementVNode(
                    "text",
                    { class: "pace" },
                    "配速 " + vue.toDisplayString(r.pace || `5'30"`),
                    1
                    /* TEXT */
                  )
                ])
              ]);
            }),
            128
            /* KEYED_FRAGMENT */
          )),
          $setup.runList.length === 0 ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 0,
            class: "empty-tip"
          }, "暂无跑步记录")) : vue.createCommentVNode("v-if", true)
        ])) : (vue.openBlock(), vue.createElementBlock("view", {
          key: 1,
          class: "list-container"
        }, [
          (vue.openBlock(true), vue.createElementBlock(
            vue.Fragment,
            null,
            vue.renderList($setup.testList, (t, i) => {
              return vue.openBlock(), vue.createElementBlock("view", {
                class: "record-card",
                key: "t" + i
              }, [
                vue.createElementVNode("view", { class: "card-left" }, [
                  vue.createElementVNode(
                    "text",
                    { class: "card-date" },
                    vue.toDisplayString(t.date),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "card-title" },
                    vue.toDisplayString(t.testName),
                    1
                    /* TEXT */
                  )
                ]),
                vue.createElementVNode("view", { class: "card-right" }, [
                  vue.createElementVNode(
                    "text",
                    {
                      class: vue.normalizeClass(["test-result", t.result === "合格" ? "pass" : "fail"])
                    },
                    vue.toDisplayString(t.result),
                    3
                    /* TEXT, CLASS */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "test-val" },
                    "成绩：" + vue.toDisplayString(t.testCount),
                    1
                    /* TEXT */
                  )
                ])
              ]);
            }),
            128
            /* KEYED_FRAGMENT */
          )),
          $setup.testList.length === 0 ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 0,
            class: "empty-tip"
          }, "暂无测试记录")) : vue.createCommentVNode("v-if", true)
        ]))
      ]),
      vue.createElementVNode("view", { class: "footer-actions" }, [
        vue.createElementVNode("button", {
          class: "action-btn outline",
          onClick: $setup.contactStudent
        }, "联系学生"),
        vue.createElementVNode("button", {
          class: "action-btn primary",
          onClick: $setup.exportReport
        }, "导出档案")
      ])
    ]);
  }
  const PagesTeacherStudentsDetail = /* @__PURE__ */ _export_sfc(_sfc_main$b, [["render", _sfc_render$a], ["__scopeId", "data-v-c1f3574c"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/students/detail.vue"]]);
  const _sfc_main$a = {
    __name: "tasks",
    setup(__props, { expose: __expose }) {
      __expose();
      const currentTab2 = vue.ref(0);
      const tasks = vue.ref([]);
      const page = vue.ref(1);
      const size = vue.ref(20);
      const total = vue.ref(0);
      const loading = vue.ref(false);
      const loadTasks = async () => {
        if (loading.value)
          return;
        loading.value = true;
        try {
          const res = await getTeacherTasks({ page: page.value, size: size.value });
          if (res.items) {
            const now = /* @__PURE__ */ new Date();
            const newTasks = res.items.map((item) => {
              const deadlineDate = new Date(item.deadline);
              const isExpired = deadlineDate < now;
              let displayType = "训练";
              if (item.type === "test")
                displayType = "考核";
              else if (item.type === "run")
                displayType = "日常";
              const completed = item.completed_count || 0;
              const totalCount = item.total_students || 0;
              const percent = totalCount > 0 ? Math.round(completed / totalCount * 100) : 0;
              return {
                id: item.id,
                title: item.title,
                type: displayType,
                desc: item.description || (item.min_distance ? `目标距离: ${item.min_distance}km` : "无具体描述"),
                status: isExpired ? "已结束" : "进行中",
                completed,
                total: totalCount,
                percent,
                deadline: item.deadline ? item.deadline.split("T")[0] : "无"
              };
            });
            if (page.value === 1) {
              tasks.value = newTasks;
            } else {
              tasks.value = [...tasks.value, ...newTasks];
            }
            total.value = res.total;
          }
        } catch (e) {
          formatAppLog("error", "at pages/teacher/tasks/tasks.vue:162", e);
          uni.showToast({ title: "加载任务失败", icon: "none" });
        } finally {
          loading.value = false;
        }
      };
      onShow(() => {
        page.value = 1;
        loadTasks();
      });
      const ongoingCount = vue.computed(() => tasks.value.filter((t) => t.status === "进行中").length);
      const totalTasks = vue.computed(() => tasks.value.length);
      const avgCompletion = vue.computed(() => {
        if (tasks.value.length === 0)
          return 0;
        const sum = tasks.value.reduce((acc, cur) => acc + cur.percent, 0);
        return Math.round(sum / tasks.value.length);
      });
      const filteredTasks = vue.computed(() => {
        if (currentTab2.value === 0) {
          return tasks.value.filter((t) => t.status === "进行中");
        } else {
          return tasks.value.filter((t) => t.status !== "进行中");
        }
      });
      const getTypeClass = (type) => {
        const map = {
          "考核": "tag-red",
          "日常": "tag-green",
          "训练": "tag-blue"
        };
        return map[type] || "tag-gray";
      };
      const isUrgent = (deadline) => {
        if (!deadline || deadline === "无")
          return false;
        const d = new Date(deadline);
        const now = /* @__PURE__ */ new Date();
        const diffTime = Math.abs(d - now);
        const diffDays = Math.ceil(diffTime / (1e3 * 60 * 60 * 24));
        return diffDays <= 3 && d > now;
      };
      const goToDetail = (task) => {
        uni.navigateTo({ url: `/pages/teacher/tasks/detail?id=${task.id}` });
      };
      const remindUnfinished = (task) => {
        uni.showToast({ title: "提醒已发送", icon: "success" });
      };
      const showActionSheet = (task) => {
        uni.showActionSheet({
          itemList: ["编辑任务", "删除任务"],
          itemColor: "#000000",
          success: async (res) => {
            if (res.tapIndex === 0) {
              uni.showToast({ title: "编辑功能开发中", icon: "none" });
            } else if (res.tapIndex === 1) {
              handleDelete(task);
            }
          }
        });
      };
      const handleDelete = (task) => {
        uni.showModal({
          title: "确认删除",
          content: `确定要删除任务"${task.title}"吗？`,
          success: async (res) => {
            if (res.confirm) {
              try {
                await deleteTask(task.id);
                uni.showToast({ title: "删除成功" });
                page.value = 1;
                loadTasks();
              } catch (e) {
                formatAppLog("error", "at pages/teacher/tasks/tasks.vue:245", e);
                uni.showToast({ title: "删除失败", icon: "none" });
              }
            }
          }
        });
      };
      const createTask = () => {
        uni.navigateTo({
          url: "/pages/teacher/tasks/create"
        });
      };
      const __returned__ = { currentTab: currentTab2, tasks, page, size, total, loading, loadTasks, ongoingCount, totalTasks, avgCompletion, filteredTasks, getTypeClass, isUrgent, goToDetail, remindUnfinished, showActionSheet, handleDelete, createTask, ref: vue.ref, computed: vue.computed, onMounted: vue.onMounted, get onShow() {
        return onShow;
      }, get getTeacherTasks() {
        return getTeacherTasks;
      }, get deleteTask() {
        return deleteTask;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$9(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "tasks-page" }, [
      vue.createElementVNode("view", { class: "dashboard-header" }, [
        vue.createElementVNode("view", { class: "header-top" }, [
          vue.createElementVNode("text", { class: "page-title" }, "任务管理"),
          vue.createElementVNode("view", { class: "header-actions" }, [
            vue.createElementVNode("view", { class: "icon-btn search" }, [
              vue.createElementVNode("text", { class: "iconfont" }, "🔍")
            ])
          ])
        ]),
        vue.createElementVNode("view", { class: "stats-card" }, [
          vue.createElementVNode("view", { class: "stat-item" }, [
            vue.createElementVNode(
              "text",
              { class: "stat-num" },
              vue.toDisplayString($setup.ongoingCount),
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "stat-label" }, "进行中")
          ]),
          vue.createElementVNode("view", { class: "stat-divider" }),
          vue.createElementVNode("view", { class: "stat-item" }, [
            vue.createElementVNode(
              "text",
              { class: "stat-num" },
              vue.toDisplayString($setup.avgCompletion) + "%",
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "stat-label" }, "平均完成率")
          ]),
          vue.createElementVNode("view", { class: "stat-divider" }),
          vue.createElementVNode("view", { class: "stat-item" }, [
            vue.createElementVNode(
              "text",
              { class: "stat-num" },
              vue.toDisplayString($setup.totalTasks),
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "stat-label" }, "累计任务")
          ])
        ])
      ]),
      vue.createElementVNode("view", { class: "tab-container" }, [
        vue.createElementVNode(
          "view",
          {
            class: vue.normalizeClass(["tab-item", { active: $setup.currentTab === 0 }]),
            onClick: _cache[0] || (_cache[0] = ($event) => $setup.currentTab = 0)
          },
          [
            vue.createTextVNode(" 进行中 "),
            $setup.currentTab === 0 ? (vue.openBlock(), vue.createElementBlock("view", {
              key: 0,
              class: "tab-line"
            })) : vue.createCommentVNode("v-if", true)
          ],
          2
          /* CLASS */
        ),
        vue.createElementVNode(
          "view",
          {
            class: vue.normalizeClass(["tab-item", { active: $setup.currentTab === 1 }]),
            onClick: _cache[1] || (_cache[1] = ($event) => $setup.currentTab = 1)
          },
          [
            vue.createTextVNode(" 历史记录 "),
            $setup.currentTab === 1 ? (vue.openBlock(), vue.createElementBlock("view", {
              key: 0,
              class: "tab-line"
            })) : vue.createCommentVNode("v-if", true)
          ],
          2
          /* CLASS */
        )
      ]),
      vue.createElementVNode(
        "scroll-view",
        {
          "scroll-y": "",
          class: "task-list",
          style: vue.normalizeStyle({ height: "calc(100vh - 380rpx)" })
        },
        [
          (vue.openBlock(true), vue.createElementBlock(
            vue.Fragment,
            null,
            vue.renderList($setup.filteredTasks, (task, index) => {
              return vue.openBlock(), vue.createElementBlock("view", {
                class: "task-card",
                key: index,
                onClick: ($event) => $setup.goToDetail(task)
              }, [
                vue.createElementVNode("view", { class: "card-header" }, [
                  vue.createElementVNode("view", { class: "tag-row" }, [
                    vue.createElementVNode(
                      "view",
                      {
                        class: vue.normalizeClass(["type-tag", $setup.getTypeClass(task.type)])
                      },
                      vue.toDisplayString(task.type),
                      3
                      /* TEXT, CLASS */
                    ),
                    vue.createElementVNode(
                      "view",
                      {
                        class: vue.normalizeClass(["deadline-tag", { urgent: $setup.isUrgent(task.deadline) }])
                      },
                      " 📅 " + vue.toDisplayString(task.deadline) + " 截止 ",
                      3
                      /* TEXT, CLASS */
                    )
                  ]),
                  vue.createElementVNode("view", {
                    class: "more-btn",
                    onClick: vue.withModifiers(($event) => $setup.showActionSheet(task), ["stop"])
                  }, "...", 8, ["onClick"])
                ]),
                vue.createElementVNode("view", { class: "card-content" }, [
                  vue.createElementVNode(
                    "text",
                    { class: "task-title" },
                    vue.toDisplayString(task.title),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "task-desc" },
                    vue.toDisplayString(task.desc),
                    1
                    /* TEXT */
                  )
                ]),
                vue.createElementVNode("view", { class: "card-progress" }, [
                  vue.createElementVNode("view", { class: "progress-info" }, [
                    vue.createElementVNode("text", { class: "info-text" }, [
                      vue.createTextVNode("完成度 "),
                      vue.createElementVNode(
                        "text",
                        { class: "highlight" },
                        vue.toDisplayString(task.percent) + "%",
                        1
                        /* TEXT */
                      )
                    ]),
                    vue.createElementVNode(
                      "text",
                      { class: "info-text sub" },
                      vue.toDisplayString(task.completed) + "/" + vue.toDisplayString(task.total) + "人",
                      1
                      /* TEXT */
                    )
                  ]),
                  vue.createElementVNode("view", { class: "progress-track" }, [
                    vue.createElementVNode(
                      "view",
                      {
                        class: "progress-bar",
                        style: vue.normalizeStyle({ width: task.percent + "%" })
                      },
                      null,
                      4
                      /* STYLE */
                    )
                  ])
                ]),
                vue.createElementVNode("view", {
                  class: "card-footer",
                  onClick: _cache[2] || (_cache[2] = vue.withModifiers(() => {
                  }, ["stop"]))
                }, [
                  vue.createElementVNode("view", { class: "avatars" }, [
                    (vue.openBlock(), vue.createElementBlock(
                      vue.Fragment,
                      null,
                      vue.renderList(3, (n) => {
                        return vue.createElementVNode(
                          "view",
                          {
                            class: "avatar",
                            key: n,
                            style: vue.normalizeStyle({ left: (n - 1) * 20 + "rpx", zIndex: 4 - n })
                          },
                          null,
                          4
                          /* STYLE */
                        );
                      }),
                      64
                      /* STABLE_FRAGMENT */
                    )),
                    vue.createElementVNode("view", {
                      class: "avatar-more",
                      style: { left: "60rpx" }
                    }, "...")
                  ]),
                  task.status === "进行中" ? (vue.openBlock(), vue.createElementBlock("button", {
                    key: 0,
                    class: "remind-btn",
                    size: "mini",
                    onClick: ($event) => $setup.remindUnfinished(task)
                  }, " 🔔 一键提醒 ", 8, ["onClick"])) : vue.createCommentVNode("v-if", true)
                ])
              ], 8, ["onClick"]);
            }),
            128
            /* KEYED_FRAGMENT */
          )),
          $setup.filteredTasks.length === 0 ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 0,
            class: "empty-state"
          }, [
            vue.createElementVNode("text", { class: "empty-text" }, "暂无任务数据")
          ])) : vue.createCommentVNode("v-if", true),
          vue.createElementVNode("view", { style: { "height": "120rpx" } })
        ],
        4
        /* STYLE */
      ),
      vue.createElementVNode("view", {
        class: "fab-btn",
        onClick: $setup.createTask
      }, [
        vue.createElementVNode("text", { class: "fab-icon" }, "+"),
        vue.createElementVNode("text", { class: "fab-text" }, "发布任务")
      ])
    ]);
  }
  const PagesTeacherTasksTasks = /* @__PURE__ */ _export_sfc(_sfc_main$a, [["render", _sfc_render$9], ["__scopeId", "data-v-6877fe60"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/tasks/tasks.vue"]]);
  const _sfc_main$9 = {
    __name: "detail",
    setup(__props, { expose: __expose }) {
      __expose();
      const taskId = vue.ref(null);
      const loading = vue.ref(true);
      const task = vue.ref({
        id: 0,
        title: "",
        status: "",
        statusText: "",
        dueDate: "",
        requirements: [],
        completedCount: 0,
        totalCount: 0
      });
      const students = vue.ref([]);
      const currentFilter = vue.ref("all");
      const completionPercentage = vue.computed(() => {
        if (task.value.totalCount === 0)
          return 0;
        return Math.round(task.value.completedCount / task.value.totalCount * 100);
      });
      const filteredStudents = vue.computed(() => {
        if (currentFilter.value === "all")
          return students.value;
        return students.value.filter((s) => s.status === currentFilter.value);
      });
      const remindStudent = (student) => {
        uni.showToast({
          title: `已发送提醒给 ${student.name}`,
          icon: "success"
        });
      };
      const goToStudentDetail = (student) => {
        uni.navigateTo({
          url: `/pages/teacher/approve/student-detail?studentId=${student.id}&studentName=${student.name}`
        });
      };
      const fetchTaskDetail = async () => {
        if (!taskId.value)
          return;
        loading.value = true;
        try {
          const res = await getTeacherTaskDetail(taskId.value);
          const reqs = [];
          if (res.type === "run") {
            reqs.push("任务类型: 跑步任务");
            if (res.min_distance)
              reqs.push(`最低距离: ${res.min_distance} km`);
            if (res.min_duration)
              reqs.push(`最低时长: ${res.min_duration} 分钟`);
          } else {
            reqs.push("任务类型: 体测任务");
            if (res.min_count)
              reqs.push(`最低次数: ${res.min_count} 次`);
          }
          if (res.description)
            reqs.push(`备注: ${res.description}`);
          const now = /* @__PURE__ */ new Date();
          const deadline = res.deadline ? new Date(res.deadline) : null;
          let status = "ongoing";
          let statusText = "进行中";
          if (deadline && deadline < now) {
            status = "ended";
            statusText = "已结束";
          }
          task.value = {
            id: res.id,
            title: res.title,
            status,
            statusText,
            dueDate: res.deadline ? res.deadline.replace("T", " ") : "无限制",
            requirements: reqs,
            completedCount: res.completed_count,
            totalCount: res.total_students
          };
          students.value = res.student_statuses.map((s) => ({
            id: s.student_id,
            name: s.student_name,
            studentId: `ID:${s.student_id}`,
            // Mock student ID if not available
            status: s.status === "completed" ? "completed" : "uncompleted",
            statusText: s.status === "completed" ? "已完成" : "未完成",
            metricValue: s.metric_value,
            avatar: ""
          }));
        } catch (e) {
          formatAppLog("error", "at pages/teacher/tasks/detail.vue:178", e);
          uni.showToast({ title: "加载失败", icon: "none" });
        } finally {
          loading.value = false;
        }
      };
      onLoad((options) => {
        if (options.id) {
          taskId.value = options.id;
          fetchTaskDetail();
        }
      });
      const __returned__ = { taskId, loading, task, students, currentFilter, completionPercentage, filteredStudents, remindStudent, goToStudentDetail, fetchTaskDetail, ref: vue.ref, computed: vue.computed, get onLoad() {
        return onLoad;
      }, get getTeacherTaskDetail() {
        return getTeacherTaskDetail;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$8(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "container" }, [
      vue.createElementVNode("view", { class: "header-card" }, [
        vue.createElementVNode("view", { class: "title-row" }, [
          vue.createElementVNode(
            "text",
            { class: "task-title" },
            vue.toDisplayString($setup.task.title),
            1
            /* TEXT */
          ),
          vue.createElementVNode(
            "view",
            {
              class: vue.normalizeClass(["status-tag", $setup.task.status])
            },
            vue.toDisplayString($setup.task.statusText),
            3
            /* TEXT, CLASS */
          )
        ]),
        vue.createElementVNode(
          "text",
          { class: "due-date" },
          "截止日期：" + vue.toDisplayString($setup.task.dueDate),
          1
          /* TEXT */
        )
      ]),
      vue.createElementVNode("view", { class: "section-card" }, [
        vue.createElementVNode("view", { class: "section-header" }, [
          vue.createElementVNode("text", { class: "section-title" }, "任务要求")
        ]),
        vue.createElementVNode("view", { class: "requirements-list" }, [
          (vue.openBlock(true), vue.createElementBlock(
            vue.Fragment,
            null,
            vue.renderList($setup.task.requirements, (req, index) => {
              return vue.openBlock(), vue.createElementBlock("view", {
                class: "req-item",
                key: index
              }, [
                vue.createElementVNode("text", { class: "dot" }, "•"),
                vue.createElementVNode(
                  "text",
                  { class: "req-text" },
                  vue.toDisplayString(req),
                  1
                  /* TEXT */
                )
              ]);
            }),
            128
            /* KEYED_FRAGMENT */
          ))
        ])
      ]),
      vue.createElementVNode("view", { class: "section-card" }, [
        vue.createElementVNode("view", { class: "section-header" }, [
          vue.createElementVNode("text", { class: "section-title" }, "完成进度"),
          vue.createElementVNode(
            "text",
            { class: "progress-stats" },
            vue.toDisplayString($setup.task.completedCount) + "/" + vue.toDisplayString($setup.task.totalCount) + " 人",
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "progress-box" }, [
          vue.createElementVNode("view", { class: "progress-bar" }, [
            vue.createElementVNode(
              "view",
              {
                class: "progress-fill",
                style: vue.normalizeStyle({ width: $setup.completionPercentage + "%" })
              },
              null,
              4
              /* STYLE */
            )
          ]),
          vue.createElementVNode(
            "text",
            { class: "percentage-text" },
            vue.toDisplayString($setup.completionPercentage) + "%",
            1
            /* TEXT */
          )
        ])
      ]),
      vue.createElementVNode("view", { class: "section-card" }, [
        vue.createElementVNode("view", { class: "section-header" }, [
          vue.createElementVNode("text", { class: "section-title" }, "参与情况"),
          vue.createElementVNode("view", { class: "filter-tabs" }, [
            vue.createElementVNode(
              "text",
              {
                class: vue.normalizeClass(["tab-item", { active: $setup.currentFilter === "all" }]),
                onClick: _cache[0] || (_cache[0] = ($event) => $setup.currentFilter = "all")
              },
              "全部",
              2
              /* CLASS */
            ),
            vue.createElementVNode(
              "text",
              {
                class: vue.normalizeClass(["tab-item", { active: $setup.currentFilter === "uncompleted" }]),
                onClick: _cache[1] || (_cache[1] = ($event) => $setup.currentFilter = "uncompleted")
              },
              "未完成",
              2
              /* CLASS */
            )
          ])
        ]),
        vue.createElementVNode("scroll-view", {
          "scroll-y": "",
          class: "student-list"
        }, [
          (vue.openBlock(true), vue.createElementBlock(
            vue.Fragment,
            null,
            vue.renderList($setup.filteredStudents, (student) => {
              return vue.openBlock(), vue.createElementBlock("view", {
                class: "student-item",
                key: student.id,
                onClick: ($event) => $setup.goToStudentDetail(student)
              }, [
                vue.createElementVNode("view", { class: "student-info" }, [
                  vue.createElementVNode("image", {
                    class: "avatar",
                    src: student.avatar || "/static/avatar.png",
                    mode: "aspectFill"
                  }, null, 8, ["src"]),
                  vue.createElementVNode("view", { class: "info-col" }, [
                    vue.createElementVNode(
                      "text",
                      { class: "name" },
                      vue.toDisplayString(student.name),
                      1
                      /* TEXT */
                    ),
                    vue.createElementVNode(
                      "text",
                      { class: "id" },
                      vue.toDisplayString(student.studentId),
                      1
                      /* TEXT */
                    ),
                    student.metricValue && student.metricValue !== "-" ? (vue.openBlock(), vue.createElementBlock(
                      "text",
                      {
                        key: 0,
                        class: "metric-val"
                      },
                      "成绩: " + vue.toDisplayString(student.metricValue),
                      1
                      /* TEXT */
                    )) : vue.createCommentVNode("v-if", true)
                  ])
                ]),
                vue.createElementVNode("view", { class: "status-col" }, [
                  vue.createElementVNode(
                    "text",
                    {
                      class: vue.normalizeClass(["status-text", student.status])
                    },
                    vue.toDisplayString(student.statusText),
                    3
                    /* TEXT, CLASS */
                  ),
                  student.status === "uncompleted" ? (vue.openBlock(), vue.createElementBlock("button", {
                    key: 0,
                    class: "remind-btn",
                    size: "mini",
                    onClick: vue.withModifiers(($event) => $setup.remindStudent(student), ["stop"])
                  }, "提醒", 8, ["onClick"])) : vue.createCommentVNode("v-if", true)
                ])
              ], 8, ["onClick"]);
            }),
            128
            /* KEYED_FRAGMENT */
          ))
        ])
      ])
    ]);
  }
  const PagesTeacherTasksDetail = /* @__PURE__ */ _export_sfc(_sfc_main$9, [["render", _sfc_render$8], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/tasks/detail.vue"]]);
  const _sfc_main$8 = {
    __name: "create",
    setup(__props, { expose: __expose }) {
      __expose();
      const taskTypes = ["run", "test"];
      const taskTypeLabels = ["跑步任务", "体能测试"];
      const groupOptions = ["all", "group_a", "group_b"];
      const groupLabels = ["全员", "体能A组", "体能B组"];
      const form = vue.ref({
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
          return uni.showToast({ title: "请完善任务信息", icon: "none" });
        }
        uni.showLoading({ title: "发布中..." });
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
          await createTeacherTask(payload);
          uni.hideLoading();
          uni.showToast({ title: "任务发布成功", icon: "success" });
          setTimeout(() => {
            uni.navigateBack();
          }, 1500);
        } catch (e) {
          uni.hideLoading();
          formatAppLog("error", "at pages/teacher/tasks/create.vue:121", e);
        }
      };
      const __returned__ = { taskTypes, taskTypeLabels, groupOptions, groupLabels, form, onTypeChange, onDateChange, onGroupChange, submitTask, ref: vue.ref, get createTeacherTask() {
        return createTeacherTask;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$7(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "create-task-page" }, [
      vue.createElementVNode("view", { class: "form-card" }, [
        vue.createElementVNode("view", { class: "form-item" }, [
          vue.createElementVNode("text", { class: "label" }, "任务标题"),
          vue.withDirectives(vue.createElementVNode(
            "input",
            {
              class: "input",
              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => $setup.form.title = $event),
              placeholder: "例如：本周5公里耐力跑"
            },
            null,
            512
            /* NEED_PATCH */
          ), [
            [vue.vModelText, $setup.form.title]
          ])
        ]),
        vue.createElementVNode("view", { class: "form-item" }, [
          vue.createElementVNode("text", { class: "label" }, "任务类型"),
          vue.createElementVNode(
            "picker",
            {
              mode: "selector",
              range: $setup.taskTypeLabels,
              onChange: $setup.onTypeChange
            },
            [
              vue.createElementVNode("view", { class: "picker-box" }, [
                vue.createElementVNode(
                  "text",
                  null,
                  vue.toDisplayString($setup.form.typeLabel || "请选择任务类型"),
                  1
                  /* TEXT */
                ),
                vue.createElementVNode("text", { class: "arrow" }, ">")
              ])
            ],
            32
            /* NEED_HYDRATION */
          )
        ]),
        vue.createElementVNode("view", { class: "form-item" }, [
          vue.createElementVNode("text", { class: "label" }, "目标距离 (km)"),
          vue.withDirectives(vue.createElementVNode(
            "input",
            {
              class: "input",
              type: "digit",
              "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => $setup.form.distance = $event),
              placeholder: "0.0"
            },
            null,
            512
            /* NEED_PATCH */
          ), [
            [vue.vModelText, $setup.form.distance]
          ])
        ]),
        vue.createElementVNode("view", { class: "form-item" }, [
          vue.createElementVNode("text", { class: "label" }, "截止日期"),
          vue.createElementVNode(
            "picker",
            {
              mode: "date",
              onChange: $setup.onDateChange
            },
            [
              vue.createElementVNode("view", { class: "picker-box" }, [
                vue.createElementVNode(
                  "text",
                  null,
                  vue.toDisplayString($setup.form.deadline || "请选择截止日期"),
                  1
                  /* TEXT */
                ),
                vue.createElementVNode("text", { class: "arrow" }, ">")
              ])
            ],
            32
            /* NEED_HYDRATION */
          )
        ]),
        vue.createElementVNode("view", { class: "form-item" }, [
          vue.createElementVNode("text", { class: "label" }, "指派对象"),
          vue.createElementVNode(
            "picker",
            {
              mode: "selector",
              range: $setup.groupLabels,
              onChange: $setup.onGroupChange
            },
            [
              vue.createElementVNode("view", { class: "picker-box" }, [
                vue.createElementVNode(
                  "text",
                  null,
                  vue.toDisplayString($setup.form.targetLabel || "全员"),
                  1
                  /* TEXT */
                ),
                vue.createElementVNode("text", { class: "arrow" }, ">")
              ])
            ],
            32
            /* NEED_HYDRATION */
          )
        ]),
        vue.createElementVNode("view", { class: "form-item vertical" }, [
          vue.createElementVNode("text", { class: "label" }, "任务说明"),
          vue.withDirectives(vue.createElementVNode(
            "textarea",
            {
              class: "textarea",
              "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $setup.form.description = $event),
              placeholder: "请输入任务的具体要求和注意事项..."
            },
            null,
            512
            /* NEED_PATCH */
          ), [
            [vue.vModelText, $setup.form.description]
          ])
        ])
      ]),
      vue.createElementVNode("view", { class: "footer-btn" }, [
        vue.createElementVNode("button", {
          class: "submit-btn",
          onClick: $setup.submitTask
        }, "发布任务")
      ])
    ]);
  }
  const PagesTeacherTasksCreate = /* @__PURE__ */ _export_sfc(_sfc_main$8, [["render", _sfc_render$7], ["__scopeId", "data-v-ddf6333b"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/tasks/create.vue"]]);
  const _sfc_main$7 = {
    __name: "exceptions",
    setup(__props, { expose: __expose }) {
      __expose();
      const currentFilter = vue.ref("all");
      const alerts = vue.ref([
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
      const pendingCount = vue.computed(() => alerts.value.length);
      const todayCount = vue.ref(5);
      const filteredAlerts = vue.computed(() => {
        if (currentFilter.value === "all")
          return alerts.value;
        return alerts.value.filter((a) => a.level === currentFilter.value);
      });
      const ignoreAlert = (id) => {
        uni.showModal({
          title: "确认忽略",
          content: "忽略后该异常将不再提醒，确认操作？",
          success: (res) => {
            if (res.confirm) {
              alerts.value = alerts.value.filter((a) => a.id !== id);
              uni.showToast({ title: "已忽略", icon: "none" });
            }
          }
        });
      };
      const notifyStudent = (alert) => {
        uni.showToast({
          title: `已发送通知给 ${alert.studentName}`,
          icon: "success"
        });
      };
      const handleAlert = (alert) => {
        uni.showActionSheet({
          itemList: ["标记为无效成绩", "标记为设备故障", "要求重测"],
          success: (res) => {
            const actions = ["无效成绩", "设备故障", "重测"];
            uni.showToast({
              title: `已标记为：${actions[res.tapIndex]}`,
              icon: "success"
            });
            alerts.value = alerts.value.filter((a) => a.id !== alert.id);
          }
        });
      };
      const __returned__ = { currentFilter, alerts, pendingCount, todayCount, filteredAlerts, ignoreAlert, notifyStudent, handleAlert, ref: vue.ref, computed: vue.computed };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$6(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "container" }, [
      vue.createElementVNode("view", { class: "header" }, [
        vue.createElementVNode("text", { class: "page-title" }, "异常处理"),
        vue.createElementVNode("view", { class: "stats-row" }, [
          vue.createElementVNode("view", { class: "stat-item" }, [
            vue.createElementVNode(
              "text",
              { class: "stat-num" },
              vue.toDisplayString($setup.pendingCount),
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "stat-desc" }, "待处理")
          ]),
          vue.createElementVNode("view", { class: "stat-item" }, [
            vue.createElementVNode(
              "text",
              { class: "stat-num" },
              vue.toDisplayString($setup.todayCount),
              1
              /* TEXT */
            ),
            vue.createElementVNode("text", { class: "stat-desc" }, "今日新增")
          ])
        ])
      ]),
      vue.createElementVNode("view", { class: "filter-bar" }, [
        vue.createElementVNode(
          "text",
          {
            class: vue.normalizeClass(["filter-item", { active: $setup.currentFilter === "all" }]),
            onClick: _cache[0] || (_cache[0] = ($event) => $setup.currentFilter = "all")
          },
          "全部",
          2
          /* CLASS */
        ),
        vue.createElementVNode(
          "text",
          {
            class: vue.normalizeClass(["filter-item", { active: $setup.currentFilter === "urgent" }]),
            onClick: _cache[1] || (_cache[1] = ($event) => $setup.currentFilter = "urgent")
          },
          "紧急",
          2
          /* CLASS */
        ),
        vue.createElementVNode(
          "text",
          {
            class: vue.normalizeClass(["filter-item", { active: $setup.currentFilter === "normal" }]),
            onClick: _cache[2] || (_cache[2] = ($event) => $setup.currentFilter = "normal")
          },
          "一般",
          2
          /* CLASS */
        )
      ]),
      vue.createElementVNode("scroll-view", {
        "scroll-y": "",
        class: "alert-list"
      }, [
        (vue.openBlock(true), vue.createElementBlock(
          vue.Fragment,
          null,
          vue.renderList($setup.filteredAlerts, (alert, index) => {
            return vue.openBlock(), vue.createElementBlock("view", {
              class: "alert-card",
              key: alert.id
            }, [
              vue.createElementVNode("view", { class: "card-header" }, [
                vue.createElementVNode("view", { class: "header-left" }, [
                  vue.createElementVNode(
                    "view",
                    {
                      class: vue.normalizeClass(["type-tag", alert.typeClass])
                    },
                    vue.toDisplayString(alert.typeText),
                    3
                    /* TEXT, CLASS */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "student-name" },
                    vue.toDisplayString(alert.studentName),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "student-id" },
                    vue.toDisplayString(alert.studentId),
                    1
                    /* TEXT */
                  )
                ]),
                vue.createElementVNode(
                  "text",
                  { class: "time" },
                  vue.toDisplayString(alert.time),
                  1
                  /* TEXT */
                )
              ]),
              vue.createElementVNode("view", { class: "card-body" }, [
                vue.createElementVNode("view", { class: "data-row" }, [
                  vue.createElementVNode("text", { class: "label" }, "异常数据："),
                  vue.createElementVNode(
                    "text",
                    { class: "value highlight" },
                    vue.toDisplayString(alert.value),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "standard" },
                    "（标准范围：" + vue.toDisplayString(alert.standard) + "）",
                    1
                    /* TEXT */
                  )
                ]),
                vue.createElementVNode("view", { class: "desc-box" }, [
                  vue.createElementVNode("text", { class: "desc-title" }, "异常说明："),
                  vue.createElementVNode(
                    "text",
                    { class: "desc-content" },
                    vue.toDisplayString(alert.description),
                    1
                    /* TEXT */
                  )
                ])
              ]),
              vue.createElementVNode("view", { class: "card-footer" }, [
                vue.createElementVNode("button", {
                  class: "action-btn ignore",
                  size: "mini",
                  onClick: ($event) => $setup.ignoreAlert(alert.id)
                }, "忽略", 8, ["onClick"]),
                vue.createElementVNode("button", {
                  class: "action-btn notify",
                  size: "mini",
                  onClick: ($event) => $setup.notifyStudent(alert)
                }, "通知学生", 8, ["onClick"]),
                vue.createElementVNode("button", {
                  class: "action-btn handle",
                  size: "mini",
                  onClick: ($event) => $setup.handleAlert(alert)
                }, "处理", 8, ["onClick"])
              ])
            ]);
          }),
          128
          /* KEYED_FRAGMENT */
        )),
        $setup.filteredAlerts.length === 0 ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "empty-state"
        }, [
          vue.createElementVNode("text", { class: "empty-text" }, "暂无异常数据")
        ])) : vue.createCommentVNode("v-if", true)
      ])
    ]);
  }
  const PagesTeacherExceptionsExceptions = /* @__PURE__ */ _export_sfc(_sfc_main$7, [["render", _sfc_render$6], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/exceptions/exceptions.vue"]]);
  const _sfc_main$6 = {
    __name: "tests",
    setup(__props, { expose: __expose }) {
      __expose();
      const currentTab2 = vue.ref("live");
      const liveStudents = vue.ref([
        { name: "张伟", action: "引体向上", currentScore: 8, isAbnormal: false, confidence: 98 },
        { name: "李强", action: "仰卧起坐", currentScore: 24, isAbnormal: true, confidence: 85 },
        { name: "王芳", action: "深蹲", currentScore: 15, isAbnormal: false, confidence: 96 },
        { name: "赵杰", action: "俯卧撑", currentScore: 12, isAbnormal: false, confidence: 99 }
      ]);
      const classSkills = vue.ref([
        { name: "爆发力", val: 85, color: "#ff6b6b" },
        { name: "耐力", val: 72, color: "#4dabf7" },
        { name: "柔韧性", val: 68, color: "#ffd43b" },
        { name: "协调性", val: 90, color: "#20C997" },
        { name: "核心力量", val: 78, color: "#a55eea" }
      ]);
      const classComparison = vue.ref([
        { label: "优秀", value: 15, percent: 30, color: "#20C997" },
        { label: "良好", value: 45, percent: 60, color: "#4dabf7" },
        { label: "及格", value: 30, percent: 45, color: "#ffd43b" },
        { label: "不及格", value: 10, percent: 20, color: "#ff6b6b" }
      ]);
      const passRates = vue.ref([
        { name: "1000米跑", rate: 85 },
        { name: "引体向上", rate: 62 },
        { name: "立定跳远", rate: 94 },
        { name: "坐位体前屈", rate: 78 }
      ]);
      const historyList = vue.ref([
        { date: "2026-05-18", testName: "全员体能摸底测试", count: 128, passRate: 92 },
        { date: "2026-05-10", testName: "力量专项考核", count: 45, passRate: 88 },
        { date: "2026-04-28", testName: "耐力跑测试", count: 128, passRate: 76 }
      ]);
      const __returned__ = { currentTab: currentTab2, liveStudents, classSkills, classComparison, passRates, historyList, ref: vue.ref };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$5(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "teacher-test-page" }, [
      vue.createElementVNode("view", { class: "header-tabs" }, [
        vue.createElementVNode(
          "view",
          {
            class: vue.normalizeClass(["tab-item", { active: $setup.currentTab === "live" }]),
            onClick: _cache[0] || (_cache[0] = ($event) => $setup.currentTab = "live")
          },
          [
            vue.createElementVNode("text", { class: "tab-title" }, "实时监控"),
            $setup.currentTab === "live" ? (vue.openBlock(), vue.createElementBlock("view", {
              key: 0,
              class: "tab-indicator"
            })) : vue.createCommentVNode("v-if", true)
          ],
          2
          /* CLASS */
        ),
        vue.createElementVNode(
          "view",
          {
            class: vue.normalizeClass(["tab-item", { active: $setup.currentTab === "analysis" }]),
            onClick: _cache[1] || (_cache[1] = ($event) => $setup.currentTab = "analysis")
          },
          [
            vue.createElementVNode("text", { class: "tab-title" }, "数据分析"),
            $setup.currentTab === "analysis" ? (vue.openBlock(), vue.createElementBlock("view", {
              key: 0,
              class: "tab-indicator"
            })) : vue.createCommentVNode("v-if", true)
          ],
          2
          /* CLASS */
        ),
        vue.createElementVNode(
          "view",
          {
            class: vue.normalizeClass(["tab-item", { active: $setup.currentTab === "history" }]),
            onClick: _cache[2] || (_cache[2] = ($event) => $setup.currentTab = "history")
          },
          [
            vue.createElementVNode("text", { class: "tab-title" }, "历史回顾"),
            $setup.currentTab === "history" ? (vue.openBlock(), vue.createElementBlock("view", {
              key: 0,
              class: "tab-indicator"
            })) : vue.createCommentVNode("v-if", true)
          ],
          2
          /* CLASS */
        )
      ]),
      $setup.currentTab === "live" ? (vue.openBlock(), vue.createElementBlock("scroll-view", {
        key: 0,
        "scroll-y": "",
        class: "content-area"
      }, [
        vue.createElementVNode("view", { class: "live-card" }, [
          vue.createElementVNode("view", { class: "live-header" }, [
            vue.createElementVNode("text", { class: "live-title" }, "当前正在进行的测试"),
            vue.createElementVNode("view", { class: "live-badge" }, "AI 评分接入中")
          ]),
          vue.createElementVNode("view", { class: "student-live-grid" }, [
            (vue.openBlock(true), vue.createElementBlock(
              vue.Fragment,
              null,
              vue.renderList($setup.liveStudents, (stu, idx) => {
                return vue.openBlock(), vue.createElementBlock("view", {
                  class: "student-monitor-card",
                  key: idx
                }, [
                  vue.createElementVNode("view", { class: "monitor-video-placeholder" }, [
                    vue.createElementVNode("text", { class: "ai-overlay" }, "AI Analyzing..."),
                    vue.createElementVNode(
                      "view",
                      {
                        class: "ai-bbox",
                        style: vue.normalizeStyle({ borderColor: stu.isAbnormal ? "#ff6b6b" : "#0f0" })
                      },
                      [
                        vue.createElementVNode(
                          "text",
                          { class: "bbox-label" },
                          vue.toDisplayString(stu.confidence) + "%",
                          1
                          /* TEXT */
                        )
                      ],
                      4
                      /* STYLE */
                    ),
                    vue.createElementVNode("view", { class: "pose-skeleton" }, [
                      vue.createElementVNode("view", { class: "bone head" }),
                      vue.createElementVNode("view", { class: "bone body" }),
                      vue.createElementVNode("view", { class: "bone arm-l" }),
                      vue.createElementVNode("view", { class: "bone arm-r" }),
                      vue.createElementVNode("view", { class: "bone leg-l" }),
                      vue.createElementVNode("view", { class: "bone leg-r" })
                    ]),
                    vue.createElementVNode(
                      "text",
                      { class: "live-score" },
                      vue.toDisplayString(stu.currentScore),
                      1
                      /* TEXT */
                    )
                  ]),
                  vue.createElementVNode("view", { class: "monitor-info" }, [
                    vue.createElementVNode(
                      "text",
                      { class: "s-name" },
                      vue.toDisplayString(stu.name),
                      1
                      /* TEXT */
                    ),
                    vue.createElementVNode(
                      "text",
                      { class: "s-action" },
                      vue.toDisplayString(stu.action),
                      1
                      /* TEXT */
                    ),
                    stu.isAbnormal ? (vue.openBlock(), vue.createElementBlock("text", {
                      key: 0,
                      class: "s-status warning"
                    }, "动作不标准")) : (vue.openBlock(), vue.createElementBlock("text", {
                      key: 1,
                      class: "s-status good"
                    }, "动作标准"))
                  ])
                ]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ])
        ])
      ])) : vue.createCommentVNode("v-if", true),
      $setup.currentTab === "analysis" ? (vue.openBlock(), vue.createElementBlock("scroll-view", {
        key: 1,
        "scroll-y": "",
        class: "content-area"
      }, [
        vue.createElementVNode("view", { class: "chart-card" }, [
          vue.createElementVNode("view", { class: "card-title" }, "班级体能综合模型"),
          vue.createElementVNode("view", { class: "skills-matrix" }, [
            (vue.openBlock(true), vue.createElementBlock(
              vue.Fragment,
              null,
              vue.renderList($setup.classSkills, (skill, idx) => {
                return vue.openBlock(), vue.createElementBlock("view", {
                  class: "skill-row",
                  key: idx
                }, [
                  vue.createElementVNode(
                    "text",
                    { class: "skill-name" },
                    vue.toDisplayString(skill.name),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode("view", { class: "skill-track" }, [
                    vue.createElementVNode(
                      "view",
                      {
                        class: "skill-bar",
                        style: vue.normalizeStyle({ width: skill.val + "%", background: skill.color })
                      },
                      null,
                      4
                      /* STYLE */
                    )
                  ]),
                  vue.createElementVNode(
                    "text",
                    { class: "skill-val" },
                    vue.toDisplayString(skill.val),
                    1
                    /* TEXT */
                  )
                ]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ]),
          vue.createElementVNode("view", { class: "analysis-summary" }, [
            vue.createElementVNode("text", { class: "summary-text" }, [
              vue.createTextVNode("💡 建议加强 "),
              vue.createElementVNode("text", { class: "highlight" }, "上肢力量"),
              vue.createTextVNode(" 专项训练")
            ])
          ])
        ]),
        vue.createElementVNode("view", { class: "chart-card" }, [
          vue.createElementVNode("view", { class: "card-title" }, "班级成绩分布对比"),
          vue.createElementVNode("view", { class: "bar-chart" }, [
            (vue.openBlock(true), vue.createElementBlock(
              vue.Fragment,
              null,
              vue.renderList($setup.classComparison, (item, idx) => {
                return vue.openBlock(), vue.createElementBlock("view", {
                  class: "bar-group",
                  key: idx
                }, [
                  vue.createElementVNode("view", { class: "bar-col" }, [
                    vue.createElementVNode(
                      "view",
                      {
                        class: "bar-fill",
                        style: vue.normalizeStyle({ height: item.percent + "%", background: item.color })
                      },
                      null,
                      4
                      /* STYLE */
                    ),
                    vue.createElementVNode(
                      "text",
                      { class: "bar-val" },
                      vue.toDisplayString(item.value),
                      1
                      /* TEXT */
                    )
                  ]),
                  vue.createElementVNode(
                    "text",
                    { class: "bar-label" },
                    vue.toDisplayString(item.label),
                    1
                    /* TEXT */
                  )
                ]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ])
        ]),
        vue.createElementVNode("view", { class: "chart-card" }, [
          vue.createElementVNode("view", { class: "card-title" }, "各项体能合格率"),
          vue.createElementVNode("view", { class: "progress-list" }, [
            (vue.openBlock(true), vue.createElementBlock(
              vue.Fragment,
              null,
              vue.renderList($setup.passRates, (p, idx) => {
                return vue.openBlock(), vue.createElementBlock("view", {
                  class: "prog-item",
                  key: idx
                }, [
                  vue.createElementVNode("view", { class: "prog-header" }, [
                    vue.createElementVNode(
                      "text",
                      { class: "prog-name" },
                      vue.toDisplayString(p.name),
                      1
                      /* TEXT */
                    ),
                    vue.createElementVNode(
                      "text",
                      { class: "prog-val" },
                      vue.toDisplayString(p.rate) + "%",
                      1
                      /* TEXT */
                    )
                  ]),
                  vue.createElementVNode("view", { class: "prog-track" }, [
                    vue.createElementVNode(
                      "view",
                      {
                        class: "prog-bar",
                        style: vue.normalizeStyle({ width: p.rate + "%" })
                      },
                      null,
                      4
                      /* STYLE */
                    )
                  ])
                ]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ])
        ])
      ])) : vue.createCommentVNode("v-if", true),
      $setup.currentTab === "history" ? (vue.openBlock(), vue.createElementBlock("scroll-view", {
        key: 2,
        "scroll-y": "",
        class: "content-area"
      }, [
        vue.createElementVNode("view", { class: "history-list" }, [
          (vue.openBlock(true), vue.createElementBlock(
            vue.Fragment,
            null,
            vue.renderList($setup.historyList, (h, idx) => {
              return vue.openBlock(), vue.createElementBlock("view", {
                class: "history-item",
                key: idx
              }, [
                vue.createElementVNode("view", { class: "h-left" }, [
                  vue.createElementVNode(
                    "text",
                    { class: "h-date" },
                    vue.toDisplayString(h.date),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "h-name" },
                    vue.toDisplayString(h.testName),
                    1
                    /* TEXT */
                  )
                ]),
                vue.createElementVNode("view", { class: "h-right" }, [
                  vue.createElementVNode(
                    "text",
                    { class: "h-stat" },
                    "参与: " + vue.toDisplayString(h.count) + "人",
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "h-stat" },
                    "合格: " + vue.toDisplayString(h.passRate) + "%",
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode("text", { class: "arrow" }, ">")
                ])
              ]);
            }),
            128
            /* KEYED_FRAGMENT */
          ))
        ])
      ])) : vue.createCommentVNode("v-if", true)
    ]);
  }
  const PagesTeacherTestsTests = /* @__PURE__ */ _export_sfc(_sfc_main$6, [["render", _sfc_render$5], ["__scopeId", "data-v-20d5ebe7"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/tests/tests.vue"]]);
  const _sfc_main$5 = {
    __name: "approve",
    setup(__props, { expose: __expose }) {
      __expose();
      const activities = vue.ref([]);
      const loadData = async () => {
        try {
          const res = await getTeacherActivities({ page: 1, size: 20 });
          if (res && res.items) {
            activities.value = res.items;
          }
        } catch (e) {
          formatAppLog("error", "at pages/teacher/approve/approve.vue:36", e);
          uni.showToast({ title: "加载待审批活动失败", icon: "none" });
        }
      };
      const handleApprove = async (id) => {
        try {
          await approveActivity(id);
          uni.showToast({ title: "审批成功" });
          loadData();
        } catch (e) {
          formatAppLog("error", "at pages/teacher/approve/approve.vue:47", e);
          uni.showToast({ title: "审批失败，请稍后重试", icon: "none" });
        }
      };
      const goToDetail = (item) => {
        uni.navigateTo({
          url: `/pages/teacher/approve/student-detail?studentId=${item.user_id}&studentName=${item.student_name}`
        });
      };
      onShow(() => {
        loadData();
      });
      const __returned__ = { activities, loadData, handleApprove, goToDetail, ref: vue.ref, get onShow() {
        return onShow;
      }, get getTeacherActivities() {
        return getTeacherActivities;
      }, get approveActivity() {
        return approveActivity;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$4(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "container" }, [
      vue.createElementVNode("view", { class: "header" }, [
        vue.createElementVNode("text", { class: "title" }, "待审批活动")
      ]),
      vue.createElementVNode("scroll-view", {
        "scroll-y": "",
        class: "list"
      }, [
        (vue.openBlock(true), vue.createElementBlock(
          vue.Fragment,
          null,
          vue.renderList($setup.activities, (item) => {
            var _a;
            return vue.openBlock(), vue.createElementBlock("view", {
              class: "item",
              key: item.id,
              onClick: ($event) => $setup.goToDetail(item)
            }, [
              vue.createElementVNode("view", { class: "info" }, [
                vue.createElementVNode(
                  "text",
                  { class: "name" },
                  vue.toDisplayString(item.student_name),
                  1
                  /* TEXT */
                ),
                vue.createElementVNode(
                  "text",
                  { class: "desc" },
                  vue.toDisplayString(item.type === "run" ? "跑步" : "体测") + " - " + vue.toDisplayString(((_a = item.metrics) == null ? void 0 : _a.distance) ? Number(item.metrics.distance).toFixed(2) : 0) + "km",
                  1
                  /* TEXT */
                ),
                vue.createElementVNode(
                  "text",
                  { class: "time" },
                  vue.toDisplayString(new Date(item.started_at).toLocaleString()),
                  1
                  /* TEXT */
                )
              ]),
              vue.createElementVNode("button", {
                class: "btn",
                onClick: vue.withModifiers(($event) => $setup.handleApprove(item.id), ["stop"]),
                disabled: item.status === "approved" || item.status === "completed",
                style: vue.normalizeStyle({ backgroundColor: item.status === "approved" || item.status === "completed" ? "#ccc" : "#20C997" })
              }, vue.toDisplayString(item.status === "approved" || item.status === "completed" ? "已通过" : "通过"), 13, ["onClick", "disabled"])
            ], 8, ["onClick"]);
          }),
          128
          /* KEYED_FRAGMENT */
        )),
        $setup.activities.length === 0 ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "empty"
        }, "暂无待审批活动")) : vue.createCommentVNode("v-if", true)
      ])
    ]);
  }
  const PagesTeacherApproveApprove = /* @__PURE__ */ _export_sfc(_sfc_main$5, [["render", _sfc_render$4], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/approve/approve.vue"]]);
  const _sfc_main$4 = {
    __name: "student-detail",
    setup(__props, { expose: __expose }) {
      __expose();
      const studentId = vue.ref(null);
      const studentName = vue.ref("");
      const activities = vue.ref([]);
      const totalDistance = vue.computed(() => {
        const dist = activities.value.reduce((acc, cur) => {
          var _a;
          return acc + (((_a = cur.metrics) == null ? void 0 : _a.distance) || 0);
        }, 0);
        return dist.toFixed(2);
      });
      const totalDuration = vue.computed(() => {
        const dur = activities.value.reduce((acc, cur) => {
          var _a;
          return acc + (((_a = cur.metrics) == null ? void 0 : _a.duration) || 0);
        }, 0);
        return Math.floor(dur / 60);
      });
      const getStatusText = (status) => {
        const map = {
          "pending": "待审批",
          "approved": "已通过",
          "rejected": "已驳回",
          "completed": "已完成",
          "finished": "已完成"
          // Default backend status
        };
        return map[status] || status;
      };
      const loadStudentData = async () => {
        if (!studentId.value)
          return;
        try {
          const res = await getTeacherStudentActivities(studentId.value, { page: 1, size: 100 });
          if (res && res.items) {
            activities.value = res.items;
          }
        } catch (e) {
          formatAppLog("error", "at pages/teacher/approve/student-detail.vue:81", e);
          uni.showToast({ title: "加载失败", icon: "none" });
        }
      };
      onLoad((options) => {
        if (options.studentId) {
          studentId.value = options.studentId;
          studentName.value = options.studentName || "学生";
          loadStudentData();
        }
      });
      const __returned__ = { studentId, studentName, activities, totalDistance, totalDuration, getStatusText, loadStudentData, ref: vue.ref, computed: vue.computed, get onLoad() {
        return onLoad;
      }, get getTeacherStudentActivities() {
        return getTeacherStudentActivities;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$3(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "container" }, [
      vue.createElementVNode("view", { class: "header" }, [
        vue.createElementVNode(
          "text",
          { class: "title" },
          vue.toDisplayString($setup.studentName) + " 的运动记录",
          1
          /* TEXT */
        )
      ]),
      vue.createElementVNode("view", { class: "stats-card" }, [
        vue.createElementVNode("view", { class: "stat-item" }, [
          vue.createElementVNode(
            "text",
            { class: "stat-num" },
            vue.toDisplayString($setup.totalDistance),
            1
            /* TEXT */
          ),
          vue.createElementVNode("text", { class: "stat-label" }, "总里程(km)")
        ]),
        vue.createElementVNode("view", { class: "stat-divider" }),
        vue.createElementVNode("view", { class: "stat-item" }, [
          vue.createElementVNode(
            "text",
            { class: "stat-num" },
            vue.toDisplayString($setup.totalDuration),
            1
            /* TEXT */
          ),
          vue.createElementVNode("text", { class: "stat-label" }, "总时长(min)")
        ]),
        vue.createElementVNode("view", { class: "stat-divider" }),
        vue.createElementVNode("view", { class: "stat-item" }, [
          vue.createElementVNode(
            "text",
            { class: "stat-num" },
            vue.toDisplayString($setup.activities.length),
            1
            /* TEXT */
          ),
          vue.createElementVNode("text", { class: "stat-label" }, "总次数")
        ])
      ]),
      vue.createElementVNode("scroll-view", {
        "scroll-y": "",
        class: "list"
      }, [
        (vue.openBlock(true), vue.createElementBlock(
          vue.Fragment,
          null,
          vue.renderList($setup.activities, (item) => {
            var _a, _b;
            return vue.openBlock(), vue.createElementBlock("view", {
              class: "item",
              key: item.id
            }, [
              vue.createElementVNode("view", { class: "info" }, [
                vue.createElementVNode(
                  "text",
                  { class: "type" },
                  vue.toDisplayString(item.type === "run" ? "跑步" : "体测"),
                  1
                  /* TEXT */
                ),
                vue.createElementVNode(
                  "text",
                  { class: "desc" },
                  vue.toDisplayString(((_a = item.metrics) == null ? void 0 : _a.distance) ? Number(item.metrics.distance).toFixed(2) : 0) + "km | " + vue.toDisplayString(((_b = item.metrics) == null ? void 0 : _b.duration) ? Math.floor(item.metrics.duration / 60) : 0) + "分钟 ",
                  1
                  /* TEXT */
                ),
                vue.createElementVNode(
                  "text",
                  { class: "time" },
                  vue.toDisplayString(new Date(item.started_at).toLocaleString()),
                  1
                  /* TEXT */
                )
              ]),
              vue.createElementVNode(
                "view",
                {
                  class: vue.normalizeClass(["status-tag", item.status])
                },
                vue.toDisplayString($setup.getStatusText(item.status)),
                3
                /* TEXT, CLASS */
              )
            ]);
          }),
          128
          /* KEYED_FRAGMENT */
        )),
        $setup.activities.length === 0 ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "empty"
        }, "暂无运动记录")) : vue.createCommentVNode("v-if", true)
      ])
    ]);
  }
  const PagesTeacherApproveStudentDetail = /* @__PURE__ */ _export_sfc(_sfc_main$4, [["render", _sfc_render$3], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/approve/student-detail.vue"]]);
  const _sfc_main$3 = {
    __name: "list",
    setup(__props, { expose: __expose }) {
      __expose();
      const activities = vue.ref([
        { id: 1, name: "五四青年节环校跑", time: "5月4日 07:00", location: "南操场", status: "报名中", statusClass: "status-active", joined: 128, image: "" },
        { id: 2, name: "周末夜跑打卡赛", time: "本周六 19:00", location: "北田径场", status: "进行中", statusClass: "status-ing", joined: 56, image: "" },
        { id: 3, name: "警务技能交流会", time: "下周三 14:00", location: "体育馆", status: "预告", statusClass: "status-future", joined: 30, image: "" }
      ]);
      const goDetail = (item) => {
        uni.navigateTo({
          url: `/pages/activity/detail?id=${item.id}&name=${item.name}`
        });
      };
      const __returned__ = { activities, goDetail, ref: vue.ref };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$2(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "activity-list-page" }, [
      vue.createElementVNode("view", { class: "header" }, [
        vue.createElementVNode("text", { class: "title" }, "跑团活动")
      ]),
      vue.createElementVNode("view", { class: "activity-list" }, [
        (vue.openBlock(true), vue.createElementBlock(
          vue.Fragment,
          null,
          vue.renderList($setup.activities, (item, index) => {
            return vue.openBlock(), vue.createElementBlock("view", {
              class: "activity-card",
              key: index,
              onClick: ($event) => $setup.goDetail(item)
            }, [
              vue.createElementVNode("image", {
                class: "act-img",
                src: item.image || "/static/activity-placeholder.png",
                mode: "aspectFill"
              }, null, 8, ["src"]),
              vue.createElementVNode("view", { class: "act-info" }, [
                vue.createElementVNode(
                  "text",
                  { class: "act-name" },
                  vue.toDisplayString(item.name),
                  1
                  /* TEXT */
                ),
                vue.createElementVNode("view", { class: "act-meta" }, [
                  vue.createElementVNode(
                    "text",
                    { class: "act-time" },
                    "📅 " + vue.toDisplayString(item.time),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "act-location" },
                    "📍 " + vue.toDisplayString(item.location),
                    1
                    /* TEXT */
                  )
                ]),
                vue.createElementVNode(
                  "view",
                  {
                    class: vue.normalizeClass(["act-status", item.statusClass])
                  },
                  [
                    vue.createElementVNode(
                      "text",
                      null,
                      vue.toDisplayString(item.status),
                      1
                      /* TEXT */
                    ),
                    vue.createElementVNode(
                      "text",
                      { class: "join-count" },
                      vue.toDisplayString(item.joined) + "人已报名",
                      1
                      /* TEXT */
                    )
                  ],
                  2
                  /* CLASS */
                )
              ])
            ], 8, ["onClick"]);
          }),
          128
          /* KEYED_FRAGMENT */
        ))
      ])
    ]);
  }
  const PagesActivityList = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["render", _sfc_render$2], ["__scopeId", "data-v-e2466d57"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/activity/list.vue"]]);
  const _imports_0 = "/static/activity-placeholder.png";
  const _sfc_main$2 = {
    __name: "detail",
    setup(__props, { expose: __expose }) {
      __expose();
      const activity = vue.ref({
        name: "加载中...",
        time: "待定",
        location: "待定",
        status: "报名中",
        joined: 0,
        limit: 100
      });
      onLoad((options) => {
        if (options.name) {
          activity.value.name = options.name;
          activity.value.time = "2026年5月4日 07:00";
          activity.value.location = "南操场主席台前";
          activity.value.joined = 128;
          activity.value.limit = 200;
        }
      });
      const handleJoin = () => {
        uni.showToast({ title: "报名成功！", icon: "success" });
      };
      const __returned__ = { activity, handleJoin, ref: vue.ref, get onLoad() {
        return onLoad;
      } };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$1(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "activity-detail-page" }, [
      vue.createElementVNode("view", { class: "banner" }, [
        vue.createElementVNode("image", {
          class: "banner-img",
          src: _imports_0,
          mode: "aspectFill"
        }),
        vue.createElementVNode("view", { class: "banner-overlay" }, [
          vue.createElementVNode(
            "text",
            { class: "act-title" },
            vue.toDisplayString($setup.activity.name),
            1
            /* TEXT */
          ),
          vue.createElementVNode(
            "text",
            { class: "act-status" },
            vue.toDisplayString($setup.activity.status),
            1
            /* TEXT */
          )
        ])
      ]),
      vue.createElementVNode("view", { class: "content-card" }, [
        vue.createElementVNode("view", { class: "info-row" }, [
          vue.createElementVNode("text", { class: "label" }, "📅 时间"),
          vue.createElementVNode(
            "text",
            { class: "value" },
            vue.toDisplayString($setup.activity.time),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "info-row" }, [
          vue.createElementVNode("text", { class: "label" }, "📍 地点"),
          vue.createElementVNode(
            "text",
            { class: "value" },
            vue.toDisplayString($setup.activity.location),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "info-row" }, [
          vue.createElementVNode("text", { class: "label" }, "👥 人数"),
          vue.createElementVNode(
            "text",
            { class: "value" },
            vue.toDisplayString($setup.activity.joined) + " / " + vue.toDisplayString($setup.activity.limit),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "divider" }),
        vue.createElementVNode("view", { class: "desc-section" }, [
          vue.createElementVNode("text", { class: "section-title" }, "活动详情"),
          vue.createElementVNode("text", { class: "desc-text" }, "这是一个模拟的活动详情页面。在这里，同学们可以查看活动的具体安排、注意事项以及奖励规则。参加活动不仅能锻炼身体，还能结识更多志同道合的朋友。")
        ])
      ]),
      vue.createElementVNode("view", { class: "bottom-bar" }, [
        vue.createElementVNode("button", {
          class: "join-btn",
          onClick: $setup.handleJoin
        }, "立即报名")
      ])
    ]);
  }
  const PagesActivityDetail = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["render", _sfc_render$1], ["__scopeId", "data-v-19f90eeb"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/activity/detail.vue"]]);
  const _sfc_main$1 = {
    __name: "ai-police",
    setup(__props, { expose: __expose }) {
      __expose();
      const isDetecting = vue.ref(false);
      const count = vue.ref(0);
      const statusText = vue.ref("准备就绪");
      const statusClass = vue.ref("normal");
      const confidence = vue.ref(0);
      const posture = vue.ref("Standing");
      let timer = null;
      const startDetect = () => {
        isDetecting.value = true;
        statusText.value = "正在检测...";
        statusClass.value = "normal";
        count.value = 0;
        startSimulationLoop();
      };
      const stopDetect = () => {
        isDetecting.value = false;
        statusText.value = "训练结束";
        clearInterval(timer);
        uni.showModal({
          title: "训练结束",
          content: `本次训练共完成 ${count.value} 次，是否查看结果？`,
          confirmText: "查看结果",
          cancelText: "取消",
          success: (res) => {
            if (res.confirm) {
              uni.showLoading({ title: "正在保存..." });
              setTimeout(() => {
                uni.hideLoading();
                uni.navigateTo({
                  url: `/pages/result/result?mode=test&project=AI智能训练&count=${count.value}&duration=0`
                });
              }, 800);
            }
          }
        });
      };
      const startSimulationLoop = () => {
        timer = setInterval(() => {
          confidence.value = (95 + Math.random() * 5).toFixed(1);
        }, 1e3);
      };
      const simValidAction = () => {
        if (!isDetecting)
          return;
        statusText.value = "动作标准";
        statusClass.value = "success";
        posture.value = "Squat Down";
        setTimeout(() => {
          count.value++;
          posture.value = "Standing";
          statusText.value = "正在检测...";
          statusClass.value = "normal";
        }, 800);
      };
      const simCheat = (type) => {
        if (!isDetecting)
          return;
        statusText.value = `警告：${type}`;
        statusClass.value = "warn";
        confidence.value = (Math.random() * 40).toFixed(1);
        uni.vibrateLong();
        uni.showToast({
          title: `检测到异常：${type}`,
          icon: "none",
          duration: 2e3
        });
        setTimeout(() => {
          statusText.value = "正在检测...";
          statusClass.value = "normal";
          confidence.value = 98.5;
        }, 2e3);
      };
      const handleCameraError = (e) => {
        formatAppLog("error", "at pages/ai-police/ai-police.vue:209", "Camera Error:", e);
        let msg = "无法访问摄像头";
        if (e.name === "NotAllowedError" || e.message === "Permission denied") {
          msg = "权限被拒绝，请在设置中允许摄像头访问";
        } else if (e.name === "NotFoundError") {
          msg = "未检测到摄像头设备";
        } else if (e.name === "NotSupportedError") {
          msg = "浏览器不支持该摄像头配置";
        }
        uni.showToast({
          title: msg,
          icon: "none",
          duration: 3e3
        });
      };
      const __returned__ = { isDetecting, count, statusText, statusClass, confidence, posture, get timer() {
        return timer;
      }, set timer(v) {
        timer = v;
      }, startDetect, stopDetect, startSimulationLoop, simValidAction, simCheat, handleCameraError, ref: vue.ref, onMounted: vue.onMounted, onUnmounted: vue.onUnmounted };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "ai-police" }, [
      vue.createElementVNode("view", { class: "camera-area" }, [
        vue.createElementVNode(
          "camera",
          {
            class: "real-camera",
            "device-position": "front",
            flash: "off",
            onError: $setup.handleCameraError
          },
          [
            vue.createElementVNode("cover-view", { class: "camera-overlay" }, [
              !$setup.isDetecting ? (vue.openBlock(), vue.createElementBlock("cover-view", {
                key: 0,
                class: "camera-tip"
              }, "请将全身置于摄像头区域内")) : (vue.openBlock(), vue.createElementBlock("cover-view", {
                key: 1,
                class: "skeleton-overlay"
              }, [
                vue.createElementVNode("cover-view", { class: "skeleton-box" })
              ])),
              $setup.isDetecting ? (vue.openBlock(), vue.createElementBlock(
                "cover-view",
                {
                  key: 2,
                  class: "debug-info"
                },
                " 置信度: " + vue.toDisplayString($setup.confidence) + "% | 姿态: " + vue.toDisplayString($setup.posture),
                1
                /* TEXT */
              )) : vue.createCommentVNode("v-if", true)
            ])
          ],
          32
          /* NEED_HYDRATION */
        )
      ]),
      vue.createElementVNode("view", { class: "dashboard" }, [
        vue.createElementVNode("view", { class: "counter-box" }, [
          vue.createElementVNode("text", { class: "count-label" }, "有效计数"),
          vue.createElementVNode(
            "text",
            { class: "count-val" },
            vue.toDisplayString($setup.count),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "status-box" }, [
          vue.createElementVNode("text", { class: "status-label" }, "当前状态"),
          vue.createElementVNode(
            "text",
            {
              class: vue.normalizeClass(["status-val", $setup.statusClass])
            },
            vue.toDisplayString($setup.statusText),
            3
            /* TEXT, CLASS */
          )
        ])
      ]),
      vue.createElementVNode("view", { class: "controls" }, [
        !$setup.isDetecting ? (vue.openBlock(), vue.createElementBlock("button", {
          key: 0,
          class: "btn-start",
          onClick: $setup.startDetect
        }, "开始AI计数")) : (vue.openBlock(), vue.createElementBlock("button", {
          key: 1,
          class: "btn-stop",
          onClick: $setup.stopDetect
        }, "结束训练")),
        vue.createElementVNode("view", { class: "simulation-tools" }, [
          vue.createElementVNode("text", { class: "tool-title" }, "开发调试：模拟场景"),
          vue.createElementVNode("view", { class: "tool-btns" }, [
            vue.createElementVNode("button", {
              size: "mini",
              onClick: $setup.simValidAction
            }, "模拟有效动作"),
            vue.createElementVNode("button", {
              size: "mini",
              onClick: _cache[0] || (_cache[0] = ($event) => $setup.simCheat("遮挡"))
            }, "模拟遮挡"),
            vue.createElementVNode("button", {
              size: "mini",
              onClick: _cache[1] || (_cache[1] = ($event) => $setup.simCheat("多人"))
            }, "模拟多人"),
            vue.createElementVNode("button", {
              size: "mini",
              onClick: _cache[2] || (_cache[2] = ($event) => $setup.simCheat("非活体"))
            }, "模拟照片攻击")
          ])
        ])
      ])
    ]);
  }
  const PagesAiPoliceAiPolice = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["render", _sfc_render], ["__scopeId", "data-v-97c40662"], ["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/pages/ai-police/ai-police.vue"]]);
  __definePage("pages/home/home", PagesHomeHome);
  __definePage("pages/run/run", PagesRunRun);
  __definePage("pages/mine/mine", PagesMineMine);
  __definePage("pages/result/result", PagesResultResult);
  __definePage("pages/login/login", PagesLoginLogin);
  __definePage("pages/register/register", PagesRegisterRegister);
  __definePage("pages/test/test", PagesTestTest);
  __definePage("pages/student/tasks/list", PagesStudentTasksList);
  __definePage("pages/teacher/home/home", PagesTeacherHomeHome);
  __definePage("pages/teacher/manage/manage", PagesTeacherManageManage);
  __definePage("pages/teacher/mine/mine", PagesTeacherMineMine);
  __definePage("pages/teacher/students/students", PagesTeacherStudentsStudents);
  __definePage("pages/teacher/students/detail", PagesTeacherStudentsDetail);
  __definePage("pages/teacher/tasks/tasks", PagesTeacherTasksTasks);
  __definePage("pages/teacher/tasks/detail", PagesTeacherTasksDetail);
  __definePage("pages/teacher/tasks/create", PagesTeacherTasksCreate);
  __definePage("pages/teacher/exceptions/exceptions", PagesTeacherExceptionsExceptions);
  __definePage("pages/teacher/tests/tests", PagesTeacherTestsTests);
  __definePage("pages/teacher/approve/approve", PagesTeacherApproveApprove);
  __definePage("pages/teacher/approve/student-detail", PagesTeacherApproveStudentDetail);
  __definePage("pages/activity/list", PagesActivityList);
  __definePage("pages/activity/detail", PagesActivityDetail);
  __definePage("pages/ai-police/ai-police", PagesAiPoliceAiPolice);
  const _sfc_main = {
    onLaunch: function() {
      try {
        const userInfo = uni.getStorageSync("userInfo");
        if (!userInfo) {
          uni.reLaunch({
            url: "/pages/login/login",
            success: () => {
            },
            fail: (err) => {
              formatAppLog("error", "at App.vue:20", "跳转登录页失败:", err);
            }
          });
        } else {
        }
      } catch (e) {
        formatAppLog("error", "at App.vue:27", "读取缓存失败:", e);
        uni.reLaunch({ url: "/pages/login/login" });
      }
    },
    onShow: function() {
    },
    onHide: function() {
    }
  };
  const App = /* @__PURE__ */ _export_sfc(_sfc_main, [["__file", "D:/PC/Document/HBuilderProjects/campus-system/fronted/App.vue"]]);
  function createApp() {
    const app = vue.createVueApp(App);
    return {
      app
    };
  }
  const { app: __app__, Vuex: __Vuex__, Pinia: __Pinia__ } = createApp();
  uni.Vuex = __Vuex__;
  uni.Pinia = __Pinia__;
  __app__.provide("__globalStyles", __uniConfig.styles);
  __app__._component.mpType = "app";
  __app__._component.render = () => {
  };
  __app__.mount("#app");
})(Vue);
