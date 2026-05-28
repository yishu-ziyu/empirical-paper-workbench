# P7-AI Auto Mode Formal Package Manifested Routed Next Gate Command Execute

## Goal

Consume the P7-AH manifested routed next-gate command preflight and run the planned next-gate command only after explicit confirmation.

## BDD Behaviors

### Behavior 1: Ready PDF command preflight creates a dry-run executable command

Given P7-AH prepared a command plan for `pdf_export`
When the execute gate runs in `dry-run` mode
Then it shows the delegated export/acceptance router command and does not run it.

Business rule: a ready command plan can be reviewed as a concrete CLI call before any command is executed.

### Behavior 2: Current blocked P7-AH output blocks command execution

Given the current checkout has a blocked P7-AH command preflight
When the execute gate runs
Then it does not run a delegated command and records no command execution.

Business rule: the current chain remains safe until P7-AG records an entry manifest and P7-AH becomes ready.

### Behavior 3: Missing or invalid P7-AH preflight blocks execution

Given the command preflight is missing, has the wrong schema, is not ready, or has blocking reasons
When the execute gate runs
Then it blocks before building or running any command.

Business rule: this node consumes only the P7-AH command preflight contract.

### Behavior 4: Command plan contract must be clean

Given the command plan is missing, duplicated, mismatched, already marked executed, or points at an unknown command
When the execute gate runs
Then it blocks as a command execution contract failure.

Business rule: exactly one reviewed command target is required before execution can be allowed.

### Behavior 5: Execute mode requires explicit confirmation and metadata

Given the command preflight is ready
When the execute gate runs in `execute` mode without confirmation, reviewer, or note
Then it blocks before running the delegated command.

Business rule: running the next gate is a separate auditable human-confirmed action.

### Behavior 6: Confirmed PDF execution runs the delegated next-gate command

Given P7-AH prepared a valid `pdf_export` command plan
When the execute gate runs in confirmed `execute` mode
Then it invokes the export/acceptance router command, captures its result, and writes only P7-AI report/review.

Business rule: P7-AI is the first node allowed to run the next-gate command, while still reporting delegated results explicitly.

### Behavior 7: Missing downstream command file blocks execution

Given P7-AH prepared a plan whose command file is not present in the repo
When the execute gate runs
Then it blocks and does not attempt execution.

Business rule: future gates can be planned before implementation, but cannot be executed until the command file exists.

### Behavior 8: CLI default reflects the current blocked P7-AH state

Given the current P7-AH output is blocked
When the CLI runs with default paths
Then it writes blocked execute JSON/Markdown and does not write product state.

Business rule: the default command is safe to run in the current checkout.

## Boundary Conditions To Confirm

- P7-AI may run only the command declared in the single P7-AH `next_gate_command_call_plan` item.
- `dry-run` never runs the delegated command.
- `execute` requires `--confirm-command-execute`, reviewer, and note.
- The delegated command must exist in the repo before execution.
- This node writes only its execute JSON and review Markdown; delegated commands may write their own reports if execution is explicitly confirmed.

## Verification Plan

- RED: `python3 -m unittest tests.test_auto_mode_formal_package_manifested_routed_next_gate_command_execute -v` fails before implementation because the P7-AI module does not exist.
- GREEN: implement the CLI-first manifested routed next-gate command execute gate.
- Regression: run P7-A through P7-AI unittest chain and Python compilation.
- Real run: default command reads the current blocked P7-AH report and writes a blocked P7-AI report/review.
