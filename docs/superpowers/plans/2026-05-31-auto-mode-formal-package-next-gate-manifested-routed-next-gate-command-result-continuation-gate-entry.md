# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Result Continuation Gate Entry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build P7-BF as a read-only continuation gate entry that consumes P7-BE and emits downstream continuation input records.

**Architecture:** P7-BF reads only the P7-BE result review. It validates that P7-BE is ready, confirms one delegated result record matches the top-level route/status/path contract, then creates continuation input records without running the next command or writing product state.

**Tech Stack:** Python stdlib, unittest, CLI-first JSON/Markdown reports.

---

## BDD 行为

1. Given P7-BE 已审阅 export router 输出并可继续, When P7-BF 构建 continuation gate entry, Then 生成一条指向 `auto_mode_formal_package_selected_route_execution_preflight` 的 continuation input record。业务规则：PDF/DOCX/package manifest 路线继续进入选中路线执行预检。
2. Given P7-BE 已审阅 delivery completion 输出并可继续, When P7-BF 构建 continuation gate entry, Then 生成一条 terminal delivery completion continuation input record，但不要求再运行 continuation command。业务规则：manual acceptance 完成后进入交付完成记录，不回到导出执行链。
3. Given 当前真实 P7-BE blocked, When P7-BF 读取默认输入, Then 阻断且不生成 continuation input。业务规则：上一关未通过不能伪造后续输入。
4. Given P7-BE 缺失、schema 错或未 ready, When P7-BF 校验输入, Then 以 P7-BE result review blocker 阻断。业务规则：只接受明确通过审阅的 P7-BE。
5. Given delegated result record 与顶层 route/gate/status/path 不一致, When P7-BF 校验合约, Then 阻断。业务规则：后续输入必须能追溯到同一条 delegated result。
6. Given routed gate 或 route type 未知, When P7-BF 校验 continuation contract, Then 阻断。业务规则：未知后续路线不能进入主链路。
7. Given P7-BE 出现运行命令、进入下一关或写正式层的副作用信号, When P7-BF 校验边界, Then 阻断。业务规则：P7-BE 必须是只读审阅节点。
8. Given P7-BF 写出 report/review, When 文件落盘, Then 只写 P7-BF 自己的 JSON/Markdown，不运行 continuation、不写 `state/product/*`。业务规则：本节点只准备输入，不执行后续动作。

## Boundary Conditions

- 本节点不运行 `auto_mode_formal_package_selected_route_execution_preflight.py`。
- 本节点不导出 PDF/DOCX，不生成 package manifest，不执行 manual acceptance。
- 本节点不写 `state/product/*`。
- 当前真实输入来自 P7-BE blocked 结果，所以真实 CLI 应输出 blocked。

## Tasks

### Task 1: RED tests

**Files:**
- Create: `tests/test_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry.py`

- [ ] Write unittest cases for the eight BDD behaviors.
- [ ] Run `python3 -m unittest tests.test_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry -v`.
- [ ] Expected: fail because `Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry` is missing.

### Task 2: Minimal implementation

**Files:**
- Create: `Program/workbench/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry.py`
- Create: `Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry.py`

- [ ] Implement result review validation, boundary validation, continuation contract validation, continuation input record creation, JSON/Markdown writers, and CLI output.
- [ ] Run target unittest until green.

### Task 3: Real run and record

**Files:**
- Modify: `Tasks/todo.md`
- Create: `Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry.md`
- Create: `notes/session-logs/2026-05-31-p7-bf-manifested-routed-next-gate-command-result-continuation-gate-entry.md`

- [ ] Run the real CLI against current P7-BE output.
- [ ] Run formal-package regression tests.
- [ ] Record actual component effect, current blocked output, downstream handoff, verification, and next P7-BG pause point.
