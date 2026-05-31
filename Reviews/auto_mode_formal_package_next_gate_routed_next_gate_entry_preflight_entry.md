# Auto Mode Formal Package Next Gate Routed Next Gate Entry Preflight Entry

- 题目：
- 状态：`blocked_by_verified_route_next_gate_router_entry_result_review`
- verified route type：``
- routed next gate：``
- 可进入 routed next gate entry preflight：false
- preflight command 已执行：false
- 本命令运行 routed next gate entry preflight：false
- preflight status：``
- 可请求进入 routed next gate：false
- next gate entry plan 数：0
- 写入 state/product：false

## Blocking Reasons
- `verified_route_next_gate_router_entry_result_review_not_ready`
- `verified_route_next_gate_router_entry_result_not_reviewed`
- `result_review_cannot_continue_to_routed_next_gate_entry_preflight`
- `result_review_router_status_not_recorded`
- `result_review_next_gate_route_not_recorded`
- `result_review_cannot_enter_routed_next_gate`
- `routed_next_gate_missing`
- `verified_route_type_missing`
- `verified_route_type_unknown:`
- `route_completion_record_count_missing`
- `next_gate_route_missing`
- `source_result_review_has_blocking_reasons`

## Next Action
- `resolve_verified_route_next_gate_router_entry_result_review_blockers`: P7-AY must accept one routed next-gate router result before preflight entry can run.
