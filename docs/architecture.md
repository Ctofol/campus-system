# 系统架构

## 组成

| 目录 | 职责 | 主要技术 |
| --- | --- | --- |
| `backend/` | 学生、教师与公共 API；数据访问；AI/人脸服务 | FastAPI、SQLAlchemy |
| `fronted/` | 学生端与教师端多平台应用 | uni-app、Vue 3 |
| `admin/frontend/` | 管理后台 SPA | Vue 3、Vite、Element Plus |
| `admin/backend/` | 独立的管理后台 API | FastAPI、SQLAlchemy |

`fronted` 是现有正式目录名。为避免影响 HBuilderX、Dockerfile 和部署脚本，暂不重命名。

## 请求路径

```text
学生/教师 uni-app ─┐
                  ├── backend/app/main.py ── SQLAlchemy ── SQLite/PostgreSQL
管理后台 Vue SPA ──┘                │
                                    ├── uploads
                                    ├── 人脸识别
                                    ├── 体测视频分析
                                    └── 外部天气/AI 服务
```

## 后端分层约定

- `routers/`：HTTP 参数、身份认证、响应状态码；不新增复杂业务计算。
- `services/`：可测试的业务流程与外部服务适配。
- `models.py`：当前 ORM 模型入口；新模块逐步迁入 `modules/<domain>/models.py`。
- `schemas.py`：当前 API 模型入口；新模块逐步迁入 `modules/<domain>/schemas.py`。
- `router_registry.py`：路由注册的唯一入口，保持 `main.py` 稳定。

模块迁移采用“触碰即迁移”：只有在需求本身涉及某业务域时才移动该域代码，并要求迁移前后 OpenAPI 路径与测试结果一致。

## 业务域边界

建议的长期边界为 `auth`、`users`、`classes`、`running`、`physical_tests`、`courses`、`run_groups`、`notifications`、`face`。角色是授权维度，不是业务模块；教师和管理员路由将渐进拆分，不做一次性重写。
