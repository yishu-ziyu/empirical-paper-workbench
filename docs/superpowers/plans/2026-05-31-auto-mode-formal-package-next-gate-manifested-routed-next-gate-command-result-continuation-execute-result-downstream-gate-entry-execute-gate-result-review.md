# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Result Continuation Execute Result Downstream Gate Entry Execute Gate Result Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build P7-BK as the result-review node that consumes P7-BJ and decides whether downstream selected-route execution or product-review preparation can continue.

**Architecture:** P7-BK reads P7-BJ plus, for export routes only, the selected-route execute report and manifest. It writes only its own JSON/Markdown review. It never runs selected-route execute, artifact execution, export commands, manual acceptance, or product-state writes.

**Tech Stack:** Python stdlib, unittest, CLI-first JSON/Markdown reports.

---

## BDD 行为

1. Given P7-BJ completed an export downstream selected-route execute and the selected-route execute report/manifest are clean, When P7-BK runs, Then it emits one route-specific artifact executor input record. 业务规则：export 分支必须先审阅 selected-route execute manifest，再进入 artifact executor。
2. Given P7-BJ recorded manual terminal product-review preparation, When P7-BK runs, Then it emits one product-review preparation result record without requiring selected-route artifacts. 业务规则：manual terminal 分支不进入 artifact executor。
3. Given current P7-BJ is blocked, When P7-BK reads default input, Then it blocks and emits no continuation record. 业务规则：真实当前状态不能伪装可继续。
4. Given P7-BJ is missing, invalid, not completed, or has blockers, When P7-BK validates source, Then it blocks at execute-gate validation. 业务规则：只审阅干净完成的 P7-BJ。
5. Given an export P7-BJ result has mismatched selected-route execute report, path, status, returncode, or manifest, When P7-BK validates delegated output, Then it blocks. 业务规则：不能凭 P7-BJ 的声明放行，必须交叉核对真实 selected-route execute 产物。
6. Given a manual terminal P7-BJ result is missing product-review preparation, mixed with external command execution, or has wrong route/kind, When P7-BK validates terminal output, Then it blocks. 业务规则：manual terminal 只能是纯产品审阅准备记录。
7. Given P7-BJ or delegated selected-route artifacts show formal writeback, product-state permission, route execution, export, rendering, manifest generation, manual acceptance, or boundary flags, When P7-BK runs, Then it blocks. 业务规则：P7-BK 只审阅结果，不接受已越权执行的输入。
8. Given any valid or blocked input, When P7-BK writes outputs or runs via CLI, Then it writes only P7-BK JSON/Markdown and does not write `state/product/*`. 业务规则：本节点只产出审阅记录。

## Boundary Conditions

- Current real input remains blocked because P7-BJ is blocked.
- Export branch requires selected-route execute report and manifest.
- Manual terminal branch does not require selected-route execute report or manifest.
- No PDF/DOCX/package manifest/manual acceptance action happens in P7-BK.

## Tasks

### Task 1: RED tests

**Files:**
- Create: `tests/test_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review.py`

- [ ] Write unittest cases for the eight BDD behaviors.
- [ ] Run `python3 -m unittest tests.test_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review -v`.
- [ ] Expected: fail because `Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review` is missing.

### Task 2: Minimal implementation

**Files:**
- Create: `Program/workbench/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review.py`
- Create: `Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review.py`

- [ ] Implement P7-BJ validation, export delegated report/manifest validation, manual terminal product-review validation, boundary checks, JSON/Markdown writers, and CLI output.
- [ ] Run target unittest until green.

### Task 3: Real run and record

**Files:**
- Modify: `Tasks/todo.md`
- Create: `Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review.md`
- Create: `notes/session-logs/2026-05-31-p7-bk-manifested-routed-next-gate-command-result-continuation-execute-result-downstream-gate-entry-execute-gate-result-review.md`

- [ ] Run the real CLI against current P7-BJ output.
- [ ] Run formal-package regression tests.
- [ ] Record actual component effect, current blocked output, verification, and next P7-BL pause point.
