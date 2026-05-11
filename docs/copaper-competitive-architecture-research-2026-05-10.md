# CoPaper.AI 竞品与架构调研

日期：2026-05-10

范围：公开网页、公开 GitHub/PyPI 线索、CoPaper landing 前端静态资源中可见的路由/API 字符串。未登录、未绕过鉴权、未访问非公开数据。

## 1. 调研结论摘要

CoPaper.AI 不是普通“AI 写论文”产品，而是一个面向实证研究的端到端生产系统。它的产品承诺是：从数据上传、研究方向设定、实证建模、稳健性检验、图表/回归表生成，到论文正文与 DOCX 导出，形成一个可复现的研究流水线。

公开信息中最核心的架构线索有四个：

1. Skills 是方法论层：把 DID、IV、RDD、PSM、DML 等实证流程编码成结构化操作手册，而不是依赖模型临场发挥。
2. StatsPAI 是统计/因果推断执行层：提供 agent-native 的 Python API、统一结果对象、tool-calling schema、Word/LaTeX/Excel/HTML 输出。
3. PaperAgent 是多代理编排层：公开资料明确提到 Supervisor + 4 子代理，分别承担 preparation / modeling / visualization / writing。
4. Human-in-the-loop 是产品交互层：系统在 outline、变量选择、模型设定、结果解释等关键节点暂停，等待用户确认。

对我们项目的启发：我们不应该只把当前产品做成“漂亮的 Agent Cluster 页面”，而应该把它重塑为一个“本地优先的实证操作系统”。它既要有 CoPaper 那种低摩擦、清晰、可信的用户旅程，又要保留我们自己的差异化：本地数据、Codex 执行、多人多 Agent、权限/成本/能力注册、产物归属、审计日志、可回滚工作流。

## 2. 证据等级

### 2.1 直接证据

直接来自公开页面或公开仓库：

- CoPaper landing：`https://www.copaper.ai/landing`
- StatsPAI 官网：`https://www.statspai.com/`
- Awesome-Agent-Skills-for-Empirical-Research：`https://github.com/brycewang-stanford/Awesome-Agent-Skills-for-Empirical-Research`
- StatsPAI GitHub：`https://github.com/brycewang-stanford/StatsPAI`

### 2.2 静态资源证据

来自 CoPaper landing 页面加载的公开 Next.js chunk 中暴露的路由/API 字符串。只能说明前端 bundle 中存在相关调用点，不能证明后端实现细节、数据库结构或权限策略。

### 2.3 推断

本文中的“技术架构推断”基于公开文案、公开 API 字符串、公开开源包能力和产品常识。凡涉及后端内部服务、队列、数据库 schema、模型网关等细节，均为推断，不作为事实断言。

## 3. CoPaper 的产品结构

### 3.1 主叙事

CoPaper 对用户的主叙事非常直接：

- From Data to Paper
- 20 Minutes to a Reproducible Paper
- AI Research Co-Author
- 你是作者，AI 是研究合作者

这套叙事的关键不是“AI 很强”，而是“你只需要带着数据和研究方向进来，系统会把实证论文该走的流程组织起来”。

### 3.2 核心用户路径

公开页面描述的主路径是四步：

1. Upload Data：上传 CSV、Excel、Stata 等数据，自动识别变量类型和数据结构。
2. Set Research Direction：定义研究问题、方法偏好、变量选择，可手动设置，也可 AI 辅助推断。
3. AI Writes, You Guide：AI 逐章生成，并在每个章节/关键节点暂停，让用户审阅和反馈。
4. Refine & Export：AI 进行润色与审阅，最终导出完整 DOCX。

这四步非常适合转化成我们产品的一阶导航：

- 项目/数据
- 研究设计
- 实证执行
- 论文草稿
- 审阅与导出

### 3.3 公开承诺的能力

CoPaper 页面和 StatsPAI 页面共同呈现了以下能力：

- 多数据集上传：CSV、Excel、JSON、Parquet，页面文案还提到最多 20 个数据集。
- Excel 多 sheet 自动识别。
- 自动 EDA、变量定义、计量建模。
- OLS、Logit/Probit、中介分析、DID、IV、RD 等主流方法。
- 38+ econometric methods。
- 图表和回归表生成。
- Python 代码，以及 Stata / R / EViews 翻译。
- 论文结构生成：Introduction、Literature Review、Data & Methods、Results、Conclusion/Discussion。
- 多轮 polish / review。
- DOCX 导出。
- 5-30 分钟生成时间。

### 3.4 最重要的交互原则

CoPaper 的核心交互不是“全自动跑完”，而是“关键节点暂停确认”。公开页面明确强调，系统会在 outline、variable selection、model specification、result interpretation 等节点暂停。

对我们来说，这是关键：实证产品不能让用户觉得 AI 在黑箱里自作主张。每一次模型选择、变量处理、样本过滤、稳健性检验，都应该能被用户看到、确认、拒绝或重跑。

## 4. CoPaper 的公开技术架构线索

### 4.1 前端技术栈

从页面 HTML 和静态资源判断：

- 使用 Next.js / React。
- 使用 Next app router 风格的 RSC / chunk 结构。
- 使用 Tailwind 风格 utility class。
- 有 Google Analytics。
- 有明显 anti-bot / headless detection 逻辑。
- landing 页面是高度视觉化的营销页，实际 app 入口在登录/上传/项目相关路由后。

### 4.2 公开 API 面

从公开前端 chunk 中提取到的 API 字符串显示，CoPaper 的产品后端至少按以下域拆分：

认证与会话：

- `/api/auth/me`
- `/api/session/`
- `/api/sessions`
- `/api/trial/quota`
- `/api/trial/complete-session`
- `/api/trial/abandon-active-session`

数据上传：

- `/api/upload`
- `/api/upload/create-session`
- `/api/upload/inspect-sheets`
- `/api/upload/confirm-sheets`
- `/api/upload/from-cleaning-session`
- `/api/upload/from-cleaning-session-multi`

数据清洗 / Data Agent：

- `/api/cleaning/upload`
- `/api/cleaning/upload-batch`
- `/api/cleaning/upload-with-sheets`
- `/api/cleaning/session/`
- `/api/cleaning/stream`
- `/api/cleaning/datasets/`
- `/api/cleaning/preview/`
- `/api/cleaning/history/`
- `/api/cleaning/codebook/parse-preview`
- `/api/cleaning/infer-variable-definitions/`
- `/api/cleaning/variable-definitions/`
- `/api/cleaning/research-context/`
- `/api/cleaning/chart-preferences/`
- `/api/cleaning/paper-outline/`
- `/api/cleaning/download-paper-docx/`

Skills：

- `/api/cleaning/skills/builtin`
- `/api/cleaning/skills/active/`
- `/api/cleaning/skills/activate/`
- `/api/cleaning/skills/deactivate/`
- `/api/cleaning/skills/user`
- `/api/cleaning/skills/user/upload`
- `/api/cleaning/skills/user/fork/`

文献综述：

- `/api/literature-review/upload-paper-async`
- `/api/literature-review/parse-status/`
- `/api/literature-review/papers/`
- `/api/literature-review/outline/`
- `/api/literature-review/complete`
- `/api/literature-review/graph/start-upload-loop`
- `/api/literature-review/graph/upload-hitl-respond`
- `/api/literature-review/graph/parse-complete-resume`

论文生成与报告：

- `/api/generate`
- `/api/report/`
- `/api/report/update`
- `/api/batch-outline/upload`
- `/api/batch-outline/generate`
- `/api/batch-outline/status/`
- `/api/batch-outline/approve`

代码与 HITL：

- `/api/stream/code/`
- `/api/hitl/confirm`
- `/api/hitl/reject`
- `/api/hitl/code-retry/respond`

润色与改稿：

- `/api/refinement/init`
- `/api/refinement/chat`
- `/api/refinement/stream`
- `/api/refinement/status/`
- `/api/refinement/papers/`
- `/api/refinement/paper-stats/`
- `/api/refinement/upload-paper`
- `/api/refinement/undo`
- `/api/refinement/undo-info/`

格式与导出：

- `/api/export/docx`
- `/api/export/docx/status`
- `/api/export/markdown-to-docx`
- `/api/export/data-agent-docx`
- `/api/export/log`
- `/api/format/upload`
- `/api/format/templates`
- `/api/format/session/`
- `/api/format/stream`
- `/api/format/download/`
- `/api/format/download-converted/`
- `/api/format/replace-source/`

图表：

- `/api/figure/schema/`
- `/api/figure/edit/`

错误与后台：

- `/api/errors/`
- `/api/errors/db/`
- `/api/errors/db/clusters`
- `/api/errors/db/bulk-resolve`
- `/api/errors/db/bulk-delete`
- `/api/errors/stats`

商业化与模型配置：

- `/api/purchase/packs`
- `/api/purchase/create-checkout`
- `/api/purchase/history`
- `/api/admin/models`
- `/api/admin/available-models`
- `/api/admin/llm-config`
- `/api/admin/data-agent-config`
- `/api/admin/data-agent-model`

### 4.3 从 API 面反推的产品模块

这些 API 字符串说明，CoPaper 很可能不是单一的“生成论文”服务，而是至少包含以下模块：

1. Upload Session：处理数据上传、sheet 检测、数据集会话。
2. Cleaning/Data Agent：处理数据清洗、变量定义、研究上下文、图表偏好、paper outline。
3. Skill Registry：内置 skill、用户上传 skill、激活/停用 skill、fork skill。
4. Literature Review Agent：上传论文、异步解析、文献图谱/循环、HITL 响应。
5. Paper Generation：报告生成、outline batch、章节/报告更新。
6. Code Stream + HITL：代码生成流、确认/拒绝、失败重试。
7. Refinement Agent：论文上传、润色、对话式修改、撤销、状态流。
8. Formatting/Export：模板、格式转换、DOCX、Markdown-to-DOCX。
9. Figure Editor：图表 schema 与编辑。
10. Trial/Billing/Admin：试用额度、购买包、模型配置、LLM 配置。
11. Error Observability：错误日志、聚类、批量处理。

这说明其真实竞争力不只在 UI，而在“研究过程被拆成了明确的服务边界”。

## 5. CoPaper 与 StatsPAI 的关系

公开信息称 StatsPAI 是 CoPaper 的因果推断引擎。StatsPAI 的核心设计点：

- `import statspai as sp`
- 800+/900+ 函数规模，公开信息在不同页面有数字差异，说明项目增长很快。
- `list_functions()` / `describe_function()` / `function_schema()` 暴露 agent-native schema。
- 统一 `CausalResult` 对象。
- 结果对象支持 `.summary()` / `.plot()` / `.to_latex()` / `.to_docx()` / `.to_agent_summary()` 等。
- `sp.paper(data, question, ...)` 是端到端 orchestrator。
- `sp.paper` 公开描述为 `diagnose -> recommend -> estimate -> robustness -> PaperDraft`。
- 出错时不整体崩溃，而是以 Pipeline notes 方式隔离失败。
- 支持 OpenAI / Anthropic tool-calling schema，并有 MCP server scaffold。

对我们产品的启发：

1. 研究执行不能只返回一段文本，必须返回结构化 result object。
2. 每个任务都要有机器可读的 assumption、diagnostic、violation、recovery hint。
3. Agent 调用统计方法时不能靠自然语言猜，必须走 schema / registry。
4. 每个产物要有 provenance：数据、代码、参数、模型、时间、agent、成本。

## 6. PaperAgent 多代理架构

公开资料提到 CoPaper.AI PaperAgent 采用：

- Supervisor
- preparation 子代理
- modeling 子代理
- visualization 子代理
- writing 子代理

Skill 按 `target_agent` 路由，每个子代理只看到相关方法论指导，减少上下文干扰。

这和我们已有的 10 Agent 研究维度不同。我们的 10 Agent 更像“研究维度并行分析”，而 CoPaper 的 4 Agent 更像“生产流水线角色分工”。

后续重塑时建议合并二者：

- Pipeline Roles：准备、建模、可视化、写作、审阅、导出。
- Research Dimension Agents：文献、数据、变量、识别、稳健性、机制、异质性、图表、正文、审稿。
- Supervisor：负责计划、路由、权限、成本、验收、失败恢复。

也就是说，我们不应该只展示“10 个 Agent 同时跑”，而要展示“一个可控的研究生产线中，各类 Agent 在不同阶段接力”。

## 7. 对我们当前产品的重塑方向

### 7.1 当前我们已有的优势

我们项目已经具备一些 CoPaper 没有公开强调的优势：

- 本地优先，适合处理敏感数据。
- Codex 本地执行，能够和真实文件系统、代码、测试、Git 工作流连接。
- Agent Drawer 已经开始展示权限、能力注册、成本追踪、产物预览。
- 后端已有 workflow / artifact API 框架。
- 已经有 `StatsPAI`、显式 Python/R/Stata skills、论文产物目录结构等基础。

这些不应该推倒重来，而应该包装成更清晰的用户旅程。

### 7.2 UI 重塑的目标

我们要向 CoPaper 学习的不是视觉表皮，而是信息架构：

- 首页第一屏要告诉用户：你现在能从“研究问题 + 数据”走到“可复现论文草稿”。
- 导航不要只是技术模块，而要映射研究工作流。
- 每一步要让用户知道：系统正在做什么、为什么做、下一步需要你确认什么。
- 产物必须有“可打开、可追溯、可推送、可回滚”的闭环。
- Agent 不只是列表，而是承担明确角色、权限、成本和产出责任。

### 7.3 建议的一阶导航

建议从当前的：

- 总览
- 项目
- 工作流
- 智能体集群
- 产物
- 草稿

重塑为更研究导向的：

- 研究总览
- 数据与变量
- 研究设计
- 实证执行
- 论文草稿
- 产物与复现
- Agent 控制台

也可以保留现在的技术导航，但在视觉层加入“研究旅程条”：

`数据 -> 变量 -> 识别 -> 模型 -> 稳健性 -> 图表 -> 正文 -> 审阅 -> 导出`

### 7.4 核心页面重构建议

#### 研究总览

目标：像 CoPaper 一样给用户强确定性。

内容：

- 当前研究问题
- 数据准备度
- 识别策略状态
- 模型执行状态
- 论文完成度
- 关键风险
- 下一步建议

#### 数据与变量

对标 CoPaper 的 upload + cleaning 模块。

内容：

- 数据集列表
- sheet / schema / 变量类型识别
- 变量定义
- 缺失值、异常值、样本过滤
- codebook 预览
- 数据处理日志

#### 研究设计

对标 CoPaper 的 research direction + paper outline。

内容：

- 研究问题
- 因变量/自变量/控制变量
- 识别策略
- DAG / 假设链
- 模型候选
- 需要用户确认的关键选择

#### 实证执行

对标 CoPaper 的 modeling + robustness。

内容：

- baseline model
- robustness battery
- mechanism / heterogeneity
- model comparison
- assumption audit
- 失败恢复建议

#### 论文草稿

对标 CoPaper 的 chapter-by-chapter generation。

内容：

- 章节树
- 每章状态
- 引用状态
- 图表/表格插入状态
- AI 修改建议
- 人工确认记录

#### 产物与复现

对标 CoPaper 的 full code + DOCX export。

内容：

- data snapshot
- code bundle
- regression outputs
- figures
- tables
- manuscript markdown
- DOCX / LaTeX / HTML
- replication pack

#### Agent 控制台

这是我们的差异化。

内容：

- agent 身份
- 权限
- 能力注册
- 成本追踪
- 当前任务
- 产物归属
- 审计日志
- 可暂停/重试/替换 provider

## 8. 后端架构映射建议

参考 CoPaper API 面，我们后续可以把服务边界整理为：

1. `project_service`：研究项目、研究问题、生命周期。
2. `dataset_service`：上传、schema、sheet、快照、数据版本。
3. `cleaning_service`：变量定义、清洗方案、codebook、数据处理日志。
4. `design_service`：研究设计、变量选择、识别策略、DAG、模型候选。
5. `workflow_service`：任务编排、状态机、HITL gate、取消/重试。
6. `agent_registry_service`：身份、角色、权限、capabilities、provider、成本策略。
7. `execution_adapter`：local Codex、StatsPAI、Stata、R、Python notebook。
8. `artifact_service`：产物存储、preview、promote、provenance、replication pack。
9. `draft_service`：章节草稿、引用、图表插入、版本/undo。
10. `export_service`：DOCX、LaTeX、Markdown、HTML、submission bundle。
11. `observability_service`：错误、日志、成本、质量门禁。

我们现在已经有 workflow/artifact 的雏形，下一步不需要一次性全做，而是先把当前功能迁移到这些边界的命名和用户语义上。

## 9. 我们应该借鉴什么，不应该照搬什么

### 9.1 应该借鉴

- 清晰的“数据到论文”主线。
- 四步式用户路径。
- 每个关键节点 human-in-the-loop。
- 数据清洗、变量定义、模型选择、报告导出拆成明确服务。
- Skills 作为方法论层，而不是散落 prompt。
- 多代理角色分工，而不是单 agent 做所有事。
- 结构化结果对象，而不是纯文本。
- DOCX 和复现代码同时输出。

### 9.2 不应照搬

- 不要只做一个 SaaS landing。我们的重点是本地操作系统，不是营销页。
- 不要过度承诺“20 分钟完成论文”。我们应强调“可审计、可复现、可交接”。
- 不要让用户只能走黑箱流程。每一步都应可打开、可审查。
- 不要把 Agent 集群做成炫技动画。要让每个 Agent 的权限、成本和产物责任清楚。
- 不要让 Skills 变成无法审计的魔法库。每个 skill 要能被查看、版本化、禁用、fork。

## 10. 分阶段重塑计划

### Phase A：产品信息架构重塑

目标：先不大改后端，把界面从“模块页面”改成“研究旅程”。

交付：

- 研究总览页新布局。
- 旅程条：数据、变量、识别、模型、稳健性、图表、正文、导出。
- Agent Cluster 从列表升级为“Agent 控制台”。
- 每个产物都显示 provenance。

### Phase B：数据与研究设计闭环

目标：让用户能从数据和研究问题进入系统，而不是只看 mock workflow。

交付：

- dataset schema preview。
- variable definition panel。
- research design card。
- method recommendation placeholder。
- user confirmation gates。

### Phase C：local Codex + StatsPAI 执行接入

目标：把 demo 任务替换为真实执行 adapter。

交付：

- local Codex provider adapter。
- StatsPAI execution adapter。
- result object JSON。
- failure notes。
- code/log artifacts。

### Phase D：论文草稿与导出

目标：形成可用的论文生产线。

交付：

- section tree。
- markdown draft。
- table/figure insertion。
- DOCX export。
- replication pack。

### Phase E：多人多 Agent 治理

目标：形成我们的差异化。

交付：

- agent identity。
- role permission。
- capability registry。
- task ownership。
- cost ledger。
- artifact ownership。
- approval history。

## 11. 对 Kimi 和 Codex 的协作分工建议

Kimi 负责：

- 视觉风格向 CoPaper 级别靠近。
- 信息架构与页面布局。
- 用户旅程、卡片、动线、交互动效。
- 空状态、加载态、完成态、错误态。

Codex 负责：

- API 契约。
- 后端 service 边界。
- local Codex / StatsPAI adapter。
- workflow 状态机。
- artifact provenance。
- agent registry / permissions / cost ledger。
- BDD/TDD 测试和验收。

共同约束：

- 所有新功能先写 BDD 行为。
- 用户确认行为后再写测试。
- 测试先失败，再写最小实现。
- UI 不能绕过真实 API 契约。
- 后端不能返回纯文本替代结构化产物。

## 12. 下一步建议

建议下一步不是马上写代码，而是进入 BDD 行为对齐，先定义第一批重塑行为：

1. 用户打开研究总览时，能看到从数据到论文的研究旅程和当前阶段。
2. 用户点击任一阶段时，能看到该阶段的输入、输出、负责人 Agent、风险和下一步确认项。
3. 用户启动研究 workflow 后，系统会创建真实的 workflow/task/artifact records，而不是只更新前端 mock。
4. 每个 Agent drawer 必须展示身份、权限、能力、成本和产物归属。
5. 每个产物必须可以预览、推送到目标目录，并保留 provenance。
6. 任何模型/变量/识别策略关键决策都必须经过 HITL gate。

这批行为确认后，再进入 TDD。

