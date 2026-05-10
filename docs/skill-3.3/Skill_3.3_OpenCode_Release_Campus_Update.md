# OpenCode / 服务器执行 — 本次 campus-system 更新说明与粘贴提示词

面向：已在 SSH 会话中、可执行 `git`、`docker compose` 的 **OpenCode / AI 运维**。请先阅读 **「本次更新摘要」**，再把 **「粘贴用提示词」** 整段复制给 OpenCode（并改参数块）。

---

## 本次更新摘要（给人类与模型对齐用）

### 后端（FastAPI，`campus-backend` 或等价服务名）

1. **数据库迁移**（必做一次）  
   - 仓库 `backend/db_update_production.py` 会补列（含 `activities.task_id`、`tasks.starts_at` 等）。  
   - **PostgreSQL**：每条 `ALTER` 已改为独立事务，避免「列已存在」导致后续语句 `InFailedSqlTransaction`。  
   - **推荐**在 `campus-backend` 容器内执行：`python /app/db_update_production.py`（与线上一致 `DATABASE_URL`）。  
   - 若列已存在，脚本会 `[skip]`，属正常。

2. **管理端 API**（主后端 `/manage`，非独立 admin 容器时与小程序同域 `/api`）  
   - 新增：`GET /manage/users/{user_id}/activities` — 管理员查看某学生的运动记录（阳光跑 / 任务跑 / 体测归类）。

3. **任务**  
   - `POST /teacher/tasks` 等支持 `starts_at`；未到开始时间学生不可提交任务跑（`student_may_submit_task`）。  
   - 学生任务列表可能出现状态 `not_started`。

4. **阳光跑口径**  
   - `score_service.sunshine_run_filter()`：`type=run` 且 `(source=free OR source IS NULL)` 且 `task_id IS NULL`，与任务跑区分。教师统计、核验、导出等已按此过滤（具体以当前 `teacher.py` / `teacher_service.py` / `score_service.py` 为准）。

5. **注册**（`/auth/register`）  
   - 学生：**档案激活**（学号+姓名对档案）；专业班级以档案为准；选科可填，优先于档案空值。  
   - 仅允许 `student` / `teacher`；密码至少 6 位等校验加强。

### 前端

- **Uni-app**：任务跑、阳光跑结果分区、注册页与任务开始时间等（随仓库 `fronted/`）。  
- **PC 管理端**（`admin/frontend`）：学生列表「运动记录」弹窗，需重新 `npm run build` 并把 `dist` 部署到线上管理静态资源（若当前架构是主后端挂载 `admin/frontend/dist`）。

### 部署顺序建议

1. 备份数据库（至少 SQLite 文件或 mysqldump，视环境而定）。  
2. `git pull` 到目标分支。  
3. **先** `python db_update_production.py`（或等价迁移），再 **`docker compose up -d --build`** 后端，避免旧代码写新列失败。  
4. 若使用 Nginx `/api/` 反代，无需为本次单独改 location（无新路径前缀）；若有独立管理前端静态目录，需更新 `dist`。  
5. 抽测：`GET /manage/users/{student_id}/activities`（需 admin Token）、学生/教师登录、发带 `starts_at` 的任务、小程序注册流程。

---

## 文首参数块（复制后改等号右侧）

```
【执行模式】用户已授权你在当前 SSH 会话所在机器上完成下列发布步骤；不要写读后感、不要出「选1/2/3」；缺信息时只列缺失项并停。
【禁止】擅自修改未绑定 DOMAIN 的 Nginx、其他项目的 compose。
【交付】命令摘要 + 关键输出 + 回滚说明。

PROJECT_ROOT=/root/campus-system
DOMAIN=campus.gzyichenai.com
GIT_BRANCH=master
COMPOSE_SERVICE=campus-backend
TOUCH_HOST_NGINX=no
```

---

## 粘贴用提示词正文（接在参数块后）

```
你是 Linux / Git / Docker Compose 运维，正在发布 campus-system 的一次功能更新。

================================================================================
硬约束
================================================================================
1. 所有 git 操作在 PROJECT_ROOT 内；pull 前 git status；禁止 force push。
2. 后端代码在容器镜像内：git pull 后必须 docker compose up -d --build COMPOSE_SERVICE，仅 restart 不会更新 Python。
3. 执行 db_update_production.py 前提醒：备份数据库；使用与 campus-backend 相同的 DATABASE_URL（可在 compose env 或容器内确认）。
4. 不要把密钥、Token 写入可被他人读取的明文文件或聊天外日志。

================================================================================
本次业务上下文（必读）
================================================================================
- 新增列：activities.task_id、tasks.starts_at 等由 backend/db_update_production.py 自动 ALTER；跑过一次即可。
- 新接口：GET /manage/users/{user_id}/activities（管理员 JWT）。
- 学生任务状态可能含 not_started（任务 starts_at 未到）。
- 阳光跑统计与任务跑区分依赖 task_id + source；旧数据 source 可能为 NULL，后端已兼容。
- 注册：学生档案激活；前端注册成功后会写 token 跳转首页。

================================================================================
执行步骤（按顺序）
================================================================================
cd PROJECT_ROOT && git fetch origin && git checkout GIT_BRANCH && git pull origin GIT_BRANCH

# 数据库结构（在 backend 目录、与线上一致的环境下）
cd PROJECT_ROOT/backend && python db_update_production.py

# 重建并启动后端
cd PROJECT_ROOT && docker compose up -d --build COMPOSE_SERVICE

# 若管理端静态由本仓库 admin/frontend/dist 挂载，需在本机或 CI 构建后同步 dist；若你当前机器有 Node：
# cd PROJECT_ROOT/admin/frontend && npm ci && npm run build
# 再将 dist 同步到线上约定目录（以用户实际架构为准）。

# 健康检查（无敏感信息）
curl -sS -o /dev/null -w "%{http_code}" "https://DOMAIN/api/" || true
curl -sS -o /dev/null -w "%{http_code}" -X POST "https://DOMAIN/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"phone":"00000000000","password":"x"}' 
# 预期非 5xx（常见 401 JSON）

================================================================================
交付物
================================================================================
1. 实际执行的命令列表（摘要）。
2. db_update 是否报错或大量 [skip]；compose 服务是否 Up。
3. 若失败：docker compose logs COMPOSE_SERVICE 最后 40 行中的 Traceback 关键词。
4. 回滚：git checkout 到上一提交 + 数据库从备份恢复（仅当迁移已破坏数据时）；若仅代码问题可只回滚镜像。
```

---

## 与本仓库其他文档的关系

| 文档 | 用途 |
|------|------|
| `Skill_3.3_Server_Change_Prompt.md` | 通用「代改服务器」参数块 + 硬约束 |
| `Skill_3.3_Git_Pull_Deploy_Prompt.md` | 仅拉代码 + 重建 + 验证 |
| **本文** | **本次迭代** 的业务说明 + 给 OpenCode 的一键粘贴正文 |

将 `PROJECT_ROOT` / `DOMAIN` / `GIT_BRANCH` / `COMPOSE_SERVICE` 换成服务器真实值后再粘贴。

---

## 服务器拉取更新（OpenCode 一键粘贴 · 与当前 docker-compose 一致）

**适用**：仓库已在 `/root/campus-system`；Compose 含 `campus-backend`、`campus-admin-backend`、`campus-frontend-h5`、`campus-admin-frontend`、`nginx`；`ubuntu` 无 docker 组时需 **`sudo`**。

**下面整段复制给 OpenCode**（可按实际改 `PROJECT_ROOT` / `DOMAIN`；已加入 docker 组则去掉 `sudo`）：

```
【执行模式】用户已授权：在 PROJECT_ROOT 执行 git pull、在 campus-backend 容器内跑迁移、docker compose build/up。禁止 force push；禁止改与本项目无关的 Nginx 站点。

【环境常量】
PROJECT_ROOT=/root/campus-system
DOMAIN=campus.gzyichenai.com
# 无 docker 组权限时全程 sudo；否则自行去掉 sudo

================================================================================
步骤
================================================================================
1) 更新代码
   cd /root/campus-system && sudo git fetch origin && sudo git checkout master && sudo git pull origin master
   sudo git log -1 --oneline

2) 数据库迁移（仅 campus-backend 镜像内，WORKDIR=/app）
   sudo docker compose exec campus-backend python /app/db_update_production.py
   若提示找不到文件：sudo docker compose exec campus-backend ls -la /app | head

3) 重建并启动（含 H5 / 管理前后端，以镜像内 nginx 与 Dockerfile 为准）
   cd /root/campus-system
   sudo docker compose up -d --build campus-backend campus-admin-backend campus-frontend-h5 campus-admin-frontend nginx

4) 状态与健康检查
   sudo docker compose ps
   curl -sS -o /dev/null -w "api_root=%{http_code}\n" "https://campus.gzyichenai.com/api/" || true
   curl -sS -o /dev/null -w "login=%{http_code}\n" -X POST "https://campus.gzyichenai.com/api/auth/login" \
     -H "Content-Type: application/json" -d '{"phone":"0","password":"x"}' || true

================================================================================
交付物
================================================================================
- 执行的命令摘要、git 最新一行、db_update 末尾是否 [done]、compose ps、三步 curl 状态码。
- 失败时：docker compose logs --tail=60 相关服务名 + 错误关键词。

【说明】仓库 master 已含：fronted/nginx.conf 上游 campus-backend、admin/backend Dockerfile PyPI 镜像、db_update 按列独立事务；拉取后重建即可，一般无需再手改 sed / 手补列。
```
