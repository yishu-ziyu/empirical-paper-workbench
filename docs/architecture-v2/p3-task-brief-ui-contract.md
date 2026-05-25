# P3 Task Brief UI Contract

Date: 2026-05-25
Status: draft contract for Kimi / frontend design pass

## Purpose

The task brief page is the first screen after the user submits a research topic. Its job is not to show all system capabilities. Its job is to help the user confirm the research task before recursive search, variable discovery, method design, or execution begins.

This page must feel like a clean research intake checkpoint, not a dashboard.

## Ownership Boundary

Codex owns:

- Product information architecture.
- Interaction contract.
- Data contract.
- State transitions.
- API wiring.
- Tests and verification.

Kimi / frontend designer owns:

- High-fidelity visual design.
- Layout polish.
- Motion details.
- Typography and spacing.
- Component skinning.

The current React demo is a low-fidelity behavior slice only. Do not copy its visual style as final design.

## Confirmed Interaction Decisions

1. The first post-submit stage is `Task Brief`.
2. Semantic analysis cards are not the first stage.
3. Desktop uses a fixed right Inspector.
4. Mobile uses a drawer Inspector.
5. Clicking a main signal highlights the corresponding Inspector item.
6. Main signal cards should not expand into long detail blocks on the main canvas.
7. High-noise details stay in Inspector or drawer.
8. The page only writes draft/session state unless the user explicitly confirms a formal transition.

## Main Canvas

The main canvas should show only the minimum signals needed for user judgment:

- Research topic.
- Research boundary.
- Data clue.
- Method inclination.
- Next step.

Each signal should support:

- default summary state,
- hover affordance,
- focus state,
- selected state,
- empty/unknown state,
- warning state when evidence is insufficient.

The main canvas must not show:

- raw JSON,
- full logs,
- cost traces,
- agent tool calls,
- long risk explanations,
- implementation caveats,
- defensive copy about what the demo cannot do.

## Right Inspector

Desktop:

- Fixed right panel.
- Visible by default after topic submission.
- Contains collapsible sections.
- Highlight the section linked to the selected main signal.

Mobile:

- Hidden by default.
- Opens as drawer.
- Drawer trigger should be visible but not dominant.

Inspector sections:

- Evidence requirements.
- Risks.
- Formal layer boundary.
- Dispatch notes.

Each section should support:

- collapsed default,
- expanded detail,
- selected highlight,
- loading state,
- empty state,
- error state.

## State Contract

`TaskBriefDraft`:

```json
{
  "topic": "string",
  "boundary": {
    "summary": "string",
    "status": "empty|draft|needs_review|ready"
  },
  "data_clue": {
    "summary": "string",
    "evidence_level": "mock|local_file|local_execution|external_source|unknown",
    "status": "empty|draft|needs_review|ready"
  },
  "method_inclination": {
    "summary": "string",
    "method_family": "OLS|DID|IV|RDD|PSM|DML|unknown",
    "status": "empty|draft|needs_review|ready"
  },
  "next_step": {
    "label": "string",
    "target_stage": "recursive_search|data_variables|method_design|execution_experiment"
  },
  "inspector": {
    "evidence_requirements": [],
    "risks": [],
    "formal_boundary": [],
    "dispatch_notes": []
  }
}
```

## API Contract Direction

Initial implementation can derive the draft locally from the submitted topic. The next functional implementation should bind this to:

- `TopicSession`,
- `ResearchQuestionDraft`,
- `SupervisorPlanDraft`,
- audit events for selection and stage transition.

No API should silently promote this draft into:

- formal ResearchQuestion,
- VariableRoleSet,
- DesignSpec,
- RunPlan,
- Finding,
- Manuscript.

Promotion requires explicit user review.

## Acceptance Criteria

- After topic submission, the task brief page appears before all analysis cards.
- The main canvas contains only five decision signals.
- Inspector contains evidence, risk, formal boundary, and dispatch details.
- Selecting a main signal highlights the linked Inspector section.
- Desktop shows fixed Inspector.
- Mobile uses drawer Inspector.
- The page does not include defensive demo copy.
- The page does not show raw logs or JSON by default.
- The page does not write formal research state.

## Next Grill-Me Decision

Decide what happens after the user accepts the task brief:

- Option A: enter recursive research search first.
- Option B: enter data and variable discovery first.
- Option C: ask Supervisor to generate a staged plan first.

Recommended: Option C. The Supervisor should generate a staged plan before recursive search or variable discovery, because it can decide whether the topic needs literature-first, data-first, or method-first exploration.

Confirmed: Option C. After the user accepts the task brief, the product should enter `SupervisorPlan` generation first. The SupervisorPlan decides whether the next branch is literature-first, data-first, method-first, or execution-precheck-first.
