# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Result Continuation Execute Result Downstream Gate Entry Execute Gate

- 题目：
- 状态：`blocked_by_manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry`
- mode：`dry-run`
- verified route type：``
- routed next gate：``
- downstream kind：``
- 可确认执行 downstream：false
- 需要显式 downstream command：false
- downstream execute command 数：0
- downstream command 已执行：false
- 本命令运行 downstream command：false
- downstream execute returncode：None
- downstream execute status：``
- selected route execute manifest 已记录：false
- product review preparation 已记录：false
- 已执行 selected route：false
- 已执行导出/验收：false
- 写入 state/product：false

## Blocking Reasons
- `manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry_not_ready`
- `manifested_routed_next_gate_downstream_gate_entry_not_recorded`
- `manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry_cannot_request_downstream`
- `source_downstream_gate_entry_has_blocking_reasons`

## Next Action
- `resolve_p7_bi_downstream_gate_entry_blockers`: P7-BI must be ready before P7-BJ can execute or record downstream action.
