# Auto Mode Formal Package Manifested Routed Next Gate Command Preflight

- 题目：
- 状态：`blocked_by_routed_next_gate_entry_manifest`
- verified route type：``
- 路由下一关：``
- 可请求执行下一关命令：false
- 需要单独 execute 命令：false
- 命令计划数：0
- 本命令运行下一关命令：false
- 已进入下一关：false
- 已执行导出/验收：false
- 本命令写入正式层：false
- 写入 state/product：false

## Blocking Reasons
- `routed_next_gate_entry_manifest_missing_or_invalid_schema`
- `routed_next_gate_entry_not_manifested`
- `routed_next_gate_entry_manifest_verified_route_type_missing`
- `routed_next_gate_entry_manifest_routed_next_gate_missing`

## Next Action
- `record_routed_next_gate_entry_manifest`: P7-AG must record an entry manifest before P7-AH can prepare a command plan.
