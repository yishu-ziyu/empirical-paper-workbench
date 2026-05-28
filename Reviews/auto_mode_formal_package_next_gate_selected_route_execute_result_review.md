# Auto Mode Formal Package Next Gate Selected Route Execute Result Review

- 题目：
- 状态：`blocked_by_next_gate_selected_route_execute`
- verified route type：``
- selected route execute status：``
- selected route execute result 已审阅：false
- 可进入 route-specific artifact executor：false
- selected route execute command 已执行：false
- 本命令运行 selected route execute command：false
- selected route execute manifest 已记录：false
- route-specific artifact executor input 数：0
- 已运行 artifact executor：false
- 已执行导出/验收：false
- 已渲染 PDF：false
- 已渲染 DOCX：false
- 已生成 package manifest：false
- 已执行人工验收：false
- 本命令写入正式层：false
- 写入 state/product：false

## Blocking Reasons
- `next_gate_selected_route_execute_not_completed`
- `selected_route_execute_command_not_executed`
- `source_execute_did_not_run_selected_route_execute_command`
- `selected_route_execute_returncode_not_zero`
- `selected_route_execute_status_not_manifest_recorded`
- `selected_route_execute_manifest_not_recorded`
- `verified_route_type_missing`
- `routed_next_gate_missing`
- `selected_route_execute_report_path_missing`
- `selected_route_execute_review_path_missing`
- `selected_route_execute_manifest_path_missing`
- `source_next_gate_selected_route_execute_has_blocking_reasons`

## Next Action
- `resolve_next_gate_selected_route_execute_blockers`: P7-AN must execute selected route manifest recording before P7-AO can continue.
