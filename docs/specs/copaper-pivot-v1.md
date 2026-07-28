# Spec: econpaper v1 — CoPaper 对标品（中文原生 + 极致章节交互 + LaTeX/Word 兼容）

**Effort:** copaper-pivot
**Spec version:** v1
**Created:** 2026-07-27
**Status:** ready-for-agent
**Triage label:** ready-for-agent

**Sources:**
- [map.md](../../实证论文项目模板/.scratch/copaper-pivot/map.md)
- [T01 Research: Academic automation landscape](../../实证论文项目模板/.scratch/copaper-pivot/issues/01-research-academic-automation-landscape.md)
- [T02 Research: Agent architecture — Loop vs Graph](../../实证论文项目模板/.scratch/copaper-pivot/issues/02-research-agent-architecture-loop-vs-graph.md)
- [T03 Grilling: 4 subsystems repositioning](../../实证论文项目模板/.scratch/copaper-pivot/issues/03-grilling-subsystem-repositioning.md)
- [T04 Grilling: Differentiation positioning](../../实证论文项目模板/.scratch/copaper-pivot/issues/04-grilling-differentiation.md)

---

## Problem Statement

经济学研究者（含产品经理 + 研究者双用户群）在写实证论文时面临三重困境：

1. **没有趁手的中文工具**：Stanford CoPaper.ai 是唯一成熟的"AI 协作写实证论文"产品，但它是英文 only，不支持中文数据集（CHARLS/CFPS/CGSS）和国内核心期刊排版规范
2. **章节式协作交互普遍很差**：现有 AI 论文工具要么一次性黑盒生成（无 HITL），要么交互卡顿不流畅，没有产品做到"章节式暂停 + 流式打字 + 实时回滚 + 章节类型感知"的组合
3. **排版输出格式不全**：国外产品只输出 DOCX，不满足国内本科/硕论的 Word 排版要求；直接 AI 生成 PDF/docx 效果差，LaTeX 路径更稳定但没有产品内嵌

研究者需要一个**给中文用户做的、交互极致流畅的、兼顾 LaTeX 规范和 Word 兼容的**经济学论文 AI 协作工具。

## Solution

**econpaper** — 一个 Web SaaS 产品，让用户上传真实数据集，通过 LangGraph 编排的 Agent 章节式生成实证论文，每章暂停等用户反馈，最终输出 LaTeX 源码 + Pandoc 转换的 Word + 可复现的 Python/Stata/R/EViews 代码。

### 核心流程

```
用户上传数据 (CSV/Excel/JSON/Parquet)
    ↓
数据清洗（clean_data 节点，8 个子步骤，HITL 暂停）
  ├─ 数据契约与 profiling（变量类型推断 + 缺失率 + 分布）
  ├─ 多期/多源数据合并（CHARLS 5 波 append + merge）
  ├─ 缺失值处理（删除 / 单值插补 / MICE，HITL 选策略）
  ├─ 异常值处理（IQR 检测 + winsorize，显示前后对比）
  ├─ 变量重编码与构造（encode / 分箱 / 对数 / 交互项 / 政策虚拟变量）
  ├─ 样本筛选（按年龄/时间/处理组，条件构建器）
  ├─ 面板平衡性检查（attrition 检测 + balance_panel）
  └─ 清洗留痕（生成 Python + Stata 脚本，写入 Raw/Interim/Final）
    ↓
EDA 探索（侧边栏 StatsPAI 集成）
    ↓
用户设定研究方向 + 变量选择
    ↓
Agent 生成 outline（HITL 暂停，用户审阅）
    ↓
逐章生成（每章 HITL 暂停，用户可调整 prompt / 回滚 / 暂停）
    ↓
代码翻译（Python → Stata/R/EViews，via stata-code）
    ↓
排版输出（LaTeX 模板 + Pandoc 转 Word）
    ↓
导出（.tex / .docx / .py / .do / .R / .m）
```

> **修正记录（2026-07-27）**：原 v1 流程图从 `upload_data` 直接跳到 `eda`，漏掉了 Bryce Wang 体系（AERS Stage 04）的"数据获取与清洗"阶段。CoPaper.ai 明确有 preparation agent；旧产品模板 `master.do` 有 `STEP 1: CLEAN`；AERS 8 步实证闭环的前 3 步是"数据清洗 → 变量构造 → 描述统计"。修正后新增 `clean_data` 节点，覆盖全部 8 个子步骤，不简化。

### 三栏沉浸式前端

- **左栏**：大纲面板（可拖拽排序改顺序，显示当前章节状态）
- **中栏**：实时流式输出编辑器（打字机效果，章节类型感知：绪论/文献综述/数据描述/方法/结果/结论不同生成策略）
- **右栏**：Agent 控制面板（任务状态、当前 prompt、可暂停/回滚/调整）

### Workspace 架构

```
/Users/mahaoxuan/Desktop/经济学论文/
├── econpaper/                        ← 本产品仓库
│   ├── frontend/                     ← 三栏沉浸式 UI
│   ├── backend/                      ← FastAPI + LangGraph orchestration
│   ├── agent/                        ← LangGraph graph 定义 + 节点实现
│   └── docs/                         ← 本 spec + ADRs
├── StatsPAI/                         ← private fork + 中文扩展（上游依赖）
├── Auto-Empirical-Research-Skills/   ← private fork + 中文扩展（上游依赖）
└── stata-code/                       ← private fork + 集成（上游依赖）
```

## User Stories

### 用户身份
- US-001: 作为经济学研究者，我想用一个 Web 工具从数据上传到论文导出全流程，这样不用在多个工具间切换
- US-002: 作为产品经理（非程序员），我想用图形界面完成实证论文写作，这样不用写代码
- US-003: 作为研究者，我想在每章生成后暂停审阅并调整，这样保证论文方向受我控制
- US-004: 作为研究者，我想随时回滚到之前的章节版本，这样不怕 AI 跑偏

### 数据上传与 EDA
- US-005: 作为研究者，我想上传 CSV/Excel/JSON/Parquet 文件，这样能开始论文流程
- US-006: 作为研究者，我想上传最多 20 个数据集，这样能做跨数据集分析
- US-007: 作为研究者，我想自动检测 Excel multi-sheet，这样不用手动拆分
- US-008: 作为研究者，我想在侧边栏点按钮跑描述统计，这样不用写 pandas 代码
- US-009: 作为研究者，我想在侧边栏生成相关性热图，这样能快速看变量关系
- US-010: 作为研究者，我想在侧边栏跑回归诊断图，这样能判断模型适用性
- US-011: 作为研究者，我想看到变量类型自动推断（数值/分类/日期），这样不用手动声明

### 数据清洗（clean_data 节点，8 个子步骤）
- US-011a: 作为研究者，我想看到数据 profiling 报告（变量类型 / 缺失率 / 唯一值数 / 分布），这样能快速了解数据质量
- US-011b: 作为研究者，我想上传 CHARLS 多期数据时自动按 ID+year 拼接成面板，这样不用手写 merge
- US-011c: 作为研究者，我想选择缺失值处理策略（删除 / 单值插补 / MICE 多重插补），这样控制清洗逻辑
- US-011d: 作为研究者，我想看到异常值检测报告 + winsorize 前后分布对比，这样判断缩尾是否合理
- US-011e: 作为研究者，我想在 UI 里构造新变量（分类 encode / 连续分箱 / 对数变换 / 交互项 / 政策虚拟变量），这样不用写代码
- US-011f: 作为研究者，我想用条件构建器筛选样本（年龄/时间/处理组），这样得到分析样本
- US-011g: 作为研究者，我想看到面板平衡性报告（attrition 检测），这样判断面板是否可用
- US-011h: 作为研究者，我想下载清洗脚本（Python + Stata 两种），这样能本地复现清洗逻辑

### 研究方向设定
- US-012: 作为研究者，我想输入研究问题（中文），这样 Agent 知道我要研究什么
- US-013: 作为研究者，我想选择自变量/因变量/控制变量，这样 Agent 知道变量结构
- US-014: 作为研究者，我想选择计量方法（从 38 种中选或让 Agent 推荐），这样控制分析路径
- US-015: 作为研究者，我想选择论文模板（中文核心期刊/本科/硕论/英文投稿），这样排版规范对齐

### Outline 生成与审阅
- US-016: 作为研究者，我想看到 Agent 生成的 outline（章节列表），这样审阅结构
- US-017: 作为研究者，我想拖拽章节改顺序，这样调整论文结构
- US-018: 作为研究者，我想删除某章或添加章节，这样定制结构
- US-019: 作为研究者，我想在 outline 阶段就看到每章的研究问题，这样判断方向
- US-020: 作为研究者，我想在 outline 暂停时调整研究方向，这样影响后续生成

### 章节式生成
- US-021: 作为研究者，我想看到当前章节的生成进度（流式打字），这样有"AI 在写"的体感
- US-022: 作为研究者，我想随时按"暂停"按钮中断当前章节生成，这样能调整 prompt
- US-023: 作为研究者，我想在章节完成后看到"上一章/下一章"导航，这样顺序审阅
- US-024: 作为研究者，我想编辑生成的内容（直接改文字），这样打磨表达
- US-025: 作为研究者，我想对某一章"重新生成"，这样不满意的章节重写
- US-026: 作为研究者，我想看到章节类型标签（绪论/文献综述/数据描述/方法/结果/结论），这样知道当前在写哪部分
- US-027: 作为研究者，我想在写"方法"章节时看到 Agent 选择的计量方法，这样判断合理性
- US-028: 作为研究者，我想在写"结果"章节时看到 Agent 调用 StatsPAI 的中间结果，这样验证数据真实性
- US-029: 作为研究者，我想在生成中看到 token 消耗估算，这样控制成本

### 代码翻译与复现
- US-030: 作为研究者，我想下载生成的 Python 代码，这样能本地复现
- US-031: 作为研究者，我想下载 Stata 代码（.do 文件），这样用 Stata 复现
- US-032: 作为研究者，我想下载 R 代码，这样用 R 复现
- US-033: 作为研究者，我想下载 EViews 代码，这样用 EViews 复现
- US-034: 作为研究者，我想看到代码中引用的 StatsPAI 函数文档，这样理解分析逻辑

### 排版与导出
- US-035: 作为研究者，我想下载 LaTeX 源码（.tex），这样能投稿中文核心期刊
- US-036: 作为研究者，我想下载编译好的 PDF，这样直接看排版效果
- US-037: 作为研究者，我想下载 Word 文档（.docx，via Pandoc），这样满足本科/硕论要求
- US-038: 作为研究者，我想选择中文核心期刊模板（经济研究/管理世界/中国工业经济等），这样排版规范对齐
- US-039: 作为研究者，我想实时预览 LaTeX 排版效果，这样调整时看到结果
- US-040: 作为研究者，我想手动编辑 LaTeX 源码，这样精细调整格式

### 进度与状态管理
- US-041: 作为研究者，我想看到整体论文生成进度条，这样知道还剩多久
- US-042: 作为研究者，我想在浏览器崩溃/关闭后恢复进度，这样不用从头开始
- US-043: 作为研究者，我想看到当前 LangGraph 节点的状态（drafting/paused/generating），这样理解 Agent 行为
- US-044: 作为研究者，我想在 30 分钟左右得到完整论文，这样不用等太久

### 数据集原生支持
- US-045: 作为研究者，我想用 CHARLS 数据集时看到原生向导（变量映射/年份选择/样本筛选），这样不用手动处理
- US-046: 作为研究者，我想用 CFPS 数据集时看到原生向导，这样不用手动处理
- US-047: 作为研究者，我想用 CGSS 数据集时看到原生向导，这样不用手动处理

## Implementation Decisions

### 架构决策

1. **Agent 框架：LangGraph（Hybrid 架构）**
   - 外层 LangGraph 状态机，定义 9-11 个节点（upload_data / **clean_data** / eda / set_direction / pick_method / generate_outline / generate_chapter_N / translate_code / export_docx）
   - **clean_data 节点**是 HITL 暂停点，内部拆 8 个子步骤（契约+合并+缺失值+异常值+变量构造+样本筛选+平衡性+留痕），覆盖 AERS Stage 04 全流程；复用 StatsPAI 的 `read_data`/`winsor`/`mice`/`balance_panel`/`outlier_indicator`，其余清洗逻辑（merge/reshape/encode/样本筛选）econpaper 自实现
   - `draft_chapter` 和 `pick_method` 节点内嵌小 ReAct loop（max_iterations=10，token budget cap）
   - 38 方法 dispatch 走静态路由表 + 一个 LLM routing 节点（Anthropic Routing workflow 模式），不把 38 工具塞给 ReAct loop
   - 理由详见 [T02](../../实证论文项目模板/.scratch/copaper-pivot/issues/02-research-agent-architecture-loop-vs-graph.md) §5-§8

2. **Durable execution：PostgresSaver checkpoint**
   - 开发用 InMemorySaver，生产用 PostgresSaver
   - Durability 模式默认 `sync`（每步前持久化），性能瓶颈时改 `async`
   - `@task` 装饰器缓存已完成章节，resume 时不重跑
   - 30 分钟长流程崩溃可从最近 checkpoint 恢复

3. **HITL 实现：LangGraph `interrupt()` + `Command(resume=...)`**
   - 每章生成后调 `interrupt(value=chapter_content)` 暂停
   - 前端收到 interrupt 信号后展示章节内容 + "继续/调整/回滚"按钮
   - 用户操作通过 `Command(resume=user_input)` 恢复 graph 执行

4. **前端架构：三栏沉浸式 Web UI**
   - 左栏大纲（可拖拽，dnd-kit 或类似库）
   - 中栏流式编辑器（基于 Monaco Editor 或 CodeMirror，支持流式 append）
   - 右栏 Agent 控制面板（任务状态、prompt 输入、暂停/回滚按钮）
   - WebSocket 连接后端接收流式输出 + interrupt 信号
   - 章节类型感知：每章带 type 标签（intro/lit_review/data_desc/methods/results/conclusion），不同 type 走不同 prompt 模板

5. **后端：FastAPI + LangGraph**
   - FastAPI 提供 REST + WebSocket
   - LangGraph graph 编排 Agent 流程
   - 上传文件存到本地 disk（开发）或 S3-compatible storage（生产）

6. **StatsPAI / AERS / stata-code 集成**
   - StatsPAI 作为 Python 库依赖（`pip install -e ../StatsPAI`），graph 节点直接调 `statspai.causal.<method>()`
   - AERS 作为 prompt/skill 库，graph 节点根据章节类型从 AERS 加载对应 skill
   - stata-code 作为代码翻译引擎，`translate_code` 节点调 `stata_code.translate(python_ast, target="stata")`

### 模块划分

7. **econpaper/frontend/** — 三栏 UI
   - 大纲组件（dnd-kit + 章节状态）
   - 流式编辑器组件（Monaco/CodeMirror + WebSocket）
   - Agent 控制面板组件
   - EDA 侧边栏组件（按钮触发 StatsPAI 调用 + 结果可视化）
   - LaTeX 预览组件
   - 导出对话框组件

8. **econpaper/backend/** — FastAPI 服务
   - 文件上传 endpoint（multipart/form-data，支持多文件）
   - WebSocket endpoint（流式输出 + interrupt 信号）
   - LangGraph graph 实例管理（per-session graph + checkpoint）
   - 导出 endpoint（生成 .tex/.docx/.py/.do/.R/.m 并打包下载）

9. **econpaper/agent/** — LangGraph graph 定义
   - graph 定义（nodes + edges + interrupt points）
   - 节点实现（upload_data / eda / set_direction / pick_method / generate_outline / generate_chapter / translate_code / export_docx）
   - 路由表（38 方法 → StatsPAI 函数映射）
   - prompt 模板（6 种章节类型各一套模板）

10. **econpaper/docs/specs/** — spec 文档（本文件）

11. **econpaper/docs/adr/** — 架构决策记录
    - ADR-0001: 选用 LangGraph 作为 Agent 框架
    - ADR-0002: 选用 LaTeX + Pandoc 作为排版方案
    - ADR-0003: 三栏沉浸式布局作为前端架构
    - ADR-0004: Private fork 策略（StatsPAI/AERS/stata-code）

### Schema / API 契约

12. **Session 状态 schema**（LangGraph State TypedDict）：
    ```python
    class EconPaperState(TypedDict):
        session_id: str
        uploaded_datasets: list[DatasetMeta]  # [{path, format, sheets, columns}]
        eda_results: Optional[EDAResult]
        research_direction: Optional[ResearchDirection]  # {question, dv, iv, controls, method}
        outline: Optional[Outline]  # [{chapter_type, title, research_question}]
        chapters: list[Chapter]  # [{type, title, content, status, version}]
        code_translations: Optional[CodeTranslations]  # {python, stata, r, eviews}
        latex_source: Optional[str]
        export_formats: list[str]  # ["tex", "pdf", "docx", "py", "do", "R", "m"]
    ```

13. **WebSocket 消息 schema**：
    ```typescript
    type WSMessage =
      | { type: "streaming_chunk", chapter_id: str, chunk: str }
      | { type: "interrupt", chapter_id: str, content: str }
      | { type: "status", node: str, status: "running"|"paused"|"done" }
      | { type: "error", message: str }
    ```

14. **REST API 契约**：
    - `POST /upload` — 上传数据集，返回 dataset_meta
    - `POST /sessions` — 创建新 session，返回 session_id
    - `WS /sessions/{id}/stream` — 流式输出 + interrupt
    - `POST /sessions/{id}/resume` — 用户审阅后恢复，传 `Command(resume=...)` 的 payload
    - `POST /sessions/{id}/rollback` — 回滚到指定章节版本
    - `GET /sessions/{id}/export?format=tex|pdf|docx|py|do|R|m` — 导出

### 交互细节

15. **章节类型感知**：6 种章节类型（intro / lit_review / data_desc / methods / results / conclusion），每种走不同 prompt 模板
16. **流式打字效果**：LLM 输出 token 通过 WebSocket 实时推送到前端，前端 append 到编辑器（不重渲染整段）
17. **暂停/回滚**：用户按"暂停"触发前端 WS 消息 → 后端调 `interrupt()` → 用户可编辑当前内容或回滚到上一版本 → 通过 `Command(resume=...)` 恢复
18. **EDA 侧边栏**：点击按钮 → 后端调 StatsPAI → 返回 plotly figure / pandas describe 表格 → 前端渲染
19. **LaTeX 实时预览**：用户编辑 LaTeX 源码 → 后端 `latexmk` 编译 → 返回 PDF 页面截图 → 前端展示

## Testing Decisions

### Testing Seams（2 个，与用户确认）

**Seam 1：LangGraph graph 整体行为**
- 测试输入：mock 数据集 + mock 研究方向
- 测试输出：期望生成的章节内容结构 + LaTeX 源码 + 代码翻译
- 不测试内部节点实现细节（pick_method 怎么选、draft_chapter 怎么写）
- 测试方式：pytest + LangGraph test utilities（`graph.stream()` + assert state transitions）
- Prior art：LangGraph 官方测试文档 https://reference.langchain.com/python/langgraph/testing

**Seam 2：前端三栏交互**
- 测试输入：用户操作序列（拖拽大纲 / 暂停 / 回滚 / 编辑）
- 测试输出：UI 状态变化 + WebSocket 消息序列
- 测试方式：Playwright E2E + Vitest 组件测试
- Prior art：Playwright 官方文档 + dnd-kit 测试示例

### 测试范围

**会测试的模块**：
- `econpaper/agent/` graph 整体行为（Seam 1）
- `econpaper/frontend/` 三栏交互（Seam 2）
- `econpaper/backend/` REST + WebSocket endpoint 契约

**不会测试的模块**（信任上游）：
- StatsPAI / AERS / stata-code 的内部实现（fork 的上游依赖）
- LangGraph 框架本身（信任 Anthropic/LangChain）
- FastAPI / Monaco Editor / dnd-kit 等第三方库

### 测试质量标准

- 只测外部行为，不测实现细节（Matt's rule）
- 现有 seam 优先于新 seam（本 spec 是新项目，无现有 seam）
- 2 个 seam 是最少必要数量，不增加第 3 个

## Out of Scope

### 不做的差异化方向（T04 明确排除）
1. **教学场景**（面向学生/教师的作业批改/课程管理）—— 定位仍是研究者工具
2. **方法论前沿改进**（超越 CoPaper 38 方法，比如前沿 DID estimator / RDD 改进）—— 38 方法够用，扩展走 StatsPAI 上游 sync
3. **完全开源**—— econpaper 产品本身闭源，3 个 fork 仓库 private
4. **Agent 透明度 / 可解释 Agent**（trace LLM 决策路径）—— 章节式 HITL 已给用户控制权
5. **复现性深度**（docker / virtualenv 一键复现）—— Stata/R/EViews 代码 + LaTeX 源码已足够

### 不做的时间承诺
6. **强制 5-30 分钟 SLA**—— 30 分钟是基准期望，不是硬性限时

### 不做的产品形态
7. **CLI 工具**—— 只做 Web SaaS
8. **Jupyter 工作流**—— 只做 Web SaaS
9. **IDE 插件**—— 只做 Web SaaS

### 不做的范围
10. **StatsPAI / AERS / stata-code 的内部修改**—— 只 fork + 加中文扩展 skill，不改上游代码
11. **多语言扩展**（除 Python/Stata/R/EViews 外的语言）—— 不做
12. **商业化 / 定价模型**—— 本 spec 只定产品定位，不定商业模式
13. **旧仓库代码迁移**—— 从零开始，不迁移 `实证论文项目模板/` 的任何代码

## Further Notes

### 关键背景（来自 T01-T04 调研 + grilling）

1. **我们一直在 mirror Bryce Wang (Stanford REAP) 的体系**：StatsPAI / AERS / stata-code / CoPaper.AI 是同一人作品。我们的 workspace 已经 fork 了前三个，econpaper 是补齐消费端产品。
2. **经济学自动化是蓝海**：Dawid et al. (arxiv 2504.09736) 显示 421 篇 agentic workflow 研究中只有 4 篇经济学。
3. **经济学家同行选择 Graph**：Korinek (UVA) 用 LangGraph，Dawid et al. 用 AutoGen，Bryce 推断也用 Graph。
4. **CoPaper.ai 是 closed-source**：我们的差异化不是技术架构（架构相同），是中文原生 + 极致交互 + LaTeX/Word 兼容。

### 已知风险（来自 T02）

| 风险 | 缓解 |
|---|---|
| LangGraph lock-in | MIT 开源 + state 格式公开；最坏自己用 Postgres + 状态机库重写 |
| 过度 graph 化（over-graphing） | 只在 graph 表达自然的地方用 graph；写章节留 ReAct loop |
| 内部 loop 成本失控 | max_iterations=10 + token budget + early stop |
| Checkpointer 选择 | 开发 InMemorySaver，生产 PostgresSaver，高并发 AsyncPostgresSaver |
| StatsPAI 边界 | graph 调 StatsPAI 函数（每个方法一个节点），不把 StatsPAI 拆成 38 独立工具 |
| vs CoPaper 差异化不足 | 架构相同但形态不同：中文 / 极致交互 / LaTeX+Word |

### 下一步（to-tickets 阶段输入）

本 spec 完成后，进入 `to-tickets` 阶段，拆成 tracer-bullet 垂直切片。每个 ticket 声明 blocking edges。**实际 ticket 已发布到** [econpaper/.scratch/copaper-pivot-v1/issues/](../../.scratch/copaper-pivot-v1/issues/)，共 11 个：

| # | Ticket | Blocked by | 端到端 demo |
|---|---|---|---|
| 01 | Workspace bootstrap | — | 4 仓库依赖装好，dev server 起来 |
| 02 | Hello-world paper | 01 | 上传 5 行 → 最小清洗 → 生成标题 → 下载 .tex |
| 03 | EDA 侧边栏 | 02 | 点 describe → 表格渲染 |
| 04 | 数据准备切片（契约+合并+缺失值+异常值）| 02 | CHARLS 5 波 → 4 子步骤清洗 → 暂停 |
| 05 | 分析样本构造切片（变量构造+筛选+平衡性+留痕）| 04 | 干净数据 → 变量构造 → 样本筛选 → 脚本下载 |
| 06 | Outline + HITL 暂停 | 02 | 输入方向 → 生成 outline → 拖拽调整 → resume |
| 07 | 第 1 章生成 + 6 种 prompt 模板 | 06 | 生成 intro，6 种 prompt 全写完 |
| 08 | 全 6 章 + 回滚 | 07, 03, 05 | 循环生成 6 章 + 版本回滚 |
| 09 | 代码翻译 | 08 | Python → Stata/R/EViews |
| 10 | LaTeX + Word 导出 | 08 | 6 章组装 → latexmk → .tex/.pdf/.docx |
| 11 | CHARLS 数据集原生向导 | 04 | 上传 CHARLS → 识别 → 变量映射向导 |

每个 ticket 的完整定义见 issues 目录下对应文件。
