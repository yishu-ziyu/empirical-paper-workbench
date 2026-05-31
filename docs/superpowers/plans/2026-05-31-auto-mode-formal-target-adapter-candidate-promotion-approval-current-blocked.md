# Auto Mode Formal Target Adapter Candidate Promotion Approval Current Blocked Record

## Stage

P7-T is the formal target adapter candidate promotion approval gate after P7-S.

User-facing effect: this node records a human decision about whether verified candidates may enter a later promotion execution preflight. In the current run, P7-S is blocked and has no promotion plan, so P7-T records a blocked approval ledger and does not enable candidate promotion.

## BDD Behaviors

### Behavior 1: Ready preflight plus approve records approval without promotion

Given P7-S is ready
And a human records `approve` with reviewer and note
When P7-T runs
Then it records effective approval for the next execution preflight
And still does not promote candidate targets.

Business rule: approval authorizes a later preflight; it is not execution.

### Behavior 2: Defer waits without approving promotion

Given P7-S is ready
When a human records `defer`
Then P7-T records a waiting state
And disables candidate promotion.

Business rule: non-approve decisions cannot start promotion.

### Behavior 3: Blocked promotion preflight blocks approval

Given P7-S is blocked
When P7-T runs with any decision
Then it reports `blocked_by_candidate_promotion_preflight`
And creates no approved promotion plan.

Business rule: human approval cannot bypass missing verified candidate promotion preflight.

### Behavior 4: Approve requires reviewer and note

Given P7-S is ready
When decision is `approve`
But reviewer or note is missing
Then P7-T blocks approval metadata.

Business rule: effective approval must be attributable.

### Behavior 5: Revise and reject do not approve promotion

Given P7-S is ready
When decision is `revise` or `reject`
Then P7-T records the route
And does not enable candidate promotion.

Business rule: revision and rejection are review outcomes, not promotion authorization.

### Behavior 6: CLI defaults to current blocked preflight

Given the current P7-S report is blocked
When P7-T CLI runs with default paths and `defer`
Then it writes blocked approval JSON and Markdown.

Business rule: the command reflects current repo state, not an assumed approval path.

### Behavior 7: Approval writes report and review only

Given P7-T runs in blocked, waiting, rejected, revised, or approved mode
When outputs are written
Then it writes approval JSON and Markdown only
And does not promote candidates, write formal package files, or write product state.

Business rule: approval is a ledger gate, not promotion execution.

## Current Run Boundary

- Current status: `blocked_by_candidate_promotion_preflight`.
- Decision: `defer`.
- Source P7-S status: `blocked_by_candidate_verification`.
- Source P7-S can request verified candidate promotion approval: `false`.
- Source P7-S promotion plan count: `0`.
- Approved: `false`.
- Verified candidate promotion allowed: `false`.
- Can enter verified candidate promotion execution preflight: `false`.
- Approved promotion plan count: `0`.
- Candidate targets promoted: `false`.
- Formal target adapters executed: `false`.
- Formal writeback executed: `false`.
- This command wrote formal state: `false`.
- Product state writeback allowed: `false`.
