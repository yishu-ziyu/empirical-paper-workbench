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
- P0-D 已完成本节点实现：React 工作台禁用按钮不再显示成高亮白块，深色背景和 DottedSurface 粒子强度已整体降噪，当前浏览器验收截图已保存。

仍缺的关键能力：

- SupervisorPlan 和 Agent Task Queue 对 Skill Registry 的选择解释还没有形成用户可见主链路。
- LLM Supervisor 什么时候介入、产出什么、何时交还给确定性执行器，已经在 P1-A 写入队列契约；下一步还要把它驱动到真实 LLM 调用和前端审计视图。
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
- P0-D visual contract:
  - `python3 -m unittest tests.test_react_workbench_visual_contract -v`
  - `python3 -m unittest tests.test_react_workbench_visual_contract tests.test_agent_task_queue -v`
  - `npm run build` in `Product/web-react`
- Browser opened `http://127.0.0.1:8771/react/react?v=20260608-p0d-contrast`; observed `--color-bg=#242424`, `--color-panel=#2b2b2b`, `--color-ink=#c8c8c8`, `dottedOpacity=0.06`, disabled button background `rgba(230, 230, 230, 0.075)`, disabled text `rgb(143, 143, 143)`, disabled opacity `1`.
- Screenshot: `artifacts/ui-checks/p0d-react-contrast-20260608.png`
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

- P0-C2 completed this compatibility fallback. Older queue state with only `selected_backend.id` now gets a human-readable default reason, default fallback backends and a conservative formal-layer boundary.

P0-C2 verified:

```bash
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueFrontendTests.test_bdd_12_legacy_backend_selection_still_has_human_explanation -v
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueFrontendTests -v
node --check Product/web/assets/app.js
git diff --check -- Product/web/assets/app.js tests/test_agent_task_queue.py
```

P0-C2 manual acceptance:

- Browser opened `http://127.0.0.1:8782/legacy?v=20260608-p0c2-legacy-backend-compat`.
- DOM check confirmed 2 `.agent-task-backend-details` blocks.
- Visible legacy fallback text includes “选择 StatsPAI，因为它适合本地统计执行、结构化结果和可追溯产物”, “Python OLS / StataMCP / Codex” and “不会自动进入正式层”.
- Screenshot saved to `artifacts/ui-checks/p0c2-legacy-backend-compat-20260608.png`.

### Task P0-D: UX contrast and action clarity fix

Status: completed for the readability and contrast part of the acceptance. The remaining “one clear next action” work is tracked as the next UX guidance node, because it changes stage interaction logic rather than the visual contrast contract.

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
- Browser screenshot saved under `artifacts/ui-checks/`.

Verified:

```bash
python3 -m unittest tests.test_react_workbench_visual_contract -v
python3 -m unittest tests.test_react_workbench_visual_contract tests.test_agent_task_queue -v
npm run build
```

Manual acceptance:

- Browser opened `http://127.0.0.1:8771/react/react?v=20260608-p0d-contrast`.
- The page is the empirical React workbench, not the unrelated app on port `5173`.
- CSS variables confirmed softer background, panel and text tokens.
- Disabled buttons confirmed with low-noise grey background, readable grey text and opacity `1`.
- Screenshot saved to `artifacts/ui-checks/p0d-react-contrast-20260608.png`.

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

P0-D completed.

Reason: 用户反馈的白色按钮不可读和背景对比度过高问题已先止血；React 工作台现在使用更柔和的暗色面、禁用按钮灰态和更低强度的背景粒子。

P0-D verified:

```bash
python3 -m unittest tests.test_react_workbench_visual_contract -v
python3 -m unittest tests.test_react_workbench_visual_contract tests.test_agent_task_queue -v
npm run build
```

P0-D manual acceptance:

- Browser opened `http://127.0.0.1:8771/react/react?v=20260608-p0d-contrast`.
- DOM style check confirmed disabled button background `rgba(230, 230, 230, 0.075)`, text `rgb(143, 143, 143)`, opacity `1`, and dotted background opacity `0.06`.
- Screenshot saved to `artifacts/ui-checks/p0d-react-contrast-20260608.png`.

P0-E completed.

Reason: Agent Task Queue 现在不只保存任务和 skill 绑定，还会保存一份 LLM 介入交接契约。用户以后点开任务时，可以看到 LLM Supervisor 在哪里做语义判断、确定性服务在哪里接手、人工确认卡在哪里。这个节点没有启动新的 UI 重构，保持在 plan / queue metadata 范围内。

P0-E behavior added:

```gherkin
Given an approved SupervisorPlan with an LLM intervention plan
And the plan recommends an internal Skill for a sub Agent
When the user creates an Agent Task Queue
Then the queue exposes the LLM intervention contract
And each task exposes which stage is LLM judgment, which service takes over, where human review happens, and why the Skill was selected.
```

P0-E verified:

```bash
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_14_queue_exposes_llm_intervention_handoff_contract -v
python3 -m unittest tests.test_agent_task_queue -v
python3 -m py_compile Product/backend/agent_task_queue_service.py
```

P0-E implementation:

- `llm_intervention_contract` is stored at the Agent Task Queue top level.
- `llm_intervention_handoff` is stored on each task.
- Skill-bound tasks use the `skill_selection` handoff and preserve `selected_skill_reason`.
- Non-skill tasks fall back to the `agent_task_queue` handoff.
- Legacy queues are normalized with the default contract so old state files still load.

P0-G completed.

Reason: 用户反馈任务处理页“不知道自己在干嘛”，核心原因之一是后端没有给前端一个明确的主动作。现在 Agent Task Queue 和每个任务都会从状态机推导 `primary_action`，前端可以直接展示“当前唯一建议动作”，不用从多个按钮和状态里猜。

P0-G behavior added:

```gherkin
Given a queued Agent Task
When the queue is shown
Then the primary action is to open dispatch review, not to execute.

Given the dispatch was approved
When the queue is shown
Then the primary action is to select an execution backend.

Given a backend was selected
When the queue is shown
Then the primary action is to start real execution.

Given execution succeeded
When the queue is shown
Then the primary action is to review the result, without writing to the formal layer.
```

P0-G verified:

```bash
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_15_queue_and_tasks_expose_one_primary_next_action -v
python3 -m unittest tests.test_agent_task_queue -v
python3 -m py_compile Product/backend/agent_task_queue_service.py
```

P0-G implementation:

- Empty queues expose a create/approve primary action.
- Created tasks expose `primary_action` from current status.
- Queue-level `primary_action` points to the first task that still needs user action.
- State changes from dispatch review, backend selection and execution recompute the primary action.
- `writes_formal_layer` is explicitly `false` through this chain.

Next node: **P0-H frontend consumes queue primary_action**.

20-minute boundary for P0-H:

- Do not redesign visual language.
- Show the backend-provided `primary_action` label and reason in the Agent Task Queue panel.
- Keep the action gated by existing buttons/endpoints; do not add new execution authority.

P0-H completed.

Reason: P0-G 已经让后端推导 `primary_action`，但旧工作台仍主要显示 `next_action` 和状态，用户需要自己猜下一步。P0-H 把后端的主动作直接显示在队列顶部和任务卡中，并解释“为什么现在做这一步”。

P0-H behavior added:

```gherkin
Given an Agent Task Queue with a backend-provided primary_action
When the user opens the queue panel
Then the panel shows the current recommended action and the reason.

Given a task carries its own primary_action
When the task card is rendered
Then the task summary shows the task-specific recommended action and reason before the folded details.
```

P0-H verified:

```bash
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueFrontendTests.test_bdd_14_frontend_renders_queue_primary_action_guidance -v
python3 -m unittest tests.test_agent_task_queue -v
node --check Product/web/assets/app.js
git diff --check -- Product/web/assets/app.js Product/web/assets/styles.css tests/test_agent_task_queue.py docs/superpowers/plans/2026-06-08-final-product-goal-development.md
```

P0-H implementation:

- Added `renderAgentTaskPrimaryAction`.
- Queue-level panel now renders `queue.primary_action` as “当前建议动作”.
- Task cards now render `task.primary_action` as “任务建议动作”.
- The existing decision row falls back to `queue.primary_action.label` before legacy `next_action`.
- Updated legacy asset version to `20260608-p0h-primary-action` so browser acceptance loads the new JS/CSS instead of a cached workbench script.
- No new execution endpoint or formal-layer authority was added.

Next node: **P0-I Browser verify primary_action guidance in legacy workbench**.

20-minute boundary for P0-I:

- Open the local legacy workbench in the Codex browser.
- Confirm the queue panel visibly contains “当前建议动作” and “为什么现在做这一步”.
- Capture screenshot evidence if the server is available.

P0-I completed.

Reason: P0-H 的代码测试只能说明前端具备渲染能力，用户真正需要的是页面打开后能看到“现在做什么”和“为什么”。本节点用当前后端服务和真实页面验证队列状态已经穿透到 UI。

P0-I verified:

```bash
python3 - <<'PY'
from pathlib import Path
from playwright.sync_api import sync_playwright
url = 'http://127.0.0.1:8782/legacy?v=20260608-p0h-primary-action-3'
out = Path('artifacts/ui-checks/p0h-primary-action-20260608.png').resolve()
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    page = browser.new_page(viewport={'width': 1440, 'height': 1200}, device_scale_factor=1)
    page.goto(url, wait_until='networkidle')
    page.wait_for_selector('.agent-task-queue-card', timeout=10000)
    result = page.evaluate("""() => ({
      primaryActionCount: document.querySelectorAll('.agent-task-primary-action').length,
      hasCurrentAction: document.body.innerText.includes('当前建议动作'),
      hasReason: document.body.innerText.includes('为什么现在做这一步'),
      hasTaskAction: document.body.innerText.includes('任务建议动作')
    })""")
    page.screenshot(path=str(out), full_page=False)
    browser.close()
print(result)
print('screenshot', out)
PY
```

Browser evidence:

- URL: `http://127.0.0.1:8782/legacy?v=20260608-p0h-primary-action-3`
- `primaryActionCount`: 4
- `hasCurrentAction`: true
- `hasReason`: true
- `hasTaskAction`: true
- Screenshot: `artifacts/ui-checks/p0h-primary-action-20260608.png`

Implementation note:

- The running backend had to be restarted because it was still serving the pre-P0-G in-memory module. After restart, the API normalized the saved legacy queue and returned `primary_action`.
- No persisted research state was rewritten.

Next node: **P0-J commit P0-H/P0-I scoped changes**.

20-minute boundary for P0-J:

- Stage only P0-H/P0-I files.
- Do not stage unrelated dirty research artifacts.
- Commit with decision-record format.

P0-J completed.

Commit:

- Included in the scoped commit `Show primary action guidance in agent queue`.

Next node: **P1-A design LLM intervention points for final product chain**.

20-minute boundary for P1-A:

- Do not implement new LLM calls yet.
- Write the explicit product map for when LLM Supervisor intervenes, what deterministic service owns, when Agent Team is dispatched, and when control returns to the user.
- Convert that map into the next BDD/API contract target.

P1-A completed.

Reason: Goal 模式需要一条稳定的产品主链路，不然 LLM Supervisor 会变成零散功能。现在 Agent Task Queue 顶层暴露 `llm_intervention_contract`，把“输入题目 -> SupervisorPlan -> Skill 选择 -> Agent Task Queue -> 文献 -> 数据变量 -> 方法 -> 执行 -> 写作 -> 导出预检”列成明确 `product_chain`，每一站都说明 LLM 做什么、确定性服务谁接手、Agent Team 什么时候参与、人什么时候拿回控制权，以及是否能写正式层。

P1-A behavior added:

```gherkin
Given no custom LLM intervention plan exists
When the user reads the Agent Task Queue contract
Then the default contract maps the full product chain from topic intake to export preflight.

Given a stage handoff is exposed
When the frontend or another agent inspects it
Then it includes the LLM role, deterministic owner, Agent Team policy, human gate, control-return condition and formal-layer boundary.

Given the queue reaches execution and export stages
When the contract is inspected
Then execution is owned by the execution backend router
And export still waits for human preflight review.
```

P1-A verified:

```bash
python3 -m py_compile Product/backend/agent_task_queue_service.py
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_16_default_llm_intervention_contract_maps_full_product_chain -v
python3 -m unittest tests.test_agent_task_queue -v
```

P1-A implementation:

- Added `product_chain` to the default LLM intervention contract.
- Added default stage handoffs for `topic_intake`, `supervisor_plan`, `skill_selection`, `agent_task_queue`, `literature_search`, `data_variables`, `method_design`, `execution_experiment`, `writing` and `review_export`.
- Each handoff now exposes `agent_team_policy`, `control_returns_to_user_when` and `writes_formal_layer`.
- Custom `plan.llm_intervention_plan.stage_handoffs` still override defaults without losing the product-chain order.
- No new LLM call was introduced in this node; this is the orchestration contract the later LLM calls must obey.

Subagent read-only result:

- Epicurus confirmed the safest integration point is the existing `SupervisorPlan -> AgentTaskQueue` contract path.
- Existing SupervisorPlan already has provider, stage plan, subagent dispatch, skill judgments and write-boundary fields.
- Queue creation already requires an approved SupervisorPlan and `can_dispatch=true`.
- Next implementation should extend this contract into reference/literature chain policy or UI visibility, not create a separate LLM orchestration service.

Next node: **P1-B reference and literature chain policy enters queue contract**.

20-minute boundary for P1-B:

- Do not build a full literature crawler.
- Add the policy fields that say when arXiv / Scholar / CNKI / Zotero / local notes are requested.
- Keep the output as a queue-readable contract and test it before any UI work.

P1-B completed.

Reason: 文献综述和引用不能再只是“后面搜索一下”。现在 Agent Task Queue 顶层暴露 `reference_chain_policy`，把 arXiv / Scholar / CNKI / Zotero / local notes 的触发条件、使用方式、递归深度、最大迭代次数、候选引用状态、引用核验队列和正式写回 gate 都写进同一个可读契约。文献类任务会继承这份策略，方法类任务不会被误挂文献链路。

P1-B behavior added:

```gherkin
Given an approved SupervisorPlan creates an Agent Task Queue
When the queue is inspected
Then it exposes the default reference chain policy with arXiv, Scholar, CNKI, Zotero and local notes.

Given a LiteratureAgent task exists
When it is created from the queue
Then it inherits the reference chain policy and remains in needs_review state.

Given candidate references are produced
When they are used before review
Then they can only enter draft citation state
And formal literature writeback still waits for review_literature_seed_package.
```

P1-B verified:

```bash
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_17_reference_chain_policy_enters_queue_and_literature_task -v
python3 -m py_compile Product/backend/agent_task_queue_service.py
python3 -m unittest tests.test_agent_task_queue -v
```

P1-B implementation:

- Added default `reference_chain_policy` to empty and created Agent Task Queue responses.
- Added default sources: `arxiv`, `scholar`, `cnki`, `zotero`, `local_notes`.
- Added `max_depth=2` and `max_iterations=5` as the first recursive-search MVP guardrail.
- Added candidate reference states: `candidate`, `verified`, `rejected`.
- Added `citation_verification_queue` and `review_literature_seed_package` as the formal writeback gate.
- Literature/reference tasks inherit `reference_chain_policy`; unrelated method tasks stay clean.
- Legacy saved queues are normalized with the default policy when read.

Next node: **P1-C connect reference chain policy into SupervisorPlan generation prompt/schema**.

20-minute boundary for P1-C:

- Do not build real web search yet.
- Make the SupervisorPlan contract able to request or override `reference_chain_policy`.
- Test that LLM-generated plans can carry custom source priorities and still keep draft/formal boundaries.

P1-C completed.

BDD behavior added:

```text
Given the local Codex Supervisor is asked to generate a plan
When it receives the prompt
Then the prompt explicitly requires reference_chain_policy with source_priority,
CNKI / Scholar / Zotero / local notes / arXiv sources, max_depth, max_iterations,
draft citation policy, formal writeback gate, and writes_formal_layer=false.

Given the LLM returns a reference_chain_policy
When SupervisorPlan is normalized and persisted
Then the plan keeps the source priority and search bounds, but forces formal
writeback to remain disabled until review_literature_seed_package.

Given an approved SupervisorPlan contains source priorities
When Agent Task Queue is created
Then the queue and LiteratureAgent task inherit the priority without letting
candidate citations write into the formal layer.
```

P1-C verified:

```bash
python3 -m unittest tests.test_supervisor_plan.SupervisorPlanApiTests.test_bdd_19_supervisor_plan_prompt_requests_reference_chain_policy tests.test_supervisor_plan.SupervisorPlanFrontendTests.test_bdd_20_supervisor_plan_keeps_reference_chain_policy_for_queue_contract -v
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_17_reference_chain_policy_enters_queue_and_literature_task -v
python3 -m unittest tests.test_supervisor_plan tests.test_agent_task_queue -v
python3 -m py_compile Product/backend/supervisor_plan_service.py Product/backend/agent_task_queue_service.py
git diff --check -- Product/backend/supervisor_plan_service.py Product/backend/agent_task_queue_service.py tests/test_supervisor_plan.py tests/test_agent_task_queue.py docs/superpowers/plans/2026-06-08-final-product-goal-development.md
```

P1-C implementation:

- Added `reference_chain_policy_template` to SupervisorPlan prompt context.
- Required the LLM output schema to include `reference_chain_policy`.
- Added SupervisorPlan normalization for source priority, source list, bounds, draft policy, and formal gate.
- Forced `writes_formal_layer=false` even if raw LLM output or a hand-written plan tries to set it to true.
- Propagated `source_priority` from SupervisorPlan into Agent Task Queue and LiteratureAgent tasks.

Next node: **P1-D make reference policy visible to product users without adding a crawler yet**.

20-minute boundary for P1-D:

- Do not implement real CNKI / Scholar / Zotero connectors yet.
- Expose the reference policy in a user-facing API/UI contract section as collapsed-by-default evidence requirements.
- Make the user see why CNKI/Scholar/Zotero/local notes/arXiv were selected and what still needs review.

P1-D BDD:

```text
Given SupervisorPlan contains a reference_chain_policy
When the user opens the collapsed plan details
Then the page shows source priority, required artifacts, draft citation policy,
and the formal writeback gate.

Given a LiteratureAgent task inherited the reference_chain_policy
When the user opens the collapsed task details
Then the task explains the reference sources, search bounds, candidate citation
state, and why it cannot silently write into the formal layer.
```

P1-D verified:

```bash
python3 -m unittest tests.test_supervisor_plan.SupervisorPlanFrontendTests.test_bdd_21_frontend_exposes_reference_chain_policy_as_progressive_disclosure tests.test_agent_task_queue.AgentTaskQueueFrontendTests.test_bdd_15_frontend_exposes_reference_chain_policy_in_literature_task_details -v
python3 -m unittest tests.test_supervisor_plan tests.test_agent_task_queue -v
```

P1-D implementation:

- Added a shared `renderReferenceChainPolicy` UI renderer.
- Exposed SupervisorPlan `reference_chain_policy` in the existing collapsed plan details.
- Exposed LiteratureAgent task `reference_chain_policy` in the existing collapsed task details.
- Kept CNKI / Scholar / Zotero / local notes / arXiv as a visible policy contract; no real crawler was added in this node.

Next node: **P1-E add a deterministic literature-source runner scaffold that reads the policy but does not yet claim verified citations**.

20-minute boundary for P1-E:

- Do not add real CNKI / Scholar / Zotero crawling yet.
- Do not mark any citation as verified.
- Do not write into the formal manuscript or canonical method library.
- Route only LiteratureAgent / reference-chain tasks through the new runner; keep ordinary Codex tasks as script generation.

P1-E BDD:

```text
Given a LiteratureAgent task inherited reference_chain_policy
When the user approves dispatch, selects Codex backend, and executes the task
Then the system writes a candidate reference seed package under workspace/runs,
and returns it as local_file evidence.

Given the seed package is produced from source_priority
When the package is inspected
Then it preserves CNKI / Scholar / Zotero / local notes / arXiv priority,
search bounds, required artifacts, and the review_literature_seed_package gate.

Given candidate queries are generated
When the package is inspected
Then every query remains review_state=candidate and can_enter_formal_layer=false;
the package explicitly says it does not claim verified citations.
```

P1-E verified:

```bash
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_18_literature_task_codex_execution_writes_candidate_reference_seed_package -v
python3 -m unittest tests.test_agent_task_queue -v
python3 -m pytest tests/test_p2_aa_agent_task_execution_backend.py -q
python3 -m py_compile Product/backend/reference_chain_seed_runner.py Product/backend/execution_backend_service.py
```

P1-E implementation:

- Added `Product/backend/reference_chain_seed_runner.py`.
- LiteratureAgent / reference-chain Codex execution now writes `workspace/runs/{run_id}/reference_chain_seed_package.json`.
- The package includes source priority, ordered sources, candidate queries, citation verification queue, verification policy, formal writeback gate, and `claims_verified_citations=false`.
- `execute_agent_task_with_backend` now returns `execution_kind=reference_chain_seed_package` only for reference-chain tasks.
- Existing non-literature Codex tasks still generate reviewable scripts, and the P2-AA execution backend tests remain green.

Next node: **P1-F surface the seed package in task result review and connect it to the next human gate**.

20-minute boundary for P1-F:

- Do not implement real CNKI / Scholar / Zotero connectors.
- Do not add a new review API yet.
- Reuse the existing execution result and task result handoff surface.
- Make the generated seed package visible as a candidate review object, not just a file path.

P1-F BDD:

```text
Given a LiteratureAgent Codex task writes a reference_chain_seed_package
When the task execution result is returned
Then the result includes a result_review object with the artifact path,
review_literature_seed_package gate, review focus, candidate reference state,
and formal-layer boundary.

Given the task queue frontend receives execution_kind=reference_chain_seed_package
When the succeeded task is rendered
Then it shows a candidate source package review block with the seed package path,
candidate query count, review gate, and "not verified citation" boundary.
```

P1-F verified:

```bash
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_18_literature_task_codex_execution_writes_candidate_reference_seed_package tests.test_agent_task_queue.AgentTaskQueueFrontendTests.test_bdd_16_frontend_exposes_reference_seed_package_result_review -v
python3 -m unittest tests.test_agent_task_queue -v
python3 -m pytest tests/test_p2_aa_agent_task_execution_backend.py -q
python3 -m py_compile Product/backend/reference_chain_seed_runner.py Product/backend/execution_backend_service.py
node --check Product/web/assets/app.js
```

P1-F implementation:

- Added `build_reference_chain_result_review` beside the seed package writer.
- Codex LiteratureAgent execution now returns and persists `result_review`.
- The result review includes title, artifact path, review gate, next action, candidate query count, review focus, reference state, and formal-layer boundary.
- Added `renderReferenceSeedPackageResultReview` to the task queue result handoff.
- Added a lightweight `.agent-task-reference-seed-result` style block so users can identify the review object before reading the generic run result.

P1-G verified:

```bash
git diff --check -- Product/backend/reference_chain_seed_runner.py Product/backend/execution_backend_service.py Product/web/assets/app.js Product/web/assets/styles.css tests/test_agent_task_queue.py docs/superpowers/plans/2026-06-08-final-product-goal-development.md
git status --short --branch
```

P1-G implementation:

- Committed P1-F as `a421772 Surface literature seed packages for review`.
- Left unrelated dirty/untracked workspace artifacts untouched.

Next node: **P1-H add review_literature_seed_package action endpoint**.

20-minute boundary for P1-H:

- Do not add CNKI / Scholar / Zotero crawlers.
- Do not verify citations automatically.
- Do not promote candidate references to the formal manuscript layer.
- Only add the human review action that decides whether the candidate source package can enter draft-layer literature writing.

P1-H BDD:

```text
Given a LiteratureAgent task has produced a reference_chain_seed_package
When the user approves it with approve_for_draft
Then the task records reference_seed_review=approved_for_draft,
sets next_action=draft_literature_review,
and keeps formal_write_allowed=false.

Given a task has not produced a reference_chain_seed_package
When the user calls the reference seed review endpoint
Then the system rejects the action with reference_seed_package_required
instead of fabricating a review state.

Given the task queue frontend receives a reference seed package result review
When the result block is rendered
Then it exposes actions for approve_for_draft, needs_revision, and reject,
with copy that approval only enters the draft layer.
```

P1-H verified:

```bash
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_19_reference_seed_package_review_only_promotes_to_draft_layer tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_20_reference_seed_package_review_requires_seed_package_result tests.test_agent_task_queue.AgentTaskQueueFrontendTests.test_bdd_17_frontend_exposes_reference_seed_package_review_actions -v
python3 -m unittest tests.test_agent_task_queue -v
python3 -m pytest tests/test_p2_aa_agent_task_execution_backend.py -q
python3 -m py_compile Product/backend/agent_task_queue_service.py Product/app.py
node --check Product/web/assets/app.js
```

P1-H implementation:

- Added `PUT /api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/reference-seed-review`.
- Added review actions: `approve_for_draft`, `needs_revision`, `reject`.
- `approve_for_draft` changes the task to `reviewed_for_draft` and makes the primary action `draft_literature_review`.
- All review outcomes keep `formal_write_allowed=false`, `writes_formal_layer=false`, and `claims_verified_citations=false`.
- Added frontend API binding and review buttons in the candidate source package result block.

Next node: **P1-I draft-layer literature review generation from approved_for_draft seed packages**.

20-minute boundary for P1-I:

- Do not implement CNKI / Scholar / Zotero connector crawling.
- Do not claim citations are verified.
- Do not write to Manuscripts formal sections.
- Only generate a draft-layer markdown literature review from an already approved candidate source seed package.

P1-I BDD:

```text
Given a LiteratureAgent task has produced a reference_chain_seed_package
And the user has approved that seed package for draft use
When the user asks the system to generate a literature review draft
Then the system writes draft_literature_review.md,
records draft_literature_review.status=draft_ready,
sets next_action=review_draft_literature_review,
and keeps formal_write_allowed=false.

Given a reference_chain_seed_package exists but has not been approved
When the user calls the draft literature review endpoint
Then the system rejects the request with reference_seed_review_required.

Given the frontend receives a draft_ready literature review record
When the agent task queue renders the task
Then the user can see the draft artifact path, source artifact path,
review action, and formal-layer boundary.
```

P1-I verified:

```bash
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_21_approved_seed_package_generates_draft_layer_literature_review tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_22_draft_literature_review_requires_approved_seed_package tests.test_agent_task_queue.AgentTaskQueueFrontendTests.test_bdd_18_frontend_exposes_draft_literature_review_generation -v
python3 -m unittest tests.test_agent_task_queue -v
python3 -m pytest tests/test_p2_aa_agent_task_execution_backend.py -q
python3 -m py_compile Product/backend/agent_task_queue_service.py Product/app.py
node --check Product/web/assets/app.js
git diff --check -- Product/backend/agent_task_queue_service.py Product/app.py Product/web/assets/app.js Product/web/assets/styles.css tests/test_agent_task_queue.py docs/superpowers/plans/2026-06-08-final-product-goal-development.md
```

P1-I implementation:

- Added `POST /api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/draft-literature-review`.
- The endpoint requires `reference_seed_review.status=approved_for_draft`.
- It reads the persisted `reference_chain_seed_package.json` and writes `draft_literature_review.md` next to it.
- The task moves to `draft_literature_review_ready` with primary action `review_draft_literature_review`.
- The draft record explicitly keeps `formal_write_allowed=false`, `writes_formal_layer=false`, and `claims_verified_citations=false`.
- The frontend now exposes `生成草稿层文献综述` after approval and renders the resulting draft artifact, source artifact, next action, and formal-layer boundary.

Next node: **P1-J review draft_literature_review and open citation-verification tasks**.

20-minute boundary for P1-J:

- Do not implement CNKI / Scholar / Zotero connector crawling.
- Do not claim citations are verified.
- Do not write to Manuscripts formal sections.
- Only let a reviewed `draft_literature_review.md` open a persisted citation verification task list.

P1-J BDD:

```text
Given a LiteratureAgent task has generated draft_literature_review.md
And the draft is still in exploratory / draft state
When the user approves the draft for citation verification
Then the system records draft_literature_review_review.status=approved_for_citation_verification,
creates citation_verification_tasks from the candidate source queries,
sets next_action=verify_citations,
and keeps formal_write_allowed=false and claims_verified_citations=false.

Given no draft_literature_review.md has been generated
When the user calls the draft literature review review endpoint
Then the system rejects the request with draft_literature_review_required.

Given the frontend receives citation_verification_tasks
When the agent task queue renders the task
Then it exposes draft review actions and a citation verification task section,
with copy that citations are not yet verified and cannot enter the formal layer.
```

P1-J verified:

```bash
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_23_reviewed_draft_literature_review_opens_citation_verification_tasks tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_24_draft_literature_review_review_requires_draft tests.test_agent_task_queue.AgentTaskQueueFrontendTests.test_bdd_19_frontend_exposes_draft_review_and_citation_verification -v
python3 -m unittest tests.test_agent_task_queue -v
python3 -m pytest tests/test_p2_aa_agent_task_execution_backend.py -q
python3 -m py_compile Product/backend/agent_task_queue_service.py Product/app.py
node --check Product/web/assets/app.js
```

P1-J implementation:

- Added `PUT /api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/draft-literature-review-review`.
- The endpoint supports `approve_for_citation_verification`, `needs_revision`, and `reject`.
- `approve_for_citation_verification` moves the task to `citation_verification_ready` and creates persisted `citation_verification_tasks`.
- Each citation verification task remains `pending`, `candidate`, `formal_write_allowed=false`, and `claims_verified_citations=false`.
- The frontend now renders draft review actions and a `引用核验任务` section under the Agent Task Queue item.

Next node: **P1-K verify citation tasks with connector/manual evidence records**.

## P1-K Citation Verification Evidence Records

Boundary: turn the candidate citation list into an auditable verification gate. This node records connector/manual evidence for each citation task and writes a citation verification log only after every required check is present. It does not fetch CNKI/Scholar/Zotero automatically yet.

BDD:

```text
Behavior 25: record evidence for one citation verification task
Given a LiteratureAgent task is citation_verification_ready
And it contains pending citation_verification_tasks
When the user or connector records authors, year, title, venue, doi_or_stable_url, relevance, connector, evidence_url, and note for one citation task
Then that citation task becomes verified,
stores the evidence record,
keeps formal_write_allowed=false,
and leaves the parent task blocked until all citation tasks are verified.

Behavior 26: block incomplete citation evidence
Given a citation verification task is pending
When the user records evidence without a required check such as doi_or_stable_url
Then the system rejects the request with citation_verification_evidence_incomplete
and does not mutate the queue.

Behavior 27: complete the citation verification gate
Given every citation_verification_task has verified evidence
When the final citation task is recorded
Then the parent task becomes citation_verification_complete,
writes Results/json/citation_verification_log.json,
sets claims_verified_citations=true only for this evidence log,
and exposes the next action as generate_verified_literature_package.
```

Status: implemented and verified.

Implemented:

- Added the citation evidence API:
  `PUT /api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/citation-verification/{citation_task_id}`.
- Required evidence fields are explicit: connector, authors, year, title, venue, DOI or stable URL, relevance, and evidence URL.
- Incomplete evidence returns `citation_verification_evidence_incomplete` before the queue file is touched.
- A verified citation task stores `evidence_record`, remains outside the formal layer, and leaves the parent task blocked until all candidate citations are verified.
- When every citation task is verified, the parent task becomes `citation_verification_complete`, writes `Results/json/citation_verification_log.json`, and exposes `generate_verified_literature_package` as the next action.
- The frontend now renders each citation task’s evidence state, a JSON evidence editor, and a `记录核验证据` action wired to the API.

Verified:

```bash
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_25_records_single_citation_verification_evidence tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_26_blocks_incomplete_citation_verification_evidence tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_27_all_verified_citations_write_verification_log tests.test_agent_task_queue.AgentTaskQueueFrontendTests.test_bdd_20_frontend_exposes_citation_evidence_recording_state -v
python3 -m unittest tests.test_agent_task_queue -v
python3 -m pytest tests/test_p2_aa_agent_task_execution_backend.py -q
python3 -m py_compile Product/backend/agent_task_queue_service.py Product/app.py
node --check Product/web/assets/app.js
```

Next node: **P1-L generate verified literature package from citation verification log**.

## P1-L Verified Literature Package

Boundary: convert a completed citation verification log into a reusable verified literature package. This package is still a draft-layer product artifact: it proves citation metadata has been checked, but it does not silently write references into the formal manuscript.

BDD:

```text
Behavior 28: generate a verified literature package from a complete citation log
Given every citation verification task has verified source evidence
And Results/json/citation_verification_log.json exists
When the user generates the verified literature package
Then the system writes Results/json/verified_literature_package.json,
stores verified reference entries with citation text and source evidence,
keeps formal_write_allowed=false,
and exposes review_verified_literature_package as the next action.

Behavior 29: block package generation before citation verification is complete
Given citation verification is still pending
When the user tries to generate the verified literature package
Then the system returns citation_verification_complete_required
and does not create Results/json/verified_literature_package.json.
```

Status: implemented and verified.

Implemented:

- Added `POST /api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/verified-literature-package`.
- The service requires `citation_verification_complete` and a real `Results/json/citation_verification_log.json`.
- The generated package has schema `p1.verified_literature_package.v1`, `verified_references`, `citation_text`, evidence links, connector metadata, and a formal-layer boundary.
- The parent Agent task moves to `verified_literature_package_ready` and exposes `review_verified_literature_package`.
- The frontend now exposes a `生成已核验文献包` action after citation verification is complete and renders the resulting package path and source log.

Verified:

```bash
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_28_verified_citation_log_generates_literature_package tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_29_verified_literature_package_requires_complete_citation_log tests.test_agent_task_queue.AgentTaskQueueFrontendTests.test_bdd_21_frontend_exposes_verified_literature_package_action -v
```

Next node: **P1-M review verified literature package before manuscript citation use**.

## P1-M Verified Literature Package Review Gate

Boundary: a verified literature package is useful evidence, but it still needs human review before the system can build a manuscript citation plan. This node opens the citation-plan step without writing formal manuscript text.

BDD:

```text
Behavior 30: approve a verified literature package for manuscript citation planning
Given Results/json/verified_literature_package.json exists
And the Agent task is waiting for verified literature package review
When the user approves the package for manuscript citations
Then the system records a human review gate,
sets manuscript_citation_plan_allowed=true,
keeps formal_write_allowed=false,
and exposes generate_manuscript_citation_plan as the next action.

Behavior 31: block literature package review before a package exists
Given citation verification has completed
But Results/json/verified_literature_package.json has not been generated
When the user tries to approve a literature package review
Then the system returns verified_literature_package_required
and does not open manuscript citation planning.
```

Status: implemented and verified.

Implemented:

- Added `PUT /api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/verified-literature-package-review`.
- The service accepts `approve_for_manuscript_citations`, `needs_revision`, and `reject`.
- Approval records `review_gate=review_verified_literature_package`, `reviewer=human`, `manuscript_citation_plan_allowed=true`, and `formal_write_allowed=false`.
- The parent Agent task moves to `verified_literature_package_approved` and exposes `generate_manuscript_citation_plan`.
- The frontend renders the review gate with `批准进入引用计划`, `要求修订`, and `拒绝文献包` actions.

Verified:

```bash
python3 -m unittest tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_30_review_verified_literature_package_opens_manuscript_citation_plan tests.test_agent_task_queue.AgentTaskQueueApiTests.test_bdd_31_verified_literature_package_review_requires_package tests.test_agent_task_queue.AgentTaskQueueFrontendTests.test_bdd_22_frontend_exposes_verified_literature_package_review_gate -v
```

Next node: **P1-N generate manuscript citation plan from approved verified literature package**.
