# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Result Continuation Execute Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build P7-BG as the explicit execute gate that consumes P7-BF continuation input and either runs export-route continuation or records manual terminal continuation.

**Architecture:** P7-BG reads only the P7-BF gate entry. It validates one continuation input record, supports dry-run previews, requires explicit confirmation plus reviewer/note for execute mode, runs the selected-route preflight command only for export-router routes, and records manual terminal continuation without external command execution or product-state writeback.

**Tech Stack:** Python stdlib, unittest, CLI-first JSON/Markdown reports.

---

## BDD 行为

1. Given P7-BF ready for export-router continuation, When P7-BG runs in dry-run, Then it builds the selected-route preflight command but does not run it. 业务规则：先预览后执行，避免自动推进。
2. Given P7-BF ready for manual terminal continuation, When P7-BG runs in dry-run, Then it shows terminal continuation readiness without external command. 业务规则：manual acceptance 完成后不再回到导出执行链。
3. Given current P7-BF is blocked, When P7-BG reads default input, Then it blocks and does not run continuation. 业务规则：上一关未通过不能继续。
4. Given P7-BF is missing, invalid, not ready, or has blockers, When P7-BG validates input, Then it blocks at gate-entry validation. 业务规则：只接受干净的 P7-BF。
5. Given continuation input record is missing, duplicated, mismatched, or marked as already run, When P7-BG validates contract, Then it blocks. 业务规则：后续执行必须由一条干净输入驱动。
6. Given execute mode lacks confirmation, reviewer, or note, When P7-BG receives request, Then it blocks before execution. 业务规则：执行 continuation 必须有人确认。
7. Given export-router continuation is confirmed, When P7-BG executes, Then it runs `auto_mode_formal_package_selected_route_execution_preflight.py` and records its result without writing product state. 业务规则：只进入后续预检，不执行导出验收。
8. Given manual terminal continuation is confirmed, When P7-BG executes, Then it records terminal continuation and does not spawn an external command. 业务规则：终态交付记录仍不等于产品状态写回。

## Boundary Conditions

- P7-BG 当前真实输入应 blocked，因为 P7-BF 当前 blocked。
- Export-route execute only runs selected-route execution preflight, not selected-route execute.
- Manual terminal continuation records completion readiness, but does not write `state/product/*`.
- No PDF/DOCX/package manifest/manual acceptance action happens in this node.

## Tasks

### Task 1: RED tests

**Files:**
- Create: `tests/test_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate.py`

- [ ] Write unittest cases for the eight BDD behaviors.
- [ ] Run `python3 -m unittest tests.test_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate -v`.
- [ ] Expected: fail because `Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate` is missing.

### Task 2: Minimal implementation

**Files:**
- Create: `Program/workbench/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate.py`
- Create: `Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate.py`

- [ ] Implement input validation, continuation record contract validation, request confirmation checks, export-route command execution, manual terminal recording, JSON/Markdown writers, and CLI output.
- [ ] Run target unittest until green.

### Task 3: Real run and record

**Files:**
- Modify: `Tasks/todo.md`
- Create: `Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate.md`
- Create: `notes/session-logs/2026-05-31-p7-bg-manifested-routed-next-gate-command-result-continuation-execute-gate.md`

- [ ] Run the real CLI against current P7-BF output.
- [ ] Run formal-package regression tests.
- [ ] Record actual component effect, current blocked output, verification, and next P7-BH pause point.
