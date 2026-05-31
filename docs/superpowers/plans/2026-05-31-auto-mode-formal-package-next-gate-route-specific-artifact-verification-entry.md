# P7-AT Auto Mode Formal Package Next Gate Route-Specific Artifact Verification Entry

Date: 2026-05-31

## Scope

Implement the next Auto Mode paper package node after P7-AS.

P7-AT consumes only:

- `Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review.json`

When P7-AS is ready, P7-AT calls the existing route-specific artifact verification CLI:

- `Program/auto_mode_formal_package_route_specific_artifact_verification.py`

P7-AT writes only its own entry report/review and the existing artifact verification report/review. It must not export PDF/DOCX, generate package manifests, perform manual acceptance, rerun models, or write `state/product/*`.

## BDD Behaviors

### Behavior 1: Ready P7-AS calls existing artifact verification

Given P7-AS has status `route_specific_artifact_execution_result_review_ready`
And it contains exactly one accepted route-specific artifact verification input record
And the referenced artifact executor report and delegated report describe an existing formal package artifact
When P7-AT runs
Then it calls the existing route-specific artifact verification command
And records the verification status, route type, and verification records in the P7-AT entry report.

Business rule: P7-AT is the bridge from accepted artifact execution to actual artifact verification.

### Behavior 2: Current blocked P7-AS blocks P7-AT

Given P7-AS is missing or blocked
When P7-AT runs
Then no verification command is run
And no verification input record is consumed.

Business rule: the next gate cannot verify a route artifact until P7-AS accepts the executed artifact result.

### Behavior 3: Invalid or not-ready P7-AS blocks entry

Given P7-AS has a wrong schema, a non-ready status, missing review approval, cannot continue, or source blockers
When P7-AT runs
Then it returns `blocked_by_route_specific_artifact_execution_result_review`.

Business rule: P7-AT trusts only the approved P7-AS result review contract.

### Behavior 4: Verification input record contract must be clean

Given P7-AS is ready
But its verification input records are missing, duplicated, route-mismatched, path-mismatched, or not accepted
When P7-AT runs
Then it returns `blocked_by_route_specific_artifact_verification_entry_contract`.

Business rule: the entry node must know exactly which artifact executor report and delegated report to verify.

### Behavior 5: Missing verification command blocks entry

Given P7-AS is ready
But the route-specific artifact verification CLI file is unavailable
When P7-AT runs
Then it does not attempt execution and reports the command as unavailable.

Business rule: a delegated verification command must be present before P7-AT can enter it.

### Behavior 6: Existing verification failure is captured

Given P7-AS is ready
And P7-AT runs the existing artifact verification CLI
But the verification report is blocked by missing or mismatched artifacts
When P7-AT records the result
Then P7-AT returns `blocked_by_route_specific_artifact_verification_failure`.

Business rule: P7-AT may call verification, but it must not convert a failed verification into progress.

### Behavior 7: CLI defaults to current blocked state

Given the current project has blocked P7-AS output
When the P7-AT CLI runs with defaults
Then it writes a blocked entry report/review
And does not write `state/product/*`.

Business rule: the real repo state remains safely blocked until upstream execution is genuinely ready.

## Boundary Conditions

- P7-AT does not run exports or manual acceptance directly.
- P7-AT does not mutate formal manuscript, bibliography, design spec, run plan, or product state.
- P7-AT is allowed to call the existing read-only artifact verification command when P7-AS is ready.
- The existing verification command may write its normal verification JSON and Markdown review.
- Downstream nodes should read P7-AT output, not assume verification succeeded from command execution alone.
