# 项目复盘报告 (Phase 3): 体验优化与数据一致性

> **文档生成日期**：2026-01-30  
> **复盘负责人**：Trae (AI Assistant)  
> **关联模块**：教师端工作台、学生个人中心、任务管理

## 1. 阶段概述

本阶段开发聚焦于 **“用户体验精细化”** 与 **“前后端数据一致性”**。在核心功能跑通的基础上，重点解决了 UI 细节粗糙、无效请求报错以及关键信息缺失等影响实际使用体验的问题。

*   **核心目标**：
    1.  **消除噪音**：解决未登录状态下的无效 API 请求报错。
    2.  **逻辑修正**：确保任务列表状态（进行中/已结束）在前后端的一致性。
    3.  **视觉规范**：重构管理列表 UI，适配移动端布局，解决文字溢出。
    4.  **信息补全**：完善学生个人档案，增加班级归属感。

---

## 2. 关键问题与修复复盘 (Bug & Fix Analysis)

### 2.1 登录页 401 报错噪音
*   **触发场景**：用户未登录或 Token 过期时打开应用，控制台刷出大量红色 `401 Unauthorized` 错误。
*   **根本原因**：
    *   首页组件 (`home.vue`) 在 `onShow` 生命周期中直接并发调用业务接口 (`fetchLatestTask`)。
    *   缺乏 Token 预检机制，导致无效请求直接发送至后端。
*   **解决方案**：
    *   **防御性编程**：在 API 调用前增加 `if (!token) return` 检查。
    *   **静默处理**：针对非核心接口的 401 错误，在前端拦截器中抑制错误 Toast 弹出，仅做重定向处理。
*   **相关文件**：[home.vue](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/home/home.vue), [teacher/home.vue](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/home/home.vue)

### 2.2 任务列表“僵尸任务”问题
*   **触发场景**：教师端“快速任务”列表中，已过期的任务仍然显示在“进行中”栏目下。
*   **根本原因**：
    *   **前端过滤局限**：后端 `/teacher/tasks` 默认返回所有任务，前端仅靠简单的 `status` 字段判断，未严格校验 `deadline`。
    *   **分页失效**：前端过滤会导致分页数据不准确（例如第一页 20 条全过滤掉后显示为空，实际上第二页还有数据）。
*   **解决方案**：
    *   **后端驱动**：修改后端接口，新增 `status=active|ended` 参数，在 SQL 层直接过滤过期任务。
    *   **逻辑下沉**：前端移除复杂的过滤计算，直接透传 Tab 状态给后端。
*   **相关文件**：[main.py](file:///d:/PC/Document/HBuilderProjects/campus-system/backend/app/main.py), [tasks.vue](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/tasks/tasks.vue)

### 2.3 学生管理列表 UI 错乱
*   **触发场景**：在小屏设备上，筛选栏（班级/小组/状态）与搜索框挤压，文字换行导致布局崩坏。
*   **根本原因**：
    *   旧布局采用单行 Flex `row` 排列，未考虑移动端宽度限制。
    *   缺乏文本截断机制，长文本（如“软件工程2301班”）撑开容器。
*   **解决方案**：
    *   **布局重构**：将工具栏改为垂直堆叠布局（搜索框在上，筛选栏在下），增加空间利用率。
    *   **样式优化**：引入 `text-overflow: ellipsis` 处理长文本，统一 Picker 组件的边框与箭头样式。
    *   **视觉增强**：为状态标签（正常/请假/伤病）增加语义化背景色。
*   **相关文件**：[students.vue](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/students/students.vue)

### 2.4 个人中心缺失班级信息
*   **触发场景**：学生“我的”页面仅显示“校园运动打卡 · 学生”，未显示具体班级。
*   **根本原因**：
    *   后端 `User` 模型有关联 `Class`，但登录接口返回的 Token Payload 和 UserInfo 中未包含 `class_name`。
    *   前端仅依赖登录缓存数据，数据更新滞后。
*   **解决方案**：
    *   **Schema 扩展**：更新 `Token` 和 `UserProfile` Pydantic 模型，增加 `class_name` 字段。
    *   **接口新增**：增加 `GET /users/profile` 接口，允许前端随时获取最新档案（含班级、学号）。
    *   **前端同步**：`onShow` 时静默刷新用户信息并更新本地缓存。
*   **相关文件**：[schemas.py](file:///d:/PC/Document/HBuilderProjects/campus-system/backend/app/schemas.py), [mine.vue](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/mine/mine.vue)

---

## 3. 架构与设计优化

### 3.1 过滤逻辑后端化 (Server-Side Filtering)
*   **反思**：早期为了开发快，将大量数据获取后在前端 `filter`。这在数据量小时可行，但随着任务增多，会导致流量浪费和分页 bug。
*   **改进**：确立了 **“筛选下沉”** 原则。凡是涉及列表分页的筛选（如状态、班级、时间），必须在数据库查询层完成，严禁全量拉取后前端过滤。

### 3.2 用户信息同步策略
*   **反思**：完全依赖登录时返回的 `userInfo` 会导致数据陈旧（例如学生转班后，本地缓存仍显示旧班级）。
*   **改进**：采用 **“登录缓存 + 懒加载更新”** 策略。核心页面（如个人中心）加载时，后台静默请求 `/users/profile` 并 merge 更新本地缓存，既保证了首屏速度，又确保了数据实时性。

### 3.3 跑步轨迹与打卡搜索修复 (Running Trajectory & Checkpoint Search Fix)
*   **问题**：
    1.  学生端跑步页面，无论选择何种打卡点或如何跑动，地图路线始终显示为一条直线。
    2.  搜索不同打卡点时，导航路线始终指向同一方向（因代码写死偏移量）。
*   **根因**：
    *   `searchCheckpoint` 函数使用伪造的固定偏移坐标 (`lat+0.001`)，导致导航目标永远在东北方。
    *   `searchCheckpoint` 直接覆写 `polyline` 数组，清除已有轨迹。
    *   Vue 3 + Uni-app 地图组件响应式更新存在兼容问题。
*   **改进**：
    *   **真实搜索逻辑**：在页面加载时调用 `getCheckpoints` 获取后端真实打卡点数据；`searchCheckpoint` 改为在本地数据中进行模糊匹配查找。
    *   **状态分离 (State Separation)**：引入 `runPolyline` (轨迹) 和 `navPolyline` (导航) 独立状态。
    *   **显式合并 (Explicit Merging)**：使用 `updateMapPolyline` 函数合并图层并深拷贝 (`JSON.parse(JSON.stringify)`) 强制触发地图渲染。
    *   **即时启动**：优化起跑逻辑，立即绘制起点。

---

## 4. 后续建议 (Next Steps)

1.  **全局状态管理**：
    *   目前用户信息分散在 `uni.getStorageSync` 和各个页面的 `ref` 中。建议引入 Pinia 或 Vuex 进行全局状态管理，减少重复的 `uni.getStorageSync` 调用。
2.  **骨架屏优化**：
    *   在 `fetchTeacherStats` 或 `loadTasks` 等数据加载过程中，UI 会有短暂空白。建议添加 Skeleton 骨架屏提升感官体验。
3.  **异常边界处理**：
    *   针对网络请求失败（如断网），目前仅是 `console.error` 或简单的 Toast。需要统一的 ErrorState 组件（如“网络开小差了”占位图）。
