# Auto Mode Formal Package Next Gate Explicit Routed Next Gate Entry Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add P7-BB as the explicit entry gate that consumes P7-BA and only invokes the existing routed entry execute component after explicit confirmation.

**Architecture:** P7-BB reads only the P7-BA result-review JSON. If P7-BA is ready and the operator supplies confirmation metadata, P7-BB reconstructs the approved preflight handoff from P7-BA and delegates manifest recording to the existing routed next-gate entry execute workbench. Otherwise it writes a blocked P7-BB gate report and does not invoke execute.

**Tech Stack:** Python standard library, `unittest`, existing Auto Mode JSON/Markdown report conventions.

---

## BDD 行为用例

### 行为 1：ready P7-BA + 显式确认才调用 existing execute

Given P7-BA 已输出 ready result review，且包含一个 explicit routed next gate entry input record
When P7-BB 以 `execute` 模式运行，并带有 `--confirm-entry`、reviewer 和 note
Then P7-BB 调用既有 routed entry execute 逻辑，记录 execute report 和 entry manifest，但不运行下一关命令。

业务规则：P7-BB 是“显式入口门”，负责把 P7-BA 的可进入信号转成 manifest；它不负责运行下一关。

### 行为 2：当前 blocked P7-BA 必须继续阻断

Given 当前仓库里的 P7-BA result review 是 blocked
When P7-BB 默认运行
Then 输出 `blocked_by_routed_next_gate_entry_preflight_entry_result_review`，不调用 execute，不生成 manifest。

业务规则：不能绕过 P7-BA 的 blocked 状态直接进入 routed entry execute。

### 行为 3：P7-BA 缺失、schema 错或未 ready 都阻断

Given P7-BA result review 缺失、schema 不对、状态不是 ready 或不能继续 explicit entry
When P7-BB 审阅
Then 输出 `blocked_by_routed_next_gate_entry_preflight_entry_result_review`。

业务规则：P7-BB 的唯一入口是 P7-BA ready result review。

### 行为 4：P7-BA input record 必须与 entry plan 匹配

Given P7-BA ready，但 explicit input record 缺失、数量不为 1、路径/status/entry ids 与 entry plan 不一致
When P7-BB 审阅
Then 输出 `blocked_by_explicit_routed_next_gate_entry_input_contract`。

业务规则：P7-BB 只接受一个明确、可追溯的 explicit entry input。

### 行为 5：ready 但缺显式确认时不调用 execute

Given P7-BA ready
When P7-BB 以 execute 模式运行但缺少 `--confirm-entry`
Then 输出 `blocked_by_missing_explicit_routed_next_gate_entry_confirmation`，不调用 execute。

业务规则：进入 manifest 记录必须有人工显式确认。

### 行为 6：ready 且确认但缺 reviewer/note 时不调用 execute

Given P7-BA ready 且带 `--confirm-entry`
When reviewer 或 note 为空
Then 输出 `blocked_by_explicit_routed_next_gate_entry_metadata`，不调用 execute。

业务规则：manifest 记录必须留下审核人和确认说明。

### 行为 7：P7-BB 不能接受越界或副作用信号

Given P7-BA result review 显示已执行 explicit entry、已进入下一关、写 formal state、写 product state 或 boundary flag 为 true
When P7-BB 审阅
Then 输出 `blocked_by_explicit_routed_next_gate_entry_boundary`。

业务规则：P7-BB 只能从干净的只读审阅结果继续。

### 行为 8：CLI 默认读取当前真实 P7-BA 并写 blocked gate report

Given 默认 CLI 参数读取当前仓库里的 P7-BA result review
When 运行 P7-BB CLI
Then 当前真实输出为 blocked，且显示没有调用 execute、没有生成 manifest、没有进入下一关、没有写 product state。

业务规则：默认运行必须反映当前真实链路状态。

## 需要用户确认的边界条件

- P7-BB ready 且显式确认后只记录 routed entry manifest，不运行下一关命令。
- P7-BB 默认不会进入 execute，因为当前 P7-BA blocked。
- P7-BB 的下游对接条件是 `status=explicit_routed_next_gate_entry_manifest_recorded` 且 `routed_next_gate_entry_manifest_recorded=true`。

## TDD 执行清单

- [ ] 新增 `tests/test_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate.py`，覆盖上述 8 条行为。
- [ ] 运行目标测试，确认因缺少 workbench 模块而 RED。
- [ ] 新增 `Program/workbench/auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate.py`。
- [ ] 新增 `Program/auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate.py`。
- [ ] 运行目标测试、真实 CLI、Python 编译和 `test_auto_mode_formal_package*.py` 回归。
- [ ] 更新 `Tasks/todo.md`，记录组件效果、真实状态、下游对接方式和验证命令。
