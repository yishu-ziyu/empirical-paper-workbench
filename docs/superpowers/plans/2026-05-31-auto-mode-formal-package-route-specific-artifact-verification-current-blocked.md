# P7-AC Auto Mode Formal Package Route-Specific Artifact Verification Current Blocked

## Component Effect

P7-AC verifies the concrete artifact produced by the route-specific executor. In product terms, it is the proof gate between "a route command ran" and "the route result can be trusted".

It checks the selected route output instead of producing a new output:

- PDF route: verify final PDF path, bytes, and sha256.
- DOCX route: verify final DOCX path, bytes, and sha256.
- Package manifest route: verify manifest plus package PDF/DOCX evidence.
- Manual acceptance route: verify the manual acceptance state copy plus package PDF/DOCX evidence.

Current user-visible effect: P7-AB has not completed a real route-specific artifact command, so P7-AC must not verify any artifact and must not allow P7-AD to record route completion.

## Current Run Boundary

Command:

```bash
python3 Program/auto_mode_formal_package_route_specific_artifact_verification.py --project-root .
```

Observed CLI result:

```text
status=blocked_by_route_specific_artifact_executor
route_type=
verified_route_type=
delegated_status=
route_specific_artifact_verified=false
selected_route_executed=false
export_or_acceptance_executed=false
can_write_product_state=false
```

Observed JSON facts from `Results/json/auto_mode_formal_package_route_specific_artifact_verification.json`:

```text
status=blocked_by_route_specific_artifact_executor
route_type=
verified_route_type=
delegated_status=
route_specific_artifact_verified=false
selected_route_executed=false
export_or_acceptance_executed=false
artifact_verification_record_count=0
can_write_product_state=false
source_executor.status=blocked_by_selected_route_execute
source_executor.route_specific_artifact_executed=false
source_executor.route_specific_command_executed=false
source_executor.delegated_report_path=
source_delegated_report.status=
next_action.id=resolve_route_specific_artifact_executor_blockers
```

Blocking reasons:

```text
route_specific_artifact_executor_not_completed
route_specific_artifact_not_executed
selected_route_not_executed
export_or_acceptance_not_executed
route_specific_artifact_executor_has_blocking_reasons
```

## BDD Coverage

Given P7-AB completed a PDF export route and the final PDF exists in the formal package with matching bytes and sha256,
When P7-AC verifies the route-specific artifact,
Then it records the PDF artifact as verified and does not write product state.

Business rule: PDF export is trusted only after the final file fingerprint is checked.

Given the current P7-AB executor is blocked,
When P7-AC runs against the current repo state,
Then it returns `blocked_by_route_specific_artifact_executor` and creates no artifact verification records.

Business rule: a non-executed route cannot be treated as a verified output.

Given the executor or delegated report is missing, invalid, or mismatched,
When P7-AC tries to verify the route,
Then it blocks before trusting any route output.

Business rule: verification needs both an executed route and the delegated command report.

Given P7-AB claims completion but its route type, flags, return code, or report path are inconsistent,
When P7-AC checks the executor contract,
Then it blocks on route-specific artifact contract errors.

Business rule: an internally inconsistent executor result is not evidence.

Given PDF/DOCX artifacts are outside the formal package or no longer match recorded bytes/sha256,
When P7-AC verifies file integrity,
Then it blocks on artifact integrity.

Business rule: only formal-package artifacts with matching fingerprints can move forward.

Given the package manifest route is complete,
When P7-AC verifies the route,
Then it verifies the manifest plus the package PDF/DOCX evidence.

Business rule: package readiness is a bundle check, not just a manifest-file existence check.

Given the manual acceptance route is complete,
When P7-AC verifies the route,
Then it verifies the manual acceptance state copy plus package PDF/DOCX evidence.

Business rule: manual acceptance must be tied back to the concrete package artifacts.

Given the CLI is run with the current blocked P7-AB executor,
When P7-AC writes outputs,
Then it writes blocked report/review files only and does not write `state/product`.

Business rule: blocked verification stays read-only with respect to product state.

## Verification

Commands run:

```bash
python3 -m unittest tests.test_auto_mode_formal_package_route_specific_artifact_verification -v
python3 -m py_compile Program/auto_mode_formal_package_route_specific_artifact_verification.py Program/workbench/auto_mode_formal_package_route_specific_artifact_verification.py tests/test_auto_mode_formal_package_route_specific_artifact_verification.py
python3 Program/auto_mode_formal_package_route_specific_artifact_verification.py --project-root .
python3 -m unittest tests.test_auto_mode_formal_package_route_specific_artifact_executor tests.test_auto_mode_formal_package_route_specific_artifact_verification tests.test_auto_mode_formal_package_verified_route_completion_ledger -v
jq -r '[...] | .[]' Results/json/auto_mode_formal_package_route_specific_artifact_verification.json
test ! -e state/product/auto_mode_formal_package_route_specific_artifact_verification.json
git diff -- Results/json/auto_mode_formal_package_route_specific_artifact_verification.json Reviews/auto_mode_formal_package_route_specific_artifact_verification.md
```

Results:

- Target tests: 8 passed.
- Adjacent regression: 24 passed.
- Python compile check: passed.
- Current CLI: exit 0 and blocked by P7-AB executor.
- Product state write check: passed; no P7-AC product state file exists.
- Scoped artifact diff: no P7-AC report/review semantic or timestamp diff after the run.

## Downstream Connection

P7-AD must not record a verified route completion ledger from this state because:

- `verified_route_type` is empty.
- `route_specific_artifact_verified=false`.
- `artifact_verification_records=[]`.
- P7-AB has no delegated report path.
- P7-AB did not execute a route-specific command.

P7-AC can become a valid P7-AD input only after P7-AB completes one real route-specific artifact command and the delegated report plus concrete artifacts pass fingerprint verification.

## Pause

Pause after P7-AC. Do not auto-advance to P7-AD until the user resumes.
