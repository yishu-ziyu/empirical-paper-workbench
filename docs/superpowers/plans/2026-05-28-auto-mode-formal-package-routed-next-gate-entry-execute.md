# P7-AG Auto Mode Formal Package Routed Next Gate Entry Execute Gate

## Goal

Record an explicit routed next-gate entry manifest from P7-AF without running the next gate command.

## BDD Behaviors

### Behavior 1: Ready PDF entry preflight supports dry-run planning

Given P7-AF prepared an entry plan for a verified `pdf_export`
When the entry execute gate runs in dry-run mode
Then it shows the export/acceptance router entry operation and does not record a manifest.

Business rule: an operator can preview the next gate entry before confirming it.

### Behavior 2: Current blocked P7-AF preflight blocks entry execution

Given the current checkout P7-AF preflight is blocked
When the entry execute gate runs
Then it records no entry operation and no manifest.

Business rule: the chain cannot advance when the next-gate entry preflight is not ready.

### Behavior 3: Missing or invalid P7-AF preflight blocks entry execution

Given the preflight report is missing, has the wrong schema, or is not ready
When the entry execute gate runs
Then it blocks before preparing any entry operation.

Business rule: the execute gate consumes only a valid P7-AF preflight.

### Behavior 4: Execute mode requires explicit confirmation

Given P7-AF is ready
When the entry execute gate runs in execute mode without confirmation
Then it blocks and records no manifest.

Business rule: entering the next Auto Mode gate is never implicit.

### Behavior 5: Execute mode requires reviewer and note

Given P7-AF is ready and confirmation is present
When reviewer or note metadata is missing
Then it blocks and records no manifest.

Business rule: a next-gate entry handoff must be auditable.

### Behavior 6: Entry plan contract must be clean

Given P7-AF is ready but its entry plan is duplicated, unknown, already marked as entered, or lacks a command
When the entry execute gate runs
Then it blocks as a routed next-gate entry contract failure.

Business rule: downstream entry handoff needs one clean pending operation.

### Behavior 7: Confirmed manual acceptance entry records a manifest only

Given P7-AF prepared a manual acceptance route to the delivery completion gate
When the entry execute gate runs with confirmation, reviewer, and note
Then it writes a routed next-gate entry manifest and does not run the delivery completion command.

Business rule: this node records the handoff, not the next gate's work.

### Behavior 8: CLI default reflects the current blocked P7-AF preflight

Given the current checkout has the blocked P7-AF preflight
When the CLI runs with default paths
Then it writes blocked JSON/Markdown and no entry manifest.

Business rule: the default command is safe to run in the current checkout.

## Boundary Conditions To Confirm

- PDF, DOCX, and package manifest entries point to `auto_mode_formal_package_export_acceptance_router`.
- Manual acceptance entry points to `auto_mode_formal_package_delivery_completion_gate`.
- This node may write only the P7-AG report/review and, when confirmed, a workspace manifest. It does not run the next gate, export/accept anything, or write `state/product/*`.

## Verification Plan

- RED: `python3 -m unittest tests.test_auto_mode_formal_package_routed_next_gate_entry_execute -v` fails before implementation because the P7-AG module does not exist.
- GREEN: implement the CLI-first routed next-gate entry execute gate.
- Regression: run P7-A through P7-AG unittest chain and Python compilation.
- Real run: default command reads current blocked P7-AF preflight and writes blocked P7-AG report/review.
