# P7-AL Auto Mode Formal Package Next Gate Workflow Continuation Execute

## Goal

Consume the P7-AK continuation preflight and provide an explicit execution gate for the next workflow continuation command. Dry-run only previews the continuation command. Execute mode requires explicit confirmation plus reviewer metadata before running the continuation command.

## BDD Behaviors

### Behavior 1: Ready continuation preflight creates a dry-run command

Given P7-AK is ready and contains one selected-route continuation plan
When P7-AL runs in dry-run mode
Then it exposes the continuation command but does not run it.

Business rule: users can inspect the next workflow command before it changes any outputs.

### Behavior 2: Current blocked P7-AK blocks execution

Given the current P7-AK report is blocked
When P7-AL runs
Then it does not expose or run a continuation command.

Business rule: blocked continuation preflight cannot be bypassed by the execute gate.

### Behavior 3: Missing, invalid, or not-ready P7-AK blocks execution

Given P7-AK is missing, has the wrong schema, is not ready, or has source blockers
When P7-AL validates the input
Then it blocks before command planning.

Business rule: continuation execution trusts only the P7-AK preflight contract.

### Behavior 4: Continuation plan contract must be clean

Given the P7-AK continuation plan is missing, duplicated, mismatched, or marked as already running work
When P7-AL validates it
Then it blocks with a continuation execute contract error.

Business rule: P7-AL can run only one known, pending, report-only continuation command.

### Behavior 5: Execute mode requires confirmation and metadata

Given P7-AK is ready
When P7-AL runs in execute mode without confirmation, reviewer, or note
Then it blocks without running the continuation command.

Business rule: crossing from plan to command execution requires an explicit human action record.

### Behavior 6: Confirmed execution runs the continuation command and records the result

Given P7-AK is ready and the delegated router report exists
When P7-AL runs in confirmed execute mode
Then it runs `auto_mode_formal_package_selected_route_execution_preflight`, records its return code and status, and does not execute export / acceptance itself.

Business rule: P7-AL may run only the next preflight command, not the route execution command that follows it.

### Behavior 7: Missing continuation command file blocks execution

Given P7-AK is ready but the command file is unavailable
When P7-AL validates command availability
Then it blocks without attempting to run.

Business rule: unavailable local commands must be surfaced as repairable blockers.

### Behavior 8: CLI default reflects current blocked P7-AK state

Given the current repository P7-AK output is blocked
When the CLI runs with default paths
Then stdout reports blocked execution and zero continuation command items.

Business rule: the live default command is safe to rerun while upstream remains blocked.

## Boundary Conditions

- P7-AL consumes only P7-AK continuation preflight.
- P7-AL can run only the command named by the validated continuation plan.
- P7-AL does not execute selected route export / acceptance.
- P7-AL writes only its own JSON/Markdown report; the continuation command may write its own preflight outputs when explicitly executed.
- P7-AL never writes `state/product/*`.

## Test Plan

- RED: `python3 -m unittest tests.test_auto_mode_formal_package_next_gate_workflow_continuation_execute -v` fails before implementation because the P7-AL module does not exist.
- GREEN: implement the smallest builder + runner + CLI that satisfies the behaviors above.
- Regression: run P7-A through P7-AL unittest chain and Python compilation.
- Real run: default command reads the current blocked P7-AK report and writes a blocked P7-AL report/review.
