# P7-AC Auto Mode Formal Package Route-Specific Artifact Verification

## Goal

Verify the route-specific formal package artifact produced by P7-AB before the Auto Mode chain treats that selected route as complete.

## BDD Behaviors

### Behavior 1: Completed PDF route verifies the final PDF fingerprint

Given P7-AB completed the `pdf_export` route and its delegated PDF writeback report points to a final PDF
When the route-specific verification gate runs
Then it verifies that the PDF exists under `Submissions/formal_package/`, and that bytes and sha256 match the delegated report.

Business rule: PDF export completion is not trusted until the actual final PDF file matches the delegated report.

### Behavior 2: Current blocked P7-AB output blocks verification

Given the current repository P7-AB output is `blocked_by_selected_route_execute`
When the route-specific verification gate runs
Then it reports `blocked_by_route_specific_artifact_executor` and verifies no artifact.

Business rule: A blocked executor cannot be promoted by a later verifier.

### Behavior 3: Missing or invalid executor/delegated report blocks verification

Given the executor report or delegated artifact report is missing or has the wrong schema
When the verification gate runs
Then it blocks before reading any route artifact.

Business rule: verification needs both the route executor evidence and the route-specific delegated evidence.

### Behavior 4: Executor completion contract must be clean

Given P7-AB did not run the delegated command successfully, has an unknown route, or route flags contradict the selected route
When the verification gate runs
Then it blocks with route executor contract reasons.

Business rule: the verifier only accepts a completed, single-route, internally consistent P7-AB report.

### Behavior 5: PDF/DOCX artifacts must exist and match fingerprints

Given the delegated PDF or DOCX report points outside the formal package, or the file is missing or changed
When the verification gate runs
Then it blocks with artifact path, bytes, or sha256 reasons.

Business rule: formal package files must be present in the formal package directory and match their delegated report fingerprints.

### Behavior 6: Package manifest route verifies the manifest and its package artifacts

Given P7-AB completed the `package_manifest` route
When the verification gate runs
Then it verifies the package manifest file status/schema and the PDF/DOCX artifact fingerprints recorded by the delegated manifest report.

Business rule: a package manifest route is complete only if the manifest and its listed package files still match the report.

### Behavior 7: Manual acceptance route verifies the acceptance record and artifacts

Given P7-AB completed the `manual_acceptance` route
When the verification gate runs
Then it verifies the manual acceptance report, matching product-state copy, and PDF/DOCX artifact fingerprints.

Business rule: manual acceptance is a product-state record plus artifact evidence, so both must match.

### Behavior 8: CLI default reflects the current blocked executor

Given the current checkout has the blocked P7-AB report
When the CLI runs with default paths
Then it writes blocked verification JSON/Markdown and does not write product state.

Business rule: the default command is safe to run in the current checkout and cannot create acceptance state.

## Boundary Conditions To Confirm

- Manual acceptance route treats `accept`, `defer`, `needs_revision`, and `reject` as valid delegated command outcomes, but only verifies the record; it does not override the human decision.
- Package manifest verification checks the manifest JSON and the listed PDF/DOCX artifacts; it does not regenerate the manifest.
- This node writes only P7-AC verification JSON/Markdown. It does not export PDF/DOCX, generate a package manifest, perform manual acceptance, or write `state/product/*`.

## Verification Plan

- RED: `python3 -m unittest tests.test_auto_mode_formal_package_route_specific_artifact_verification -v` fails before implementation because `Program.workbench.auto_mode_formal_package_route_specific_artifact_verification` does not exist.
- GREEN: implement a CLI-first verification module and wrapper command.
- Regression: run P7-A through P7-AC unittest chain and Python compilation.
- Real run: default command reads current blocked P7-AB output and writes blocked P7-AC report/review.
