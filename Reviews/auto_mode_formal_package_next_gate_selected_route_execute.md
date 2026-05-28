# Auto Mode Formal Package Next Gate Selected Route Execute

- 题目：
- 状态：`blocked_by_workflow_continuation_result_review`
- 模式：`dry-run`
- verified route type：``
- 路由下一关：``
- 可确认执行 selected route：false
- selected route execute command 数：0
- 已运行 selected route execute command：false
- 本命令运行 selected route execute command：false
- selected route execute returncode：None
- selected route execute status：``
- selected route execute manifest 已记录：false
- 已执行 selected route：false
- 已执行导出/验收：false
- 已渲染 PDF：false
- 已渲染 DOCX：false
- 已生成 package manifest：false
- 已执行人工验收：false
- 本命令写入正式层：false
- 写入 state/product：false

## Blocking Reasons
- `workflow_continuation_result_review_not_ready`
- `workflow_continuation_result_not_reviewed`
- `workflow_continuation_result_cannot_continue_to_selected_route_execution`
- `workflow_continuation_not_executed`
- `source_result_review_has_blocking_reasons`

## Next Action
- `resolve_workflow_continuation_result_review_blockers`: P7-AM must be ready before P7-AN can run selected route execute.
