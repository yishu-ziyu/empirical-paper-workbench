# P7-AD Auto Mode Formal Package Verified Route Completion Ledger

## Goal

Record a read-only completion ledger after P7-AC verifies one selected formal package route artifact.

## BDD Behaviors

### Behavior 1: Verified PDF route records a completion ledger

Given P7-AC verified the `pdf_export` artifact and recorded a verified PDF artifact fingerprint
When the completion ledger runs
Then it records one route completion entry that can enter the next Auto Mode gate, without writing formal/product state.

Business rule: a route is complete only after the selected artifact is verified and recorded as ledger evidence.

### Behavior 2: Current blocked P7-AC output blocks ledger recording

Given the current checkout P7-AC output is `blocked_by_route_specific_artifact_executor`
When the completion ledger runs
Then it reports blocked status, records no completion entry, and cannot enter the next gate.

Business rule: blocked verification cannot be treated as route completion.

### Behavior 3: Missing or invalid P7-AC report blocks ledger recording

Given the source verification report is missing, has the wrong schema, or is not in verified status
When the ledger runs
Then it blocks before recording completion evidence.

Business rule: the ledger consumes only a valid P7-AC verification report.

### Behavior 4: Verified report must be internally consistent

Given P7-AC claims verified status but has missing artifact records, unverified artifact records, or remaining blocking reasons
When the ledger runs
Then it blocks as a verified-route completion contract failure.

Business rule: a completion ledger cannot depend on contradictory verification evidence.

### Behavior 5: Route flags must match the verified route

Given the verified route type and route flags disagree
When the ledger runs
Then it blocks as a verified-route completion contract failure.

Business rule: PDF, DOCX, package manifest, and manual acceptance routes each have one expected flag shape.

### Behavior 6: Package route preserves artifact evidence

Given P7-AC verified a package manifest route with manifest, PDF, and DOCX artifact records
When the ledger records completion
Then the completion entry preserves all artifact ids, paths, bytes, sha256 values, and verification statuses.

Business rule: downstream gates need a compact ledger but cannot lose artifact evidence.

### Behavior 7: Boundary violations block ledger recording

Given the source verification report indicates formal writeback, product-state permission, or boundary flags
When the ledger runs
Then it blocks and records no completion entry.

Business rule: this ledger is read-only and must not authorize or hide state writes.

### Behavior 8: CLI default reflects the current blocked verification

Given the current checkout has the blocked P7-AC report
When the CLI runs with default paths
Then it writes blocked ledger JSON/Markdown and does not write product state.

Business rule: the default command is safe to run in the current checkout and cannot advance a blocked route.

## Boundary Conditions To Confirm

- Manual acceptance completion requires the P7-AC source product-state copy to be verified, but this ledger still does not write `state/product/*`.
- This node records only verified route completion. It does not export PDF/DOCX, generate a package manifest, perform manual acceptance, promote candidate targets, or write formal state.
- The next Auto Mode gate should consume this ledger only when `can_enter_next_auto_mode_gate=true`.

## Verification Plan

- RED: `python3 -m unittest tests.test_auto_mode_formal_package_verified_route_completion_ledger -v` fails before implementation because `Program.workbench.auto_mode_formal_package_verified_route_completion_ledger` does not exist.
- GREEN: implement a CLI-first completion ledger module and wrapper command.
- Regression: run P7-A through P7-AD unittest chain and Python compilation.
- Real run: default command reads current blocked P7-AC output and writes blocked P7-AD report/review.
