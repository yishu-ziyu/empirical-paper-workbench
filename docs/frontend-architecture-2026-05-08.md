# Frontend Architecture — Agent Cluster View

Date: 2026-05-08
Scope: `Product/web/` — Agent Cluster UI only
Backend owner: Codex

---

## 1. Current State

The Agent Cluster view (`#view-agent-cluster`) already has a complete visual implementation:

| Component | Status | File |
|-----------|--------|------|
| Workflow header (title, phase, progress, agent count) | ✅ UI ready, mock data | `index.html` + `app.js` |
| Stage timeline (queued → planning → researching → synthesizing → reviewing → completed) | ✅ UI ready, mock-driven | `app.js` |
| Agent row list (avatar, name, dimension, progress bar, status pill) | ✅ UI ready, mock-driven | `app.js` |
| Agent hover card (scope, status, outputs, evidence gaps) | ✅ UI ready, mouse-driven | `app.js` + `styles.css` |
| Artifact drawer (slide-in panel, grouped by agent) | ✅ UI ready, toggle-driven | `app.js` + `styles.css` |
| Completion card (stats, actions: view report, promote, dismiss) | ✅ UI ready, mock-driven | `app.js` + `styles.css` |
| Composer bar (research goal input + start button) | ✅ UI ready, triggers mock | `index.html` + `app.js` |

**What is missing: real API integration.**

The entire Agent Cluster runs on `createMockWorkflow()` + `simulateTaskProgress()` in `app.js`. It does not call any backend API. The other views (Dashboard, Projects, Workflow, Artifacts, Drafts) already call real FastAPI endpoints.

---

## 2. Component Hierarchy

```
AppShell
├── Sidebar (shared, existing)
│   └── Nav: Dashboard | Projects | Workflow | Agent Cluster | Artifacts | Drafts
├── Main
│   ├── TopBar (shared, existing)
│   └── View: Agent Cluster
│       ├── WorkflowHeader
│       │   ├── Title + Subtitle
│       │   └── Meta: Phase | Progress | Agent Count | Artifact Toggle Button
│       ├── StageTimeline
│       │   └── [Dot + Label + Connector Line] × 6 stages
│       ├── AgentClusterPanel
│       │   └── AgentRow × N
│       │       ├── Avatar (colored circle + initial)
│       │       ├── Info (dimension title + agent name + summary)
│       │       ├── Dimension Number
│       │       ├── Progress Bar
│       │       └── Status Pill
│       ├── CompletionCard (conditional)
│       │   ├── Icon
│       │   ├── Stats (completed / artifacts / progress)
│       │   └── Actions (view report | promote | dismiss)
│       ├── ComposerBar (fixed bottom)
│       │   ├── Research Goal Input
│       │   └── Start Button
│       ├── ArtifactDrawer (fixed right, off-screen)
│       │   ├── Header (title + close)
│       │   └── Content (grouped artifact list)
│       └── AgentHoverCard (fixed, absolute positioned, hidden)
│           ├── Header (avatar + name + role)
│           ├── Research Scope (bulleted list)
│           ├── Current Status (label + progress)
│           ├── Outputs (file links)
│           └── Evidence Gaps (conditional bulleted list)
```

---

## 3. State Model (Frontend)

```javascript
const state = {
  // Existing shared state (do not break)
  projects: [],
  selectedProjectId: null,
  selectedProject: null,
  activeRun: null,

  // Agent Cluster state (new)
  workflows: [],              // list of workflow summaries
  selectedWorkflowId: null,   // active workflow
  selectedWorkflow: null,     // full workflow object
  workflowTasks: [],          // array of task objects
  workflowArtifacts: [],      // array of artifact objects
  hoverTaskId: null,          // currently hovered task id
  isArtifactDrawerOpen: false,
  isCompletionVisible: false,
  pollIntervalId: null,
};
```

**Rule:** The existing `projects` / `selectedProject` state must remain functional. Agent Cluster is an additive view, not a replacement.

---

## 4. API Contract Requirements

The frontend expects the following endpoints. Codex should implement these in `Product/backend/`.

### 4.1 Workflow Lifecycle

```
POST /api/v1/workflows
Body: { "title": "string", "project_id": "string?" }
Response: { workflow: Workflow, tasks: Task[] }
```

```
GET /api/v1/workflows
Response: { items: WorkflowSummary[] }
```

```
GET /api/v1/workflows/{workflow_id}
Response: { workflow: Workflow, tasks: Task[], artifacts: Artifact[] }
```

```
POST /api/v1/workflows/{workflow_id}/start
Response: { workflow: Workflow }
```

```
POST /api/v1/workflows/{workflow_id}/cancel
Response: { workflow: Workflow }
```

### 4.2 Task Polling

```
GET /api/v1/workflows/{workflow_id}/tasks
Response: { items: Task[] }
```

```
GET /api/v1/workflows/{workflow_id}/tasks/{task_id}
Response: { task: Task }
```

### 4.3 Artifacts

```
GET /api/v1/workflows/{workflow_id}/artifacts
Response: { items: Artifact[] }
```

```
GET /api/v1/artifacts/{artifact_id}
Response: { artifact: Artifact, content?: string }
```

```
POST /api/v1/artifacts/{artifact_id}/promote
Body: { "target": "manuscripts|results|submissions" }
Response: { artifact: Artifact }
```

### 4.4 Final Report

```
GET /api/v1/workflows/{workflow_id}/report
Response: { content: string, path: string }
```

---

## 5. Data Schemas

### Workflow

```json
{
  "id": "wf_robot_labor_match_001",
  "project_id": "proj_undergraduate_thesis",
  "title": "工业机器人应用对劳动力市场匹配效率的影响",
  "status": "running",
  "phase": "parallel_research",
  "progress": 0.42,
  "agent_count": 10,
  "created_at": "2026-05-08T00:00:00+08:00",
  "updated_at": "2026-05-08T00:00:00+08:00"
}
```

### Task

```json
{
  "id": "task_05",
  "workflow_id": "wf_robot_labor_match_001",
  "agent_name": "维农",
  "role": "识别策略研究员",
  "dimension": "识别策略与内生性处理",
  "dimension_number": 5,
  "status": "researching",
  "progress": 0.65,
  "summary": "正在分析工具变量有效性...",
  "research_scope": [
    "Bartik IV 构造逻辑",
    "排他性约束检验",
    "弱工具变量诊断"
  ],
  "outputs": [
    "docs/workflows/wf_robot_labor_match_001/05_识别策略与内生性处理.md"
  ],
  "evidence_gaps": [],
  "started_at": "2026-05-08T00:01:00+08:00",
  "completed_at": null
}
```

### Artifact

```json
{
  "id": "artifact_task_05_001",
  "workflow_id": "wf_robot_labor_match_001",
  "task_id": "task_05",
  "kind": "markdown",
  "path": "docs/workflows/wf_robot_labor_match_001/05_识别策略与内生性处理.md",
  "title": "识别策略与内生性处理",
  "created_by": "task_05",
  "status": "draft",
  "created_at": "2026-05-08T00:02:00+08:00"
}
```

---

## 6. Frontend Polling Strategy

When a workflow is `running`, the frontend should poll:

```javascript
// Every 3 seconds
const pollWorkflow = async (workflowId) => {
  const { workflow, tasks, artifacts } = await fetchJson(
    `/api/v1/workflows/${workflowId}`
  );
  state.selectedWorkflow = workflow;
  state.workflowTasks = tasks;
  state.workflowArtifacts = artifacts;
  renderAgentCluster();

  if (workflow.status === "completed" || workflow.status === "failed") {
    clearInterval(state.pollIntervalId);
    state.pollIntervalId = null;
    state.isCompletionVisible = true;
  }
};
```

Replace the current `simulateTaskProgress()` interval with this real polling loop.

---

## 7. UI Behavior Spec

### 7.1 Composer Bar

1. User types a research title in the input
2. Clicks "启动研究"
3. Frontend calls `POST /api/v1/workflows` with the title
4. Backend creates workflow + 10 tasks
5. Frontend receives response, stores workflow + tasks
6. Frontend calls `POST /api/v1/workflows/{id}/start`
7. Backend transitions workflow to `running`
8. Frontend starts polling loop

### 7.2 Agent Row Hover

1. Mouse enters an agent row
2. After 200ms debounce, fetch `/api/v1/workflows/{id}/tasks/{task_id}` (or use cached task)
3. Render hover card positioned below the row (or above if overflow)
4. Mouse leaves row → 300ms fade out

### 7.3 Artifact Drawer

1. Click "产物" button in workflow header → slide in from right
2. Groups artifacts by agent (task.dimension + task.agent_name)
3. Click artifact item → open/preview (TBD: modal or new tab)
4. Click backdrop or "关闭" → slide out

### 7.4 Completion Card

1. Appears when all tasks reach `completed` or `failed`
2. Shows: completed count, total artifacts, overall progress
3. Actions:
   - "查看最终报告" → GET `/api/v1/workflows/{id}/report`, render in modal
   - "导出到项目" → POST `/api/v1/artifacts/{id}/promote` for each artifact
   - "关闭" → dismiss card

---

## 8. Codex Implementation Notes

### What Codex Should Implement

1. **Workflow Service** (`Product/backend/workflow_service.py` + `workflow_schema.py`)
   - CRUD for workflows
   - Task lifecycle (queued → planning → researching → synthesizing → reviewing → completed/failed)
   - Progress aggregation

2. **Artifact Service** (`Product/backend/artifact_service.py`)
   - Artifact CRUD
   - Grouping by task
   - Promotion path (workflow → manuscripts/results/submissions)

3. **Task Runner** (mock for Phase 4, real for Phase 5)
   - For Phase 4: a background timer that advances task progress and stages
   - For Phase 5: real agent dispatch or StatsPAI adapter calls

4. **API Routes** in `Product/app.py` or a new router
   - All endpoints listed in Section 4

### What Codex Should NOT Touch

- `Product/web/index.html`
- `Product/web/assets/styles.css`
- `Product/web/assets/app.js` (except adding real API calls in the sections marked below)

### Integration Point

In `app.js`, replace these mock-only functions with real API calls:

```javascript
// REPLACE: createMockWorkflow() + simulateTaskProgress()
// WITH: real POST /api/v1/workflows + polling loop

// REPLACE: startMockWorkflow()
// WITH: async function startWorkflow(title) {
//   const { workflow, tasks } = await fetchJson('/api/v1/workflows', {
//     method: 'POST', body: JSON.stringify({ title })
//   });
//   ...
// }
```

---

## 9. Styling Constraints

The existing CSS uses these design tokens. Codex should not change them.

```css
--bg: #f5f0e7;
--panel: rgba(255, 250, 244, 0.92);
--line: rgba(107, 81, 44, 0.18);
--text: #1b1712;
--muted: #6b5b45;
--accent: #1e6f62;
--accent-2: #a14a18;
```

Font: `"Iowan Old Style", "Palatino Linotype", "Book Antiqua", serif`
Layout: CSS Grid (`300px sidebar + 1fr main`)
Responsive breakpoints: `1100px`, `600px`

---

## 10. Testing Checklist (for Codex)

After implementing backend APIs, verify:

- [ ] `POST /api/v1/workflows` creates workflow + 10 tasks with correct defaults
- [ ] `GET /api/v1/workflows/{id}` returns workflow + tasks + artifacts
- [ ] `POST /api/v1/workflows/{id}/start` changes status to `running`
- [ ] Task progress updates are reflected in `GET` responses
- [ ] All tasks complete → workflow status becomes `completed`
- [ ] Artifacts are grouped correctly in `GET /api/v1/workflows/{id}/artifacts`
- [ ] `POST /api/v1/artifacts/{id}/promote` moves file to correct target directory
- [ ] CORS allows `Product/web/` origin

---

## 11. Files

| File | Role | Owner |
|------|------|-------|
| `Product/web/index.html` | HTML structure | Kimi ✅ |
| `Product/web/assets/styles.css` | Styling | Kimi ✅ |
| `Product/web/assets/app.js` | Frontend logic (mock → real API) | Kimi (hook up) / Codex (provide APIs) |
| `Product/backend/workflow_service.py` | Backend workflow logic | Codex |
| `Product/backend/workflow_schema.py` | Pydantic schemas | Codex |
| `Product/backend/artifact_service.py` | Artifact management | Codex |
| `Product/app.py` | FastAPI routes | Codex |
