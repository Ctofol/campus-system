# 灵析运动 - Cursor AI 编程助手项目核心文档

> 本文档专为 AI 编程助手（Cursor）快速理解项目而生成，聚焦代码路径、开发逻辑、技术卡点。

---

## 一、项目基础信息

### 1.1 核心定位

**灵析运动**是面向高校体育教学场景的运动健康管理系统（H5 小程序形态）。

**目标用户**：高校体育教师 + 在校学生（双角色，同一套代码按角色分流）

**核心功能模块**：
- 学生端：运动任务完成（跑步/体测）、户外跑 GPS 打卡、体能测试视频上传、课程选修、跑团联盟、健康报备/请假
- 教师端：任务布置与评分、异常运动数据监控（反作弊）、学员管理、班级管理、数据导出、测试监控
- 通用：手机号注册/登录（含图形验证码）、个人信息管理、账号安全、AI 聊天机器人

**核心业务流程**：
```
学生注册 → 绑定班级 → 教师布置任务 → 学生完成运动（上传视频/GPS数据）→ 教师评分审批 → 数据统计导出
```

---

### 1.2 技术栈详情

| 维度 | 详情 |
|------|------|
| 基础框架 | uni-app（Vue3 Composition API，`<script setup>` 语法） |
| 开发语言 | JavaScript + Vue3 |
| 后端接口 | RESTful API，JSON 格式 |
| 生产接口域名 | `http://101.37.24.171:8000`（App 端直连；H5 端通过 Nginx 反向代理，使用相对路径） |
| 后端框架 | Python FastAPI + SQLite（SQLAlchemy ORM） |
| 认证方式 | JWT Token（Bearer），存储在 `uni.getStorageSync('token')` |
| 打包方式 | HBuilderX → 发行 → 网站-H5手机版 |
| 部署方式 | Nginx 静态托管前端 + uvicorn 运行后端（服务器 `101.37.24.171`） |
| 第三方依赖 | 微信 API（暂未接入）、GPS 定位（`uni.getLocation`）、图形验证码（后端 captcha 库） |
| 小程序生命周期 | 使用 `@dcloudio/uni-app` 的 `onShow`/`onHide`，通过 ref 手动传递给子组件 |

**注意**：当前为 H5 形态，未发布微信小程序版本。`#ifdef H5` 条件编译控制平台差异代码。


---

### 1.3 代码目录结构

```
fronted/                              # 前端根目录（uni-app 项目）
├── pages/
│   ├── tab/                          # Tab 主页面（4个底部导航页）
│   │   ├── home.vue                  # 首页（角色分流：student-home / teacher-home）
│   │   ├── function.vue              # 运动页（学生：跑步/体测；教师：综合管理）
│   │   ├── learn.vue                 # 课程页（学生选课 + 教师管理课程）
│   │   └── mine.vue                  # 我的（角色分流：student-mine / teacher-mine）
│   ├── login/login.vue               # 登录页（手机号 + 图形验证码）
│   ├── register/register.vue         # 注册页（手机号注册，选择角色/班级）
│   ├── run/run.vue                   # 跑步页（委托 student-run 组件）
│   ├── test/test.vue                 # 体能测试页
│   ├── result/result.vue             # 运动结算页
│   ├── student/tasks/list.vue        # 学生任务列表
│   ├── history/history.vue           # 历史记录
│   ├── history/detail.vue            # 历史详情
│   ├── health/request.vue            # 健康报备/请假申请
│   ├── courses/                      # 课程相关页面（list/detail/player/create/edit）
│   ├── run-group/                    # 跑团联盟（discover/my/detail/activity-*）
│   ├── teacher/
│   │   ├── home/home.vue             # 教师首页（已废弃，功能移至 teacher-home 组件）
│   │   ├── tasks/tasks.vue           # 任务管理列表
│   │   ├── tasks/create.vue          # 发布新任务（含视频上传）
│   │   ├── tasks/detail.vue          # 任务详情
│   │   ├── tasks/score.vue           # 任务打分
│   │   ├── students/students.vue     # 学员管理
│   │   ├── students/detail.vue       # 学员详情
│   │   ├── exceptions/exceptions.vue # 异常运动处理（反作弊）
│   │   ├── approval/index.vue        # 待审批列表
│   │   ├── approve/approve.vue       # 活动审批
│   │   ├── class/class-list.vue      # 班级管理
│   │   ├── class/class-detail.vue    # 班级详情
│   │   ├── todos/index.vue           # 今日待办
│   │   ├── profile/edit.vue          # 个人信息编辑
│   │   ├── security/security.vue     # 账号安全
│   │   ├── security/change-password.vue # 修改密码
│   │   ├── notifications/list.vue    # 系统通知
│   │   └── resources/resources.vue  # 教学资源
│   ├── admin/                        # 管理员后台（dashboard/classes/users/import）
│   └── mine/edit-profile/            # 学生个人信息编辑
├── components/
│   ├── student-home/student-home.vue # 学生首页核心组件（任务流、跑团、GO按钮）
│   ├── student-mine/student-mine.vue # 学生我的页面组件
│   ├── student-run/student-run.vue   # 跑步核心组件（GPS、计时、轨迹）
│   ├── student-test/student-test.nvue# 体能测试组件（nvue 原生渲染）
│   ├── teacher-home/teacher-home.vue # 教师首页组件（数据概览、待办）
│   ├── teacher-manage/teacher-manage.vue # 教师综合管理（6个模块入口）
│   ├── teacher-mine/teacher-mine.vue # 教师我的页面组件
│   ├── teacher-tests/teacher-tests.vue # 测试监控组件
│   └── ai-chat-robot/ai-chat-robot.vue # AI 聊天机器人组件
├── utils/
│   └── request.js                    # 统一请求封装（token 注入、401 跳转、错误处理）
├── static/                           # 静态资源（tab 图标、头像等）
├── pages.json                        # 页面路由注册（新页面必须在此注册！）
├── App.vue                           # 全局生命周期
└── main.js                           # 入口文件

backend/
├── app/
│   ├── main.py                       # FastAPI 入口（CORS、路由注册、验证码接口）
│   ├── models.py                     # SQLAlchemy 数据模型
│   ├── schemas.py                    # Pydantic 请求/响应 Schema
│   ├── auth.py                       # JWT 认证逻辑
│   ├── database.py                   # 数据库连接（SQLite）
│   ├── response.py                   # 统一响应格式
│   ├── routers/
│   │   ├── admin.py                  # 管理员路由（/admin/*）
│   │   ├── teacher.py                # 教师路由（/teacher/*）
│   │   ├── student.py                # 学生路由（/student/*）
│   │   ├── courses.py                # 课程路由（/courses/*）
│   │   ├── run_groups.py             # 跑团路由（/run-group/*）
│   │   ├── approvals.py              # 审批路由
│   │   └── upload.py                 # 文件上传路由（/upload/file）
│   └── services/
│       └── video_score.py            # 视频评分服务（AI 评分逻辑）
└── uploads/                          # 上传文件存储目录（图片/视频）
```


---

### 1.4 关键开发约定（Cursor 必读）

```javascript
// 1. 所有 API 请求必须通过 request() 函数，不要直接用 uni.request
import { request } from '@/utils/request.js';

// 2. H5 使用相对路径（Nginx 代理），App 使用绝对路径
// request.js 中通过 #ifdef H5 条件编译自动处理，无需手动切换

// 3. 新增页面必须在 fronted/pages.json 中注册，否则 404
// 格式：{ "path": "pages/xxx/xxx", "style": { "navigationBarTitleText": "标题" } }

// 4. Tab 页面（home/function/learn/mine）通过角色分流，不要直接写业务逻辑
// 角色从 uni.getStorageSync('userRole') 读取，值为 'student' | 'teacher' | 'admin'

// 5. 生命周期传递模式（Tab 页 → 子组件）
onShow(() => {
  nextTick(() => {
    if (componentRef.value?.onPageShow) componentRef.value.onPageShow();
  });
});

// 6. 文件上传使用 uploadFile()，不要用 request()
import { uploadFile } from '@/utils/request.js';
```

---

### 1.5 运行/调试说明

**本地开发**：
```bash
# 后端启动
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端：在 fronted/utils/request.js 中取消注释本地地址
# baseUrl = 'http://127.0.0.1:8000';
# 然后在 HBuilderX 中运行到浏览器（Chrome）
```

**生产部署**：
```bash
# 1. HBuilderX → 发行 → 网站-H5手机版 → 生成 dist/build/h5/
# 2. 上传 dist/build/h5/ 内容到服务器 /var/www/campus-sports/
# 3. Nginx 配置：静态文件托管 + /auth/ /teacher/ /student/ 等路径反向代理到 :8000
```

**测试账号**：
- 教师：`13900139000 / 123456`
- 学生：`13800138000 / 123456`
- 管理员：通过 `backend/create_admin.py` 创建

**调试注意**：
- H5 打包后需重新上传服务器，修改源码不会自动生效
- 验证码接口：`GET /common/captcha` → 返回 `{image: base64, key: md5hash}`
- 登录接口：`POST /auth/login` → 返回 `{access_token, role, user_id}`

---

## 二、项目进度与完成度

**整体完成度：约 75%**

| 维度 | 完成度 |
|------|--------|
| 页面开发 | 85% |
| 接口对接 | 70% |
| 功能逻辑 | 70% |
| 测试调优 | 35% |


---

### 2.1 已完成核心模块

| 文件路径 | 功能状态 |
|----------|----------|
| `fronted/pages/login/login.vue` | ✅ 完成：手机号登录 + 图形验证码（`/common/captcha` + `/auth/login`） |
| `fronted/pages/register/register.vue` | ✅ 完成：手机号注册，角色选择（student/teacher），班级绑定 |
| `fronted/utils/request.js` | ✅ 完成：统一封装，token 注入，401 自动跳转登录，H5/App 路径条件编译 |
| `fronted/components/teacher-home/teacher-home.vue` | ✅ 完成：数据概览（今日打卡/请假待处理/运动待审批）、待办列表、学员体能概览 |
| `fronted/components/teacher-manage/teacher-manage.vue` | ✅ 完成：6个模块入口（学员管理/任务管理/异常处理/教学资源/数据导出/测试监控） |
| `fronted/components/teacher-mine/teacher-mine.vue` | ✅ 完成：导航到个人信息/账号安全/通知等真实页面 |
| `fronted/pages/teacher/exceptions/exceptions.vue` | ✅ 完成：异常运动数据展示，连接后端异常 API，支持紧急/一般筛选 |
| `fronted/pages/teacher/tasks/create.vue` | ✅ 完成：发布任务（跑步/体测类型），含体测示范视频上传（`/upload/file`） |
| `fronted/pages/teacher/tasks/tasks.vue` | ✅ 完成：任务列表，状态筛选（进行中/已结束） |
| `fronted/pages/teacher/profile/edit.vue` | ✅ 完成：个人信息编辑 |
| `fronted/pages/teacher/security/security.vue` | ✅ 完成：账号安全页 |
| `fronted/pages/teacher/security/change-password.vue` | ✅ 完成：修改密码 |
| `fronted/pages/teacher/notifications/list.vue` | ✅ 完成：系统通知列表（当前为静态数据） |
| `fronted/components/student-home/student-home.vue` | ✅ 完成：GO 按钮、任务流（最近3条）、跑团联盟入口、运动数据展示 |
| `fronted/pages/student/tasks/list.vue` | ✅ 完成：任务列表 UI（进行中/已结束 Tab），接口对接完成 |
| `fronted/pages/run-group/discover.vue` | ✅ 完成：跑团发现列表 + 创建跑团表单，接口对接完成 |
| `fronted/pages/run-group/detail.vue` | ✅ 完成：跑团详情、成员列表、活动列表 |
| `fronted/pages/tab/learn.vue` | ✅ 完成：课程列表（分类筛选）、学生选课、教师管理课程入口 |
| `fronted/pages/courses/detail.vue` | ✅ 完成：课程详情、章节列表、选课操作 |
| `fronted/pages/courses/player.vue` | ✅ 完成：视频播放页（H5 video 标签） |
| `backend/app/routers/teacher.py` | ✅ 完成：教师仪表盘统计、学员管理、任务 CRUD、审批、数据导出 |
| `backend/app/routers/student.py` | ✅ 完成：学生摘要统计、任务查询 |
| `backend/app/routers/courses.py` | ✅ 完成：课程 CRUD、选课、我的课程 |
| `backend/app/routers/run_groups.py` | ✅ 完成：跑团 CRUD、加入/退出、活动管理、排行榜 |
| `backend/app/routers/upload.py` | ✅ 完成：文件上传（图片/视频），返回访问 URL |
| `backend/app/services/video_score.py` | ✅ 完成：视频评分服务（AI 分析逻辑） |

---

### 2.2 未完成/待验证模块

| 文件路径 | 问题描述 | 技术卡点 |
|----------|----------|----------|
| `fronted/components/student-run/student-run.vue` | 跑步 GPS 轨迹记录功能待完整测试 | `uni.getLocation` 在 H5 需要 HTTPS + 用户授权；轨迹点采集频率与电量消耗平衡未调优 |
| `fronted/pages/test/test.vue` | 体能测试视频上传流程待端到端测试 | 大文件上传（>10MB）进度显示缺失；`uni.uploadFile` 超时配置未设置 |
| `fronted/pages/teacher/tasks/score.vue` | 评分页面视频播放待测试 | H5 跨域视频播放（服务器需配置 `Access-Control-Allow-Origin`）；视频 URL 拼接逻辑需验证 |
| `fronted/pages/courses/list.vue` | 硬编码了 `baseURL = 'http://127.0.0.1:8000'` | 应改用 `import { BASE_URL } from '@/utils/request.js'`，当前生产环境图片加载失败 |
| `fronted/pages/teacher/approval/index.vue` | 审批列表与 `approve/approve.vue` 功能重叠 | 两个页面逻辑未整合，存在冗余 |
| `fronted/pages/teacher/todos/index.vue` | 今日待办数据为静态 mock | 需对接后端真实待办接口 |
| `fronted/pages/teacher/notifications/list.vue` | 通知列表为静态数据 | 后端无通知推送接口，需新增 |
| `fronted/components/ai-chat-robot/ai-chat-robot.vue` | AI 聊天机器人功能未完整实现 | 后端 AI 接口未接入，当前为 UI 框架 |
| `fronted/pages/health/request.vue` | 健康报备/请假申请待测试 | 审批流程（学生提交→教师审批）端到端未验证 |
| `fronted/pages/mine/edit-profile/edit-profile.vue` | 学生个人信息编辑待测试 | 头像上传与信息保存接口对接未验证 |
| 数据导出功能 | 已实现但未完整测试 | 后端依赖 `openpyxl`，需确认服务器已安装；前端触发下载逻辑在 H5 需特殊处理 |


---

### 2.3 已知核心问题（含代码定位）

**问题 1：`courses/list.vue` 硬编码本地地址**
```javascript
// fronted/pages/courses/list.vue（约第40行）
const baseURL = 'http://127.0.0.1:8000';  // ❌ 生产环境图片加载失败
// 修复：改为
import { BASE_URL } from '@/utils/request.js';
```

**问题 2：`uploadFile` 的 `fileType` 参数声明但未使用**
```javascript
// fronted/utils/request.js
export const uploadFile = (filePath, fileType = 'image') => {
  // fileType 参数从未被读取，IDE 报 hint 警告
  // 修复：删除参数，或在 header 中根据 fileType 设置 Content-Type
}
```

**问题 3：后端不会开机自启**
- 服务器重启后 uvicorn 进程消失，需配置 systemd 服务
- 文件路径：`/etc/systemd/system/campus-backend.service`

**问题 4：Nginx 默认页面冲突**
- 需删除 `/etc/nginx/sites-enabled/default`，否则显示 Nginx 欢迎页而非前端应用

**问题 5：接口错误无统一兜底提示**
```javascript
// fronted/utils/request.js 中 server 类型错误不显示 toast
// 调用方需自行 catch 并处理，但部分页面未做 catch，导致静默失败
```

**问题 6：`student/tasks/list.vue` 的 `doTask()` 跳转逻辑不完整**
- 点击"去完成"按钮后，跑步类任务应跳转 `/pages/run/run`，体测类应跳转 `/pages/test/test`
- 当前跳转目标页面的任务 ID 传参逻辑需验证

---

## 三、后续开发方向

### 3.1 短期（1-2周，优先）

**核心任务**：

1. **修复 `courses/list.vue` 硬编码 baseURL**
   - 文件：`fronted/pages/courses/list.vue`
   - 改用 `BASE_URL` 从 `request.js` 导入，确保生产环境图片正常加载

2. **完善学生任务完成流程**
   - 文件：`fronted/pages/student/tasks/list.vue` → `doTask()` 函数
   - 逻辑：根据 `task.type`（`run`/`test`）跳转对应页面，携带 `taskId` 参数
   - 对接：`fronted/pages/run/run.vue` 和 `fronted/pages/test/test.vue` 接收 taskId 并在完成后提交

3. **验证注册/登录/验证码完整流程**
   - 文件：`fronted/pages/login/login.vue`、`fronted/pages/register/register.vue`
   - 重点：验证码 key 校验逻辑（后端 MD5 无状态验证）、token 存储与角色跳转

4. **配置后端 systemd 开机自启**
   - 在服务器创建 `/etc/systemd/system/campus-backend.service`
   - 确保服务器重启后后端自动运行

5. **测试教师评分功能**
   - 文件：`fronted/pages/teacher/tasks/score.vue`
   - 重点：视频跨域播放配置（Nginx 添加 `add_header Access-Control-Allow-Origin *`）

**代码编写重点**：
```javascript
// doTask 跳转逻辑示例
const doTask = (task) => {
  if (task.type === 'run') {
    uni.navigateTo({ url: `/pages/run/run?taskId=${task.id}` });
  } else if (task.type === 'test') {
    uni.navigateTo({ url: `/pages/test/test?taskId=${task.id}` });
  }
};
```

---

### 3.2 中期（1个月内，迭代优化）

**功能迭代**：

1. **跑步轨迹防作弊优化**
   - 文件：`fronted/components/student-run/student-run.vue`
   - 逻辑：GPS 点位合理性校验（速度异常检测）、最小有效距离阈值
   - 后端：`backend/app/routers/teacher.py` 中异常检测算法完善

2. **文件上传进度显示**
   - 文件：`fronted/pages/test/test.vue`、`fronted/utils/request.js`
   - 使用 `uni.uploadFile` 的 `onProgressUpdate` 回调显示进度条

3. **今日待办接口对接**
   - 前端：`fronted/pages/teacher/todos/index.vue`（当前静态数据）
   - 后端：新增 `GET /teacher/todos` 接口，聚合待审批/待评分数据

4. **通知系统实现**
   - 前端：`fronted/pages/teacher/notifications/list.vue`
   - 后端：新增 `notifications` 表 + CRUD 接口

5. **AI 聊天机器人接入**
   - 文件：`fronted/components/ai-chat-robot/ai-chat-robot.vue`
   - 后端：新增 `/ai/chat` 接口，对接大模型 API

**体验/性能优化**：
- `fronted/pages/tab/learn.vue`：课程列表添加分页懒加载（当前一次性加载全部）
- `fronted/utils/request.js`：server 类型错误添加默认 toast 兜底，避免静默失败
- 图片加载失败处理：全局 `@error` 事件绑定默认占位图

---

### 3.3 长期（拓展方向）

**功能拓展**：
- 接入微信小程序版本（当前仅 H5，需处理微信登录 `wx.login` 替换手机号登录）
- 运动数据可视化图表（ECharts for uni-app 集成，目标页面：`teacher-home` 学员体能概览）
- 微信运动步数同步（`wx.getWeRunData` API，需微信小程序环境）
- 小程序分享功能（`uni.share` / `wx.shareAppMessage`）

**技术优化**：
- 后端拆分：`backend/app/main.py` 中剩余路由迁移到对应 router 文件（当前 main.py 仍有部分路由）
- 数据库迁移：引入 Alembic 替代 `create_all`，支持 schema 变更
- 本地缓存策略：任务列表、课程列表添加 `uni.setStorageSync` 缓存，减少重复请求
- 接口层重构：将 `request.js` 中的 API 函数按模块拆分（auth.js / teacher.js / student.js）

---

## 四、API 接口速查

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/common/captcha` | 获取图形验证码（返回 base64 图片 + key） |
| POST | `/auth/login` | 登录（phone + password + captcha_code + captcha_key） |
| POST | `/auth/register` | 注册（phone + password + name + role + class_id） |

### 学生端
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/student/summary` | 今日运动摘要（当前用户） |
| GET | `/student/tasks` | 任务列表（?page&size&status） |
| POST | `/activity/finish` | 提交运动记录 |
| GET | `/activity/history` | 历史记录（?page&size） |
| POST | `/activity/checkin` | 打卡签到 |

### 教师端
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/teacher/stats` | 仪表盘统计 |
| GET | `/teacher/dashboard/stats` | 仪表盘详细统计 |
| GET | `/teacher/tasks` | 任务列表 |
| POST | `/teacher/tasks` | 创建任务 |
| DELETE | `/teacher/tasks/{id}` | 删除任务 |
| GET | `/teacher/activities` | 学生运动记录列表 |
| POST | `/teacher/activity/{id}/approve` | 审批运动记录 |

### 课程 & 跑团
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/courses/` | 课程列表（?category&page&size） |
| POST | `/courses/{id}/enroll` | 选课 |
| GET | `/courses/my/enrollments` | 我的课程 |
| GET | `/run-group/list` | 跑团列表 |
| POST | `/run-group/create` | 创建跑团 |
| POST | `/run-group/join?group_id=` | 加入跑团 |
| GET | `/run-group/rank` | 跑团排行榜 |

### 文件上传
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/upload/file` | 上传文件（multipart/form-data，字段名 `file`） |

> 所有需要认证的接口请求头需携带：`Authorization: Bearer {token}`

