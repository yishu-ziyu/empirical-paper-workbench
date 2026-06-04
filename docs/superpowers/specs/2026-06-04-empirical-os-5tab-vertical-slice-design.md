# Spec: 本地实证研究 OS 5-Tab 纵切贯通

| | |
|---|---|
| **Date** | 2026-06-04 |
| **Status** | Draft (待用户审) |
| **Author** | Claude (brainstorming 流程产出) |
| **Owner** | mahaoxuan (PM, 非程序员) |
| **Repo** | `实证论文项目模板/` (5-layer: Data/Program/Results/Manuscripts/Submissions) |
| **Target** | 5 个 tab 全部接真后端，端到端走通 1 条研究流水线 |

---

## 1. Context（为什么做这件事）

### 1.1 现状
项目 `Product/web-react/` 已有 React 19 前端，5 个 tab 写死在 `App.tsx:108-131`：
- `brief`（任务书）：✅ 有真组件 (`TaskBriefDemo` → `SupervisorPlanReview` → `AgentActivityPanel`)
- `recursive-search` / `variables` / `design` / `execution`：❌ 全部 fallthrough 到 `SemanticGlowCards`（一个 regex 匹配 did/iv/rdd/psm/dml 关键词的占位卡片）
- 所有任务数据 `evidence_level: "mock"` 写死
- 前端 `src/` 里 **0 个 fetch/axios**，40 个后端 service 完全没接

### 1.2 已有的资产
- **后端 40 个 service** 在 `Product/backend/`（`orchestrator.py` 60KB、`project_service.py` 82KB、`auto_research_service.py`、`supervisor_plan_service.py` 等）
- **91K pipeline**：`Program/workbench/manuscript_section_draft_expansion.py` 已能跑 9 节论文，verdict 2 红（接近通过）
- **StatsPAI SDK**：`../StatsPAI/` 因果断面 + Skill
- **Awesome-Agent-Skills**：`../Awesome-Agent-Skills-for-Empirical-Research/` 30+ 经验研究 skill 库
- **arxiv-mcp** / **paper-search MCP**：可做文献搜索

### 1.3 为什么现在
- PM 已验收前端 UI（`/`，session 5851a729 末尾）
- 91K pipeline 模板版已被 assistant 自己说"分析深度是模板的"
- 用户明确要求："**结果可被用户复现使用**"

---

## 2. Goals & Non-Goals

### 2.1 Goals（必须做）
1. **5 tab 全部接真后端**：每个 tab 背后调 1 个真实 FastAPI endpoint，对应真实 service 调用
2. **可复现使用**：每个 tab 的产物落盘到 `Tasks/{topic}/` + `Manuscripts/{topic}/` + `Results/{topic}/`，第二天能 re-run 拿到等价结果
3. **LLM 选择性增强**：在 5 个"语义判断"点用 LLM（任务书扩写、搜索重排、变量映射、方法解释、9 节论文写作）
4. **保持可复现**：LLM 调用的 prompt / model / seed / 数据快照全部入库
5. **verdict gate 复用**：之前 91K 用的 9 节判分标准直接搬过来作为质量门
6. **LLM prompt 调优**：每个 LLM tab 的 prompt **至少迭代 2 轮**，由 verdict gate 红色 + 用户反馈驱动。详细机制见 §4.6

### 2.2 Non-Goals（明确不做）
- ❌ 多用户协作 / 权限管理
- ❌ 主题切换的清理
- ❌ 论文 LaTeX 高端排版
- ❌ 移动端 / 触屏适配
- ❌ 实时协同编辑
- ❌ 把 91K pipeline 重写成"非模板"（本次贯通，调优包含 prompt 而非重写 ManuscriptAgent 本身）

---

## 3. Architecture

### 3.1 系统地图
```
浏览器 (React 19 + Vite, :8765)
  ├─ 输入课题 → 走前端状态机切 5 tab
  └─ 每个 tab 各自 fetch 自己的后端 endpoint
        │ fetch + SSE (长任务流式)
        ▼
FastAPI (Product/app.py, :8765)
  ├─ /api/brief       (短)
  ├─ /api/search      (短)
  ├─ /api/variables   (中)
  ├─ /api/design      (中, 调 StatsPAI + LLM)
  └─ /api/execute     (SSE, 跑 StatsPAI + LLM 写作)
        │
        ▼
后端服务层 (Product/backend/*_service.py, 40 个)
  ├─ supervisor_plan_service   (任务书 LLM 扩写)
  ├─ auto_research_service     (执行实验流水线)
  ├─ project_service           (项目元数据)
  └─ + 5 个新写的 wrapper service 对接 5 个 endpoint
        │
   ┌────┴────┐
   ▼         ▼
外部工具   本地文件
 • arxiv-mcp       • Manuscripts/{topic}/paper.pdf
 • StatsPAI SDK    • Tasks/{topic}/
 • Claude API      • Results/{topic}/
```

### 3.2 关键约束
- 前端 0 LLM 调用（不在浏览器暴露 API key）
- 后端 5 个 endpoint 是**新写的 wrapper**，不重写 40 个 service
- 已有 91K pipeline 跑通的部分（执行实验）**不动核心逻辑**，只包 endpoint
- 长任务用 SSE 流式返回进度
- 5 tab 状态串接：每个 tab 写一个文件，下一个 tab 读它当输入
- **LLM 唯一真实模型：MiniMax M3**（不是 Claude/OpenAI/Kimi）。`Product/backend/llm_client.py` 里列的 9 个 model label（`claude-opus-4-6` / `claude-sonnet-4-6` / `claude-haiku-4-5` / `gpt-4o` / `kimi-for-coding` 等）**都是 M3 的 alias**。spec 中所有 LLM 调用统一走 `llm_client.py` 的 `MiniMax-M3` 入口。不存在"轻 tab 走轻模型 / 重 tab 走重模型"的 tier 策略

### 3.3 5 tab 的工作流串接
```
[输入课题] → 任务书 → 递归搜索 → 数据变量 → 方法设计 → 执行实验 → paper.pdf
              │           │           │           │           │
              ▼           ▼           ▼           ▼           ▼
         brief.md   literature.md  variables.yaml  design.json  paper.pdf
                                                                   +
                                                              results.json
```

每个 tab 产出带 provenance 元数据（topic / generated_by / timestamp / model / prompt_version / seed_query）。

---

## 4. Per-Tab Behavior

### 4.1 任务书 (Brief)
- **用户动作**：输入课题文字 → 提交
- **系统行为**：LLM 扩写为 4 段（问题/贡献/边界/成功标准）→ 写 `Tasks/{topic}/brief.md`
- **UI 反馈**：4 段卡片展示，"重生成"/"手动编辑"按钮
- **失败模式**：LLM 超时 → 重试 2 次，失败让用户重试

### 4.2 递归搜索 (Recursive Search)
- **前置**：任务书已确认
- **用户动作**：点"开始搜索"
- **系统行为**：LLM 生成 3-5 个搜索词 → 调 arxiv-mcp → 拿 30+ 篇 → LLM 按相关性重排 → 写 `Tasks/{topic}/literature.md`
- **UI 反馈**：8-12 篇精选论文（题名/作者/年份/摘要/相关性评分），勾选"采纳/排除"。**排除后，文献列表缩短到剩余采纳篇数，下游 tab（数据变量）不引用被排除的论文**。
- **失败模式**：arxiv 不可用 → "搜索服务暂不可用，可手动添加论文"

### 4.3 数据变量 (Variables)
- **前置**：任务书已确认
- **用户动作**：选数据集（CFPS / CHIP / CHARLS / 自选） → 点"识别变量"
- **系统行为**：后端解析数据集 schema → LLM 把列名映射到研究变量 → 写 `Tasks/{topic}/variables.yaml`
- **UI 反馈**：5-10 个研究变量表（X / Y / 控制变量），每个有"列名映射 + 语义说明 + 引用文献"
- **失败模式**：数据集缺失 → "请把 CFPS CSV 放到 `data/cfps/`"

### 4.4 方法设计 (Design)
- **前置**：数据变量已确认
- **用户动作**：点"设计方法"
- **系统行为**：StatsPAI 真实跑 estimand 候选（DID/IV/RD/PSM/DML）→ LLM 解释为什么某个适合 → 写 `Tasks/{topic}/design.json`
- **UI 反馈**：3 个候选方法卡 + LLM 解释 + StatsPAI 推荐 + **StatsPAI SDK 自动生成的 Python 代码 stub**（用户可直接复制到 `Program/runs/{topic}/` 跑）
- **失败模式**：StatsPAI 抛异常 → 显示错误信息，让用户换数据集或重试

### 4.5 执行实验 (Execution)
- **前置**：方法设计已确认
- **用户动作**：点"开始跑"
- **系统行为**：SSE 流式返回进度 → StatsPAI 跑数据 → ManuscriptAgent LLM 写 **9 节论文**（沿用 `Program/workbench/manuscript_section_draft_expansion.py` 的节结构：引言/文献综述/制度背景/数据/实证策略/主结果/稳健性/结论/参考文献）→ 出 PDF → 写 `Manuscripts/{topic}/paper.pdf` + `Results/{topic}/results.json`
- **UI 反馈**：实时进度条 + 9 节逐节状态 + 最终 PDF 预览 + 下载
- **失败模式**：跑超 60 分钟 → 客户端 SSE 断线重连，后端继续跑

### 4.6 Prompt 调优机制（核心质量保障）

**为什么是 first-class goal**：91K pipeline 当时"自动版是结构化模板"—— 这次不重写 ManuscriptAgent，但**通过迭代 prompt 弥补"模板感"**。4 个 LLM tab 任何一个 prompt 没调过，质量就会回退到模板感。

**迭代驱动器**（双源信号）：
- **自动**：verdict gate 红色（任务书 4 段缺、文献评分缺失、变量映射不完整、9 节判分 < 8/9）
- **人工**：用户在 UI 上点"这段不对"或"这节写得太浅" → 反馈进 `Tasks/{topic}/feedback.jsonl`

**每个 LLM tab 的迭代预算**：
| Tab | 至少迭代轮数 | 典型调优点 |
|---|---|---|
| 任务书 | 2 轮 | 4 段结构、边界划定粒度 |
| 递归搜索 | 2 轮 | 相关性评分标准、剔除条件 |
| 数据变量 | 3 轮 | 列名→研究变量的语义桥、引用文献匹配 |
| 方法设计 | 3 轮 | DID/IV/RD 解释深度、代码 stub 可执行性 |
| 论文 9 节写作 | **4 轮** | 每节 prompt 各 1 轮 + 整体连贯性 1 轮（最关键）|

**总成本预算**：~15 轮 prompt 迭代 × ~1.5 USD/轮 ≈ **25 USD 上限**（实际可能 8-15 USD）。M3 单档定价（待 Day 1 探明精确值，placeholder 按 Sonnet 4.6 档估算）。每次迭代结束打印 token 计数。

**verdict 红了怎么办**（重要 — 没有 tier 切换退路）：
- 唯一手段是**继续调 M3 prompt**（M3 一档，没有"换模型"这条路）
- 4 轮内未达标 → 标黄但**仍交付**（让用户 PM 视角判断"模板感"是否可接受）
- 9 节论文若整篇 M3 4 轮仍红 → 接受"模板感"上限，不强求 Opus 级（如果未来用户接入真 Opus，可重跑历史 topic）
- 计入 DoD：每 LLM tab 的"未达标节"清单 + 用户决策记录入 `Tasks/{topic}/quality_decisions.md`

**Prompt 版本管理**：
- 每个 prompt 模板存 `Program/prompts/{tab}/{tab}_v{N}.md`（带 commit）
- 每次调优记录到 `Program/prompts/{tab}/CHANGELOG.md`（写"为什么改 + 改了什么"）
- LLM 调用的 prompt_version 进 provenance 元数据（接 §5.2）
- "可复现"的定义升级为"**指定 prompt_version 可重跑**"

**Re-tune 触发**（不锁死调优结束）：
- 用户随时可要求"这节再调一版"（不受 2-4 轮上限约束）
- 但超出预算的调优需要单独 token 预算审批

---

## 5. Data Flow & Persistence

### 5.1 文件落盘约定

```
{project_root}/
├── Tasks/
│   └── {topic-slug}/
│       ├── brief.md           (任务书 LLM 扩写)
│       ├── literature.md      (递归搜索结果)
│       ├── variables.yaml     (数据变量映射)
│       ├── design.json        (方法设计)
│       └── execution.log      (执行实验 SSE 流式日志)
├── Manuscripts/
│   └── {topic-slug}/
│       └── paper.pdf          (最终论文)
├── Results/
│   └── {topic-slug}/
│       ├── results.json       (StatsPAI 统计量)
│       └── tables/            (回归表等)
└── Program/
    └── runs/{topic-slug}/     (本次跑用的 Python 脚本、prompt 模板)
```

### 5.2 Provenance 元数据（每个产出文件带 frontmatter）

```yaml
---
topic: 工业机器人对城市制造业就业结构的影响——基于 CFPS 2010-2022 的证据
topic_slug: industrial-robots-cfps-2010-2022
generated_by: brief+arxiv+llm-rerank
timestamp: 2026-06-04T05:30:00Z
model: MiniMax-M3            # 唯一真实模型; llm_client.py 中其他 label 都是 alias
prompt_version: v1.2
seed_query: brief.md
upstream:
  - brief.md
downstream_consumers:
  - variables.yaml
---
```

### 5.3 重跑机制（"可复现"的具体实现）
- 单 tab re-run：用户改 prompt/数据集/方法，重新跑那一个 tab，下游产物保留上游
- 端到端 re-run：用户重输同一 topic，从任务书开始，所有产物可选择性 re-run
- 第二天 re-run：浏览器打开同一 topic，看到同样 5 tab 状态 + 同样最终 PDF 路径

---

## 6. Acceptance Criteria (BDD)

### 6.1 5 tab BDD 验收

| Tab | Given | When | Then |
|---|---|---|---|
| 任务书 | 用户输入 "工业机器人对城市制造业就业结构的影响——基于 CFPS 2010-2022 的证据" | 点提交 | 4 段简报生成，写入 `Tasks/{topic}/brief.md`，可点"重生成"或"手动编辑" |
| 递归搜索 | 任务书已确认 | 点"开始搜索" | `Tasks/{topic}/literature.md` 出现，含 8-12 篇精选论文（题名/作者/年份/摘要/相关性评分），用户能勾选"采纳/排除" |
| 数据变量 | 任务书已确认、用户选 CFPS | 点"识别变量" | `Tasks/{topic}/variables.yaml` 出现，含 5-10 个研究变量（X/Y/控制变量），每个有"列名映射 + 语义说明 + 引用文献" |
| 方法设计 | 数据变量已确认 | 点"设计方法" | `Tasks/{topic}/design.json` 出现，含 3 个候选方法 + LLM 解释 + StatsPAI estimand 推荐 + Python 代码 stub |
| 执行实验 | 方法设计已确认 | 点"开始跑" | SSE 流式返回进度，最终 `Manuscripts/{topic}/paper.pdf` 落盘 + `Results/{topic}/results.json` 含所有统计量 |

### 6.2 端到端贯通验收
**单一用例**：从空白浏览器开始，60 分钟内完成 5 tab 走通，得到一份可入库的 paper.pdf。
- 跑完后 `Tasks/{topic}/` 里有 4 个文件
- `Manuscripts/{topic}/` 里有 paper.pdf
- `Results/{topic}/` 里有 results.json
- 用户第二天打开同一 topic，能看到同样 5 tab 状态 + 同样最终 PDF 路径

### 6.3 失败模式（要正面处理）

| 失败 | 表现 | 应对 |
|---|---|---|
| arxiv-mcp 不可用 | 递归搜索返回 0 篇 | Tab 显示"搜索服务暂不可用，可手动添加论文" + 留空输入框 |
| LLM API 超时 | 4 个 LLM tab 卡 loading | 自动重试 2 次，失败后让用户重试或换 prompt |
| StatsPAI 数据集缺失 | 数据变量报"CFPS 未在 `data/` 找到" | Tab 提示"请把 CFPS CSV 放到 `data/cfps/`" |
| 执行实验跑超 60 分钟 | SSE 断线 | 客户端断线重连，后端继续跑，不浪费已计算结果 |
| LLM 输出不符合 schema | Tab 显示"AI 输出格式异常" | 后端自动重试 1 次，失败后让人介入 |

### 6.4 质量门（verdict gate 复用）
复用之前 91K pipeline 用的判分：
- 任务书：判定"是否含 4 段"
- 递归搜索：判定"是否含 N 篇 + 相关性评分"
- 数据变量：判定"是否含 N 个变量 + 映射完整"
- 方法设计：判定"是否含 3 个候选 + StatsPAI 推荐"
- 执行实验：判定 paper.pdf 是否含 9 节 + results.json 是否含 p 值

每个 tab 通过门才能解锁下一个。

---

## 7. Risks & Mitigations

| # | 风险 | 严重度 | 缓解 |
|---|---|---|---|
| 1 | LLM 写 9 节质量不达标（部分节空洞、verdict 判红）| 高 | 每个 tab 都接 verdict gate，红色让人介入；先跑 1 节让用户看质量，再调 prompt |
| 2 | CFPS 真实数据缺失（项目里可能只有 schema 描述）| 高 | Day 1 audit `data/`、`Tasks/data/`，缺则用"schema + 10 行样本"demo 通 |
| 3 | ManuscriptAgent 现状未明（之前 91K 是模板，集成时可能发现不是 LLM）| 中 | Day 1 audit ManuscriptAgent 源码，模板则本次只做"贯通"，不优化写作 |
| 4 | Token 成本（5 tab 走完预计 5-10 USD）| 低 | 每次跑完打印 token 计数，让用户决定值不值；可重跑不毁旧结果 |
| 5 | 5 agent 并行协调（API 契约没冻结会出乱子）| 中 | Day 1 先冻结 5 个 endpoint 的 OpenAPI，再派 agent；每日同步一次 |

---

## 8. Day-by-Day Plan

```
Day 1 (今日): 冻结 + audit
  ├─ 冻结 5 endpoint OpenAPI 规范
  ├─ audit CFPS 数据是否真存在
  ├─ audit ManuscriptAgent 是模板还是 LLM
  └─ 用户确认审计结果，决定 Day 2 是否启动

Day 2-3: 5 agent 并行
  ├─ Agent 1: 任务书 polish (LLM 扩写 + 持久化)
  ├─ Agent 2: 递归搜索 (arxiv + LLM 重排)
  ├─ Agent 3: 数据变量 (CFPS 解析 + LLM 映射)
  ├─ Agent 4: 方法设计 (StatsPAI + LLM 解释)
  └─ Agent 5: 执行实验 (SSE + ManuscriptAgent)

Day 4: 集成 + 第一跑 + 识别弱 prompt
  ├─ 5 个 endpoint 串起来
  ├─ 端到端跑一次（用 session 里的工业机器人题目），v1 prompt
  ├─ 收集 verdict gate 红色信号 + 用户反馈
  └─ 输出"prompt 调优清单"（哪个 tab 的哪一节需要改）

Day 5-6: Prompt 调优（核心质量阶段）
  ├─ Day 5 上午：调优 任务书 + 递归搜索（2 轮）→ 跑 → 验收
  ├─ Day 5 下午：调优 数据变量 + 方法设计（3 轮）→ 跑 → 验收
  ├─ Day 6 上午：调优 9 节论文写作（4 轮）→ 跑 → 验收
  └─ Day 6 下午：用户 PM 视角验收 paper.pdf，对照 verdict 评分

Day 7: 修 + 文档 + DoD 验收
  ├─ 修 Day 5-6 验收遗留问题
  ├─ 写 spec runner（明天能 re-run 同一 topic）
  ├─ 打印最终 token 成本
  └─ 出 60 分钟贯通 demo（用调优后的 prompt）
```

---

## 9. Definition of Done (DoD)

满足**全部**才算这个 spec 跑完：
- [ ] 5 个 tab 各自 BDD 验收通过（§6.1 那个表全绿）
- [ ] 端到端 60 分钟内跑通 1 次，得到 paper.pdf
- [ ] 失败模式 5 种都被正面处理
- [ ] 5 个 tab 产物都入库到 `Tasks/{topic}/` + `Manuscripts/{topic}/` + `Results/{topic}/`
- [ ] 第二天能 re-run 拿到等价结果（不是逐字相同，但 9 节结构、关键发现、变量选择一致）
- [ ] 每个 LLM tab 的 prompt 已按 §4.6 预算迭代到对应轮数（任务书 2 / 搜索 2 / 变量 3 / 设计 3 / 写作 4）
- [ ] Token 成本打印出来给用户看，且 ≤ 25 USD（§4.6 M3 单档预算）
- [ ] 用户 PM 视角验收过

---

## 10. Open Questions（Day 1 audit 后回答）

1. CFPS 真实 CSV 在 `data/cfps/` 还是 `Tasks/data/`？schema 完整吗？
2. `ManuscriptAgent` 当前是模板填空还是 LLM 调用？调用的是什么 LLM？
3. 之前 91K pipeline 跑出的 paper.pdf 在 `Manuscripts/industrial-robots-cfps-2010-2022/` 吗？要拿来做模板还是覆盖？
4. `Product/backend/` 40 个 service 哪些可以 import，哪些是 stub？
5. 后端 SSE 基础设施（如果有）能复用吗？
6. **MiniMax M3 真实定价**（input/output 每 MTok 各多少）？当前 §4.6 预算 25 USD 是按 Sonnet 4.6 档 placeholder 估的，差 3-5 倍就可能需要重新定预算
7. **M3 调用入口**：在 `llm_client.py` 里应该用哪个具体的 model 字符串？是 `MiniMax-M3` 还是某个 label 才会路由到 M3？需 Day 1 跑一个最小测试确认

---

## 11. Out of Scope（明确不做）

详见 §2.2。补充：
- 跨 topic 的清理 / 归档
- 论文多版本管理（每个 topic 只保留最新 1 版）
- 国际化（界面只做中文）
- 离线模式（必须连 Claude API）
- 用户账号系统

---

## 12. References

- 上次 session：5851a729-e6a4-49aa-909f-576b0b06ae2a（3 天工作，2936 条消息）
- 项目根：`/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/`
- StatsPAI：`../StatsPAI/` 因果断面 SDK
- Awesome-Agent-Skills：`../Awesome-Agent-Skills-for-Empirical-Research/`
- 91K pipeline：`Program/workbench/manuscript_section_draft_expansion.py`
- 现有服务层：`Product/backend/*_service.py`
- React 前端：`Product/web-react/src/App.tsx:108-131`
