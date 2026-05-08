# Agent Cluster Workflow Development Progress

Date: 2026-05-08

## Current Position

This document records the development progress for turning the screenshot-style "Agent 集群 / 10 个并行任务" interface into a concrete workflow inside this empirical-paper workbench.

The target is not a generic chat UI. The intended product surface is a research workflow orchestrator:

- User enters one research goal.
- The system decomposes it into multiple research dimensions.
- Specialized sub-agents run in parallel.
- Each sub-agent has visible status, progress, hover details, and artifacts.
- A supervisor agent synthesizes the outputs into a final research package.
- The final package can be written back into the existing empirical-paper project structure.

## Existing Foundation in This Project

The project already has enough structure to support a first implementation:

- `Product/app.py` already provides a FastAPI product shell.
- `Product/backend/orchestrator.py` already contains an orchestration direction.
- `Product/backend/orchestration_schema.py` already has handoff/review schema concepts.
- `Product/state/projects.json` already tracks multiple projects.
- `Product/web/index.html` already hosts the product UI.
- `Program/run_paper.py` and `Program/export_docx.py` already prove the analysis-to-draft-to-docx path.
- `Results/`, `Manuscripts/`, `Submissions/`, `docs/`, `Tasks/`, and `state/` already provide durable artifact locations.

The existing product shell is therefore a suitable base. The next step should extend it, not start a separate prototype elsewhere.

## Target User Experience

The target interface should behave like this:

1. The user enters a research goal, for example:

   `研究工业机器人应用对劳动力市场匹配效率的影响，目标是形成可执行的本科论文实证设计。`

2. The system creates a workflow and displays:

   `现在创建研究 Agent 并并行部署 10 个维度的深度研究。`

3. The UI shows an `Agent 集群` panel with 6 to 10 research tasks.

4. Each row displays:

   - Agent avatar
   - Agent name
   - Research dimension number
   - Task title
   - Current one-line status
   - Progress indicator
   - Task sequence number

5. Hovering a row opens a details card with:

   - Agent role
   - Research dimension
   - Full task description
   - Research scope
   - Current status
   - Outputs already written
   - Evidence gaps or blockers

6. After all child agents finish, the supervisor produces:

   - A comprehensive research report
   - A literature/evidence matrix
   - A data-readiness note
   - An identification-design memo
   - A paper outline
   - A next-action checklist

7. The completion card lets the user open, export, or sync the outputs into the project workspace.

## Recommended Research Dimensions for the Economics Thesis Workflow

The first workflow template should be named:

`empirical_thesis_deep_research`

Default child tasks:

1. `研究背景与政策语境`
2. `文献综述与研究缺口`
3. `数据源与变量可得性`
4. `核心变量定义与测度`
5. `识别策略与内生性处理`
6. `基准模型与估计方案`
7. `稳健性检验设计`
8. `异质性与机制分析`
9. `表格图形与结果呈现`
10. `论文结构与写作路径`

For the current robot/labor-market direction, these dimensions map naturally to the registered external source pools:

- `/Users/mahaoxuan/Desktop/实证数据库`
- `/Users/mahaoxuan/Zotero`
- `/Users/mahaoxuan/Desktop/论文核心素材库/1_文献/PDF原文`

The workflow should register and inspect source roots first. It should not copy or mutate raw sources until the topic and dataset subset are narrowed.

## Proposed Data Model

The MVP can use JSON files instead of a database.

Recommended state folder:

`Product/state/workflows/`

Suggested files:

- `Product/state/workflows/<workflow_id>/workflow.json`
- `Product/state/workflows/<workflow_id>/tasks/<task_id>.json`
- `Product/state/workflows/<workflow_id>/artifacts.json`
- `Product/state/workflows/<workflow_id>/events.jsonl`
- `Product/state/workflows/<workflow_id>/final_report.md`

### Workflow JSON

```json
{
  "id": "wf_20260508_001",
  "slug": "robot_labor_match_deep_research",
  "title": "工业机器人应用对劳动力市场匹配效率的影响",
  "template": "empirical_thesis_deep_research",
  "status": "running",
  "phase": "parallel_research",
  "progress": 0.42,
  "agent_count": 10,
  "created_at": "2026-05-08T00:00:00+08:00",
  "updated_at": "2026-05-08T00:00:00+08:00"
}
```

### Agent Task JSON

```json
{
  "id": "task_05",
  "workflow_id": "wf_20260508_001",
  "agent_name": "维农",
  "role": "识别策略研究员",
  "dimension": "识别策略与内生性处理",
  "status": "running",
  "progress": 0.8,
  "summary": "正在比较 Bartik IV、DID 和固定效应模型",
  "research_scope": [
    "OLS 基准模型",
    "Bartik 工具变量",
    "行业-地区面板固定效应",
    "潜在内生性来源",
    "安慰剂与稳健性检验"
  ],
  "outputs": [
    "docs/workflows/wf_20260508_001/identification_design.md"
  ]
}
```

### Artifact JSON

```json
{
  "id": "artifact_001",
  "workflow_id": "wf_20260508_001",
  "task_id": "task_05",
  "kind": "markdown",
  "path": "docs/workflows/wf_20260508_001/identification_design.md",
  "title": "识别策略设计",
  "created_by": "task_05",
  "status": "ready"
}
```

## Backend Development Plan

### Phase 1: State and API Skeleton

Goal: create a real workflow object and return mock agent tasks.

Files to add or extend:

- `Product/backend/workflow_service.py`
- `Product/backend/agent_task_service.py`
- `Product/backend/artifact_service.py`
- `Product/backend/workflow_schema.py`
- `Product/app.py`

API endpoints:

- `POST /api/workflows`
- `GET /api/workflows`
- `GET /api/workflows/{workflow_id}`
- `POST /api/workflows/{workflow_id}/start`
- `GET /api/workflows/{workflow_id}/tasks`
- `GET /api/workflows/{workflow_id}/artifacts`
- `POST /api/workflows/{workflow_id}/export`

Verification:

- Creating a workflow writes JSON under `Product/state/workflows/`.
- Listing workflows returns the created workflow.
- Getting tasks returns 10 structured child tasks.
- No project data or raw source files are mutated.

### Phase 2: Simulated Parallel Agent Execution

Goal: make the UI feel like the screenshot before wiring real agents.

Implementation:

- Start each task in `queued`.
- Advance tasks through deterministic states:
  - `queued`
  - `planning`
  - `researching`
  - `synthesizing`
  - `completed`
- Write task events to `events.jsonl`.
- Generate one markdown artifact per task.
- Generate one supervisor summary after all tasks finish.

Verification:

- Refreshing the page shows persisted progress.
- Completed tasks keep their outputs.
- A workflow can be resumed from disk after server restart.

### Phase 3: Real Research Workflow Binding

Goal: replace simulated task output with real local research operations.

Initial real bindings:

- Literature/source inventory from registered roots.
- Topic memo generation under `docs/workflows/<workflow_id>/`.
- Data-readiness memo from known dataset folders.
- Identification-design memo using StatsPAI method vocabulary.
- Paper-outline draft under `Manuscripts/generated/` or `docs/workflows/`.

Verification:

- Outputs cite concrete local paths inspected during the run.
- The workflow produces durable markdown files.
- The supervisor report identifies gaps instead of inventing missing evidence.

### Phase 4: UI Integration

Goal: build the screenshot-like product surface.

Recommended components:

- `WorkflowHeader`
- `AgentClusterPanel`
- `AgentRow`
- `AgentHoverCard`
- `StageTimeline`
- `ArtifactDrawer`
- `ComposerBar`
- `CompletionCard`

If keeping the current static frontend, these can first be implemented inside `Product/web/index.html` with plain JavaScript and CSS. If the frontend grows, split into `Product/web/app.js` and `Product/web/styles.css`.

Required UI behavior:

- Agent rows are dense and stable in height.
- Hovering a row shows a floating detail card.
- Progress bars reflect task JSON progress.
- Completion card appears only after supervisor synthesis.
- Artifact links open the generated files through backend endpoints.

Verification:

- Browser can show the workflow at `http://127.0.0.1:8765`.
- The agent list is non-empty after creating a workflow.
- Hover details do not overlap the composer bar on desktop-sized screens.
- Text stays inside row/card boundaries.

## Frontend Visual Specification

The interface should stay close to the screenshot:

- White or near-white page background.
- Light border cards.
- Dense list rows.
- Small avatar circles.
- Minimal green progress indicators.
- Hover card width around `360px` to `420px`.
- Row height around `84px` to `96px`.
- Bottom composer fixed to the lower area of the viewport.
- No marketing hero section.
- No decorative gradients or ornamental background blobs.

Suggested statuses:

- `Queued`
- `Planning`
- `Researching`
- `Synthesizing`
- `Reviewing`
- `Completed`
- `Failed`

The status should be visual but not noisy. The main evidence should be the artifact list and the event log.

## Artifact Placement

Recommended output folder:

`docs/workflows/<workflow_id>/`

Expected artifacts:

- `00_workflow_brief.md`
- `01_policy_context.md`
- `02_literature_gap.md`
- `03_data_readiness.md`
- `04_variable_design.md`
- `05_identification_design.md`
- `06_baseline_model_plan.md`
- `07_robustness_plan.md`
- `08_heterogeneity_mechanism.md`
- `09_table_figure_plan.md`
- `10_paper_outline.md`
- `final_research_report.md`
- `next_actions.json`

Later, selected final outputs can be promoted into:

- `Tasks/`
- `Manuscripts/generated/`
- `Results/json/`
- `state/orchestration/`

## Current Status

Completed before this note:

- Empirical-paper workbench structure exists.
- Product shell exists.
- Multi-project registry exists.
- Basic orchestration concepts exist.
- Markdown/LaTeX/docx pipeline exists.
- Source roots have been registered.
- The screenshot-inspired workflow has been translated into a product design.

Completed in this note:

- Target UX was specified.
- Economics-specific 10-dimension workflow was defined.
- JSON state model was drafted.
- Backend API plan was drafted.
- Frontend component plan was drafted.
- Artifact placement policy was drafted.
- Verification criteria were defined.

Not implemented yet:

- Workflow API endpoints.
- Persistent `Product/state/workflows/` runtime.
- Screenshot-like agent cluster UI.
- Hover detail cards.
- Real parallel task execution.
- Supervisor synthesis output.
- Browser verification of the new workflow surface.

## Immediate Next Development Steps

1. Add `workflow_schema.py` and `workflow_service.py`.
2. Add `POST /api/workflows` and `GET /api/workflows/{id}`.
3. Seed the `empirical_thesis_deep_research` template with 10 default tasks.
4. Persist workflows under `Product/state/workflows/`.
5. Extend `Product/web/index.html` with an Agent Cluster panel.
6. Add hover detail cards and progress rendering.
7. Generate mock markdown artifacts for all 10 tasks.
8. Add final synthesis artifact once all tasks complete.
9. Run backend tests.
10. Start the local product server and verify the UI in browser.

## Risks and Constraints

- Do not mutate raw data roots during workflow exploration.
- Do not present mock task outputs as real research evidence.
- Keep the first implementation JSON-backed; avoid adding a database dependency too early.
- Keep the first frontend implementation inside the existing product shell unless complexity forces a split.
- Treat Zotero as bibliographic truth and the PDF folder as a reading pool.
- Treat generated research notes as drafts until reviewed against actual sources.

## Definition of Done for MVP

The MVP is done when:

- A user can create a workflow from one research goal.
- The UI displays 10 child agent rows.
- Each child row has progress and hover details.
- Each child task writes one markdown artifact.
- The supervisor writes `final_research_report.md`.
- The completion card links to all artifacts.
- The workflow survives server restart.
- The product can be opened locally and visually checked.
- The implementation has tests for create/list/get workflow behavior.

