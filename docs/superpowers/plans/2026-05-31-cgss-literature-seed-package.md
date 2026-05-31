# CGSS Literature Seed Package

## Stage

P6-I7 builds a reviewable literature seed package for the CGSS social capital and subjective wellbeing paper path.

User-facing effect: this node gives the literature/review workflow a concrete starting packet. It does not claim that the bibliography is verified. It tells the user which theory, measurement, method, Chinese literature, and CGSS context sources still need human verification.

## BDD Behaviors

### Behavior 1: Build reviewable literature seed

Given the CGSS variable role review draft is ready and the results evidence package is ready
When P6-I7 builds the literature seed package
Then it outputs a human-reviewable package with seed sources, coverage areas, variable support, mechanism map, method support, and manual search queues.

Business rule: literature support must become an inspectable artifact before it can influence paper writing.

### Behavior 2: Block when variable roles are not reviewable

Given the variable role review draft is missing or not in a reviewable state
When P6-I7 runs
Then it blocks and produces no seed sources.

Business rule: literature binding cannot proceed before variables are clear enough to review.

### Behavior 3: Preserve formal-layer boundary

Given P6-I7 runs successfully
When it writes outputs
Then it writes only JSON/Markdown review artifacts and keeps formal bibliography, manuscript, variable roles, DesignSpec, RunPlan, and product state untouched.

Business rule: a seed package is not a verified bibliography or final literature review.

## Boundary Conditions

- P6-I7 consumes `cgss_social_capital_happiness_variable_role_review_draft.json` and `cgss_social_capital_happiness_results_evidence_package.json`.
- P6-I7 emits candidate seed sources and manual verification queues only.
- P6-I7 keeps `promotion.allowed=false`.
- P6-I7 must not write formal manuscript, formal bibliography, formal variable roles, DesignSpec, RunPlan, or `state/product/*`.
