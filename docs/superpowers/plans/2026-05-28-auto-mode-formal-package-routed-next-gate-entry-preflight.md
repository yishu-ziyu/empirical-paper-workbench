# P7-AF Auto Mode Formal Package Routed Next Gate Entry Preflight

## Goal

Prepare the routed next Auto Mode gate entry from P7-AE without entering that gate.

## BDD Behaviors

### Behavior 1: Ready PDF next-gate route creates an entry preflight plan

Given P7-AE recorded a next-gate route for a verified `pdf_export`
When the routed next-gate entry preflight runs
Then it creates one entry plan for the export/acceptance router and does not enter the next gate.

Business rule: a clean P7-AE route can be prepared for handoff, but entry still needs a later explicit command.

### Behavior 2: Current blocked P7-AE router blocks entry preflight

Given the current checkout P7-AE router is blocked
When the entry preflight runs
Then it creates no entry plan and cannot request next-gate entry.

Business rule: the Auto Mode chain cannot advance when the route to the next gate has not been recorded.

### Behavior 3: Missing or invalid P7-AE router blocks entry preflight

Given the router report is missing, has the wrong schema, or is not route-recorded
When the entry preflight runs
Then it blocks before preparing a next-gate entry plan.

Business rule: this preflight consumes only a valid P7-AE router.

### Behavior 4: Next-gate route contract must be clean

Given P7-AE is route-recorded but the route object is missing, mismatched, not pending, or does not require an explicit command
When the entry preflight runs
Then it blocks as a routed next-gate entry contract failure.

Business rule: downstream commands need one clean pending route contract.

### Behavior 5: Unknown or mismatched next gate blocks entry preflight

Given P7-AE routes to an unsupported gate or pairs a gate with the wrong action
When the entry preflight runs
Then it blocks instead of guessing how to enter.

Business rule: gate entry commands must be explicitly mapped.

### Behavior 6: Manual acceptance route creates a delivery completion entry plan

Given P7-AE recorded a `manual_acceptance` route to the delivery completion gate
When the entry preflight runs
Then it prepares the delivery completion gate command, not another export loop command.

Business rule: manual acceptance finishes the route cycle and moves to delivery completion.

### Behavior 7: Boundary violations block entry preflight

Given the router indicates next-gate entry, export/acceptance execution, formal writeback, product-state permission, or boundary flags
When the entry preflight runs
Then it blocks and records no entry plan.

Business rule: this preflight must remain read-only and cannot hide side-effect signals from upstream.

### Behavior 8: CLI default reflects the current blocked P7-AE router

Given the current checkout has the blocked P7-AE router
When the CLI runs with default paths
Then it writes blocked entry preflight JSON/Markdown and does not write product state.

Business rule: the default command is safe to run in the current checkout.

## Boundary Conditions To Confirm

- PDF, DOCX, and package manifest routes prepare `auto_mode_formal_package_export_acceptance_router`.
- Manual acceptance prepares `auto_mode_formal_package_delivery_completion_gate`.
- This node does not enter the next gate, export PDF/DOCX, generate package manifests, perform acceptance, or write `state/product/*`.

## Verification Plan

- RED: `python3 -m unittest tests.test_auto_mode_formal_package_routed_next_gate_entry_preflight -v` fails before implementation because the P7-AF module does not exist.
- GREEN: implement the CLI-first routed next-gate entry preflight module and wrapper command.
- Regression: run P7-A through P7-AF unittest chain and Python compilation.
- Real run: default command reads current blocked P7-AE router and writes blocked P7-AF report/review.
