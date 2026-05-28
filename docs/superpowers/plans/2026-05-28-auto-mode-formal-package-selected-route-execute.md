# Auto Mode Formal Package Selected Route Execute Gate Plan

Date: 2026-05-28

## Node Goal

P7-AA consumes the P7-Z selected route execution preflight and creates an explicit selected-route execute gate.

This node separates `dry-run` from confirmed `execute`. The confirmed execution mode only records a selected-route execute manifest for a later route-specific artifact executor. It does not render PDF, export DOCX, generate the final package manifest, perform manual acceptance, mutate formal manuscript sources, bibliography, project bibliography, DesignSpec, RunPlan, product state, model outputs, or statistical execution artifacts.

## BDD Behaviors

### Behavior 1: Ready preflight supports dry-run route planning

Given P7-Z selected route preflight is ready for route execution review
When Auto Mode runs selected route execute in `dry-run` mode
Then the status is `selected_route_execute_dry_run_ready`
And it lists the selected route operation
And no export or acceptance is performed.

Business rule: ready 后也必须先能看清楚要执行哪一条正式包路线。

### Behavior 2: DOCX, package manifest, and manual routes map cleanly

Given P7-Z preflight selects DOCX, package manifest, or manual acceptance
When Auto Mode builds the execute gate
Then each route maps to one operation with the expected route type and planned output.

Business rule: 后续 route-specific executor 能直接按 route type 对接。

### Behavior 3: Current blocked preflight blocks execution

Given the current P7-Z output is blocked
When Auto Mode runs selected route execute
Then the status is `blocked_by_selected_route_execution_preflight`
And no selected route operation is created.

Business rule: P7-AA 不能绕过 P7-Z 的阻断。

### Behavior 4: Missing, invalid, or unready preflight blocks execution

Given P7-Z preflight is missing, has the wrong schema, or is not ready
When Auto Mode builds the execute gate
Then it blocks before creating operations.

Business rule: execute gate 只接受一份干净的 P7-Z ready contract。

### Behavior 5: Execute requires explicit confirmation

Given P7-Z preflight is ready
When Auto Mode runs in `execute` mode without confirmation
Then it blocks with a missing confirmation reason.

Business rule: execute 不能由默认参数或误触发完成。

### Behavior 6: Execute requires reviewer and note

Given P7-Z preflight is ready
And confirmation is present
But reviewer or note is missing
When Auto Mode runs in `execute` mode
Then it blocks with metadata reasons.

Business rule: 执行层必须留下可追溯的人和说明。

### Behavior 7: Bad selected route plan contract blocks execution

Given the selected route plan is unknown, duplicated, already marked for execution, missing a command, or missing outputs
When Auto Mode builds the execute gate
Then it blocks before dry-run or execute can continue.

Business rule: route-specific executor 只能消费一条明确、未执行、可追踪的路线。

### Behavior 8: Confirmed execute records manifest only

Given P7-Z preflight is ready
And `--confirm-execute`, reviewer, and note are present
When outputs are written
Then the execute JSON, review Markdown, and execute manifest are written
And no PDF, DOCX, final package manifest, manual acceptance report, formal state, or product state is written.

Business rule: P7-AA 只记录 selected route execute manifest，真实产物执行留给后续节点。

### Behavior 9: CLI default reflects current blocked preflight

Given the current P7-Z preflight is blocked
When the CLI runs with default paths
Then it writes a blocked selected route execute report
And reports no execute manifest and no formal package artifacts created.

Business rule: 当前真实状态应继续停在阻断处，而不是伪造正式包执行。

## Boundary Conditions

- Requires `p7.auto_mode_formal_package_selected_route_execution_preflight.v1`.
- Requires `status=ready_for_selected_formal_package_route_execution_review` before dry-run ready or execute manifest.
- Requires exactly one selected route execution plan item.
- Requires route type in PDF, DOCX, package manifest, or manual acceptance.
- Requires `mode=execute`, `--confirm-execute`, reviewer, and note before execute manifest can be recorded.
- No PDF/DOCX rendering in this node.
- No final package manifest generation in this node.
- No manual acceptance in this node.
- No `state/product/*` writeback.
- No model execution or statistical artifact overwrite.

## Verification

- RED: `python3 -m unittest tests.test_auto_mode_formal_package_selected_route_execute -v` fails before implementation because `Program.workbench.auto_mode_formal_package_selected_route_execute` does not exist.
- GREEN: target tests pass after minimal selected-route execute gate implementation.
- Real run writes `Results/json/auto_mode_formal_package_selected_route_execute.json` and `Reviews/auto_mode_formal_package_selected_route_execute.md` with current status blocked by P7-Z preflight.
