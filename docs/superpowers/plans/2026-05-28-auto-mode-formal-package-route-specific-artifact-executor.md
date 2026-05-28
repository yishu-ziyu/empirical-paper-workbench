# Auto Mode Formal Package Route-Specific Artifact Executor Plan

Date: 2026-05-28

## Node Goal

P7-AB consumes the P7-AA selected route execute report and execute manifest, then dispatches exactly one selected formal-package route to the existing route-specific artifact command.

This node keeps `dry-run` as the default. Confirmed `execute` delegates to the existing PDF, DOCX, package manifest, or manual acceptance command for the selected route. It does not invent artifact formats or bypass the P7-AA execute manifest.

## BDD Behaviors

### Behavior 1: Ready execute manifest supports dry-run route dispatch planning

Given P7-AA recorded a selected route execute manifest
When Auto Mode runs the route-specific artifact executor in `dry-run` mode
Then the status is `route_specific_artifact_executor_dry_run_ready`
And it shows the delegated command for the selected route
And no artifact command runs.

Business rule: 后续节点能看清楚要调用哪一个真实产物命令，但默认不写产物。

### Behavior 2: Current blocked P7-AA output blocks the executor

Given the current P7-AA output is blocked
When Auto Mode runs the route-specific artifact executor
Then the status is `blocked_by_selected_route_execute`
And no delegated command runs.

Business rule: P7-AB 不能绕过 P7-AA 的 execute manifest。

### Behavior 3: Missing or invalid execute report / manifest blocks execution

Given the selected route execute report or manifest is missing or has the wrong schema
When Auto Mode builds the executor report
Then it blocks before route dispatch.

Business rule: 真实产物执行只接受可审计的 P7-AA 输出。

### Behavior 4: Bad selected route operation contract blocks execution

Given the manifest has zero, multiple, unknown, already-executed, or incomplete route operations
When Auto Mode builds the executor report
Then it blocks before route dispatch.

Business rule: route-specific executor 只能处理一条明确、未执行、可追踪的路线。

### Behavior 5: Execute requires explicit confirmation, reviewer, and note

Given P7-AA manifest is ready
When Auto Mode runs in `execute` mode without confirmation, reviewer, or note
Then it blocks with request metadata reasons.

Business rule: 真实产物写入必须有单独确认和可追溯说明。

### Behavior 6: Confirmed PDF and DOCX routes delegate to artifact commands

Given P7-AA manifest selects PDF or DOCX
And the route-specific inputs are ready
When Auto Mode runs confirmed `execute`
Then it delegates to the PDF or DOCX command
And writes the expected formal package artifact.

Business rule: P7-AB 是从路线到账面产物的真实执行入口。

### Behavior 7: Confirmed package manifest and manual acceptance routes delegate to artifact commands

Given P7-AA manifest selects package manifest or manual acceptance
And the route-specific inputs are ready
When Auto Mode runs confirmed `execute`
Then it writes the package manifest or records the manual acceptance decision through the existing command.

Business rule: 最终包清单和人工验收也走同一 selected route 执行入口。

### Behavior 8: CLI default reflects current blocked execute report

Given the current P7-AA output is blocked
When the CLI runs with default paths
Then it writes a blocked executor report and review
And does not run any route-specific artifact command.

Business rule: 当前真实状态继续停在阻断处，不伪造正式包产物。

## Boundary Conditions

- Requires `p7.auto_mode_formal_package_selected_route_execute.v1`.
- Requires `p7.auto_mode_formal_package_selected_route_execute_manifest.v1`.
- Requires exactly one route operation.
- Route type must be one of `pdf_export`, `docx_export`, `package_manifest`, or `manual_acceptance`.
- `dry-run` never runs delegated artifact commands.
- `execute` requires `--confirm-artifact-execution`, reviewer, and note.
- Manual acceptance uses the existing manual acceptance command and may write its existing product-state acceptance record only when that route is selected and confirmed.
- Current real checkout remains blocked because P7-AA has not recorded an execute manifest.

## Verification

- RED: `python3 -m unittest tests.test_auto_mode_formal_package_route_specific_artifact_executor -v` fails before implementation because `Program.workbench.auto_mode_formal_package_route_specific_artifact_executor` does not exist.
- GREEN: target tests pass after minimal route-specific artifact executor implementation.
- Real run writes `Results/json/auto_mode_formal_package_route_specific_artifact_executor.json` and `Reviews/auto_mode_formal_package_route_specific_artifact_executor.md` with current status blocked by P7-AA.
