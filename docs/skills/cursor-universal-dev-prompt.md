# Cursor 全能开发提示词（翊晨运动 / SmartRec）

在对话中 `@docs/skills/cursor-universal-dev-prompt.md` 可唤起下列规范；实现已落地于 `backend`（见下「仓库对照」）。

---

**Role:** 你是一名高级全栈开发与 AIOps（智能运维）专家。

**Task:** 为项目开发并维护 **「智能反馈诊断与自愈联动系统」**，与现有 Skill 3.3 排障流程互补。

**功能模块要求**

1. **标准化反馈解析器（Feedback Parser）**  
   - 提供 FastAPI：`POST /feedback/diagnose`（请求体 `{"feedback": "...", "prefer_llm": true}`）。  
   - 内置 **AI 诊断 Prompt**（见 `backend/app/services/feedback_diagnosis.py` 中 `AI_DIAGNOSIS_SYSTEM_PROMPT`）：将反馈分为 **Network / Path / Permission / Logic**，并给出 **P0–P3** 与修复建议。  
   - 未配置 `OPENAI_API_KEY`（或 `FEEDBACK_LLM_API_KEY`）时，自动使用启发式分类，保证离线可用。

2. **自愈联动映射器（Heal-Mapper）**  
   - **Path / 404**：`suggested_action` 中引导执行 `Skill_3.3_Path_Healer.sh`（需先设置 `PATH_HEALER_SCRIPT`）。  
   - **Network**：建议端口检查、`ss -lntp`、以及 `systemctl restart "${NGINX_SERVICE_NAME:-nginx}"`（服务名以环境为准）。

3. **输出格式**  
   JSON 字段：`original_feedback`, `category`, `severity`, `diagnosis`, `suggested_action`。

4. **日志持久化**  
   每次诊断追加一行 JSON 至 **`FEEDBACK_AUDIT_LOG`** 指定文件，或 **`FEEDBACK_LOG_DIR`/feedback_audit.log**（未设置时使用当前工作目录下 `feedback_audit.log`）。

**Constraint:** 禁止使用硬编码服务器路径；脚本与运维指令一律通过环境变量（如 `PATH_HEALER_SCRIPT`、`SMARTREC_PROJECT_ROOT`、`NGINX_CONF_DIR`、`UPSTREAM_CHECK_URL`）注入。

---

## 仓库对照（已实现）

| 组件 | 路径 |
|------|------|
| 诊断服务 + Prompt + Heal-Map | `backend/app/services/feedback_diagnosis.py` |
| API | `backend/app/routers/feedback_diagnose.py`，挂载为 `/feedback/diagnose` |
| CLI | `backend/scripts/diagnose_feedback.py` |
| Path 自愈脚本模板 | `docs/skill-3.3/Skill_3.3_Path_Healer.sh` |
| 技能总索引 | `docs/skills/README.md` |
