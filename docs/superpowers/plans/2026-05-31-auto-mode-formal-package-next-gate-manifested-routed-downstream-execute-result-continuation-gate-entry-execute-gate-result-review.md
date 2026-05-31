# P7-BN Manifested Routed Downstream Execute Result Continuation Gate Entry Execute Gate Result Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build P7-BN as the result-review node after P7-BM downstream execute result continuation execute gate.

**Architecture:** P7-BN consumes only the P7-BM execute gate plus the branch-specific delegated artifacts that P7-BM names or creates. Export branches must review the route-specific artifact executor entry and its artifact executor dry-run report before allowing explicit artifact execution. Manual terminal branches must review the product-review packet preparation record before allowing product-review packet continuation. P7-BN never runs commands, exports artifacts, accepts packages, or writes product state.

**Tech Stack:** Python stdlib, unittest, existing CLI-first Auto Mode JSON/Markdown pattern.

---

## BDD 行为

1. Given P7-BM export execute has entered route-specific artifact executor entry and the delegated dry-run is clean, When P7-BN reviews the result, Then it accepts the branch for explicit route-specific artifact execution.
   - 业务规则：export 分支只有在下一层 dry-run 已进入且仍没有正式产物副作用时，才能继续到真正产物执行闸门。

2. Given P7-BM manual execute recorded product-review packet preparation, When P7-BN reviews the result, Then it accepts the branch for product-review packet continuation.
   - 业务规则：manual terminal 分支只审阅产品审阅包准备记录，不要求外部命令结果。

3. Given the current real P7-BM is blocked, When P7-BN runs with default inputs, Then it remains blocked and writes no continuation review records.
   - 业务规则：上游执行闸门未完成时，P7-BN 不猜测后续路线。

4. Given P7-BM is missing, has the wrong schema, is not completed, or has blockers, When P7-BN reviews it, Then it blocks on the source execute gate.
   - 业务规则：P7-BN 只接受 P7-BM 的两个完成状态：artifact executor entry entered 或 product-review packet preparation recorded。

5. Given an export P7-BM result has missing, mismatched, failed, or dirty route-specific artifact executor entry artifacts, When P7-BN reviews it, Then it blocks on the artifact executor entry result contract.
   - 业务规则：export 分支必须证明 P7-BM、entry report、artifact executor dry-run report 三者描述同一个干净结果。

6. Given a manual P7-BM result has missing, duplicated, mismatched, or unreviewable product-review packet preparation records, When P7-BN reviews it, Then it blocks on the product-review packet preparation contract.
   - 业务规则：manual 分支只能有一个干净的 preparation record。

7. Given P7-BM or delegated reports show artifact execution, export/acceptance, rendering, formal writeback, product-state write, or boundary flags, When P7-BN reviews them, Then it blocks on boundary violation.
   - 业务规则：P7-BN 是结果审阅节点，不承认任何正式产物副作用。

8. Given P7-BN writes outputs, When it completes, Then it writes only P7-BN JSON/Markdown and never writes `state/product/*`.
   - 业务规则：本节点只审阅，不执行、不写产品状态。

## 边界条件

- 当前真实仓库默认应因 P7-BM blocked 而 blocked。
- P7-BN 不调用任何外部命令。
- Export 分支复用 route-specific artifact executor entry result contract。
- Manual 分支只看 P7-BM 的 product-review packet preparation record。
- 下一节点只消费 P7-BN 输出。

## 验证步骤

1. 写 `tests/test_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate_result_review.py` 并先运行 RED。
2. 新增 workbench 与 CLI。
3. 运行目标测试、真实 CLI、`py_compile`、Auto Mode 回归和 diff 检查。
4. 把阶段效果写入 `Tasks/todo.md` 和 session log。
