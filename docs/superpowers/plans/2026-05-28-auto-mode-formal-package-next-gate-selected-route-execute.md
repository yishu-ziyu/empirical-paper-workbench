# P7-AN Auto Mode Formal Package Next Gate Selected Route Execute

## Goal

Consume P7-AM workflow continuation result review and gate the explicit selected route execute command. This node may run `auto_mode_formal_package_selected_route_execute` only after P7-AM is ready and the user provides explicit confirmation, reviewer, and note. The selected route command itself records an execute manifest only; it must not render PDF/DOCX, generate package manifest content, perform manual acceptance, or write `state/product/*`.

## BDD Behaviors

1. Given P7-AM reviewed a selected route preflight as ready, when P7-AN runs in dry-run mode, then it previews the selected route execute command without running it.
   - Business rule: ready review creates a visible handoff to explicit selected route execution.
2. Given the current P7-AM report is blocked, when P7-AN runs, then it blocks and does not build or run a selected route execute command.
   - Business rule: blocked continuation result review cannot trigger selected route execution.
3. Given P7-AM is missing, has the wrong schema, is not ready, or has blockers, when P7-AN runs, then it blocks on the result review.
   - Business rule: P7-AN trusts only a completed P7-AM review.
4. Given P7-AM selected route preflight record is missing, duplicated, unknown, or path/status mismatched, when P7-AN runs, then it blocks on the selected route execute contract.
   - Business rule: selected route execution must be anchored to exactly one clean reviewed preflight record.
5. Given P7-AN is run in execute mode without confirmation or metadata, when it evaluates the request, then it blocks and does not run the command.
   - Business rule: selected route execution requires explicit human confirmation.
6. Given P7-AM is ready and execute is confirmed, when P7-AN runs, then it calls `auto_mode_formal_package_selected_route_execute`, records that command result, and the downstream selected-route manifest may be written.
   - Business rule: P7-AN only delegates to the selected route execute gate; it does not render or accept artifacts itself.
7. Given the selected route execute CLI is missing, when P7-AN evaluates a ready review, then it blocks before trying to run anything.
   - Business rule: missing delegated command is a hard local contract failure.
8. Given the CLI is run with the current blocked P7-AM report, when defaults are used, then it writes a blocked P7-AN report with zero command.
   - Business rule: the default local chain must reflect the current real blocked state.

## Boundary Conditions

- P7-AN consumes only P7-AM result review.
- P7-AN may run only `Program/auto_mode_formal_package_selected_route_execute.py`.
- P7-AN must pass the selected route preflight path recorded by P7-AM.
- P7-AN itself must not render PDF/DOCX, generate package manifest content, perform manual acceptance, or write `state/product/*`.
- Current real repository state is expected to remain blocked because P7-AM is blocked by P7-AL.

## Verification Plan

- RED: `python3 -m unittest tests.test_auto_mode_formal_package_next_gate_selected_route_execute -v` should fail because the P7-AN module does not exist yet.
- GREEN: implement the workbench module and CLI.
- Real blocked run: run the CLI against `Results/json/auto_mode_formal_package_next_gate_workflow_continuation_result_review.json`.
- Regression: run P7-A through P7-AN unittest suite.
