# Auto Mode Formal Package Next Gate Verified Route Completion Ledger Entry Result Review

## 节点

P7-AW：verified route completion ledger entry result review。

## 目标

把 P7-AV 的 ledger entry 与既有 verified route completion ledger 输出做成只读审阅门。它不重新运行 ledger，也不进入 router；只判断 ledger 是否足够干净，可以交给下一道 verified route next gate router。

## BDD 行为

### 行为 1：ready P7-AV 和干净 ledger 才放行到 next gate router

Given P7-AV entry 已进入 verified route completion ledger，且既有 ledger 已记录一条完成路线
When 构建 P7-AW result review
Then 输出 `verified_route_completion_ledger_entry_result_review_ready`，并生成一条 router input record。

业务规则：router 不直接信任 P7-AV；必须先由 P7-AW 确认 entry 与 ledger 一致。

### 行为 2：当前 P7-AV blocked 时继续阻断

Given 当前 P7-AV entry 因 P7-AU blocked 而 blocked
When 构建 P7-AW result review
Then 不读取为可放行状态，不生成 router input record。

业务规则：真实当前链路还没有完成 ledger entry，P7-AW 不能把它推进到 router。

### 行为 3：P7-AV 缺失、schema 错、未完成或有 blockers 时阻断

Given P7-AV entry 缺失、schema 错误、状态未完成或带 blocking reasons
When 构建 P7-AW result review
Then 输出 `blocked_by_verified_route_completion_ledger_entry`。

业务规则：上一节点没完成时，下游只记录阻断原因。

### 行为 4：P7-AV 记录的 ledger 路径、状态和摘要必须匹配真实 ledger

Given P7-AV entry 声称 ledger 已记录
When ledger 路径、状态、returncode 或摘要与真实 ledger 不一致
Then 输出 contract blocked。

业务规则：不能只看上一节点的布尔值；必须核对实际 ledger 文件。

### 行为 5：ledger 本身必须是可路由的完成记录

Given ledger 文件存在
When schema 错、状态未 recorded、未允许进入下一 gate、记录缺失或 route mismatch
Then 输出 ledger review blocked。

业务规则：只有一条干净的 completion record 才能交给 router。

### 行为 6：任何正式层写入或边界越权标志都会阻断

Given P7-AV entry 或 ledger 带有正式写回、state/product 写入或边界越权标志
When 构建 P7-AW result review
Then 阻断，不生成 router input record。

业务规则：本节点只审阅，不写正式层，也不接受已经越权的上游结果。

### 行为 7：CLI 默认读取当前 blocked P7-AV 并写 blocked review

Given 项目当前默认 P7-AV entry 仍 blocked
When 运行 P7-AW CLI
Then 写出 JSON 和 Markdown review，显示不能继续到 next gate router。

业务规则：命令行入口可直接接入 Auto Mode，但不会误推进当前 blocked 链路。

## 边界条件

- 不运行 `auto_mode_formal_package_verified_route_next_gate_router.py`。
- 不重新运行 verified route completion ledger。
- 不导出 PDF/DOCX，不生成 package manifest，不执行人工验收。
- 不写 `state/product/*`。
- 只消费 P7-AV entry 与既有 ledger 输出。
