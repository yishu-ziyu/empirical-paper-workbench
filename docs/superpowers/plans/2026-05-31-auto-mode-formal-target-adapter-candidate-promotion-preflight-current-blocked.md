# Auto Mode Formal Target Adapter Candidate Promotion Preflight Current Blocked Record

## Stage

P7-S is the formal target adapter candidate promotion preflight gate after P7-R.

User-facing effect: this node tells downstream components whether verified candidate targets can request a separate promotion approval. In the current run, P7-R is blocked and has zero verified target records, so P7-S records a blocked promotion preflight and does not create a promotion plan.

## BDD Behaviors

### Behavior 1: Verified candidates create a promotion preflight plan

Given P7-R has verified candidate target records
When P7-S runs
Then it creates a promotion preflight plan
And requires separate promotion approval and explicit promotion execution.

Business rule: verified candidates may request promotion review, but are not promoted by preflight.

### Behavior 2: Blocked candidate verification blocks promotion preflight

Given P7-R is blocked
When P7-S runs
Then it reports `blocked_by_candidate_verification`
And creates no promotion plan.

Business rule: promotion preflight cannot bypass candidate verification.

### Behavior 3: Missing or invalid verification schema blocks preflight

Given candidate verification is missing or has an invalid schema
When P7-S runs
Then it blocks promotion preflight.

Business rule: promotion planning must be traceable to a valid verification report.

### Behavior 4: Candidate records must be verified and auditable

Given candidate verification is otherwise ready
When a record is unverified, outside `Submissions/auto_mode`, missing SHA256, missing bytes, or mismatched
Then P7-S blocks promotion preflight.

Business rule: only auditable verified records can become promotion plan entries.

### Behavior 5: Boundary violations block preflight

Given P7-R reports a boundary violation
When P7-S runs
Then it blocks promotion preflight.

Business rule: unsafe verification output cannot feed promotion.

### Behavior 6: CLI defaults to current blocked verification

Given the current P7-R report is blocked
When P7-S CLI runs with default paths
Then it writes blocked preflight JSON and Markdown.

Business rule: the command reflects current repo state, not an assumed happy path.

### Behavior 7: Preflight writes report and review only

Given P7-S runs in either blocked or ready mode
When outputs are written
Then it writes preflight JSON and Markdown only
And does not promote candidates, write formal package files, or write product state.

Business rule: preflight is a gate, not an execution step.

## Current Run Boundary

- Current status: `blocked_by_candidate_verification`.
- Source P7-R status: `blocked_by_materialization_execute`.
- Source P7-R candidate targets verified: `false`.
- Source P7-R target verification records count: `0`.
- Can request verified candidate promotion approval: `false`.
- Requires separate promotion approval: `false`.
- Requires explicit promotion execute command: `false`.
- Promotion plan count: `0`.
- Candidate targets promoted: `false`.
- Formal target adapters executed: `false`.
- Formal writeback executed: `false`.
- This command wrote formal state: `false`.
- Product state writeback allowed: `false`.
