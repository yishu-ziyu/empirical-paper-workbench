# P7-AR Auto Mode Formal Package Next Gate Route-Specific Artifact Execution

## Goal

Add an explicit execution gate after P7-AQ. The node consumes the P7-AQ result review and runs the existing route-specific artifact executor in `execute` mode only when the review is ready and the execution request is explicitly confirmed.

## Business Behaviors

1. Given P7-AQ is ready, when P7-AR runs in dry-run mode, then it shows the artifact execution command without running it.
   - 业务规则：ready 只代表可以请求执行，不代表本节点默认执行产物。
2. Given the current P7-AQ result review is blocked, when P7-AR runs, then no artifact execution command is produced.
   - 业务规则：上游未放行时，不能绕过 result review 执行导出或验收。
3. Given P7-AQ is missing, invalid, not ready, or has blockers, when P7-AR runs, then execution is blocked.
   - 业务规则：P7-AR 只接收已批准的 P7-AQ result review。
4. Given the artifact execution record is missing, duplicated, mismatched, or not approved, when P7-AR runs, then the execution contract is blocked.
   - 业务规则：执行前必须有一条干净、可追溯的 route-specific artifact execution record。
5. Given P7-AR runs in execute mode, when confirmation or metadata is missing, then execution is blocked.
   - 业务规则：真实 artifact execution 必须有明确确认、reviewer 和 note。
6. Given P7-AR is confirmed and inputs are ready, when it runs, then it calls the existing artifact executor in execute mode and records the route output.
   - 业务规则：P7-AR 只封装执行门，实际路线动作仍由既有 artifact executor 负责。
7. Given the artifact executor command file is missing, when P7-AR runs, then execution is blocked before any subprocess call.
   - 业务规则：缺少执行器时不能部分执行。
8. Given the CLI reads the current blocked P7-AQ result by default, when it runs, then it writes a blocked execution report and review.
   - 业务规则：当前真实仓库状态应保持停住，不执行 artifact。

## Boundary Conditions

- Dry-run must not run the artifact executor.
- Execute mode must require `--confirm-artifact-execution`, `--reviewer`, and `--note`.
- Current real run must not write `state/product/*`.
- Current real run must not render PDF/DOCX, generate manifest, or perform manual acceptance.
- Downstream must read `Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution.json`.

## RED Record

The first target test run failed because `Program.workbench.auto_mode_formal_package_next_gate_route_specific_artifact_execution` did not exist.

## Verification

- Target test: `python3 -m unittest tests.test_auto_mode_formal_package_next_gate_route_specific_artifact_execution -v`
- Real blocked CLI run against current repo state.
- P7 Auto Mode regression suite through P7-AR.
- Python compile check for the new CLI and workbench module.
