# CGSS RunPlan Seed Executor

## Stage

P6-J6b executes the approved CGSS RunPlan seed in the draft evidence layer.

User-facing effect: this node turns the approved execution plan into concrete model evidence. It runs the planned OLS and Ordered Logit checks, then merges their outputs into a result evidence package that can be reviewed before manuscript drafting.

## BDD Behaviors

### Behavior 1: Blocks without an approved seed

Given the RunPlan seed has not been approved for draft execution
When P6-J6b is invoked
Then it returns `blocked_run_plan_seed_not_approved`, runs no models, and writes no formal state.

Business rule: model execution must not bypass the human approval gate.

### Behavior 2: Executes approved OLS and Ordered Logit tasks

Given P6-J6a has produced an approved seed
When P6-J6b runs the seed
Then it executes `run_ols_baseline` and `run_ordered_logit_robustness`.

Business rule: the execution layer must follow the approved plan, not invent a new model path.

### Behavior 3: Merges model results into an evidence package

Given OLS and Ordered Logit outputs are available
When P6-J6b completes
Then it writes a results evidence package with sample size, coefficient direction, method gate status, and writing inputs.

Business rule: downstream writing should consume evidence, not raw model files alone.

### Behavior 4: Keeps the result in human-review state

Given model execution completes
When the execution report is inspected
Then status is `completed_needs_human_result_review` and evidence package status is `ready_for_paper_draft_input`.

Business rule: successful model execution is not the same as a reviewed paper claim.

### Behavior 5: Does not write formal product state

Given P6-J6b runs successfully
When repository outputs are inspected
Then formal RunPlan, variable roles, manuscript, and `state/product/*` remain out of scope.

Business rule: draft evidence and formal product state stay separated.

## Boundary Conditions

- Current real run uses reviewer `mahaoxuan` from the approved seed.
- Current real run executes CGSS2023 with analysis sample `n=5310`.
- Current real run finds a positive social-capital coefficient in both OLS and Ordered Logit.
- Current real run writes evidence for review only; it does not promote a canonical claim.
- The next stage should be human review or manuscript-section routing, not formal result promotion.
