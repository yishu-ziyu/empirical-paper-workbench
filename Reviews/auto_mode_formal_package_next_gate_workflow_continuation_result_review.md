# Auto Mode Formal Package Next Gate Workflow Continuation Result Review

- 题目：
- 状态：`blocked_by_next_gate_workflow_continuation_execute`
- verified route type：``
- 路由下一关：``
- continuation 状态：``
- selected route preflight 状态：``
- 已审阅 continuation 结果：false
- 可继续 selected route execution：false
- selected route preflight records：0
- source 已运行 continuation：false
- 本命令运行 continuation：false
- 已执行 selected route：false
- 已执行导出/验收：false
- 本命令写入正式层：false
- 写入 state/product：false

## Blocking Reasons
- `next_gate_workflow_continuation_execute_not_completed`
- `workflow_continuation_not_executed`
- `source_execute_did_not_run_continuation`
- `continuation_returncode_not_zero`
- `verified_route_type_missing`
- `routed_next_gate_missing`
- `continuation_report_path_missing`
- `continuation_status_missing`
- `source_execute_has_blocking_reasons`

## Next Action
- `resolve_workflow_continuation_execute_blockers`: P7-AL must complete a continuation command before result review can continue.
