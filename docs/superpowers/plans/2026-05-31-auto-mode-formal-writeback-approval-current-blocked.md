# Auto Mode Formal Writeback Approval Current Blocked Record

## Stage

P7-K records whether the package can enter the formal writeback execution preflight.

User-facing effect: this node proves that the product cannot skip from a generated paper package to formal writeback. In the current run, P7-K is blocked because P7-J is not ready.

## BDD Behaviors

### Behavior 1: Ready promotion preflight plus approval only enables execution preflight

Given P7-J reports `ready_for_formal_writeback_approval`
And the human decision is `approve`
And reviewer and note metadata are present
When P7-K runs
Then it records `approved_for_formal_writeback_execution_preflight`
And still does not write formal state.

Business rule: formal writeback approval is only a ledger for the next gate.

### Behavior 2: Defer waits without approval

Given P7-J is ready
When the P7-K decision is `defer`
Then formal writeback remains disabled.

Business rule: waiting is not approval.

### Behavior 3: Blocked P7-J cannot be bypassed

Given P7-J is `blocked_by_final_review_decision`
When P7-K runs
Then it reports `blocked_by_formal_promotion_preflight`
And `formal_writeback_allowed=false`.

Business rule: downstream approval cannot bypass upstream final review.

### Behavior 4: Approve requires reviewer and note

Given P7-J is ready
When P7-K receives `approve` without reviewer or note
Then it blocks approval metadata.

Business rule: writeback approval must be attributable.

### Behavior 5: Revise and reject do not enable writeback

Given P7-J is ready
When P7-K receives `revise` or `reject`
Then it records the route without enabling writeback.

Business rule: negative decisions must never enter execution preflight.

### Behavior 6: P7-K writes only approval records

Given P7-K runs
When it writes outputs
Then it writes JSON and Markdown records only
And does not write formal manuscript, product state, PDF, DOCX, DesignSpec, or RunPlan.

Business rule: this gate is still before actual delivery writeback.

## Current Run Boundary

- Current status: `blocked_by_formal_promotion_preflight`.
- Source P7-J status: `blocked_by_final_review_decision`.
- Approval decision: `defer`.
- Approved: `false`.
- Formal writeback allowed: `false`.
- Can enter formal writeback execution preflight: `false`.
- Current next action: resolve formal promotion preflight blockers.
