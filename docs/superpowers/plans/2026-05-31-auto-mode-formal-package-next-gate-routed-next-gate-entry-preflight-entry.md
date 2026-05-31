# Auto Mode Formal Package Next Gate Routed Next Gate Entry Preflight Entry

## 节点

P7-AZ：routed next gate entry preflight entry。

## 目标

把 P7-AY 的 result review 转成显式 routed next gate entry preflight entry。它只在 P7-AY 已审阅并放行时调用既有 `auto_mode_formal_package_routed_next_gate_entry_preflight.py`；当前真实 blocked 路径只记录阻断，不运行 preflight。

## BDD 行为

### 行为 1：ready P7-AY 会调用既有 preflight 并记录进入计划

Given P7-AY 已确认 routed next gate 可以交给 preflight
When 构建并运行 P7-AZ entry
Then 调用既有 preflight，输出 routed next gate entry plan，并标记可以请求进入 routed next gate。

业务规则：P7-AZ 不重新生成下一关进入计划，只把已审阅的 router 输出交给既有 preflight。

### 行为 2：当前 P7-AY blocked 时不运行 preflight

Given 当前 P7-AY 因 P7-AX blocked 而 blocked
When 构建 P7-AZ entry
Then 输出 blocked，不生成 preflight 命令执行结果。

业务规则：真实当前链路没有 ready review，不能跳过审阅门直接进入 preflight。

### 行为 3：P7-AY 缺失、schema 错、未 ready 或有 blockers 时阻断

Given P7-AY result review 缺失、schema 错、未 ready 或带 blocking reasons
When 构建 P7-AZ entry
Then 输出 `blocked_by_verified_route_next_gate_router_entry_result_review`。

业务规则：上一道审阅门必须明确放行。

### 行为 4：preflight input record 必须干净

Given P7-AY ready
When preflight input record 缺失、重复、路径错配、route 错配或 review status 不接受
Then 输出 contract blocked。

业务规则：preflight 只能消费一条已接受的 routed next gate input record。

### 行为 5：preflight command 不存在时阻断

Given P7-AY ready
When 既有 preflight CLI 文件不存在
Then 输出 command unavailable，且不尝试执行。

业务规则：不能在缺少执行入口时假装进入 preflight。

### 行为 6：既有 preflight 运行后仍 blocked 时不放行

Given P7-AY ready
When preflight CLI 运行后没有生成 ready preflight
Then 输出 preflight failure blocked。

业务规则：P7-AZ 的成功只以真实 preflight 输出为准。

### 行为 7：CLI 默认读取当前 blocked P7-AY 并写 blocked entry

Given 项目当前默认 P7-AY result review 仍 blocked
When 运行 P7-AZ CLI
Then 写出 JSON 和 Markdown entry，显示没有进入 routed next gate entry preflight。

业务规则：命令行入口可直接接入 Auto Mode，但不会误推进当前 blocked 链路。

## 边界条件

- P7-AZ 可以调用 existing preflight，但不执行 routed next gate entry command。
- 不进入下一关，不导出 PDF/DOCX，不生成 package manifest，不执行人工验收。
- 不写 `state/product/*`。
- 不重新运行 verified route next-gate router。
