# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Result Continuation Execute Result Downstream Gate Entry

- 题目：
- 状态：`blocked_by_manifested_routed_next_gate_result_continuation_execute_result_review`
- verified route type：``
- routed next gate：``
- downstream kind：``
- downstream status：``
- downstream gate entry 已记录：false
- 可请求 continuation downstream：false
- 需要显式 downstream command：false
- downstream input records：0
- 本命令运行 downstream command：false
- 已执行 selected route：false
- 已执行导出/验收：false
- 本命令写入正式层：false
- 写入 state/product：false

## Blocking Reasons
- `manifested_routed_next_gate_result_continuation_execute_result_review_not_ready`
- `manifested_routed_next_gate_result_continuation_execute_result_not_reviewed`
- `manifested_routed_next_gate_result_continuation_execute_result_review_cannot_continue`
- `verified_route_type_missing`
- `routed_next_gate_missing`
- `source_result_review_has_blocking_reasons`

## Next Action
- `resolve_p7_bh_result_review_blockers`: P7-BH must be ready before P7-BI can create downstream input.
