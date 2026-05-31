# Auto Mode Formal Package Next Gate Verified Route Next-Gate Router Entry Result Review

## 节点

P7-AY：verified route next-gate router entry result review。

## 目标

把 P7-AX entry 和既有 verified route next-gate router 输出做成只读审阅门。它只在 P7-AX 确认已运行 router、且 router 已记录 routed next gate 时，才生成给 routed next gate entry preflight 使用的 input record；当前真实 blocked 路径只记录阻断。

## BDD 行为

### 行为 1：ready P7-AX 和干净 router 输出才放行

Given P7-AX 已进入 verified route next-gate router，且 router 输出已记录下一关路由
When 构建 P7-AY result review
Then 输出 ready，并生成一条 routed next gate entry preflight input record。

业务规则：P7-AY 不选择路由，只审阅 P7-AX 与 router 输出是否一致。

### 行为 2：当前 P7-AX blocked 时继续阻断

Given 当前 P7-AX 因 P7-AW blocked 而 blocked
When 构建 P7-AY result review
Then 输出 blocked，不生成 preflight input record。

业务规则：真实当前链路没有 router 结果，不能跳过 entry result review。

### 行为 3：P7-AX 缺失、schema 错、未 entered 或有 blockers 时阻断

Given P7-AX entry 缺失、schema 错、未 entered 或带 blocking reasons
When 构建 P7-AY result review
Then 输出 `blocked_by_verified_route_next_gate_router_entry`。

业务规则：上一道 entry 必须证明 router 已经真实完成。

### 行为 4：P7-AX 记录的 router 路径、状态和摘要必须匹配真实 router

Given P7-AX entry 标记已进入 router
When 它记录的 router report path、status 或 summary 与真实 router 不一致
Then 输出 contract blocked。

业务规则：不能只相信 entry 自述，必须对照 router 输出。

### 行为 5：router 输出必须满足 routed next gate preflight 的输入要求

Given P7-AX entry 干净
When router 输出 schema、状态、route record 或 next gate route contract 不干净
Then 输出 router review blocked 或 preflight contract blocked。

业务规则：只有既有 preflight 也会接受的 router 输出才能继续。

### 行为 6：正式层写入或越界标志会阻断

Given entry 或 router 出现进入下一关、导出验收、正式写入或 state/product 写入信号
When 构建 P7-AY result review
Then 输出 boundary blocked。

业务规则：P7-AY 是只读审阅门，不能消费已经产生后续副作用的输入。

### 行为 7：只写 result review

Given P7-AY 输入 ready
When 写出 P7-AY 结果
Then 只写 JSON 和 Markdown，不运行 routed next gate preflight，不写 `state/product/*`。

业务规则：后续 preflight 必须由下一节点显式执行。

### 行为 8：CLI 默认读取当前 blocked P7-AX 并写 blocked review

Given 项目当前默认 P7-AX entry 仍 blocked
When 运行 P7-AY CLI
Then 写出 blocked result review，显示没有继续到 routed next gate preflight。

业务规则：命令行入口可直接接入 Auto Mode，但不会误推进当前 blocked 链路。

## 边界条件

- P7-AY 不运行 routed next gate entry preflight。
- 不进入下一关，不导出 PDF/DOCX，不生成 package manifest，不执行人工验收。
- 不写 `state/product/*`。
- 不重新运行 verified route next-gate router。
