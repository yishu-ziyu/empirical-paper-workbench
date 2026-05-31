# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Result Continuation Execute Result Downstream Gate Entry Execute Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build P7-BJ as the explicit execute gate that consumes P7-BI downstream gate entry records and either delegates export routes to selected-route execution or records manual terminal product-review preparation.

**Architecture:** P7-BJ reads only P7-BI. Export records may dry-run or, with explicit confirmation metadata, call the existing selected-route execute command using the selected-route preflight report path from the P7-BI input record. Manual terminal records never run external commands; execute mode records product-review preparation only.

**Tech Stack:** Python stdlib, unittest, CLI-first JSON/Markdown reports.

---

## BDD 行为

1. Given P7-BI is ready with an export downstream input, When P7-BJ runs in dry-run, Then it shows the selected-route execution command without running it. 业务规则：export 分支进入显式执行预览，不直接导出。
2. Given P7-BI is ready with a manual terminal downstream input, When P7-BJ runs in dry-run, Then it shows product-review preparation readiness without external command. 业务规则：manual terminal 不回到导出命令。
3. Given current P7-BI is blocked, When P7-BJ reads default input, Then it blocks and does not create an execution action. 业务规则：真实当前状态不能伪装可继续。
4. Given P7-BI is missing, invalid, not ready, or has blockers, When P7-BJ validates source, Then it blocks at downstream gate entry validation. 业务规则：只消费干净的 P7-BI。
5. Given the downstream input record is missing, duplicated, wrong kind, wrong route, or not aligned with the source report path, When P7-BJ validates the record, Then it blocks. 业务规则：执行门只能由唯一且可追踪的下游输入驱动。
6. Given execute mode is requested without explicit confirmation, reviewer, or note, When P7-BJ validates the request, Then it blocks before external execution or record writing. 业务规则：任何执行或产品审阅准备记录都需要明确人工元数据。
7. Given a ready export input and confirmed execute request, When P7-BJ runs, Then it delegates to selected-route execute and records the delegated result without writing product state. 业务规则：export 执行动作委托给既有 selected-route execute。
8. Given a ready manual terminal input and confirmed execute request, When P7-BJ runs, Then it records product-review preparation without running external commands or writing product state. 业务规则：manual terminal 只形成后续产品审阅准备记录。

## Boundary Conditions

- Current real input remains blocked because P7-BI is blocked.
- Export execute calls the existing selected-route execute CLI; it does not call artifact export commands directly.
- Manual terminal execute records product-review preparation only.
- No PDF/DOCX/package manifest/manual acceptance action happens inside P7-BJ.

## Tasks

### Task 1: RED tests

**Files:**
- Create: `tests/test_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate.py`

- [x] Write unittest cases for the eight BDD behaviors.
- [x] Run `python3 -m unittest tests.test_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate -v`.
- [x] Expected: fail because `Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate` is missing.

### Task 2: Minimal implementation

**Files:**
- Create: `Program/workbench/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate.py`
- Create: `Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate.py`

- [x] Implement source validation, downstream input contract validation, execute request validation, delegated selected-route execute, manual product-review preparation record, JSON/Markdown writers, and CLI output.
- [x] Run target unittest until green.

### Task 3: Real run and record

**Files:**
- Modify: `Tasks/todo.md`
- Create: `Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate.md`
- Create: `notes/session-logs/2026-05-31-p7-bj-manifested-routed-next-gate-command-result-continuation-execute-result-downstream-gate-entry-execute-gate.md`

- [x] Run the real CLI against current P7-BI output.
- [x] Run formal-package regression tests.
- [x] Record actual component effect, current blocked output, verification, and next P7-BK pause point.
