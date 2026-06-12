# 服务器后端 AI — 拉取 campus-system 更新（粘贴提示词）

面向：已在 **SSH / 服务器 shell** 中、可执行 `git` 与 `docker compose` 的运维 AI（OpenCode、Claude Code 等）。  
目标：**从 GitHub 拉取最新代码**，并按约定 **更新后端容器**；不写读后感、不输出「请选 1/2/3」。

完整发版（含迁移说明、教师端路由、验证清单）见同目录 **`Skill_3.3_OpenCode_Release_Campus_Update.md`**。

---

## 文首参数块（复制后改等号右侧）

```
【执行模式】用户已授权你在当前 SSH 会话所在机器上执行 git pull 与 docker compose；缺信息时只列缺失项并停止。
【禁止】force push、修改未授权仓库、向聊天外写入明文密钥。
【交付】执行命令摘要 + 关键输出（前若干行）+ 失败时回滚思路。

PROJECT_ROOT=/root/campus-system
GIT_REMOTE=origin
GIT_BRANCH=master
COMPOSE_SERVICE=campus-backend
RUN_DB_UPDATE=yes
```

说明：

- `RUN_DB_UPDATE=yes`：在 **与线上一致 DATABASE_URL** 的环境下执行 `backend/db_update_production.py`（仅补列，幂等）。不确定环境时改为 `no` 并说明原因。
- 后端代码若在镜像内：**pull 后必须** `docker compose up -d --build COMPOSE_SERVICE`，**仅 `restart` 不会更新镜像内 Python**。

---

## 粘贴用提示词正文（接在参数块后）

```
你是 Linux / Git / Docker Compose 运维。任务：在 PROJECT_ROOT 从 GIT_REMOTE 拉取 GIT_BRANCH 最新代码，并更新 COMPOSE_SERVICE。

================================================================================
硬约束
================================================================================
1. 所有 git 操作在 PROJECT_ROOT 内；pull 前执行 git status（有未提交改动则停止并说明，不要 stash 除非用户明确要求）。
2. 禁止 git push --force、禁止删除远程分支。
3. 不要把数据库密码、JWT 密钥、TENCENT_MAP_KEY 写入聊天或非受控日志（Key 只写在 backend/.env）。
4. db_update 仅当 RUN_DB_UPDATE=yes 且你能确认使用与 campus-backend 相同的 DB 连接时再执行；执行前口头提醒「生产库应先备份」（一句即可）。
5. **学生首页天气**：若发版含首页改版，pull 前/后检查 backend/.env 是否有 TENCENT_MAP_KEY；缺失则追加 ET4BZ-QJAL4-EMPUD-FBOLE-M23H3-3RBXD 并 --build 重启 COMPOSE_SERVICE。细则见同目录 Skill_3.3_Weather_Env_Deploy_Note.md。

================================================================================
执行步骤（严格顺序）
================================================================================
set -e
cd PROJECT_ROOT
git status
git fetch GIT_REMOTE
git checkout GIT_BRANCH
git pull GIT_REMOTE GIT_BRANCH
# 记录：git log -1 --oneline

# 学生首页天气 env（无则追加，有则跳过）
grep -q '^TENCENT_MAP_KEY=' PROJECT_ROOT/backend/.env || echo 'TENCENT_MAP_KEY=ET4BZ-QJAL4-EMPUD-FBOLE-M23H3-3RBXD' >> PROJECT_ROOT/backend/.env

若 RUN_DB_UPDATE=yes：
  cd PROJECT_ROOT/backend
  python db_update_production.py
  cd PROJECT_ROOT

cd PROJECT_ROOT
docker compose up -d --build COMPOSE_SERVICE
docker compose ps COMPOSE_SERVICE

# 可选：最近 30 行日志，确认无立即崩溃
docker compose logs --tail=30 COMPOSE_SERVICE

================================================================================
最小验证（无敏感信息）
================================================================================
- `docker compose ps` 中 COMPOSE_SERVICE 为 Up（或 healthy）。
- 若宿主机可访问对外 API：对 `https://<用户域名>/api/` 或 `/api/auth/login` 发请求，返回非 5xx（具体 URL 以用户 Nginx 为准；不知道域名则跳过并写明「未验证 HTTP」）。

================================================================================
交付物（简短列表）
================================================================================
1. 实际执行的命令（一行一条摘要即可）。
2. `git log -1 --oneline` 输出（当前部署提交）。
3. db_update：已执行 / 已跳过及原因。
4. compose：服务是否 Up；若失败附 `docker compose logs COMPOSE_SERVICE` 末尾含 Traceback 的片段。
5. 回滚：git checkout 到 pull 前提交（`git reflog` 找上一 HEAD）+ 对 COMPOSE_SERVICE 再次 --build；若执行了迁移且破坏数据则从备份恢复（仅说明，不擅自恢复）。
```

---

## 给人类操作员的一句提醒

发版含 **Schema 变更** 或 **小程序前端** 时，除后端 pull 外还需：小程序重新上传审核、管理端静态资源重新构建等；本提示词**仅覆盖仓库拉取 + 后端容器更新**。
