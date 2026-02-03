# 项目复盘报告 (Phase 2): 业务修正与工程化治理

> **文档生成日期**：2026-01-29  
> **复盘负责人**：Trae (AI Assistant)  
> **关联版本**：Phase 4 & 5 (详见 CHANGELOG.md)

## 1. 阶段概述

本阶段重点解决了 **H5 环境下的业务闭环问题** 以及 **项目工程化治理**。从单纯的“功能实现”转向“用户体验优化”和“可维护性提升”。

*   **核心目标**：
    1.  **数据准确性**：修正体测数据与跑步数据的混淆问题。
    2.  **流程闭环**：打通视频证据的上传、存储与教师端预览链路。
    3.  **工程规范**：清理冗余文件，规范 Git 工作流。

---

## 2. 关键问题与修复复盘 (Bug & Fix Analysis)

### 2.1 视频上传 404 错误
*   **触发场景**：学生在体测结束后，点击提交成绩，视频上传请求失败。
*   **错误现象**：Network 面板显示 `POST /activity/evidence` 返回 `404 Not Found`。
*   **根本原因**：
    *   后端 API 路由重构后，移除了独立的证据上传接口，改为在 `/activity/finish` 中统一处理。
    *   前端 `test.vue` 仍保留了旧的异步上传逻辑。
*   **解决方案**：
    *   **接口合并**：前端移除单独的 `uploadEvidence` 调用。
    *   **数据聚合**：在提交成绩的 JSON Payload 中直接包含 `evidence` 数组（包含视频 URL）。
*   **相关文件**：[test.vue](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/test/test.vue)

### 2.2 体测数据单位显示错误
*   **触发场景**：教师端审批列表或学生端详情页，体测项目（如引体向上）显示为“XX 公里”。
*   **根本原因**：
    *   前端组件（`student-detail.vue`, `approve.vue`）复用了跑步模块的展示逻辑，默认统一使用 `distance` (km) 作为核心指标。
    *   未针对 `activity.type` 进行条件渲染。
*   **解决方案**：
    *   **多态展示**：引入 `v-if/v-else` 判断。
        *   `type === 'run'` -> 显示 `distance` (km)
        *   `type === 'physical_test'` -> 显示 `count` (次/个)
*   **相关文件**：[student-detail.vue](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/approve/student-detail.vue), [approve.vue](file:///d:/PC/Document/HBuilderProjects/campus-system/fronted/pages/teacher/approve/approve.vue)

### 2.3 教师端视频无法播放
*   **触发场景**：教师点击“查看媒体”按钮，弹窗黑屏或无反应。
*   **根本原因**：
    *   数据结构解析错误：后端返回的 `evidence` 是数组，但前端未正确提取 `data_ref` 字段。
    *   `video` 标签在部分 H5 浏览器中被遮挡或层级 (z-index) 问题。
*   **解决方案**：
    *   **逻辑修正**：增加 `hasMedia` 过滤函数，确保只渲染有效的视频证据。
    *   **组件优化**：使用 Uni-app 的 `<video>` 组件并强制设置高层级。

### 2.4 Git 仓库体积膨胀
*   **现象**：`git status` 显示大量 `unpackage/` 下的变动，仓库体积激增。
*   **根本原因**：项目初始化时未配置 `.gitignore`，导致编译缓存（临时文件）被纳入版本控制。
*   **解决方案**：
    *   **清理**：编写脚本删除 `unpackage`, `__pycache__`, `uploads/*`。
    *   **规范**：新增 `.gitignore` 并强制从暂存区移除垃圾文件 (`git rm -r --cached`)。

---

## 3. 架构与设计优化

### 3.1 接口设计的原子性
*   **反思**：最初将“成绩提交”和“证据上传”分为两个 HTTP 请求，导致了状态不一致风险（如成绩提交成功但视频上传失败）。
*   **改进**：采用**聚合提交**模式。虽然增加了单个请求的 Payload 大小，但保证了业务事务的原子性——要么全部成功，要么全部失败，降低了脏数据的可能性。

### 3.2 前端展示的防御性编程
*   **反思**：在展示层直接读取 `metrics.distance` 导致了非跑步项目的显示 bug。
*   **改进**：在 UI 组件中强制加入类型检查（Type Guard）。
    ```javascript
    // 改进前
    <text>{{ item.metrics.distance }} km</text>

    // 改进后
    <text v-if="item.type === 'run'">{{ item.metrics.distance }} km</text>
    <text v-else>{{ item.metrics.count }} 次</text>
    ```

---

## 4. 后续建议 (Next Steps)

1.  **自动化测试**：
    *   当前测试主要依赖人工点击（真机/浏览器）。建议引入简单的单元测试，特别是针对 `submitResult` 这种核心逻辑。
2.  **资源管理**：
    *   目前视频直接存储在后端本地磁盘 (`backend/uploads`)。随着数据量增长，建议迁移至对象存储 (OSS/S3) 以减轻服务器压力。
3.  **异常监控**：
    *   H5 端目前缺乏全局错误捕获，建议接入 Sentry 或简单的日志上报接口，以便排查用户端的白屏或接口异常。
