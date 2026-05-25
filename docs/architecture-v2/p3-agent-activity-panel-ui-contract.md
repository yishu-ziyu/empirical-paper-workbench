# P3 Agent Activity Panel UI Contract

Date: 2026-05-25
Status: draft contract for Kimi / Gemini high-fidelity design and Codex functional wiring

## Purpose

The Agent Activity Panel visualizes what each research agent is doing after a SupervisorPlan has been approved and an Agent Task Queue has been generated.

It should feel like a live research operations inbox: compact, inspectable, and easy to scan. The user should see who is working, what they are doing, what evidence they produced, and whether human review is needed.

## Reference Pattern

The user provided a notification-feed style React component as a useful reference.

We should borrow the pattern, not the literal semantics:

- avatar / identity -> agent identity,
- notification item -> agent activity event,
- tabs -> activity filters,
- unread dot -> needs user attention,
- file card -> artifact / evidence attachment,
- action buttons -> approve / revise / reject / open evidence,
- timestamp / time ago -> audit timeline.

This is not a social notification panel. It is an Agent work ledger.

## Confirmed Automation Stop Point

After the user approves a SupervisorPlan:

1. Create the Agent Task Queue.
2. Let Auto Mode organize and prepare work until the next human gate.
3. Stop before real data / method execution starts.
4. Show the task queue, evidence requirements, risks, and execution readiness.

The first human gate after approval is:

> Confirm whether to start real data and method execution.

This keeps the product simple while preventing accidental regression runs, data writes, or formal claim generation.

## Panel Placement

The Agent Activity Panel should not dominate the first post-topic screens.

Recommended placement:

- Main workspace: visible inside the `Agent Task Queue` / `Agent Console` stage.
- Right Inspector: selected agent / selected task detail.
- Bottom drawer: optional live log stream for advanced inspection.

Do not show this panel on the intake screen.

## Tabs / Filters

Suggested tabs:

- `All` / 全部
- `Needs review` / 待确认
- `Running` / 进行中
- `Blocked` / 阻塞
- `Artifacts` / 有产物

Counts should reflect real queue/activity state.

## Agent Activity Item

Each item should show, collapsed by default:

- agent avatar or role mark,
- agent name,
- action summary,
- task target,
- short status,
- timestamp,
- attention marker if user input is needed.

Expandable detail can show:

- task id,
- input evidence,
- output artifacts,
- blockers,
- risks,
- cost / duration if available,
- audit events,
- tool calls if the user explicitly opens technical details.

## Agent Identity Mapping

Initial agent roles:

- `Supervisor`
- `LiteratureAgent`
- `DataAgent`
- `MethodAgent`
- `ExecutionAgent`
- `ReviewerAgent`
- `ManuscriptAgent`
- `ExportAgent`

Each agent should have:

- short display name,
- role description,
- current task count,
- status,
- latest activity.

## Evidence / Artifact Card

Borrow the file-card pattern from the provided reference component.

Artifact card fields:

```json
{
  "name": "string",
  "path": "string",
  "kind": "dataset_profile|literature_note|method_spec|run_precheck|table|figure|draft|audit_log",
  "evidence_level": "mock|local_file|local_execution|external_source|unknown",
  "size": "string",
  "created_at": "string",
  "open_action": "preview|download|open_in_project|show_provenance"
}
```

The main list should show only name, kind, evidence level, and action. Full provenance stays in Inspector.

## Status Semantics

Allowed activity statuses:

- `queued`
- `running`
- `blocked`
- `needs_review`
- `ready_for_execution`
- `completed_draft`
- `failed`

Do not use social-notification semantics such as `liked`, `followed`, or `mentioned`.

## Human Actions

Allowed actions depend on the task state:

- `open`
- `approve`
- `request_revision`
- `reject`
- `start_execution`
- `pause`
- `view_evidence`
- `view_audit`

Important boundary:

`start_execution` is only available at the human gate after the queue is prepared. It should not appear on every item by default.

## State Contract

`AgentActivityPanel`:

```json
{
  "queue_id": "string",
  "supervisor_plan_id": "string",
  "status": "empty|preparing|needs_review|ready_for_execution|running|blocked|completed_draft|failed",
  "active_filter": "all|needs_review|running|blocked|artifacts",
  "summary": {
    "total": 0,
    "needs_review": 0,
    "running": 0,
    "blocked": 0,
    "artifacts": 0
  },
  "activities": [
    {
      "activity_id": "string",
      "agent": {
        "id": "string",
        "name": "string",
        "role": "string",
        "avatar_fallback": "string"
      },
      "action": "string",
      "target": "string",
      "status": "queued|running|blocked|needs_review|ready_for_execution|completed_draft|failed",
      "summary": "string",
      "timestamp": "string",
      "attention_required": true,
      "artifacts": [],
      "available_actions": []
    }
  ]
}
```

## Empty / Loading / Error States

Empty:

- SupervisorPlan has not been approved.
- Or Agent Task Queue has not been generated.
- Primary action: return to SupervisorPlan Review.

Preparing:

- Show that Auto Mode is organizing queue and checking evidence requirements.
- Do not show fake progress.

Blocked:

- Show blocker summary.
- Let user open Inspector for detail.

Error:

- Show failure reason and retry action.
- Raw stack traces remain hidden by default.

## Acceptance Criteria

- The panel makes agent work visible without becoming a log dump.
- The default list is compact and scan-friendly.
- User attention items are obvious.
- Evidence artifacts are visible but not overwhelming.
- The next human gate is clear: start real data / method execution.
- No formal research state is promoted from this panel without explicit user action.

## Next Grill-Me Decision

Decide what the `start_execution` confirmation should require:

- just one global confirmation,
- or per-stage confirmation for data, method, and manuscript stages.

Recommended: one global confirmation for the MVP, with stage-level pause/reject controls available later if a task becomes blocked or risky.
