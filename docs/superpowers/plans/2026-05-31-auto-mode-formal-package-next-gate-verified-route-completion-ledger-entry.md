# P7-AV Auto Mode Formal Package Next Gate Verified Route Completion Ledger Entry

## 目标

实现 `verified route completion ledger entry`：只消费 P7-AU result review，ready 时调用既有 `auto_mode_formal_package_verified_route_completion_ledger.py`，把已验证路线登记到 completion ledger。默认当前真实仓库因 P7-AU blocked 而 blocked。

## BDD 行为

### 行为 1：ready P7-AU 会调用既有 completion ledger 并记录成功结果

Given P7-AU result review 已确认 verification 可进入 completion ledger
And 既有 route-specific artifact verification report 可被 ledger 接受
When 运行 P7-AV ledger entry
Then 它调用既有 completion ledger CLI
And 输出 `next_gate_verified_route_completion_ledger_entered`。

业务规则：P7-AV 是进入 ledger 的执行入口，不重新实现 ledger 规则。

### 行为 2：当前 P7-AU blocked 时，不运行 completion ledger

Given 当前 P7-AU result review 是 blocked
When 运行 P7-AV ledger entry
Then 返回 `blocked_by_route_specific_artifact_verification_entry_result_review`
And ledger command 为空且未执行。

业务规则：上游 verification result review 未放行时，不能误登记 completion ledger。

### 行为 3：P7-AU 缺失、schema 错、未 ready 或有 blockers 时阻断

Given P7-AU result review 缺失、schema 错误、状态不是 ready，或包含 blocking reasons
When 运行 P7-AV ledger entry
Then 阻断在 P7-AU result review 层。

业务规则：P7-AV 必须先信任上游审阅记录。

### 行为 4：ledger input record 合约必须干净

Given P7-AU 的 `verified_route_completion_ledger_input_records` 缺失、重复、路径错、状态错或未放行
When 运行 P7-AV ledger entry
Then 返回 `blocked_by_verified_route_completion_ledger_entry_contract`。

业务规则：completion ledger 的输入必须是一条明确、可追踪的 verification result。

### 行为 5：completion ledger 命令文件缺失时阻断

Given P7-AU ready
And completion ledger CLI 不存在
When 构建 P7-AV entry
Then 返回 `blocked_by_verified_route_completion_ledger_command_unavailable`。

业务规则：缺少既有 ledger 命令时不能假装已登记。

### 行为 6：既有 ledger 运行后仍 blocked 时，P7-AV 不放行

Given P7-AU ready
And 既有 ledger CLI 运行后产出 blocked ledger report
When 运行 P7-AV ledger entry
Then 返回 `blocked_by_verified_route_completion_ledger_failure`
And 记录 ledger status 和 blocking reasons。

业务规则：执行命令不等于通过，必须以 ledger 输出为准。

### 行为 7：CLI 默认读取当前 blocked P7-AU，写 blocked ledger entry

Given CLI 未传自定义输入路径
And 默认 P7-AU result review 是 blocked
When 运行 P7-AV CLI
Then 写出 blocked entry
And stdout 显示没有运行 completion ledger。

业务规则：当前真实仓库状态必须可复现为 blocked。

## 待确认边界

- P7-AV 会在 ready 时调用既有 completion ledger CLI；它本身不重新实现 ledger 记录规则。
- P7-AV 只写自己的 entry JSON/Markdown，并可能通过既有 CLI 写 ledger JSON/Markdown；不写 `state/product/*`。
- 当前真实运行预期为 blocked，因为 P7-AU 仍 blocked。
