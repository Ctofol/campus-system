# Campus Sports Health MVP - Phase 4: UI/UX Refinement Plan

**Date:** 2026-02-14
**Version:** 1.0.0
**Status:** Draft

## 1. Overview (概述)

本阶段遵循 **"Optimize First, Expand Later" (先优化，后扩展)** 的原则。
当前重点不在于堆砌新功能（如课程），而是**打通现有功能的断点**，重构信息架构（IA），提升交互体验，并清理冗余资源。

---

## 2. Phasing Strategy (分阶段执行策略)

### 🟢 Phase 4.1: Foundation & UI Polish (基础与体验优化)
**目标**: 让现有的功能（跑步、任务、审批）更好用，界面更清爽。
- **任务 1**: **主页重构 (Home Revamp)** - 实现 "Action-Oriented" 学生主页和教师仪表盘。
- **任务 2**: **功能精简 (Feature Trim)** - 移除不再需要的“测试监控”模块，减少系统复杂度。
- **任务 3**: **资源瘦身 (Cleanup)** - 清理未使用的静态图片和冗余 CSS。

### 🟡 Phase 4.2: Course Framework (课程框架搭建)
**目标**: 搭建课程模块的骨架，暂不填充复杂内容。
- **任务 1**: **TabBar 调整** - 新增“课程”Tab，调整导航结构。
- **任务 2**: **基础列表** - 实现课程列表页（仅展示 Demo 数据）。

### ⚪ Phase 4.3: Advanced Features (深度功能扩展)
**目标**: 完善课程交互与 AI 能力。
- **任务 1**: **互动教学** - 评论、课件下载、防作弊播放。
- **任务 2**: **AI 接入** - 替换模拟数据，尝试接入真实 AI 识别 API。

---

## 3. Student Side Optimization (学生端优化)

### 2.1 Design Goals (设计目标)
- **Holistic Sports Hub (综合运动枢纽)**: 不再单一强调跑步，而是聚合多种运动形式（跑步、AI体能、课程学习）。
- **Learn & Move (学练结合)**: 新增“体育课程”模块，强调理论与技能的学习。
- **Action-Oriented UI**: 采用极简大卡片设计，核心数据（今日运动、待办）一目了然，减少干扰。

### 2.2 Key Changes (核心变更)

#### A. 核心行动区 (Hero Section: Sports Hub)
- **现状**: 缺乏明确入口，或过于侧重单一功能。
- **计划**: 
  - **"开始运动" 聚合入口**: 点击弹出或跳转至运动选择页。
    - 选项1: **户外跑步** (GPS记录)
    - 选项2: **AI体能考核** (调用摄像头/手动上传凭证，后续接入AI)
    - 选项3: **自由练习** (手动打卡)
  - **今日运动概览**: 展示综合指标（如 `今日消耗千卡` 或 `运动时长`）。

#### B. 课程学习模块 (New: PE Courses)
- **核心逻辑 (Core Logic)**:
  - **选课机制 (Enrollment)**: 模拟大学生选课系统。学生浏览并加入课程，建立师生绑定。
  - **资源共享 (Sharing)**: 教师可引用全校公开课资源，也可上传私有内容。
  - **内容来源 (Source)**: 混合模式（本地上传 + 外部链接）。
  - **教师视角**: 创建课程 -> 上传视频/资料 -> 查看选课名单 -> 监控学习进度。
  - **学生视角**: 浏览选课 -> 加入课程 -> 接收学习任务 -> 观看视频/完成打卡。

#### C. 任务流卡片 (Task Stream)
- **优化**: 任务类型涵盖更广，除了“去跑步”，还包括“观看视频”、“完成课后作业”等。
- **样式**: 保持卡片式布局，明确区分任务类型（🏃‍♂️ 运动类 / 📺 学习类）。

#### D. 数据激励 (Motivation)
- **计划**: 底部展示 **"成长轨迹"**，综合统计跑步里程、课程学习时长和体测成绩。

---

## 3. Navigation & Structure Optimization (导航与架构优化)

### 3.1 TabBar Redesign (底部导航重构)
为了适应“学练结合”的新架构，底部的 TabBar 需要重新规划：

- **Current (现状)**: `首页` | `运动` | `体测` | `我的`
- **Proposed (新方案)**: 
  1. **首页 (Home)**: 聚合概览（任务、课程推荐、今日数据）。
  2. **课程 (Learn)**: **(New)** 视频课程库、技能教学、理论知识。
  3. **运动 (Move)**: 跑步、AI体能、自由训练的统一入口。
  4. **我的 (Profile)**: 个人数据、设置、历史记录。

> **Change Note**: 移除独立的“体测”Tab，将其作为“运动”或“首页”下的一个功能模块，释放位置给高频的“课程”模块。

---

## 4. Teacher Side Optimization (教师端优化)

### 3.1 Design Goals (设计目标)
- **Efficiency First**: 提升处理待办事项（审批、异常）的效率。
- **Global Awareness**: 一眼掌握班级整体健康与运动状况。

### 3.2 Key Changes (核心变更)

#### A. 异常预警仪表盘 (Alert Dashboard)
- **现状**: 数据展示较为平铺直叙，缺乏风险提示。
- **计划**: 
  - 顶部采用 **"红绿灯"** 色彩系统。
  - 醒目展示 **关键指标卡片**:
    - 🔴 **异常/请假**: `3人` (点击直达学生列表-异常筛选)
    - 🟠 **待审批**: `5条` (点击直达审批页)
    - 🟢 **今日打卡**: `45/50人` (点击查看未打卡名单)

#### B. 快捷操作网格 (Quick Actions)
- **计划**: 中部增加 4 格金刚区 (Grid Menu):
  - [发布任务]
  - [课程管理] (New: 上传视频/管理课件)
  - [发起体测] (未来对接 AI)
  - [数据导出]

#### C. 实时动态流 (Live Feed)
- **计划**: 底部展示 **"班级动态"**，实时更新学生的运动记录（如 "张三 刚刚完成了 3km"），增强对班级活跃度的感知。

---

## 5. Technical Implementation (技术实现路径)

### 5.1 Frontend (Vue/Uni-app)
- **Pages & Routing**:
  - 新增 `pages/tab/learn.vue` (课程Tab页)。
  - 调整 `pages.json`: 更新 tabBar 配置，图标替换。
- **Components**:
  - 新增 `components/student-home/hero-action.vue` (运动环+按钮)
  - 新增 `components/teacher-home/alert-card.vue` (预警卡片)
  - 优化 `circle-progress` 组件支持 NVUE 动画。
- **NVUE Compatibility**:
  - 确保主页 CSS 动画（如进度条增长）符合 NVUE 标准（避免 `transition: all`）。

### 5.2 Backend (FastAPI)
- **API Enhancements**:
  - 优化 `/teacher/dashboard/stats`: 确保返回结构包含点击跳转所需的 `target_url`。
  - 优化 `/student/tasks`: 增加 `urgent` 标记（如截止前24小时）。
- **New Modules**:
  - 新增 `routers/courses.py`: 处理课程 CRUD、选课、进度。
  - 数据库新增表：
    - `Course`: 课程基础信息（标题、封面、老师ID、类型）。
    - `CourseContent`: 课程章节/视频内容（支持 `local_file` 或 `external_url`）。
    - `Enrollment`: 选课记录（学生ID <-> 课程ID）。
    - `CourseProgress`: 学习进度记录。

---

## 6. Next Steps (下一步计划)

1. **Review**: 确认 TabBar 变更是否符合预期。
2. **Setup**: 创建课程相关数据库表和接口。
3. **Frontend**: 更新 TabBar 结构，开发课程列表页。
4. **Iterate**: 推进主页和教师端的改造。
