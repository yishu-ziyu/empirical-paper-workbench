# Auto Mode Formal Target Adapter Promoted Package Verification Current Blocked Record

## Stage

P7-W is the promoted formal package verification gate after P7-V.

User-facing effect: this node tells downstream components whether promoted formal package targets really exist and match the promotion manifest. In the current run, P7-V is blocked and no promotion manifest exists, so P7-W records a blocked verification and does not let export or acceptance begin.

## BDD Behaviors

### Behavior 1: Completed promotion verifies formal targets

Given P7-V completed promotion
And the promotion manifest lists promoted formal targets
When P7-W runs
Then it verifies each formal target by path, byte size, and SHA256.

Business rule: downstream export may start only from a checked formal package, not from claimed writes.

### Behavior 2: Blocked P7-V blocks formal package verification

Given P7-V is blocked
When P7-W runs
Then it reports `blocked_by_candidate_promotion_execute`
And creates no formal target verification records.

Business rule: verification cannot bypass a missing promotion execution.

### Behavior 3: Missing or invalid manifest blocks verification

Given P7-V claims promotion completed
When the promotion manifest is missing or has the wrong schema
Then P7-W blocks verification.

Business rule: formal package verification requires an auditable promotion manifest.

### Behavior 4: Execute report must be completed promotion state

Given P7-V is only dry-run or not completed
When P7-W runs
Then it blocks formal package verification.

Business rule: dry-run is not a formal package write.

### Behavior 5: Missing, changed, or outside formal targets block verification

Given P7-V completed promotion
When a formal target is missing, changed, or outside `Submissions/formal_package/`
Then P7-W blocks verification.

Business rule: the formal package must be reproducible and path-bounded.

### Behavior 6: Boundary violations block verification

Given P7-V or its manifest reports product/render/model side effects
When P7-W runs
Then it blocks verification.

Business rule: package verification cannot hide unrelated write or render side effects.

### Behavior 7: P7-W writes report and review only

Given P7-W runs in any state
When outputs are written
Then it writes verification JSON and Markdown review only
And does not write product state.

Business rule: this node verifies; it does not mutate product or formal package state.

## Current Run Boundary

- Current status: `blocked_by_candidate_promotion_execute`.
- Source P7-V status: `blocked_by_candidate_promotion_execution_preflight`.
- Source P7-V promotion manifest recorded: `false`.
- Source P7-V candidate targets promoted: `false`.
- Source P7-V promotion operations count: `0`.
- Source promotion manifest promoted targets count: `0`.
- Formal package verified: `false`.
- Promoted formal targets verified: `false`.
- Formal target verification records count: `0`.
- Formal writeback executed by this node: `false`.
- This command wrote formal state: `false`.
- Product state writeback allowed: `false`.
- Blocking reasons: `candidate_promotion_execute_not_completed`, `promotion_manifest_not_recorded`, `candidate_targets_not_promoted`, `candidate_promotion_execute_did_not_write_formal_state`, `candidate_promotion_execute_missing_formal_state_write_flag`.
