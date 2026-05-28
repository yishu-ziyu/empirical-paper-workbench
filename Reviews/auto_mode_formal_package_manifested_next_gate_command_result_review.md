# Auto Mode Formal Package Manifested Next Gate Command Result Review

- 题目：
- 状态：`blocked_by_manifested_next_gate_command_execute`
- verified route type：``
- 路由下一关：``
- delegated 状态：``
- 已审阅 delegated 结果：false
- 可继续下一关后续流程：false
- delegated result records：0
- 本命令运行下一关命令：false
- 本命令写入正式层：false
- 写入 state/product：false

## Blocking Reasons
- `manifested_next_gate_command_execute_not_completed`
- `next_gate_command_not_executed`
- `this_command_did_not_run_next_gate_command`
- `delegated_returncode_not_zero`
- `verified_route_type_missing`
- `routed_next_gate_missing`
- `delegated_report_path_missing`
- `delegated_status_missing`
- `source_execute_has_blocking_reasons`

## Next Action
- `resolve_manifested_next_gate_command_execute_blockers`: P7-AI must complete a delegated next-gate command before result review can continue.
