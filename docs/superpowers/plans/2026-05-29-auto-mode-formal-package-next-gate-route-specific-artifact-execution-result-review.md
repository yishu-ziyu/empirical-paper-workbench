# P7-AS Auto Mode Formal Package Next Gate Route-Specific Artifact Execution Result Review

## Goal

Review the P7-AR route-specific artifact execution report and the existing route-specific artifact executor output before allowing downstream artifact verification.

## BDD Behaviors

1. Given P7-AR executed a route-specific artifact and the artifact executor output is clean, when P7-AS reviews both reports, then it emits one artifact verification input record and allows the next gate.
   - 业务规则：路线产物执行成功后，必须先被审阅，才能进入产物验证。
2. Given the current P7-AR execution report is blocked, when P7-AS reviews it, then P7-AS blocks and emits no verification input record.
   - 业务规则：当前真实链路未执行产物时，不能假装进入验证。
3. Given P7-AR is missing, invalid, not completed, or has blockers, when P7-AS reviews it, then artifact execution result review is blocked.
   - 业务规则：P7-AS 只接受完成态 P7-AR execution report。
4. Given P7-AR and the artifact executor output disagree on paths, return code, status, route type, or summary, when P7-AS reviews them, then the result contract is blocked.
   - 业务规则：P7-AS 必须确认 P7-AR 记录的执行结果就是同一个 artifact executor 输出。
5. Given the artifact executor output is missing, invalid, not executed, dirty, or has route flag mismatches, when P7-AS reviews it, then artifact verification is blocked.
   - 业务规则：进入 verification 前，executor 输出必须明确表示某一路线产物已经执行完成。
6. Given P7-AS writes outputs, when it runs, then it writes only result-review JSON and Markdown.
   - 业务规则：P7-AS 只审阅执行结果，不验证 artifact、不重新导出、不写 `state/product/*`。
7. Given the CLI is run against the current blocked P7-AR output, when it uses defaults, then it writes a blocked result review.
   - 业务规则：真实项目当前仍应保持 blocked，等待上游解除。

## Boundary Conditions To Confirm Later

- Route types remain `pdf_export`, `docx_export`, `package_manifest`, and `manual_acceptance`.
- P7-AS checks the artifact executor output contract only; delegated artifact file fingerprints remain the responsibility of the existing route-specific artifact verification component.
- `manual_acceptance` may write product state in the delegated executor, but P7-AS itself must not write product state.

## Verification Plan

- Run the new target test first and confirm RED because the P7-AS module does not exist.
- Implement the smallest module and CLI wrapper to satisfy the behaviors.
- Run target tests, real CLI against current blocked inputs, Python compile, P7 regression, and scoped diff checks.
