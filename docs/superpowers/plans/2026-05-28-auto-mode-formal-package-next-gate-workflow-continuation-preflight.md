# P7-AK Auto Mode Formal Package Next Gate Workflow Continuation Preflight

## Goal

Consume the P7-AJ manifested next-gate command result review and produce a reviewable continuation plan for the next workflow node. This command does not run the continuation command, does not execute export / acceptance, and does not write product state.

## BDD Behaviors

### Behavior 1: Reviewed export router output creates continuation plan

Given P7-AJ reviewed a delegated `formal_package_export_acceptance_router` result for a supported route type
When P7-AK builds the continuation preflight
Then it creates one continuation plan pointing to `auto_mode_formal_package_selected_route_execution_preflight`.

Business rule: after a delegated export / acceptance router records a route, the next safe step is only a preflight for selected route execution.

### Behavior 2: Current blocked P7-AJ blocks continuation

Given the current P7-AJ report is blocked by P7-AI
When P7-AK builds the continuation preflight
Then it does not create a continuation plan and reports a blocked status.

Business rule: a blocked delegated-result review cannot be treated as permission to continue.

### Behavior 3: Missing, invalid, or not-ready P7-AJ blocks continuation

Given P7-AJ is missing, has the wrong schema, or is not `manifested_next_gate_command_result_review_ready`
When P7-AK builds the continuation preflight
Then it blocks before reading continuation contracts.

Business rule: P7-AK trusts only the P7-AJ result-review contract, not partial or ad hoc reports.

### Behavior 4: Result record must match the top-level P7-AJ contract

Given P7-AJ has a delegated result record that mismatches the top-level route, gate, status, or report path
When P7-AK builds the continuation preflight
Then it blocks with a continuation contract error.

Business rule: downstream routing must be based on one internally consistent delegated result.

### Behavior 5: Unsupported next gate or route blocks continuation

Given P7-AJ names an unknown next gate or a route type not supported by that gate
When P7-AK builds the continuation preflight
Then it blocks instead of inventing a continuation.

Business rule: continuation is allowed only for known workflow contracts.

### Behavior 6: Continuation preflight remains report-only

Given P7-AJ is ready
When P7-AK writes outputs
Then it writes only JSON and Markdown review files, without running the continuation command or writing `state/product`.

Business rule: P7-AK prepares handoff; it never performs the next action itself.

### Behavior 7: CLI default reflects current blocked P7-AJ state

Given the current repository P7-AJ output is blocked
When the CLI runs with default paths
Then stdout reports blocked continuation and zero continuation plan items.

Business rule: the live default command must be safe to run repeatedly while upstream remains blocked.

## Boundary Conditions

- P7-AK consumes only P7-AJ result review.
- P7-AK never runs `auto_mode_formal_package_selected_route_execution_preflight.py`.
- Export / acceptance router continuation maps to `auto_mode_formal_package_selected_route_execution_preflight`.
- Missing or empty delegated result records are blockers.
- Exactly one delegated result record is required for non-terminal continuation.
- Writes only JSON + Markdown; never writes `state/product/*`.

## Test Plan

- RED: `python3 -m unittest tests.test_auto_mode_formal_package_next_gate_workflow_continuation_preflight -v` fails before implementation because the P7-AK module does not exist.
- GREEN: implement the smallest builder + CLI that satisfies the behaviors above.
- Regression: run P7-A through P7-AK unittest chain and Python compilation.
- Real run: default command reads the current blocked P7-AJ report and writes a blocked P7-AK report/review.
