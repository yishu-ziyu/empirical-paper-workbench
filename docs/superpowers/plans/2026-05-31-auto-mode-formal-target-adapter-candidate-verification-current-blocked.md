# Auto Mode Formal Target Adapter Candidate Verification Current Blocked Record

## Stage

P7-R is the formal target adapter candidate verification gate after P7-Q.

User-facing effect: this node tells downstream components whether materialized candidate targets exist and match the materialization manifest. In the current run, P7-Q is blocked and has not recorded a materialization manifest, so P7-R records a blocked verification result and does not produce verified candidate records.

## BDD Behaviors

### Behavior 1: Completed materialization verifies candidate targets

Given P7-Q has completed materialization
And the materialization manifest lists candidate targets
When P7-R runs
Then it records verified target records for the candidate files.

Business rule: only real materialized candidate files can become verified candidates.

### Behavior 2: Blocked materialization execute blocks verification

Given P7-Q is blocked
When P7-R runs
Then it reports `blocked_by_materialization_execute`
And creates no target verification records.

Business rule: verification cannot invent candidate targets.

### Behavior 3: Missing or invalid manifest blocks verification

Given P7-Q reports completed materialization
But the materialization manifest is missing or has an invalid schema
When P7-R runs
Then it blocks verification.

Business rule: candidate verification must be tied to a valid manifest.

### Behavior 4: Execute report must be completed and materialized

Given the execute report is only a dry-run or is otherwise not completed
When P7-R runs
Then it blocks verification.

Business rule: dry-run planning is not a verified candidate package.

### Behavior 5: Missing targets or byte mismatches block verification

Given the manifest lists candidate targets
When a target is missing or its byte count differs from the manifest
Then P7-R blocks verification.

Business rule: verification must prove the staged files match the manifest.

### Behavior 6: Boundary violations block verification

Given P7-Q or its manifest reports a formal-state boundary violation
When P7-R runs
Then it blocks verification.

Business rule: verification cannot bless artifacts produced by an unsafe boundary crossing.

### Behavior 7: Verification writes report and review only

Given P7-R runs in either blocked or verified mode
When outputs are written
Then it writes candidate verification JSON and Markdown only
And does not write product state or formal state.

Business rule: candidate verification is a gate, not a promotion.

## Current Run Boundary

- Current status: `blocked_by_materialization_execute`.
- Source P7-Q status: `blocked_by_materialization_preflight`.
- Source P7-Q materialization manifest recorded: `false`.
- Source P7-Q candidate targets materialized: `false`.
- Candidate targets verified: `false`.
- Target verification records: `0`.
- Formal target adapters executed: `false`.
- Formal writeback executed: `false`.
- This command wrote formal state: `false`.
- Product state writeback allowed: `false`.
