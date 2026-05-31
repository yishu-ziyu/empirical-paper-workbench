# Auto Mode Formal Target Adapter Candidate Promotion Execute Current Blocked Record

## Stage

P7-V is the formal target adapter candidate promotion execute gate after P7-U.

User-facing effect: this node tells downstream components whether approved candidate targets were actually promoted into the formal package. In the current run, P7-U is blocked and has zero promotion execution plan items, so P7-V records a blocked dry-run and does not write formal package targets or a promotion manifest.

## BDD Behaviors

### Behavior 1: Confirmed promote copies candidates and writes manifest

Given P7-U is ready
And promotion is explicitly confirmed with reviewer and note
When P7-V runs in `promote` mode
Then it copies candidate targets to formal package targets
And writes a promotion manifest.

Business rule: only explicit, attributable execution may write formal package targets.

### Behavior 2: Dry-run does not copy candidates

Given P7-U is ready
When P7-V runs in `dry-run`
Then it reports planned promotion operations
And does not write formal package targets.

Business rule: dry-run previews execution but is not execution.

### Behavior 3: Blocked preflight blocks promotion

Given P7-U is blocked
When P7-V runs
Then it reports `blocked_by_candidate_promotion_execution_preflight`
And creates no promotion operations.

Business rule: promotion cannot bypass execution preflight.

### Behavior 4: Promote requires confirmation, reviewer, and note

Given P7-U is ready
When P7-V runs in `promote` mode without confirmation, reviewer, or note
Then it blocks promotion.

Business rule: formal package writes must be explicit and attributable.

### Behavior 5: Missing, changed, or existing targets block promotion

Given P7-U is ready
When a candidate is missing, candidate hash/bytes differ, or a formal target already exists
Then P7-V blocks promotion.

Business rule: promotion must be reproducible and non-overwriting.

### Behavior 6: CLI defaults to current blocked preflight

Given the current P7-U report is blocked
When P7-V CLI runs with default paths
Then it writes blocked execute JSON and Markdown.

Business rule: the command reflects current repo state, not an assumed promote path.

## Current Run Boundary

- Current status: `blocked_by_candidate_promotion_execution_preflight`.
- Mode: `dry-run`.
- Source P7-U status: `blocked_by_candidate_promotion_approval`.
- Source P7-U can request verified candidate promotion execution: `false`.
- Source P7-U promotion execution plan count: `0`.
- Can promote with confirmation: `false`.
- Promotion operations count: `0`.
- Promotion manifest recorded: `false`.
- Candidate targets promoted: `false`.
- Formal target adapters executed: `false`.
- Formal writeback executed: `false`.
- This command wrote formal state: `false`.
- Product state writeback allowed: `false`.
- Blocking reasons: `promotion_execution_preflight_not_ready`, `promotion_execution_preflight_cannot_request_execution`, `promotion_execution_preflight_missing_explicit_command_requirement`, `promotion_execution_plan_missing`.
