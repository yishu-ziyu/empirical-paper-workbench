# CGSS AER-like Method Gate

## Stage

P6-K reviews the CGSS exploratory paper with an AER-like method gate after draft PDF preflight.

User-facing effect: this node tells the product whether the current paper draft can safely move toward a stronger review track, or whether it must pause for method review before any formal promotion.

## BDD Behaviors

### Behavior 1: Forces method review for AER-like profile

Given the exploratory paper, result evidence package, and literature draft packet are ready
When P6-K runs with `--profile aer_like`
Then it records `needs_human_method_gate_review`, `gate_status=yellow`, and `gate_enforcement.required=true`.

Business rule: a stricter journal-style track must not treat a draft empirical paper as ready without method review.

### Behavior 2: Keeps the default working-paper profile advisory

Given the same inputs
When P6-K runs without the AER-like profile
Then it suggests the method gate without forcing the blocking review path.

Business rule: early working-paper exploration can stay lighter than a stricter submission-style route.

### Behavior 3: Checks method standards and risks

Given a CGSS cross-sectional design
When the method gate evaluates the draft
Then it checks variable definitions, OLS and Ordered Logit fit, literature grounding, baseline controls, robustness plans, and endogeneity risks.

Business rule: the product should show the user why a paper is blocked, not only say that it is blocked.

### Behavior 4: Uses result numbers from the evidence package

Given the model evidence package contains OLS and Ordered Logit estimates
When P6-K writes the method gate
Then it binds the reported coefficients and sample sizes to that evidence package.

Business rule: method review must trace numeric claims back to model evidence, not regenerate or invent numbers.

### Behavior 5: Does not create a formal package

Given P6-K completes
When outputs are inspected
Then it writes only draft-layer method gate JSON and review Markdown, without formal manuscript, bibliography, DesignSpec, RunPlan, or `state/product/*` writeback.

Business rule: method gate review is a blocking checkpoint, not final acceptance.

### Behavior 6: Blocks when core inputs are missing

Given the evidence package or paper assembly is not ready
When P6-K runs
Then it records a blocked status and does not produce an approvable method gate.

Business rule: a method gate cannot judge a paper without the current draft and its evidence trail.

## Boundary Conditions

- Current real run uses `--profile aer_like`.
- Current status is `needs_human_method_gate_review`.
- Current gate status is `yellow`.
- Current promotion remains blocked.
- Current bound results are OLS `0.1658`, Ordered Logit `0.405`, and `n=5310`.
- Current follow-up tasks are human method review, variable definition detail, robustness/heterogeneity/mechanism planning, and endogeneity-risk handling.
