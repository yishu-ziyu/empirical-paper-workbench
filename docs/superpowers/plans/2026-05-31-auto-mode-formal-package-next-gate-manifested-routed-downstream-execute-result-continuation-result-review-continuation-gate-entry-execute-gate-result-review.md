# Auto Mode Formal Package Next Gate Manifested Routed Downstream Execute Result Continuation Result Review Continuation Gate Entry Execute Gate Result Review

## Stage

P7-BQ reviews the P7-BP execute gate result.

User-facing effect: this node checks whether the P7-BP gate safely entered the next dry-run surface. If P7-BP is blocked, this review also blocks. If export is ready, it verifies the route-specific artifact execution dry-run. If manual is ready, it verifies the product-review packet continuation record.

## BDD Behaviors

### Behavior 1: Export entered result can be reviewed as ready

Given P7-BP reports that route-specific artifact execution was entered
When P7-BQ reviews the matching route-specific artifact execution dry-run report
Then it marks the export branch ready for the next continuation and does not execute artifacts.

Business rule: entering the next dry-run gate is enough for review, but not enough to claim export completion.

### Behavior 2: Manual continuation record can be reviewed as ready

Given P7-BP records one product-review packet continuation
When P7-BQ reviews it
Then it marks the manual branch ready for product-review packet follow-up without running commands.

Business rule: manual acceptance remains an auditable review packet, not an automatic acceptance.

### Behavior 3: Current blocked P7-BP blocks result review

Given the real P7-BP output is blocked
When P7-BQ reads it
Then P7-BQ produces a blocked review with no continuation records.

Business rule: a blocked execute gate cannot be treated as a successful handoff.

### Behavior 4: Invalid P7-BP source contract blocks

Given P7-BP is missing, has the wrong schema, is not in an entered/recorded status, or contains blockers
When P7-BQ evaluates it
Then P7-BQ blocks before trusting delegated records.

Business rule: result review only trusts completed P7-BP outputs.

### Behavior 5: Export dry-run report must be clean

Given P7-BP claims route-specific artifact execution was entered
When the delegated execution report is missing, mismatched, not dry-run ready, or dirty
Then P7-BQ blocks the export branch.

Business rule: the export branch cannot proceed unless the delegated dry-run is clean.

### Behavior 6: Manual continuation record must be clean

Given P7-BP claims product-review packet continuation was recorded
When the record is missing, duplicated, mismatched, incomplete, or unaudited
Then P7-BQ blocks the manual branch.

Business rule: the manual branch needs exactly one clean packet continuation record.

### Behavior 7: Boundary violations block review

Given P7-BP or delegated dry-run carries export, acceptance, formal writeback, or product-state side effects
When P7-BQ reviews it
Then P7-BQ blocks.

Business rule: this review node must remain evidence-only.

### Behavior 8: P7-BQ writes only its own report and review

Given P7-BQ runs
When it writes outputs
Then it creates only its JSON/Markdown review and leaves formal artifacts and product state untouched.

Business rule: the review output is a handoff record, not a production action.

## Boundary Conditions

- P7-BQ consumes only P7-BP execute gate output plus the delegated route-specific artifact execution dry-run when the export branch is entered.
- P7-BQ defaults to blocked in the current real repo state because P7-BP is blocked.
- P7-BQ keeps `can_write_product_state=false`.
- P7-BQ does not render PDF/DOCX, generate package manifest, perform manual acceptance, or write formal state.
