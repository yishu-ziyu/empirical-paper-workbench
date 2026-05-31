# Auto Mode Formal Package Next Gate Verified Route Next-Gate Router Entry

## 节点

P7-AX：verified route next-gate router entry。

## 目标

把 P7-AW 的 result review 转成显式 router entry。它只在 P7-AW 已审阅并放行时调用既有 `auto_mode_formal_package_verified_route_next_gate_router.py`；当前真实 blocked 路径只记录阻断，不运行 router。

## BDD 行为

### 行为 1：ready P7-AW 会调用既有 router 并记录下一关路由

Given P7-AW 已确认 completion ledger 可以交给 router
When 构建并运行 P7-AX entry
Then 调用既有 router，输出下一关路由记录，并标记可以进入 routed next gate。

业务规则：P7-AX 不重新判断导出路线，只把已审阅的 ledger 交给既有 router。

### 行为 2：当前 P7-AW blocked 时不运行 router

Given 当前 P7-AW 因 P7-AV blocked 而 blocked
When 构建 P7-AX entry
Then 输出 blocked，不生成 router 命令执行结果。

业务规则：真实当前链路没有 ready review，不能跳过审阅门直接路由。

### 行为 3：P7-AW 缺失、schema 错、未 ready 或有 blockers 时阻断

Given P7-AW result review 缺失、schema 错、未 ready 或带 blocking reasons
When 构建 P7-AX entry
Then 输出 `blocked_by_verified_route_completion_ledger_entry_result_review`。

业务规则：上一道审阅门必须明确放行。

### 行为 4：router input record 必须干净

Given P7-AW ready
When router input record 缺失、重复、路径错配、route 错配或 review status 不接受
Then 输出 contract blocked。

业务规则：router 只能消费一条已接受的 ledger input record。

### 行为 5：router command 不存在时阻断

Given P7-AW ready
When 既有 router CLI 文件不存在
Then 输出 command unavailable，且不尝试执行。

业务规则：不能在缺少执行入口时假装进入下一关路由。

### 行为 6：既有 router 运行失败或输出未 recorded 时不放行

Given P7-AW ready
When router CLI 运行后没有生成 `verified_route_next_gate_route_recorded`
Then 输出 router failure blocked。

业务规则：P7-AX 的成功只以真实 router 输出为准。

### 行为 7：CLI 默认读取当前 blocked P7-AW 并写 blocked entry

Given 项目当前默认 P7-AW result review 仍 blocked
When 运行 P7-AX CLI
Then 写出 JSON 和 Markdown entry，显示没有进入 router。

业务规则：命令行入口可直接接入 Auto Mode，但不会误推进当前 blocked 链路。

## 边界条件

- P7-AX 可以调用 existing router，但不进入 routed next gate 的下一道命令。
- 不导出 PDF/DOCX，不生成 package manifest，不执行人工验收。
- 不写 `state/product/*`。
- 不重跑 verified route completion ledger。
