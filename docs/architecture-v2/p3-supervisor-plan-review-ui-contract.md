# P3 SupervisorPlan Review UI Contract

Date: 2026-05-25
Status: draft contract for Kimi / Gemini high-fidelity design and Codex functional wiring

## Purpose

`SupervisorPlan Review` is the first control-room page after the user confirms the task brief. It is where the system explains how the research should proceed before any recursive search, data binding, method design, or execution starts.

The user should first judge whether the plan direction is intellectually reasonable, then inspect the stage tree only when needed.

## Confirmed Interaction Decision

Default structure:

1. A single total plan summary is visible first.
2. A multi-stage task tree sits below the summary.
3. The task tree is expandable by stage.
4. The page must support approve / request revision / reject.

Rationale:

- The user first needs to decide whether the plan direction is sound.
- Detailed child tasks are necessary, but should not dominate the first view.
- This page should feel like reviewing a research director's plan, not reading logs.

## Page Model

### Main Canvas

Visible by default:

- Plan title.
- One-sentence research route.
- Recommended first branch: `literature_first | data_first | method_first | execution_precheck_first`.
- Why this branch is recommended.
- Readiness status.
- Primary action: approve plan.
- Secondary actions: request revision, reject.

Below the summary:

- Stage task tree.
- Each stage collapsed by default except the recommended first branch.
- Each stage shows only title, owner, status, and one-line reason when collapsed.

### Right Inspector

Desktop:

- Fixed right Inspector.
- Shows evidence requirements, assumptions, risk, and formal write boundary.

Mobile:

- Drawer Inspector.

Inspector sections:

- Inputs used by Supervisor.
- Key assumptions.
- Evidence required before execution.
- Risks and blocking issues.
- Formal layer boundary.
- Audit trail.

## Stage Tree

Recommended stages:

1. Literature / recursive search.
2. Data and variable discovery.
3. Method design.
4. Execution precheck.
5. Experiment run.
6. Findings review.
7. Manuscript draft.
8. Export and reproducibility.

Each stage node should expose:

- stage id,
- stage title,
- owner agent,
- status,
- rationale,
- required inputs,
- expected outputs,
- evidence requirements,
- blocking conditions,
- estimated cost / time if available.

Do not show raw tool calls or logs in the collapsed tree.

## State Contract

`SupervisorPlanReview`:

```json
{
  "plan_id": "string",
  "topic_session_id": "string",
  "research_question_draft_id": "string",
  "status": "draft|needs_review|approved|needs_revision|rejected",
  "route_summary": "string",
  "recommended_first_branch": "literature_first|data_first|method_first|execution_precheck_first",
  "recommendation_reason": "string",
  "readiness": {
    "label": "string",
    "blocking_count": 0,
    "risk_count": 0
  },
  "stages": [
    {
      "stage_id": "string",
      "title": "string",
      "owner_agent": "Supervisor|LiteratureAgent|DataAgent|MethodAgent|ExecutionAgent|ReviewerAgent|ManuscriptAgent",
      "status": "empty|draft|ready|running|failed|needs_review|approved|deprecated",
      "rationale": "string",
      "required_inputs": [],
      "expected_outputs": [],
      "evidence_requirements": [],
      "blocking_conditions": []
    }
  ],
  "inspector": {
    "inputs_used": [],
    "assumptions": [],
    "evidence_required": [],
    "risks": [],
    "formal_boundary": [],
    "audit_events": []
  },
  "available_actions": ["approve", "request_revision", "reject"]
}
```

## Human Review Actions

Approve:

- Marks the plan as approved.
- Enables Agent Task Queue generation.
- Does not start execution automatically unless a later Auto Mode rule allows it.

Request revision:

- Requires a short human note.
- Keeps the plan out of dispatch.
- Sends the plan back to Supervisor for revision.

Reject:

- Requires a short human note.
- Stops this plan branch.
- Does not delete the audit trail.

## Draft vs Formal Boundary

Approving a SupervisorPlan does not approve:

- final variables,
- final method design,
- run plan,
- findings,
- manuscript claims.

It only approves the research route and allows the next work queue to be generated.

## Empty / Loading / Error States

Empty:

- Shows that task brief is confirmed but no SupervisorPlan exists yet.
- Primary action: generate plan.

Loading:

- Shows Supervisor is drafting the plan.
- Display current phase such as `reading task brief`, `checking data hints`, `choosing first branch`.

Error:

- Shows failure reason.
- Offers retry.
- Keeps task brief available.

No state should show raw stack traces by default.

## Acceptance Criteria

- The first visible object is a total plan summary.
- The stage task tree is present but not visually dominant.
- The recommended first branch is explicit.
- The user can approve, request revision, or reject.
- Approving the plan only enables dispatch; it does not execute analysis silently.
- Risks, assumptions, evidence requirements, and audit events are accessible in Inspector.
- Raw logs and JSON are hidden by default.

## Next Grill-Me Decision

Decide the single automation rule after a SupervisorPlan is approved.

Confirmed simplification principle:

- Do not split the product into two separate local / cloud workflows.
- Build one product flow first.
- Local execution is the first implementation environment.
- Cloud execution should reuse the same product state machine later.
- The difference is infrastructure, not user-facing workflow.

Recommended rule:

After approval, create the Agent Task Queue and let Auto Mode run until the next human gate. The next gate is: confirm whether to start real data and method execution.

Before that gate, Auto Mode may organize tasks, list evidence requirements, expose risks, and prepare execution readiness. It must not run regressions, write formal results, or generate formal claims.

All outputs remain `draft | exploratory | needs_human_review` unless the user explicitly promotes them.
