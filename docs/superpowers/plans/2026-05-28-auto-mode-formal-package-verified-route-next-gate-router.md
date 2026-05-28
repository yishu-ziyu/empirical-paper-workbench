# P7-AE Auto Mode Formal Package Verified Route Next Gate Router

## Goal

Route a verified P7-AD route completion ledger to the next Auto Mode gate without executing that gate.

## BDD Behaviors

### Behavior 1: Ready PDF completion ledger records a next-gate route

Given P7-AD recorded a verified `pdf_export` completion ledger
When the next-gate router runs
Then it records a route to the next Auto Mode gate and does not export, accept, or write product state.

Business rule: a verified route completion can be handed to the next gate, but the handoff is still read-only.

### Behavior 2: Current blocked P7-AD ledger blocks routing

Given the current checkout P7-AD ledger is blocked
When the next-gate router runs
Then it records no next-gate route and cannot enter the next gate.

Business rule: a blocked completion ledger cannot advance the Auto Mode chain.

### Behavior 3: Missing or invalid P7-AD ledger blocks routing

Given the ledger report is missing, has the wrong schema, or is not in recorded status
When the router runs
Then it blocks before choosing any next gate.

Business rule: the router consumes only a valid P7-AD completion ledger.

### Behavior 4: Completion record must match the verified route

Given the ledger claims completion but has no completion record, a mismatched record, or a non-recorded completion status
When the router runs
Then it blocks as a next-gate contract failure.

Business rule: downstream gates need one clean route completion record.

### Behavior 5: Unknown route type blocks routing

Given the ledger uses an unsupported verified route type
When the router runs
Then it blocks instead of guessing a gate.

Business rule: route-to-gate mapping must be explicit.

### Behavior 6: Manual acceptance routes to delivery completion gate

Given P7-AD recorded a verified `manual_acceptance` completion
When the next-gate router runs
Then it routes to the formal package delivery completion gate, not back to export routing.

Business rule: manual acceptance is the end of the export/acceptance route cycle.

### Behavior 7: Boundary violations block routing

Given the ledger indicates formal writeback, product-state permission, or boundary flags
When the router runs
Then it blocks and records no next-gate route.

Business rule: this router must remain read-only and cannot hide state-write signals.

### Behavior 8: CLI default reflects the current blocked ledger

Given the current checkout has the blocked P7-AD ledger
When the CLI runs with default paths
Then it writes blocked router JSON/Markdown and does not write product state.

Business rule: the default command is safe to run in the current checkout.

## Boundary Conditions To Confirm

- PDF, DOCX, and package manifest completions route back to the export/acceptance loop for the next explicit decision.
- Manual acceptance completion routes to a delivery completion gate.
- This node only records next-gate routing. It does not run the next gate, export PDF/DOCX, generate a package manifest, perform manual acceptance, or write `state/product/*`.

## Verification Plan

- RED: `python3 -m unittest tests.test_auto_mode_formal_package_verified_route_next_gate_router -v` fails before implementation because `Program.workbench.auto_mode_formal_package_verified_route_next_gate_router` does not exist.
- GREEN: implement a CLI-first next-gate router module and wrapper command.
- Regression: run P7-A through P7-AE unittest chain and Python compilation.
- Real run: default command reads current blocked P7-AD ledger and writes blocked P7-AE report/review.
