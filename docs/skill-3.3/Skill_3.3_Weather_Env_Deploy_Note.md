# Skill 3.3 — 学生首页天气 API（后端环境变量 · 粘贴提示词附录）

用途：发版含 **学生首页天气**（`GET /student/weather`）时，粘贴到 **OpenCode / 服务器运维 AI**，或在人工部署时对照执行。  
实现：`backend/app/services/weather_service.py` 代理腾讯位置服务；**Key 仅存后端**，前端只调 `/api/student/weather?lat=&lng=`。

---

## 你必须配置的环境变量

在 **`backend/.env`**（Docker Compose 挂载 `./backend/.env` → 容器内 `/app/.env`）增加或确认：

```env
# 腾讯位置服务 WebService — 学生首页天气（与小程序地图 SDK 可用同一 Key）
TENCENT_MAP_KEY=ET4BZ-QJAL4-EMPUD-FBOLE-M23H3-3RBXD
# 可选
# TENCENT_MAP_API_BASE=https://apis.map.qq.com
# WEATHER_CACHE_TTL_SEC=1800
```

**腾讯控制台**（[我的应用](https://lbs.qq.com/dev/console/application/mine) → Key「大学生运动健康平台」→ **详情/编辑**）须同时开启：

1. **WebServiceAPI**
2. **天气服务**（有配额；备注「路线规划」不影响，关键是产品开关要开）

未配置 `TENCENT_MAP_KEY` 时：接口仍返回 200，但 `ok: false`；小程序首页显示「天气加载中」。

---

## 粘贴用提示词（接在发版参数块后，或单独发给运维 AI）

```
【附加任务 — 学生首页天气 API 环境】
在 PROJECT_ROOT/backend/.env 中确认存在 TENCENT_MAP_KEY=ET4BZ-QJAL4-EMPUD-FBOLE-M23H3-3RBXD（若缺失则追加，勿覆盖其它已有变量）。
修改 .env 后必须重建/重启 campus-backend（仅 restart 不读新 env 时改用 docker compose up -d --build campus-backend 或 systemctl restart 对应 unit）。
验证（需有效学生 Token，将 TOKEN 与 lat/lng 替换为实际值）：
  curl -sS "https://DOMAIN/api/student/weather?lat=23.1&lng=113.3" -H "Authorization: Bearer TOKEN" | head -c 400
期望 JSON 含 "ok":true 与 "weather":{"temp":...,"condition":...,"aqi_label":...}；若 ok:false 且 message 含 key，检查 .env 与腾讯控制台「天气服务」是否开启。
交付物中写明：TENCENT_MAP_KEY 已存在/已新增；curl 结果 ok  true/false 及原因。
```

---

## 与仓库文件对应

| 项 | 路径 |
|----|------|
| 路由 | `GET /student/weather`、`GET /student/home/dashboard`、`PUT /student/home/run-goal` — `backend/app/routers/student.py` |
| 首页聚合 | `backend/app/services/home_dashboard_service.py` |
| 历史轨迹字段 | `GET /activity/history` 每项含 `has_trajectory`、`trajectory_preview` |
| 代理逻辑 | `backend/app/services/weather_service.py` |
| 配置项 | `backend/app/config.py` → `TENCENT_MAP_KEY` |
| 示例 env | `backend/.env.example` |
| 前端调用 | `fronted/utils/weather.js` → `request('/student/weather')` |

---

## 人工快速检查（本地 / 服务器）

```bash
grep TENCENT_MAP_KEY backend/.env || echo "缺失 TENCENT_MAP_KEY"
docker compose up -d --build campus-backend   # 或 systemctl restart campus-backend
```

发版主流程仍用同目录 **`Skill_3.3_Git_Pull_Deploy_Prompt.md`** / **`Skill_3.3_OpenCode_Release_Campus_Update.md`**；本文件为 **天气专项附录**，每次涉及首页天气或首次上线该功能时一并粘贴或 @ 引用。
