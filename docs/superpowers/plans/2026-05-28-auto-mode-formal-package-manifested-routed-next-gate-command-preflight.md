# P7-AH Auto Mode Formal Package Manifested Routed Next Gate Command Preflight

## Goal

Turn a P7-AG routed next-gate entry manifest into a reviewed next-gate command call plan without running that command.

## BDD Behaviors

### Behavior 1: Ready PDF entry manifest creates a next-gate command preflight plan

Given P7-AG recorded an entry manifest for a verified `pdf_export`
When the command preflight runs
Then it prepares the export/acceptance router command call plan and does not run the command.

Business rule: the manifest can be translated into an executable command shape, but execution is still a later explicit step.

### Behavior 2: Current missing P7-AG entry manifest blocks command preflight

Given the current checkout has no P7-AG entry manifest
When the command preflight runs
Then it creates no command plan and cannot request command execution.

Business rule: downstream next-gate commands cannot be inferred without a recorded entry manifest.

### Behavior 3: Missing or invalid entry manifest blocks command preflight

Given the manifest is missing, has the wrong schema, or is not marked as manifested
When the command preflight runs
Then it blocks before preparing a command plan.

Business rule: this node consumes only the P7-AG entry manifest contract.

### Behavior 4: Entry manifest boundary violations block command preflight

Given the manifest says a next gate was already entered, a command was already run, or product/formal state can be written
When the command preflight runs
Then it blocks and records no command plan.

Business rule: a preflight cannot hide side-effect signals from the manifest.

### Behavior 5: Entry operation contract must be clean

Given the manifest operation is missing, duplicated, unknown, mismatched, or already marked as runnable by this command
When the command preflight runs
Then it blocks as a command contract failure.

Business rule: the next node needs exactly one clean command target.

### Behavior 6: Manual acceptance entry creates delivery completion command plan

Given P7-AG recorded a manual acceptance entry manifest
When the command preflight runs
Then it prepares the delivery completion gate command plan, not the export/acceptance router.

Business rule: manual acceptance exits the export loop and moves toward delivery completion.

### Behavior 7: Writing the command preflight remains report-only

Given a ready entry manifest
When command preflight outputs are written
Then only the preflight JSON and review Markdown are written.

Business rule: this node records the call plan only; it does not run commands or create workspace manifests.

### Behavior 8: CLI default reflects the current missing manifest

Given the current checkout has no P7-AG entry manifest
When the CLI runs with default paths
Then it writes blocked command preflight JSON/Markdown and does not write product state.

Business rule: the default command is safe to run in the current checkout.

## Boundary Conditions To Confirm

- PDF, DOCX, and package manifest routes map to `Program/auto_mode_formal_package_export_acceptance_router.py`.
- Manual acceptance maps to `Program/auto_mode_formal_package_delivery_completion_gate.py`, even if that downstream command is implemented later.
- This node never runs the command, never exports or accepts artifacts, and never writes `state/product/*`.

## Verification Plan

- RED: `python3 -m unittest tests.test_auto_mode_formal_package_manifested_routed_next_gate_command_preflight -v` fails before implementation because the P7-AH module does not exist.
- GREEN: implement the CLI-first manifested routed next-gate command preflight.
- Regression: run P7-A through P7-AH unittest chain and Python compilation.
- Real run: default command reads the missing current P7-AG manifest and writes blocked P7-AH report/review.
