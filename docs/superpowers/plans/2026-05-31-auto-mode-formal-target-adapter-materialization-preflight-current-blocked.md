# Auto Mode Formal Target Adapter Materialization Preflight Current Blocked Record

## Stage

P7-P is the formal target adapter materialization preflight after P7-O.

User-facing effect: this node tells downstream components whether a recorded target adapter execution manifest can be converted into a materialization plan. In the current run, P7-O is blocked and has not recorded an execution manifest, so P7-P records a blocked preflight and exposes no materialization plan.

## BDD Behaviors

### Behavior 1: Recorded execution manifest supports materialization preflight

Given P7-O has recorded a valid execution manifest
When P7-P runs
Then it reports `ready_for_adapter_materialization_review`
And shows a materialization plan without creating candidate targets.

Business rule: preflight can explain what would be materialized, but it is not materialization.

### Behavior 2: Blocked execution report blocks preflight

Given P7-O is blocked
When P7-P runs
Then it reports `blocked_by_target_adapter_execution`
And exposes no materialization plan.

Business rule: materialization preflight cannot bypass adapter execution.

### Behavior 3: Missing or invalid manifest blocks preflight

Given P7-O claims readiness but the execution manifest is missing or invalid
When P7-P runs
Then it blocks by execution manifest.

Business rule: materialization requires a valid manifest, not only a report.

### Behavior 4: Execution report must be manifest-recorded

Given P7-O only produced a dry-run
When P7-P runs
Then it blocks target adapter execution state.

Business rule: dry-run is not permission to materialize.

### Behavior 5: Bad adapter plan blocks materialization

Given the execution manifest contains incomplete plan items
When P7-P runs
Then it blocks the materialization contract.

Business rule: every materialization item needs source artifacts, candidate targets, and materialization requirements.

### Behavior 6: Preflight output does not create candidate targets

Given P7-P writes JSON and Markdown output
When the command completes
Then no candidate target file is created
And no `state/product` write is made.

Business rule: P7-P prepares a later explicit materialize command only.

## Current Run Boundary

- Current status: `blocked_by_target_adapter_execution`.
- Source P7-O status: `blocked_by_target_adapter_readiness`.
- Source P7-O execution manifest recorded: `false`.
- Execution manifest: missing.
- Materialization plan: `0`.
- Can request adapter materialization: `false`.
- Requires explicit materialize command: `false`.
- Candidate targets materialized: `false`.
- Formal target adapters executed: `false`.
- Formal writeback executed: `false`.
- This command wrote formal state: `false`.
- Product state writeback allowed: `false`.
