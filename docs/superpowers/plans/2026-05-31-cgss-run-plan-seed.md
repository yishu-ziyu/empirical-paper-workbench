# CGSS RunPlan Seed

## Stage

P6-J5 turns the CGSS DesignSpec draft into a reviewable RunPlan seed.

User-facing effect: this node shows exactly what the system would execute next, including source fields, constructed analysis variables, model commands, expected outputs, and failure explanations. It does not run the models.

## BDD Behaviors

### Behavior 1: Builds a draft RunPlan seed without formal writeback

Given P6-J4 has a reviewable DesignSpec draft
When P6-J5 builds the RunPlan seed
Then it writes a draft seed with planned tasks and keeps formal RunPlan, DesignSpec, variable roles, manuscript, and `state/product/*` unchanged.

Business rule: an execution plan must be inspectable before it becomes formal or executable.

### Behavior 2: Translates source fields into analysis variables

Given the DesignSpec binds CGSS source fields
When P6-J5 builds execution preflight
Then it lists required source columns and constructed variables such as `happiness`, `social_capital_index`, `female`, `age`, `education_level`, `log_income`, `health`, `urban_hukou`, and `province`.

Business rule: the product must make data transformation visible before analysis.

### Behavior 3: Schedules OLS and Ordered Logit tasks

Given the DesignSpec recommends OLS and Ordered Logit
When P6-J5 builds planned tasks
Then it emits CLI tasks for `Program/cgss_minimal_model.py` and `Program/cgss_ordered_robustness.py` with expected output paths.

Business rule: downstream execution should be command-driven and reproducible.

### Behavior 4: Blocks without a reviewable DesignSpec draft

Given the DesignSpec draft is missing or blocked
When P6-J5 is invoked
Then it returns `blocked_missing_reviewable_design_spec_draft` and does not create a RunPlan seed.

Business rule: RunPlan seed generation must not skip the design review gate.

### Behavior 5: Does not run models

Given P6-J5 completes successfully
When outputs are inspected
Then `ran_models=false` and the model result artifacts are only listed as expected outputs.

Business rule: planning is separate from execution.

## Boundary Conditions

- Current real run uses the P6-J4 CGSS DesignSpec draft.
- Current real run plans source columns `a36/a33/a31a/a31b/a311/a2/a3a/a7a/a8a/a15/a18/s41`.
- Current real run plans OLS and Ordered Logit commands.
- Current real run defers `a7b/a21/a8b` as secondary control-source columns.
- `needs_human_run_plan_seed_review` is a pause state, not execution approval.
