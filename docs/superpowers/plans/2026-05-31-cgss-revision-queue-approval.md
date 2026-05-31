# CGSS Revision Queue Approval Record

## Stage

P6-I14 records a human decision for the CGSS revision task queue.

User-facing effect: this node provides the backend contract for an approval button. By default it records `defer`, so no approval is invented and no Agent work orders are generated.

## BDD Behaviors

### Behavior 1: Defer records a pending human decision

Given the revision queue still needs human approval
When P6-I14 runs with the default decision
Then it records `pending_human_revision_queue_decision`, keeps `approved=false`, and writes no approved queue sidecar.

Business rule: the system can show the queue is waiting without pretending a human approved it.

### Behavior 2: Approve requires reviewer and note

Given a user chooses `approve`
When reviewer or note is missing
Then P6-I14 blocks with missing approval metadata and does not approve the queue.

Business rule: approval must leave an accountable human trace.

### Behavior 3: Approve creates only an approved queue sidecar

Given a user chooses `approve` with reviewer and note
When P6-I14 records the decision
Then it writes an approved queue sidecar for downstream work-order generation.

Business rule: approval unlocks the next draft-work-order gate, but still does not write formal manuscript or product state.

### Behavior 4: Revise and reject do not unlock work orders

Given a user chooses `revise` or `reject`
When P6-I14 records the decision
Then it routes the queue back to revision or rebuild and writes no approved queue.

Business rule: negative or change-request decisions must not trigger Agent execution.

### Behavior 5: CLI default does not write product state

Given the real project queue is pending approval
When the default CLI runs
Then it writes only JSON/Markdown review artifacts and no `state/product/agent_task_queue.json`.

Business rule: this node records a decision ledger, not an executable product-state task queue.

## Boundary Conditions

- P6-I14 consumes `Results/json/cgss_social_capital_happiness_revision_task_queue.json`.
- Current real default decision is `defer`.
- Current real output must have `approved=false` and no approved queue sidecar.
- `approve` requires both reviewer and note.
- P6-I14 must not write Agent packet files, formal manuscript, verified bibliography, DesignSpec, RunPlan, `state/product/*`, or `state/product/agent_task_queue.json`.
