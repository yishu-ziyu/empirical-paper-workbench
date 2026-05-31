# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Result Continuation Execute Result Downstream Gate Entry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build P7-BI as the downstream gate entry node that consumes P7-BH result review and creates the next explicit input record for selected-route execution or product-review preparation.

**Architecture:** P7-BI reads only the P7-BH result review. Export routes must expose one selected-route preflight record and become a selected-route execution input; manual terminal routes must expose one terminal continuation record and become a product-review preparation input. This node writes only its own JSON and Markdown entry record; it never runs selected-route execution, exports artifacts, performs manual acceptance, or writes product state.

**Tech Stack:** Python stdlib, unittest, CLI-first JSON/Markdown reports.

---

## BDD 行为

1. Given P7-BH is ready with an export selected-route preflight record, When P7-BI runs, Then it records one downstream selected-route execution input. 业务规则：export 分支只能进入显式 selected-route execution，不直接导出。
2. Given P7-BH is ready with a manual terminal continuation record, When P7-BI runs, Then it records one product-review preparation input without external command execution. 业务规则：manual terminal 分支进入产品审阅准备，不再回到导出命令。
3. Given current P7-BH is blocked, When P7-BI reads default input, Then it blocks and creates no downstream input. 业务规则：真实当前状态不能伪装可继续。
4. Given P7-BH is missing, invalid, not ready, or has blockers, When P7-BI validates source, Then it blocks at result-review validation. 业务规则：只消费干净的 P7-BH。
5. Given selected-route or terminal record is missing, duplicated, wrong route/gate, not accepted, or cannot continue, When P7-BI validates record contract, Then it blocks. 业务规则：下游入口必须由唯一且干净的 record 驱动。
6. Given route/gate is unsupported or record contents do not match the downstream contract, When P7-BI validates mapping, Then it blocks. 业务规则：不能猜测未知路线或下游命令。
7. Given P7-BH indicates command execution, selected-route execution, export/acceptance, formal writeback, product-state permission, or boundary flags, When P7-BI runs, Then it blocks. 业务规则：本节点只记录入口，不执行正式层动作。
8. Given any valid source, When P7-BI writes outputs or runs via CLI, Then it writes only P7-BI JSON/Markdown and does not write `state/product/*`. 业务规则：本节点只产出下游入口。

## Boundary Conditions

- Current real input remains blocked because P7-BH is blocked.
- Export downstream input requires later explicit execution.
- Manual terminal downstream input has no command path and no product-state write.
- No PDF/DOCX/package manifest/manual acceptance action happens in P7-BI.

## Tasks

### Task 1: RED tests

**Files:**
- Create: `tests/test_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry.py`

- [x] Write unittest cases for the eight BDD behaviors.
- [x] Run `python3 -m unittest tests.test_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry -v`.
- [x] Expected: fail because `Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry` is missing.

### Task 2: Minimal implementation

**Files:**
- Create: `Program/workbench/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry.py`
- Create: `Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry.py`

- [x] Implement source validation, downstream record contract validation, boundary checks, JSON/Markdown writers, and CLI output.
- [x] Run target unittest until green.

### Task 3: Real run and record

**Files:**
- Modify: `Tasks/todo.md`
- Create: `Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry.md`
- Create: `notes/session-logs/2026-05-31-p7-bi-manifested-routed-next-gate-command-result-continuation-execute-result-downstream-gate-entry.md`

- [x] Run the real CLI against current P7-BH output.
- [x] Run formal-package regression tests.
- [x] Record actual component effect, current blocked output, verification, and next P7-BJ pause point.
