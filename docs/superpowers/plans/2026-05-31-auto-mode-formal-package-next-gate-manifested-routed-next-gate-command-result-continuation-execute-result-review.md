# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Result Continuation Execute Result Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build P7-BH as the result review node that consumes P7-BG continuation execute output and decides whether the export continuation output or manual terminal continuation record is clean enough for the next step.

**Architecture:** P7-BH reads only the P7-BG execute gate output. Export routes must contain one clean selected-route preflight result. Manual terminal routes must contain a clean terminal continuation record. This node writes only its own JSON and Markdown review; it never runs continuation, executes selected routes, exports files, performs manual acceptance, or writes product state.

**Tech Stack:** Python stdlib, unittest, CLI-first JSON/Markdown reports.

---

## BDD 行为

1. Given P7-BG completed an export continuation and selected-route preflight is ready, When P7-BH reviews it, Then it creates one selected-route preflight record and allows downstream selected-route execution review. 业务规则：只接受已经跑完且结果干净的 export continuation。
2. Given P7-BG recorded manual terminal continuation, When P7-BH reviews it, Then it creates one terminal continuation record and allows downstream product-review preparation without external command execution. 业务规则：manual terminal 是终态记录，不再触发导出命令。
3. Given current P7-BG is blocked, When P7-BH reads default input, Then it blocks and exposes no continuation records. 业务规则：真实当前状态不能伪装成可继续。
4. Given P7-BG is missing, invalid, not completed, failed, or has blockers, When P7-BH validates the source, Then it blocks at execute-gate validation. 业务规则：P7-BH 只能消费干净的 P7-BG。
5. Given export continuation output has wrong path, status, schema, summary, or selected-route plan, When P7-BH validates the result, Then it blocks. 业务规则：输出文件和 summary 必须同一套事实。
6. Given manual terminal continuation is missing terminal flags or incorrectly includes a command/run result, When P7-BH validates it, Then it blocks. 业务规则：terminal 分支只能记录完成状态，不能混入外部命令执行。
7. Given P7-BG or continuation output indicates selected route execution, export/acceptance, formal writeback, or product-state write permission, When P7-BH reviews it, Then it blocks. 业务规则：本段仍在审阅阶段，不允许正式层动作。
8. Given any valid source, When P7-BH writes outputs or runs via CLI, Then it writes only P7-BH JSON/Markdown and does not write `state/product/*`. 业务规则：本节点只产出审阅结果。

## Boundary Conditions

- Current real input should remain blocked because P7-BG is blocked.
- Export continuation can have `this_command_ran_continuation=true` in P7-BG because P7-BG was the executing node; P7-BH itself must keep `this_command_ran_continuation=false`.
- Manual terminal continuation can have terminal-record flags in P7-BG; P7-BH itself must not run commands.
- No selected-route execution, PDF/DOCX export, package manifest generation, manual acceptance, or product state write happens in P7-BH.

## Tasks

### Task 1: RED tests

**Files:**
- Create: `tests/test_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review.py`

- [x] Write unittest cases for the eight BDD behaviors.
- [x] Run `python3 -m unittest tests.test_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review -v`.
- [x] Expected: fail because `Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review` is missing.

### Task 2: Minimal implementation

**Files:**
- Create: `Program/workbench/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review.py`
- Create: `Program/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review.py`

- [x] Implement P7-BG source validation, export selected-route output validation, manual terminal record validation, boundary checks, JSON/Markdown writers, and CLI output.
- [x] Run target unittest until green.

### Task 3: Real run and record

**Files:**
- Modify: `Tasks/todo.md`
- Create: `Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review.md`
- Create: `notes/session-logs/2026-05-31-p7-bh-manifested-routed-next-gate-command-result-continuation-execute-result-review.md`

- [x] Run the real CLI against current P7-BG output.
- [x] Run formal-package regression tests.
- [x] Record actual component effect, current blocked output, verification, and next P7-BI pause point.
