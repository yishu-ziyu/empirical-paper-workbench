# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Result Continuation Gate Entry

- 题目：
- 状态：`blocked_by_manifested_routed_next_gate_command_result_review`
- verified route type：``
- routed next gate：``
- delegated 状态：``
- continuation gate entry 已记录：false
- 可请求 manifested routed next gate result continuation：false
- 需要显式 continuation command：false
- continuation input records：0
- 已运行 continuation：false
- 本命令运行 continuation：false
- 本命令写入正式层：false
- 写入 state/product：false

## Blocking Reasons
- `manifested_routed_next_gate_command_result_review_not_ready`
- `manifested_routed_next_gate_command_result_not_reviewed`
- `manifested_routed_next_gate_command_result_review_cannot_continue`
- `manifested_routed_next_gate_command_not_executed`
- `verified_route_type_missing`
- `routed_next_gate_missing`
- `delegated_status_missing`
- `source_result_review_has_blocking_reasons`

## Next Action
- `resolve_manifested_routed_next_gate_command_result_review_blockers`: P7-BE must accept the delegated result before continuation input can be prepared.
