# CGSS Dataset-Bound Variable Role Draft

## Stage

P6-J3 turns the CGSS data discovery draft into a reviewable variable-role draft.

User-facing effect: this node shows which CGSS2023 fields are proposed as the outcome, social-capital measures, and controls. It is still a draft. It does not write formal variable roles.

## BDD Behaviors

### Behavior 1: Filters candidates to the recommended dataset

Given P6-J2 recommends CGSS2023
When P6-J3 builds the variable-role draft
Then it selects variables only from the recommended 2023 dataset and excludes 2021/2018 candidates from the main draft.

Business rule: a model draft must not mix variables from different survey waves unless that is explicitly designed.

### Behavior 2: Proposes an outcome variable with review reasons

Given CGSS2023 contains `a36`
When P6-J3 drafts the outcome role
Then it proposes `happiness <- a36` and explains that coding direction, missing values, and ordered scale need review.

Business rule: the product must show why a variable was chosen and what still needs human checking.

### Behavior 3: Proposes social-capital items as a multi-dimensional draft

Given CGSS2023 contains trust and social interaction items
When P6-J3 drafts the treatment role
Then it proposes `a33/a31a/a31b/a311` as social-capital items without finalizing index construction.

Business rule: social capital should not be collapsed into a black-box index before literature and coding review.

### Behavior 4: Blocks when dataset binding is not reviewable

Given the data discovery report is blocked or missing a recommended dataset
When P6-J3 builds the draft
Then it returns `blocked_missing_dataset_binding` and does not propose roles.

Business rule: variable-role drafting must depend on a reviewable dataset binding.

### Behavior 5: Writes reviewable artifacts without formal writeback

Given P6-J3 completes
When it writes outputs
Then it creates JSON and Markdown review artifacts, while leaving formal variable roles, DesignSpec, RunPlan, manuscript, and `state/product/*` unchanged.

Business rule: a variable-role draft is not a formal variable-role approval.

## Boundary Conditions

- Current real run uses the P6-J2 recommended CGSS2023 dataset.
- Current real run proposes `a36` as the outcome.
- Current real run proposes `a33/a31a/a31b/a311` as social-capital items.
- Current real run proposes `a2/a3a/a7a/a7b/a15/a18/a21/a8a/a8b/s41` as controls.
- `needs_human_dataset_bound_role_review` is a pause state, not a promotion.
