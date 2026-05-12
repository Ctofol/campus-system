# Skill 3.3 — 空白库：拉取代码并一次性搭建数据库（粘贴用提示词）

用途：服务器上 **新建空库** 或 **表已清空需从零恢复** 时，让 AI 执行：**拉最新代码 → 重建后端镜像 → 运行 `setup_database.py`**（建表 + 幂等补列 + 首个管理员 + 默认选科）。

仓库脚本：`backend/setup_database.py`（与 `SQLALCHEMY_DATABASE_URL` 一致；Docker 内路径 `/app/setup_database.py`）。

与「仅增量补列」对照：`Skill_3.3_Git_Pull_Deploy_Prompt.md` 里的 `db_update_production.py`。  
与「灌演示业务数据」对照：空白库搭好后若需要假数据，**再**在相同环境下执行 `python seed.py`（生产慎用）。

---

## 文首参数块（复制后改等号右侧）

```
【执行模式】用户已授权你在当前 SSH 会话所在机器上执行命令；不要写读后感、不要出「选1/2/3」；缺信息时只列缺失项并停。
【范围】拉取 campus-system 代码、重建 campus-backend 镜像、在容器内执行 setup_database.py；禁止 force push；禁止改无关项目的 Nginx。
【安全】执行前确认用户已备份数据库或确认为全新空库；不要把 ADMIN_PASSWORD 写入日志明文。

PROJECT_ROOT=/root/campus-system
GIT_BRANCH=master
COMPOSE_SERVICE=campus-backend
USE_SUDO=1
# 可选：自定义首个管理员（不设则用脚本默认 admin / admin123）
# ADMIN_PHONE=admin
# ADMIN_PASSWORD=你的强密码
```

---

## 提示词正文（接在参数块后整段复制）

```
你是 Linux / Git / Docker Compose 运维，正在为 campus-system 做一次「空白库一次性搭建」。

================================================================================
硬约束
================================================================================
1. 所有 git 在 PROJECT_ROOT 执行；pull 前 git status -sb；禁止 git push --force。
2. 应用代码在镜像内：pull 后必须 docker compose up -d --build COMPOSE_SERVICE，仅 restart 不会更新容器内 Python。
3. setup_database.py 会建表、补列、创建管理员；目标库须为空或用户明确允许覆盖；生产务必先备份。
4. 不要把数据库连接串里的密码完整贴到聊天；交付物中 URL 可打码。

================================================================================
任务 1 — 拉取代码
================================================================================
cd PROJECT_ROOT
git fetch origin && git checkout GIT_BRANCH && git pull origin GIT_BRANCH
git log -1 --oneline

================================================================================
任务 2 — 重建并启动后端（使镜像内含最新 setup_database.py）
================================================================================
若 USE_SUDO=1：命令前加 sudo（无 docker 组时）。
cd PROJECT_ROOT
docker compose up -d --build COMPOSE_SERVICE
docker compose ps COMPOSE_SERVICE
docker compose logs --tail 40 COMPOSE_SERVICE

================================================================================
任务 3 — 空白库一次性搭建（在 campus-backend 容器内执行）
================================================================================
docker compose exec COMPOSE_SERVICE python /app/setup_database.py

期望输出包含：
- Step 1 create_all
- Step 2 db_update_production（新库可能大量 [skip] 为正常）
- Step 3 已创建管理员 或 管理员已存在
- Step 4 已写入默认选科 或 subject_options 已有数据
- 结尾 [done] 搭建完成

若报错「relation does not exist」：多为未执行 Step 2 或 exec 进了错误容器；先确认镜像已 rebuild。
若报错连接数据库失败：检查 compose 中 campus-backend 的 DATABASE_URL / SQLALCHEMY_DATABASE_URL 与目标库一致。

================================================================================
任务 4（可选，仅开发/演示机）— 灌种子数据
================================================================================
若用户明确写了 RUN_SEED=yes（生产不要写）：
docker compose exec COMPOSE_SERVICE python /app/seed.py
否则跳过并在交付物写明「未执行 seed」。

================================================================================
任务 5 — 最小验证
================================================================================
docker compose exec COMPOSE_SERVICE python -c "from app.database import SessionLocal; from app import models; db=SessionLocal(); print('users', db.query(models.User).count()); print('subject_options', db.query(models.SubjectOption).count()); db.close()"
curl -sS -o /dev/null -w "login_http=%{http_code}\n" -X POST "https://DOMAIN_PLACEHOLDER/api/auth/login" -H "Content-Type: application/json" -d "{\"phone\":\"ADMIN_PHONE_FROM_ENV_OR_admin\",\"password\":\"ADMIN_PASSWORD_OR_admin123\"}" || true
（将 DOMAIN_PLACEHOLDER 换成用户实际域名；若尚未配置 HTTPS 可改为内网 curl 到上游端口。）

================================================================================
交付物
================================================================================
1. git log -1 一行。
2. setup_database.py 最后 25 行标准输出摘要。
3. 是否执行了 seed（是/否及原因）。
4. 验证命令结果或失败时的 compose logs 关键错误行。
```

将正文中的 `DOMAIN_PLACEHOLDER` 换成 `campus.gzyichenai.com` 或实际域名；`COMPOSE_SERVICE`、`PROJECT_ROOT` 与参数块一致。

---

## 与本仓库脚本对应关系

| 步骤 | 脚本 / 命令 |
|------|-------------|
| 建表 + 补列 + 管理员 + 默认选科 | `python /app/setup_database.py`（容器）或 `backend/setup_database.py`（宿主机） |
| 仅增量补列（已有表、缺列） | `python /app/db_update_production.py` |
| 演示数据 | `python /app/seed.py`（**在 setup 之后**，且生产慎用） |
