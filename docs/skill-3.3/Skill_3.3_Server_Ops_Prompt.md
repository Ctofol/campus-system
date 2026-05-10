# Skill 3.3 — 服务器端一次性运维提示词（Nginx + 后端 500 + 库结构）

用途：在 **SSH / OpenCode / 服务器对话** 中整段粘贴，让 AI 按剧本执行；适用于本项目（校园运动）域名 **`campus.gzyichenai.com`** 及同类「小程序 `BASE_URL` 为 `https://域名/api` + FastAPI 在根路径」的部署。

执行前请将文中 **`{{DOMAIN}}`**、**`{{UPSTREAM_HOST}}`**、**`{{UPSTREAM_PORT}}`**、**`{{PROJECT_ROOT}}`**、**`{{API_SERVICE}}`**（systemd 服务名或 Docker 容器名）替换为实际值。示例：`campus.gzyichenai.com`、`127.0.0.1`、`18721`、`/opt/campus-system`、`campus-api`。

---

## 提示词正文（从下一行起复制到服务器）

```
你是 Linux / Nginx / Python(FastAPI) / systemd 运维，在同一台机器可能托管多个站点的前提下工作。

================================================================================
硬约束（必须遵守，避免误伤其他项目）
================================================================================
1. 只允许修改「与域名 {{DOMAIN}} 绑定的 server { }」所在配置文件；grep 到多份时先列出路径，若无法唯一确定则停止并列出需用户确认的文件，禁止猜测写入。
2. 禁止擅自修改：未绑定 {{DOMAIN}} 的 server、default_server 站点、其他项目的 include、全局 http 段（除非用户明确要求且已说明影响面）。
3. 任何写配置文件或业务代码前：对将改动的文件执行整文件备份，例如 cp 路径 路径.bak.$(date +%F_%H%M)。
4. 修改 Nginx 后必须：sudo nginx -t；仅通过后再 sudo systemctl reload nginx（或环境等价命令）。失败则恢复备份，不得留下无效配置。
5. 数据库结构变更前提醒：生产库建议维护窗口；有备份再执行 ALTER。

================================================================================
背景（本项目约定）
================================================================================
- 小程序 / 前端生产环境请求基址为：https://{{DOMAIN}}/api
- FastAPI 路由在应用根路径（如 /auth/login、/users/profile），无 /api 前缀。
- 因此 Nginx 必须对 location /api/ 使用「剥前缀」代理：proxy_pass http://{{UPSTREAM_HOST}}:{{UPSTREAM_PORT}}/;（注意末尾斜杠），使 /api/auth/login → 后端 /auth/login。
- 同一域名上若还有 /admin/api/ 指向管理端等其他上游，禁止改动那些 location，除非用户明确要求。

================================================================================
任务 A — Nginx：/api/ 与静态站冲突（404、HTML 错误页）
================================================================================
1. 定位：grep -R "server_name" /etc/nginx/ 2>/dev/null | grep -F "{{DOMAIN}}" 或用户提供的 conf 目录。
2. 在绑定 {{DOMAIN}} 的 server 块内（含 443 与 80 若均对外），检查是否已有 location /api/；若缺失或 proxy_pass 错误（例如指到带 /api/ 后缀的上游路径导致双重前缀），按「剥前缀」规则修正。
3. location /api/ 建议写在会吞请求到 H5 的 location / 之前或依赖更长前缀匹配；补充常用头：Host、X-Real-IP、X-Forwarded-For、X-Forwarded-Proto；上传接口需 client_max_body_size 时仅加在本 location 或本 server，勿改全局。
4. 验证（在服务器或可访问网络的机器）：
   curl -si -X POST "https://{{DOMAIN}}/api/auth/login" -H "Content-Type: application/json" -d '{"phone":"t","password":"t"}' | head -20
   期望：不再是静态站 404；可为 401/422/400 等 JSON 业务响应。

================================================================================
任务 B — 后端 5xx：已能打到 /api/ 但接口返回 500（例如 GET /api/users/profile）
================================================================================
说明：502/504 多为网关或上游不可达；500 多为应用内异常或响应校验失败，需读进程日志与数据库。

1. 查日志（按实际二选一或都做）：
   - systemd：journalctl -u {{API_SERVICE}} -n 200 --no-pager
   - Docker：docker logs --tail 200 {{API_SERVICE}}
   在报错时间点查找 Traceback、OperationalError、ValidationError、no such column 等关键字。

2. 若日志为数据库「缺列 / no such column」：
   - 在 {{PROJECT_ROOT}} 使用与线上一致的 DATABASE_URL，执行仓库中的结构补丁脚本（本仓库为 backend/db_update_production.py：为 users 等表补充 signature、avatar_url、regular_score 等列并 create_all 缺表）。
   - 命令示例：cd {{PROJECT_ROOT}}/backend && source .venv/bin/activate 2>/dev/null; python db_update_production.py
   - 执行后重启 API 进程或容器，再复测 GET /api/users/profile（需带合法 Bearer）。

3. 若日志为 Pydantic 响应校验、None 与 str 不匹配等：
   - 记录具体字段；优先通过应用代码默认值或数据库 UPDATE 将 NULL 改为合法值；不要为「省事」关闭全局校验除非用户明确要求。

4. 若日志为代码逻辑错误：
   - 最小化修复；修改前备份文件；修复后重启服务并复测。

================================================================================
任务 C — 超时（timeout）与 Nginx 超时
================================================================================
若日志或 curl 显示上游慢、客户端超时，可在绑定 {{DOMAIN}} 的 server 或 location /api/ 内按需增加（勿设过大掩盖故障）：
proxy_connect_timeout、proxy_send_timeout、proxy_read_timeout（例如 60s）。
先确认慢因（DB、外呼 HTTP、死锁），再调超时。

================================================================================
交付物（你必须输出）
================================================================================
1. 修改了哪些文件的哪些配置/命令（摘要 + 关键行含义）。
2. 验证命令与结果（HTTP 状态码 + 是否 JSON）。
3. 回滚步骤：如何从 .bak 恢复配置并 reload；数据库若未做不可逆操作则说明「无库回滚」或备份路径。
4. 影响范围说明：为何未影响其他域名、/admin/api/、其他 location。

若任一环节无法在不违反硬约束的前提下完成：说明阻塞原因与最短需用户补充的信息（上游端口、服务名、conf 路径、是否 Docker）。
```

---

## 使用说明

- **只修 Nginx**：让执行方只做「任务 A」并在交付物里写明未动数据库。  
- **只修 500**：提供报错 URL、时间与（若有）日志片段，让执行方从「任务 B」开始。  
- **全链路**：整段粘贴，由对方按 A→B→C 顺序执行并在无法继续时停下提问。

与本仓库模板配置的对照文件：`remote_nginx.conf`（含 `location /api/` 示例）。
