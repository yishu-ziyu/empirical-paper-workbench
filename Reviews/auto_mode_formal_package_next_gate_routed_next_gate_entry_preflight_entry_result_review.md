# Auto Mode Formal Package Next Gate Routed Next Gate Entry Preflight Entry Result Review

- 题目：
- 状态：`blocked_by_routed_next_gate_entry_preflight_entry`
- verified route type：``
- routed next gate：``
- preflight status：``
- 已审阅 preflight entry result：false
- 可继续 explicit routed next gate entry：false
- 可请求进入 routed next gate：false
- 需要 explicit next gate entry command：false
- next gate entry plan 数：0
- explicit entry input records：0
- 已执行 explicit routed next gate entry：false
- 本命令进入下一关：false
- 写入 state/product：false

## Blocking Reasons
- `routed_next_gate_entry_preflight_entry_not_entered`
- `routed_next_gate_entry_preflight_entry_did_not_allow_preflight`
- `routed_next_gate_entry_preflight_entry_command_not_executed`
- `preflight_entry_did_not_run_routed_next_gate_entry_preflight`
- `routed_next_gate_entry_preflight_returncode_not_zero`
- `routed_next_gate_entry_preflight_status_not_ready`
- `preflight_entry_cannot_request_routed_next_gate_entry`
- `preflight_entry_missing_explicit_next_gate_entry_requirement`
- `verified_route_type_missing`
- `routed_next_gate_missing`
- `preflight_entry_next_gate_entry_plan_missing`
- `routed_next_gate_entry_preflight_report_path_missing`
- `routed_next_gate_entry_preflight_review_path_missing`
- `routed_next_gate_entry_preflight_status_missing`
- `source_preflight_entry_has_blocking_reasons`

## Next Action
- `resolve_routed_next_gate_entry_preflight_entry_blockers`: P7-AZ must prove that routed next-gate entry preflight ran successfully.
