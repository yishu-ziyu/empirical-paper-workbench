# P7-AQ Auto Mode Formal Package Next Gate Route-Specific Artifact Executor Entry Result Review

## Goal

Add a result-review node after P7-AP. The node consumes the route-specific artifact executor entry report plus the artifact executor dry-run report and decides whether downstream may enter explicit route-specific artifact execution.

## Business Behaviors

1. Given P7-AP entered the artifact executor and the executor dry-run report is clean, when P7-AQ reviews both reports, then it emits one route-specific artifact execution record and allows the next gate.
   - 业务规则：只有 dry-run 已经被上一阶段真实触发并且结果干净，后续才可以对接显式 artifact execution。
2. Given the current P7-AP entry is blocked, when P7-AQ reviews it, then P7-AQ is blocked and emits no execution record.
   - 业务规则：上一阶段没进到 executor，就不能假装已有 dry-run 可审。
3. Given P7-AP is missing, invalid, not completed, or has source blockers, when P7-AQ reviews it, then entry review is blocked.
   - 业务规则：P7-AQ 只接收完成态 entry report。
4. Given P7-AP and the artifact executor report disagree on report path, review path, returncode, status, or route type, when P7-AQ reviews them, then the entry-result contract is blocked.
   - 业务规则：上一阶段记录和实际 dry-run report 必须指向同一个结果。
5. Given the artifact executor dry-run report is missing, invalid, dirty, or has already executed artifacts, when P7-AQ reviews it, then dry-run report review is blocked.
   - 业务规则：P7-AQ 只做放行审阅，不接受任何已执行 artifact 的结果。
6. Given P7-AQ writes outputs, when it runs, then it writes only result-review JSON and Markdown.
   - 业务规则：本节点不能导出 PDF/DOCX，不能生成 package manifest，不能执行人工验收，也不能写 `state/product/*`。
7. Given the CLI runs against the current blocked entry by default, when it writes outputs, then it reports blocked and no execution records.
   - 业务规则：当前真实仓库状态应保持停在 blocked，不推进正式产物执行。

## Boundary Conditions

- Do not run route-specific artifact commands from this node.
- Do not render PDF or DOCX.
- Do not generate formal package manifest.
- Do not perform manual acceptance.
- Do not write `state/product/*`.
- Downstream must require `status=route_specific_artifact_executor_entry_result_review_ready` and `can_continue_to_route_specific_artifact_execution=true` before consuming records.

## RED Record

The first target test run failed because `Program.workbench.auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review` did not exist.

## Verification

- Target test: `python3 -m unittest tests.test_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review -v`
- Real blocked CLI run against current repo state.
- P7 Auto Mode regression suite through P7-AQ.
- Python compile check for the new CLI and workbench module.
