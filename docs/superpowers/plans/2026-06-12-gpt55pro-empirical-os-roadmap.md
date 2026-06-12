# GPT-5.5 Pro Empirical OS Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development for research / implementation / verification lanes, or superpowers:executing-plans for single-lane execution. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 吸收 GPT-5.5 Pro 指南，把当前项目从“已有 Product Shell + 若干执行节点”推进为本地优先、证据可追溯、可扩展到云端的 Empirical Research OS。第一条主链路必须能从研究题目进入数据、变量、设计、执行、Finding、草稿、Verifier 和导出预检。

**Architecture:** 保留现有 AER 风格项目模板和 Product Shell。以 `paper.yaml`、`state/product/*.json`、`state/runs/*`、`Results/*`、`Manuscripts/*`、`Submissions/*` 作为可审计状态和证据层。LLM Supervisor 负责语义判断和计划生成，确定性后端负责统计执行、状态写入、门禁和导出。

**Tech Stack:** FastAPI backend, React/Vite Product Shell, local JSON state, Python execution, StatsPAI adapters, optional StataMCP / stata-code adapters, Pandoc / LaTeX export, Git-backed formal layer, BDD/TDD under `tests/`, browser verification under local Product Shell.

---

## 1. 指南带来的路线修正

这份指南确认当前仓库已经有正确骨架，接下来要强化它，而不是另起一个 CoPaper 克隆。

当前仓库已经具备的骨架：

- AER 风格目录：`Data/`、`Program/`、`Results/`、`Manuscripts/`、`Submissions/`、`Tasks/`。
- 项目配置和执行入口：`paper.yaml`、`Program/run_paper.py`、`Program/export_docx.py`。
- Product Shell：工作台首页、数据与设计、实证执行、结果与草稿、审阅与导出。
- Agent OS 资产：SupervisorPlan、Agent Task Queue、Capability Registry、Verifier、Trace Learning、internal skills。
- 真实执行资产：本地 Python / StatsPAI 路径、run manifest、run events、method execution result、export preflight。

新的开发判断：

1. 主线是把 `VariableRoleSet -> DesignSpec -> RunPlan -> MethodExecutionResult -> Finding -> Draft -> Verifier -> ExportPackage` 做成可重复、可审计、可验收的链路。
2. `sp.paper(...)` 适合做草稿生成能力，不能承担主执行层；主执行层必须由明确的变量、设计、运行计划和执行结果驱动。
3. UI 是信任界面：用户必须看见下一步、证据状态、Agent 任务、门禁、风险和可导出状态。
4. 外部 skills 和 AERS/StatsPAI 能力要进入 Capability Registry，并保留 attribution、license、风险和是否可执行的边界。
5. 当前最重要的不是增加 Agent 名字，而是让每个 Agent 产物能落盘、能追溯、能被人工确认。

## 2. 北极星用户路径

```text
输入研究题目
-> 生成 ResearchQuestion / TopicSession
-> LLM Supervisor 生成 SupervisorPlan
-> 用户确认研究边界和任务书
-> Capability Registry 推荐 skills / 方法 / 后端
-> Agent Task Queue 生成可审阅任务
-> 数据预检与字段画像
-> VariableRoleSet 候选与人工批准
-> DesignSpec 候选与人工批准
-> MethodWorkflow readiness
-> RunPlan 候选与人工批准
-> 真实统计后端执行
-> MethodExecutionResult / run events / artifacts
-> Finding Review
-> Manuscript Candidate
-> Verifier Checks
-> DOCX / PDF / Replication Package 预检
-> 人工决定是否进入正式层
```

每一步必须回答四个问题：

1. 当前用户需要判断什么？
2. 当前证据来自哪个文件、run 或外部来源？
3. 当前状态能否进入下一步？
4. 如果不能，缺什么证据或确认？

## 3. Canonical 对象模型

| 对象 | 当前承载位置 | 必须补齐的契约 | 进入正式层条件 |
|---|---|---|---|
| `Project` | `paper.yaml`, `state/product/project*.json` | 项目元信息、当前阶段、可见数据源、最后一次 run | 项目注册成功且可重启恢复 |
| `ResearchQuestion` | `Tasks/*/brief.md`, topic state | 题目、边界、样本、数据线索、方法倾向 | 用户确认任务书 |
| `DatasetImport` | `Data/*`, preflight JSON | 文件路径、格式、schema、行列数、读取状态 | 预检通过 |
| `FieldProfile` | state/product or run artifacts | 字段类型、缺失、唯一值、分布、样本口径 | 数据画像完成 |
| `VariableRoleSet` | `state/product/variable_roles*.json` | outcome/treatment/control/instrument/time/unit | 人工批准 |
| `DesignSpec` | `state/product/design_spec*.json` | estimand、方程、识别假设、威胁清单 | 人工批准 |
| `MethodWorkflow` | method workflow state | 方法适用条件、blocked reason、所需产物 | readiness 通过 |
| `RunPlan` | `state/product/run_plan*.json` | 后端、公式、样本、预期表图、失败策略 | 人工批准 |
| `Run` | `state/runs/{run_id}` | run manifest、steps、events、cost、backend | 真执行完成或明确失败 |
| `MethodExecutionResult` | `Results/json/*` | 系数、标准误、p 值、样本量、公式、artifact path | 绑定 run_id |
| `Finding` | finding review state | 论断、证据、识别边界、是否可写入正文 | 用户 approve |
| `DraftSection` | `Manuscripts/*` | section、来源、数字绑定、引用绑定 | verifier 通过 |
| `ExportPackage` | `Submissions/*` | manifest、docx/pdf、replication README、logs | export gate 通过 |
| `VerifierCheck` | `state/product/verifier_checks.json` | check id、status、evidence、blocking reason | 所有 blocking check 通过 |
| `AgentTask` | `state/product/agent_task_queue.json` | task id、agent、skill、输入输出、权限、状态 | 用户批准派工 |
| `Capability` | `state/product/capabilities.json`, `Product/internal_skills` | 来源、license、阶段、风险、adapter 状态 | reindex 落盘 |

## 4. Agent Team 编排

Lead agent 负责整合、写代码、提交和最终说明。Worker agents 只处理独立 lane。

| Agent | 何时调用 | 产物 | 何时收回 |
|---|---|---|---|
| `SupervisorAgent` | 题目进入系统、计划生成、路线修订 | SupervisorPlan、风险、证据要求、任务拆分 | 进入人工确认 |
| `DataAgent` | 数据预检、字段画像、变量候选 | DatasetImport、FieldProfile、VariableRoleSet candidate | 变量角色进入人工批准 |
| `MethodAgent` | DesignSpec、方法 readiness、AERS/StatsPAI skill 选择 | DesignSpec candidate、MethodWorkflow、blocked reason | RunPlan 审阅前 |
| `ExecutionAgent` | RunPlan 批准后 | run manifest、run events、method execution result | 结果落盘后 |
| `EvidenceVerifier` | Finding、Draft、Export 前 | verifier checks、evidence gap、blocking reason | gate 明确通过或阻断 |
| `ManuscriptAgent` | approved Finding 后 | DraftSection、Manuscript Candidate | 正式写回前 |
| `ReproAgent` | 导出前 | replication manifest、README、环境说明 | export preflight 完成 |
| `ProductUXAgent` | 用户反馈 UI 看不懂、按钮不可读、流程断裂 | UX critique、可验收交互建议 | 需要改核心状态机时 |

Agent 调用规则：

- 20 分钟内没有可检查产物，就拆小任务或换路径。
- Agent 产物默认进入 proposal layer。
- Canonical 文件必须由人工确认或明确 gate 通过后写入。
- 外部联网、数据修改、执行后端切换必须在 UI 或日志中可见。
- Worker 输出必须合并成一个代码改动、一个测试、一个文档或一个产品决策。

## 5. LLM 介入边界

LLM 是产品核心，但它不能替代证据层。

| 阶段 | LLM 做什么 | 后端做什么 | 交还点 |
|---|---|---|---|
| 题目输入 | 解析研究问题、生成候选边界 | 写 TopicSession | 用户确认任务书 |
| SupervisorPlan | 生成路线、风险、证据要求、子 Agent 分工 | 持久化 pending plan | approve / revise / reject |
| Skill 选择 | 解释为什么选择 AERS/StatsPAI/internal skill | Registry 返回来源、license、adapter 状态 | 写入 plan / queue |
| 数据变量 | 生成变量角色候选理由 | 字段画像、缺失、样本量、类型检查 | VariableRoleSet 审阅 |
| 方法设计 | 说明识别策略和威胁 | MethodWorkflow readiness | DesignSpec / RunPlan 审阅 |
| 执行失败 | 解释错误、提出修复建议 | 真实执行、日志、错误分类 | rerun / revise plan |
| 写作 | 生成研究报告和草稿段落 | evidence binding、引用校验、verifier | draft review |

强制边界：

- LLM 不能把 mock 标成 local_execution。
- LLM 不能未执行就写统计结果。
- LLM 不能静默改正式状态。
- LLM 不能静默联网。
- LLM 不能静默修改数据。
- LLM 生成的 methodology patch proposal 必须人工 review 后才能进入 canonical 规则库。

## 6. 质量门禁

### 6.1 Data Gate

通过条件：

- 数据文件存在且可读取。
- 字段画像完成。
- outcome、treatment、controls、instrument/time/unit 等角色有候选。
- 样本口径和缺失处理方式写入状态。
- 用户批准 VariableRoleSet。

阻断条件：

- 数据仍不可读。
- 字段画像缺失。
- 样本量、单位或时间范围无法说明。
- 用户未批准变量角色。

### 6.2 Design Gate

通过条件：

- DesignSpec 包含 estimand、估计方程、识别假设、威胁清单。
- 方法前置条件通过 readiness。
- 对 observational design 明确写入解释边界。
- 用户批准 DesignSpec。

阻断条件：

- 方程缺 outcome/treatment。
- DID/IV/RDD/PSM/DML 所需关键字段缺失。
- 识别假设为空。
- blocked method 仍被放进 RunPlan。

### 6.3 Execution Gate

通过条件：

- RunPlan 已批准。
- 后端明确选择。
- 数据路径和公式可用。
- 执行日志、run steps、run events、artifacts 全部写入。
- 成功状态来自真实执行。

阻断条件：

- 未选择后端。
- 运行失败但状态写成 succeeded。
- 产物缺失却进入 Finding。

### 6.4 Result Gate

通过条件：

- Finding 绑定 run_id、artifact_path、evidence_level。
- 系数、标准误、p 值、样本量、公式存在。
- 用户 approve Finding。
- 解释文本包含识别边界。

阻断条件：

- evidence_id 找不到文件。
- 同一数字跨章节不一致。
- 未批准 Finding 被写入正文。

### 6.5 Manuscript Gate

通过条件：

- 草稿 section 绑定来源。
- 数字、表格、图形、引用可追溯。
- 数据段消费 Data Contract / Codebook。
- 方法段消费 DesignSpec。
- 结果段只消费 approved Finding。

阻断条件：

- 出现 `{placeholder}`。
- 引用不存在。
- 表格不存在。
- exploratory result 被写成正式因果结论。

### 6.6 Export Gate

通过条件：

- verifier checks 全部通过。
- result binding 通过。
- run plan、method execution、draft preview 存在。
- DOCX/PDF preflight 通过。
- export manifest 写入来源文件和命令。

阻断条件：

- mock evidence 进入正式包。
- method execution artifact 缺失。
- docx/pdf 预检失败。

## 7. P0-P6 开发路线

### P0: 稳定 Product Shell 和当前状态地图

目标：让现有页面、API 和 JSON 状态关系清晰可查。

- [ ] Step P0-A: 生成当前产品地图。
  - Files: create `docs/current-product-map.md`, `docs/api-map.md`, `docs/state-schema.md`.
  - Verify: `rg -n "Product Shell|state/product|local_execution|mock|endpoint" docs/current-product-map.md docs/api-map.md docs/state-schema.md`.
- [ ] Step P0-B: 标记所有 mock / local_file / local_execution 展示。
  - Files: `Product/web*`, `Product/backend/*`, relevant state serializers.
  - BDD: UI 必须显示 evidence level；mock 不得伪装成真执行。
  - Verify: run focused UI contract tests and browser smoke.
- [ ] Step P0-C: 修复启动和服务未连接体验。
  - Files: `Product/app.py`, frontend API client, server boot docs.
  - Verify: backend stopped 时显示可行动提示；backend running 时恢复流程。

验收：

- `python3 Product/serve_product.py` 可启动。
- 打开 Product Shell 后能看见项目当前阶段、下一步、证据状态。
- 服务断开时提示用户怎么恢复，不丢已保存材料。

### P1: Data -> VariableRoleSet -> DesignSpec

目标：把真实数据进入研究设计前半段做稳。

- [ ] Step P1-A: 数据候选池和导入预检。
  - Files: `Product/backend/dataset*`, `state/product/dataset_import_preflights.json`, `tests/test_dataset_import_preflight*.py`.
  - BDD: Given 用户选择 CSV/Stata 文件, When 运行预检, Then 系统写入可读性、schema、行列数和风险。
  - Verify: `python3 -m unittest tests.test_dataset_import_preflight -v`.
- [ ] Step P1-B: 字段画像和变量角色候选。
  - Files: `Product/backend/variable_role*`, `state/product/field_profiles.json`, `state/product/variable_role_candidates.json`.
  - BDD: Given 字段画像完成, When LLM/DataAgent 生成变量角色候选, Then 每个候选包含理由、字段证据和缺失风险。
  - Verify: focused unit tests plus one real dataset CLI smoke.
- [ ] Step P1-C: VariableRoleSet 审阅和批准。
  - Files: `state/product/variable_roles.json`, frontend review component.
  - BDD: 未批准变量角色不能生成正式 DesignSpec。
  - Verify: API tests and browser flow.
- [ ] Step P1-D: DesignSpec 生成、审阅、批准。
  - Files: `Product/backend/design_spec*`, `state/product/design_spec.json`.
  - BDD: DesignSpec 必须包含 estimand、方程、识别假设、威胁清单。
  - Verify: `python3 -m unittest tests.test_design_spec_state_machine -v`.

验收：

- 用户能从真实数据生成可审阅 VariableRoleSet。
- 用户能从 approved VariableRoleSet 进入 approved DesignSpec。
- 缺关键字段时 MethodWorkflow 显示 blocked。

### P2: MethodWorkflow -> RunPlan -> Execution

目标：把实证执行做成真实可审计链路。

- [ ] Step P2-A: MethodWorkflow readiness。
  - Files: `Product/backend/method_workflow*`, `Program/methodology/*`, `Product/internal_skills/*`.
  - BDD: DID/IV/RDD/PSM/DML 缺前置条件时必须 blocked，并给出缺失证据。
  - Verify: method readiness tests.
- [ ] Step P2-B: RunPlan 候选和批准。
  - Files: `state/product/run_plan.json`, `Product/backend/run_plan*`.
  - BDD: RunPlan 必须绑定 DesignSpec、后端、公式、样本和预期产物。
  - Verify: run plan state-machine tests.
- [ ] Step P2-C: OLS full run 真实执行。
  - Files: `Program/run_paper.py`, `Product/backend/execution*`, `Results/json/method_execution_result.json`.
  - BDD: 成功 run 写 local_execution；失败 run 写 error，不生成成功 Finding。
  - Verify: one real dataset smoke and API test.
- [ ] Step P2-D: StatsPAI adapter validation。
  - Files: `Product/backend/statspai*`, `Product/internal_skills/StatsPAI*`.
  - BDD: StatsPAI 可用时返回 structured validation；不可用时 blocked 而不是静默跳过。
  - Verify: adapter contract tests.

验收：

- Full run 成功后有 run manifest、run events、method execution result。
- OLS 结果含系数、标准误、p 值、置信区间和样本量。
- 执行失败可读、可重跑、可进入修复建议。

### P3: Finding Review -> Draft Binding

目标：结果写进草稿前必须被审阅、批准和绑定证据。

- [ ] Step P3-A: 从 execution result 生成 Finding。
  - Files: `Product/backend/finding*`, `state/product/finding_reviews.json`.
  - BDD: Finding 必须绑定 run_id、artifact_path、evidence_level。
  - Verify: `python3 -m unittest tests.test_finding_review* -v`.
- [ ] Step P3-B: Finding 审阅状态机。
  - Files: backend review API and frontend review panel.
  - BDD: reject / needs_revision / approve 都持久化。
  - Verify: API tests and browser flow.
- [ ] Step P3-C: DraftSection evidence binding。
  - Files: `Manuscripts/generated/*`, `state/product/manuscript_candidates.json`.
  - BDD: 未批准 Finding 不能写入结果段。
  - Verify: manuscript evidence integrity tests.

验收：

- 草稿每个关键数字能追到结果文件。
- 拒绝 Finding 后草稿候选更新。
- 数据段、方法段、结果段分别消费对应 evidence。

### P4: Verifier -> ExportPackage

目标：形成可审阅、可复现、可导出的材料包。

- [ ] Step P4-A: Verifier hard gates。
  - Files: `Product/backend/verifier*`, `tests/test_paper_evidence_integrity_gate.py`.
  - BDD: placeholder、缺表格、缺 evidence_id、数字冲突必须 blocking。
  - Verify: verifier tests.
- [ ] Step P4-B: DOCX / PDF export preflight。
  - Files: `Program/export_docx.py`, export service, `Submissions/export_manifest.json`.
  - BDD: 缺 run plan 或 method execution 时导出按钮禁用。
  - Verify: export preflight tests and manual open file.
- [ ] Step P4-C: Replication package。
  - Files: `Submissions/replication_package.zip`, README generator, manifest.
  - BDD: 包含数据说明、代码、结果、草稿、运行日志和环境说明。
  - Verify: manifest path checks.

验收：

- verifier 失败时不能导出正式 docx/pdf。
- export manifest 记录来源文件和命令。
- 导出包可以被用户打开检查。

### P5: Capability Registry + AERS/StatsPAI 深度吸收

目标：把外部优质 skills 变成产品能力目录、方法门禁和任务队列建议。

- [ ] Step P5-A: Capability reindex。
  - Files: `Product/backend/internal_skill_registry.py`, `state/product/capabilities.json`.
  - BDD: AERS、StatsPAI、internal skills 都写入来源、license、阶段、风险、adapter 状态。
  - Verify: registry contract tests.
- [ ] Step P5-B: Skill selection explanation。
  - Files: `Product/backend/supervisor_plan_service.py`, `Product/backend/agent_task_queue_service.py`.
  - BDD: SupervisorPlan 和 AgentTask 必须解释为什么选这个 skill、缺什么证据、是否 executable。
  - Verify: queue tests and browser inspect.
- [ ] Step P5-C: AERS quality gates 映射。
  - Files: `Program/methodology/aers_*`, verifier mapping service.
  - BDD: 外部 skill 先进入 proposal layer；人工 review 后才能成为 canonical rule。
  - Verify: proposal/canonical gate tests.

验收：

- 用户能看到每个 skill 的来源、用途、风险和执行边界。
- 没有 local adapter 的 skill 不能标记 executable。
- AERS 不只作为资料链接，而是进入 MethodWorkflow / Verifier / AgentTask。

### P6: CoPaper-like Local Research OS MVP

目标：从一句研究题目到可审阅研究包，形成完整本地 MVP。

- [ ] Step P6-A: 题目到本地数据匹配。
  - Files: auto-research service, dataset registry.
  - Verify: 给定 CGSS / CFPS / 上市公司题目能推荐候选数据，并说明匹配理由。
- [ ] Step P6-B: 自动生成研究报告和 exploratory 论文草稿。
  - Files: manuscript service and research report templates.
  - Verify: 草稿长度、结构、引用、数据段、方法段、结果段通过 verifier preview。
- [ ] Step P6-C: Journal Skill 审稿门。
  - Files: journal skill registry, AER-like gate, reviewer critique service.
  - Verify: 用户选择 AER-like 时启用更高门槛，默认建议开启。
- [ ] Step P6-D: 一次完整浏览器验收。
  - Files: Playwright/browser verification notes.
  - Verify: 用户从前端跑完题目输入、计划确认、队列生成、数据/设计/执行/草稿/导出预检。

验收：

- 30-40 分钟内能从一个合适题目得到可审阅研究包。
- 每个正文数字有 evidence binding。
- 每个关键状态有人工确认记录。
- 每个执行结果有日志。
- 每个导出包有 verifier 记录。

## 8. 14 天实施节奏

| 日期 | 目标 | 交付物 | 验收 |
|---|---|---|---|
| Day 1-2 | 当前状态地图 | `docs/current-product-map.md`, `docs/api-map.md`, `docs/state-schema.md` | 页面/API/JSON 对应关系清楚 |
| Day 3-5 | VariableRoleSet | dataset preflight, field profile, variable role review | 真实数据进入 approved VariableRoleSet |
| Day 6-8 | DesignSpec / RunPlan | design spec, method readiness, run plan | blocked 方法不能执行 |
| Day 9-11 | OLS full run | method execution result, run events, StatsPAI validation | local_execution 真实可追溯 |
| Day 12-14 | Finding / Draft / Verifier | finding review, manuscript candidate, export preflight | 未通过 verifier 不能导出 |

## 9. UI/UX 主线

UI 不再按技术对象堆叠，而按用户当前决策组织。

五个主页面继续保留：

1. 工作台首页：Next Action、Workflow Spine、Evidence Status、Open Gates、Latest Run、Agent Queue。
2. 数据与设计：数据候选池、导入预检、字段画像、变量角色、DesignSpec。
3. 实证执行：RunPlan、MethodWorkflow、后端选择、Run Monitor、Events、Artifacts。
4. 结果与草稿：Findings、Finding Review、Draft Sections、Evidence Binding、Manuscript Candidate。
5. 审阅与导出：Verifier Checks、DOCX/PDF Preflight、Replication Checklist、Export Manifest。

新增工具页按需开放：

- 文献与引用。
- 方法目录。
- 复现包详情。
- 项目历史。
- Agent 控制台。
- 治理面板。

交互原则：

- 首屏只处理题目和下一步。
- 每个阶段主屏显示 3-5 个决策信号。
- 细节放右侧 Inspector 或抽屉。
- 禁用按钮必须清楚说明原因。
- Agent 队列默认折叠，但当前阻塞任务可见。
- 用户反馈“看不懂在干嘛”时，优先补 Next Action 和解释层，而不是继续加卡片。

## 10. 技术分层

后端服务拆分方向：

- `project_service`
- `dataset_service`
- `variable_role_service`
- `design_spec_service`
- `method_workflow_service`
- `run_plan_service`
- `execution_service`
- `artifact_service`
- `finding_service`
- `manuscript_candidate_service`
- `verifier_service`
- `agent_task_queue_service`
- `capability_registry`
- `permission_service`
- `cost_service`
- `provenance_service`

存储策略：

- P0 继续以 JSON 文件为透明 source of truth。
- P1 增加 SQLite 索引，用于 project/run/artifact/finding/agent/capability/cost 查询。
- 文件产物继续作为 canonical evidence。

执行后端顺序：

1. Python OLS adapter。
2. StatsPAI OLS validation。
3. StatsPAI formal adapter for OLS / IV / DID / RDD / PSM / DML。
4. StataMCP / stata-code adapter。
5. R / Quarto adapter。
6. container execution。

## 11. 成功指标

产品指标：

- 用户 5 分钟内创建或恢复项目。
- 用户 10 分钟内完成数据导入和变量角色确认。
- 用户 20 分钟内完成 DesignSpec 和 RunPlan。
- 用户 30 分钟内完成一次 OLS full run。
- 用户 40 分钟内看到可审阅草稿和导出预检。

质量指标：

- 100% 正文数字有 evidence binding。
- 100% exported package 有 export manifest。
- 100% full run 有 run manifest。
- 100% local_execution 来自真实执行。
- 0 个 mock result 进入正式导出。
- 0 个未批准 Finding 写入正文。

方法指标：

- OLS 支持 progressive controls。
- IV 支持 first-stage 和 weak instrument warning。
- DID 支持 event-study 和 pretrend。
- RDD 支持 density test 和 rdplot。
- PSM 支持 overlap 和 balance。
- DML 支持 cross-fitting 和 nuisance diagnostics。

写作指标：

- 草稿区分 causal / associational / exploratory。
- 方法段包含估计方程。
- 结果段包含样本量和标准误说明。
- 稳健性段落绑定表格。
- 导出包包含复现说明。

## 12. 立即执行顺序

下一轮开发从 P0-A 开始，不继续扩散 UI 或方法族。

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile Product/app.py Product/backend/*.py Program/run_paper.py Program/export_docx.py
```

然后按以下顺序推进：

1. 当前产品地图：页面、API、JSON、evidence level。
2. Data -> VariableRoleSet -> DesignSpec 的真实状态闭环。
3. MethodWorkflow -> RunPlan -> OLS Full Run 的真实执行闭环。
4. Finding -> Draft -> Verifier 的证据约束闭环。
5. Capability Registry 把 AERS/StatsPAI/internal skills 接入主链路。
6. CoPaper-like 本地 MVP 浏览器验收。

每个节点完成后必须写清：

- 改了什么文件。
- 哪个行为被覆盖。
- 哪个测试证明它生效。
- 浏览器或 CLI 怎么验收。
- 哪些内容仍不能进入正式层。
