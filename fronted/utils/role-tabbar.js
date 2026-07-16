const TABBAR_CONFIGS = {
  student: [
    { text: '首页', iconPath: '/static/tab/tab-home-v3.png', selectedIconPath: '/static/tab/tab-home-v3-active.png' },
    { text: '运动', iconPath: '/static/tab/tab-run-v3.png', selectedIconPath: '/static/tab/tab-run-v3-active.png' },
    { text: '课程', iconPath: '/static/tab/tab-course-v3.png', selectedIconPath: '/static/tab/tab-course-v3-active.png' },
    { text: '我的', iconPath: '/static/tab/tab-mine-v3.png', selectedIconPath: '/static/tab/tab-mine-v3-active.png' }
  ],
  teacher: [
    { text: '工作台', iconPath: '/static/tab/tab-home-v3.png', selectedIconPath: '/static/tab/tab-home-v3-active.png' },
    { text: '管理', iconPath: '/static/tab/teacher-manage-v3.png', selectedIconPath: '/static/tab/teacher-manage-v3-active.png' },
    { text: '课程', iconPath: '/static/tab/tab-course-v3.png', selectedIconPath: '/static/tab/tab-course-v3-active.png' },
    { text: '我的', iconPath: '/static/tab/tab-mine-v3.png', selectedIconPath: '/static/tab/tab-mine-v3-active.png' }
  ]
};

const applyTabBarItem = (index, item) => {
  try {
    const ret = uni.setTabBarItem({
      index,
      ...item,
      fail: () => {}
    });
    if (ret && typeof ret.catch === 'function') ret.catch(() => {});
  } catch (e) {
    // Some non-tab contexts do not expose tabBar mutation.
  }
};

export const applyRoleTabBar = (role = 'student') => {
  const config = TABBAR_CONFIGS[role] || TABBAR_CONFIGS.student;
  config.forEach((item, index) => applyTabBarItem(index, item));
};

export const getRoleTabBarConfig = (role = 'student') => (
  TABBAR_CONFIGS[role] || TABBAR_CONFIGS.student
);
