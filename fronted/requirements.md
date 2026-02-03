# 项目需求文档

## 1. 项目背景与目标
- 面向校园场景的跑步与体能考核平台，打通学生端采集与教师端管理、统计与分析。
- 形成“跑步轨迹记录 + 校园电子围栏打卡 + 专项体能测试 + 任务下发与统计”的闭环。

## 2. 技术栈与架构
- 前端：Uni-app（Vue3, Vite），适配 H5/微信小程序/App。
- 后端：FastAPI + SQLAlchemy + Pydantic，数据库 PostgreSQL。
- 数据流与原则：
  - 分页列表采用服务端筛选与统计，减少前端负担。
  - 用户信息采用“登录缓存 + 懒更新”策略，降低频繁请求。

## 3. 角色与权限
- 学生：跑步记录、校园打卡、专项体能测试、查看历史、接收并完成教师任务。
- 教师：发布任务、管理学生/班级、监控考核数据、处理异常与审批。

## 4. 核心功能需求
- 跑步页面（学生端）
  - 模式切换：普通跑步 / 专项测试 / 校园打卡。
  - 实时定位与轨迹绘制；轨迹（蓝线）与导航线（红线）分层渲染。
  - 计步（加速度传感器）与心率展示；异常提醒与目标进度。
  - 结束后提交活动数据，包含轨迹 JSON 与打卡 JSON。
  - 专项测试支持从任务页跳转携带目标距离（米）与达标配速（分钟/公里）并实时判定。
  - 参考实现：[run.vue](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue)
- 学生任务
  - 显示进行中与已结束任务；支持“去完成”跳转跑步页并传递参数。
  - 任务参数转换逻辑：min_distance(km)→米，min_duration(分钟)→pace(分钟/公里)。
  - 完成统计由服务端按类型/指标/时间窗口匹配。
  - 参考实现：[list.vue](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/student/tasks/list.vue)
- 教师端
  - 任务全生命周期管理；列表统计完成率与截止时间。
  - 学员档案与体能画像；批量提醒未完成任务。
  - 实时监控与分析页；异常处理（生理/数据/设备）。
  - 参考实现：[tasks.vue](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/tasks/tasks.vue)

## 5. 数据模型与接口要点
- Activity/ActivityMetrics：记录跑步或测试数据（距离 km、时长 s、配速、轨迹 JSON、打卡 JSON、达标标记）。
  - 模型定义：[models.py](file:///d:/PC/Document/HBuilderProjects/campus-system/backend/app/models.py)
- Task：任务要求（类型、最小距离、最小时长、最小次数、截止时间、目标班级）。
  - 模型与响应：[schemas.py](file:///d:/PC/Document/HBuilderProjects/campus-system/backend/app/schemas.py)
- 关键接口：
  - 学生提交活动：[main.py](file:///d:/PC/Document/HBuilderProjects/campus-system/backend/app/main.py#L117-L156)
  - 学生任务列表：[main.py](file:///d:/PC/Document/HBuilderProjects/campus-system/backend/app/main.py#L869-L1059)
  - 前端提交与结果展示：[run.vue](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue#L951-L1026)

## 6. 交互与业务规则
- 轨迹分层与深拷贝渲染，避免直线覆盖或不刷新。
  - 实现：updateMapPolyline 深拷贝，runPolyline/navPolyline 分层。
  - 参考：[run.vue:updateMapPolyline](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue#L340-L357)
- 普通跑步开始时清空导航线，保证地图干净。
  - 参考：[startNormalRun](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue#L907-L919)
- 专项测试参数传递与判定：在 onLoad 中解析 pace/target 并应用。
  - 参考：[onLoad](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue#L541-L557)
- 校园打卡：电子围栏判定与后端 checkIn 成功提示。
  - 参考：[updateLocationLogic](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/run/run.vue#L406-L425)

## 7. 非功能性需求
- 性能：每秒定位更新；长列表服务器分页；轨迹抖动过滤。
- 稳定性：H5 端 HTTPS/权限降级；传感器监听开启/停止保护。
- 安全：后端鉴权；不暴露敏感信息；任务按目标班级可见。
- 隐私：数据仅教学使用，遵循校内治理规范。
- 兼容：H5/小程序/App 差异化处理与降级提示。

## 8. 验收标准与测试方案
- 轨迹：开始即绘制首点，移动轨迹随更新，无直线覆盖。
- 打卡：选择打卡点后生成导航线，进入围栏范围自动提示与记录。
- 专项测试：从任务跳转后展示任务标题，配速达标判定准确。
- 数据提交：结束后成功写入后端，结果页可读取展示。
- 任务统计：服务端达成判断符合距离/时长/次数要求与时间窗口。
