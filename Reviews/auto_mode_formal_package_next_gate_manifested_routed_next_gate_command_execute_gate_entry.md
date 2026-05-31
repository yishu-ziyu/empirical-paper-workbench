# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Execute Gate Entry

- 题目：
- 状态：`blocked_by_manifested_routed_next_gate_run_preflight`
- verified route type：``
- routed next gate：``
- command execute gate entry 已执行：false
- manifested command execute status：``
- delegated command 数：0
- 已运行下一关命令：false
- 本命令运行下一关命令：false
- 已进入下一关：false
- 已执行导出/验收：false
- 本命令写入正式层：false
- 写入 state/product：false

## Blocking Reasons
- `manifested_routed_next_gate_run_preflight_not_ready`
- `manifested_routed_next_gate_run_preflight_not_reviewed`
- `manifested_routed_next_gate_run_preflight_cannot_request_execution`
- `manifested_routed_next_gate_run_preflight_missing_explicit_command_requirement`
- `manifested_routed_next_gate_run_preflight_verified_route_type_missing`
- `manifested_routed_next_gate_run_preflight_routed_next_gate_missing`
- `next_gate_command_call_plan_missing`
- `source_run_preflight_has_blocking_reasons`

## Next Action
- `resolve_manifested_routed_next_gate_run_preflight_blockers`: P7-BC must be ready before P7-BD can execute the routed next-gate command.
