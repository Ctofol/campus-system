# 项目复盘报告：Run-Checkin 运动健康管理系统

> **文档生成日期**：2026-01-22  
> **复盘负责人**：Trae (AI Assistant)

## 1. 项目概述

*   **项目名称**：Run-Checkin (大学生运动健康管理)
*   **当前版本**：1.0.0
*   **开发周期**：2026-01-22 (本次冲刺)
*   **核心功能目标**：
    1.  **H5 端全量适配**：解决 UniApp 项目转 H5 时的硬件调用差异（摄像头、定位）。
    2.  **地图与定位修复**：解决浏览器安全策略导致的跨域阻断 (COEP) 及定位权限问题。
    3.  **用户体验优化**：修复 UI 遮挡问题，完善页面导航闭环。
    4.  **容器化部署**：提供 Docker 部署方案。

---

## 2. 错误日志分析

本次开发过程中遇到的关键技术阻碍及解决方案复盘。

### 2.1 H5 摄像头黑屏/不可用
*   **触发场景**：进入 `pages/ai-police/ai-police.vue` 或 `pages/test/test.vue` 进行 AI 识别时。
*   **完整错误信息**：
    > `camera is unsupported` (自定义提示) 或 控制台报 `Uncaught (in promise) TypeError: video.play is not a function`
*   **根本原因分析**：
    1.  **API 差异**：代码混用了小程序专用 API `uni.createCameraContext`，H5 端不支持。
    2.  **DOM 渲染时序**：使用 `v-html` 动态插入 `<video>` 标签，导致 Vue 挂载时 DOM 尚未完全渲染，`document.getElementById` 获取失败或获取到的不是 Element 对象。
    3.  **CSS 层级**：H5 原生 `<video>` 标签默认层级行为与小程序不同，导致覆盖层被挤压。
*   **最终解决方案**：
    *   [代码调整]：使用条件编译 `#ifdef H5` 隔离代码。
    *   [DOM 优化]：直接在 template 中编写 `<video>` 标签，废弃 `v-html`。
    *   [时序控制]：在 `initH5Camera` 中增加 `setTimeout` 延时确保 DOM 就绪。
    *   [UI 修复]：将覆盖层样式改为 `position: absolute; z-index: 10`。
*   **相关文件**：[ai-police.vue](file:///d:/PC/Document/HBuilderProjects/run-checkin/pages/ai-police/ai-police.vue), [test.vue](file:///d:/PC/Document/HBuilderProjects/run-checkin/pages/test/test.vue)

### 2.2 腾讯地图跨域加载失败
*   **触发场景**：`pages/run/run.vue` 加载地图组件时。
*   **完整错误信息**：
    > `Failed to load resource: net::ERR_BLOCKED_BY_RESPONSE.NotSameOriginAfterDefaultedToSameOriginByCoep`
*   **根本原因分析**：
    *   现代浏览器默认开启严格的 **COEP (Cross-Origin-Embedder-Policy)** 安全策略。
    *   腾讯地图 JS SDK 资源未设置 `Cross-Origin-Resource-Policy` 响应头，导致被浏览器安全策略拦截。
    *   `manifest.json` 中的 `headers` 配置在 Vite 开发服务器中优先级不足或存在缓存。
*   **最终解决方案**：
    *   [配置重构]：创建 `vite.config.js`，通过 `server.headers` 显式将 COEP 和 COOP 设置为 `unsafe-none`。
    *   [缓存清理]：强制清理 `unpackage` 缓存并重启服务。
*   **相关文件**：[vite.config.js](file:///d:/PC/Document/HBuilderProjects/run-checkin/vite.config.js), [manifest.json](file:///d:/PC/Document/HBuilderProjects/run-checkin/manifest.json)

### 2.3 跑步页面无法返回
*   **触发场景**：用户进入 `pages/run/run.vue` 后，无返回按钮且底部 TabBar 缺失。
*   **根本原因分析**：
    *   `run.vue` 被设计为独立页面（非 TabBar 页面跳转进入），默认隐藏了原生 TabBar。
    *   页面设计未包含返回导航栏。
*   **最终解决方案**：
    *   [组件复用]：引入 `CustomTabBar` 组件。
    *   [资源管理]：添加 `onUnmounted` 钩子清理定时器，防止后台运行。
*   **相关文件**：[run.vue](file:///d:/PC/Document/HBuilderProjects/run-checkin/pages/run/run.vue)

---

## 3. 开发流程复盘

### 3.1 技术选型
*   **框架**：UniApp (Vue3) + Vite
    *   *决策背景*：需兼顾小程序和 H5 发布，UniApp 是最优解。
    *   *关键决策*：引入 `vite.config.js` 接管 H5 开发服务器配置，而非依赖 HBuilderX 的黑盒配置，提升了可控性。

### 3.2 实施过程
1.  **阶段一：H5 硬件适配**
    *   识别 H5 环境 -> 替换 `uni.` API 为 `navigator.mediaDevices` -> 修复 DOM 和 CSS。
2.  **阶段二：网络与安全策略攻坚**
    *   发现地图跨域 -> 尝试 `manifest.json` (失败) -> 转向 `vite.config.js` (成功)。
3.  **阶段三：部署容器化**
    *   编写 `Dockerfile` -> 配置 `nginx.conf` (复用跨域头策略)。

### 3.3 遇到的典型挑战
*   **挑战**：UniApp 的 `v-html` 在 H5 端处理视频流绑定的兼容性差。
*   **对策**：放弃动态 HTML 注入，回归 Vue 原生模板语法，利用 `ref` 或 `id` 进行直接 DOM 操作。

---

## 4. 经验总结

### 4.1 成功实践
*   **条件编译是核心**：在处理跨端硬件差异（摄像头、定位）时，严格使用 `#ifdef H5` 和 `#ifndef H5` 隔离逻辑，避免 API 报错。
*   **Vite 配置优于 Manifest**：涉及底层服务器行为（如 Response Headers）时，直接操作 `vite.config.js` 比修改 `manifest.json` 更有效且生效更快。
*   **资源显式清理**：在 SPA (单页应用) 模式下，`setInterval` 和 `EventListener` 必须在 `onUnmounted` 中手动清除，否则会导致严重的内存泄漏和逻辑冲突。

### 4.2 改进方向
*   **技术债务**：
    *   `ai-police.vue` 中的 AI 逻辑在 H5 端目前为模拟实现（点击触发），需接入 `TensorFlow.js` 或类似 Web AI 库实现真实的 H5 端骨架识别。
    *   `run.vue` 的地图在 H5 端依赖 IP 定位或浏览器定位，精度低于小程序 SDK，需增加定位引导 UI。

---

## 5. 后续行动计划

*   **文档归档**：本文件归档于项目根目录 `PROJECT_REVIEW.md`。
*   **代码 TODO**：
    *   [ ] 调研 TensorFlow.js 在 UniApp H5 端的集成方案。
    *   [ ] 优化 H5 端定位失败时的用户引导流程（引导用户开启系统权限）。
*   **预防措施**：
    *   在后续开发中，凡涉及原生能力的模块，必须先行编写 H5 兼容层或降级方案。
    *   修改服务器配置后，必须强制重启服务并清理浏览器缓存。

