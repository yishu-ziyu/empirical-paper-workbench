# CGSS Verified Bibliography Candidates

## Stage

P6-I9 builds reviewable verified bibliography candidates from the CGSS literature source verification preflight.

User-facing effect: this node turns source-checked literature into a human approval desk for bibliography candidates. It also keeps unresolved sources in a manual follow-up queue and maps approved candidates to paper sections and claim roles. It does not create the formal bibliography and does not write the manuscript.

## BDD Behaviors

### Behavior 1: Build source-checked bibliography candidates

Given the source verification preflight is reviewable
When P6-I9 builds verified bibliography candidates
Then it emits source-checked candidate records with citation keys, source evidence, paper use, and human approval requirements.

Business rule: a source can become a bibliography candidate only after the system records source-check evidence, and human approval is still required before formal use.

### Behavior 2: Keep unresolved sources in manual follow-up

Given some seed sources still need official page, DOI, Zotero, Scholar, CNKI, or database verification
When P6-I9 builds the candidate package
Then those sources remain in `manual_followup_queue` and block promotion.

Business rule: unresolved source work must stay visible instead of being silently promoted.

### Behavior 3: Bind candidates to paper sections and claims

Given source-checked candidates exist
When P6-I9 emits citation bindings
Then each binding points to a target section, claim role, and draft sentence slot.

Business rule: downstream writing should know what each citation is allowed to support.

### Behavior 4: Block when source preflight is not ready

Given the source verification preflight is missing or not in `needs_source_verification`
When P6-I9 runs
Then it blocks and emits no bibliography candidates.

Business rule: bibliography candidate review cannot start from an invalid source preflight.

### Behavior 5: Preserve formal-layer boundary

Given P6-I9 runs successfully
When it writes outputs
Then it writes only JSON/Markdown review artifacts and keeps verified bibliography CSV, contribution matrix, formal bibliography, manuscript, and product state untouched.

Business rule: this stage prepares approval, not formal writeback.

## Boundary Conditions

- P6-I9 consumes only the source verification preflight as its upstream literature artifact.
- P6-I9 emits reviewable candidates, manual follow-up items, and citation bindings.
- P6-I9 keeps `promotion.allowed=false`.
- P6-I9 requires human bibliography approval before any formal bibliography or contribution matrix write.
- P6-I9 must not write `Data/literature/processed/verified_bibliography.csv`, contribution matrix, formal bibliography, formal manuscript, or `state/product/*`.
