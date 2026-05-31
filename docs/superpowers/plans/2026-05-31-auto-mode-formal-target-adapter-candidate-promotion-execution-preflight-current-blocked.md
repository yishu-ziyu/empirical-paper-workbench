# Auto Mode Formal Target Adapter Candidate Promotion Execution Preflight Current Blocked Record

## Stage

P7-U is the formal target adapter candidate promotion execution preflight gate after P7-T.

User-facing effect: this node tells downstream components whether an effective approval can be turned into a later explicit promotion execute command. In the current run, P7-T is blocked and has no approved promotion plan, so P7-U records a blocked execution preflight and does not create a promotion execution plan.

## BDD Behaviors

### Behavior 1: Effective approval creates execution preflight without promotion

Given P7-T has effective approval
And an approved promotion plan exists
When P7-U runs
Then it creates a promotion execution preflight plan
And still does not promote candidate targets.

Business rule: execution preflight prepares an execute gate; it is not execution.

### Behavior 2: Blocked or ineffective approval blocks execution preflight

Given P7-T is blocked or not approved
When P7-U runs
Then it reports `blocked_by_candidate_promotion_approval`
And creates no promotion execution plan.

Business rule: execution preflight cannot bypass approval.

### Behavior 3: Malformed approved promotion plan blocks preflight

Given P7-T approval is otherwise effective
When approved plan items are missing candidate paths, formal targets, bytes, SHA256, or explicit execute requirements
Then P7-U blocks execution preflight.

Business rule: execute preparation must have complete auditable target evidence.

### Behavior 4: Approval boundary violations block execution preflight

Given P7-T reports a boundary violation
When P7-U runs
Then it blocks execution preflight.

Business rule: unsafe approval output cannot feed promotion execution.

### Behavior 5: CLI defaults to current blocked approval

Given the current P7-T report is blocked
When P7-U CLI runs with default paths
Then it writes blocked execution preflight JSON and Markdown.

Business rule: the command reflects current repo state, not an assumed execution path.

### Behavior 6: Execution preflight writes report and review only

Given P7-U runs in blocked or ready mode
When outputs are written
Then it writes execution preflight JSON and Markdown only
And does not promote candidates, write formal package files, or write product state.

Business rule: preflight is a gate, not the promotion execute command.

## Current Run Boundary

- Current status: `blocked_by_candidate_promotion_approval`.
- Source P7-T status: `blocked_by_candidate_promotion_preflight`.
- Source P7-T approved: `false`.
- Source P7-T decision: `defer`.
- Source P7-T approved promotion plan count: `0`.
- Can request verified candidate promotion execution: `false`.
- Requires explicit promotion execute command: `false`.
- Promotion execution plan count: `0`.
- Candidate targets promoted: `false`.
- Formal target adapters executed: `false`.
- Formal writeback executed: `false`.
- This command wrote formal state: `false`.
- Product state writeback allowed: `false`.
