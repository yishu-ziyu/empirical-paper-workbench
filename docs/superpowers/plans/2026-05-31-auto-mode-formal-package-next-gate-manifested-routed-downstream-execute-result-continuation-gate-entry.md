# P7-BL Manifested Routed Downstream Execute Result Continuation Gate Entry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build P7-BL as the read-only continuation gate entry after P7-BK downstream execute result review.

**Architecture:** P7-BL consumes only the P7-BK result review JSON. It writes a new gate-entry JSON/Markdown record that either points export routes toward route-specific artifact executor continuation or points the manual terminal route toward a product-review packet continuation. It never runs commands, exports artifacts, accepts packages, or writes product state.

**Tech Stack:** Python stdlib, unittest, existing CLI-first Auto Mode JSON/Markdown pattern.

---

## BDD 行为

1. Given P7-BK is export-ready with one accepted route-specific artifact executor input record, When P7-BL builds the continuation gate entry, Then it records one route-specific artifact executor continuation input and requires an explicit continuation command.
   - 业务规则：export 分支只能把已审阅的 route-specific artifact executor 输入交给下一段入口，不能直接执行产物。

2. Given P7-BK is manual-terminal-ready with one accepted product-review preparation result record, When P7-BL builds the continuation gate entry, Then it records one product-review packet continuation input and does not require an external command.
   - 业务规则：manual terminal 分支已经是产品审阅准备结果，只能转成产品审阅包入口。

3. Given the current real P7-BK is blocked, When P7-BL runs with default inputs, Then it remains blocked and writes no continuation input records.
   - 业务规则：上游未放行时不能猜测后续路线。

4. Given P7-BK is missing, has the wrong schema, is not ready, cannot continue, or has blockers, When P7-BL reviews it, Then it blocks on the source result review.
   - 业务规则：P7-BL 只接受完整、明确放行的 P7-BK。

5. Given an export-ready P7-BK has missing, duplicated, mismatched, unaccepted, or non-continuable route-specific artifact executor input records, When P7-BL reviews it, Then it blocks on the continuation contract.
   - 业务规则：export continuation 只能有一个干净、已接受、可继续的 artifact executor input record。

6. Given a manual-ready P7-BK has missing, duplicated, mismatched, unaccepted, or mixed product-review preparation records, When P7-BL reviews it, Then it blocks on the product-review continuation contract.
   - 业务规则：manual continuation 只能有一个干净的 product-review preparation result record，不能混入 artifact executor record。

7. Given P7-BK or its boundary flags show command execution, artifact execution, export/acceptance, rendering, formal writeback, or product-state write, When P7-BL reviews it, Then it blocks on boundary violation.
   - 业务规则：P7-BL 是入口记录，不承认任何已执行正式动作。

8. Given P7-BL writes outputs, When it completes, Then it writes only P7-BL JSON/Markdown and never writes `state/product/*`.
   - 业务规则：本节点不进入正式产品层。

## 边界条件

- 当前真实仓库默认应因 P7-BK blocked 而 blocked。
- P7-BL 不调用 artifact executor，不生成 PDF/DOCX，不生成 package manifest，不执行人工验收。
- P7-BL 只为后续显式节点生成入口记录；下一节点应只消费 P7-BL 输出。

## 验证步骤

1. 写 `tests/test_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry.py` 并先运行 RED。
2. 新增 workbench 与 CLI。
3. 运行目标测试、真实 CLI、`py_compile`、Auto Mode 回归和 diff 检查。
4. 把阶段效果写入 `Tasks/todo.md` 和 session log。
