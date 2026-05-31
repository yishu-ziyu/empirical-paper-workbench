# CGSS RunPlan Seed Approval

## Stage

P6-J6a records the human decision for the CGSS RunPlan seed.

User-facing effect: this node turns a reviewable execution plan into an approved draft-execution input. It gives the next executor permission to run the planned CGSS OLS and Ordered Logit checks, but only in the draft evidence layer.

## BDD Behaviors

### Behavior 1: Defer keeps execution blocked

Given P6-J5 has produced a reviewable RunPlan seed
When P6-J6a records the default `defer` decision
Then it writes an approval review record, keeps `approved=false`, and does not create an approved seed.

Business rule: silence is not execution approval.

### Behavior 2: Approve requires reviewer and note

Given a reviewer chooses `approve`
When reviewer or note is missing
Then the node returns `blocked_missing_human_approval_metadata` and does not create an approved seed.

Business rule: execution must be attributable to an explicit human decision.

### Behavior 3: Approve creates only a draft execution sidecar

Given the user has approved the RunPlan seed for draft execution
When P6-J6a records `approve` with reviewer and note
Then it creates `Results/json/cgss_social_capital_happiness_run_plan_seed_approved.json` and keeps formal writeback disabled.

Business rule: approval opens the execution gate, not the formal paper gate.

### Behavior 4: Revise or reject cannot execute

Given the reviewer chooses `revise` or `reject`
When P6-J6a writes the decision record
Then no approved seed exists and downstream execution remains blocked.

Business rule: objections must stop the execution path.

### Behavior 5: Approval does not run models

Given P6-J6a completes successfully
When outputs are inspected
Then it has only written approval artifacts and has not run OLS, Ordered Logit, formal RunPlan writeback, or paper generation.

Business rule: decision and execution stay separate.

## Boundary Conditions

- Current real run records reviewer `mahaoxuan`.
- Current real run treats the 2026-05-31 continuation instruction as approval for draft execution only.
- Current real run writes an approved seed for P6-J6b.
- The approved seed still has `formal_writeback_allowed=false`.
- Results from P6-J6b must still go to human review before any paper claim or formal product state.
