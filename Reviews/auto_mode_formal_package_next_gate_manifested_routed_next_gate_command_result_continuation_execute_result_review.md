# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Result Continuation Execute Result Review

- 题目：
- 状态：`blocked_by_manifested_routed_next_gate_result_continuation_execute_gate`
- verified route type：``
- routed next gate：``
- continuation 状态：``
- selected route preflight 状态：``
- terminal 状态：``
- 已审阅 continuation 执行结果：false
- 可继续 after manifested routed continuation：false
- selected route preflight records：0
- terminal continuation records：0
- source 已运行 continuation：false
- source 已记录 terminal continuation：false
- 本命令运行 continuation：false
- 已执行 selected route：false
- 已执行导出/验收：false
- 本命令写入正式层：false
- 写入 state/product：false

## Blocking Reasons
- `manifested_routed_next_gate_result_continuation_execute_gate_not_completed`
- `verified_route_type_missing`
- `routed_next_gate_missing`
- `continuation_status_missing`
- `source_execute_gate_has_blocking_reasons`

## Next Action
- `resolve_p7_bg_execute_gate_blockers`: P7-BG must complete or record continuation before result review can continue.
