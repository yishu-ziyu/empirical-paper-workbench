# Empirical Research OS Architecture

Date: 2026-05-08

## Purpose

This document is the architecture planning record for merging the three local assets under `/Users/mahaoxuan/Desktop/经济学论文` into one coherent empirical research operating system.

The system should not physically merge all repositories into one codebase. The intended architecture is layered integration:

- `实证论文项目模板` is the product host and operating-system shell.
- `StatsPAI` is the empirical method engine.
- `Awesome-Agent-Skills-for-Empirical-Research` is the skill registry and methodology library.

The user explicitly cares about multi-user and multi-agent governance:

- agent identity
- permissions
- capability registration
- output ownership
- cost tracking

These are not later polish. They are first-class architectural requirements.

## Current Repository Roles

### Product Host: `实证论文项目模板`

Path:

`/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`

Role:

- Product shell
- Project/workspace manager
- Workflow runtime
- Artifact and audit ledger
- UI/API host
- Integration layer for StatsPAI, skills, Zotero, PDFs, and datasets

Important files:

- `Product/app.py`
- `Product/backend/project_service.py`
- `Product/backend/orchestrator.py`
- `Product/backend/orchestration_schema.py`
- `Product/backend/run_store.py`
- `Product/backend/registry.py`
- `Product/backend/workbench_paths.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Program/run_paper.py`
- `Program/export_docx.py`
- `Program/workbench/statspai_runner.py`
- `paper.yaml`

This is the main repository for future implementation.

### Method Engine: `StatsPAI`

Path:

`/Users/mahaoxuan/Desktop/经济学论文/StatsPAI`

Role:

- Causal inference and econometrics engine
- Method discovery registry
- Structured tool interface for agents
- Report and result object support

Important interfaces:

- `sp.list_functions()`
- `sp.describe_function()`
- `sp.search_functions()`
- `sp.function_schema()`
- `sp.causal(...)`
- `sp.paper(data, question)`
- `sp.<method>(...)`
- `statspai` CLI
- StatsPAI MCP server

Important files:

- `src/statspai/__init__.py`
- `src/statspai/registry.py`
- `src/statspai/help.py`
- `src/statspai/workflow/causal_workflow.py`
- `src/statspai/workflow/paper.py`
- `src/statspai/agent/mcp_server.py`
- `src/statspai/agent/tools.py`
- `src/statspai/cli.py`
- `pyproject.toml`
- `MIGRATION.md`

StatsPAI should not own product UI, user permissions, project lifecycle, or source governance.

### Skill Registry: `Awesome-Agent-Skills-for-Empirical-Research`

Path:

`/Users/mahaoxuan/Desktop/经济学论文/Awesome-Agent-Skills-for-Empirical-Research`

Role:

- Methodology knowledge base
- Skill registry source
- Workflow template source
- Agent role and checklist source

Important files and folders:

- `README.md`
- `docs/01-选题与研究设计.md`
- `docs/02-文献检索与综述.md`
- `docs/03-论文阅读与拆解.md`
- `docs/04-数据获取与清洗.md`
- `docs/05-统计分析与因果推断.md`
- `docs/06-论文写作.md`
- `docs/07-论文修改与润色.md`
- `docs/08-引用管理与排版.md`
- `docs/09-论文复现与可复现研究.md`
- `docs/10-审稿回复与学术答辩.md`
- `skills/00-StatsPAI_skill/SKILL.md`
- `skills/*/SKILL.md`
- `skills/*/CLAUDE.md`
- `skills/*/dot-claude/agents/*.md`

This repository should not be treated as a runtime execution engine. It supplies structured methodology and role templates.

## Target Product

Working name:

`Empirical Research OS`

Chinese name:

`实证研究操作系统`

Positioning:

An operating system for empirical research that turns one research question into a traceable workflow across source discovery, literature review, data readiness, identification design, empirical estimation, robustness planning, manuscript drafting, review, and export.

Core product promise:

The system does not only answer questions. It creates inspectable research operations:

- who or which agent did what
- what capability was used
- what source was inspected
- what output was produced
- who owns the output
- what it cost
- what remains uncertain

## Architecture Layers

```text
Product UI Layer
  Agent cluster UI, project console, workflow timeline, artifact browser

API and Workflow Layer
  FastAPI routes, workflow service, run store, artifact service, event stream

Governance Layer
  Identity, permissions, capability registry, output ownership, cost tracking

Agent Orchestration Layer
  Supervisor, child agents, handoff packets, review packets, task state machine

Skill Registry Layer
  Awesome skills index, workflow templates, role prompts, checklists

Method Engine Layer
  StatsPAI adapter, function discovery, causal/paper execution, result contracts

Source Registry Layer
  Zotero, PDF library, empirical datasets, uploaded files, source metadata

Workspace and Artifact Layer
  Data, Program, Results, Manuscripts, Submissions, docs, Tasks, state
```

## Governance Requirements

The following five modules should be designed before heavy implementation.

### 1. Identity

The system needs identities for both people and agents.

User identities:

- owner
- collaborator
- reviewer
- viewer
- external advisor

Agent identities:

- supervisor
- literature_agent
- data_agent
- identification_agent
- modeling_agent
- robustness_agent
- writing_agent
- reviewer_agent
- export_agent

Minimum identity fields:

```json
{
  "id": "agent_identification_01",
  "kind": "agent",
  "display_name": "识别策略 Agent",
  "role": "identification_agent",
  "created_by": "user_owner_01",
  "status": "active",
  "capability_profile_id": "cap_identification_v1"
}
```

Recommended backend module:

- `Product/backend/identity_service.py`
- `Product/backend/identity_schema.py`

Recommended state files for JSON-backed MVP:

- `Product/state/identities/users.json`
- `Product/state/identities/agents.json`

### 2. Permissions

Permissions must be action-based, not only role-name based.

Important actions:

- `project.read`
- `project.write`
- `source.register`
- `source.inspect`
- `source.promote`
- `workflow.create`
- `workflow.run`
- `workflow.cancel`
- `agent.spawn`
- `agent.assign`
- `artifact.read`
- `artifact.write`
- `artifact.promote`
- `method.execute`
- `export.docx`

Example permission policy:

```json
{
  "subject_id": "agent_literature_01",
  "subject_kind": "agent",
  "project_id": "proj_undergraduate_thesis",
  "allow": [
    "source.inspect",
    "artifact.write",
    "artifact.read"
  ],
  "deny": [
    "source.promote",
    "method.execute",
    "export.docx"
  ]
}
```

Recommended backend module:

- `Product/backend/permission_service.py`
- `Product/backend/permission_schema.py`

Recommended state files:

- `Product/state/permissions/policies.json`

First implementation rule:

Agents should receive only the permissions needed for their task. For example, a literature agent can inspect Zotero/PDF metadata and write literature notes, but cannot overwrite analysis data or export final docx.

### 3. Capability Registration

Capabilities describe what a human or agent can do.

Capability sources:

- Built-in product actions
- StatsPAI functions
- Awesome skill entries
- Local source tools
- Export tools

Capability registry should normalize:

- capability id
- name
- source repository
- category
- required inputs
- expected outputs
- risk level
- cost model
- allowed roles
- adapter path

Example:

```json
{
  "id": "cap_statspai_causal_did",
  "source": "StatsPAI",
  "category": "causal_inference",
  "name": "DID / causal workflow",
  "entrypoint": "sp.causal",
  "input_contract": "dataset + question + method_hint",
  "output_contract": "result object + summary + diagnostics",
  "risk_level": "medium",
  "allowed_roles": [
    "modeling_agent",
    "robustness_agent"
  ],
  "cost_model": "local_cpu_time"
}
```

Recommended backend modules:

- `Product/backend/capability_registry.py`
- `Product/backend/skill_registry_adapter.py`
- `Product/backend/statspai_adapter.py`

Recommended state files:

- `Product/state/capabilities/capabilities.json`
- `Product/state/capabilities/skill_index.json`
- `Product/state/capabilities/statspai_functions.json`

First implementation rule:

Do not execute every discovered skill. First index it, classify it, and explicitly mark whether it is executable, advisory, or documentation-only.

### 4. Output Ownership

Every output needs an owner, creator, source lineage, and promotion status.

Artifact ownership fields:

```json
{
  "id": "artifact_identification_design_001",
  "project_id": "proj_undergraduate_thesis",
  "workflow_id": "wf_robot_labor_match_001",
  "task_id": "task_identification_05",
  "created_by": "agent_identification_01",
  "owner": "user_owner_01",
  "path": "docs/workflows/wf_robot_labor_match_001/05_identification_design.md",
  "kind": "markdown",
  "status": "draft",
  "promotion_status": "not_promoted",
  "source_lineage": [
    "state/source_registry.json",
    "StatsPAI:sp.describe_function",
    "Awesome:docs/05-统计分析与因果推断.md"
  ],
  "review_status": "pending"
}
```

Artifact statuses:

- `draft`
- `reviewed`
- `accepted`
- `rejected`
- `promoted`
- `archived`

Recommended backend modules:

- `Product/backend/artifact_service.py`
- `Product/backend/ownership_service.py`

Recommended state files:

- `Product/state/artifacts/artifacts.json`
- `Product/state/ownership/ownership_ledger.jsonl`

First implementation rule:

No agent output should overwrite canonical manuscript or final results directly. Agent outputs first go to `docs/workflows/<workflow_id>/` and are promoted only after review.

### 5. Cost Tracking

Cost tracking must include both monetary and non-monetary cost.

Track at least:

- wall-clock time
- CPU/local execution time
- tool invocations
- LLM provider
- model
- token estimate if available
- external API cost if available
- local file reads by source type
- failed/retried runs

Cost event example:

```json
{
  "event_id": "cost_evt_001",
  "project_id": "proj_undergraduate_thesis",
  "workflow_id": "wf_robot_labor_match_001",
  "task_id": "task_literature_02",
  "actor_id": "agent_literature_01",
  "capability_id": "cap_skill_literature_review",
  "event_type": "agent_task_run",
  "started_at": "2026-05-08T00:00:00+08:00",
  "finished_at": "2026-05-08T00:02:10+08:00",
  "wall_seconds": 130,
  "provider": "local",
  "model": null,
  "input_tokens": null,
  "output_tokens": null,
  "estimated_usd": 0.0,
  "status": "succeeded"
}
```

Recommended backend modules:

- `Product/backend/cost_service.py`
- `Product/backend/cost_schema.py`

Recommended state files:

- `Product/state/costs/cost_events.jsonl`
- `Product/state/costs/cost_summary.json`

First implementation rule:

Even if exact token cost is unavailable, every workflow/task should record wall time, actor id, capability id, and status. Exact billing can be added later without changing the core ledger shape.

## Workflow State Model

The workflow runtime should become the central lifecycle surface.

Recommended MVP state root:

`Product/state/workflows/`

Workflow files:

```text
Product/state/workflows/<workflow_id>/
  workflow.json
  tasks/
    task_01.json
    task_02.json
  artifacts.json
  events.jsonl
  cost_events.jsonl
  final_report.md
```

Workflow JSON:

```json
{
  "id": "wf_robot_labor_match_001",
  "project_id": "proj_undergraduate_thesis",
  "title": "工业机器人应用对劳动力市场匹配效率的影响",
  "template": "empirical_thesis_deep_research",
  "created_by": "user_owner_01",
  "supervisor_agent_id": "agent_supervisor_01",
  "status": "running",
  "phase": "parallel_research",
  "progress": 0.42,
  "agent_count": 10,
  "created_at": "2026-05-08T00:00:00+08:00",
  "updated_at": "2026-05-08T00:00:00+08:00"
}
```

Task JSON:

```json
{
  "id": "task_05",
  "workflow_id": "wf_robot_labor_match_001",
  "assigned_agent_id": "agent_identification_01",
  "owner": "user_owner_01",
  "dimension": "识别策略与内生性处理",
  "status": "running",
  "progress": 0.8,
  "capabilities_used": [
    "cap_statspai_function_search",
    "cap_skill_causal_inference"
  ],
  "outputs": [
    "artifact_identification_design_001"
  ],
  "cost_summary": {
    "wall_seconds": 130,
    "estimated_usd": 0.0
  }
}
```

## Product API Modules

The current API should be extended rather than replaced.

Existing core:

- `Product/app.py`
- `Product/backend/project_service.py`
- `Product/backend/run_store.py`
- `Product/backend/orchestrator.py`

Recommended new functional modules:

```text
Product/backend/identity_schema.py
Product/backend/identity_service.py
Product/backend/permission_schema.py
Product/backend/permission_service.py
Product/backend/capability_registry.py
Product/backend/skill_registry_adapter.py
Product/backend/statspai_adapter.py
Product/backend/workflow_schema.py
Product/backend/workflow_service.py
Product/backend/artifact_service.py
Product/backend/ownership_service.py
Product/backend/cost_schema.py
Product/backend/cost_service.py
```

Recommended API resources:

```text
GET  /api/v1/identities
GET  /api/v1/agents
GET  /api/v1/capabilities
POST /api/v1/capabilities/reindex
POST /api/v1/workflows
GET  /api/v1/workflows
GET  /api/v1/workflows/{workflow_id}
POST /api/v1/workflows/{workflow_id}/start
POST /api/v1/workflows/{workflow_id}/cancel
GET  /api/v1/workflows/{workflow_id}/tasks
GET  /api/v1/workflows/{workflow_id}/artifacts
GET  /api/v1/workflows/{workflow_id}/costs
POST /api/v1/artifacts/{artifact_id}/promote
```

## UI Responsibility Boundary

The UI work will be handed to Kimi.

Kimi should receive:

- this architecture document
- the API contract documents
- JSON state examples
- backend endpoint list
- desired screenshot-like behavior

Kimi should own:

- visual layout
- interaction design
- agent cluster panel
- hover cards
- progress display
- artifact drawer
- completion card
- responsive layout

Functional/backend implementation should not depend on Kimi's UI choices. Backend endpoints and state contracts should remain stable.

## Functional Module Responsibility

Functional modules to implement in this project:

1. Identity module
2. Permission module
3. Capability registry module
4. Skill registry adapter
5. StatsPAI adapter
6. Workflow runtime
7. Artifact ownership ledger
8. Cost tracking ledger
9. Source registry integration
10. Export and promotion workflow

These are backend/product responsibilities and should be implemented in `实证论文项目模板`, not inside StatsPAI or Awesome-Agent-Skills.

## Integration Rules

### Do Not Physically Merge Repositories

Keep the three folders separate.

The product repository should reference external capability sources by path and version:

```json
{
  "statspai_path": "/Users/mahaoxuan/Desktop/经济学论文/StatsPAI",
  "skills_path": "/Users/mahaoxuan/Desktop/经济学论文/Awesome-Agent-Skills-for-Empirical-Research"
}
```

### Keep Existing Main Pipeline

Do not break:

```text
paper.yaml -> Program/run_paper.py -> Results -> Manuscripts -> Program/export_docx.py -> Submissions
```

Agent workflow output should first land in:

```text
docs/workflows/<workflow_id>/
```

Only reviewed outputs should be promoted into:

```text
Manuscripts/generated/
Results/
Submissions/
```

### Treat Mock Outputs as Mock

Any simulated child-agent output must be marked as:

```json
{
  "evidence_level": "mock",
  "promotion_status": "blocked"
}
```

### Treat Skills as Advisory Unless Explicitly Executable

Skill registry entries should be classified:

- `advisory`
- `template`
- `role_prompt`
- `checklist`
- `executable`

Only `executable` capabilities may be called by the runtime.

### Treat StatsPAI as an Adapter-Driven Engine

The product should call StatsPAI through a stable adapter, not directly from every service.

Recommended first adapter methods:

- `list_capabilities()`
- `describe_capability(name)`
- `search_capabilities(query)`
- `run_paper(dataset_path, question, config)`
- `run_causal(dataset_path, question, method_hint, config)`

## Implementation Phases

### Phase 0: Architecture and Contracts

Status:

Planned.

Goal:

Create written contracts before implementation.

Deliverables:

- this architecture document
- workflow state spec
- capability registry spec
- StatsPAI adapter spec
- skill registry adapter spec
- governance spec for identity, permissions, ownership, and costs

No runtime implementation in this phase.

### Phase 1: Governance Skeleton

Goal:

Add JSON-backed identity, permission, capability, ownership, and cost ledgers.

Deliverables:

- identity schemas/services
- permission policy checker
- capability registry schema
- ownership ledger
- cost event ledger
- tests for CRUD and permission checks

### Phase 2: Capability Indexing

Goal:

Index Awesome skills and StatsPAI methods without executing them.

Deliverables:

- skill registry adapter
- StatsPAI capability adapter
- capability index JSON
- capability reindex endpoint

### Phase 3: Workflow Runtime

Goal:

Create workflows with assigned agent identities and task state.

Deliverables:

- workflow schema/service
- task state machine
- event ledger
- artifact ledger
- cost event recording

### Phase 4: Mock Agent Cluster

Goal:

Support Kimi's UI with realistic backend state before real agents run.

Deliverables:

- 10 default empirical thesis research tasks
- simulated task progress
- mock artifact generation
- completion report
- strict mock evidence labels

### Phase 5: Real Research Binding

Goal:

Replace selected mock outputs with real source inspection and StatsPAI calls.

Deliverables:

- source registry inspection
- literature/data readiness notes
- StatsPAI method recommendation
- example estimation if data is available
- reviewed promotion path

## Open Decisions

These decisions require explicit approval before implementation:

1. Should the first backend implementation use only JSON files, or should SQLite be introduced early?
2. Should user identities be local-only first, or should they anticipate login/account support?
3. Should cost tracking start with wall time only, or include provider/token fields immediately?
4. Should Kimi receive only UI specs, or also a static mock JSON bundle?
5. Should Phase 1 start before the current uncommitted docs are committed?

## Recommended Approval Scope

Recommended first approval:

Approve Phase 0 and Phase 1 only.

Reason:

The governance modules are foundational. If identity, permissions, ownership, and cost tracking are added later, the workflow runtime will need to be redesigned. Building them first keeps the system honest.

