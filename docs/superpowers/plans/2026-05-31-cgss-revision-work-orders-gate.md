# CGSS Revision Work Orders Gate

## Stage

P6-I13 turns the P6-I12 revision task queue into an approval-gated draft work-order layer.

User-facing effect: this node prevents agents from receiving executable draft work orders until a human explicitly approves the revision queue. In the current real project state, it blocks and writes no agent packet files.

## BDD Behaviors

### Behavior 1: Pending queue blocks work orders

Given the revision task queue is still pending human approval
When P6-I13 builds revision work orders
Then it emits `blocked_revision_queue_not_approved`, with zero work orders and zero written work-order files.

Business rule: agents must not start drafting from an unapproved queue.

### Behavior 2: Approved queue maps tasks to draft work orders

Given the revision task queue is approved by a human
When P6-I13 builds revision work orders
Then it converts queued tasks into draft-layer work orders for the owning agent roles.

Business rule: approval unlocks task handoff, but only at the draft-work-order layer.

### Behavior 3: Approved queue can write agent packet files

Given the queue is approved and work-order writing is enabled
When P6-I13 runs
Then it writes only agent packet work-order files under the review packet area.

Business rule: file generation is allowed only after queue approval, and those files are still not formal manuscript or product state.

### Behavior 4: CLI blocks the real pending queue

Given the real project queue currently requires `human_approve_cgss_revision_task_queue`
When the default CLI runs
Then it writes a blocked JSON/Markdown review artifact and creates no agent work-order files.

Business rule: the command should reflect the current approval state on disk instead of silently promoting work.

## Boundary Conditions

- P6-I13 consumes `Results/json/cgss_social_capital_happiness_revision_task_queue.json`.
- The real current queue is not approved.
- Current real output must have `work_orders=0` and `written_work_orders=0`.
- Agent packet files can be written only from an approved queue.
- P6-I13 must not write formal manuscript, verified bibliography, DesignSpec, RunPlan, `state/product/*`, or `state/product/agent_task_queue.json`.
