# CGSS DesignSpec Draft

## Stage

P6-J4 turns the dataset-bound variable-role draft into a reviewable research design draft.

User-facing effect: this node explains what kind of empirical design the CGSS topic can support. It recommends OLS and Ordered Logit as draft model candidates, and blocks stronger causal methods for now.

## BDD Behaviors

### Behavior 1: Builds a reviewable DesignSpec draft

Given P6-J3 has reviewable dataset-bound variable roles
When P6-J4 builds the design draft
Then it records the dataset, outcome, treatment, controls, source bindings, identification summary, model candidates, and review gates.

Business rule: model execution needs a readable design contract before RunPlan generation.

### Behavior 2: Recommends cross-section model candidates

Given the current data is CGSS2023 cross-sectional survey data
When P6-J4 evaluates model families
Then it recommends an OLS baseline and an Ordered Logit robustness model.

Business rule: the first executable design should match the data structure and outcome scale.

### Behavior 3: Sets a clear claim boundary

Given the design is cross-sectional
When P6-J4 writes the design draft
Then it marks the claim level as `conditional_association_not_strong_causality`.

Business rule: the paper should not overclaim causality from this design.

### Behavior 4: Explains blocked method families

Given DID, IV, RDD, PSM, and DML require stronger design conditions
When P6-J4 builds the method gate
Then it lists why each family is not ready for the current topic.

Business rule: the product should show why advanced methods are blocked, not silently omit them.

### Behavior 5: Does not write formal state

Given P6-J4 completes successfully
When it writes outputs
Then it only creates JSON and Markdown draft artifacts, while leaving formal DesignSpec, RunPlan, variable roles, manuscript, and `state/product/*` unchanged.

Business rule: a DesignSpec draft is not formal DesignSpec approval.

## Boundary Conditions

- Current real run uses the CGSS2023 variable-role draft from P6-J3.
- Current real run recommends OLS and Ordered Logit.
- Current real run blocks DID, IV, RDD, PSM, and DML.
- Current real run limits claims to conditional association.
- `needs_human_design_spec_review` is a pause state, not a promotion.
