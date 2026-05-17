# Agent Task Queue To AI Research Pipeline MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the next MVP layer after P2-U: turn an approved SupervisorPlan and Agent Task Queue into a human-audited, data-aware, method-disciplined empirical research pipeline with real data promotion, execution checks, reviewer scoring, and export readiness.

**Architecture:** Keep the current FastAPI + static frontend architecture. Product state remains explicit JSON artifacts under `state/product/`; run evidence remains under `state/runs/{run_id}` and project artifacts under `Results/`, `Manuscripts/`, and `artifacts/`. LLM/Codex Supervisor proposes and decomposes work, but every state mutation that affects the research design, execution plan, findings, manuscript, or export package must pass through an explicit API and human-visible UI action.

**Tech Stack:** Python 3 standard library + FastAPI backend, static HTML/CSS/JS frontend, `unittest` test suite, local JSON state files, current OLS Python adapter, StatsPAI validation path, future StataMCP/Stata adapter boundary.

---

## 0. Locked Starting State

**Local project folder:** `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`

**Git remote:** `https://github.com/yishu-ziyu/empirical-paper-workbench.git`

**Branch:** `main`

**Current status at plan creation:** local `main` is aligned with `origin/main`, no local changes.

**Current commit:** `86496774ff6af674feb81e1da165c7a24a01968b`

**Current commit subject:** `Make approved supervisor plans dispatchable as auditable queues`

**Current product baseline:**
- Topic-first home exists.
- `ResearchQuestion / TopicSession` is persisted in `state/product/research_question.json`.
- SupervisorPlan generation is bound to confirmed ResearchQuestion.
- SupervisorPlan review state machine exists.
- Agent Task Queue exists and is summary-first.
- Current true app state has no approved `state/product/supervisor_plan.json`, so Agent Task Queue is correctly blocked.
- Real data inventory and import preflight exist.
- Real CFPS `.dta` field profile and VariableRoleCandidate review exist.
- Formal `VariableRoleSet`, `DesignSpec`, and `RunPlan` state objects already exist.
- Python OLS and StatsPAI CSV OLS validation exist; method families beyond OLS are not production execution backends yet.

**Current verification baseline from P2-U:**
- `python3 -m unittest discover -s tests -v` -> 234 tests OK, skipped=1.
- `python3 -m py_compile Product/app.py Product/backend/agent_task_queue_service.py Product/backend/supervisor_plan_service.py` passed.
- `node --check Product/web/assets/app.js` passed.
- Browser blocked-state and controlled approved-plan state were verified.

---

## 1. Product Direction Locked By This Plan

The product is not a generic dashboard and not a one-click fake paper generator. It is a **human-in-the-loop empirical research operating system**:

```text
Research topic / real dataset
-> data-aware candidate research questions
-> formal variable role review
-> identification design
-> method workflow checklist
-> audited task queue
-> real execution backend
-> reviewer scoring
-> finding approval
-> manuscript candidate
-> export / reproducibility package
```

Article-derived product principles to enforce:

- AI-generated research questions must be data-aware, not pure LLM guesses.
- Every candidate must bind to actual variables, sample structure, feasible method, and risk notes.
- DID / IV / RDD / PSM / DML are workflows with prerequisites and evaluator checks, not decorative buttons.
- Agent roles are product objects: Supervisor, Data Agent, Design Agent, Execution Agent, Reviewer Agent, Manuscript Agent, Verifier Agent.
- Reviewer Agent output must become a scorecard and follow-up task suggestions, not vague prose.
- Claims, tables, figures, and manuscript sections must bind to provenance and evidence level.
- Human gates are required for topic choice, variable roles, design strategy, execution dispatch, result claims, and export.

---

## 2. File Structure Map

### Existing files to extend

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/app.py`
  - Add new API endpoints for dispatch audit, candidate promotion, method workflow checks, reviewer scoring, and verifier checks.

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/agent_task_queue_service.py`
  - Extend queue items from `ready_for_dispatch` draft into `reviewed_for_dispatch`, `dispatched`, `blocked`, `completed`, `failed`, `cancelled`.

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/variable_role_service.py`
  - Add promotion from approved `VariableRoleCandidate` into editable formal `VariableRoleSet` draft.

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/design_spec_service.py`
  - Add method workflow checklist binding to `DesignSpec` and `RunPlan`.

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/project_service.py`
  - Add execution backend routing metadata and method-workflow evaluator hooks without breaking existing full-run path.

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/results_draft_service.py`
  - Add reviewer score binding and follow-up task suggestions to FindingCard output.

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/manuscript_candidate_service.py`
  - Add verifier checks before export promotion.

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/web/index.html`
  - Add panels only where they serve the main workflow. Avoid a new all-features wall.

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/web/assets/app.js`
  - Add client API bindings, render functions, and event handlers.
  - Keep default visible UI summary-first; details go into `details/summary` or the right inspector pattern.

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/web/assets/styles.css`
  - Extend clean workbench styles with dense but readable evidence rows, queue states, scorecards, and verifier checks.

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Tasks/current-stage.md`
- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Tasks/todo.md`
- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Tasks/handoff.md`
- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Tasks/manifest.md`
- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Tasks/decision-log.md`
- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Tasks/review.md`
  - Update after every completed phase.

### New backend files to create

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/task_dispatch_service.py`
  - Own human dispatch audit state and transition rules for Agent Task Queue items.

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/method_workflow_service.py`
  - Own method family checklists for OLS, DID, IV, RDD, PSM, DML.

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/reviewer_score_service.py`
  - Own reviewer scorecards and follow-up task suggestions.

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/verifier_service.py`
  - Own citation/result/reproducibility/export verification checks.

### New BDD docs to create

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/docs/architecture-v2/codex-phase-p2-dispatch-audit-bdd.md`
- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/docs/architecture-v2/codex-phase-p2-real-variable-role-promotion-bdd.md`
- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/docs/architecture-v2/codex-phase-p2-method-workflow-checklist-bdd.md`
- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/docs/architecture-v2/codex-phase-p2-reviewer-scorecard-bdd.md`
- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/docs/architecture-v2/codex-phase-p2-verifier-export-gates-bdd.md`

### New tests to create

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/tests/test_agent_task_dispatch_audit.py`
- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/tests/test_real_variable_role_promotion.py`
- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/tests/test_method_workflow_checklist.py`
- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/tests/test_reviewer_scorecard.py`
- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/tests/test_verifier_export_gates.py`

---

## 3. Execution Protocol For Every Task

Every task below must follow this loop:

```text
1. Write BDD doc or extend existing BDD doc.
2. Write failing tests.
3. Run only the target tests and confirm RED for the expected reason.
4. Implement the minimum production code.
5. Run target tests and adjacent regression tests.
6. Run full unittest before commit.
7. Run py_compile and node --check when touched files require them.
8. Use Browser / Computer Use for visible app verification.
9. Update Tasks/*.md.
10. Commit with Lore trailers and push.
```

Required commit trailer:

```text
Co-authored-by: OmX <omx@oh-my-codex.dev>
```

Minimum final verification after each phase:

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile Product/app.py Product/backend/*.py
node --check Product/web/assets/app.js
git diff --check
git status --short --branch
```

---

## 4. Task P2-V: Human Dispatch Audit For Agent Task Queue

**Goal:** Let users explicitly review and approve individual Agent Task Queue items before any task can move toward execution.

**Business rule:** An approved SupervisorPlan can create a queue, but queue creation is not permission to execute. Each task must pass dispatch audit.

**Files:**
- Create: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/docs/architecture-v2/codex-phase-p2-dispatch-audit-bdd.md`
- Create: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/tests/test_agent_task_dispatch_audit.py`
- Create: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/task_dispatch_service.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/agent_task_queue_service.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/app.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/web/index.html`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/web/assets/app.js`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/web/assets/styles.css`

### BDD cases

- [ ] **Step 1: Write BDD doc**

Add these behaviors:

```gherkin
Feature: Agent Task Dispatch Audit

  Scenario: Queue item cannot be dispatched before human audit
    Given an Agent Task Queue exists with task "data_profile"
    And the task status is "queued"
    When the user requests task dispatch status
    Then the task is blocked by "dispatch_review_required"
    And no execution backend is called

  Scenario: User approves a queue item for dispatch
    Given an Agent Task Queue exists with task "data_profile"
    And the task has input evidence and output requirements
    When the user approves dispatch with note "数据画像任务可以执行"
    Then the task status becomes "reviewed_for_dispatch"
    And the dispatch review records reviewer, note, timestamp, and evidence level "local_file"

  Scenario: User rejects a queue item
    Given an Agent Task Queue exists with task "design_review"
    When the user rejects dispatch with note "识别策略不完整"
    Then the task status becomes "blocked"
    And the task cannot be executed until a new review decision is made

  Scenario: Dispatch audit does not mutate research state
    Given ResearchQuestion, VariableRoleSet, DesignSpec, RunPlan, and SupervisorPlan files exist
    When a queue item is approved for dispatch
    Then none of those files are modified

  Scenario: Frontend keeps task details collapsed by default
    Given the queue contains multiple tasks
    When the Overview page renders the Agent Task Queue
    Then each task shows status, owner, blockers, and one dispatch action area
    And input evidence, output requirements, and audit log are hidden until expanded
```

- [ ] **Step 2: Write failing tests**

Create `tests/test_agent_task_dispatch_audit.py` with these tests and assertions:

```text
AgentTaskDispatchAuditTests.test_bdd_1_queue_item_requires_human_dispatch_review
- Arrange a queue with one queued task.
- Call GET queue or task dispatch status.
- Assert blocker contains dispatch_review_required.
- Assert task can_execute is false.

AgentTaskDispatchAuditTests.test_bdd_2_user_approves_queue_item_for_dispatch
- Arrange a queue with one queued task and evidence metadata.
- Call PUT dispatch-review with action=approve and a Chinese note.
- Assert task status is reviewed_for_dispatch.
- Assert dispatch_review contains action, note, reviewed_by, reviewed_at, and evidence_level=local_file.

AgentTaskDispatchAuditTests.test_bdd_3_user_rejects_queue_item_and_blocks_execution
- Arrange a queue with one queued task.
- Call PUT dispatch-review with action=reject.
- Assert task status is blocked.
- Assert can_execute is false.
- Assert next_action explains revision or replacement.

AgentTaskDispatchAuditTests.test_bdd_4_dispatch_review_does_not_mutate_research_state
- Arrange checksum or mtime snapshots for ResearchQuestion, VariableRoleSet, DesignSpec, RunPlan, and SupervisorPlan.
- Approve one queue item.
- Assert the snapshots are unchanged.

AgentTaskDispatchAuditTests.test_bdd_5_frontend_renders_summary_first_dispatch_controls
- Read Product/web/index.html and Product/web/assets/app.js.
- Assert agent-task-queue panel contains dispatch controls.
- Assert details/summary is used for evidence and audit logs.
- Assert default details are not rendered with open attribute.
```

Expected initial failures:

```text
404 for PUT /api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/dispatch-review
ImportError or AttributeError for task_dispatch_service
Frontend test fails because data-dispatch-review-action is missing
```

- [ ] **Step 3: Run RED**

```bash
python3 -m unittest tests.test_agent_task_dispatch_audit -v
```

Expected: FAIL for missing API/service/UI only.

- [ ] **Step 4: Implement backend dispatch audit**

Add API:

```text
PUT /api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/dispatch-review
```

Payload:

```json
{
  "action": "approve",
  "note": "数据画像任务可以执行"
}
```

Supported actions:

```text
approve -> reviewed_for_dispatch
reject -> blocked
needs_revision -> needs_revision
```

Write state back into:

```text
state/product/agent_task_queue.json
```

Each task must gain:

```json
{
  "dispatch_review": {
    "action": "approve",
    "note": "数据画像任务可以执行",
    "reviewed_by": "human",
    "reviewed_at": "ISO-8601 timestamp",
    "evidence_level": "local_file"
  },
  "status": "reviewed_for_dispatch",
  "can_execute": false,
  "next_action": "select_execution_backend"
}
```

`can_execute` remains `false` in P2-V because backend selection and execution is a later explicit gate.

- [ ] **Step 5: Implement frontend dispatch audit UI**

Add visible controls inside each task row:

```text
批准派工
要求修改
阻断任务
```

Default visible text per task:

```text
任务名
负责人
当前状态
阻塞项
派工审阅状态
```

Details remain folded:

```html
<details class="agent-task-details">
  <summary>查看任务证据和审计</summary>
</details>
```

- [ ] **Step 6: Verify**

```bash
python3 -m unittest tests.test_agent_task_dispatch_audit tests.test_agent_task_queue -v
python3 -m unittest discover -s tests -v
python3 -m py_compile Product/app.py Product/backend/agent_task_queue_service.py Product/backend/task_dispatch_service.py
node --check Product/web/assets/app.js
git diff --check
```

- [ ] **Step 7: Browser acceptance**

Start app:

```bash
python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8768
```

Open:

```text
http://127.0.0.1:8768/?v=20260517-p2v-dispatch-audit
```

Acceptance:

```text
Overview -> Agent 任务队列
Task rows show summary only.
Click 查看任务证据和审计 to expand details.
Approve dispatch changes task status to reviewed_for_dispatch.
No formal research state files change.
Console error count is 0.
```

- [ ] **Step 8: Commit**

Lore intent subject:

```text
Require human dispatch review before agent task execution
```

---

## 5. Task P2-W: Promote Real VariableRoleCandidate Into Formal VariableRoleSet Draft

**Goal:** Turn approved real-data field candidates into an editable formal VariableRoleSet draft, without silently replacing the confirmed research state.

**Business rule:** Field heuristics can suggest roles, but only a human-edited and explicitly saved VariableRoleSet can enter DesignSpec and RunPlan.

**Files:**
- Create: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/docs/architecture-v2/codex-phase-p2-real-variable-role-promotion-bdd.md`
- Create: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/tests/test_real_variable_role_promotion.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/variable_role_service.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/app.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/web/assets/app.js`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/web/assets/styles.css`

### BDD cases

- [ ] **Step 1: Write BDD doc**

```gherkin
Feature: Real Variable Role Promotion

  Scenario: Approved candidate creates editable draft
    Given a VariableRoleCandidate has review_status "approved_candidate"
    When the user chooses "基于候选创建变量角色草稿"
    Then the system creates a VariableRoleSet draft
    And the draft records source_candidate_id and source_dataset evidence
    And the draft status is "draft"

  Scenario: Promotion does not overwrite approved VariableRoleSet
    Given an approved VariableRoleSet already exists
    When the user creates a draft from an approved candidate
    Then the approved VariableRoleSet remains unchanged
    And the new draft is stored as pending_variable_roles_draft

  Scenario: User edits and approves promoted draft
    Given a promoted draft exists
    When the user edits outcome, treatment, controls, fixed effects, and cluster field
    And saves with status "approved"
    Then state/product/variable_roles.json is updated
    And the source candidate provenance remains visible

  Scenario: Frontend separates heuristic candidate from formal state
    Given a real-data candidate and a formal VariableRoleSet draft exist
    When Data & Variables renders
    Then the candidate card says "候选建议"
    And the formal editor says "正式变量角色"
```

- [ ] **Step 2: Write failing tests**

Create these tests:

```text
RealVariableRolePromotionTests.test_bdd_1_approved_candidate_creates_editable_draft
- Arrange variable_role_candidates.json with an approved_candidate.
- Call POST promote.
- Assert response status is draft and source_candidate_id matches.
- Assert variable_roles_drafts.json is created.

RealVariableRolePromotionTests.test_bdd_2_promotion_does_not_overwrite_approved_variable_roles
- Arrange existing variable_roles.json and record its hash.
- Promote an approved candidate.
- Assert variable_roles.json hash is unchanged.

RealVariableRolePromotionTests.test_bdd_3_user_approves_promoted_draft_into_formal_state
- Arrange a promoted draft.
- Call existing PUT /variable-roles with edited roles and status=approved.
- Assert formal variable_roles.json includes source_candidate provenance.

RealVariableRolePromotionTests.test_bdd_4_frontend_separates_candidate_from_formal_state
- Read frontend files.
- Assert visible copy includes 候选建议 and 正式变量角色.
- Assert promote action and formal save action are separate handlers.
```

Expected initial failures:

```text
POST /api/v1/projects/{project_id}/variable-role-candidates/{candidate_id}/promote returns 404
Frontend lacks data-promote-variable-candidate-action
```

- [ ] **Step 3: Run RED**

```bash
python3 -m unittest tests.test_real_variable_role_promotion -v
```

- [ ] **Step 4: Implement promotion API**

Add:

```text
POST /api/v1/projects/{project_id}/variable-role-candidates/{candidate_id}/promote
```

Response shape:

```json
{
  "status": "draft",
  "draft_id": "variable_roles_draft_from_<candidate_id>",
  "source_candidate_id": "<candidate_id>",
  "evidence_level": "local_file",
  "roles": {
    "outcome": [],
    "treatment": [],
    "controls": [],
    "instruments": [],
    "fixed_effects": [],
    "cluster_by": []
  },
  "write_boundary": "draft_only_until_user_approval"
}
```

Persist draft to:

```text
state/product/variable_roles_drafts.json
```

Do not change:

```text
state/product/variable_roles.json
```

until existing `PUT /variable-roles` is called with explicit approved status.

- [ ] **Step 5: Frontend**

In Data & Variables:

```text
真实字段候选
候选建议：outcome / treatment / controls
按钮：基于候选创建变量角色草稿

正式变量角色
可编辑 outcome / treatment / controls / instruments / fixed_effects / cluster_by
按钮：保存正式变量角色
```

- [ ] **Step 6: Verify**

```bash
python3 -m unittest tests.test_real_variable_role_promotion tests.test_variable_role_candidates tests.test_variable_role_confirmation -v
python3 -m unittest discover -s tests -v
python3 -m py_compile Product/app.py Product/backend/variable_role_service.py
node --check Product/web/assets/app.js
git diff --check
```

- [ ] **Step 7: Browser acceptance**

Open:

```text
http://127.0.0.1:8768/?v=20260517-p2w-real-variable-promotion
```

Acceptance:

```text
Data & Variables shows real-data candidate as 候选建议.
Click 基于候选创建变量角色草稿.
Formal editor appears separately.
Saving formal roles updates workflow contract.
Candidate card remains provenance, not source of truth.
```

- [ ] **Step 8: Commit**

Subject:

```text
Separate real-data role candidates from formal variable roles
```

---

## 6. Task P2-X: Method Workflow Checklist Library

**Goal:** Encode method families as prerequisite checklists and evaluator requirements before execution.

**Business rule:** OLS, DID, IV, RDD, PSM, and DML are not equal buttons. Each method must declare required data structure, required variables, required diagnostics, and readiness status.

**Files:**
- Create: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/docs/architecture-v2/codex-phase-p2-method-workflow-checklist-bdd.md`
- Create: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/tests/test_method_workflow_checklist.py`
- Create: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/method_workflow_service.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/design_spec_service.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/overview_service.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/app.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/web/assets/app.js`

### BDD cases

- [ ] **Step 1: Write BDD doc**

```gherkin
Feature: Method Workflow Checklist

  Scenario: OLS is ready when outcome and treatment exist
    Given approved VariableRoleSet has outcome and treatment
    When method workflow is requested
    Then OLS has readiness_status "ready"
    And required checks include sample size, missingness, coefficient table, residual diagnostics

  Scenario: DID is blocked without panel time and treatment timing
    Given approved VariableRoleSet has no time variable and no treatment timing
    When method workflow is requested
    Then DID has readiness_status "blocked"
    And blockers include "time_variable_required" and "treatment_timing_required"

  Scenario: IV is blocked without instruments
    Given approved VariableRoleSet has no instruments
    When method workflow is requested
    Then IV has readiness_status "blocked"
    And blockers include "instrument_required"

  Scenario: Method workflow binds to RunPlan
    Given the user selects method "DID" in RunPlan
    And DID readiness_status is "blocked"
    When the user saves RunPlan
    Then the RunPlan saves as "draft" or "blocked"
    And full execution remains unavailable
```

- [ ] **Step 2: Write failing tests**

Create these tests:

```text
MethodWorkflowChecklistTests.test_bdd_1_ols_ready_when_outcome_and_treatment_exist
- Arrange approved VariableRoleSet with outcome and treatment.
- Call GET /method-workflows.
- Assert OLS readiness_status is ready and diagnostics include coefficient_table.

MethodWorkflowChecklistTests.test_bdd_2_did_blocked_without_panel_time_and_treatment_timing
- Arrange approved VariableRoleSet without time variable or treatment timing.
- Call GET /method-workflows.
- Assert DID blockers include time_variable_required and treatment_timing_required.

MethodWorkflowChecklistTests.test_bdd_3_iv_blocked_without_instruments
- Arrange approved VariableRoleSet with no instruments.
- Call GET /method-workflows.
- Assert IV blocker includes instrument_required.

MethodWorkflowChecklistTests.test_bdd_4_blocked_method_cannot_be_approved_for_run_plan
- Attempt to save RunPlan with method=DID and status=approved while DID is blocked.
- Assert response is 409 method_workflow_blocked or saved state is blocked.

MethodWorkflowChecklistTests.test_bdd_5_frontend_shows_method_workflow_requirements
- Read frontend files.
- Assert renderMethodWorkflows exists.
- Assert copy includes 查看方法要求 and blocked method blocker display.
```

- [ ] **Step 3: Run RED**

```bash
python3 -m unittest tests.test_method_workflow_checklist -v
```

- [ ] **Step 4: Implement method workflow service**

Expose:

```text
GET /api/v1/projects/{project_id}/method-workflows
```

Return:

```json
{
  "methods": [
    {
      "method": "OLS",
      "readiness_status": "ready",
      "required_inputs": ["outcome", "treatment"],
      "required_diagnostics": ["sample_size", "missingness", "coefficient_table", "residual_diagnostics"],
      "blockers": []
    },
    {
      "method": "DID",
      "readiness_status": "blocked",
      "required_inputs": ["outcome", "treatment", "unit_id", "time_variable", "treatment_timing"],
      "required_diagnostics": ["parallel_trends", "event_study", "sensitivity_analysis", "heterogeneous_treatment_effects"],
      "blockers": ["time_variable_required", "treatment_timing_required"]
    }
  ]
}
```

- [ ] **Step 5: Enforce RunPlan method readiness**

When saving RunPlan:

```text
approved + blocked method -> reject or downgrade to blocked with explanation
approved + ready method -> allow
```

Prefer explicit 409 response if user tries to approve a blocked method:

```json
{
  "detail": {
    "error": "method_workflow_blocked",
    "blockers": ["time_variable_required"]
  }
}
```

- [ ] **Step 6: Frontend**

Execution / Design page must show method workflow cards:

```text
OLS：可执行
DID：缺少时间变量、处理时点
IV：缺少工具变量
RDD：缺少断点运行变量
PSM：可预检
DML：可预检
```

Details folded by default:

```text
查看方法要求
```

- [ ] **Step 7: Verify**

```bash
python3 -m unittest tests.test_method_workflow_checklist tests.test_method_skill_catalog tests.test_design_run_plan_state_machine -v
python3 -m unittest discover -s tests -v
python3 -m py_compile Product/app.py Product/backend/method_workflow_service.py Product/backend/design_spec_service.py Product/backend/overview_service.py
node --check Product/web/assets/app.js
git diff --check
```

- [ ] **Step 8: Browser acceptance**

Open:

```text
http://127.0.0.1:8768/?v=20260517-p2x-method-workflow
```

Acceptance:

```text
Execution shows method workflows.
OLS ready state is visible.
DID/IV/RDD show explicit blockers.
Blocked methods cannot be saved as approved RunPlan.
No fake local_execution evidence is shown for blocked methods.
```

- [ ] **Step 9: Commit**

Subject:

```text
Make empirical methods executable only through readiness checklists
```

---

## 7. Task P2-Y: Reviewer Scorecard And Follow-Up Task Suggestions

**Goal:** Convert AI/reviewer critique into structured scores and actionable follow-up tasks.

**Business rule:** A reviewer comment is not product state unless it is structured, scored, bound to evidence, and can produce follow-up tasks.

**Files:**
- Create: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/docs/architecture-v2/codex-phase-p2-reviewer-scorecard-bdd.md`
- Create: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/tests/test_reviewer_scorecard.py`
- Create: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/reviewer_score_service.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/results_draft_service.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/agent_task_queue_service.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/app.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/web/assets/app.js`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/web/assets/styles.css`

### BDD cases

- [ ] **Step 1: Write BDD doc**

```gherkin
Feature: Reviewer Scorecard

  Scenario: Reviewer scorecard requires a successful full run
    Given there is no successful full run
    When the user requests reviewer scorecard
    Then the API returns 409 "full_run_required"

  Scenario: Scorecard evaluates finding and design dimensions
    Given a successful full run and FindingCard exist
    When the user generates a reviewer scorecard
    Then the scorecard includes novelty, identification_credibility, data_quality, clarity, and policy_relevance
    And each dimension has score, rationale, evidence binding, and suggested tasks

  Scenario: Low identification credibility creates follow-up task suggestions
    Given identification_credibility score is below 6
    When the scorecard is saved
    Then suggested tasks include method diagnostics or robustness checks
    And tasks are not added to Agent Task Queue until human accepts them

  Scenario: Frontend shows scorecard before manuscript export
    Given a scorecard exists
    When Review & Export renders
    Then scores are visible as compact rows
    And rationales and suggested tasks are folded by default
```

- [ ] **Step 2: Write failing tests**

```text
ReviewerScorecardTests.test_bdd_1_scorecard_requires_successful_full_run
- Arrange a project without successful full-run evidence.
- Call GET or POST reviewer-scorecard.
- Assert response is 409 full_run_required.

ReviewerScorecardTests.test_bdd_2_scorecard_has_five_dimensions_with_evidence
- Arrange latest successful full run and FindingCard.
- Call POST reviewer-scorecard.
- Assert five dimensions exist: novelty, identification_credibility, data_quality, clarity, policy_relevance.
- Assert each dimension includes score, rationale, evidence, and suggested_tasks.

ReviewerScorecardTests.test_bdd_3_low_score_creates_follow_up_task_suggestions_not_queue_mutations
- Arrange deterministic scorecard with identification_credibility below 6.
- Assert suggested_tasks are returned.
- Assert agent_task_queue.json is unchanged.

ReviewerScorecardTests.test_bdd_4_frontend_shows_compact_scorecard_with_folded_details
- Read frontend files.
- Assert scorecard panel exists in Review & Export.
- Assert rationales and suggested tasks are inside details/summary.
```

- [ ] **Step 3: Run RED**

```bash
python3 -m unittest tests.test_reviewer_scorecard -v
```

- [ ] **Step 4: Implement scorecard service**

Add:

```text
GET /api/v1/projects/{project_id}/reviewer-scorecard
POST /api/v1/projects/{project_id}/reviewer-scorecard
```

State file:

```text
state/product/reviewer_scorecard.json
```

Scorecard shape:

```json
{
  "status": "needs_review",
  "evidence_level": "local_file",
  "source_run_id": "run_x",
  "dimensions": [
    {
      "id": "identification_credibility",
      "label": "识别可信度",
      "score": 5.2,
      "rationale": "当前只有 OLS，缺少因果识别增强。",
      "evidence": ["state/product/run_plan.json", "Results/json/analysis_result.json"],
      "suggested_tasks": [
        {
          "id": "add_parallel_trends_if_did",
          "label": "如果升级 DID，补平行趋势检验",
          "target_agent": "Design Agent",
          "requires_human_acceptance": true
        }
      ]
    }
  ]
}
```

If no real LLM reviewer is enabled, deterministic baseline evaluator is allowed, but must say:

```json
"reviewer_backend": "deterministic_baseline",
"evidence_level": "local_file"
```

Do not claim `local_execution` unless an actual reviewer backend ran.

- [ ] **Step 5: Frontend**

Review & Export page:

```text
审稿评分
新颖性 6.0
识别可信度 5.2
数据质量 7.0
表达清晰度 6.5
政策相关性 5.8
```

Each row details:

```text
查看理由与后续任务
```

Suggested task button:

```text
加入任务队列草案
```

This button must create a proposed task only after explicit human click; it must not mutate the existing queue automatically.

- [ ] **Step 6: Verify**

```bash
python3 -m unittest tests.test_reviewer_scorecard tests.test_results_draft_evidence_binding tests.test_review_export_package -v
python3 -m unittest discover -s tests -v
python3 -m py_compile Product/app.py Product/backend/reviewer_score_service.py Product/backend/results_draft_service.py Product/backend/agent_task_queue_service.py
node --check Product/web/assets/app.js
git diff --check
```

- [ ] **Step 7: Browser acceptance**

Open:

```text
http://127.0.0.1:8768/?v=20260517-p2y-reviewer-scorecard
```

Acceptance:

```text
Review & Export shows score rows.
Details are folded.
Low-score suggestions are visible only after expansion.
No task is added to queue until user clicks explicit action.
```

- [ ] **Step 8: Commit**

Subject:

```text
Turn reviewer critique into scored evidence and follow-up tasks
```

---

## 8. Task P2-Z: Verifier Gates For Results, Manuscript, And Export

**Goal:** Add explicit verifier checks before export or write-back can be considered safe.

**Business rule:** A paper package is not export-ready just because a draft exists. It must pass result binding, reproducibility, citation, and docx/export preflight checks.

**Files:**
- Create: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/docs/architecture-v2/codex-phase-p2-verifier-export-gates-bdd.md`
- Create: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/tests/test_verifier_export_gates.py`
- Create: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/verifier_service.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/backend/manuscript_candidate_service.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/app.py`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/web/assets/app.js`
- Modify: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Product/web/assets/styles.css`

### BDD cases

- [ ] **Step 1: Write BDD doc**

```gherkin
Feature: Verifier Export Gates

  Scenario: Export verifier requires approved manuscript candidate
    Given no manuscript candidate is approved for export
    When the user requests verifier checks
    Then the API returns 409 "export_candidate_required"

  Scenario: Verifier checks result binding
    Given a ready_for_export manuscript candidate exists
    When verifier checks run
    Then every claim in the candidate maps to a FindingCard and result artifact
    And missing bindings are marked failed

  Scenario: Verifier checks reproducibility package
    Given export package manifest exists
    When verifier checks run
    Then manifest, run_plan, analysis_result, method_execution_result, and draft preview are checked
    And each check has passed/failed status and artifact path

  Scenario: Docx export preflight remains blocked until checks pass
    Given verifier checks contain failures
    When the user opens Review & Export
    Then docx export is disabled
    And the failed checks are visible before any export action
```

- [ ] **Step 2: Write failing tests**

```text
VerifierExportGatesTests.test_bdd_1_verifier_requires_export_candidate
- Arrange no ready_for_export manuscript candidate.
- Call GET or POST verifier-checks.
- Assert response is 409 export_candidate_required.

VerifierExportGatesTests.test_bdd_2_verifier_checks_result_binding
- Arrange ready_for_export candidate and FindingCard evidence.
- Run verifier checks.
- Assert result_binding check passes when artifact paths exist.

VerifierExportGatesTests.test_bdd_3_verifier_checks_reproducibility_package_artifacts
- Arrange export package manifest with required artifacts.
- Run verifier checks.
- Assert manifest, run_plan, analysis_result, method_execution_result, and draft preview checks exist.

VerifierExportGatesTests.test_bdd_4_docx_export_blocked_until_verifier_passes
- Arrange one failed verifier check.
- Assert can_export_docx is false.
- Assert docx export preflight status is blocked.

VerifierExportGatesTests.test_bdd_5_frontend_shows_verifier_gates_before_export_actions
- Read frontend files.
- Assert verifier gate panel appears before export action markup.
- Assert failed checks are visible and export button disabled state is driven by can_export_docx.
```

- [ ] **Step 3: Run RED**

```bash
python3 -m unittest tests.test_verifier_export_gates -v
```

- [ ] **Step 4: Implement verifier service**

Add:

```text
GET /api/v1/projects/{project_id}/verifier-checks
POST /api/v1/projects/{project_id}/verifier-checks/run
```

State file:

```text
state/product/verifier_checks.json
```

Check IDs:

```text
result_binding
repro_manifest
method_execution_artifact
draft_preview_exists
evidence_levels_valid
docx_export_preflight
```

Response shape:

```json
{
  "status": "failed",
  "can_export_docx": false,
  "checks": [
    {
      "id": "result_binding",
      "label": "结果绑定",
      "status": "passed",
      "evidence_level": "local_file",
      "artifact_paths": ["Results/json/analysis_result.json"]
    }
  ]
}
```

- [ ] **Step 5: Frontend**

Review & Export page:

```text
验证闸门
结果绑定：通过
复现清单：通过
方法执行产物：通过
草稿预览：通过
证据等级：通过
docx 导出预检：阻断
```

Docx export button must stay disabled unless:

```text
can_export_docx=true
```

- [ ] **Step 6: Verify**

```bash
python3 -m unittest tests.test_verifier_export_gates tests.test_review_export_package tests.test_manuscript_consumption -v
python3 -m unittest discover -s tests -v
python3 -m py_compile Product/app.py Product/backend/verifier_service.py Product/backend/manuscript_candidate_service.py
node --check Product/web/assets/app.js
git diff --check
```

- [ ] **Step 7: Browser acceptance**

Open:

```text
http://127.0.0.1:8768/?v=20260517-p2z-verifier-gates
```

Acceptance:

```text
Review & Export shows verifier gate rows before export actions.
Failed checks are visible.
docx export is disabled unless all required checks pass.
No source draft is overwritten.
Console error count is 0.
```

- [ ] **Step 8: Commit**

Subject:

```text
Block manuscript export behind explicit verifier gates
```

---

## 9. Integration Milestone: AI Research Pipeline MVP Review

After P2-V through P2-Z are complete, run this milestone before moving to real StataMCP or broader method execution.

- [ ] **Step 1: Run complete regression**

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile Product/app.py Product/backend/*.py
node --check Product/web/assets/app.js
git diff --check
```

- [ ] **Step 2: Start app**

```bash
python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8768
```

- [ ] **Step 3: Browser end-to-end manual flow**

Open:

```text
http://127.0.0.1:8768/?v=20260517-pipeline-mvp-review
```

Manual acceptance path:

```text
1. Home shows topic-first entry.
2. ResearchQuestion is confirmed or restored.
3. SupervisorPlan panel explains whether Codex execution is enabled.
4. SupervisorPlan cannot dispatch until approved.
5. Agent Task Queue shows summary-first tasks.
6. A task can be dispatch-reviewed without executing.
7. Data & Variables separates candidate suggestions from formal VariableRoleSet.
8. Method workflows show OLS ready and blocked methods with reasons.
9. Results & Draft shows Findings and manuscript candidates with provenance.
10. Review & Export shows reviewer scorecard and verifier gates.
```

- [ ] **Step 4: Record screenshots**

Save screenshots into:

```text
artifacts/ui-checks/pipeline-mvp-home.png
artifacts/ui-checks/pipeline-mvp-data-variables.png
artifacts/ui-checks/pipeline-mvp-execution.png
artifacts/ui-checks/pipeline-mvp-review-export.png
```

- [ ] **Step 5: Update handoff**

Update:

```text
Tasks/current-stage.md
Tasks/todo.md
Tasks/handoff.md
Tasks/manifest.md
Tasks/decision-log.md
Tasks/review.md
```

Include:

```text
当前目标
已完成事项
已验证证据
关键文件路径
不能重复探索的结论
下一步第一件事
未解决风险
```

- [ ] **Step 6: Final commit and push**

Use Lore format and push:

```bash
git status --short --branch
git add Product app.py Product/backend Product/web tests docs/architecture-v2 Tasks docs/superpowers/plans/2026-05-17-agent-task-queue-to-ai-research-pipeline-mvp.md
git commit -m "Advance the empirical workbench through audited research pipeline gates" -m "The pipeline now keeps AI planning, dispatch review, method readiness, reviewer scoring, and export verification as explicit human-visible state transitions." -m "Constraint: Formal research state can only change through explicit approved APIs and visible UI actions.
Rejected: Let approved SupervisorPlan directly execute all sub agent tasks | dispatch audit and method readiness must remain separate gates.
Rejected: Treat heuristic variable candidates as formal evidence | candidates must be promoted into editable VariableRoleSet state before analysis.
Confidence: high
Scope-risk: broad
Directive: Preserve summary-first UI and do not hide state mutations inside LLM or worker execution.
Tested: python3 -m unittest discover -s tests -v; python3 -m py_compile Product/app.py Product/backend/*.py; node --check Product/web/assets/app.js; git diff --check; browser acceptance on the current localhost URL.
Not-tested: Cloud upload runtime and real StataMCP execution unless specifically completed in a later task." -m "Co-authored-by: OmX <omx@oh-my-codex.dev>"
git push
git status --short --branch
```

---

## 10. What This Plan Explicitly Does Not Do Yet

These are not forgotten; they are deliberately held until the MVP pipeline is stable.

- It does not enable autonomous sub-agent execution by default.
- It does not call real Codex Supervisor unless `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1` is explicitly set during a controlled acceptance run.
- It does not claim DID / IV / RDD / PSM / DML are real execution backends until they produce logs, results, diagnostics, and reproducible artifacts.
- It does not overwrite `Manuscripts/generated/paper_draft.md`.
- It does not upload local user data to a cloud runtime.
- It does not implement online SaaS upload flow; local and cloud editions remain separate.
- It does not make heuristic variable candidates acceptable as formal research evidence.

---

## 11. Definition Of Done

This plan is complete only when all of the following are true:

- [ ] P2-V through P2-Z tests exist and pass.
- [ ] Full regression passes.
- [ ] Browser acceptance has been performed in the Codex in-app browser.
- [ ] No visible page defaults to showing all high-noise details at once.
- [ ] All new product state is persisted to explicit JSON artifacts.
- [ ] All state mutations have human-visible actions.
- [ ] Queue, reviewer, verifier, and method workflow objects do not silently mutate formal research state.
- [ ] `Tasks/*.md` handoff files are updated.
- [ ] Changes are committed with Lore format and pushed to GitHub.
