# OpenCode / 服务器执行 — 本次 campus-system 更新说明与粘贴提示词

面向：已在 SSH 会话中、可执行 `git`、`docker compose` 的 **OpenCode / AI 运维**。请先阅读 **「本次更新摘要」**，再把 **「粘贴用提示词」** 整段复制给 OpenCode（并改参数块）。

---

## 本次更新摘要（给人类与模型对齐用）

> 以下为 **master 近期累积能力** 的发布对齐说明；以仓库当前代码为准。

### 后端（FastAPI，`campus-backend`）

1. **数据库迁移（按需，拉代码后常见）**  
   - **`backend/setup_database.py`（空白库首建）**：`create_all` + 调用 `db_update_production` + 首个管理员 + 默认 `subject_options`；容器内：`python /app/setup_database.py`。详见 **`docs/skill-3.3/Skill_3.3_Fresh_Database_Setup_Prompt.md`** 粘贴提示词。  
   - **`backend/db_update_production.py`（已有库仅补列）**：补列（如 `activities.task_id`、`tasks.starts_at` 等）；PostgreSQL 下每条 `ALTER` 独立事务。容器内：`docker compose exec campus-backend python /app/db_update_production.py`。列已存在会 `[skip]`。

2. **教师端**  
   - **`GET /teacher/student-groups`**：返回当前教师管辖学员中已出现的 `group_name`（去重）。**旧镜像未包含该路由时，公网会 404**；部署新后端并重建镜像后，未带 Token 访问应为 **401 JSON**，不是 Nginx HTML 404。  
   - **任务**：创建任务须绑定教师管辖的 **班级**（`class_id`），列表完成率/人数与详情口径对齐（`teacher.py` / `teacher_service.py`）。  
   - **学员列表**：`GET /teacher/students` 与统计共用 `get_managed_students_query`。

3. **学生端**  
   - 任务列表、提交校验等与 `class_id` / `starts_at` 一致（见 `student.py`、`task_run_service.py`）。  
   - **首页天气**：`GET /student/weather?lat=&lng=`（需登录）；后端 `TENCENT_MAP_KEY` 代理腾讯位置服务；前端 `fronted/utils/weather.js`。发版须在 **`backend/.env`** 配置 Key 并重启后端 — 见 **`Skill_3.3_Weather_Env_Deploy_Note.md`**。

4. **管理端 `/manage`**  
   - 控制台「专业活跃度」等聚合依赖班级 `major_id`；创建用户时补 `major_name`（见 `admin.py`）。  
   - 若有 `GET /manage/users/{id}/activities` 等能力，以当前 `admin.py` 为准。

5. **数据与种子**  
   - `backend/app/services/student_major_sync.py`：`sync_student_majors_from_class`，用于学生专业与行政班专业对齐；`seed.py` / 灌数脚本可能已调用，**生产一次性纠偏需备份后**再在相同 DB 环境下执行。

### 前端

- **Uni-app（`fronted/`）**：教师学员页小组筛选与 `currentGroupName` 等修复；任务创建页仅可选管辖班级；跑步/人脸与隐私相关页（`student-run.vue`、`run.vue`、`manifest.json` 等）。发**正式版/体验版**前请重新发行小程序。  
- **PC 管理端（`admin/frontend`）**：看板、班级/用户/科目等；部署静态资源需 `npm run build` 后同步 `dist`（依实际 Nginx 挂载）。

### 部署顺序建议

1. 备份数据库。  
2. `git pull` 目标分支。  
3. 确认 **`backend/.env`** 含 `TENCENT_MAP_KEY=ET4BZ-QJAL4-EMPUD-FBOLE-M23H3-3RBXD`（腾讯控制台开启 WebService + 天气服务）；详见 **`Skill_3.3_Weather_Env_Deploy_Note.md`**。  
4. 按需执行 `db_update_production.py`，再 **`docker compose up -d --build campus-backend`**（代码在镜像内时 **仅 restart 不会更新 Python**）。  
5. 按需重建管理端前后端 / H5 / nginx 服务（见根目录 `docker-compose.yml`）。  
6. 验证：`POST /api/auth/login` 非 5xx；**`GET /api/teacher/student-groups` 无 Token 为 401 JSON（非 404 HTML）**；教师学员列表、发任务、管理端看板抽测；**可选** `GET /api/student/weather?lat=&lng=` + 学生 Token 返回 `"ok":true`。

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
- 教师端新路由：GET /teacher/student-groups（旧镜像会 404；新镜像无 Token 应为 401 JSON）。
- 管理端：用户创建写 major_name；看板专业活跃度依赖班级 major_id。
- 学生任务状态可能含 not_started（任务 starts_at 未到）；任务创建须 class_id。
- 阳光跑统计与任务跑区分依赖 task_id + source；旧数据 source 可能为 NULL，后端已兼容。
- 可选数据纠偏：app.services.student_major_sync.sync_student_majors_from_class（生产须备份）。
- **学生首页天气**：backend/.env 必须有 TENCENT_MAP_KEY（本项目 Key：ET4BZ-QJAL4-EMPUD-FBOLE-M23H3-3RBXD）；改 env 后须 --build 重启 campus-backend。附录：Skill_3.3_Weather_Env_Deploy_Note.md。

================================================================================
执行步骤（按顺序）
================================================================================
cd PROJECT_ROOT && git fetch origin && git checkout GIT_BRANCH && git pull origin GIT_BRANCH

# 环境变量（学生首页天气 — 若 .env 无 TENCENT_MAP_KEY 则追加，勿删其它行）
grep -q '^TENCENT_MAP_KEY=' PROJECT_ROOT/backend/.env || echo 'TENCENT_MAP_KEY=ET4BZ-QJAL4-EMPUD-FBOLE-M23H3-3RBXD' >> PROJECT_ROOT/backend/.env

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
curl -sS -o /dev/null -w "student_groups=%{http_code}\n" "https://DOMAIN/api/teacher/student-groups" || true
# 预期 401（路由已部署）；若为 404 且非 JSON，说明后端镜像未更新或反代错误

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
   curl -sS -o /dev/null -w "student_groups=%{http_code}\n" "https://campus.gzyichenai.com/api/teacher/student-groups" || true
   # student_groups 期望 401（JSON）；404 表示路由未进新镜像

================================================================================
交付物
================================================================================
- 执行的命令摘要、git 最新一行、db_update 末尾是否 [done]、compose ps、含 student_groups 的 curl 状态码。
- 失败时：docker compose logs --tail=60 相关服务名 + 错误关键词。

【说明】仓库 master 已含：fronted/nginx.conf 上游 campus-backend、admin/backend Dockerfile PyPI 镜像、db_update 按列独立事务；拉取后重建即可，一般无需再手改 sed / 手补列。
```
