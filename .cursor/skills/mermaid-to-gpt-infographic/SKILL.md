---
name: mermaid-to-gpt-infographic
description: >-
  After Skill 3.1 outputs flowcharts: writes docs/diagrams/fig-*.mmd, tells user
  to export PNG via mermaid.live, and produces ChatGPT image prompts. Use when
  the user wants 计划书配图, proposal figures, or GPT infographic from Mermaid.
disable-model-invocation: true
---

# Mermaid → 落盘 `.mmd` → 网站导出 → GPT 信息图

## 标准流水线（与 Skill 3.1 串联，推荐按序执行）

| 阶段 | 谁做 | 做什么 |
|------|------|--------|
| **A** | 你 + Skill 3.1 | `@docs/skill-3.1/Skill_3.1_README.md`，用第四节「万能逻辑转换 Prompt」+ 计划书/接口说明，产出 **3 套** Mermaid（流程 / 时序 / 拓扑）。本流水线默认取其中的 **流程图** `flowchart`。 |
| **B** | 你 + **本技能**（新开一条 Cursor 对话） | `@mermaid-to-gpt-infographic`，粘贴 Skill 3.1 **刚生成的流程图** fenced 代码（或说明主题）。要求 Agent 按下方 **「Agent 交付清单」** 交付。 |
| **C** | 你 | 打开 [mermaid.live](https://mermaid.live)，粘贴 `.mmd` 全文 → **Export PNG**（结构参考；SVG 可选）。 |
| **D** | 你 + ChatGPT（多模态） | 上传 **风格参考** → 再上传 **mermaid.live 导出的 PNG** → 粘贴阶段 B 给出的 **生图提示词** → 出图。 |
| **E** | 你 | 插入 Word/PPT，图注写版本与日期；以后只改 `.mmd` → 重新导出 → 提示词微调后再生。 |

**CLI 替代网站（可选）**：项目根已装 Node 时：

```bash
npx @mermaid-js/mermaid-cli -i docs/diagrams/fig-<主题>-flow.mmd -o docs/assets/fig-<主题>-flow.png -w 2400 -H 1350 -b white
```

导出 PNG 同样可作为 ChatGPT 的「结构参考」。

---

## Agent 交付清单（`@mermaid-to-gpt-infographic` 时必须满足）

用户附上 **Skill 3.1 生成的流程图**（或等价 Mermaid）时，Agent **必须一次性给出**：

1. **`docs/diagrams/fig-<主题>-flow.mmd`**  
   - 写入仓库：内容与用户流程图一致；仅允许 **排版级** 整理（换行、`subgraph` 标题统一），**不得改业务节点、箭头语义或分区名**（如 FE / API / SVC / DATA / EXT）。  
   - 若用户已指定文件名，从其命名。

2. **一段可复制到 ChatGPT 的完整生图提示词**  
   - 须写明：16:9、扁平商务信息图、**第一张上传图 = 风格参考**、**第二张 = mermaid.live（或 mmdc）导出的结构参考**、不得删减的关键阶段与术语。  
   - 可直接用本文 **「主提示词模板」** 填好 `{...}`（推荐，易改字）；或 **一句高密度提示词**，但必须在句内或句末强调「拓扑须与第二张结构参考及仓库 `.mmd` 一致」。

3. **一句给用户的手动步骤**（附在提示词后即可）  
   - 例：`请用 mermaid.live 打开并粘贴 docs/diagrams/fig-<主题>-flow.mmd，导出 PNG，再与风格参考图一并上传到 ChatGPT，最后粘贴上面的提示词。`

**不要**假设 ChatGPT 能读私有仓库路径：提示词里若写路径，仅作你本地对照；**结构真源**以 **`.mmd` + 上传的导出图** 为准。

---

## 何时使用

- 已用 **Skill 3.1** 得到流程图，要把同一张图变成：**可 PR 的 `.mmd`** + **网站可渲染** + **GPT 信息图提示词**。  
- 或已有 Mermaid，希望统一走：**落盘 `docs/diagrams/` → mermaid.live → ChatGPT**。

## 核心原则

1. **Mermaid / `.mmd` 是唯一结构真源**；ChatGPT 只做版式美化，拓扑以导出图为锚。  
2. **GPT 不善精确中文小字**：默认 **占位符 + PPT 改字**（模式 A），或 **GPT 底图 + SVG 叠字**（模式 C）。  
3. **与 Skill 3.1 同一故事多图时**：流程图优先做信息图；时序/拓扑可另开对话各产一份 `.mmd` + 提示词，并在提示里要求 **色系统一**。

## 工作流细节（按需查阅）

### 固化与命名

- 路径：`docs/diagrams/fig-<主题>-flow.mmd`（时序/拓扑可用 `fig-<主题>-seq.mmd` / `topology.mmd`）。  
- 计划书插图资产：`docs/assets/fig-<主题>-flow.svg` / `.png`（与正文「图 x-x」编号稳定对应，可只换文件）。

### 使用 GPT 时的推荐模式

- **模式 A（稳）**：色带、箭头、图例由 GPT 出；框内 `步骤1` / `L1` 占位，你在 Office 里替换中文。  
- **模式 B**：允许框内中文，多生成几张选优，再逐字校对。  
- **模式 C**：GPT 出 16:9 底图，Mermaid 导出 SVG 叠在 Figma/PPT 上保证文字准确。

具体模型是否支持「参考图生图」以当前产品为准；本技能不绑定单一模型名。

### 交付前自检

- [ ] 箭头与阶段顺序与 `.mmd` 一致  
- [ ] 图例与正文术语一致（FE/API/SVC/DATA/EXT 等）  
- [ ] 图注或文件名含 **版本或日期**  

---

## 主提示词模板（Agent 填好 `{...}` 后整段给用户复制）

把 `{...}` 换成从 `.mmd` 提炼的阶段列表或简短文字摘要；可同时要求「严格参考上传的第一张图为版式，第二张图为结构」。

```text
你是信息图设计师。请生成一张 16:9、300dpi 可用的横版示意图（扁平/商务信息图，无照片）。

【版式】参考我上传的「风格参考图」：横向多条彩色阶段带，阶段之间用向下粗箭头连接；阶段内从左到右步骤流；最下方放图例（实线箭头=流程方向，虚线框=阶段边界）。

【内容结构】参考我上传的「结构参考图」或下列文字，不得删减关键阶段：
{粘贴：Mermaid 文字摘要或阶段列表}

【多模态扩展】除视频主路径外，增加并行泳道：GPS 轨迹处理、运动传感器、历史训练记录，汇聚到「多模态融合/时间对齐」节点（若与当前流程图主题不符可整段删除）。

【文字策略】为减少错字，步骤框内使用简短中文或英文占位（如「步骤1」「采集」）；禁止编造未提供的指标与接口名。

【风格】浅色背景，五色以内，对比足够打印黑白稿仍可区分。

【输出】单张完整图；若无法一次完成，请分「线稿版」与「上色版」两步说明。
```

---

## 变体：仅要「GPT 写提示词」

若用户用 Midjourney 等，可让 GPT **只输出** 中英文生图提示（800 字内），并带负面提示：`no photorealistic people, no illegible tiny text, no watermark`。

---

## 与 Skill 3.1 的分工与关键词

| 技能 | 职责 |
|------|------|
| `docs/skill-3.1/Skill_3.1_README.md` | 业务/代码 → **三套可审计 Mermaid**（流程 / 时序 / 拓扑）。 |
| **本技能** | 其中选定的一套（通常 **流程图**）→ **`fig-*.mmd`** + **mermaid.live / mmdc 导出说明** + **ChatGPT 生图提示词**。 |

从 Skill 3.1 图里复述进【内容结构】时，按该次需求保留关键词，例如：`FE / API / SVC / DATA / EXT`；`/activity/finish`；`verify_activity`；`metrics, trajectory, evidence, video_url`；数据最小化与留痕；拓扑里 **Future 虚线** 等。**勿**改成无关微服务名或漏审计边。

**用户一句话模板（Cursor 里 @ 本技能时可直接粘贴）：**

```text
下面 @Skill 3.1 刚生成的流程图 Mermaid（粘贴代码）。请按 mermaid-to-gpt-infographic 技能：
1）写入 docs/diagrams/fig-<短主题>-flow.mmd；
2）用「主提示词模板」生成一段完整 ChatGPT 生图提示词（保留图中 FE/API 等分区与关键边）；
3）附一句说明：用 mermaid.live 导出该 mmd 的 PNG 作结构参考再发 ChatGPT。
```

---

## 一张图 vs 三张图

- **计划书主线**：通常只做 **流程图** 这一条流水线。  
- **附录**：时序图可 **只导出 PNG** 直接插图；拓扑若要信息图风格，再 `@` 本技能一次，并在提示里写「与上一张流程信息图 **同一色板**」。

## 延伸阅读

- 提示词变体、对话骨架、mmdc 批量导出：见 [reference.md](reference.md)
