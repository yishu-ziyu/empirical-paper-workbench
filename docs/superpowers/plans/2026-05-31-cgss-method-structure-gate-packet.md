# CGSS Method Structure Gate Packet

## Stage

P6-I11 builds a reviewable method and paper-structure gate from the CGSS results evidence package and literature review draft packet.

User-facing effect: this node tells the product what the paper is allowed to claim, which methods are blocked, and what each manuscript section must contain before drafting continues. It does not write DesignSpec, RunPlan, or manuscript sections.

## BDD Behaviors

### Behavior 1: Build method and structure gate

Given the results evidence package and literature review draft packet are reviewable
When P6-I11 builds the gate packet
Then it emits paper length standards, section standards, method claim gates, and human approval gating.

Business rule: drafting needs explicit method and structure constraints before writing.

### Behavior 2: Separate association claims from causal methods

Given the CGSS design currently supports OLS and Ordered Logit associations
When P6-I11 evaluates method claims
Then it allows conditional association and ordered-outcome robustness wording while blocking DID, IV, RDD, PSM, and DML.

Business rule: the paper must not overclaim causal identification when the current design does not support it.

### Behavior 3: Use real result numbers

Given the results evidence package contains OLS and Ordered Logit outputs
When P6-I11 builds the main result gate
Then it records the real sample size, coefficients, standard errors, p values, and claim boundary.

Business rule: method constraints must be grounded in real outputs, not generic prose.

### Behavior 4: Block when inputs are not ready

Given the results evidence package or literature packet is invalid
When P6-I11 runs
Then it blocks and emits no method or section standards.

Business rule: method gates cannot be created from incomplete evidence.

### Behavior 5: Preserve formal-layer boundary

Given P6-I11 runs successfully
When it writes outputs
Then it writes only JSON/Markdown review artifacts and keeps DesignSpec, RunPlan, formal manuscript, bibliography, and product state untouched.

Business rule: this stage prepares a gate packet, not formal writeback.

## Boundary Conditions

- P6-I11 consumes the results evidence package and literature review draft packet.
- P6-I11 emits method claim gates and section standards only.
- P6-I11 keeps `promotion.allowed=false`.
- P6-I11 requires human approval before DesignSpec, RunPlan, empirical-strategy, or main-results writeback.
- P6-I11 must not write DesignSpec, RunPlan, formal manuscript, formal bibliography, or `state/product/*`.
