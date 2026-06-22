# 当前产品地图

本文档记录当前实证研究 OS 已经长出来的产品骨架。它不是愿景稿，而是给后续开发使用的落地地图：用户从哪里进入、每个页面负责什么、哪些内容可以直接展示、哪些内容必须进入审计或人工确认。

## 1. 产品主线

当前产品的主线是一个本地优先的实证研究工作台。用户先输入研究题目，系统生成研究简报，然后进入分阶段工作流：

1. 工作台首页：用户输入题目、数据线索、方法偏好或文献片段。首页只承担启动任务和展示当前项目摘要，不应该堆满所有功能。
2. 任务书：把题目拆成研究问题、边际文献、研究边界和成功标准。这个阶段的核心动作是确认边界，不直接跑回归。
3. 递归搜索：围绕题目进行文献、数据、变量和方法线索检索。当前自动链路以 arxiv 检索为主；Google Scholar、CNKI 和本地资料先作为人工辅助入口或后续扩展，不应被理解为已自动接通。
4. 数据与设计：读取本地数据资产，生成变量画像、VariableRoleSet、DesignSpec 和 RunPlan。这里是 Data Gate 与 Design Gate 的主界面。
5. 实证执行：按 RunPlan 调用 Python、StatsPAI、StataMCP 或本地脚本，产出 MethodExecutionResult、回归表、图和日志。这里必须显示 local_execution 证据。
6. 结果与草稿：从真实结果中提炼 Finding，生成研究报告和 exploratory 论文草稿。该阶段可以写作，但不能把草案直接当成正式论文。
7. 审阅与导出：运行 Verifier、文献校验、证据一致性校验、PDF/DOCX 预检和正式层写回审批。Export Gate 通过后才允许生成正式包。

## 2. 当前入口边界

当前仓库只有一个用户可见产品入口：

- React shell：`Product/web-react/src/main.tsx` 挂载 `Product/web-react/src/App.tsx`。这是唯一当前产品壳，包含论文生产状态、阶段状态机、topic intake、SupervisorPlan 审批和 Agent Task Queue。
- Product/web 已移除：旧静态工作台源码不再作为运行入口或验收入口保留。`/legacy` 只重定向到 `/`，历史解释留在 docs/Tasks 记录里。
- FastAPI server：`Product/app.py` 是主应用和 API 入口。`demo_server.py` 只是启动 `uvicorn Product.app:app` 的薄启动器。

React 当前的主要阶段组件包括 `BriefPanel`、`SearchPanel`、`VariablesPanel`、`DesignPanel`、`ExecutionPanel`、`IdentificationAuditPanel`、`SupervisorPlanReview`、`AgentTaskQueuePanel` 和 `SystemStatusBar`。如果页面看起来“不知道下一步做什么”，优先检查 `App.tsx` 的阶段状态机和当前阶段的 Next Action，而不是在单个卡片上继续堆文案。

## 3. 页面职责

### 工作台首页

工作台首页负责降低用户认知负担。它应该只显示研究题目输入器、模式选择、最近项目和最必要的 Next Action。这里不展示完整 Agent Task Queue，不展示长日志，不展示方法树。首页的判断标准是：用户进来后知道“现在该输入题目或继续哪个项目”。

### 数据与设计

数据与设计页面承担从数据资产到可执行设计的桥接。它应该展示数据源、变量画像、VariableRoleSet、DesignSpec、RunPlan 和相关 gate 状态。任何 mock 或启发式变量推荐都必须显式标注。证据等级至少区分 mock、local_file、local_execution。mock 只能用于体验演示；local_file 表示来自本地文件或配置；local_execution 表示本机真实运行产生的证据。

### 实证执行

实证执行页面围绕 run 展开。用户需要看到 run id、方法、参数、脚本、日志、表格、图、失败原因、成本和产物。这里的 Next Action 通常是“查看失败诊断”“批准进入结果解释”“重新执行指定 run”。这个页面不是论文写作页，不应该把执行日志和论文正文混在一起。

### 结果与草稿

结果与草稿页面负责把 MethodExecutionResult 变成可审阅的 Finding，再进入研究报告和草稿。每个 Finding 必须绑定 evidence_id、结果文件和证据等级。没有真实表格的 Finding 只能停留在 draft 或 needs_human_review，不能进入 formal writeback。

### 审阅与导出

审阅与导出是最终质量门。它要呈现 Verifier 的检查结果：占位符、样本量一致性、系数一致性、变量定义、识别策略、引用真实存在性、PDF/DOCX 导出预检、复现包 manifest。这个页面的用户动作是批准、驳回、要求修订或导出。

## 4. Agent 面板与任务队列

Agent Task Queue 是产品的执行中枢可视化层。它不应该替代主流程页面，而应该解释“谁正在做什么、为什么做、用哪个 skill、产出在哪里、是否需要人工确认”。建议角色包括：

- Supervisor：生成研究路线、派发任务、合并审阅意见。
- DataAgent：读取数据、画像变量、提出 VariableRoleSet。
- DesignAgent：生成 DesignSpec、识别策略和方法门槛。
- ExecutionAgent：执行 RunPlan，生成 MethodExecutionResult。
- LiteratureAgent：检索文献、校验引用、维护文献证据。
- ManuscriptAgent：生成研究报告和草稿层文本。
- Verifier：检查证据一致性、占位符、引用、样本量和正式层写回条件。

Agent 面板应该默认折叠技术细节，只展示状态、Next Action 和阻塞原因。点击任务后再展开日志、工具调用、能力包和审计记录。

## 5. 证据等级和正式层边界

当前产品必须持续区分三个层次：

- 草案层：LLM、Agent 和启发式规则可以自动生成、修改、重写。
- 审阅层：用户或 Verifier 检查证据、变量、方法、引用和一致性。
- 正式层：只有通过 gate 后才允许写回论文正式稿、导出包或提交材料。

证据等级的最小集合：

- mock：演示数据或硬编码样例，不可进入正式论文。
- local_file：本地文件、数据字典、配置、用户上传材料。
- local_execution：本机真实执行产生的表格、图、日志、结果。
- external_source：外部论文、网页、数据库、CNKI、Crossref、Scholar 等来源。
- reviewed：已被用户或 Verifier 明确确认的证据。

后续功能若无法说明证据等级，就不应进入正式层。

## 6. 已知漂移点

当前最容易出错的地方有三类：

- 前端可能连到错误端口或静态服务。必须通过 `SystemStatusBar`、`/api/system/status`、`/api/v1/providers/llm-supervisor` 或 `/api/v1/health` 确认真实后端。
- `/api/*` 是阶段面板使用的轻量 wrapper flow，`/api/v1/projects/*` 是产品状态层接口。两者可以共存，但不能把 wrapper 的临时产物误认为 canonical state。
- `Product/state/*` 与仓库根目录 `state/*` 同时存在。项目/工作流 registry 主要在 `Product/state`，产品核心状态和 run 观测主要在 `state/product` 与 `state/runs`。

## 7. 当前开发落点

当前开发落点不是继续堆 P 阶段，而是把 CGSS 论文生产链做成可验收产品路径：浏览器内生成审阅报告、展示用户可读修订清单、把下一步动作回写到 headless state。后续每个节点都要能回答：

- 它属于哪个页面？
- 它读写哪个状态对象？
- 它由哪个 Agent 或 skill 负责？
- 它的 Next Action 是什么？
- 它能否进入正式层？
- 它的证据等级是 mock、local_file 还是 local_execution？
