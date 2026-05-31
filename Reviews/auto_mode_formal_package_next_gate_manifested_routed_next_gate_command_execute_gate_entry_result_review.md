# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Execute Gate Entry Result Review

- 题目：
- 状态：`blocked_by_manifested_routed_next_gate_command_execute_gate_entry`
- verified route type：``
- routed next gate：``
- delegated 状态：``
- command execute gate entry result 已审阅：false
- 可继续 manifested routed next gate command 后续流程：false
- delegated result records：0
- 本命令运行下一关命令：false
- 本命令写入正式层：false
- 写入 state/product：false

## Blocking Reasons
- `command_execute_gate_entry_not_completed`
- `command_execute_gate_entry_not_executed`
- `manifested_command_execute_not_completed`
- `next_gate_command_not_executed`
- `source_command_did_not_run_next_gate_command`
- `verified_route_type_missing`
- `routed_next_gate_missing`
- `delegated_report_path_missing`
- `source_command_execute_gate_entry_has_blocking_reasons`

## Next Action
- `resolve_manifested_routed_next_gate_command_execute_gate_entry_blockers`: P7-BD must complete before P7-BE can review the delegated command result.
