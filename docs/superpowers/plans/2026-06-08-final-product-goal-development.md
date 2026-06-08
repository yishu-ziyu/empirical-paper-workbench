# Final Product Goal Development Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development for independent research / implementation / verification lanes, or superpowers:executing-plans for inline execution. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把实证研究 OS 从“能跑若干节点”推进到一条可验收的最终产品主链路：用户输入题目后，系统生成可解释的 SupervisorPlan，派发 Agent Task Queue，选择合适 Skills 和统计后端，产出真实执行证据、研究报告、论文草案和导出预检。

**Architecture:** Goal 模式保存北极星目标；项目计划文件保存可执行分解；每个 P 节点必须在 20 分钟内产生可检查证据。UI 是用户的控制面和信任面，所有后台能力必须在前端以清晰、低噪声、可展开、可审计的方式呈现。

**Tech Stack:** Codex Goal tool, FastAPI backend, React/Vite frontend, local filesystem state under `state/product`, run artifacts under `workspace/runs`, tests under `tests`, plans under `docs/superpowers/plans`, optional StatsPAI / Python / StataMCP / Codex subagent backends.

---

## 1. Goal 模式怎么用

本轮已经创建一个 active Goal：

```text
推进实证研究 OS 最终形态产品开发：围绕“输入题目 -> SupervisorPlan -> Agent Task Queue -> skill 解释 -> 真实执行/草案/导出”的第一条完整主链路，建立北极星计划并持续落地到可验证产品能力。
```

Goal 模式在本项目里的用法：

- `Goal` 只记录北极星目标，不替代 BDD/TDD、计划文件、测试、浏览器验收和 commit。
- `Goal` 保持 active，直到这条主链路真实可用并且用户能从浏览器验收。
- 每个小节点仍按 P0/P1/P2 拆分；单个节点超过 20 分钟还没有证据，就拆小或换路。
- 只有目标真的完成，才把 Goal 标记为 complete。
- 只有同一阻塞连续多轮无法推进，才把 Goal 标记为 blocked。
- 不在 Goal 里塞具体实现细节；细节写在本文件、`Tasks/round-log.md`、测试和 commit 里。

## 2. 最终产品形态

最终形态是一个面向严肃实证研究的本地优先 Research OS，后续同一套状态模型接云端产品。

用户体验主线：

```text
输入题目
-> 研究任务书
-> SupervisorPlan
-> Agent Task Queue
-> Skill / 数据 / 方法 / 文献 / 执行后端选择
-> 真实运行和 evaluator 检查
-> 研究报告
-> exploratory 论文草案
-> Journal Skill 审稿门
-> PDF / DOCX / 复现包导出预检
-> 人工决定是否进入正式层
```

产品上必须同时满足两件事：

- 本地工作流高效：能读取本地数据、本地模型、本地日志、本地 Git 化论文状态。
- 云端产品可迁移：本地路径以后替换成云端 dataset id / object storage / cloud sandbox，但 `ResearchQuestion`、`SupervisorPlan`、`AgentTaskQueue`、`SkillRegistry`、`RunManifest`、`EvidenceGate`、`ReviewExport` 这些状态不重写。

## 3. UI 的位置

UI 是核心产品面。

后台能力负责严谨性，UI 负责让用户知道现在发生了什么、下一步该做什么、哪些内容能信、哪些内容要审。

UI 设计原则：

- 首屏只让用户输入或选择研究题目，不铺满所有功能。
- 进入工作台后，每个阶段只显示当前决策需要的 3-5 个信号。
- 细节默认折叠，用户点击后在右侧 Inspector 或抽屉展开。
- Agent 队列、Skill 选择、执行日志、风险、证据要求都要可见，但不能一上来冲到主屏。
- 所有按钮必须能读清；禁用态不能白字白底；背景对比度保持克制。
- UI 文案用研究者能理解的话，不写开发者自我解释。

## 4. 当前真实进展

已经具备的能力：

- Topic-first 入口已经存在。
- ResearchQuestion / TopicSession 已经持久化。
- SupervisorPlan 有人工审批状态机。
- approved SupervisorPlan 可以生成 Agent Task Queue。
- Agent Task Queue 默认仍需人工派工审阅。
- 真实数据候选池、导入预检、字段画像、变量候选审阅已经做过。
- OLS / Python adapter 有本地执行证据。
- Review & Export 已有 verifier gates。
- Auto Mode 草稿层和正式层边界已经多轮固化。
- 内部方法库、统计结果契约、Level 3 manuscript gate、formal writeback gates 有一批 CLI-first 资产。
- P0-F 已完成并提交 `4be3d7a`：intake 阶段的研究问题分析不再注入固定“机器人 / 工资 / DID / 工具变量”假设，LLM preview 必须绑定用户当前题目。
- P2-AB 已完成并提交 `00f055f`：Agent Task Queue 执行 API 必须先选择执行后端；未选后端时返回 `execution_backend_required`，不会把任务污染成真实执行失败。
- P0-D 已完成本节点实现：禁用按钮不再被基础按钮样式覆盖成白底白字，DottedSurface 背景粒子强度下调，当前浏览器验收截图已保存。

仍缺的关键能力：

- SupervisorPlan 和 Agent Task Queue 对 Skill Registry 的选择解释还没有形成用户可见主链路。
- LLM Supervisor 什么时候介入、产出什么、何时交还给确定性执行器，还需要写成状态机。
- Agent Task Queue 到执行后端选择层还需要接实：StatsPAI / Python / StataMCP / Codex subagent 的边界要清楚。
- 文献检索和 Journal Skill 审稿门还没有稳定进入主链路。
- 论文草稿能生成，但距离 CoPaper-like “可直接审阅的完整论文包”还要补长度、结构、引用校验、方法规范和多轮修订。
- 前端仍有体验问题：任务处理页还需要更强的下一步引导；按钮可读性和背景粒子强度已在 P0-D 先做止血。

今天已验证的测试：

- `python3 -m unittest tests.api.test_mode_dispatch_endpoints -v`
- `python3 -m unittest tests.test_demo_server_real_llm_contract tests.test_agent_task_queue tests.test_agent_task_dispatch_audit -v`
- `python3 -m unittest tests.test_agent_task_queue tests.test_agent_task_dispatch_audit -v`
- `python3 -m pytest tests/test_p2_aa_agent_task_execution_backend.py -q`
- `python3 -m unittest tests.test_workbench_visual_contrast_contract tests.test_brief_panel_self_critique_contract -v`
- `python3 -m py_compile Product/api/auto_research.py Product/api/supervisor.py Product/backend/agent_task_queue_service.py Product/app.py`
- `git diff --check -- Product/backend/agent_task_queue_service.py Product/app.py tests/test_agent_task_queue.py`
- `npm run build` in `Product/web-react`
- Browser opened `http://127.0.0.1:8771/react/react?v=20260608-p0d-ux-contrast`; observed `dottedOpacity=0.1`, disabled button background `rgba(230, 230, 230, 0.17)`, disabled text `rgb(208, 208, 208)`.
- Screenshot: `artifacts/ui-checks/p0d-ux-contrast-20260608.png`
- P0-B1 已完成本节点实现：Agent Task Queue 的任务详情现在会展开显示绑定的内部 Skill、为什么选它、预期产物、执行边界和 Skill 来源；后端的 SupervisorPlan / Queue / Registry 契约与前端可见契约已一起通过。
- P0-B2 已完成本节点实现：工作台首页现在会实际挂载 SupervisorPlan 审阅台和 Agent Task Queue，不再出现后端数据已返回但页面容器为空的情况。
- Browser opened `http://127.0.0.1:8782/legacy?v=20260608-p0b-skill-visible-2`; observed `.supervisor-plan-skill-review = 1`, `.agent-task-skill-binding = 1`, and the page text includes “推荐 Skill / 选择理由 / 缺失证据 / 为什么选这个 Skill / 预期产物 / 执行边界 / Skill 来源”.
- Screenshot: `artifacts/ui-checks/p0b-skill-visible-20260608.png`

## 5. LLM 介入编排

LLM 的职责是语义判断、计划生成、解释和草稿写作。确定性后端负责文件、统计、日志、证据、状态写入和门禁。

| 阶段 | LLM 介入 | 确定性后端 | 交还条件 |
|---|---|---|---|
| 输入题目 | 解析研究问题、候选数据线索、方法倾向 | 写 `ResearchQuestion` / `TopicSession` | 用户确认题目 |
| SupervisorPlan | 生成路线、风险、证据要求、子 Agent 分工 | 写待审 `supervisor_plan.json` | 用户 approve / revise / reject |
| Skill 选择 | 解释为什么选某个 Skill / 方法规范 | Skill Registry 返回来源、版本、适用条件 | 解释和来源写入 plan / queue |
| Agent Task Queue | 生成任务摘要、阻塞项、输入输出要求 | 写 `agent_task_queue.json`，默认不能执行 | 用户批准派工或要求修改 |
| 数据变量 | 候选变量映射、变量角色理由 | 数据画像、字段类型、缺失、样本量 | 变量候选进入草稿层 |
| 方法设计 | 方法可行性解释、识别风险说明 | Method workflow checklist / StatsPAI schema | RunPlan 草案进入人工审阅 |
| 执行实验 | 失败诊断、下一步修复建议 | StatsPAI / Python / StataMCP 运行、日志、结果文件 | evaluator checks 产出 |
| 写作 | 研究报告、论文草案、修订建议 | 引用校验、证据绑定、导出预检 | needs_human_review |

## 6. Agent Team 调用规则

每轮开发由 lead agent 负责集成，subagent 只做独立任务。

适合派 Agent Team 的节点：

- 外部开源 Skill 仓库调研和实践。
- StatsPAI / StataMCP / Python 后端能力对比。
- 前端 UX 问题截图检查和交互文案审阅。
- BDD 行为用例审阅。
- 测试覆盖和回归风险审计。

收回 Agent Team 的条件：

- 需要改同一组核心文件。
- 需要决定状态机字段命名。
- 需要 commit。
- 需要解释给用户验收。

Agent Team 输出必须被整合成一个产品决策或一个代码改动，不保留散乱报告。

## 7. P0：本轮 Goal 主链路落地

### Task P0-A: Goal plan ledger

**Files:**
- Create: `docs/superpowers/plans/2026-06-08-final-product-goal-development.md`

- [x] **Step 1: Read current project stage**

Read:

```bash
sed -n '1,120p' tasks/current-stage.md
sed -n '1,220p' docs/architecture-v2/north-star-cli-first-research-os-plan-2026-05-26.md
sed -n '1,220p' docs/architecture-v2/long-run-optimization-protocol.md
```

Expected: identify P2-AA, CLI-first north star, long-run round log protocol.

- [x] **Step 2: Create this plan**

Write this file and keep it scoped to Goal mode, final product shape, P0/P1/P2 split, UI role, LLM intervention and Agent Team rules.

- [x] **Step 3: Verify plan discoverability**

Run:

```bash
rg -n "Goal 模式|最终产品形态|LLM 介入|P0-B|UI 是核心产品面" docs/superpowers/plans/2026-06-08-final-product-goal-development.md
git diff --check -- docs/superpowers/plans/2026-06-08-final-product-goal-development.md
```

Expected: all key phrases found; diff check has no whitespace errors.

- [x] **Step 4: Commit the plan only**

Run:

```bash
git add docs/superpowers/plans/2026-06-08-final-product-goal-development.md
git commit -m "Define final product goal development plan"
```

Expected: only this plan file is committed.

### Task P0-B: Skill Registry explanation contract

Status: implemented for the P0-B visible explanation contract. Backend already carries the registry recommendation and LLM semantic judgment; this node added the missing frontend task-detail visibility and the missing Journey-page render hook so the user can inspect “为什么选这个 Skill” from the workbench.

**Files:**
- Inspect: `Product/backend/supervisor_plan_service.py`
- Inspect: `Product/backend/agent_task_queue_service.py`
- Inspect: `Product/backend/internal_skill_registry.py` or nearest existing registry module
- Test: `tests/test_supervisor_plan.py`
- Test: `tests/test_agent_task_queue.py`
- Test: `tests/test_internal_agent_skill_registry_contract.py`

Behavior cases:

```gherkin
Given a confirmed research question
And the internal skill registry contains empirical method skills
When the backend generates a SupervisorPlan
Then the plan includes selected_skill_ids, skill_sources, applicability_reason and missing_evidence.

Given an approved SupervisorPlan with selected skills
When the user creates an Agent Task Queue
Then each queue item carries the skill id, why_this_skill, expected_artifacts and execution_boundary.

Given the LLM Supervisor cannot justify a skill selection
When the plan is generated
Then the plan records needs_human_skill_review instead of silently selecting the skill.
```

Acceptance:

- Browser shows each task’s chosen Skill and “为什么选它”.
- Queue still does not execute until user approves dispatch.
- No canonical method rule is promoted automatically.

Verified:

```bash
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueFrontendTests.test_bdd_10_journey_view_renders_supervisor_plan_and_task_queue -v
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueFrontendTests -v
node --check Product/web/assets/app.js
python3 -m unittest tests.test_supervisor_plan tests.test_agent_task_queue tests.test_internal_agent_skill_registry_contract -v
git diff --check -- Product/web/assets/app.js Product/web/assets/styles.css tests/test_agent_task_queue.py tests/test_supervisor_plan.py docs/superpowers/plans/2026-06-08-final-product-goal-development.md
```

Manual acceptance:

- Browser opened `http://127.0.0.1:8782/legacy?v=20260608-p0b-skill-visible-2`.
- DOM check confirmed `supervisorSkillReviewCount=1`, `agentTaskSkillBindingCount=1`, `planBodyLength=935`, `queueBodyLength=3428`.
- Screenshot saved to `artifacts/ui-checks/p0b-skill-visible-20260608.png`.

### Task P0-C: Execution backend selection layer

Status: P0-C1 implemented for frontend-visible backend selection rationale. The queue already persisted selected backend metadata; this node exposes why the backend was selected, fallback backend choices, execution output boundary and formal-layer boundary in the task detail UI.

**Files:**
- Inspect: `Product/backend/agent_task_queue_service.py`
- Inspect: `Product/backend/orchestrator.py`
- Inspect: `Product/backend/run_service.py`
- Test: `tests/test_agent_task_queue_backend_selection.py`

Behavior cases:

```gherkin
Given a reviewed Agent Task Queue item
When the system selects an execution backend
Then it records one of StatsPAI, Python, StataMCP or CodexSubagent with selection reason and fallback.

Given the selected backend is unavailable
When the user tries to start execution
Then the system records blocked_by_backend_unavailable with visible retry or fallback choices.

Given a backend selection is only exploratory
When execution finishes
Then evidence_level remains local_execution or exploratory_execution and cannot enter formal layer automatically.
```

Acceptance:

- Frontend can show “本任务将由哪个后端执行”.
- Logs and output paths are visible before final manuscript writing.

Verified:

```bash
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueFrontendTests.test_bdd_11_frontend_exposes_backend_selection_reason_fallback_and_boundary -v
python3 -m unittest tests.test_agent_task_queue tests.test_supervisor_plan tests.test_internal_agent_skill_registry_contract -v
python3 -m pytest tests/test_p2_aa_agent_task_execution_backend.py -q
node --check Product/web/assets/app.js
```

Manual acceptance:

- Browser opened `http://127.0.0.1:8782/legacy?v=20260608-p0c-backend-visible`.
- DOM check confirmed `.agent-task-backend-details = 1`, with visible “为什么选这个后端 / 失败后备选 / 执行产物范围 / 正式层边界”.
- Browser cache needed a hard refresh before the latest `app.js` rendered; this is a dev-server cache issue, not product state.
- Screenshot saved to `artifacts/ui-checks/p0c-backend-visible-20260608.png`.

Compatibility note:

- Older queue state may contain `selected_backend.id` without `selection_reason`, `fallback_backend_ids` or `execution_boundary`. The next node should add a compatibility fallback or migration so old tasks still explain backend choice instead of showing empty detail text.

### Task P0-D: UX contrast and action clarity fix

Status: implemented for the readability and contrast part of the acceptance. The remaining “one clear next action” work should be handled as a separate UX guidance node, because it changes stage interaction logic rather than the visual contrast contract.

**Files:**
- Inspect: `Product/web-react/src/styles.css`
- Inspect: `Product/web-react/src/App.tsx`
- Inspect: relevant button/card components under `Product/web-react/src/`
- Test: existing frontend smoke test or browser manual acceptance

Behavior cases:

```gherkin
Given a primary or disabled button
When the page is displayed on the dark workbench background
Then the button label remains readable.

Given a user enters a task page
When the current stage needs a decision
Then the page shows one clear primary action and the reason for that action.

Given a section contains long details
When the page first loads
Then the details are collapsed and available through Inspector or local expansion.
```

Acceptance:

- No white text on near-white buttons.
- Background contrast is softened.
- Current task page tells the user what to do next.
- Browser screenshot saved under `artifacts/ui-checks/`.

## 8. P1：CoPaper-like 完整研究包

### Task P1-A: Literature and reference chain

Goal: make literature search, CNKI/Scholar/Zotero/manual import and candidate reference marking part of the main chain.

Acceptance:

- LiteratureAgent writes `Tasks/{slug}/literature.md`.
- Candidate references are marked as candidate / verified / rejected.
- Draft can cite candidate references only with visible review state.

### Task P1-B: Method gate enters main chain

Goal: Method Design reads canonical + proposal method rules, StatsPAI capability schema and selected journal profile.

Acceptance:

- AER-like profile can be recommended by default but activated by user.
- DID / IV / RDD / PSM / DML method doors show missing conditions and recommended diagnostics.
- Review & Export can block formal export based on activated journal rules.

### Task P1-C: Full exploratory PDF package

Goal: produce a full-length exploratory PDF package from real data and visible evidence.

Acceptance:

- Output includes `research_report.md`, `paper_draft_exploratory.md`, `paper.pdf`, `results.json`, `run_manifest.json`.
- Paper structure includes title, abstract, introduction, literature, data, method, results, robustness / limitations, conclusion, references.
- PDF is previewable from UI and local path is visible.

## 9. P2：产品化上线准备

### Task P2-A: Local/cloud runtime parity

Goal: same workflow state supports local and cloud runtime.

Acceptance:

- Local uses local path and local model/provider config.
- Cloud uses uploaded dataset id and cloud sandbox.
- UI shows runtime mode without splitting product logic.

### Task P2-B: Product onboarding and first-run loop

Goal: first-time user can start from topic input and reach a reviewed package without reading developer docs.

Acceptance:

- First screen asks for topic, data hint and optional method/journal standard.
- Empty/error/loading states are clear.
- Failed backend or missing data gives one actionable recovery path.

### Task P2-C: Quality review and final export

Goal: move from exploratory package to formal export through explicit review.

Acceptance:

- Human can approve, request revision, or reject each formal promotion.
- Formal layer has Git-like history.
- Export package includes paper, tables, figures, code, logs, manifest and README.

## 10. Completion definition for this Goal

This Goal is complete when all conditions below are true:

- User can enter a topic in the browser and see a topic-bound SupervisorPlan.
- SupervisorPlan explains selected Skills and missing evidence.
- Approved plan creates Agent Task Queue with skill, backend and audit metadata.
- At least one real execution backend runs from queue and writes logs/results/evaluator checks.
- UI shows progress, evidence, risk and next action without overwhelming the user.
- System generates an exploratory research report and PDF paper package.
- Review & Export blocks formal export until explicit human review.
- Relevant backend tests pass.
- Browser acceptance is completed and screenshot evidence is saved.
- A commit records the final verified slice.

## 11. Next node

Start with **P0-C2 Legacy backend metadata compatibility**.

Reason: P0-C1 已经让新任务显示“这个任务准备用哪个后端执行、为什么、不可用时怎么办”。浏览器验收发现旧的 `selected_backend` 状态可能缺少解释字段，所以要先补兼容层，避免用户打开旧任务时又看到空解释。

20-minute boundary for P0-C2:

- Add one contract: legacy `selected_backend.id` can still render a human-readable reason, fallback and boundary.
- Implement a frontend compatibility fallback or backend migration, choosing the smaller path after inspection.
- Verify with unit contract and browser DOM check.
- Do not change real backend execution semantics in this node.
