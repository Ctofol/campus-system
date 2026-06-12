# 翊晨运动 — Cursor 技能总索引

在本仓库里需要「按剧本办事」时：**先 `@` 本文件**，再点开下表对应链接；或直接在对话里 `@` 具体路径。

| 编号 | 名称 | 用途 | 在对话里 `@` 这个文件 |
|------|------|------|------------------------|
| **3.1** | 架构可视化（Mermaid 三套图） | 把业务/接口说明转成 **流程图 + 时序图 + 模块拓扑**（可审计、与 FE/API/SVC/DATA/EXT 命名一致） | `docs/skill-3.1/Skill_3.1_README.md` |
| **配图** | Mermaid → 导出 → GPT 信息图 | 把 Skill 3.1（或其它）产出的 Mermaid **导出 SVG/PNG**，并生成 **ChatGPT 配图主提示词**（计划书/PPT 横条风格） | `.cursor/skills/mermaid-to-gpt-infographic/SKILL.md` |
| **3.3** | AI 自动运维 / 排障分流 | 根据报错 **前端 Self-Fix** 或 **生成服务器端修复 Prompt**（含 Linux 命令与闭环话术） | `docs/skill-3.3/Skill_3.3_Prompt.txt` |
| **反馈诊断** | 用户反馈 → 分类 + 自愈建议 | `POST /feedback/diagnose`，日志 `FEEDBACK_AUDIT_LOG`；Path 类联动 `Skill_3.3_Path_Healer.sh` | `docs/skills/cursor-universal-dev-prompt.md`（规范与路径索引） |

## 如何把表格、清单传给 Agent（含配图技能）

表格本身不会「上传」到技能文件里，**传的是对话上下文**。任选其一即可：

| 方式 | 做法 | 适合 |
|------|------|------|
| **直接粘贴** | 在对话里粘贴 Markdown 表格或从 Excel 复制的制表符表格 | 行数不多、马上要用 |
| **`@` 文件** | 把表放进 `docs/.../*.md` 或 `*.csv`，对话里 `@` 该文件路径 | 表大、要改版控 |
| **截图** | 截屏贴进对话（Cursor 支持贴图） | 只读 PDF/网页上的表 |
| **口述 + 补表** | 先说「第 1 列阶段、第 2 列说明」，再贴表 | 需要 Agent 按列解释 |

**和「配图」技能一起用时**：表格一般当作 **【内容结构】素材**——先 `@.cursor/skills/mermaid-to-gpt-infographic/SKILL.md`，再 `@` 含表的文件或粘贴表，并说明「请按表中的阶段顺序写入给 ChatGPT 的主提示词，不要删行」。图生图模型**不擅长**在图里画清整张表，通常是把表 **转成阶段框/泳道文字**；若必须保留表形，用 Word/PPT 插图表格，配图只负责流程条带。

## 常用组合

1. **写方案 / 答辩材料要架构图**  
   `@docs/skill-3.1/Skill_3.1_README.md` → 产出三份 Mermaid → 存 `docs/diagrams/*.mmd`。

2. **要把流程图变成信息图**  
   `@.cursor/skills/mermaid-to-gpt-infographic/SKILL.md` → 按技能用 mermaid.live 或 `mmdc` 导出 → 再贴技能里的「主提示词模板」到 ChatGPT。

3. **线上/本地报错要修**  
   `@docs/skill-3.3/Skill_3.3_Prompt.txt` → 粘贴控制台或日志（勿贴真实密钥）。

4. **后端发版 / OpenCode 拉代码（含学生首页天气 env）**  
   `@docs/skill-3.3/Skill_3.3_Git_Pull_Deploy_Prompt.md` 或 `@docs/skill-3.3/Skill_3.3_Weather_Env_Deploy_Note.md`（`TENCENT_MAP_KEY` + `/student/weather` 验证）。

5. **用户表单反馈自动分类 / 审计**  
   `@docs/skills/cursor-universal-dev-prompt.md` → 调 `POST /feedback/diagnose` 或 `backend/scripts/diagnose_feedback.py`；Path 类按提示设置 `PATH_HEALER_SCRIPT` 后执行 `Skill_3.3_Path_Healer.sh`。

## 与 `.cursorrules` 的关系

仓库根目录 `.cursorrules` 会在排障场景下 **摘要引用 Skill 3.3**；完整条文仍以 `Skill_3.3_Prompt.txt` 为准。Skill 3.1 与配图技能 **默认靠你 `@` 本索引或对应文件** 唤起。

## 仓库内图源示例

- 跑步审核流程（Mermaid 源）：`docs/diagrams/fig-run-audit-flow.mmd`  
- 配图技能延伸阅读：`.cursor/skills/mermaid-to-gpt-infographic/reference.md`
