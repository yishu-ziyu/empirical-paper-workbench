# P7-AJ Auto Mode Formal Package Manifested Next Gate Command Result Review

## Goal

Consume the P7-AI manifested next-gate command execute report and review the delegated next-gate output without running any command.

## BDD Behaviors

### Behavior 1: Executed PDF next-gate command with route-recorded output is review-ready

Given P7-AI executed the export/acceptance router command for `pdf_export`
When the result review reads the execute report and delegated router report
Then it marks the delegated output as reviewed and allows continuation.

Business rule: downstream gates must trust a reviewed delegated result, not just a subprocess return code.

### Behavior 2: Current blocked P7-AI output blocks result review

Given the current checkout has a blocked P7-AI execute report
When the result review runs
Then it records no delegated result record and cannot continue.

Business rule: if the command did not run, there is no delegated output to trust.

### Behavior 3: Missing or invalid P7-AI execute report blocks review

Given the execute report is missing, has the wrong schema, is not completed, or has blocking reasons
When the result review runs
Then it blocks before reading delegated output as valid.

Business rule: this node consumes only completed P7-AI execution evidence.

### Behavior 4: Execute report contract must match one known next gate

Given P7-AI claims a route type, gate id, report path, or delegated status that does not match the known next-gate contract
When the result review runs
Then it blocks as a result contract failure.

Business rule: a delegated report must belong to the planned gate and route.

### Behavior 5: Delegated report must be valid and successful

Given P7-AI ran a command but the delegated report is missing, has the wrong schema, has blocking reasons, or is not in a success status
When the result review runs
Then it blocks and explains the delegated report problem.

Business rule: a subprocess returning zero is not enough; the delegated report itself must be valid.

### Behavior 6: Writing result review remains report-only

Given a review-ready delegated result
When result review outputs are written
Then only the result review JSON and review Markdown are written.

Business rule: this node reviews evidence only; it does not run commands or write product state.

### Behavior 7: CLI default reflects the current blocked P7-AI state

Given the current P7-AI output is blocked
When the CLI runs with default paths
Then it writes blocked result review JSON/Markdown and does not write product state.

Business rule: the default command is safe to run in the current checkout.

## Boundary Conditions To Confirm

- P7-AJ never runs delegated commands.
- P7-AJ consumes only P7-AI execute report plus the delegated report path recorded by P7-AI.
- Export/acceptance router success means `formal_package_export_acceptance_route_recorded`.
- Missing delegated report path is a blocker, not an implicit success.
- This node writes only its result review JSON and review Markdown.

## Verification Plan

- RED: `python3 -m unittest tests.test_auto_mode_formal_package_manifested_next_gate_command_result_review -v` fails before implementation because the P7-AJ module does not exist.
- GREEN: implement the CLI-first manifested next-gate command result review.
- Regression: run P7-A through P7-AJ unittest chain and Python compilation.
- Real run: default command reads the current blocked P7-AI report and writes a blocked P7-AJ report/review.
