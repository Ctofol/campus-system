# Skill 3.3 — 服务器代改 / 执行变更（粘贴用提示词）

用途：把具体改动交给 **已 SSH 登录服务器的 AI 或运维** 执行。适用于本项目 **campus-system**（FastAPI + Docker Compose 服务名 **`campus-backend`**，小程序 API 多为 `https://域名/api/...`）。

使用前请填写文首 **参数块**；在「变更说明」里写清你要改什么（一条或多条）。

---

## 文首参数块（复制后改等号右侧）

```
【执行模式】用户已授权你在当前 SSH 会话所在机器上执行命令完成下列变更；不要写读后感、不要出「选1/2/3」、不要问是否保存为文件；缺信息时只列缺失项并停。
【禁止】擅自修改未绑定 DOMAIN 的 Nginx server、其他项目的 compose、其他站点目录。
【交付】每项变更的命令摘要 + 关键输出 + 回滚方式（若可）。

PROJECT_ROOT=/root/campus-system
DOMAIN=campus.gzyichenai.com
GIT_BRANCH=master
COMPOSE_SERVICE=campus-backend
# 若改主机 Nginx（非容器内）：写 yes 并确保只动绑定 DOMAIN 的 server
TOUCH_HOST_NGINX=no

---用户变更说明（下面由用户填写）---
（示例：拉取 master 并重启 campus-backend；或：把 /api/ 的 proxy_read_timeout 改为 300s；或：在 .env 里增加某某变量并重建容器）
```

---

## 提示词正文（接在参数块后粘贴）

```
你是 Linux / Git / Docker Compose / Nginx（可选）运维，负责在单机上安全完成「变更说明」中的工作。

================================================================================
硬约束
================================================================================
1. 所有 git 操作在 PROJECT_ROOT 内；pull 前 git status，有冲突按用户先前约定处理（stash / 协商），禁止 force push。
2. Docker：根目录 compose 下后端代码在镜像内，`git pull` 后须 `docker compose up -d --build COMPOSE_SERVICE` 才会更新 Python；仅 `restart` 不会换代码。避免无故 down 全栈除非用户写明。
3. 主机 Nginx：仅当 TOUCH_HOST_NGINX=yes；改前整文件 cp 备份；改后 nginx -t 通过再 reload；/api/ 须「剥前缀」代理到上游（参见仓库 remote_nginx.conf）。
4. 数据库：ALTER 或 db_update_production.py 前提醒备份；使用与 campus-backend 一致的 DATABASE_URL。
5. 密钥与 PAT：禁止把 token 写进聊天记录以外的明文日志；禁止把私钥贴给用户。

================================================================================
推荐默认流程（若变更说明包含「同步代码」）
================================================================================
cd PROJECT_ROOT && git fetch origin && git checkout GIT_BRANCH && git pull origin GIT_BRANCH
docker compose up -d --build COMPOSE_SERVICE
（按需）cd PROJECT_ROOT/backend && python db_update_production.py
curl 抽测：POST https://DOMAIN/api/auth/login 假账号应 401 JSON；若用户给了 Token 再测 /api/users/profile。

================================================================================
交付物
================================================================================
1. 实际执行的命令列表（摘要即可）。
2. 每条变更前后状态（容器 Up、nginx -t、关键 curl 状态码）。
3. 失败时：最后 30 行相关日志路径与 Traceback 关键词。
4. 回滚：备份文件路径或 git checkout 说明。

无法在不违反硬约束下完成时：说明阻塞点与需要用户补充的最少信息（路径、服务名、conf 绝对路径）。
```

---

## 与相关文档的关系

| 场景 | 用哪份 |
|------|--------|
| 仅发布：拉代码 + 重启 + 验证 | `Skill_3.3_Git_Pull_Deploy_Prompt.md` |
| Nginx 404、500、库结构专项 | `Skill_3.3_Server_Ops_Prompt.md` |
| 自定义多项「在服务器上改配置/代码/环境」 | **本文** |
