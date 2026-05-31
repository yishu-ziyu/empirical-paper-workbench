# Auto Mode Formal Package Next Gate Manifested Routed Downstream Execute Result Continuation Result Review Continuation Gate Entry Execute Gate

## Stage

P7-BP implements the execute gate after P7-BO.

User-facing effect: this node decides whether the reviewed downstream continuation can move forward. If P7-BO is blocked, it stops cleanly. If an export branch is ready, it can enter route-specific artifact execution dry-run. If a manual branch is ready, it records the product-review packet continuation. It must not render PDF/DOCX or write product state by itself.

## BDD Behaviors

### Behavior 1: Export dry-run previews the next execution gate

Given P7-BO is ready with one accepted `route_specific_artifact_execution_continuation` record
When the P7-BP execute gate runs in `dry-run` mode
Then it exposes the route-specific artifact execution command but does not run it, render files, or write product state.

Business rule: export continuation must be visible and reviewable before any real execution.

### Behavior 2: Manual dry-run previews product-review packet continuation

Given P7-BO is ready with one accepted `product_review_packet_continuation` record
When the P7-BP execute gate runs in `dry-run` mode
Then it previews the manual continuation without an external command and without recording the packet yet.

Business rule: manual acceptance remains a human-review handoff, not an automatic acceptance.

### Behavior 3: Current blocked P7-BO blocks this execute gate

Given the real P7-BO output is blocked
When P7-BP reads it
Then P7-BP produces a blocked report with no continuation command and no product-state permission.

Business rule: the chain must not skip a failed upstream review.

### Behavior 4: Invalid P7-BO source contract blocks

Given P7-BO is missing, has the wrong schema, is not ready, cannot request continuation, or contains blocking reasons
When P7-BP evaluates it
Then P7-BP blocks before reading any continuation record.

Business rule: P7-BP only trusts the exact approved P7-BO contract.

### Behavior 5: Continuation input record must be single and clean

Given P7-BO has zero, duplicate, mismatched, unaccepted, or non-continuable records
When P7-BP evaluates it
Then P7-BP blocks as a contract failure.

Business rule: one gate invocation can only advance one clearly accepted downstream route.

### Behavior 6: Execute mode requires explicit human confirmation metadata

Given P7-BO is ready
When P7-BP runs in `execute` mode without confirmation, reviewer, or note
Then P7-BP blocks without running the continuation.

Business rule: moving to the next gate must be auditable.

### Behavior 7: Confirmed manual execute records only the review-packet continuation

Given P7-BO is ready for manual continuation
When P7-BP runs in confirmed `execute` mode
Then it records the product-review packet continuation and does not run external commands or write formal state.

Business rule: the manual branch remains a review package, not a generated acceptance.

### Behavior 8: Confirmed export execute enters route-specific artifact execution dry-run only

Given P7-BO is ready for export continuation
When P7-BP runs in confirmed `execute` mode
Then it writes the route-specific artifact execution dry-run output and still does not execute the artifact export.

Business rule: this node advances the gate, not the final export.

## Boundary Conditions

- P7-BP consumes only P7-BO gate-entry output.
- P7-BP defaults to blocked in the current real repo state because P7-BO is blocked.
- P7-BP must keep `can_write_product_state=false`.
- P7-BP must not render PDF/DOCX, generate package manifest, perform manual acceptance, or write formal state.
