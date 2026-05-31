# Auto Mode Formal Package Next Gate Routed Next Gate Entry Preflight Entry Result Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add P7-BA as a read-only review gate between P7-AZ preflight entry and the later explicit routed next-gate entry gate.

**Architecture:** The workbench consumes exactly two JSON inputs: the P7-AZ preflight entry report and the existing routed next-gate entry preflight report. It writes only a P7-BA result-review JSON and Markdown review; it never enters the next gate, runs export/acceptance, renders files, or writes `state/product/*`.

**Tech Stack:** Python standard library, `unittest`, existing Auto Mode JSON/Markdown report conventions.

---

## BDD 行为用例

### 行为 1：ready P7-AZ + clean preflight 才能生成 explicit entry input

Given P7-AZ 已成功运行 routed next gate entry preflight，且既有 preflight 输出为 `ready_for_routed_next_gate_entry_review`
When P7-BA 审阅这两个结果
Then 输出 `routed_next_gate_entry_preflight_entry_result_review_ready`，并生成一个 `explicit_routed_next_gate_entry_input_records` 交给下游 explicit entry gate。

业务规则：P7-BA 的功能是“审阅可否交接”，不是直接进入下一关；只有上游入口和真实 preflight 输出都干净时才放行。

### 行为 2：当前 blocked P7-AZ 必须继续阻断

Given 当前仓库里的 P7-AZ entry 是 blocked
When P7-BA 审阅当前真实输入
Then 输出 `blocked_by_routed_next_gate_entry_preflight_entry`，且不生成 explicit entry input。

业务规则：不能因为已有历史 preflight 文件存在，就绕过当前 P7-AZ blocked 状态。

### 行为 3：P7-AZ 缺失、schema 错或未 entered 都阻断

Given P7-AZ entry 缺失、schema 不对、状态不是 `next_gate_routed_next_gate_entry_preflight_entered` 或带 blocking reasons
When P7-BA 审阅
Then 输出 `blocked_by_routed_next_gate_entry_preflight_entry`。

业务规则：下游只能接“真正跑过 preflight 的 P7-AZ entry”。

### 行为 4：P7-AZ 记录的 preflight 结果必须匹配既有 preflight 输出

Given P7-AZ entry 里的 preflight 路径、状态、returncode 或摘要与真实 preflight 输出不一致
When P7-BA 审阅
Then 输出 `blocked_by_routed_next_gate_entry_preflight_entry_result_contract`。

业务规则：P7-BA 要保护证据链，不能只看一个来源自称成功。

### 行为 5：preflight 输出必须满足 explicit entry 前置条件

Given 既有 preflight 输出 schema 错、状态未 ready、不能请求 entry、缺少 explicit command requirement 或 next gate entry plan 不干净
When P7-BA 审阅
Then 输出 preflight review 或 contract blocked 状态。

业务规则：P7-BA 交给下游的是“可进入 explicit entry gate 的计划”，不是任意 preflight 文件。

### 行为 6：任何正式层写入或越界信号都阻断

Given P7-AZ entry 或 preflight 输出显示进入下一关、执行导出/验收、写 formal state、写 product state 或 boundary flag 为 true
When P7-BA 审阅
Then 输出 `blocked_by_routed_next_gate_entry_preflight_entry_result_boundary`。

业务规则：P7-BA 是只读审阅门，不接受已经发生副作用的输入。

### 行为 7：P7-BA 只写 result review

Given 输入满足 ready 条件
When P7-BA 写出结果
Then 只生成 P7-BA JSON 和 Markdown review，不写 `state/product/*`。

业务规则：这个节点的产物只能被下游读取，不能修改正式产品状态。

### 行为 8：CLI 默认读取当前真实输入并写 blocked result review

Given 默认 CLI 参数读取当前仓库里的 P7-AZ entry 和 routed preflight output
When 运行 P7-BA CLI
Then 当前真实输出为 blocked，且明确显示没有 explicit entry input、没有进入下一关、没有写 product state。

业务规则：默认运行必须反映当前真实链路状态，不能制造 ready 假象。

## 需要用户确认的边界条件

- P7-BA 不调用 `auto_mode_formal_package_routed_next_gate_entry_execute.py`，只为后续 P7-BB 准备 input record。
- P7-BA 当前真实状态默认 blocked，因为 P7-AZ 当前真实输出是 blocked。
- P7-BA 的下游对接条件是 `status=routed_next_gate_entry_preflight_entry_result_review_ready` 且 `can_continue_to_explicit_routed_next_gate_entry=true`。

## TDD 执行清单

- [ ] 新增 `tests/test_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.py`，覆盖上述 8 条行为。
- [ ] 运行目标测试，确认因缺少 workbench 模块而 RED。
- [ ] 新增 `Program/workbench/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.py`。
- [ ] 新增 `Program/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.py`。
- [ ] 运行目标测试、真实 CLI、Python 编译和 `test_auto_mode_formal_package*.py` 回归。
- [ ] 更新 `Tasks/todo.md`，记录组件效果、真实状态、下游对接方式和验证命令。
