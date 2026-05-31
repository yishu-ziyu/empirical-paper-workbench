# P7-AU Auto Mode Formal Package Next Gate Route-Specific Artifact Verification Entry Result Review

## 目标

实现 `route-specific artifact verification entry result review`：只消费 P7-AT entry 和既有 route-specific artifact verification 输出，审阅验证结果是否可以进入 verified route completion ledger。默认当前真实仓库因 P7-AT blocked 而 blocked。

## BDD 行为

### 行为 1：已进入 verification 且 verification 干净时，放行给 ledger

Given P7-AT entry 已进入 route-specific artifact verification
And 既有 route-specific artifact verification 输出为 verified
When 运行 P7-AU result review
Then 生成 `route_specific_artifact_verification_entry_result_review_ready`
And 输出一个 `verified_route_completion_ledger_input_records` 记录。

业务规则：只有 verification 真的验证过路线产物，才允许进入 completion ledger。

### 行为 2：当前 P7-AT blocked 时，不输出 ledger 输入

Given 当前 P7-AT entry 是 blocked
When 运行 P7-AU result review
Then 返回 `blocked_by_route_specific_artifact_verification_entry`
And `verified_route_completion_ledger_input_records` 为空。

业务规则：上游 entry 未完成时，下游不能误认为 verification 已经可用。

### 行为 3：P7-AT 缺失、schema 错、未 entered 或有 blockers 时阻断

Given P7-AT entry 缺失、schema 错误、状态不是 entered，或包含 blocking reasons
When 运行 P7-AU result review
Then 阻断在 P7-AT entry 层。

业务规则：result review 必须先信任入口记录本身。

### 行为 4：entry 与 verification 输出的契约必须一致

Given P7-AT entry 和 verification report 的路径、状态、route type 或 summary 不一致
When 运行 P7-AU result review
Then 返回 `blocked_by_route_specific_artifact_verification_entry_result_contract`。

业务规则：不能把一次 entry 记录和另一份 verification 输出拼接成假的连续链路。

### 行为 5：verification 输出本身必须可被 ledger 接受

Given verification report 未 verified、artifact records 缺失、route flags 错误或有边界越界
When 运行 P7-AU result review
Then 返回 `blocked_by_route_specific_artifact_verification_output`。

业务规则：P7-AU 的放行条件要与既有 verified route completion ledger 的输入要求一致。

### 行为 6：P7-AU 只写 result review，不写 ledger 或 state/product

Given P7-AT entry 和 verification report 都干净
When 写出 P7-AU outputs
Then 只生成 P7-AU JSON 和 Markdown
And 不生成 verified route completion ledger
And 不写 `state/product/*`。

业务规则：本节点只做审阅，不替下游 ledger 执行。

### 行为 7：CLI 默认读取当前 blocked entry，写 blocked result review

Given CLI 未传自定义输入路径
And 默认 P7-AT entry 是 blocked
When 运行 P7-AU CLI
Then 写出 blocked result review
And stdout 显示不能进入 verified route completion ledger。

业务规则：当前真实仓库状态必须可复现为 blocked，不隐藏上游阻断。

## 待确认边界

- 本节点不直接调用 `auto_mode_formal_package_verified_route_completion_ledger.py`，只输出给它消费的记录。
- P7-AU 的 ledger 预检规则复用既有 verified route completion ledger 的判定口径。
- 当前真实运行预期为 blocked，因为 P7-AT 仍 blocked。
