# CGSS Revision Approval Router

## Stage

P6-I15 routes the CGSS revision queue approval record into the next workflow step.

User-facing effect: this node is the workflow traffic controller after the approval button. It tells the product whether to keep waiting, revise the queue, stop/rebuild, or generate draft Agent work orders.

## BDD Behaviors

### Behavior 1: Defer waits without writes

Given the approval record decision is `defer`
When P6-I15 routes the decision
Then it outputs `waiting_for_human_revision_queue_decision`, routes to `wait_for_human_confirmation`, and writes no Agent work orders.

Business rule: waiting is an explicit route, not a hidden failure.

### Behavior 2: Revise routes back to queue update

Given the approval record decision is `revise`
When P6-I15 routes the decision
Then it outputs `revision_queue_update_required` and recommends revising the CGSS revision task queue.

Business rule: requested changes should return to the queue, not start Agent work.

### Behavior 3: Reject routes to rebuild or stop

Given the approval record decision is `reject`
When P6-I15 routes the decision
Then it outputs `revision_queue_rebuild_or_stop_required` and writes no work orders.

Business rule: rejected queues must not unlock downstream execution.

### Behavior 4: Approve with an approved queue writes draft work orders only

Given the approval record decision is `approve` and contains an approved queue sidecar
When P6-I15 routes the decision
Then it expands the approved queue into draft-layer Agent work orders.

Business rule: only explicit approval with approved queue data can unlock work-order generation, and the generated files remain draft-layer artifacts.

### Behavior 5: CLI reads the real approval record

Given the real project approval JSON currently records `defer`
When the default CLI runs
Then it writes router JSON/Markdown and keeps `work_orders=0`.

Business rule: the router must reflect the live approval ledger rather than inventing a route.

## Boundary Conditions

- P6-I15 consumes `Results/json/cgss_social_capital_happiness_revision_queue_approval.json`.
- Current real decision is `defer`.
- Current real output must route to `wait_for_human_confirmation`.
- Current real output must have no written work orders.
- P6-I15 must not write formal manuscript, verified bibliography, DesignSpec, RunPlan, `state/product/*`, or `state/product/agent_task_queue.json`.
