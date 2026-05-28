# Auto Mode Formal Package Manifested Routed Next Gate Command Execute

- 题目：
- 状态：`blocked_by_manifested_routed_next_gate_command_preflight`
- 模式：`dry-run`
- verified route type：``
- 路由下一关：``
- 可确认执行下一关命令：false
- delegated command 数：0
- 已运行下一关命令：false
- 本命令运行下一关命令：false
- delegated returncode：None
- delegated status：``
- 已进入下一关：false
- 已执行导出/验收：false
- 本命令写入正式层：false
- 写入 state/product：false

## Blocking Reasons
- `manifested_routed_next_gate_command_preflight_not_ready`
- `manifested_routed_next_gate_command_preflight_cannot_request_execution`
- `manifested_routed_next_gate_command_preflight_missing_explicit_command_requirement`
- `source_preflight_has_blocking_reasons`

## Next Action
- `resolve_manifested_routed_next_gate_command_preflight_blockers`: P7-AH must be ready before P7-AI can run a delegated next-gate command.
