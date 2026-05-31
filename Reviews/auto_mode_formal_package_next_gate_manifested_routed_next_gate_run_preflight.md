# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Run Preflight

- 题目：
- 状态：`blocked_by_explicit_routed_next_gate_entry_gate`
- verified route type：``
- routed next gate：``
- run preflight 已审阅：false
- 可请求执行下一关命令：false
- 需要单独 execute 命令：false
- 命令计划数：0
- run input records：0
- 本命令运行下一关命令：false
- 已进入下一关：false
- 已执行导出/验收：false
- 本命令写入正式层：false
- 写入 state/product：false

## Blocking Reasons
- `explicit_routed_next_gate_entry_gate_not_manifest_recorded`
- `explicit_routed_next_gate_entry_gate_not_executed`
- `explicit_routed_next_gate_entry_execute_status_not_recorded`
- `explicit_routed_next_gate_entry_gate_verified_route_type_missing`
- `explicit_routed_next_gate_entry_gate_routed_next_gate_missing`
- `routed_next_gate_entry_manifest_path_missing`
- `explicit_routed_next_gate_entry_operations_missing`
- `explicit_routed_next_gate_entry_gate_has_blocking_reasons`

## Next Action
- `resolve_explicit_routed_next_gate_entry_gate_blockers`: P7-BB must record the routed next-gate entry manifest before P7-BC can continue.
